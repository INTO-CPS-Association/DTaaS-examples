from rabbitmq import Rabbitmq
from pyhocon import ConfigFactory
from fmuinterface import FMUInterface
import logging
import os

# TODO: Fix hard-coded paths (FMUInterface and simulation.conf)
# TODO: General code cleanup
# TODO: Make it possible to reset through scenario and implement in execute.py

ANOMALY_TOPIC = "incubator.diagnosis.plant.lidopen"
ANOMALY_KEY = "lid_open"
ENERGY_SAVING_KEY = "energy_saver_on"
ENERGY_SAVING_TOPIC = "incubator.energysaver.status"
ENERGY_SAVER_ALERT_TOPIC = "incubator.energysaver.alert"

class NuRVService:
    def __init__(self, rabbit, fmu_path):
        # Initialize FMUInterface with the given file path and start time
        self.fmu = FMUInterface(
            fileName=fmu_path,
            startTime=0,
        )
        # Initial states
        self.anomaly = False
        self.energy_saving = False
        self.rabbit = rabbit

    def on_read(self, ch, method, properties, body):
        # Update state based on incoming message body
        if ANOMALY_KEY in body:
            self.anomaly = body[ANOMALY_KEY]
        if ENERGY_SAVING_KEY in body:
            self.energy_saving = body[ENERGY_SAVING_KEY]

        # Define FMU inputs
        inputs = {
            "Boolean": {
                "anomaly": self.anomaly,
                "energy_saving": self.energy_saving,
                "_soft_reset": False,
            },
        }
        # Perform simulation step
        self.fmu.setInputs(inputs)
        self.fmu.callback_doStep(0, 1)
        res = self.fmu.getAllOutputs()
        print(f"Inputs: {inputs}. Outputs: {res}")
        alert_int = {"alert": res["Integer"]["_output"]}

        # Send alert if energy saving status is updated
        if ENERGY_SAVING_KEY in body:
            self.rabbit.send_message(routing_key=ENERGY_SAVER_ALERT_TOPIC, message=alert_int)

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Base path from environment variable
    lifecycle_path = os.getenv('LIFECYCLE_PATH')
    if not lifecycle_path:
        raise EnvironmentError("The LIFECYCLE_PATH environment variable is not defined.")

    # Construct default paths
    default_fmu_path = os.path.abspath(os.path.join(lifecycle_path, '../../../models/safe-operation.fmu'))
    default_config_path = os.path.abspath(os.path.join(lifecycle_path, '../simulation.conf'))

    # Load paths from environment variables with defaults
    fmu_path = os.getenv('FMU_PATH', default_fmu_path)
    config_path = os.getenv('CONFIG_PATH', default_config_path)

    # Load RabbitMQ configuration
    config = ConfigFactory.parse_file(config_path)["rabbitmq"]
    rabbit = Rabbitmq(**config)

    service = NuRVService(rabbit, fmu_path)

    rabbit.connect_to_server()
    rabbit.subscribe(routing_key=ANOMALY_TOPIC, on_message_callback=service.on_read)
    rabbit.subscribe(routing_key=ENERGY_SAVING_TOPIC, on_message_callback=service.on_read)
    rabbit.start_consuming()


if __name__ == "__main__":
    main()
