#!/usr/bin/env python
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_ENERGY_SAVER_ENABLE
import argparse


def send_energy_saver(config, enable):
    with Rabbitmq(**config) as rabbitmq:
        rabbitmq.send_message(
            ROUTING_KEY_ENERGY_SAVER_ENABLE, {"enable_energy_saver": enable}
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enables/disables the energy saving mode. Anomaly detection is left unchanged."
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disables energy saving mode. The mode will be enabled if not provided.",
    )
    args = parser.parse_args()
    enable = False if args.disable else True

    config_logger("logging.conf")
    config = load_config("simulation.conf")

    enable_str = "enable" if enable == True else "disable"
    print(f"Setting energy saver mode: {enable_str}")
    send_energy_saver(config["rabbitmq"], enable)
