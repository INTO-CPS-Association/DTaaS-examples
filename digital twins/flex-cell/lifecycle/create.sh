#!/bin/bash
printf "Installing dependencies...\n\n"
apt-get install default-jre ## Minimum java 1.8
apt-get install maven
mvn -f /workspace/examples/tools/DTManager/pom.xml package
cp /workspace/examples/tools/DTManager/target/DTManager-0.0.1-Maestro.jar /workspace/examples/tools/
pip install -r /workspace/examples/tools/flex-cell/requirements/requirements.txt
if [ ! -d /workspace/examples/data/flex-cell/output ]; then
    mkdir /workspace/examples/data/flex-cell/output
fi
if [ ! -d /workspace/examples/data/flex-cell/output/physical_twin ]; then
    mkdir /workspace/examples/data/flex-cell/output/physical_twin
fi