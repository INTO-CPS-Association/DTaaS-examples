set input_file "/workspace/digital_twins/mass-spring-damper-monitor/model/m2.smv"
go
build_monitor -n 0 -C "/workspace/digital_twins/mass-spring-damper-monitor/model/observables_m2.list"
generate_monitor -n 0 -l 3 -L "FMU" -o "m2"
quit
