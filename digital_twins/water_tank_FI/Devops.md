# Water Tank FI

This Digital Twin pipeline runs across four stages — `create`, `execute`, `analyze`, and `clean`.

* In `create`, the Docker image is either pulled from the registry or built and pushed if not found.
* In `execute`, the simulation is run via `lifecycle/execute`, and outputs (`outputs.csv`) are saved.
* The `analyze` stage runs `lifecycle/analyze` to generate plots, which are stored as artifacts.
* Finally, `clean` runs `lifecycle/clean` to remove temporary or intermediate data.

To make the DT run properly, update the FMU paths in `digital_twins/water_tank_FI/multimodelFI.json`.
Replace:
`file:///builds/user/dtaas_examples/models/watertankcontroller-c.fmu`
with:
`file://${CI_PROJECT_DIR}/models/watertankcontroller-c.fmu`
