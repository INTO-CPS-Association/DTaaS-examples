# Desktop Robotti DT

## Overview

This example demonstrates bidirectional communication between a mock physical twin and a digital twin of a mobile robot (Desktop Robotti).
The communication is enabled by RabbitMQ Broker.

The mock physical twin of mobile robot is created using two python scripts

1. data/drobotti_rmqfmu/rmq-publisher.py
1. data/drobotti_rmqfmu/consume.py

The mock physical twin sends its physical location in _(x,y)_ coordinates and
expects a cartesian distance _sqrt(x^2 + y^2)_ calculated from digital twin.

The _rmq-publisher.py_ reads the recorded _(x,y)_ physical coordinates of mobile robot.
The recorded values are available in __drobotti_playback_data.csv__.
These _(x,y)_ values are published to RabbitMQ Broker. The published _(x,y)_ values are
consumed by the digital twin.

The _consume.py_ subscribes to RabbitMQ Broker and waits for the the calculated distance value
from the digital twin.

The digital twin consists of a FMI-based co-simulation, where Maestro is used as co-orchestration engine.
In this case, the co-simulation is created by using two FMUs - RMQ FMU (rabbitmq-vhost.fmu)
and distance FMU (distance-from-zero.fmu). The RMQ FMU receives the _(x,y)_ coordinates from
_rmq-publisher.py_ and sends calculated distance value to _consume.py_. The RMQ FMU uses
RabbitMQ broker for communication with the mock mobile robot, i.e., _rmq-publisher.py_ and _consume.py_.
The distance FMU is responsible
for calculating the distance between _(0,0)_ and _(x,y)_. The RMQ FMU and distance FMU exchange values
during co-simulation.

## Configure

This example uses RabbitMQ broker and client services. Thus a working account
is needed on a RabbitMQ broker. The following credentials are required:

```ini
hostname: services.foo.com
username: foo
password: bar
port: 5672
vhost: vhost
```

These credentials are to be updated in two files:

1. multimodel.json
1. rabbitMQ-credentials.json

## Lifecycle Phases

The following lifecycle phases are covered:

1) __create__ - Installation of depenencies in create phase
2) __execute__ - Generation of outputs in execute stage
3) __clean__ - Clean-up after termination

## Results

Executing the DT will generate and launch a co-simulation (RMQFMU and distance FMU), and two python scripts.
One to publish data that is read from a file. And one to consume what is sent by the distance FMU.

In this examples the DT will run for 10 seconds, with a stepsize of 100ms. 
Thereafter it is possible to examine the logs produce in ```/workspace/examples/DTaaS-examples/digital_twins/drobotti_rmqfmu/target```.
The outputs for each FMU, xpos and ypos for the RMQFMU, and the distance for the distance FMU are recorded in the ```outputs.csv``` file.
Other logs can be examined for each FMU and the publisher scripts.
Note that, the RMQFMU only sends data, if the current input is different to the previous one.

## References

See the
[fmu-rabbitmq](https://github.com/INTO-CPS-Association/fmu-rabbitmq)
git repository for the complete source code and documentation of the RMQ FMU.

