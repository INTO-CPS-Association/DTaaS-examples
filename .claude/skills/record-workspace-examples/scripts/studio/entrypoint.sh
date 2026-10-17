#!/bin/bash
# Give the admin user access to the Docker socket of the host, then idle.
set -e
SOCKET_GID="$(stat -c %g /var/run/docker.sock)"
if ! getent group "${SOCKET_GID}" > /dev/null; then
  groupadd -g "${SOCKET_GID}" dockerhost
fi
usermod -aG "$(getent group "${SOCKET_GID}" | cut -d: -f1)" dtaas
chown dtaas:dtaas /var/lib/dtaas-demo
exec sleep infinity
