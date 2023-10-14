
This example has been taken from:

https://github.com/INTO-CPS-Association/fault-injection-maestro/blob/development/fi_example/README.md

and shows an a fault injection (FI) enabled DT. In this case the watertank case-study is used, consisting
in a tank and controller, the goal of which is to keep the level of water in the tank between ```1``` and ```2```.
The output of the controller is injected, such that it is closed for a period of time, leading to the water level increasing in the tank beyond the desired level.

This example demonstrates: create, execute, analyze and terminate phases

## Create phase

Installs Open Java Development Kit 17 and pip dependencies.
The pandas and matplotlib are the pip dependencies installated.

```bash
lifecycle/create
```

## Execute phase

Run the co-simulation. Generate the co-simulation output.csv file
at `/workspace/examples/digital_twins/water_tank_FI/targetFI`.

```bash
lifecycle/execute
```

## Analyze phase

Process the output of co-simulation to produce a plot at:
`/workspace/examples/data/water_tank_FI/output/plots/`.

```bash
lifecycle/analyze
```

## Terminate phase

Clean up the temporary files and output plot

```bash
lifecycle/terminate
```
