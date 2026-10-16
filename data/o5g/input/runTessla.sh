#!/bin/bash

if [ -z "$O5G_INSTALL_PATH" ]; then
  O5G_INSTALL_PATH="/workspace/examples"
fi

printf "Compiling TeSSLa monitor from specification \n"

cd "${O5G_INSTALL_PATH}/tools/tessla-telegraf-connector/"
chmod +x TesslaTelegrafConnector
./TesslaTelegrafConnector -i specification.tessla -c "${O5G_INSTALL_PATH}/data/o5g/input/telegraf.conf" -r