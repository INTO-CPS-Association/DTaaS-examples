## Overview
This example is an implementation of the the paper Digital Twin for Rescue Missions--a Case Study by Leucker et al.: https://ceur-ws.org/Vol-3507/paper4.pdf

## Lifecycle

### Create

Before running the create script please download the `tessla-telegraf-connector.zip` from https://git.tessla.io/telegraf/tessla-telegraf-connector and extract its contents to `tools/tessla/tessla-telegraf-connector`.  
Also make sure all the files of this exampla are present at the correct locations as specified at the top of `lifecycle/create`.
Insert your MQTT server address, username, and password in `config.py` and `telegraf.conf`

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