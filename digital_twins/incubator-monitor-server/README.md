# Incubator Digital Twin with NuRV monitoring service

## Overview

This example demonstrates how a runtime monitoring service (in this example NuRV[1]) can be connected with the Incubator Digital Twin (DT)[2] to verify runtime behavior of the Incubator.

## Simulated scenario

This example simulates a scenario where the lid of the Incubator is removed and later put back on. The Incubator is equipped with anomaly detection capabilities, which can detect anomalous behavior (i.e. the removal of the lid). When an anomaly is detected, the Incubator then triggers an energy saving mode where the heater is turned off. 

From a monitoring perspective, we wish to verify that within 3 simulation steps of an anomaly detection, the energy saving mode is turned on. To verify this behavior, we construct the property $anomaly \rightarrow F [ 0, 3 ] energy_saving$. Whenever a True or False verdict is produced by the monitor, it is reset, allowing for the detection of repeated satisfaction/violation detections of the property.

The simulated scenario progresses as follows:

- *Initialization*: The services are initialized and the Kalman filter in the Incubator is given 2 minutes to stabilize. Sometimes, the anomaly detection algorithm will detect an anomaly at startup even though the lid is still on. It will disappear after approx 15 seconds.
- *After 2 minutes*: The lid is lifted and an anomaly is detected. The energy saver is turned on shortly after
- *After another 30 seconds*: The energy saver is manually disabled producing a False verdict.
- *After another 30 seconds*: The lid is put back on and the anomaly detection is given time to detect that the lid is back on. The simulation then ends. 


## Digital Twin configuration

Before running the example, please configure the _simulation.conf_ file (located in /digital_twins/incubator-monitor-server/incubator/) with your RabbitMQ credentials and address to your RabbitMQ instance (vhost is also required).

## Lifecycle phases

The lifecycle phases for this example include:

| Lifecycle phase | Completed tasks |
| ------ | ------- |
| Create    | Downloads the necessary tools and creates a virtual python environment with the necessary dependencies |
| Execute   | Runs a python script that starts up the necessary services as well as the Incubator simulation. Various status messages are printed to the console, including the monitored system states and monitor verdict. |
| Clean     | Removes created _data_ directory. |

If required, change the execute permissions of lifecycle scripts you need to execute. This can be done using the following command 
```bash
chmod +x lifecycle/{script}
```
where {script} is the name of the script, e.g. _create_, _execute_ etc. 


## Running the example

To run the example, first run the following command in a terminal:
```bash
cd /workspace/examples/digital_twins/incubator-monitor-server/
```
Then, first execute the _create_ script (this can take a few mins depending on your network connection) followed by the _execute_ script using the following command:
```bash
lifecycle/{script}
```

The _execute_ script will then start outputting system states and the monitor verdict approx every 3 seconds. The output is printed as follows $State: {anomaly state} & {energy_saving state}, verdict: {Verdict}$ where "anomaly" indicates that an anomaly is detected and "!anomaly" indicates that an anomaly is not currently detected. The same format is used for the energy_saving state.
The monitor verdict can be True, False or Unknown, where the latter indicates that the monitor does not yet have sufficient information to determine the satisfaction of the property.

There is currently some startup issues with connecting to the NuRV server, and it will likely take a few tries before the connection is established. This is however handled automatically.

## References

[1]: Information on the NuRV monitor can be found here: https://es-static.fbk.eu/tools/nurv/
[2]: The code used to simulate the Incubator can be found here: [https://github.com/INTO-CPS-Association/example_digital-twin_incubator/](https://github.com/INTO-CPS-Association/example_digital-twin_incubator/) (commit 989ccf5).
