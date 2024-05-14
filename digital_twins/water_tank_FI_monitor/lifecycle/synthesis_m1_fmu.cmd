set input_file "/workspace/examples/digital_twins/water_tank_FI_monitor/model/m1.smv"
go
build_monitor -n 0 -C "/workspace/examples/digital_twins/water_tank_FI_monitor/model/observables_m1.list"
generate_monitor -n 0 -l 3 -L "FMU" -o "m1"
quit
