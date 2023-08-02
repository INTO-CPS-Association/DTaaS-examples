#!/bin/bash
printf "Installing dependencies...\n\n"
apt-get install default-jre ## Minimum java 1.8
pip install -r /workspace/tools/flex-cell/requirements/requirements.txt
if [ ! -d /workspace/data/flex-cell/output ]; then
    mkdir /workspace/data/flex-cell/output
fi
if [ ! -d /workspace/data/flex-cell/output/physical_twin ]; then
    mkdir /workspace/data/flex-cell/output/physical_twin
fi