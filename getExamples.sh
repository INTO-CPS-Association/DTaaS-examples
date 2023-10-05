#!/bin/bash
wget -P workspace https://github.com/INTO-CPS-Association/DTaaS-examples/archive/refs/heads/main.zip
unzip workspace/main.zip -d workspace
mv workspace/DTaaS-examples-main workspace/examples
rm workspace/main.zip
