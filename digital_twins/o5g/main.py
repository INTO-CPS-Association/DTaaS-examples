import os
import sys
import subprocess
import json
import numpy as np
import paho.mqtt.client as mqtt

# Read config from env
INSTALL_PATH = os.environ.get("O5G_INSTALL_PATH", "/workspace/examples")

MQTT_SERVER = os.environ['O5G_MQTT_SERVER']
MQTT_PORT = int(os.environ['O5G_MQTT_PORT'])
MQTT_USER = os.environ['O5G_MQTT_USER']
MQTT_PASS = os.environ['O5G_MQTT_PASS']

MQTT_TOPIC_SENSOR = os.environ['O5G_MQTT_TOPIC_SENSOR']
MQTT_TOPIC_AIR_PREDICTION = os.environ['O5G_MQTT_TOPIC_AIR_PREDICTION']

tool_path = INSTALL_PATH + '/tools'
sys.path.append(tool_path)
print(f"Importing tools from {tool_path}")
from path2Time import calc_oxygen
from graph2Path import calculate_shortest_path


converter_exec = os.path.join(INSTALL_PATH, 'tools/ifc2graph')
ifc_file = os.path.join(INSTALL_PATH, 'models/lab.ifc')
output_file = 'graph.json'

graph_script = os.path.join(INSTALL_PATH, 'tools/graphToPath.py')
test_fmu = os.path.join(INSTALL_PATH, 'tools/pathToTime.py')
# [Lat, Lon, Elevation]
start_position = np.array([42, 0, 6])
end_node = 0 


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_SENSOR + '/#')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(f"{msg.topic} {str(msg.payload)}")
    ue_identifier = msg.topic.split('/')[-1]
    # ue_identifier = 42
    if ue_identifier == 'remainingm ':
        # print('Skipping result')
        return

    try:
        data = json.loads(msg.payload)
        position = data['measurements']['position']
        start_position[0] = position['latitude']
        start_position[1] = position['longitude']
        start_position[2] = position['elevation']

        # print("Calculating route from position ", start_position)

        route_dist, path = calculate_shortest_path(graph, start_position, end_node, draw_graph=False)
        # print("route exists (" + str(path) + "), invoking FMU ")

        # Step Route->Prediction
        result = {}
        result['air-supply'] = {}
        result['air-supply']['remaining'] = calc_oxygen([route_dist])

        # publish the new value to the output topic
        result_topic = MQTT_TOPIC_AIR_PREDICTION
        # client.publish(result_topic, json.dumps(result))
        result_influx = "prediction air-remaining=" + str(result['air-supply']['remaining'])
        print(f'Publishing "{result_influx}" to {result_topic}')
        client.publish(result_topic, result_influx)

    except ValueError:
        print("Received non-numeric value. Skipping...")


# Step IFC->Graph
converter_command = f"{converter_exec} -i {ifc_file} -o {output_file} >/dev/null 2>&1"
subprocess.run(converter_command, shell=True, check=True)
# print("Graph exists, finding path")

# Step Graph->Route
with open(output_file, 'r') as content:
    graph = json.load(content)

client = mqtt.Client("supplymon")
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to " + MQTT_SERVER + ":" + str(MQTT_PORT))
client.connect(MQTT_SERVER, MQTT_PORT, 60)

client.loop_forever()
