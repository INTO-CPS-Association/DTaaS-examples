#!/bin/bash
## Run first the side tools and finally run the main.java file
printf "Executing the Flex-cell Digital Twin case study... \n\n"
python /workspace/tools/flex-cell/publisher-flexcell-physical.py &
java -cp /workspace/tools/DTManager-0.0.1-Maestro.jar /workspace/tools/flex-cell/FlexCellMain.java