#!/usr/bin/env python
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PUB_ENERGY_SAVER
import argparse


def send_pub_energy_saver(config, enable):
    with Rabbitmq(**config) as rabbitmq:
        rabbitmq.send_message(
            ROUTING_KEY_PUB_ENERGY_SAVER, {"pub_energy_saver": enable}
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enables/disables whether the energy saver messages are being sent. Anomaly detection is left unchanged."
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disables sending energy saving messages. The mode will be enabled if not provided.",
    )
    args = parser.parse_args()
    enable = False if args.disable else True

    config_logger("logging.conf")
    config = load_config("simulation.conf")

    enable_str = "enable" if enable == True else "disable"
    print(f"Setting pub_energy_saver: {enable_str}")
    send_pub_energy_saver(config["rabbitmq"], enable)
