from rabbitmq import Rabbitmq
from pyhocon import ConfigFactory
from fmuinterface import FMUInterface
import logging

# TODO: Fix hard-coded paths (FMUInterface and simulation.conf)
# TODO: General code cleanup
# TODO: Make it possible to reset through scenario and implement in execute.py

ANOMALY_TOPIC = "incubator.diagnosis.plant.lidopen"
ANOMALY_KEY = "lid_open"
ENERGY_SAVING_KEY = "energy_saver_on"
ENERGY_SAVING_TOPIC = "incubator.energysaver.status"
ENERGY_SAVER_ALERT_TOPIC = "incubator.energysaver.alert"

class NuRVService:
    def __init__(self, rabbit):
        # Initialize FMUInterface with the given file path and start time
        self.fmu = FMUInterface(
            fileName="/home/au610920/repos/DTaaS-examples/models/safe-operation.fmu",
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
    # Load RabbitMQ configuration
    config = ConfigFactory.parse_file("../simulation.conf")["rabbitmq"]
    rabbit = Rabbitmq(**config)

    service = NuRVService(rabbit)

    rabbit.connect_to_server()
    rabbit.subscribe(routing_key=ANOMALY_TOPIC, on_message_callback=service.on_read)
    rabbit.subscribe(routing_key=ENERGY_SAVING_TOPIC, on_message_callback=service.on_read)
    rabbit.start_consuming()


if __name__ == "__main__":
    main()
