---
name: record-workspace-examples
description: >-
  Screen-record the DTaaS workspace examples running in a terminal of the
  VNC desktop of a DTaaS workspace-dex-localhost installation, including the
  setup of the RabbitMQ and InfluxDB services some examples need. Use this
  skill whenever the user wants a video, screen recording, demo recording or
  walkthrough of the DTaaS examples, wants to run all examples in the
  workspace desktop and capture it, or wants to re-record the examples after
  changing them, even if they do not say "skill" or name the installation.
---

# Record the DTaaS workspace examples

The recording shows what a DTaaS user does: sign in through Dex, open the
workspace desktop from the Workbench, get the examples with
`getExamples.sh` in a terminal of the VNC desktop, and run every example's
lifecycle scripts there. Host-side steps (the optional installation and the
RabbitMQ/InfluxDB services) are typed into a host terminal shown in the
same recording.

Everything runs in a recording container (`dtaas-studio`): a virtual
screen with `xterm` and Chromium, recorded by `ffmpeg`, driven by
`scripts/driver.py`. The examples and their steps are listed in
`scripts/plan.py`.

## Prerequisites

- Docker with about 30 GB free in its disk and 4 GB of memory; check with
  `docker system df` and free space before starting
- Free host ports 80 and 5556 (DTaaS), 5672, 1883, 15672 and 8086 (services)
- Network access to GitHub, the Ubuntu archive and the OpenModelica servers

## Workflow

Run the commands from the repository root. `record.sh` is
`.claude/skills/record-workspace-examples/scripts/record.sh`.

1. Choose where the examples come from. `getExamples.sh` downloads them in
   the workspace; set `EXAMPLES_REPOSITORY` and `EXAMPLES_BRANCH` to record a
   fork or a branch that is not merged yet, for example
   `export EXAMPLES_REPOSITORY=<user>/DTaaS-examples EXAMPLES_BRANCH=<branch>`.
   The branch must contain the `getExamples.sh` with `REPOSITORY` support.
2. Start the recording container: `record.sh start`.
3. Decide whether the installation is part of the recording.
   - Not recorded: `record.sh install`, then `record.sh record`.
   - Recorded: `record.sh record --with-install` on a clean slate.
   Add example names (directory names under `digital_twins/`) to record only
   those, for example `record.sh record mass-spring-damper heart_dt`.
4. Follow the progress with `record.sh status` every 10 to 20 minutes. It
   prints the last steps and saves the current screen to
   `/tmp/recording-status.png`; look at the image when a step seems stuck.
   A full run takes about three hours.
5. When the status says `finished`, copy the results:
   `record.sh fetch <directory>`. The directory then holds
   - `dtaas-workspace-examples.mp4` with chapters per example
     (`dtaas-workspace-examples.mkv` is the raw recording)
   - `chapters.txt`, the chapter start times
   - `report.json`, evidence per example (output rows, plots, HTTP status,
     InfluxDB series) collected right after the step that produces it
   - `driver.log`, every typed step with its time
6. Check `report.json` and skim the video at the chapter marks before
   reporting success. An example only counts as recorded successfully when
   its evidence is present.
7. Clean up with `record.sh teardown` once the user has the video.

## What to expect in the recording

- Examples that use OpenModelica (`opc-ua-waterplant`, `o5g`) depend on
  build.openmodelica.org. When it is unreachable, the example stops after
  `lifecycle/install` and is retried at the end of the session, up to three
  times with ten-minute pauses. Report it when the retries also fail.
- `sudo` in the workspace asks for a password; the workspace user has an
  empty one, so the driver answers the prompt with Enter.
- Long-running digital twins (incubator, flex-cell) are stopped with Ctrl+C
  after a fixed time; the o5g tmux session is shown for a minute and
  detached.

Read `references/troubleshooting.md` when a step fails or hangs, when you
change the installation or the workspace image, or when you add an example
to `scripts/plan.py`.
