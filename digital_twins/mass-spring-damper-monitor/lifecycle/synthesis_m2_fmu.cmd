set input_file "/workspace/examples/models/m2.smv"
go
build_monitor -n 0 -C "/workspace/examples/models/observables_m2.list"
generate_monitor -n 0 -l 3 -L "FMU" -o "m2"
quit
