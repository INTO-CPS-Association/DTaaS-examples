"""
Optimizer FMU — Two-Axis Solar Tracker
=======================================

Algorithm Overview
------------------
PHASE 1 – 2-D Perturb & Observe (P&O) MPPT
    The power surface P(pan, tilt) is a smooth unimodal hill.
    We find its peak by simultaneously perturbing both axes:

        1. Try all four cardinal neighbours (±Δpan, ±Δtilt) one at a time.
        2. Move to whichever neighbour increased power most.
        3. Shrink step-size when no improvement is found (adaptive P&O).
        4. Stop when step falls below the fine-resolution threshold.

PHASE 2 – Radial Binary Search for Target Power
    Once the MPP (pan*, tilt*) and P_max are known:

      • Power is strictly non-increasing along any ray outward from the MPP.
      • Binary-search on scalar t ∈ [0,1] along the ray MPP → farthest corner.

KEY FIX — Settle Counter
    The FMU is event-driven (one do_step per telemetry tick), NOT clock-driven.
    Without settling, the binary search reads stale power (from the previous
    position) and oscillates wildly.  After issuing any new position command
    we wait SETTLE_TICKS ticks before reading the resulting power and
    advancing the state machine.
"""

from __future__ import annotations

import math
from typing import Any
import time
from pythonfmu import Fmi2Slave
from pythonfmu.enums import Fmi2Causality, Fmi2Variability
from pythonfmu.variables import Integer, Real


# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------
_STEP_INIT    = 10.0   # initial P&O perturbation step (degrees)
_STEP_MIN     =  0.5   # stop P&O when step shrinks below this
_STEP_SHRINK  =  0.65  # multiply step by this factor when no improvement
_POWER_TOL    =  0.10  # W  — "close enough" for target-power match
_T_TOL        =  0.005 # binary-search convergence in t-space
_SETTLE_TICKS =  2     # ticks to wait after a move before reading power
                       # (covers transport delay + any low-pass smoothing)
# Additional real-world settle time (seconds) after a move command. Use this
# to model communication + actuator travel delay for real hardware.
SETTLE_TIME_SECONDS = 0.0

# Seconds between full MPP re-checks (set in seconds). The optimizer will
# attempt to re-find the MPP and then re-run the target-power search every
# `REPEAT_INTERVAL_CHECK` seconds. Set to 0 to disable periodic checks.
REPEAT_INTERVAL_CHECK = 30

# During each periodic re-check cycle, optionally probe a few low-power poses
# to refresh the minimum reachable power estimate under changing weather.
MIN_REFRESH_ENABLED = True
MIN_REFRESH_PROBES = 1

_PAN_MIN,  _PAN_MAX  = 0.0, 180.0
_TILT_MIN, _TILT_MAX = 0.0,  90.0


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))



class Optimizer(Fmi2Slave):
    """Optimizer: 2-D P&O MPPT then radial binary search for target power."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # ── Register FMU variables ───────────────────────────────────────────
        self.register_variable(Real("in_current_power",
            causality=Fmi2Causality.input, variability=Fmi2Variability.continuous))
        self.register_variable(Integer("start_mode",
            causality=Fmi2Causality.parameter, variability=Fmi2Variability.discrete))
        self.register_variable(Real("initial_target_power",
            causality=Fmi2Causality.parameter, variability=Fmi2Variability.fixed))
        self.register_variable(Real("out_target_pan",
            causality=Fmi2Causality.output, variability=Fmi2Variability.continuous))
        self.register_variable(Real("out_target_tilt",
            causality=Fmi2Causality.output, variability=Fmi2Variability.continuous))

        # ── FMU I/O ─────────────────────────────────────────────────────────
        self.in_current_power:     float = 0.0
        self.start_mode:           int   = 1
        self.initial_target_power: float = 10.0
        self.out_target_pan:       float = 0.0
        self.out_target_tilt:      float = 0.0

        # ── Internal state ───────────────────────────────────────────────────
        self.state:     str   = "INIT"
        self.mpp_pan:   float = 0.0
        self.mpp_tilt:  float = 0.0
        self.max_power: float = -1.0
        self.min_power: float = float("inf")
        self._last_target_power: float = -1.0

        # Settle counter — counts down after each position change
        self._settle_remaining: int = 0
        self._settle_until: float = 0.0

        # P&O
        self._step          = _STEP_INIT
        self._best_pan      = 0.0
        self._best_tilt     = 0.0
        self._best_power    = -1.0
        self._probes:       list = []   # remaining (pan, tilt) probes
        self._probe_results:list = []   # (power, pan, tilt) collected this round

        # Binary search
        self._corner_pan:  float = 0.0
        self._corner_tilt: float = 0.0
        self._bs_lo:       float = 0.0
        self._bs_hi:       float = 1.0
        self._bs_target:   float = 0.0

        # Periodic re-check state
        self._last_check_time: float = time.time()
        self._need_full_check: bool = False
        self._recheck_in_progress: bool = False
        self._min_refresh_points: list[tuple[float, float]] = []

        # Last computed reachability snapshot for UI/clients
        self.last_achievable: bool = True
        self.last_clamped: str = "none"  # one of: none, min, max

        # Expose the same interface used elsewhere in the project
        # Inputs / parameters
        # `in_current_power`, `start_mode`, `initial_target_power`
        # Outputs
        # `out_target_pan`, `out_target_tilt`

    # ── Private helpers ──────────────────────────────────────────────────────

    def _go_to(self, pan: float, tilt: float) -> None:
        """Command a new position and reset the settle counter."""
        new_pan  = _clip(pan,  _PAN_MIN, _PAN_MAX)
        new_tilt = _clip(tilt, _TILT_MIN, _TILT_MAX)
        moved = (abs(new_pan - self.out_target_pan) > 0.01 or
                 abs(new_tilt - self.out_target_tilt) > 0.01)
        self.out_target_pan  = new_pan
        self.out_target_tilt = new_tilt
        if moved:
            self._settle_remaining = _SETTLE_TICKS
            if SETTLE_TIME_SECONDS > 0:
                self._settle_until = time.time() + SETTLE_TIME_SECONDS

    def _cardinal_probes(self, pan: float, tilt: float, step: float) -> list:
        raw = [(pan+step,tilt),(pan-step,tilt),(pan,tilt+step),(pan,tilt-step)]
        seen, result = set(), []
        for p, t in raw:
            cp, ct = _clip(p,_PAN_MIN,_PAN_MAX), _clip(t,_TILT_MIN,_TILT_MAX)
            key = (round(cp,4), round(ct,4))
            if key != (round(pan,4),round(tilt,4)) and key not in seen:
                seen.add(key); result.append((cp, ct))
        return result

    def _farthest_corner(self, pan: float, tilt: float) -> tuple[float, float]:
        corners = [(_PAN_MIN,_TILT_MIN),(_PAN_MIN,_TILT_MAX),
                   (_PAN_MAX,_TILT_MIN),(_PAN_MAX,_TILT_MAX)]
        return max(corners, key=lambda c: math.hypot(c[0]-pan, c[1]-tilt))

    def _prepare_min_refresh_points(self) -> list[tuple[float, float]]:
        if not MIN_REFRESH_ENABLED or MIN_REFRESH_PROBES <= 0:
            return []
        corners = [(_PAN_MIN,_TILT_MIN),(_PAN_MIN,_TILT_MAX),
                   (_PAN_MAX,_TILT_MIN),(_PAN_MAX,_TILT_MAX)]
        corners = sorted(
            corners,
            key=lambda c: math.hypot(c[0] - self.mpp_pan, c[1] - self.mpp_tilt),
            reverse=True,
        )
        return corners[:min(MIN_REFRESH_PROBES, len(corners))]

    def _maybe_start_min_refresh(self) -> bool:
        if not self._recheck_in_progress:
            return False
        if not self._min_refresh_points:
            return False

        pan, tilt = self._min_refresh_points.pop(0)
        self._go_to(pan, tilt)
        self.state = "MIN_REFRESH"
        return True

    def _ray_point(self, t: float) -> tuple[float, float]:
        pan  = self.mpp_pan  + t*(self._corner_pan  - self.mpp_pan)
        tilt = self.mpp_tilt + t*(self._corner_tilt - self.mpp_tilt)
        return _clip(pan,_PAN_MIN,_PAN_MAX), _clip(tilt,_TILT_MIN,_TILT_MAX)

    def _issue_next_probe(self) -> None:
        pan, tilt = self._probes.pop(0)
        self._go_to(pan, tilt)
        self.state = "PROBE"

    def _evaluate_probes(self) -> None:
        best_p, best_pan, best_tilt = max(self._probe_results, key=lambda r: r[0])
        if best_p > self._best_power + _POWER_TOL:
            self._best_pan, self._best_tilt, self._best_power = best_pan, best_tilt, best_p
        else:
            self._step *= _STEP_SHRINK

        if self._step < _STEP_MIN:
            self.mpp_pan, self.mpp_tilt = self._best_pan, self._best_tilt
            self.max_power = self._best_power
            self._go_to(self.mpp_pan, self.mpp_tilt)
            self.state = "CHECK_TARGET"
        else:
            self._probes = self._cardinal_probes(self._best_pan, self._best_tilt, self._step)
            self._probe_results = []
            self._go_to(self._best_pan, self._best_tilt)
            self._issue_next_probe()

    # ── Main state machine ───────────────────────────────────────────────────

    def do_step(self, current_time: float, step_size: float) -> bool:  # noqa: ARG002
        if int(self.start_mode) == 0:
            return True

        # Track observed power envelope continuously so the optimizer adapts to
        # real hardware where minimum power may be non-zero and drift over time.
        if math.isfinite(self.in_current_power):
            self.min_power = min(self.min_power, self.in_current_power)
            if self.max_power < 0:
                self.max_power = self.in_current_power

        # ── Settle guard ─────────────────────────────────────────────────────
        # After any position change, burn ticks until the panel has moved and
        # the power reading reflects the NEW position.  This is the key fix
        # for the oscillation seen in the telemetry chart.
        if self._settle_remaining > 0:
            self._settle_remaining -= 1
            return True     # ← do nothing this tick; just wait
        if self._settle_until > 0 and time.time() < self._settle_until:
            return True

        # Re-enter target search if desired power changed post-calibration
        if (abs(self.initial_target_power - self._last_target_power) > 0.01
                and self.state in ("CHECK_TARGET", "LINE_SEARCH", "DONE")):
            self.state = "CHECK_TARGET"
            self._last_target_power = self.initial_target_power

        # Periodic full-MPP re-check trigger: if enough real time has passed
        # and we are idle-ish, restart the calibration to find a fresh MPP.
        if REPEAT_INTERVAL_CHECK > 0 and not self._recheck_in_progress:
            try:
                if (time.time() - self._last_check_time) >= REPEAT_INTERVAL_CHECK:
                    # Only trigger from stable states to avoid interrupting an
                    # ongoing calibration/search. INIT and WAIT_CENTER are OK.
                    if self.state in ("DONE", "CHECK_TARGET", "LINE_SEARCH", "WAIT_CENTER"):
                        self._recheck_in_progress = True
                        self._min_refresh_points = self._prepare_min_refresh_points()
                        # Reset state machine to re-run the P&O calibration
                        self.state = "INIT"
            except Exception:
                # Be defensive: never raise in the model loop
                pass

        # ── INIT ─────────────────────────────────────────────────────────────
        if self.state == "INIT":
            self._step, self._best_power = _STEP_INIT, -1.0
            self._probe_results = []
            self._go_to((_PAN_MIN+_PAN_MAX)/2.0, (_TILT_MIN+_TILT_MAX)/2.0)
            self.state = "WAIT_CENTER"

        # ── Record centre reading, begin first P&O round ─────────────────────
        elif self.state == "WAIT_CENTER":
            self._best_pan   = self.out_target_pan
            self._best_tilt  = self.out_target_tilt
            self._best_power = self.in_current_power
            self._probes = self._cardinal_probes(self._best_pan, self._best_tilt, self._step)
            self._probe_results = []
            self._issue_next_probe()

        # ── 2-D P&O: one measurement per settled tick ─────────────────────────
        elif self.state == "PROBE":
            self._probe_results.append(
                (self.in_current_power, self.out_target_pan, self.out_target_tilt))
            if self._probes:
                self._issue_next_probe()
            else:
                self._evaluate_probes()

        # ── Decide how to pursue target power ────────────────────────────────
        elif self.state == "CHECK_TARGET":
            self._last_target_power = self.initial_target_power
            target = self.initial_target_power

            # Dynamic reachable range based on calibrated max and observed min.
            reachable_max = self.max_power if self.max_power > 0 else self.in_current_power
            if math.isfinite(self.min_power):
                reachable_min = self.min_power
            else:
                reachable_min = 0.0

            if target >= reachable_max - _POWER_TOL:
                self._go_to(self.mpp_pan, self.mpp_tilt)
                self.last_achievable = target <= reachable_max + _POWER_TOL
                self.last_clamped = "max" if not self.last_achievable else "none"
                self.state = "DONE"
            elif target <= reachable_min + _POWER_TOL:
                self._go_to(*self._farthest_corner(self.mpp_pan, self.mpp_tilt))
                self.last_achievable = target >= reachable_min - _POWER_TOL
                self.last_clamped = "min" if not self.last_achievable else "none"
                self.state = "DONE"
            else:
                self.last_achievable = True
                self.last_clamped = "none"
                self._corner_pan, self._corner_tilt = self._farthest_corner(
                    self.mpp_pan, self.mpp_tilt)
                self._bs_lo, self._bs_hi = 0.0, 1.0
                self._bs_target = target
                self._go_to(*self._ray_point(0.5))
                self.state = "LINE_SEARCH"

        # ── Radial binary search — one step per settled tick ─────────────────
        elif self.state == "LINE_SEARCH":
            error = self.in_current_power - self._bs_target
            if abs(error) < _POWER_TOL or (self._bs_hi - self._bs_lo) < _T_TOL:
                self.state = "DONE"
                # Fine-tune: stay at this position (power is within tolerance)
                # If this was part of a periodic recheck, mark it finished
                if self._recheck_in_progress:
                    if self._maybe_start_min_refresh():
                        return True
                    self._recheck_in_progress = False
                    self._last_check_time = time.time()
            else:
                if self.in_current_power > self._bs_target:
                    self._bs_lo = (self._bs_lo + self._bs_hi) / 2.0
                else:
                    self._bs_hi = (self._bs_lo + self._bs_hi) / 2.0
                self._go_to(*self._ray_point((self._bs_lo + self._bs_hi) / 2.0))

        # ── Minimum-bound refresh probes during periodic re-check ───────────
        elif self.state == "MIN_REFRESH":
            # `min_power` is already updated at the top of do_step from current telemetry.
            if self._min_refresh_points:
                pan, tilt = self._min_refresh_points.pop(0)
                self._go_to(pan, tilt)
            else:
                self._recheck_in_progress = False
                self._last_check_time = time.time()
                # Resume normal solve for current target using refreshed min bound.
                self.state = "CHECK_TARGET"

        # DONE — hold position; target change will re-enter CHECK_TARGET.
        # If we reached DONE from a non-line path (e.g. target >= max_power)
        # and a recheck was in progress, record completion time.
        if self.state == "DONE" and self._recheck_in_progress:
            if self._maybe_start_min_refresh():
                return True
            self._recheck_in_progress = False
            self._last_check_time = time.time()

        return True


# ---------------------------------------------------------------------------
# Standalone socket runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import socketio

    GATEWAY_URL = "http://localhost:4000"
    MAX_POWER_W = 20.0
    sio   = socketio.Client()
    model = Optimizer(instance_name="optimizer_twin")
    mode  = {"v": "inverse"}
    in_flight = {"v": False}

    def _safe(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            n = float(value)
            return n if math.isfinite(n) else None
        return None

    def _emit(pwr: float) -> None:
        in_flight["v"] = True
        calibrating = model.state in ("INIT", "WAIT_CENTER", "PROBE")
        avail  = model.max_power if model.max_power > 0 else MAX_POWER_W
        min_p  = model.min_power if math.isfinite(model.min_power) else 0.0
        target = float(model.initial_target_power)
        achievable = calibrating or (min_p - 0.1 <= target <= avail + 0.1)
        if not calibrating:
            # Use the model's most recent clamp decision when available.
            achievable = model.last_achievable
        sio.emit("model_update", {
            "target_pan":          float(model.out_target_pan),
            "target_tilt":         float(model.out_target_tilt),
            "achievable":          achievable,
            "clamped":             model.last_clamped,
            "current_power":       pwr,
            "estimated_max_power": avail,
            "estimated_min_power": min_p,
            "state":               model.state,
        })

    @sio.on("connect")
    def _conn() -> None:
        print("Optimizer Digital Twin connected to Gateway")
        _emit(model.in_current_power)

    @sio.on("control_mode")
    def _cmode(data: Any) -> None:
        m = "forward" if isinstance(data, dict) and data.get("mode") == "forward" else "inverse"
        mode["v"] = m
        model.start_mode = 0 if m == "forward" else 1

    @sio.on("update_target_power")
    @sio.on("set_target_power")
    def _tgt(data: Any) -> None:
        if not isinstance(data, dict):
            return
        t = _safe(data.get("target"))
        if t is None:
            return
        # Treat explicit target updates as an optimization request.
        mode["v"] = "inverse"
        model.start_mode = 1
        model.initial_target_power = max(0.0, t)
        # DO NOT call model.do_step(0.0, 0.1) here.
        # The FMU is event driven by telemetry ticks. Calling do_step on pure
        # parameter updates artificialy advances the settle counter, causing
        # the model to read stale power values when multiple updates arrive.
        if not in_flight["v"]:
            _emit(model.in_current_power)

    @sio.on("telemetry_update")
    @sio.on("data_update")
    def _data(data: Any) -> None:
        if not isinstance(data, dict):
            return
        p = _safe(data.get("current_power"))
        if p is None:
            return
        
        in_flight["v"] = False
        
        model.in_current_power = p
        model.start_mode = 1 if mode["v"] == "inverse" else 0
        model.do_step(0.0, 0.1)
        if mode["v"] == "inverse":
            _emit(p)

    try:
        sio.connect(GATEWAY_URL, transports=["polling"])
        sio.wait()
    except Exception as e:
        print(f"Failed to connect: {e}")

