"""Settings of a recording, read from the environment of the recording container."""

import os

DISPLAY = ":99"
SIZE = "1600x900"
FPS = 10
VIDEO = "dtaas-workspace-examples"

# Directory of the DTaaS installation; a path inside the Docker VM, so that
# the bind mounts of the installation are on a native file system
BASE = os.environ.get("DTAAS_BASE", "/var/lib/dtaas-demo")
INSTALL = f"{BASE}/workspace-dex-localhost"
OUT = os.environ.get("REC_OUT", "/opt/recording")
WORKSPACE = os.environ.get("WORKSPACE_CONTAINER", "dtaas-user-1")
RELEASE = os.environ.get(
    "DTAAS_RELEASE",
    "https://github.com/INTO-CPS-Association/DTaaS/releases/download/v1.0/"
    "workspace-dex-localhost-1.0.zip")
EXAMPLES_REPOSITORY = os.environ.get(
    "EXAMPLES_REPOSITORY", "INTO-CPS-Association/DTaaS-examples")
EXAMPLES_BRANCH = os.environ.get("EXAMPLES_BRANCH", "main")

# Where getExamples.sh puts the examples in the workspace
EXAMPLES_DIR = "/workspace/examples"
DT_DIR = EXAMPLES_DIR + "/digital_twins"

STEP_LIMIT = 45 * 60  # seconds before a hanging step is interrupted
RETRIES = 3  # rounds for examples whose OpenModelica download failed
RETRY_WAIT = 600  # seconds between the rounds
