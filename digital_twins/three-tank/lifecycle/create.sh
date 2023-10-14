#!/bin/bash
printf "Installing dependencies...\n\n"
apt-get install default-jre ## Minimum java 1.8
apt-get install maven
mvn -f /workspace/examples/tools/DTManager/pom.xml package
cp /workspace/examples/tools/DTManager/target/DTManager-0.0.1-Maestro.jar /workspace/examples/tools/
if [ ! -d /workspace/examples/data/three-tank/output ]; then
    mkdir /workspace/examples/data/three-tank/output
fi