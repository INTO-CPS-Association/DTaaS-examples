import logging
import math
from time import time, sleep

from oomodelling import Model
from scipy.integrate import RK45


class RTModelSolver:
    def __init__(self):
        super().__init__()
        self._l = logging.getLogger("RTModelSolver")

    def start_simulation(self, model: Model, h, start_t=0.0, stop_t=math.inf):
        model.set_time(start_t)
        model.assert_initialized()
        f = model.derivatives()
        x = model.state_vector()
        # Record first time.
        model.record_state(x, start_t)
        solver = RK45(f, start_t, x, t_bound=math.inf, max_step=h/10, vectorized=False)
        solver_time = start_t
        sim_start_wc = time()
        while solver_time <= stop_t:
            # wall clock time
            wc_time = time()
            solver_time = solver.t
            self._l.debug(f"solver_time before while ={solver_time}")
            accumulated_delay = (wc_time - sim_start_wc) - solver_time
            self._l.debug(f"Delay={accumulated_delay}")

            while solver.t - solver_time <= h:
                solver.step()
                self._l.debug(f"solver.t={solver.t}")

            model.record_state(solver.y, solver.t)
            model.discrete_step()

            e_wc = time() - wc_time
            e_solver = solver.t - solver_time
            self._l.debug(f"Step taken: wc={e_wc}s solver={e_solver}")
            if e_wc > e_solver:
                self._l.warning(f"Solver is running late.")

            sleep_for = e_solver - (e_wc + accumulated_delay)
            self._l.debug(f"sleep_for={sleep_for}s")
            sleep(sleep_for)
