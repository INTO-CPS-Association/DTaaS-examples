# Troubleshooting the recording

Lessons from making the recording work. Each item says what goes wrong
and why the scripts do what they do.

## Installation and files

- **Where the installation lives.** On Docker Desktop and Rancher Desktop,
  host folders reach the Docker VM through a sharing layer (Rancher uses
  sshfs) that refuses absolute symlinks. Python virtual environments in
  `/workspace` then fail with `Operation not permitted`. `record.sh` puts
  the installation in `DTAAS_BASE` (default `/var/lib/dtaas-demo`), a path
  inside the VM, and mounts it at the same path into the recording
  container, so `docker compose` bind mounts resolve to a native file
  system.
- **Ownership of the user files.** The workspace user is uid 1000. Run
  `sudo chown -R 1000:100 files/*` after extracting the release, as the
  DTaaS installation docs do; otherwise the user cannot write to
  `/workspace`. The admin user of the recording container is uid 1000 too.
- **Examples source.** `getExamples.sh` refuses to overwrite an existing
  `/workspace/examples`. Remove it, or start from a fresh installation, to
  record again.

## Driving the browser and the desktop

- The DTaaS sign-in button is labelled `SignIn`; Dex redirects back to
  `/Library` (capital L).
- The Workbench Desktop entry is a button titled `Desktop-btn` that opens
  a new tab.
- Playwright mouse coordinates are relative to the page, not the screen.
  The Applications menu of the desktop is at page position (60, 15) and its
  "Terminal Emulator" entry at (88, 75) with the default 1600x900 screen.
- Ctrl+Alt+T does not open a terminal in the workspace desktop; the menu
  does. Alt+F10 maximises the terminal.
- Grant the clipboard permissions to the browser context, or a clipboard
  dialog covers the desktop.
- Firefox in the workspace image shows its profile chooser because the
  default `profiles.ini` has no profile entry. The plan opens Firefox with
  `--profile ~/.mozilla/firefox/kasm` and closes it with `pkill -x firefox`.

## Knowing when a command has finished

- The driver watches the child processes of the terminal shell in the
  workspace container: a step is done when the shell has had no children
  for two checks in a row.
- A `sudo` waiting for a password has no child process. Finished `sudo`
  processes can stay as zombies without children; the detector ignores
  zombies, otherwise it presses Enter in a loop.
- `pkill -f <pattern>` inside `bash -c '...'` also matches that shell,
  because its command line contains the pattern. Use `pkill -x <name>` or
  the `[x]yz` bracket trick.

## The recording container

- The driver sets `DISPLAY` for itself; Playwright needs it to start a
  headed browser.
- Files left in `/tmp` by an earlier run under another user
  (`/tmp/.X99-lock`, `/tmp/xvfb.log`) stop Xvfb from starting.
  `record.sh record` removes them.
- The Docker VM needs room: the examples install Java, OpenModelica with
  clang, Rust, Maven, Telegraf and several Python virtual environments in
  the workspace container.

## Services

- RabbitMQ and InfluxDB come from the incubator example
  (`common/digital_twins/incubator`), started with their own compose files
  and connected to the `dtaas_default` network, so the workspace reaches
  them as `rabbitmq-server` and `influxdb-server`.
- RabbitMQ provides MQTT on port 1883 through its MQTT plugin; flex-cell
  and o5g use it.
- The InfluxDB data comes from `influxdb.zip`, which holds the incubator
  organisation, bucket and token.
- Each service example's configuration is edited in the recording with
  `sed` to use the service names and the incubator credentials; see the
  steps in `scripts/plan.py`.

## Adding or changing an example

Add the example to `EXAMPLES` in `scripts/plan.py` with its lifecycle
steps, and add an evidence check to `CHECKS` in `scripts/driver.py` that
runs right after the step producing the output, before any cleanup step
removes it. Rehearse the steps without recording first, for example with
`docker exec -u user dtaas-user-1 bash -c '<commands>'`.
