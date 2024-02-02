set input_file "/workspace/examples/models/m1.smv"
go
build_monitor -n 0 -C "/workspace/examples/models/observables_m1.list"
generate_monitor -n 0 -l 3 -L "FMU" -o "m1"
quit
