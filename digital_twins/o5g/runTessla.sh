#!/bin/bash

printf "Compiling TeSSLa monitor from specification \n"

cd /workspace/tools/tessla/tessla-telegraf-connector
chmod +x TesslaTelegrafConnector
./TesslaTelegrafConnector -i specification.tessla -c /workspace/digital_twins/o5g/telegraf.conf -r