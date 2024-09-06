set input_file "/workspace/examples/models/incubator/nurv-specification.smv"
go
build_monitor -n 0
generate_monitor -n 0 -l 3 -L "FMU" -o "safe-operation"
quit
