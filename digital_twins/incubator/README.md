# Incubator Digital Twin

This example reuses the [Incubator digital twin](../../common/digital_twins/incubator/README.md).
Only the configuration and lifecycle scripts are explained on this page.

## Digital Twin Configuration

There is one configuration file: `simulation.conf`.
The RabbitMQ and InfluxDB configuration parameters need to be updated.

## Lifecycle Phases

The lifecycles that are covered include:

| Lifecycle Phase    | Completed Tasks |
| --------- | ------- |
| Create    | Installs Python and creates a virtual environment with the Python dependencies |
| Execute   | Executes the Incubator digital twin and produces output in the terminal and in _incubator/log.log_. |
| Clean     | Removes the log file. |

## Run the example

To run the example, change your present directory.

```bash
cd /workspace/examples/digital_twins/incubator
```

If required, change the execute permission of lifecycle scripts
you need to execute, for example:

```bash
chmod +x lifecycle/create
```

Now, run the following scripts:

### Create

Installs Python, if needed, and creates a Python virtual environment with
the dependencies of the incubator in _common/digital\_twins/incubator/.venv_.

```bash
lifecycle/create
```

### Execute

Executes the Incubator digital twin with a mock physical twin. Pushes the results in the terminal, _incubator/log.log_, and in InfluxDB.

```bash
lifecycle/execute
```

### Clean

Removes the output log file.

```bash
lifecycle/clean
```
