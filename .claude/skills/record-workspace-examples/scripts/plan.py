"""Session plan for the recorded DTaaS workspace-dex-localhost demonstration.

Each example is a list of steps typed into the terminal of the VNC desktop.
Step forms:
  "command"                         type the command, wait until it finishes
  ("command", {"interrupt": secs})  type, wait secs, press Ctrl+C, wait until it finishes
  ("command", {"tmux_view": secs})  type (attaches tmux), wait secs, detach with Ctrl+B d
  ("command", {"background": secs}) type a command that returns quickly, then wait secs
"""

EX = "/workspace/examples"
DT = EX + "/digital_twins"



def use_services(conf):
    """Point an incubator configuration at the RabbitMQ and InfluxDB services.

    The examples built on the incubator copy its configuration; each edits its
    own copy, so that it also works when the incubator example is not
    recorded in the same session.
    """
    return ("sed -i -e 's/ip = \"localhost\"/ip = \"rabbitmq-server\"/' "
            f"-e 's#url = http://localhost:8086#url = http://influxdb-server:8086#' {conf}")


def show(path_or_url, secs=20):
    """Show a plot or web page in the desktop's Firefox for a while."""
    return (f"firefox --profile ~/.mozilla/firefox/kasm --new-window {path_or_url} >/dev/null 2>&1 & "
            f"sleep {secs}; pkill -x firefox", {})


EXAMPLES = [
    ("mass-spring-damper", "Mass Spring Damper", [
        "lifecycle/create",
        "lifecycle/execute",
        f"head -5 {EX}/data/mass-spring-damper/output/outputs.csv",
        "lifecycle/terminate",
    ]),
    ("water_tank_FI", "Water Tank Fault Injection", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show(f"{EX}/data/water_tank_FI/output/plots/resultFI.png"),
        "lifecycle/terminate",
    ]),
    ("water_tank_swap", "Water Tank Model Swap", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show(f"{EX}/data/water_tank_swap/output/plots/result.png"),
        "lifecycle/terminate",
    ]),
    ("heart_dt", "Heart Digital Twin", [
        "lifecycle/create",
        "lifecycle/execute",
        ("sleep 20", {}),
        show("http://localhost:5001", 40),
        "lifecycle/clean",
    ]),
    ("drobotti_rmqfmu", "Desktop Robotti and RabbitMQ", [
        "# Point the example at the RabbitMQ service (rabbitmq-server)",
        "sed -i -e 's/: \"host\"/: \"rabbitmq-server\"/' -e 's/: \"usr\"/: \"incubator\"/' "
        "-e 's/: \"user\"/: \"incubator\"/' -e 's/: \"pass\"/: \"incubator\"/' "
        "-e 's/: \"vhost\"/: \"\\/\"/' rabbitMQ-credentials.json multimodel.json",
        "cat rabbitMQ-credentials.json",
        "lifecycle/create",
        "lifecycle/execute",
        "head -5 target/outputs.csv",
        "lifecycle/terminate",
    ]),
    ("opc-ua-waterplant", "Water Treatment Plant and OPC-UA", [
        "lifecycle/install",
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/clean",
    ]),
    ("three-tank", "Three Water Tanks with TwinManager Framework", [
        "lifecycle/create",
        "lifecycle/execute",
        f"head -5 {EX}/data/three-tank/output/outputs.csv",
        "lifecycle/clean",
    ]),
    ("flex-cell", "Flex Cell with Two Industrial Robots", [
        "# Point the example at the RabbitMQ service, which also provides MQTT",
        "sed -i -e 's/\"www.google.com\"/\"rabbitmq-server\"/' -e 's/= 1884/= 1883/' -e 's/= 5667/= 5672/' "
        "-e 's/\"username[12]\"/\"incubator\"/' -e 's/\"password[12]\"/\"incubator\"/' "
        "-e 's/vhost = \"vhost\"/vhost = \"\\/\"/' " + EX + "/data/flex-cell/input/connections.conf",
        f"cat {EX}/data/flex-cell/input/connections.conf",
        "lifecycle/create",
        "lifecycle/prepare",
        ("lifecycle/execute", {"interrupt": 150}),
        "lifecycle/analyze",
        show(f"{EX}/data/flex-cell/output/experiment_plot.png"),
        "lifecycle/save",
        "lifecycle/clean",
        "lifecycle/terminate",
    ]),
    ("incubator", "Incubator", [
        "# Point the incubator at the RabbitMQ and InfluxDB services",
        use_services("simulation.conf"),
        "head -18 simulation.conf",
        "lifecycle/create",
        ("lifecycle/execute", {"interrupt": 90}),
        "lifecycle/clean",
    ]),
    ("o5g", "Firefighters in Emergency Environments", [
        "# Point the example at the MQTT (rabbitmq-server) and InfluxDB services",
        "TOKEN=$(grep token ../incubator/simulation.conf | cut -d'\"' -f2)",
        "sed -i -e 's/^export O5G_MQTT_SERVER=.*/export O5G_MQTT_SERVER=rabbitmq-server/' "
        "-e 's/^export O5G_MQTT_PORT=.*/export O5G_MQTT_PORT=1883/' "
        "-e 's/^export O5G_MQTT_USER=.*/export O5G_MQTT_USER=incubator/' "
        "-e 's/^export O5G_MQTT_PASS=.*/export O5G_MQTT_PASS=incubator/' "
        "-e 's/^export O5G_INFLUX_SERVER=.*/export O5G_INFLUX_SERVER=influxdb-server/' "
        "-e 's/^export O5G_INFLUX_PORT=.*/export O5G_INFLUX_PORT=8086/' "
        "-e \"s|^export O5G_INFLUX_TOKEN=.*|export O5G_INFLUX_TOKEN='$TOKEN'|\" "
        "-e 's/^export O5G_INFLUX_ORG=.*/export O5G_INFLUX_ORG=incubator/' "
        "-e 's/^export O5G_INFLUX_BUCKET=.*/export O5G_INFLUX_BUCKET=incubator/' config",
        "cat config",
        "lifecycle/install",
        "lifecycle/create",
        "lifecycle/execute",
        ("tmux attach -t o5g", {"tmux_view": 60}),
        "lifecycle/terminate",
        "lifecycle/clean",
    ]),
    ("mass-spring-damper-monitor", "Mass Spring Damper with NuRV Runtime Monitor FMU", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show(f"{EX}/data/mass-spring-damper-monitor/output/plots/resultWT_mon.png"),
        "lifecycle/terminate",
    ]),
    ("water_tank_FI_monitor", "Water Tank Fault Injection with NuRV Runtime Monitor FMU", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show(f"{EX}/data/water_tank_FI_monitor/output/plots/resultFI_mon.png"),
        "lifecycle/terminate",
    ]),
    ("incubator-NuRV-monitor-validation", "Incubator Co-Simulation with NuRV Runtime Monitor FMU", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show(f"{EX}/data/incubator-NuRV-monitor-validation/output/plots/resultIV.png"),
        "lifecycle/terminate",
    ]),
    ("incubator-NuRV-monitor-service", "Incubator with NuRV Runtime Monitor as Service", [
        "cp ../incubator/simulation.conf simulation.conf",
        use_services("simulation.conf"),
        "lifecycle/create",
        "lifecycle/execute 2>&1 | tee /tmp/nurv-service.log",
        "lifecycle/clean",
    ]),
    ("incubator-NuRV-fmu-monitor-service", "Incubator with NuRV Runtime Monitor FMU as Service", [
        "cp ../incubator/simulation.conf simulation.conf",
        use_services("simulation.conf"),
        "lifecycle/create",
        "lifecycle/execute",
    ]),
    ("incubator-TeSSLa-monitor-service", "Incubator with TeSSLa Runtime Monitor as Service", [
        "cp ../incubator/simulation.conf simulation.conf",
        use_services("simulation.conf"),
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/clean",
    ]),
    ("incubator-TeSSLa-active-control", "Incubator with TeSSLa Runtime Monitor for Active Control", [
        "cp ../incubator/simulation.conf simulation.conf",
        use_services("simulation.conf"),
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/clean",
    ]),
]


def steps(example):
    """Normalised (command, options) steps of one example, starting with the cd."""
    name, title, items = example
    out = [(f"cd {DT}/{name} && clear", {}), (f"# ===== {title} =====", {})]
    for item in items:
        out.append(item if isinstance(item, tuple) else (item, {}))
    return out
