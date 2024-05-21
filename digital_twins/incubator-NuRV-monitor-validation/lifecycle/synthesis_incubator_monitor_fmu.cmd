set input_file "/workspace/examples/digital_twins/incubator-NuRV-monitor-validation/model/safe-operation.smv"
go
build_monitor -n 0
generate_monitor -n 0 -l 3 -L "FMU" -o "safe-operation"
quit
