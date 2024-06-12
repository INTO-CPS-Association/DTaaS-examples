import json
from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import MQTTv311

config_file = 'config.json'

def load_config(config_file: str):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

config = load_config(config_file)

HOST = config['mqtt']['host']
PORT = config['mqtt']['port']
USERNAME = config['mqtt']['username']
PASSWORD = config['mqtt']['password']
MQTT_TOPIC = config['mqtt']['topic']

mqttc = MQTTClient(
            callback_api_version=CallbackAPIVersion.VERSION2,
            protocol=MQTTv311)

def on_connect(mqttc, userdata, flags, rc, properties=None):
    print("connected with response code %s" %rc)

def main():
    print('HOST:', HOST)
    print('PORT:', PORT)
    print('USERNAME:', USERNAME)
    mqttc.connect(HOST, PORT, 60)

    mqttc.loop_start()
    mqttc.publish(MQTT_TOPIC, 'Hello World')
    mqttc.loop_stop()

if __name__ == "__main__":
    main()