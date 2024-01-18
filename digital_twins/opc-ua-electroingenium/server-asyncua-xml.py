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
    with open('config.json', 'r') as f:
        DATA = json.load(f)  

    # Instance of Server class
    server = Server()   
    await server.init()

    # Endpoint
    server.set_endpoint(DATA['url'])

    # Import nodes from XML file
    await server.import_xml("nodes-export.xml")

    # Find input nodes to simulate a signal
    objects_node = server.get_objects_node()
    inputs_node = None
    for node in await objects_node.get_children():
        display_name = await node.read_display_name()
        if  display_name.Text == "INPUTS":
            inputs_node = node
            break
    
    inputs_node_list = await inputs_node.get_children()
    # Run server
    async with server:    
        while True:
            await inputs_node_list[0].set_value(random.uniform(20.0, 100.0))
            await inputs_node_list[1].set_value(random.uniform(0.0, 100.0))
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    asyncio.run(main())        