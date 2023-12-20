from opcua import Server
import json
import os
import random
import time


if __name__ == "__main__":
    working_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(working_directory)
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    assert cwd == working_directory, f"working directory expected {working_directory}, got: {cwd}"

    # Read configuration file and store info in DATA dictionary
    with open('config.json', 'r') as f:
        DATA = json.load(f)  

    # Instance of Server class
    server = Server()

    # Endpoint
    server.set_endpoint(DATA['url'])

    # Import nodes from XML file
    server.import_xml("nodes-export.xml")

    # Find input nodes to simulate a signal
    objects_node = server.get_objects_node()
    inputs_node = None
    for node in objects_node.get_children():
        if node.get_display_name().Text == "INPUTS":
            inputs_node = node
            break

    # Run server
    try:
        server.start()
        inputs_node_list = inputs_node.get_children()
        while True:
            # Simulate 2 random signals that update every 1.0 seconds
            inputs_node_list[0].set_value(random.uniform(20.0, 100.0))
            inputs_node_list[1].set_value(random.uniform(0.0, 100.0))
            time.sleep(1.0)            
    except:
        pass
    finally:
        server.stop()
    
