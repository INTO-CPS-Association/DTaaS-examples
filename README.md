[![Maintainability](https://api.codeclimate.com/v1/badges/a413d543fc310a630ac8/maintainability)](https://codeclimate.com/github/INTO-CPS-Association/DTaaS-examples/maintainability)
[![Contributors](https://img.shields.io/github/contributors/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/graphs/contributors)
[![Latest Commit](https://img.shields.io/github/last-commit/INTO-CPS-Association/DTaaS-Examples)](https://github.com/INTO-CPS-Association/DTaaS-Examples/commits/main)
[![INTO-CPS Association](https://img.shields.io/badge/INTO_CPS_Association-white)](https://into-cps.org/)



The order of digital twin examples to work through:

1. Mass Spring Damper
2. water Tank FI
3. Water Tank Swap


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

1. [Mass Spring Damper](./mass-spring-damper/README.md)
1. [Water Tank Fault Injection](./water_tank_FI/README.md)
1. [Water Tank Model Swap](./water_tank_swap/README.md)
1. [Desktop Robotti and RabbitMQ](./drobotti-rmqfmu/README.md)
1. [Water Treatment Plant and OPC-UA](./opc-ua-waterplant/README.md)
1. [Three Water Tanks with DT Manager Framework](./three-tank/README.md)
