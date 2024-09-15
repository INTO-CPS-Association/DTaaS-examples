import subprocess, os, time, sys, traceback

incubator_location = os.getenv("INCUBATOR_PATH")
sys.path.append(os.path.join(f"{incubator_location}"))
from threading import Thread, Event
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import load_config
from digital_twin.communication.rabbitmq_protocol import (
    ROUTING_KEY_ENERGY_SAVER_ENABLE,
    ROUTING_KEY_ENERGY_SAVER_STATUS,
    ROUTING_KEY_LIDOPEN,
)

MONITOR_RESET_KEY = "reset"
MONITOR_RESET_TOPIC = "monitor_reset"


def startRabbitMQ(message_callback):
    config = load_config(f"{incubator_location}/simulation.conf")
    rabbitMq = Rabbitmq(**config["rabbitmq"])
    rabbitMq.connect_to_server()
    print("Connected to rabbitmq server.")
    rabbitMq.subscribe(ROUTING_KEY_ENERGY_SAVER_STATUS, handleMessage)
    rabbitMq.subscribe(ROUTING_KEY_LIDOPEN, handleMessage)
    rabbitMq.subscribe("incubator.energysaver.alert", handleMessage)
    return rabbitMq


def startIncubator():
    print("Starting incubator")
    incubatorProcess = subprocess.Popen(
        f"cd {incubator_location}/; exec python -m startup.start_all_services",
        shell=True,
        cwd=os.getcwd(),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    time.sleep(5)
    result = incubatorProcess.poll()
    if result is not None:
        print("Failed to start incubator")
        output = incubatorProcess.stderr.readlines()
        print(output)
        exit()
    return incubatorProcess


def runScenario(event):
    print(
        "Running scenario with initial state: lid closed and energy saver on",
        flush=True,
    )
    os.system(f"cd {incubator_location}; python -m cli.trigger_energy_saver")
    os.system(f"cd {incubator_location}; python -m cli.mess_with_lid_mock 1")
    for i in range(1200):  # wait 2 minutes
        if event.is_set():
            return
        time.sleep(0.1)

    print("Opening lid...", flush=True)
    os.system(f"cd {incubator_location}; python -m cli.mess_with_lid_mock 100")
    for i in range(300):  # wait 30 seconds
        if event.is_set():
            return
        time.sleep(0.1)

    print("Disabling energy saver...", flush=True)
    os.system(f"cd {incubator_location}; python -m cli.trigger_energy_saver --disable")
    for i in range(300):
        if event.is_set():
            return
        time.sleep(0.1)

    print("Putting lid back on...", flush=True)
    os.system((f"cd {incubator_location}; python -m cli.mess_with_lid_mock 1"))

    # Wait a bit before resetting the monitor
    for i in range(100):
        if event.is_set():
            return
        time.sleep(0.1)
    print("Resetting monitor state.", flush=True)
    config = load_config(f"{incubator_location}/simulation.conf")
    rabbitMq = Rabbitmq(**config["rabbitmq"])
    rabbitMq.connect_to_server()
    msg = {MONITOR_RESET_KEY: True}
    rabbitMq.send_message(routing_key=MONITOR_RESET_TOPIC, message=msg)

    for i in range(
        200
    ):  # wait for the anomaly detection to determine that the lid is back on
        if event.is_set():
            return
        time.sleep(0.1)
    event.set()


if __name__ == "__main__":

    rabbitMq = None
    incubatorProcess = None
    scenario_thread = None
    event = Event()
    try:
        # Start incubator
        incubatorProcess = startIncubator()
        message = {}
        message["anomaly"] = "!anomaly"
        message["energy_saving"] = "!energy_saving"
        message["alert"] = "unknown"

        # setup RabbitMQ
        def handleMessage(channel, method, properties, body_json):
            # print(f"Channel: {channel}. Method: {method}. Properties: {properties}. Body: {body_json}.")
            if "lid_open" in body_json:
                message["anomaly"] = "anomaly" if body_json["lid_open"] else "!anomaly"
            elif "energy_saver_on" in body_json:
                message["energy_saving"] = (
                    "energy_saving"
                    if body_json["energy_saver_on"]
                    else "!energy_saving"
                )
            elif "alert" in body_json:
                message["alert"] = "alert" if body_json["alert"] else "normal"
                # print(f"Message from TeSSLa: {body_json['alert']}")
            states = f"{message['anomaly']} & {message['energy_saving']}"
            print(f"State: {states}, verdict: {message['alert']}")

            if event.is_set():
                rabbitMq.close()

        rabbitMq = startRabbitMQ(handleMessage)
        scenario_thread = Thread(target=runScenario, args=[event])
        # Wait to ensure incubator running
        # time.sleep(1)
        scenario_thread.start()
        rabbitMq.start_consuming()
        print("Finished simulation")
    except KeyboardInterrupt:
        event.set()
        print("Stopping simulation...")
    except Exception as e:
        event.set()
        print("An error has occurred:")
        traceback.print_exc()
    finally:
        if rabbitMq and not event.is_set():
            rabbitMq.close()
        if incubatorProcess:
            print(f"Stopping incubator with pid: {incubatorProcess.pid}")
            incubatorProcess.kill()
            incubatorProcess.wait()
        os.system('pkill -f "python -m startup.start_all_services"')
        if scenario_thread is not None:
            scenario_thread.join()
