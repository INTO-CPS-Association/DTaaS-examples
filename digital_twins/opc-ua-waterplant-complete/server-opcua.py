from opcua import Server
import json
import os
import random
import time


if __name__ == "__main__":
    working_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(working_directory)
    cwd = os.getcwd()
    assert cwd == working_directory, f"working directory expected {working_directory}, got: {cwd}"

    # Read configuration file and store info in DATA dictionary
    with open('config.json', 'r') as f:
        DATA = json.load(f)  

    # Instance of Server class
    server = Server()

    # Endpoint
    server.set_endpoint(DATA['url'])

    # Configure server namespace
    namespace = "DTaaS_OPCUA_Simulation_Server"
    ns_ind = server.register_namespace(namespace)
    namespace_array = server.get_namespace_array()
    namespace_index = [server.get_namespace_index(name) for name in namespace_array]
    namespace_dict = dict(zip(namespace_index, namespace_array))  

    # Get principal nodes
    objects_node = server.get_objects_node()
    root_node = server.get_root_node()
    # server_node = server.get_server_node()

    # Create objects and nodes
    INPUTS = objects_node.add_object(ns_ind, "INPUTS")

    INPUTS.add_variable(ns_ind, "power_1", 0.0)
    INPUTS.add_variable(ns_ind, "power_2", 0.0)


    OUTPUTS = objects_node.add_object(ns_ind, "OUTPUTS")

    OUTPUTS.add_variable(ns_ind, "conOutA1_1", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_2", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_3", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_4", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_5", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_6", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA1_7", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA3_3", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutA3_7", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutC_1", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutC_3", 0.0)
    OUTPUTS.add_variable(ns_ind, "conOutC_7", 0.0)

    # Set nodes as writable by clients. A node is always writable on server side.
    for node in OUTPUTS.get_children():
        node.set_writable()

    # Run server
    try:
        server.start()
        input_list = INPUTS.get_children()        
        while True:
            input_list[0].set_value(random.uniform(20.0, 100.0))
            input_list[1].set_value(random.uniform(0.0, 100.0))
            time.sleep(1.0)
    except:
        pass
    finally:
        server.export_xml_by_ns('nodes-export.xml', namespaces=ns_ind)
        server.stop()
    
