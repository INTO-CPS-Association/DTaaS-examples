#!/bin/bash
# Copies the DTaaS examples into the workspace of the current user.
#   - Private assets (digital_twins, data, functions, models, tools)
#     are copied into the private workspace directory (/workspace).
#   - Common assets are copied into the common workspace
#     directory (/workspace/common).

set -e

PRIVATE_DIR="${PRIVATE_DIR:-/workspace}"
COMMON_DIR="${COMMON_DIR:-${PRIVATE_DIR}/common}"
BRANCH="${BRANCH:-main}"
ARCHIVE="https://github.com/INTO-CPS-Association/DTaaS-examples/archive/refs/heads/${BRANCH}.tar.gz"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

wget -qO- "${ARCHIVE}" | tar -xz -C "${TMP_DIR}"
SRC_DIR="${TMP_DIR}/DTaaS-examples-${BRANCH}"

mkdir -p "${PRIVATE_DIR}" "${COMMON_DIR}"
for asset in digital_twins data functions models tools; do
  cp -r "${SRC_DIR}/${asset}" "${PRIVATE_DIR}/"
done
cp -r "${SRC_DIR}/common/." "${COMMON_DIR}/"

printf "Copied private examples into %s\n" "${PRIVATE_DIR}"
printf "Copied common examples into %s\n" "${COMMON_DIR}"
