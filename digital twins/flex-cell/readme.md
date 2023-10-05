# Flex-cell Digital Twin
## Overview
The flex-cell Digital Twin is a case study with two industrial robotic arms, a UR5e and a Kuka LBR iiwa 7, working in a cooperative setting on a manufacturing cell.

The case study focuses on the robot positioning in the discrete cartesian space of the flex-cell working space.
Therefore, it is possible to send (X,Y,Z) commands to both robots, which refer to the target hole and height they want should move to.

The flex-cell case study is managed using the ```DTManager```, which is packed as a jar library in the tools, and run from a java main file.
The ```DTManager``` uses Maestro as a slave for co-simulation, so it generates the output of the co-simulation and can interact with the real robots at the same time (with the proper configuration and setup).
The mainfile can be changed according to the application scope, i.e., the ```/workspace/examples/tools/flex-cell/FlexCellMain.java``` can be manipulated to get a different result.

The ```/workspace/examples/models/flex-cell/``` folder contains the ```.fmu``` files for the kinematic models of the robotic arms, the ```.urdf``` files for visualization (including the grippers), and the ```.aasx``` files for the schema representation with Asset Administration Shell.
The case study also uses RabbitMQFMU to inject values into the co-simulation, therefore, there is the rabbitmqfmu in the models folder as well.
Right now, RabbitMQFMU is only used for injecting values into the co-simulation, but not the other way around.
The ```DTManager``` is in charge of reading the values from the co-simulation output and the current state of the physical twins.

The lifecycles that are covered include:
1. Installation of dependencies in the create phase.
2. Preparing the credentials for connections in the prepare phase.
3. Execution of the experiment in the execution phase.
4. Saving experiments in the save phase.
5. Plotting the results of the co-simulation and the real data coming from the robots in the analyze phase.
6. Terminating the background processes and cleaning up the outputs in the termination phase.

The order the run this example is:
1. Run the create script file with ```/workspace/examples/digital twins/flex-cell/lifecycle/create.sh```. In case of error, be sure the installed version of Java is OpenJDK 11, otherwise, install manually the OpenJDK 11 and use the command ```update-java-alternatives``` to set the Java version to be OpenJDK 11 and rerun the ```create.sh``` script.
2. Set up the credentials in the ```/workspace/examples/data/flex-cell/connections.conf``` and run the script file ```./workspace/examples/digital twins/flex-cell/lifecycle/prepare.sh```.
3. Execute the Digital Twin with the script file ```/workspace/examples/digital twins/flex-cell/lifecycle/execute.sh```.
4. (Optional) save the results with the script file ```/workspace/examples/digital twins/flex-cell/lifecycle/save.sh```.
5. (Optional) plot the results with the script file ```/workspace/examples/digital twins/flex-cell/lifecycle/analyze.sh```, which saves the plots in the folder ```/workspace/examples/data/flex-cell/output```.
6. Terminate the background processes with the script file ```/workspace/examples/digital twins/flex-cell/lifecycle/terminate.sh```. This one is required before running an execution again.
7. (Optional) clean up the output folder with the script file ```/workspace/examples/digital twins/flex-cell/lifecycle/clean.sh```. **Remark**: This command also removes the files in the ```physical_twin``` subfolder with the data from the real robots.

## Examining the results
Executing this Digital Twin will generate a co-simulation output, but the results can also be monitored from updating the ```/workspace/examples/tools/flex-cell/FlexCellMain.java``` with a specific set of ```getAttributeValue``` commands, such as shown in the code.
That main file enables the online execution and comparison on Digital Twin and Physical Twin at the same time and at the same abstraction level.

The output is generated to the ```/workspace/examples/data/flex-cell/output``` folder.
In case a specific experiments is to be saved, the ```save``` lifecycle script stores the co-simulation results into the ```/workspace/examples/data/flex-cell/output/saved_experiments``` folder.

In the default example, the co-simulation is run for 10 seconds in steps of 0.5 seconds.
This can be modified for a longer period and different step size.
The output stored in ```outputs.csv``` contains the joint position of both robotic arms and the current discrete (X,Y,Z) position of the TCP of the robot.
Additional variables can be added, such as the discrete (X,Y,Z) position of the other joints.

When connected to the real robots, the tools ```urinterface``` and ```kukalbrinterface``` log their data at a higher sampling rate.


## Connection setup
The files ```/workspace/examples/digital twins/flex-cell/kuka_actual.conf```, ```/workspace/examples/digital twins/flex-cell/ur5e_actual.conf```, ```/workspace/examples/tools/flex-cell/publisher-flexcell-physical.py```, and the ```modelDescription.xml``` for the RabbitMQFMU require special credentials to connect to the RabbitMQ and the MQTT brokers.

The script file  ```/workspace/examples/digital twins/flex-cell/lifecycle/prepare.sh``` helps you to set up the credentials and connection parameters easily.
The only thing needed to set up the connection is to update the file ```/workspace/examples/data/flex-cell/connections.conf``` with the connection parameters for MQTT and RabbitMQ and then execute the ```prepare.sh``` script.
The script will set up the RabbitMQFMU and config files for this example for you.
