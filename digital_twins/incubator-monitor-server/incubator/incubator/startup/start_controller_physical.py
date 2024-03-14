import logging
import time

from incubator.config.config import config_logger, load_config
from incubator.physical_twin.controller_physical import ControllerPhysical


def start_controller_physical(ok_queue=None):
    config_logger("logging.conf")
    l = logging.getLogger("start_controller_physical")
    config = load_config("simulation.conf")

    while True:
        try:
            controller = ControllerPhysical(rabbit_config=config["rabbitmq"], **(config["physical_twin"]["controller"]))
            controller.setup()
            if ok_queue is not None:
                ok_queue.put("OK")
            controller.start_control()
        except KeyboardInterrupt:
            exit(0)
        except Exception as exc:
            l.error("The following exception occurred. Attempting to reconnect.")
            l.error(exc)
            time.sleep(1.0)


if __name__ == '__main__':
    start_controller_physical()
