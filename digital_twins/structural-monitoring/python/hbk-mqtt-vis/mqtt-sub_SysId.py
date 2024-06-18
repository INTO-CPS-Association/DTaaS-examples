import json
import struct
from datetime import datetime
from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import MQTTv311

config_file = 'sysid_config_private.json'

def load_config(config_file: str):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

config = load_config(config_file)

HOST = config['mqtt']['host']
PORT = config['mqtt']['port']
USERNAME = config['mqtt']['username']
PASSWORD = config['mqtt']['password']
MQTT_TOPICS = config['mqtt']['topics']

acceleration_values = {}

def on_connect(mqttc, userdata, flags, rc, properties=None):
    print("connected with response code %s" %rc)
    #mqttc.subscribe(MQTT_TOPICS[0])
    for topic in MQTT_TOPICS:
        mqttc.subscribe(topic)

# message payload packet structure: 
#  2 byte for descriptor
#  2 bytes for metadata id
#  8 bytes for timestamp in seconds (milli and micro seconds are always zero)
#  8 bytes for nano seconds of a timestamp (always zero)
#  640 bytes for data


def on_subscribe(self, mqttc, userdata, msg, granted_qos):
    print("mid/response = " + str(msg) + " / " + str(granted_qos))

def on_message(client, userdata, msg):
    payload = msg.payload
    print(msg.topic)
    data = []
    timestamp = struct.unpack('Q', payload[4:12])[0]
    data = struct.unpack_from('640f', payload, 20)
    acceleration_values[timestamp] = {msg.topic: data}
    timestamp_key = acceleration_values.get(timestamp)
    if timestamp not in acceleration_values:
        acceleration_values[timestamp] = {}
    acceleration_values[timestamp][msg.topic] = data
    print(datetime.fromtimestamp(timestamp).strftime("%y-%m-%d %H-%M-%S %f"))
    print(acceleration_values.values().keys())
    #print(acceleration_values.keys())

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