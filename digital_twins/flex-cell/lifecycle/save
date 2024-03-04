#!/bin/bash
printf "Saving current experiment... \n\n"
if [ ! -d /workspace/examples/data/flex-cell/output/saved_experiments ]; then
    mkdir /workspace/examples/data/flex-cell/output/saved_experiments
fi
cp /workspace/examples/data/flex-cell/output/outputs.csv /workspace/examples/data/flex-cell/output/saved_experiments/outputs_"$(date +"%Y_%m_%d_%H_%M_%S").csv"