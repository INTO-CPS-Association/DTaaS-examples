from asyncua import Server
import asyncio
import json
import os
import random 

async def main():
    working_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(working_directory)
    cwd = os.getcwd()
    assert cwd == working_directory, f"working directory expected {working_directory}, got: {cwd}"

    # Read configuration file and store info in DATA dictionary
    with open('/workspace/examples/digital_twins/opc-ua-waterplant/config.json', 'r') as f:
        DATA = json.load(f)  

    # Instance of Server class
    server = Server()   
    await server.init()

    # Endpoint
    server.set_endpoint(DATA['url'])

    # Configure server namespace
    namespace = "DTaaS_OPCUA_Simulation_Server"
    ns_ind = await server.register_namespace(namespace)
    namespace_array = await server.get_namespace_array()
    namespace_index = [await server.get_namespace_index(name) for name in namespace_array]
    namespace_dict = dict(zip(namespace_index, namespace_array))  

    # Get principal nodes
    objects_node = server.get_objects_node()
    root_node = server.get_root_node()

    # Create objects and nodes
    INPUTS = await objects_node.add_object(ns_ind, "INPUTS")

    await INPUTS.add_variable(ns_ind, "power_1", 0.0)
    await INPUTS.add_variable(ns_ind, "power_2", 0.0)


    OUTPUTS = await objects_node.add_object(ns_ind, "OUTPUTS")

    await OUTPUTS.add_variable(ns_ind, "conOutA1_1", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_2", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_3", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_4", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_5", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_6", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA1_7", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA3_3", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutA3_7", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutC_1", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutC_3", 0.0)
    await OUTPUTS.add_variable(ns_ind, "conOutC_7", 0.0)

    # Set nodes as writable by clients. A node is always writable on server side.
    for node in await OUTPUTS.get_children():
        await node.set_writable()

    # Run server
    try:
        await server.start()
        input_list = await INPUTS.get_children()        
        while True:
            await input_list[0].set_value(random.uniform(20.0, 100.0))
            await input_list[1].set_value(random.uniform(0.0, 100.0))
            await asyncio.sleep(1.0)
    except:
        pass
    finally:
        await server.export_xml_by_ns('nodes-export.xml', namespaces=ns_ind)
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())        
