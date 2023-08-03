#!/bin/bash
printf "Preparing file with credentials...\n\n"
## From the DTaaS-examples
unzip /workspace/models/rmqfmu.fmu -d /tmp/rabbitmqfmu_flexcell
python /workspace/functions/flex-cell/prepare.py
cp /workspace/models/flex-cell/modelDescription.xml /tmp/rabbitmqfmu_flexcell/
cp /workspace/models/flex-cell/modelDescription.xml /tmp/rabbitmqfmu_flexcell/resources/
rm /workspace/models/flex-cell/rmqfmu_flexcell.fmu
(cd /tmp/rabbitmqfmu_flexcell && zip -r rmqfmu_flexcell.fmu .)
cp /tmp/rabbitmqfmu_flexcell/rmqfmu_flexcell.fmu /workspace/models/flex-cell/
rm -r /tmp/rabbitmqfmu_flexcell