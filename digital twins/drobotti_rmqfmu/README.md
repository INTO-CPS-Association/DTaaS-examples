This example demonstrates feeding data to the DT using the rabbitMQ FMU (RMQFMU).
In this example, the data consists in the ```xpos``` and ```ypos```.
The data goes to a distance FMU, that calculates the distance of the robot from point (0,0),
and send this back through the RMQFMU.
The following steps are covered:

1) installation of depenencies in create phase
2) generation of outputs in execute stage

Find the complete documentation for the RMQFMU [https://github.com/INTO-CPS-Association/fmu-rabbitmq/](here).