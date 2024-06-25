# Incubator Digital Twin with TeSSLa monitoring service

## Overview

This example demonstrates how the runtime monitoring service [TeSSLa](https://www.tessla.io) can be connected with the [Incubator digital twin](../../common/digital_twins/incubator/README.md) to verify the runtime behavior of the Incubator. TeSSLa provides passive monitoring capabilities to observe state changes and trigger alerts based on specific conditions. This example is designed to illustrate the application of runtime monitoring to ensure that the Incubator's operations align with desired safety and efficiency parameters.

In this scenario, the Incubator is tasked with maintaining a controlled environment for sensitive biological samples. The primary focus is on monitoring the status of the incubator's lid and the activation state of its energy-saving mode. The monitoring system ensures that if the lid is open, the energy-saving mode activates within three simulation steps to mitigate any loss of controlled environment, conserving energy and maintaining stability. This setup models a typical safety and operational protocol in biological sample storage, where maintaining constant internal conditions is critical.

The TeSSLa monitor uses event streams to detect changes in the lid state and energy-saving mode. It computes these states to determine compliance with the operational rules specified. If the TeSSLa monitor detects that the energy-saving mode does not activate promptly after the lid is opened, it triggers an alert, indicating a potential safety violation. This monitoring is crucial as it provides real-time oversight, allowing for immediate corrective actions to be taken before any damage to the biological samples can occur.

The setup includes a Telegraf component that facilitates the connection between the physical components of the Incubator and the TeSSLa monitor. Telegraf collects data from the Incubator's sensors and forwards this data to the TeSSLa monitor for analysis. This integration not only ensures seamless data flow but also enhances the system's ability to adapt to configuration changes without needing a system restart, making the monitoring system both robust and flexible.

By monitoring these critical aspects of the Incubator’s operation, the TeSSLa-based system helps maintain the necessary conditions for sample integrity and energy efficiency, illustrating an effective application of digital twin technology in a high-stakes environment.

## Key Components and Their Roles

![](https://md.isp.uni-luebeck.de/uploads/upload_6501e52a2ec8501f183272afc3c26c17.png)


The diagram illustrates the integration of various components within a Digital Twins as a Service (DTaaS) platform, designed to monitor and control a physical system (Physical Twin).

1. **Physical Twin:**
   - This is the actual physical object or system being monitored, sending data to the RabbitMQ server which relays it to the digital counterpart.

2. **Digital Twin:**
   - A virtual model of the Physical Twin, receiving and processing real-time data from the RabbitMQ server to simulate and analyse the physical system’s state.

3. **RabbitMQ Server (Platform Service):**
   - Acts as a message broker, coordinating data communication between the Physical Twin and the Digital Twin, along with other services.

4. **Telegraf:**
   - A server agent used for collecting, processing, and passing on metrics and data from the Digital Twin to TeSSLa.

5. **Connector:**
   - Facilitates data transfer between Telegraf and TeSSLa, ensuring smooth integration of data streams into the monitoring process.

6. **TeSSLa:**
   - Monitors the state and activities of the Physical Twin based on predefined specifications and outputs results indicating system performance.

### Interaction Overview:
Data flows from the Physical Twin to the RabbitMQ Server, and onward to the Digital Twin. It is then channelled through Telegraf and the Connector to TeSSLa for analysis. The outcomes of this analysis are sent back, helping make operational or maintenance decisions regarding the Physical Twin.


## Lifecycle Phases

The lifecycle for this example includes the setup, execution, and cleanup of the monitoring environment:

| Lifecycle phase | Completed tasks                                    |
|-----------------|----------------------------------------------------|
| create          | Set up the environment and install necessary tools |
| execute         | Start the monitoring service and simulate scenarios |
| terminate       | Remove temporary files and logs                    |

To adjust the script execution permissions, use:
```bash
chmod +x lifecycle/{script}
```

## Running the Example

Navigate to the example directory and execute the lifecycle scripts:
```bash
cd /workspace/examples/digital_twins/incubator-tessla-monitor-service/
```

Run the _create_ script to install necessary components:
```bash
lifecycle/create
```

Execute the _execute_ script to start the simulation:
```bash
lifecycle/execute
```

The output is printed every few seconds, showing the current state and the verdict.
