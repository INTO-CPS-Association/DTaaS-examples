# Replace Mock Panel With Real Panel (Raspberry Pi)

This guide explains how to replace `hardware/mock_panel.py` with a real panel adapter while keeping the rest of the system unchanged.

## Architecture (unchanged)

- Frontend <-> Gateway (`socket.io`, port `4000`)
- Gateway <-> Hardware Adapter (`tcp`, port `4001`)
- Optimizer <-> Gateway (`socket.io`, port `4000`)

The hardware adapter (mock or real) must use the same text protocol:

- Command from gateway: `<pan,tilt>\n`
- Telemetry to gateway: `>P:<power_in_watts>\n`

## New Delay Controls

The code now supports configurable delay knobs for real hardware behavior.

### 1) Gateway delays (recommended for real hardware)

In `gateway/server.js`, delays are controlled by environment variables:

- `HARDWARE_TX_DELAY_MS`: delay before sending command to hardware
- `HARDWARE_RX_DELAY_MS`: delay before emitting telemetry to clients

Examples:

```bash
export HARDWARE_TX_DELAY_MS=500
export HARDWARE_RX_DELAY_MS=700
```

### 2) Optimizer move settle delay

In `models/optimizer.py`:

- `SETTLE_TIME_SECONDS = 0.0`

Set this to account for panel movement + measurement stabilization after each angle change.

Example:

```python
SETTLE_TIME_SECONDS = 2.5
```

### 3) Mock-only delay simulation

In `hardware/mock_panel.py`:

- `CMD_RX_APPLY_DELAY_SEC`
- `POWER_TX_DELAY_SEC`

Keep both at `0.0` for instant mock behavior.

## How to switch from mock to real

`lifecycle/execute` now supports selecting hardware script with `HARDWARE_SCRIPT`.
Default remains mock:

- `hardware/mock_panel.py`

To use your real adapter script:

```bash
cd /workspace/digital_twins/solar-panel
export HARDWARE_SCRIPT=hardware/real_panel.py
export HARDWARE_TX_DELAY_MS=500
export HARDWARE_RX_DELAY_MS=700
./lifecycle/execute
```

## What your Raspberry Pi real adapter must do

Create a Python script (for example `hardware/real_panel.py`) that:

1. Connects to gateway TCP at `127.0.0.1:4001` (or gateway host/IP if remote).
2. Reads `<pan,tilt>` commands line-by-line.
3. Sends those angles to motor controller (servo/stepper driver).
4. Waits for movement + sensor stabilization as needed.
5. Reads measured panel power (watts) from your sensor path.
6. Sends telemetry line `>P:<watts>\n` back to gateway.
7. Reconnects automatically if connection drops.

## Minimal real adapter skeleton

Use this as a starting point and fill hardware-specific parts.

```python
#!/usr/bin/env python3
import socket
import time

GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 4001
ROTATION_SETTLE_SEC = 2.0


def parse_command(line: str):
    line = line.strip()
    if not (line.startswith("<") and line.endswith(">")):
        return None
    body = line[1:-1]
    parts = body.split(",")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None


def move_panel(pan: float, tilt: float) -> None:
    # TODO: send pan/tilt to motor controller
    pass


def read_power_watts() -> float:
    # TODO: read real power from your sensor
    return 0.0


def run(conn: socket.socket) -> None:
    buf = ""
    while True:
        data = conn.recv(1024)
        if not data:
            raise ConnectionError("gateway disconnected")
        buf += data.decode("utf-8", errors="ignore")
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            parsed = parse_command(line)
            if parsed is None:
                continue
            pan, tilt = parsed
            move_panel(pan, tilt)
            time.sleep(ROTATION_SETTLE_SEC)
            watts = read_power_watts()
            conn.sendall(f">P:{watts:.2f}\\n".encode("utf-8"))


def main() -> None:
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((GATEWAY_HOST, GATEWAY_PORT))
                run(s)
        except Exception as exc:
            print(f"real_panel reconnecting: {exc}")
            time.sleep(2)


if __name__ == "__main__":
    main()
```

## Safe rollout checklist

1. Keep mock as fallback (`HARDWARE_SCRIPT` unset).
2. Test real adapter with low movement speed first.
3. Start with conservative delays:
   - `HARDWARE_TX_DELAY_MS=300`
   - `HARDWARE_RX_DELAY_MS=500`
   - `SETTLE_TIME_SECONDS=2.0`
4. Verify optimizer log and telemetry stability.
5. Tune delays down only after stable behavior.
