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

## Copy Examples

The first step is to copy all the example code into your
user workspace within the DTaaS.
Use the given shell script to copy all the examples
into `/workspace/examples` directory.

```bash
wget https://raw.githubusercontent.com/INTO-CPS-Association/DTaaS-examples/main/getExamples.sh
bash getExamples.sh
```

## Example List

The digital twins provided in examples vary in their complexity. It is best
to use the examples in the following order.

1. [Mass Spring Damper](./digital_twins/mass-spring-damper/README.md)
1. [Water Tank Fault Injection](./digital_twins/water_tank_FI/README.md)
1. [Water Tank Model Swap](./digital_twins/water_tank_swap/README.md)
1. [Desktop Robotti and RabbitMQ](./digital_twins/drobotti-rmqfmu/README.md)
1. [Water Treatment Plant and OPC-UA](./digital_twins/opc-ua-waterplant/README.md)
1. [Three Water Tanks with DT Manager Framework](./digital_twins/three-tank/README.md)
1. [Flex Cell with Two Industrial Robots](./digital_twins/flex-cell/README.md)
1. [Incubator](./digital_twins/incubator/README.md)
1. [Firefighters in Emergency Environments](./digital_twins/o5g/README.md)
1. [Incubator with NuRV run-time monitor service](./incubator-NuRV-monitor-service/README.md)
