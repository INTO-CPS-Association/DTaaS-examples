"""Steps of the recording before the examples: installation, examples and services.

The installation and the services are typed into the host terminal, the
examples download into the terminal of the VNC desktop.
"""

import config

# Steps of the release README and the DTaaS installation docs
INSTALL = [
    "# DTaaS v1.0 workspace-dex-localhost installation",
    f"cd {config.BASE}",
    f"curl -LO {config.RELEASE}",
    "unzip -q workspace-dex-localhost-1.0.zip && cd workspace-dex-localhost && ls",
    "sed -n '/Quick Demo/,/Stop the demo/p' README.md",
    "cp .env.example .env",
    "cp config/dex-config.yaml.example config/dex-config.yaml",
    "# give the user workspace files to the workspace user (DTaaS installation docs)",
    "sudo chown -R 1000:100 files/*",
    "ls -ln files",
    "docker compose up -d",
    "sleep 20 && docker compose ps",
]

EXISTING_INSTALL = [f"cd {config.INSTALL} && docker compose ps"]


def get_examples(repository, branch):
    """Steps that download the examples into the workspace with getExamples.sh."""
    script = f"https://raw.githubusercontent.com/{repository}/{branch}/getExamples.sh"
    return [
        f"# Get the DTaaS examples ({repository}, branch {branch})",
        f"cd ~ && wget -q {script}",
        f"REPOSITORY={repository} BRANCH={branch} bash getExamples.sh",
        f"ls {config.EXAMPLES_DIR} {config.DT_DIR}",
    ]


# RabbitMQ and InfluxDB of the incubator example, on the network of DTaaS
SERVICES = [
    "# RabbitMQ (with MQTT) and InfluxDB services used by some examples",
    "cd files/user/examples/common/digital_twins/incubator",
    "(cd incubator/communication/installation && docker compose up -d --build)",
    "(cd digital_twin/data_access/influxdbserver && unzip -q -o influxdb.zip -d influxdb "
    "&& docker compose up -d --build)",
    "docker network connect dtaas_default rabbitmq-server "
    "&& docker network connect dtaas_default influxdb-server",
    "sleep 15 && docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}'",
]

# Shown in the workspace after the services start
SERVICES_CHECK = [
    "# Services are reachable from the workspace by name: rabbitmq-server, influxdb-server",
    "curl -s http://influxdb-server:8086/health; echo; "
    "(echo > /dev/tcp/rabbitmq-server/5672) && echo rabbitmq-server:5672 reachable",
]
