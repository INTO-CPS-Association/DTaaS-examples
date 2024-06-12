import matplotlib.pyplot as plt
import numpy as np
from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import MQTTv311
import queue
import struct
import time

HOST = "hostname"
PORT = 1883
USERNAME = "username"
PASSWORD = "password"
MQTT_TOPIC = "topic"

data = []
data_queue = queue.Queue()

def on_connect(mqttc, userdata, flags, rc, properties=None):
    print("connected with response code %s" %rc)
    mqttc.subscribe(MQTT_TOPIC)

def on_subscribe(self, mqttc, userdata, msg, granted_qos):
    print("mid/response = " + str(msg) + " / " + str(granted_qos))

def on_message(client, userdata, msg):
    payload = msg.payload
    data = struct.unpack_from('640f', payload, 20)
    data_queue.put(data)

mqttc = MQTTClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            protocol=MQTTv311)

def main():
    # Set username and password
    mqttc.username_pw_set(USERNAME, PASSWORD)

    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe
    mqttc.connect(HOST, PORT, 60)

    mqttc.loop_start()
    plt.ion()
    fig, ax = plt.subplots()
    line1, = ax.plot(np.linspace(1, 640, 640), np.linspace(-10, 10, 640))

    while True:
       if not data_queue.empty():
            data = data_queue.get()
            line1.set_ydata(data)
            fig.canvas.draw()
            fig.canvas.flush_events()
        # Sleep for a short time to reduce CPU usage
       time.sleep(0.1)
       pass

if __name__ == "__main__":
    main()