[![Contributors](https://img.shields.io/github/contributors/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/graphs/contributors)
[![Latest Commit](https://img.shields.io/github/last-commit/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/commits/main)
[![INTO-CPS Association](https://img.shields.io/badge/INTO_CPS_Association-white)](https://into-cps.org/)

# DTaaS Examples

This repository contains example digital twins for the
[DTaaS software](https://github.com/into-cps-association/DTaaS).
These digital twins run interactively inside the DTaaS user workspace.
Work through the steps in the README of each example to try the features
of the platform and to learn good practice for managing digital twins
on it.

The following
[slides](https://odin.cps.digit.au.dk/into-cps/dtaas/assets/20240917-Examples.pdf)
and
[video](https://odin.cps.digit.au.dk/into-cps/dtaas/assets/videos/20240917-Examples-Recorded-web.mp4)
give an overview of these examples.
A [short video](https://odin.cps.digit.au.dk/into-cps/dtaas/assets/videos/cpsens.mp4)
shows the use of DTaaS for creating a digital shadow. This video is
recorded using DTaaS v0.2.0.

## Copy Examples

Copy all the example code into the user workspace with this script:

```bash
wget https://raw.githubusercontent.com/INTO-CPS-Association/DTaaS-examples/main/getExamples.sh
bash getExamples.sh
```

This copies all examples into the `/workspace/examples` directory.

The script also works when run as root. The examples are then given to
the user who ran `sudo`, or to the owner of the directory containing
the examples, so that the workspace user can run them.
Set `REPOSITORY` and `BRANCH` to download the examples from another
repository or branch, for example
`REPOSITORY=<user>/DTaaS-examples BRANCH=<branch> bash getExamples.sh`.

The lifecycle scripts locate the models, tools, data and common assets
relative to their own location. The examples work from
`/workspace/examples` and from any other directory that contains
a copy of this repository.

## Try the Examples Locally

The examples are tested in the DTaaS workspace container
(`intocps/workspace:main-d27a3c2`, based on Ubuntu 24.04).
You can run the examples in a standalone workspace container.

```bash
mkdir -p files/user1
git clone https://github.com/INTO-CPS-Association/DTaaS-examples.git \
  files/user1/examples

docker run -d --shm-size=512m -p 8080:8080 \
  -e MAIN_USER=user1 -e USER_PW=<password> \
  -v "$PWD/files/user1:/workspace" \
  --name workspace intocps/workspace:main-d27a3c2
```

Open a terminal in the workspace using one of
[VS Code](http://localhost:8080/user1/tools/vscode),
[Jupyter Lab](http://localhost:8080/user1/lab) or
[the desktop](http://localhost:8080/user1/tools/vnc).
You can also use a shell from the host:

```bash
docker exec -it -u user1 workspace bash
```

The workspace user is not root. The lifecycle scripts use `sudo` to install
the required system packages. The `sudo` command asks for the password
given in `USER_PW`.

:warning: Ubuntu 24.04 does not allow installation of pip packages
into the system Python. The examples either install the Python packages
from the Ubuntu repositories (`python3-*` apt packages) or create
a Python virtual environment inside the digital twin directory.

## Example List

The examples vary in complexity. Try them in the following order.
Some examples need external services, such as RabbitMQ, MQTT or InfluxDB,
to be running and reachable from the workspace. Configure the access
details of these services as described in the README of each example.
The demo video of each example shows it running in a terminal of the
workspace desktop of DTaaS v1.0 (`workspace-dex-localhost` installation).
The videos are sped up: results play at normal speed, installations and
long runs at 16x, and everything else at 4x.

| # | Example | External services | Video |
|--:|:---|:---|:---|
| 1 | [Mass Spring Damper](./digital_twins/mass-spring-damper/README.md) | None | [demo](./digital_twins/mass-spring-damper/demo.mp4) |
| 2 | [Water Tank Fault Injection](./digital_twins/water_tank_FI/README.md) | None | [demo](./digital_twins/water_tank_FI/demo.mp4) |
| 3 | [Water Tank Model Swap](./digital_twins/water_tank_swap/README.md) | None | [demo](./digital_twins/water_tank_swap/demo.mp4) |
| 4 | [Heart Digital Twin](./digital_twins/heart_dt/README.md) | None | [demo](./digital_twins/heart_dt/demo.mp4) |
| 5 | [Desktop Robotti and RabbitMQ](./digital_twins/drobotti_rmqfmu/README.md) | RabbitMQ | [demo](./digital_twins/drobotti_rmqfmu/demo.mp4) |
| 6 | [Water Treatment Plant and OPC-UA](./digital_twins/opc-ua-waterplant/README.md) | None (uses a mock OPC-UA server) | [demo](./digital_twins/opc-ua-waterplant/demo.mp4) |
| 7 | [Water Treatment Plant and OPC-UA (complete version, without lifecycle scripts)](./digital_twins/opc-ua-waterplant-complete/README.md) | OPC-UA server (mock servers included) | – |
| 8 | [Three Water Tanks with TwinManager Framework](./digital_twins/three-tank/README.md) | None | [demo](./digital_twins/three-tank/demo.mp4) |
| 9 | [Flex Cell with Two Industrial Robots](./digital_twins/flex-cell/README.md) | RabbitMQ, MQTT | [demo](./digital_twins/flex-cell/demo.mp4) |
| 10 | [Incubator](./digital_twins/incubator/README.md) | RabbitMQ, InfluxDB | [demo](./digital_twins/incubator/demo.mp4) |
| 11 | [Firefighters in Emergency Environments](./digital_twins/o5g/README.md) | MQTT, InfluxDB | [demo](./digital_twins/o5g/demo.mp4) |
| 12 | [Mass Spring Damper with NuRV Runtime Monitor FMU](./digital_twins/mass-spring-damper-monitor/README.md) | None | [demo](./digital_twins/mass-spring-damper-monitor/demo.mp4) |
| 13 | [Water Tank Fault Injection with NuRV Runtime Monitor FMU](./digital_twins/water_tank_FI_monitor/README.md) | None | [demo](./digital_twins/water_tank_FI_monitor/demo.mp4) |
| 14 | [Incubator Co-Simulation with NuRV Runtime Monitor FMU](./digital_twins/incubator-NuRV-monitor-validation/README.md) | None | [demo](./digital_twins/incubator-NuRV-monitor-validation/demo.mp4) |
| 15 | [Incubator with NuRV Runtime Monitor as Service](./digital_twins/incubator-NuRV-monitor-service/README.md) | RabbitMQ, InfluxDB | [demo](./digital_twins/incubator-NuRV-monitor-service/demo.mp4) |
| 16 | [Incubator with NuRV Runtime Monitor FMU as Service](./digital_twins/incubator-NuRV-fmu-monitor-service/README.md) | RabbitMQ, InfluxDB | [demo](./digital_twins/incubator-NuRV-fmu-monitor-service/demo.mp4) |
| 17 | [Incubator with TeSSLa Runtime Monitor as Service](./digital_twins/incubator-TeSSLa-monitor-service/README.md) | RabbitMQ, InfluxDB | [demo](./digital_twins/incubator-TeSSLa-monitor-service/demo.mp4) |
| 18 | [Incubator with TeSSLa Runtime Monitor for Active Control](./digital_twins/incubator-TeSSLa-active-control/README.md) | RabbitMQ, InfluxDB | [demo](./digital_twins/incubator-TeSSLa-active-control/demo.mp4) |
| 19 | [BIM - Building Information Modeling](./digital_twins/fzk_haus/README.md) | MQTT | [demo](./digital_twins/fzk_haus/demo.mp4) |
