#!/bin/bash
printf "Installing dependencies...\n\n"
apt-get install default-jre ## Minimum java 1.8
apt-get install maven
mvn -f /workspace/tools/DTManager/pom.xml package
cp /workspace/tools/DTManager/target/DTManager-0.0.1-Maestro.jar /workspace/tools/
if [ ! -d /workspace/data/three-tank/output ]; then
    mkdir /workspace/data/three-tank/output
fi