#!/bin/bash
# Record the DTaaS workspace examples running in the VNC desktop of a
# workspace-dex-localhost installation.
#
# Usage: record.sh <command> [options]
#   start                       build and start the recording container
#   install                     install DTaaS workspace-dex-localhost (not recorded)
#   record [--with-install] [example ...]
#                               start the recording in the background; without
#                               --with-install an existing installation is used
#   status                      show the progress and save a screenshot
#   stop                        stop the recording
#   fetch <directory>           copy the recording and its report to the host
#   teardown                    remove the installation, the services and the
#                               recording container
#
# Environment: EXAMPLES_REPOSITORY, EXAMPLES_BRANCH (examples to download),
# DTAAS_BASE (installation directory inside the Docker VM, default
# /var/lib/dtaas-demo), DTAAS_RELEASE (release zip URL)

set -e

SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDIO="dtaas-studio"
IMAGE="dtaas-recording-studio"
BASE="${DTAAS_BASE:-/var/lib/dtaas-demo}"
INSTALL="${BASE}/workspace-dex-localhost"
RELEASE="${DTAAS_RELEASE:-https://github.com/INTO-CPS-Association/DTaaS/releases/download/v1.0/workspace-dex-localhost-1.0.zip}"

as_admin() { docker exec -u dtaas -w "${BASE}" "${STUDIO}" bash -c "$1"; }

start_studio() {
  docker build -q -t "${IMAGE}" "${SCRIPTS}/studio" > /dev/null
  if ! docker ps --format '{{.Names}}' | grep -qx "${STUDIO}"; then
    docker rm -f "${STUDIO}" > /dev/null 2>&1 || true
    # host network: the browser reaches DTaaS on localhost:80 and Dex on
    # localhost:5556; the installation directory is a path inside the VM
    docker run -d --name "${STUDIO}" --network host --shm-size=1g \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v "${BASE}:${BASE}" "${IMAGE}" > /dev/null
  fi
  docker cp -q "${SCRIPTS}/driver.py" "${STUDIO}:/opt/rec/driver.py"
  docker cp -q "${SCRIPTS}/plan.py" "${STUDIO}:/opt/rec/plan.py"
  docker exec "${STUDIO}" chown -R dtaas:dtaas /opt/rec
  echo "Recording container ${STUDIO} is running"
}

install_dtaas() {
  # Steps of the release README and the DTaaS installation docs
  as_admin "set -e
    curl -fsSL -O '${RELEASE}'
    unzip -q -o workspace-dex-localhost-1.0.zip
    cd workspace-dex-localhost
    cp .env.example .env
    cp config/dex-config.yaml.example config/dex-config.yaml
    sudo chown -R 1000:100 files/*
    docker compose up -d"
}

record() {
  local args=(--skip-install)
  if [ "$1" = "--with-install" ]; then
    args=()
    shift
  elif ! docker ps --format '{{.Names}}' | grep -qx dtaas-user-1; then
    echo "No DTaaS installation is running; run '$0 install' or use --with-install"
    exit 1
  fi
  if docker exec "${STUDIO}" pgrep -f "python driver.py" > /dev/null; then
    echo "A recording is already running"
    exit 1
  fi
  # leftovers of an earlier recording that would stop Xvfb from starting
  docker exec "${STUDIO}" bash -c 'pkill -x Xvfb; rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 /tmp/xvfb.log /tmp/demo-bashrc; rm -rf /opt/recording/*' || true
  docker exec -d -u dtaas -w /opt/rec \
    -e EXAMPLES_REPOSITORY="${EXAMPLES_REPOSITORY:-INTO-CPS-Association/DTaaS-examples}" \
    -e EXAMPLES_BRANCH="${EXAMPLES_BRANCH:-main}" \
    -e DTAAS_BASE="${BASE}" -e DTAAS_RELEASE="${RELEASE}" \
    "${STUDIO}" bash -c "/opt/pw/bin/python driver.py ${args[*]} $* > /opt/recording/driver.out 2>&1"
  echo "Recording started; check it with '$0 status'"
}

status() {
  docker exec "${STUDIO}" bash -c '
    if pgrep -f "[p]ython driver.py" > /dev/null; then echo "recording: running"; else echo "recording: not running"; fi
    tail -5 /opt/recording/driver.log 2>/dev/null
    grep -m3 -E "Error|Traceback" /opt/recording/driver.out 2>/dev/null || true
    ls -lh /opt/recording 2>/dev/null | grep -E "mkv|mp4"' || true
  docker exec "${STUDIO}" bash -c 'ffmpeg -loglevel error -y -f x11grab -video_size 1600x900 -i :99 -frames:v 1 /tmp/status.png 2>/dev/null' \
    && docker cp -q "${STUDIO}:/tmp/status.png" "${TMPDIR:-/tmp}/recording-status.png" \
    && echo "current screen: ${TMPDIR:-/tmp}/recording-status.png"
}

stop() {
  # the [x] patterns match the processes but not this command line
  docker exec "${STUDIO}" bash -c 'pkill -f "[p]ython driver.py"; sleep 2; pkill -x ffmpeg; pkill -f "[c]hrome"; pkill -x xterm; pkill -x openbox; pkill -x Xvfb' || true
  echo "Recording stopped"
}

fetch() {
  local dest="${1:?Usage: $0 fetch <directory>}"
  mkdir -p "${dest}"
  docker cp -q "${STUDIO}:/opt/recording/." "${dest}/"
  ls -lh "${dest}"
}

teardown() {
  local incubator="${INSTALL}/files/user/examples/common/digital_twins/incubator"
  as_admin "
    [ -d '${incubator}' ] && (cd '${incubator}/incubator/communication/installation' && docker compose down -v)
    [ -d '${incubator}' ] && (cd '${incubator}/digital_twin/data_access/influxdbserver' && docker compose down -v)
    [ -d '${INSTALL}' ] && (cd '${INSTALL}' && docker compose down -v)
    sudo rm -rf '${BASE:?}'/*" || true
  docker rm -f "${STUDIO}" > /dev/null 2>&1 || true
  echo "Installation, services and recording container removed"
}

case "$1" in
  start) start_studio ;;
  install) install_dtaas ;;
  record) shift; record "$@" ;;
  status) status ;;
  stop) stop ;;
  fetch) shift; fetch "$@" ;;
  teardown) teardown ;;
  *) sed -n '2,20p' "$0"; exit 1 ;;
esac
