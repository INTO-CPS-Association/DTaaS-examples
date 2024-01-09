import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
import logging
import json
import config


# MQTT configurations
BROKER_ADDRESS = config.MQTT_SERVER
PORT = config.MQTT_PORT
TOPIC = "vgiot/dt/#"

# Dictionary to hold values for each subtopic
data = {}

# Directory for plots

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC)

# Callback when a message is received
def on_message(client, userdata, message):
    try:
        print(message.payload)
        # Convert message payload to float
        content = json.loads(message.payload)
        value = float(content['air-supply']['remaining'])
        
        # Append value to the appropriate subtopic list in the data dictionary
        subtopic = message.topic.split('/')[-1]
        if subtopic not in data:
            data[subtopic] = []
        data[subtopic].append(value)

    except ValueError:
        print(f"Received non-numeric value on topic {subtopic}: {message.payload.decode('utf-8')}")



# Set up the MQTT client
client = mqtt.Client("Listener")
client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
client.on_message = on_message
client.on_connect = on_connect
client.connect(BROKER_ADDRESS, PORT)
client.subscribe(TOPIC)

# Start listening and wait for 10 seconds
print("Listening...")
client.loop_start()
time.sleep(10)
client.loop_stop()
print(f"Recieved values for {len(data)} sensors.")


# Plot the values for each subtopic
for subtopic, values in data.items():
    if values:
        plt.figure()  # create a new figure for each subtopic
        plt.plot(values)
        plt.title(f'Values Over Time for {subtopic}')
        plt.xlabel('Time (sequence)')
        plt.ylabel('Value')
        filename = f"/workspace/digital_twins/o5g/figures/{subtopic}_plot.png"
        plt.savefig(filename)
    else:
        print(f"No data received for topic {subtopic} in the given time frame.")
