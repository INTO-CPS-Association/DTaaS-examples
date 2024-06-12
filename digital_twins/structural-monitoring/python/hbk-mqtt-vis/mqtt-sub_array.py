from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import MQTTv311
import struct

HOST = "hostname"
PORT = 1883
USERNAME = "username"
PASSWORD = "password"
MQTT_TOPIC = "topic"

data = []

def on_connect(mqttc, userdata, flags, rc, properties=None):
    print("connected with response code %s" %rc)
    mqttc.subscribe(MQTT_TOPIC)

def on_subscribe(self, mqttc, userdata, msg, granted_qos):
    print("mid/response = " + str(msg) + " / " + str(granted_qos))

def on_message(client, userdata, msg):
    payload = msg.payload
    data = []
    data = struct.unpack_from('640f', payload, 20)
    print(data)
    # process data here

mqttc = MQTTClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            protocol=MQTTv311)

def main():
    mqttc.username_pw_set(USERNAME, PASSWORD)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe
    mqttc.connect(HOST, PORT, 60)

    mqttc.loop_start()

    while True:
        pass

if __name__ == "__main__":
    main()