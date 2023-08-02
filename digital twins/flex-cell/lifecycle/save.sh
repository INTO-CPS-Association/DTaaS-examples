#!/bin/bash
printf "Saving current experiment... \n\n"
if [ ! -d /workspace/data/flex-cell/output/saved_experiments ]; then
    mkdir /workspace/data/flex-cell/output/saved_experiments
fi
cp /workspace/data/flex-cell/output/outputs.csv /workspace/data/flex-cell/output/saved_experiments/outputs_"$(date +"%Y_%m_%d_%H_%M_%S").csv"