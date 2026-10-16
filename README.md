[![Contributors](https://img.shields.io/github/contributors/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/graphs/contributors)
[![Latest Commit](https://img.shields.io/github/last-commit/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/commits/main)
[![INTO-CPS Association](https://img.shields.io/badge/INTO_CPS_Association-white)](https://into-cps.org/)

# DTaaS Examples

This repository contains examples for
[DTaaS software](https://github.com/into-cps-association/DTaaS)

Use these examples and follow the steps given in the example READMEs
to experience features of the DTaaS software platform and understand
best practices for managing digital twins within the platform.

You can also see a
[short video](https://odin.cps.digit.au.dk/into-cps/dtaas/assets/videos/cpsens.mp4)
on the use of DTaaS for creating a digital shadow. This video is recorded using
DTaaS v0.2.0.

## Workspace Layout

The examples are tested in the DTaaS workspace container
(`intocps/workspace:main-d27a3c2`, based on Ubuntu 24.04).
The workspace container expects two directories:

| Directory in container | Purpose | Contents from this repository |
|:---|:---|:---|
| `/workspace` | private files of a user | `digital_twins`, `data`, `functions`, `models`, `tools` |
| `/workspace/common` | files shared by all users | everything inside `common/` |

The lifecycle scripts of the examples use these absolute paths.

## Copy Examples

The first step is to copy all the example code into your
user workspace within the DTaaS.
Use the given shell script to copy the private assets
into `/workspace` and the common assets into `/workspace/common`.

```bash
wget https://raw.githubusercontent.com/INTO-CPS-Association/DTaaS-examples/main/getExamples.sh
bash getExamples.sh
```

## Try the Examples Locally

You can also run the examples in a standalone workspace container.
Create the private and common directories, copy the examples into them
and start the workspace container with both directories mounted.

```bash
mkdir -p files/user1 files/common
git clone https://github.com/INTO-CPS-Association/DTaaS-examples.git
for asset in digital_twins data functions models tools; do
  cp -r DTaaS-examples/${asset} files/user1/
done
cp -r DTaaS-examples/common/. files/common/

docker run -d --shm-size=512m -p 8080:8080 \
  -e MAIN_USER=user1 -e USER_PW=<password> \
  -v "$PWD/files/user1:/workspace" \
  -v "$PWD/files/common:/workspace/common" \
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

## External Services

Some examples need external services to be running.

| Example | Services needed |
|:---|:---|
| [Mass Spring Damper](./digital_twins/mass-spring-damper/README.md) | None |
| [Mass Spring Damper with NuRV monitor](./digital_twins/mass-spring-damper-monitor/README.md) | None |
| [Water Tank Fault Injection](./digital_twins/water_tank_FI/README.md) | None |
| [Water Tank Fault Injection with NuRV monitor](./digital_twins/water_tank_FI_monitor/README.md) | None |
| [Water Tank Model Swap](./digital_twins/water_tank_swap/README.md) | None |
| [Incubator NuRV monitor validation](./digital_twins/incubator-NuRV-monitor-validation/README.md) | None |
| [Three Water Tanks](./digital_twins/three-tank/README.md) | None |
| [Water Treatment Plant and OPC-UA](./digital_twins/opc-ua-waterplant/README.md) | None (uses a mock OPC-UA server) |
| [Heart Digital Twin](./digital_twins/heart_dt/README.md) | None |
| [Desktop Robotti and RabbitMQ](./digital_twins/drobotti_rmqfmu/README.md) | RabbitMQ |
| [Flex Cell](./digital_twins/flex-cell/README.md) | RabbitMQ |
| [Incubator](./digital_twins/incubator/README.md) and its variants | RabbitMQ, InfluxDB |
| [Firefighters in Emergency Environments](./digital_twins/o5g/README.md) | MQTT, InfluxDB |

## Example List

The digital twins provided in examples vary in their complexity. It is best
to use the examples in the following order.

1. [Mass Spring Damper](./digital_twins/mass-spring-damper/README.md)
1. [Water Tank Fault Injection](./digital_twins/water_tank_FI/README.md)
1. [Water Tank Model Swap](./digital_twins/water_tank_swap/README.md)
1. [Desktop Robotti and RabbitMQ](./digital_twins/drobotti_rmqfmu/README.md)
1. [Water Treatment Plant and OPC-UA](./digital_twins/opc-ua-waterplant/README.md)
1. [Three Water Tanks with DT Manager Framework](./digital_twins/three-tank/README.md)
1. [Flex Cell with Two Industrial Robots](./digital_twins/flex-cell/README.md)
1. [Incubator](./digital_twins/incubator/README.md)
1. [Firefighters in Emergency Environments](./digital_twins/o5g/README.md)
1. [Incubator with NuRV run-time monitor service](./digital_twins/incubator-NuRV-monitor-service/README.md)
