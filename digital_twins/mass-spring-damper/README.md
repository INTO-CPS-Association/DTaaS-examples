
This example is from https://github.com/INTO-CPS-Association/example-mass\_spring\_damper

This example demonstrates: create, execute and terminate phases

## Create phase

Installs Open Java Development Kit 17 in the workspace.

```bash
lifecycle/create
```

## Execute phase

Run the co-simulation. Generate the co-simulation output.csv file
at `data/mass-spring-damper/output/output.csv`.

There are also debug and maestro log files stored in
`data/mass-spring-damper/output` directory.

```bash
lifecycle/execute
```

## Terminate phase

Terminate to clean up the debug files and co-simulation output.

```bash
lifecycle/terminate
```
