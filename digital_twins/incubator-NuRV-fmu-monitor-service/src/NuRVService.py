from rabbitmq import Rabbitmq
from pyhocon import ConfigFactory
from fmuinterface import FMUInterface
import logging

f = FMUInterface(fileName="../safe-operation.fmu", startTime=0)
anomaly = False
anomaly_key = "lid_open"
anomaly_topic = "incubator.diagnosis.plant.lidopen"
energy_saving = False
energy_saving_key = "energy_saver_on"
energy_saving_topic = "incubator.energysaver.status"


def on_read(ch, method, properties, body):
    global anomaly, energy_saving
    if anomaly_key in body:
        anomaly = body[anomaly_key]
    if energy_saving_key in body:
        energy_saving = body[energy_saving_key]

    inputs = {
        "Boolean": {
            "anomaly": anomaly,
            "energy_saving": energy_saving,
            "_soft_reset": False,
        },
    }
    f.setInputs(inputs)
    f.callback_doStep(0, 1)
    res = f.getAllOutputs()
    print(f"Inputs: {inputs}. Outputs: {res}")


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    config = ConfigFactory.parse_file("../simulation.conf")["rabbitmq"]

    rabbit = Rabbitmq(**config)

    rabbit.connect_to_server()
    rabbit.subscribe(routing_key=anomaly_topic, on_message_callback=on_read)
    rabbit.subscribe(routing_key=energy_saving_topic, on_message_callback=on_read)
    rabbit.start_consuming()


if __name__ == "__main__":
    main()
