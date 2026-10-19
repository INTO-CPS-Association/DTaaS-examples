"""The examples of the recording, in the order of the README, with their steps.

Each example is (directory under digital_twins, title, steps). The steps are
typed into the terminal of the VNC desktop, in the directory of the example:
  "command"                         type the command, wait until it is done
  ("command", {"interrupt": secs})  type, wait secs, press Ctrl+C, wait until done
  ("command", {"tmux_view": secs})  type (attaches tmux), wait secs, detach
  ("command", {"desktop": actions}) type, then act on the desktop while the
                                    command runs: a number waits that many
                                    seconds, a string presses a key, and
                                    ("click", x, y) clicks the screen
  ("comment", {"dtaas_page": (path, actions)})
                                    type, then show the DTaaS page at path in
                                    the signed-in tab: a number waits, ("click",
                                    name) presses a button by its name,
                                    ("scroll", pixels) scrolls the page and
                                    ("zoom", pixels) zooms the 3D view
"""

from config import DT_DIR, EXAMPLES_DIR


def use_services(conf):
    """Point an incubator configuration at the RabbitMQ and InfluxDB services."""
    return ("sed -i -e 's/ip = \"localhost\"/ip = \"rabbitmq-server\"/' "
            f"-e 's#url = http://localhost:8086#url = http://influxdb-server:8086#' {conf}")


def incubator_config():
    """Steps that copy the incubator configuration and point it at the services.

    Each example built on the incubator edits its own copy, so that it also
    works when the incubator example is not recorded in the same session.
    """
    return ["cp ../incubator/simulation.conf simulation.conf", use_services("simulation.conf")]


def show(path_or_url, secs=20):
    """Show a plot or web page in the Firefox of the desktop for a while."""
    return (f"firefox --profile ~/.mozilla/firefox/kasm --new-window {path_or_url} "
            f">/dev/null 2>&1 & sleep {secs}; pkill -x firefox", {})


def output(name, file):
    """Path of an output file of an example."""
    return f"{EXAMPLES_DIR}/data/{name}/output/{file}"


# Heart digital twin in Firefox in kiosk mode, so that the page fills the
# screen. A click on the page heading gives Firefox the keyboard (keys must
# not reach the terminal), the zoom shows the whole page, and Tab reaches
# the blue buttons: after the four settings, Apply Settings, then Reset
# Position. Clicking them starts the beating heart.
HEART_DT_PAGE = (
    "firefox --profile ~/.mozilla/firefox/kasm --kiosk http://localhost:5001 "
    ">/dev/null 2>&1 & sleep 60; pkill -x firefox",
    {"desktop": [12, ("click", 800, 50), 1, *["Control+Minus"] * 3, 2,
                 *["Tab"] * 5, "Enter", 3, "Tab", "Enter"]})


def show_plot(name, file):
    """Show a plot of an example."""
    return show(output(name, f"plots/{file}"))


FLEX_CELL_CONNECTIONS = f"{EXAMPLES_DIR}/data/flex-cell/input/connections.conf"

# The Buildings page with the FZK-Haus: roofs hidden, the ground floor and the
# heatmap per sensor, coloured by the readings the publisher sends, then the
# floor plan from above and the sensor cards
BIM_PAGE = ("# DTaaS page: the building, coloured by its readings", {"dtaas_page": (
    "/bim/models/fzk_haus",
    [8, ("scroll", 300), ("click", "Hide Slabs, Roofs And Ceilings"),
     ("click", "The floor below"), ("click", "The floor below"), ("click", "Heatmap"), 10,
     ("click", "Look From Above"), ("zoom", 400), 15, ("scroll", 700), 10])})

# The library folder the Buildings page of DTaaS reads, where the BIM example
# writes the model and the files derived from it
BIM_MODELS = "/workspace/common/models"

EXAMPLES = [
    ("mass-spring-damper", "Mass Spring Damper", [
        "lifecycle/create",
        "lifecycle/execute",
        "head -5 " + output("mass-spring-damper", "outputs.csv"),
        "lifecycle/terminate",
    ]),
    ("water_tank_FI", "Water Tank Fault Injection", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show_plot("water_tank_FI", "resultFI.png"),
        "lifecycle/terminate",
    ]),
    ("water_tank_swap", "Water Tank Model Swap", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show_plot("water_tank_swap", "result.png"),
        "lifecycle/terminate",
    ]),
    ("heart_dt", "Heart Digital Twin", [
        "lifecycle/create",
        "lifecycle/execute",
        ("sleep 20", {}),
        HEART_DT_PAGE,
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
        "head -5 " + output("three-tank", "outputs.csv"),
        "lifecycle/clean",
    ]),
    ("flex-cell", "Flex Cell with Two Industrial Robots", [
        "# Point the example at the RabbitMQ service, which also provides MQTT",
        "sed -i -e 's/\"www.google.com\"/\"rabbitmq-server\"/' "
        "-e 's/= 1884/= 1883/' -e 's/= 5667/= 5672/' "
        "-e 's/\"username[12]\"/\"incubator\"/' -e 's/\"password[12]\"/\"incubator\"/' "
        "-e 's/vhost = \"vhost\"/vhost = \"\\/\"/' " + FLEX_CELL_CONNECTIONS,
        "cat " + FLEX_CELL_CONNECTIONS,
        "lifecycle/create",
        "lifecycle/prepare",
        ("lifecycle/execute", {"interrupt": 150}),
        "lifecycle/analyze",
        show(output("flex-cell", "experiment_plot.png")),
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
        show_plot("mass-spring-damper-monitor", "resultWT_mon.png"),
        "lifecycle/terminate",
    ]),
    ("water_tank_FI_monitor", "Water Tank Fault Injection with NuRV Runtime Monitor FMU", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show_plot("water_tank_FI_monitor", "resultFI_mon.png"),
        "lifecycle/terminate",
    ]),
    ("incubator-NuRV-monitor-validation", "Incubator Co-Simulation with NuRV Runtime Monitor FMU", [
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/analyze",
        show_plot("incubator-NuRV-monitor-validation", "resultIV.png"),
        "lifecycle/terminate",
    ]),
    ("incubator-NuRV-monitor-service", "Incubator with NuRV Runtime Monitor as Service", [
        *incubator_config(),
        "lifecycle/create",
        "lifecycle/execute 2>&1 | tee /tmp/nurv-service.log",
        "lifecycle/clean",
    ]),
    ("incubator-NuRV-fmu-monitor-service", "Incubator with NuRV Runtime Monitor FMU as Service", [
        *incubator_config(),
        "lifecycle/create",
        "lifecycle/execute",
    ]),
    ("incubator-TeSSLa-monitor-service", "Incubator with TeSSLa Runtime Monitor as Service", [
        *incubator_config(),
        "lifecycle/create",
        "lifecycle/execute",
        "lifecycle/clean",
    ]),
    ("incubator-TeSSLa-active-control",
     "Incubator with TeSSLa Runtime Monitor for Active Control",
     [
         *incubator_config(),
         "lifecycle/create",
         "lifecycle/execute",
         "lifecycle/clean",
     ]),
    ("fzk_haus", "BIM - Building Information Modeling", [
        "lifecycle/create",
        f"ls -l {BIM_MODELS}",
        "# One proposed sensor per room, each with the MQTT topic it publishes on",
        f"grep -E '\"(label|topic)\"' {BIM_MODELS}/fzk_haus.manifest.json",
        "# Publish the readings over the MQTT of the RabbitMQ service",
        "export MQTT_HOST=rabbitmq-server MQTT_USERNAME=incubator MQTT_PASSWORD=incubator",
        "lifecycle/execute",
        ("sleep 10", {}),
        "cat publisher.log",
        f".venv/bin/python lifecycle/show_readings.py {BIM_MODELS}/fzk_haus.manifest.json",
        BIM_PAGE,
        "lifecycle/terminate",
    ]),
]


def steps(example):
    """Normalised (command, options) steps of one example, starting with the cd."""
    name, title, items = example
    out = [(f"cd {DT_DIR}/{name} && clear", {}), (f"# ===== {title} =====", {})]
    for item in items:
        out.append(item if isinstance(item, tuple) else (item, {}))
    return out


# example directory by title, for naming the chapters of the video
TITLES = {title: name for name, title, _ in EXAMPLES}
