## Overview
This example is an implementation of the the paper Digital Twin for Rescue Missions--a Case Study by Leucker et al.: https://ceur-ws.org/Vol-3507/paper4.pdf

## Lifecycle

### Create

##### TeSSLa

Before running the create script please download the `tessla-telegraf-connector.zip` from https://git.tessla.io/telegraf/tessla-telegraf-connector and extract its contents to `tools/tessla/tessla-telegraf-connector`.  

Make sure the following files of this example are at the correct locations:
```
   /workspace/digital_twins/o5g/main.py
   /workspace/digital_twins/o5g/sensorSimulation.py
   /workspace/digital_twins/o5g/telegraf.conf
   /workspace/digital_twins/o5g/runTessla.sh
   /workspace/digital_twins/o5g/config.py
   /workspace/data/lab.ifc
   /workspace/models/graphToPath.py
   /workspace/models/pathToTime.py
   /workspace/models/PathOxygenEstimate.mo
   /workspace/models/makefmu.mos
   /workspace/tools/ifc_to_graph
   /workspace/tools/tessla/tessla-telegraf-connector/     containing the contents of 
       https://git.tessla.io/telegraf/tessla-telegraf-connector/-/blob/master/Release/tessla-telegraf-connector.zip
   /workspace/tools/tessla/tessla-telegraf-connector/specification.tessla
```

##### MQTT
Insert your MQTT server address, username, and password in `config.py` and `telegraf.conf`

##### InfluxDB
This example uses InfuxDB as a data storage, which will need to be configured to use your Access data.
    - Log into the InfluxDB Web UI (Default Port 8086 on DTaaS), you will need the following:
    - Your org name below your username in the sidebar
    - Create a data bucket if you don't have one already in `Load Data -> Buckets`
    - Create an API access token in `Load Data -> API Tokens`, Copy and save this token somewhere immediately, you can not access it later!
    Insert your InfluxDB configuration in `lifecycle\create` and `telegraf.conf`

##### Grafana
This example can also use Grafana to visualize the data. To use it Log into the WEB UI (Default Port 8088 on DTaaS) and in `Administration -> Service Accounts` add a new service account. Create a Token for this Service Account an copy it to `lifecycle\create`. Also set USE_GRAFANA to true.

#### Running create

Run the create script by executing
```bash
lifecycle/create
```

This will install all the required dependencies from apt and pip, install OpenModelica and compile the modelica modell to a Functional Mockup Unit (FMU) for the correct platform.

### Exceute

To run the Digital Twin execute 
```bash
lifecycle/execute
```

This will start all the required components in a single tmux session called `o5g` in the background. To view the running Digital Twin attatch to this tmux session by executing
```bash
tmux a -t o5g
```
This session contains 4 components of the Example
 - Top Left: Sensor simulator generating random location and O2-level data
 - Top Right: Main Digital Twin receives the sensor data and calculates an estimate of how many minutes of air remain
 - Bottom Left: Telegraf to convert between different message formats, also displays all messages between components
 - Bottom Right: TeSSLa monitor raises an alarm, if the remaining time is to low.

### Terminate

To stop the all components and close the tmux session execute
```bash
lifecycle/terminate
```

### Clean

To remove temoporary files created by the Digital Twin execute
```bash
lifecycle/clean
```