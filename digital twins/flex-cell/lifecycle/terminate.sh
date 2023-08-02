#!/bin/bash
printf "Stopping background processes \n\n"
pkill -9 -f /workspace/tools/flex-cell/publisher-flexcell-physical.py
pkill -f java