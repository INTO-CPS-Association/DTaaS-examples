# Desktop Robotti DT

## Overview

This example demonstrates feeding data to the DT using the rabbitMQ FMU (RMQFMU).
In this example, the data consists in the ```xpos``` and ```ypos```.
The DT consists of the RMQFMU and a distance FMU.
The ```xpos``` and ```ypos``` go from the RMQFMU to the distance FMU, which calculates the distance of the robot based on the received position from point (0,0), which is then fed to the RMQFMU as input..
Thereafter the distance is send out externally through RMQFMU, which publishes a message to the rabbitMQ server.

The following steps are covered:

1) Installation of depenencies in create phase
2) Generation of outputs in execute stage
3) Clean-up after termination

Find the complete documentation for the RMQFMU here: https://github.com/INTO-CPS-Association/fmu-rabbitmq.

## Examining the results

Executing the DT will generate and launch a co-simulation (RMQFMU and distance FMU), and two python scripts.
One to publish data that is read from a file. And one to consume what is sent by the distance FMU.

In this examples the DT will run for 10 seconds, with a stepsize of 100ms. 
Thereafter it is possible to examine the logs produce in ```/workspace/DTaaS-examples/digital twins/drobotti_rmqfmu/target```.
The outputs for each FMU, xpos and ypos for the RMQFMU, and the distance for the distance FMU are recorded in the ```outputs.csv``` file.
Other logs can be examined for each FMU and the publisher scripts. 
Note that, the RMQFMU only sends data, if the current input is different to the previous one.

