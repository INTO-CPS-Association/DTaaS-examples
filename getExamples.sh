#!/bin/bash
# Downloads the DTaaS examples and places them in /workspace/examples
#
# Optional environment variables:
#   EXAMPLES_PATH   where to place the examples (default: /workspace/examples)
#   REPOSITORY      GitHub repository (default: INTO-CPS-Association/DTaaS-examples)
#   BRANCH          branch to download (default: main)
#   EXAMPLES_OWNER  user:group that owns the examples when the script runs as root

set -e

EXAMPLES_PATH="${EXAMPLES_PATH:-/workspace/examples}"
REPOSITORY="${REPOSITORY:-INTO-CPS-Association/DTaaS-examples}"
BRANCH="${BRANCH:-main}"
ARCHIVE="https://github.com/${REPOSITORY}/archive/refs/heads/${BRANCH}.tar.gz"

if [ -e "${EXAMPLES_PATH}" ]; then
  printf "%s already exists. Move or remove it before downloading the examples.\n" \
    "${EXAMPLES_PATH}"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

mkdir "${TMP_DIR}/examples"
# The demo videos are for the README on GitHub, not for the workspace
wget -qO- "${ARCHIVE}" |
  tar -xz --no-same-owner --strip-components=1 --exclude='digital_twins/*/demo.mp4' \
    -C "${TMP_DIR}/examples"
mkdir -p "$(dirname "${EXAMPLES_PATH}")"
mv "${TMP_DIR}/examples" "${EXAMPLES_PATH}"

# The examples belong to the workspace user, also when this script runs as root:
# the user given in EXAMPLES_OWNER, else the user who ran sudo,
# else the owner of the directory that contains the examples.
if [ "$(id -u)" -eq 0 ]; then
  if [ -n "${EXAMPLES_OWNER}" ]; then
    OWNER="${EXAMPLES_OWNER}"
  elif [ -n "${SUDO_UID}" ]; then
    OWNER="${SUDO_UID}:${SUDO_GID}"
  else
    OWNER="$(stat -c '%u:%g' "$(dirname "${EXAMPLES_PATH}")")"
  fi
  chown -R "${OWNER}" "${EXAMPLES_PATH}"
fi

# Readable by everyone, writable by the owner, lifecycle scripts executable
chmod -R u+rwX,go+rX "${EXAMPLES_PATH}"
find "${EXAMPLES_PATH}/digital_twins" -path '*/lifecycle/*' -type f ! -name '*.*' \
  -exec chmod +x {} +

printf "Copied the examples into %s\n" "${EXAMPLES_PATH}"
