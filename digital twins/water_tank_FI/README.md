The fault-injection plugin is an extension to the Maestro co-orchestration engine that enables injecting inputs and outputs of FMUs in an FMI-based co-simulation with tampered values.
More details on the plugin can be found here: https://github.com/INTO-CPS-Association/fault-injection-maestro/tree/development.

This example has been taken from:

https://github.com/INTO-CPS-Association/fault-injection-maestro/blob/development/fi_example/README.md

and shows a fault injection (FI) enabled DT. In this case the watertank case-study is used, consisting
in a tank and controller, the goal of which is to keep the level of water in the tank between ```1``` and ```2```.
The output of the controller is injected, such that it is closed for a period of time, leading to the water level increasing in the tank beyond the desired level.

This example demonstrates the following phases in the lifecycle of the DT:

1) installation of depenencies in create phase
2) generation of outputs in execute stage
3) Visualisation of the results
4) terminate to clean up the temporary files and outputs

