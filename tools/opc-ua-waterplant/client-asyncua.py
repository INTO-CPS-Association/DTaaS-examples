from fmpy import read_model_description, extract, fmi_info, dump
from fmpy.fmi2 import FMU2Slave
from fmpy.simulation import Recorder 
# from fmpy.simulation import apply_start_values, Input, settable_in_instantiated, settable_in_initialization_mode
import numpy as np
import shutil
from asyncua import Client
from asyncua import ua
import asyncio
import pandas as pd
import sys
from datetime import datetime
from fmpy import *
import os
import json

class ClientOPCUA(Client):
    def init(self):
        super().__init__()

    def opcua_read_value(self, node_id:str) -> float:
        """
Read node value from OPCUA    

        Parameters
        ----------
        node_id : str
            Identifier of the desired node

        Returns
        -------
        float
            Node value

        """
        client_node = self.get_node(node_id)
        client_node_value = client_node.get_value()
        return client_node_value
        
    def opcua_read_values(self, inputs):
        """
        We introduce a dataframe with the inputs from which we want to read its OPCUA value and update it with the value of the node. 
        value of OPCUA and the dataframe is updated with the value of the node that corresponds to each input. 
        corresponding to each input

        Parameters
        ----------
        inputs : pd.DataFrame(index = input_names, columns = ["NodeID", "Reference", "Value"])
            In the dataframe each row corresponds to a variable and the columns are:
                - NodeID: identifier of the OPCUA node.
                - Reference: reference assigned to the variable within the FMU
                - Value: value read from the OPCUA node

        Returns
        -------
        inputs : pd.DataFrame
            The dataframe with the "Value" column updated.
        """
        for name in inputs.index:
            inputs.loc[name,"value"] = self.opcua_read_value(inputs.loc[name,'node_id'])
        return inputs

    async def opcua_write_value(self, node_id, value):
        client_node = self.get_node(node_id)

        ## Virtual PLC
        # client_node.set_value(value)
        
        ## Physic PLC
        data_value = ua.DataValue(ua.Variant(value, ua.VariantType.Double))
        await client_node.set_data_value(data_value)

    async def opcua_write_values(self, node_values:dict):
        # for node_id in node_values.keys():
        #     opcua_write_value(node_id,node_values[node_id])

        ## Another way to do the same
        for node_id, value in node_values.items():
            await self.opcua_write_value(node_id,value)

#%% ============ FUNCIONES ============
class SubscriptionHandler(object):

    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def datachange_notification(self, node, val, data):
        node_str = str(node)
        names = self.df.index[self.df["node_id"] == node_str]
        self.df.loc[names, "value"] = val     # Update dataframe when an OPC node changes its value
        
def export_model_description(model_description,filename):
    df = pd.DataFrame(columns=["name","causality","reference","start_value","description"])
    for i,variable in enumerate(model_description.modelVariables):
        df.loc[i,"name"] = variable.name
        df.loc[i,"causality"] = variable.causality
        df.loc[i,"reference"] = variable.valueReference
        df.loc[i,"start_value"] = variable.start   
        df.loc[i,"description"] = variable.description   

    assert filename.lower().endswith((".csv",".xls",".xlsx")),\
    f"Wrong file extension for saving model description, the expected formats are: '.csv' o '.xls' o '.xlsx', but got: '.{filename.rsplit('.')[-1]}'"

    if filename.lower().endswith(".csv"):        
        df.to_csv(filename,sep=';',index=False)        
    elif filename.lower().endswith(".xlsx"):
        df.to_excel(filename,sheet_name="model_description",index=False)        
    

async def runFMU(client       : ClientOPCUA,
           fmu_filename : str,
           start_time   : float, 
           stop_time    : float, 
           step_size    : float, 
           inputs       : pd.DataFrame, 
           send_to_plc  : pd.DataFrame, 
           parametros   : pd.DataFrame, 
           record       : bool = True, 
           record_interval: float = 5.0,
           record_variables: list = None, 
           enable_send  : bool = False):
    # read the model description
    global model_description
    global node_values
    
    # Read and export model description
    model_description = read_model_description(fmu_filename)    
    export_model_description(model_description,"model_description.csv")

    info_fmi = fmi_info(fmu_filename)
    fmi_version = info_fmi[0]
    fmi_type = info_fmi[1]   # 'CoSimulation' o 'ModelExchange'
    print("Simulating %s (FMI: Version = %s, Type = %s)..." % (fmu_filename, fmi_version, fmi_type))

    # Update dataframes ('inputs' and 'send_to_plc) with the FMU value references collected from the model description
    variable_names = list()
    idx_param = list()
    for variable in model_description.modelVariables:
        variable_names.append(variable.name)
        if variable.name in inputs.index:
            inputs.loc[variable.name,"reference"] = int(variable.valueReference)
        if variable.name in send_to_plc.index.to_list():
            send_to_plc.loc[variable.name,"reference"] = int(variable.valueReference)
        if variable.name in parametros.index.to_list():
            parametros.loc[variable.name,"reference"] = int(variable.valueReference)
            idx_param.append(variable.name)
    # extract the FMU
    unzipdir = extract(fmu_filename)
    
    fmu = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=unzipdir,
                    modelIdentifier=model_description.modelExchange.modelIdentifier,
                    instanceName='instance1')
    
    # initialize
    fmu.instantiate()
    fmu.setupExperiment(startTime=start_time)
    # =============== set parameters ================
    # ¡¡¡ VERY IMPORTANT TO DEFINE PARAMETERS AND VARIABLES between fmu.setupExperiment() y fmu.enterInitializationMode()  !!!
    if len(idx_param) > 0:
        fmu.setReal(parametros.loc[idx_param,'reference'].to_list(), parametros.loc[idx_param, 'value'])
    else:
        pass
    # fmu.setReal(parametros["reference"].to_list(), parametros["value"].to_list())
    # start_values = {key: val for key, val in start_values.items() if key not in vr_inputs}
    # start_values = apply_start_values(fmu, model_description, start_values, settable=settable_in_instantiated)
    # ===============================================
    fmu.enterInitializationMode()
    # start_values = apply_start_values(fmu, model_description, start_values, settable=settable_in_initialization_mode)
    fmu.exitInitializationMode()  
        
    if not all(element in variable_names for element in send_to_plc.index.to_list()):
        print("WARNING: some variable of the configuration file is not present in the model description")
    if record == True:
        varNames = send_to_plc.index.to_list()
        varNames.extend(["power[1]", "power[2]", "power[3]", "vfr"])
        recorder = Recorder(fmu=fmu, modelDescription=model_description, variableNames=record_variables, interval=record_interval)
    
    # Get the values that we want to send to the PLC
    idx_send = send_to_plc["node_id"] != ""       
    
    # Bucle
    time = start_time
    t_ini = datetime.now()
    elapsed_time = 0.0
    while time < stop_time:         
    # while True:  
        elapsed_time = datetime.now() - t_ini
        while (elapsed_time.seconds + elapsed_time.microseconds/1e6) < time:
            elapsed_time = datetime.now() - t_ini

    ###############################
        # set the input

        fmu.setReal(inputs["reference"].to_list(),inputs["value"].to_list())
        fmu.setReal([inputs.loc["vfr","reference"]],[inputs.loc["vfr","value"]/3600]) # Cambio de unidades de m3/h a m3/s
        # correccion de potencia si es mayor que 100
        if inputs.loc["power[1]","value"] > 100:
            fmu.setReal([inputs.loc["power[1]","reference"]],[100])
        if inputs.loc["power[2]","value"] > 100:
            fmu.setReal([inputs.loc["power[2]","reference"]],[100])
        if inputs.loc["power[3]","value"] > 100:
            fmu.setReal([inputs.loc["power[3]","reference"]],[100])
        
        # perform one step
        fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)

        # advance the time
        time += step_size
        
        while (elapsed_time.seconds + elapsed_time.microseconds/1e6) < time:
            elapsed_time = datetime.now() - t_ini
        # get values we want to send
        results = fmu.getReal(send_to_plc.loc[idx_send,"reference"].to_list())           
        for i,_ in enumerate(results):
            if results[i] < 1E-10:
                results[i] = 0                
        node_values = dict(zip(send_to_plc.loc[idx_send,"node_id"].to_list(), results))  
        
        if enable_send == True:     
            elapsed_time = datetime.now() - t_ini
            print(f"Simulation time = {time} ---------- Real time = {elapsed_time.seconds + elapsed_time.microseconds/1e6}")                      
            await client.opcua_write_values(node_values)

        # get the values
        if record == True:
            recorder.sample(time)            
        
        
    if record == True:
        results_df = pd.DataFrame(recorder.result())
        results_df.to_csv("results.csv",index=False,sep=';')    
    else:
        results_df = None
    
    # Close FMU 
    fmu.terminate()
    fmu.freeInstance()
    shutil.rmtree(unzipdir, ignore_errors=True)   

    return results_df

#%% ============ MAIN ============
async def main():
    working_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(working_directory)
    cwd = os.getcwd()
    assert cwd == working_directory, f"working directory expected {working_directory}, got: {cwd}"
    # ================ Read configuration 'config.json' file ===============   
    with open('/workspace/examples/digital_twins/opc-ua-waterplant/config.json', 'r') as f:
        DATA = json.load(f)       
    # ================ Read configuration Excel .ods file ===============   
    inputs = pd.read_excel(DATA['config_ods'],sheet_name="inputs",index_col="name",na_filter=False)    
    send_to_plc = pd.read_excel(DATA['config_ods'],sheet_name="send_to_plc",index_col="name",na_filter=False)  
    parametros = pd.read_excel(DATA['config_ods'],sheet_name="parametros",index_col="name")   
    # Set 'value' column as float
    inputs = inputs.astype({'value': 'float'})
    send_to_plc = send_to_plc.astype({'value': 'float'})
    parametros = parametros.astype({'value': 'float'})
    # Set 'reference' column as int
    inputs = inputs.astype({'reference': 'int'})
    send_to_plc = send_to_plc.astype({'reference': 'int'})
    parametros = parametros.astype({'reference': 'int'})
    # ============ OPC UA SETUP ============    
    try:
        client = ClientOPCUA(url = DATA['url'])
        await client.connect()
        print("Client connected successfully")
        nodes = list()  # Lista de elementos tipo nodo
        idx = inputs["node_id"] != ""
        for name in inputs.index[idx]:
            node = client.get_node(inputs.loc[name,"node_id"])
            nodes.append(node)
        handler = SubscriptionHandler(inputs)
        sub = await client.create_subscription(500, handler) # 500 miliseconds
        handle = await sub.subscribe_data_change(nodes)
    except Exception as err:  
        print("Error while creating the connection ", err)
        sys.exit(1)

    else:        
        # ============= RUN FMU ================
        print(dump(DATA['fmu_filename']))
        res = await runFMU(
            client          = client,
            fmu_filename    = DATA['fmu_filename'],
            start_time      = 0.0, 
            stop_time       = DATA['stop_time'], 
            step_size       = DATA['step_size'], 
            inputs          = inputs, 
            send_to_plc     = send_to_plc,
            parametros      = parametros,
            record          = DATA['record'],
            record_interval = DATA['record_interval'],
            record_variables= DATA['record_variables'], 
            enable_send     = DATA['enable_send'])        

    finally:                
        # ============ EXIT ============    
        # Send a zero to al writable nodes before disconnecting
        idx_send = send_to_plc["node_id"] != ""  
        nodes_before_exit = send_to_plc.loc[idx_send,"node_id"].to_list()
        send_before_exit = dict()
        for node in nodes_before_exit:
            send_before_exit[node] = 0.0

        try:
            await client.opcua_write_values(send_before_exit)
            # Disconnect client from OPC UA server
            await client.disconnect()
            print("Client disconnected")
        except:
            pass

        # Close FMU
        try:
            fmu.terminate()
            fmu.freeInstance()
            shutil.rmtree(unzipdir, ignore_errors=True)            
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
