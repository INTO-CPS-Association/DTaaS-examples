The model-swap is an extension to Maestro that enables the swapping during the execution of an FMI-based co-simulation of the present FMUs with new ones should user defined conditions be satisfied.
It is possible to change the whole structure of the co-simulation, by adding/removing connections, as wells as adding/removing FMUs.

This example has been taken from:
https://github.com/hejersbo/dtaas-wt-swap

This example demonstrates the following phases in the lifecycle of the DT:

1) installation of depenencies in create phase
2) generation of outputs in execute stage
3) self-triggered reconfiguration
4) script to analyze and produce plots
5) terminate to clean up the temporary files and outputs

