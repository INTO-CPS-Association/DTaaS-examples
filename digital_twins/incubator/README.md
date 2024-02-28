# Incubator Digital Twin

## Overview

This is a case study of an Incubator with the purpose of understanding the steps and processes involved in developing a digital twin system. This incubator is an insulated container with the ability to keep a temperature and heat, but not cool.

The overall purpose of the system is to reach a certain temperature within a box and keep the temperature regardless of content.
An overview of the system can be seen below:

![Incubator](figures/system.svg)

The system consists of:
- 1x styrofoam box in order to have an insulated container
- 1x heat source to heat up the content within the Styrofoam box.
- 1x fan to distribute the heating within the box
- 2x temperature sensor to monitor the temperature within the box
- 1x temperature Sensor to monitor the temperature outside the box
- 1x controller to actuate the heat source and the fan and read sensory information from the temperature sensors, and communicate with the digital twin.

The original repository for the example can be found: [Orignal repository](https://github.com/INTO-CPS-Association/example_digital-twin_incubator/).<br>
This version of the example deviates from the original as it does not use docker for instantiating the dependencies.

The original repository contains the complete documentation of the example, including the full system architecture, instructions for running with a physical twin, and instructions for running a 3D visualization of the incubator.

## Example Structure

![System overview of the incubator](figures/L0_Communication.svg)

## Digital Twin Configuration

This example uses a plethora of Python scripts to run the digital twin. By default it is configured to run with a mock physical twin. Furthermore, it depends on a RabbitMQ and an InfluxDB instance.

| Asset Type | Names of Assets | Visibility | Reuse in Other Examples |
|:---|:---|:---|:---|
| Model | incubator/mock_plant/real_time_model_solver.py | Private | No |
| Data | incubator/log.log | Private | No |

This DT has a single configuration file: _simulation.conf_

## Lifecycle Phases

The lifecycles that are covered include:

| Lifecycle Phase    | Completed Tasks |
| --------- | ------- |
| Create    | Potentially updates the system and installs Python dependencies |
| Execute   | Executes the Incubator digital twin and produces output in the terminal and in _incubator/log.log_. |
| Clean     | Removes the log file. |

## Run the example

To run the example, change your present directory.

```bash
cd /workspace/examples/digital_twins/incubator
```

If required, change the execute permission of lifecycle scripts
you need to execute, for example:

```bash
chmod +x lifecycle/create
```

Now, run the following scripts:

### Create

Potentially updates the system and installs Python dependencies.

```bash
lifecycle/create
```

### Execute

Executes the Incubator digital twin with a mock physical twin. Pushes the results in the terminal, _incubator/log.log_, and in InfluxDB.

```bash
lifecycle/execute
```

### Clean

Removes the output log file.

```bash
lifecycle/clean
```

## Examining the results

After starting all services successfully, the controller service will start producing output that looks like the following:
````
time           execution_interval  elapsed  heater_on  fan_on   room   box_air_temperature  state 
19/11 16:17:59  3.00                0.01     True       False   10.70  19.68                Heating
19/11 16:18:02  3.00                0.03     True       True    10.70  19.57                Heating
19/11 16:18:05  3.00                0.01     True       True    10.70  19.57                Heating
19/11 16:18:08  3.00                0.01     True       True    10.69  19.47                Heating
19/11 16:18:11  3.00                0.01     True       True    10.69  19.41                Heating
````

## References

To understand what a digital twin is, we recommend you read/watch one or more of the following resources:
- Feng, Hao, Cláudio Gomes, Casper Thule, Kenneth Lausdahl, Alexandros Iosifidis, and Peter Gorm Larsen. “Introduction to Digital Twin Engineering.” In 2021 Annual Modeling and Simulation Conference (ANNSIM), 1–12. Fairfax, VA, USA: IEEE, 2021. https://doi.org/10.23919/ANNSIM52504.2021.9552135.
- [Claudio's presentation at Aarhus IT](https://videos.ida.dk/media/Introduction+to+Digital+Twin+Engineering+with+Cl%C3%A1udio+%C3%82ngelo+Gon%C3%A7alves+Gomes%2C+Aarhus+Universitet/1_7r1j05g8/256930613)
