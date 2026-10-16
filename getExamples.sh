#!/bin/bash
# Downloads the DTaaS examples and places them in /workspace/examples

set -e

EXAMPLES_PATH="${EXAMPLES_PATH:-/workspace/examples}"
BRANCH="${BRANCH:-main}"
ARCHIVE="https://github.com/INTO-CPS-Association/DTaaS-examples/archive/refs/heads/${BRANCH}.tar.gz"

if [ -e "${EXAMPLES_PATH}" ]; then
  printf "%s already exists. Move or remove it before downloading the examples.\n" \
    "${EXAMPLES_PATH}"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

wget -qO- "${ARCHIVE}" | tar -xz -C "${TMP_DIR}"
mkdir -p "$(dirname "${EXAMPLES_PATH}")"
mv "${TMP_DIR}/DTaaS-examples-${BRANCH}" "${EXAMPLES_PATH}"

printf "Copied the examples into %s\n" "${EXAMPLES_PATH}"
