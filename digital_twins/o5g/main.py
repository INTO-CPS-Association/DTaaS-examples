import os
import sys
import subprocess
import json
import numpy as np
import paho.mqtt.client as mqtt

sys.path.append('/workspace/models')
from pathToTime import calc_oxygen
from graphToPath import calculate_shortest_path

# Directories and executable paths
dir_ifc_to_graph = '/workspace/tools/'
dir_bim_files = '/workspace/data/'
dir_graph_to_nav = '/workspace/models/'
dir_path_to_oxygen = '/workspace/models/'

converter_exec = os.path.join(dir_ifc_to_graph, 'ifc_to_graph')
ifc_file = os.path.join(dir_bim_files, 'lab.ifc')
output_file = 'graph.json'

graph_script = os.path.join(dir_graph_to_nav, 'graphToPath.py')
test_fmu = os.path.join(dir_path_to_oxygen, 'pathToTime.py')
# [Lat, Lon, Elevation]
start_position = np.array([42, 0, 6])
end_node = 0  # ToDo: Find all end nodes automatically and find the minimal shortest path


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("vgiot/ue/metric/#")
    # client.subscribe("vgiot/dt/prediction/#")


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
        # print(f"Final integer value from Test.fmu: {result['air-supply']['remaining']}")

        # publish the new value to the output topic
        result_topic = "vgiot/dt/prediction/" + str(ue_identifier)
        result_topic = "vgiot/dt/prediction"
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
client.username_pw_set("lars", "LarsLubeck082023")
client.on_connect = on_connect
client.on_message = on_message

client.connect("dtl-server-2.st.lab.au.dk", 8090, 60)

client.loop_forever()
