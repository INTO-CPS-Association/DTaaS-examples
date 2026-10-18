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
#   reset                       stop the services, close the terminals and
#                               remove the examples from the workspace, to
#                               record again on the same installation
#   status                      show the progress and save a screenshot
#   stop                        stop the recording
#   split [--copy]              cut the recording into one video per example
#                               (done automatically at the end of a recording)
#   postprocess [--web] [--gif] speed up the videos for the web (web/) and make
#                               one GIF per example from them (gif/); both by default
#                               (done automatically at the end of a recording)
#   fetch <directory>           copy the recording and its report to the host
#   assemble <out> <take>...    one set of videos of all examples from fetched
#                               and post-processed recordings: each example from
#                               the latest take with evidence for it
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

# The Python modules of the recording, without their tests
copy_scripts() {
  local f
  for f in "${SCRIPTS}"/*.py; do
    case "$(basename "${f}")" in test_*) continue ;; esac
    docker cp -q "${f}" "${STUDIO}:/opt/rec/"
  done
  docker exec "${STUDIO}" chown -R dtaas:dtaas /opt/rec
}

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
  copy_scripts
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
  if docker exec "${STUDIO}" pgrep -f "[p]ython driver.py" > /dev/null; then
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

reset() {
  local incubator="${INSTALL}/files/user/examples/common/digital_twins/incubator"
  # the recording starts the services and gets the examples again;
  # getExamples.sh does not overwrite existing examples
  as_admin "
    [ -d '${incubator}' ] || exit 0
    (cd '${incubator}/incubator/communication/installation' && docker compose down -v)
    (cd '${incubator}/digital_twin/data_access/influxdbserver' && docker compose down -v && sudo rm -rf influxdb)" || true
  docker exec -u user dtaas-user-1 bash -c \
    'tmux kill-server 2> /dev/null; pkill -x telegraf; pkill -x xfce4-terminal; rm -rf /workspace/examples ~/getExamples.sh*' || true
  echo "Services stopped and examples removed from the workspace"
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

split_recording() {
  copy_scripts
  docker exec -u dtaas -w /opt/rec "${STUDIO}" python3 split.py "$@"
}

postprocess() {
  copy_scripts
  docker exec -u dtaas -w /opt/rec "${STUDIO}" python3 postprocess.py "$@"
}

fetch() {
  local dest="${1:?Usage: $0 fetch <directory>}"
  mkdir -p "${dest}"
  docker cp -q "${STUDIO}:/opt/recording/." "${dest}/"
  ls -lh "${dest}"
}

assemble() {
  local out="${1:?Usage: $0 assemble <output directory> <take directory>...}"
  shift
  [ $# -gt 0 ] || { echo "Usage: $0 assemble <output directory> <take directory>..."; exit 1; }
  mkdir -p "${out}"
  # the takes are on the host; mount them at the same paths into a
  # container of the recording image, which has ffmpeg
  local dirs=() mounts=() d
  for d in "${out}" "$@"; do
    d="$(realpath "${d}")"
    dirs+=("${d}")
    mounts+=(-v "${d}:${d}")
  done
  docker build -q -t "${IMAGE}" "${SCRIPTS}/studio" > /dev/null
  docker run --rm -u "$(id -u):$(id -g)" -e PYTHONDONTWRITEBYTECODE=1 "${mounts[@]}" \
    -v "${SCRIPTS}:/opt/skill:ro" -w /opt/skill --entrypoint python3 "${IMAGE}" \
    assemble.py "${dirs[@]}"
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
  reset) reset ;;
  status) status ;;
  stop) stop ;;
  split) shift; split_recording "$@" ;;
  postprocess) shift; postprocess "$@" ;;
  fetch) shift; fetch "$@" ;;
  assemble) shift; assemble "$@" ;;
  teardown) teardown ;;
  *) sed -n '2,31p' "$0"; exit 1 ;;
esac
