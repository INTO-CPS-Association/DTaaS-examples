"""Evidence that an example worked, collected right after the step that produces it.

CHECKS maps an example to the step after which to look and the command, run
in the workspace container, whose output is the evidence.
"""

from config import DT_DIR, EXAMPLES_DIR
from examples import output


def line_count(path):
    """Number of lines of a file."""
    return f"wc -l < {path}"


def plots(name):
    """The plots of an example."""
    return f"ls {output(name, 'plots')}"


def influx_count(measurement):
    """Number of series of a measurement written to InfluxDB in the last 5 minutes."""
    query = ('from(bucket:"incubator") |> range(start: -5m) '
             f'|> filter(fn: (r) => r._measurement == "{measurement}") |> count()')
    return (f"TOKEN=$(grep -m1 token {DT_DIR}/incubator/simulation.conf | cut -d'\"' -f2); "
            "curl -s -X POST 'http://influxdb-server:8086/api/v2/query?org=incubator' "
            "-H \"Authorization: Token $TOKEN\" -H 'Content-Type: application/vnd.flux' "
            f"-d '{query}' | grep -c _result")


CHECKS = {
    "mass-spring-damper": (
        "lifecycle/execute", line_count(output("mass-spring-damper", "outputs.csv"))),
    "water_tank_FI": ("lifecycle/analyze", plots("water_tank_FI")),
    "water_tank_swap": ("lifecycle/analyze", plots("water_tank_swap")),
    "heart_dt": (
        "sleep 20",
        "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:5001/ecg-data"),
    "drobotti_rmqfmu": (
        "lifecycle/execute", line_count(f"{DT_DIR}/drobotti_rmqfmu/target/outputs.csv")),
    "opc-ua-waterplant": (
        "lifecycle/execute",
        f"grep -c 'Simulation time' {EXAMPLES_DIR}/data/opc-ua-waterplant/output/execute.log"),
    "three-tank": ("lifecycle/execute", line_count(output("three-tank", "outputs.csv"))),
    "flex-cell": ("lifecycle/execute", line_count(output("flex-cell", "outputs.csv"))),
    "incubator": ("lifecycle/execute", influx_count("controller")),
    "o5g": ("tmux attach -t o5g", influx_count("prediction")),
    "mass-spring-damper-monitor": ("lifecycle/analyze", plots("mass-spring-damper-monitor")),
    "water_tank_FI_monitor": ("lifecycle/analyze", plots("water_tank_FI_monitor")),
    "incubator-NuRV-monitor-validation": (
        "lifecycle/analyze", plots("incubator-NuRV-monitor-validation")),
    # verdicts of the monitors; the NuRV monitor service prints them only
    # to the terminal, so its step saves them with tee
    "incubator-NuRV-monitor-service": (
        "lifecycle/execute 2>&1 | tee /tmp/nurv-service.log",
        "grep -c 'verdict:' /tmp/nurv-service.log"),
    "incubator-NuRV-fmu-monitor-service": (
        "lifecycle/execute", "grep -c 'Outputs:' /tmp/nurv-fmu-service.log"),
    "incubator-TeSSLa-monitor-service": ("lifecycle/execute", "grep -c 'alert' /tmp/tessla.log"),
    "incubator-TeSSLa-active-control": (
        "lifecycle/execute", "grep -c 'Valid Message' /tmp/tessla.log"),
    # the publisher logs the number of sensors once it is connected
    "fzk_haus": (
        "sleep 10", f"grep -c 'Publishing 7 sensors' {DT_DIR}/fzk_haus/publisher.log"),
}


def check_after(name, command):
    """The evidence command to run after this step of the example, or None."""
    step, check = CHECKS.get(name, (None, None))
    return check if command == step else None
