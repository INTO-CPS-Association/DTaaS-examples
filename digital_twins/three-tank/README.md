# Three-Tank System Digital Twin

## Overview

The three-tank system is a simple case study allows us to represent
a system that is composed of three individual components that are coupled
in a cascade as follows:
The first tank is connected to the input of the second tank, and the output
of the second tank is connected to the input of the third tank.

This example contains only the simulated components for demonstration
purposes; therefore, there is no configuration for the connection with
the physical system.

The three-tank system case study is managed using the ```DTManager```,
which is packed as a jar library in the tools, and run from a java main file.
The ```DTManager``` uses Maestro as a slave for co-simulation,
so it generates the output of the co-simulation.
The main file can be changed according to the application scope,
i.e., the ```/workspace/examples/tools/three-tank/TankMain.java```
can be manipulated to get a different result.

The ```/workspace/examples/models/three-tank/``` folder contains
the ```Linear.fmu``` file, which is a non-realistic model for a tank
with input and output and the ```TankSystem.aasx``` file for the schema
representation with Asset Administration Shell.
The three instances use the same ```.fmu``` file and the same schema
due to being of the same object class.
The ```DTManager``` is in charge of reading the values from
the co-simulation output.

The lifecycles that are covered include:

1. Installation of dependencies in the create phase.
2. Execution of the experiment in the execution phase.
3. Terminating the background processes and cleaning up the outputs
   in the termination phase.

This example demonstrates: create, execute and terminate phases

## Create phase

Installs _Open Java Development Kit 17_ and _maven_ in the workspace.
This project uses **DTManager** tool which is a maven project.
The create phase builds the **DTManager** tool.

```bash
lifecycle/create
```

## Execute phase

Run the co-simulation. Generate the co-simulation output.csv file
at `data/mass-spring-damper/output/output.csv`.

There are also debug and maestro log files stored in
`data/mass-spring-damper/output` directory.

```bash
lifecycle/execute
```

## Terminate phase

Terminate to clean up the debug files and co-simulation output.

```bash
lifecycle/terminate
```

The order the run this example is:

1. Run the create script file with
   ```/workspace/examples/digital_twins/three-tank/lifecycle/create```.
   In case of error, be sure the installed version of Java is OpenJDK 11,
   otherwise, install manually the OpenJDK 11 and use the command
   ```update-java-alternatives``` to set the Java version to be OpenJDK 11
   and rerun the ```create``` script.
2. Execute the Digital Twin with the script file
   ```/workspace/examples/digital_twins/three-tank/lifecycle/execute```.
3. Terminate the background processes with the script file
   ```/workspace/examples/digital_twins/three-tank/lifecycle/terminate```.
4. (Optional) clean up the output folder with the script file
   ```/workspace/examples/digital_twins/three-tank/lifecycle/clean```.

## Examining the results

Executing this Digital Twin will generate a co-simulation output,
but the results can also be monitored from updating the
```/workspace/examples/tools/three-tank/TankMain.java``` with
a specific set of ```getAttributeValue``` commands, such as shown
in the code.

That main file enables the online execution of the Digital Twin
and its internal components.

The output of the co-simulation is generated to the
```/workspace/examples/data/three-tank/output``` folder.

In the default example, the co-simulation is run for 10 seconds
in steps of 0.5 seconds.
This can be modified for a longer period and different step size.
The output stored in ```outputs.csv``` contains the level,
in/out flow, and leak values.

No data from the physical twin are generated/used.
