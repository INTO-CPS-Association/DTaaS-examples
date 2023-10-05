#!/bin/bash
printf "Preparing file with credentials...\n\n"
## From the DTaaS-examples
unzip /workspace/examples/models/rmqfmu.fmu -d /tmp/rabbitmqfmu_flexcell
python /workspace/examples/functions/flex-cell/prepare.py
cp /workspace/examples/models/flex-cell/modelDescription.xml /tmp/rabbitmqfmu_flexcell/
cp /workspace/examples/models/flex-cell/modelDescription.xml /tmp/rabbitmqfmu_flexcell/resources/
rm /workspace/examples/models/flex-cell/rmqfmu_flexcell.fmu
(cd /tmp/rabbitmqfmu_flexcell && zip -r rmqfmu_flexcell.fmu .)
cp /tmp/rabbitmqfmu_flexcell/rmqfmu_flexcell.fmu /workspace/examples/models/flex-cell/
rm -r /tmp/rabbitmqfmu_flexcell