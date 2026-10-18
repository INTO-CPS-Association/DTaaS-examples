---
name: record-workspace-examples
description: Screen-record the DTaaS workspace examples running in a terminal of the VNC desktop of a DTaaS workspace-dex-localhost installation, including the setup of the RabbitMQ and InfluxDB services some examples need, and make sped-up web videos and GIFs of them. Use this skill whenever the user wants a video, screen recording, demo recording, GIF or walkthrough of the DTaaS examples, wants to run all examples in the workspace desktop and capture it, or wants to re-record the examples after changing them, even if they do not say "skill" or name the installation.
compatibility: Requires Docker with about 30 GB of free disk and 4 GB of memory, and network access to GitHub, the Ubuntu archive and the OpenModelica servers. The recording container brings Python 3.12, Playwright, ffmpeg and the other tools.
---

# Record the DTaaS workspace examples

The recording shows what a DTaaS user does: sign in through Dex, open the
workspace desktop from the Workbench, get the examples with
`getExamples.sh` in a terminal of the VNC desktop, and run every example's
lifecycle scripts there. Host-side steps (the optional installation and the
RabbitMQ/InfluxDB services) are typed into a host terminal shown in the
same recording.

Everything runs in a recording container (`dtaas-studio`): a virtual
screen with `xterm` and Chromium, recorded by `ffmpeg`. `scripts/record.sh`
is the one command; the Python modules, each under 250 lines, run in the
container:

- `driver.py`: the recording, in chapters, using `recorder.py` (screen,
  ffmpeg, chapters), `terminals.py` (the host xterm and the terminal of
  the VNC desktop), `browser.py` (sign-in and desktop) and `session.py`
  (log, chapters and evidence).
- `examples.py`: the examples in README order with the steps typed for
  each; `setup_steps.py`: the installation, examples download and
  services; `checks.py`: the evidence collected for each example.
- `split.py`: one video per chapter; `postprocess.py` with `speed.py`:
  the web videos and GIFs; `media.py`: ffmpeg helpers and video names.
- `config.py`: the settings, read from the environment.

## Prerequisites

- Docker with about 30 GB free in its disk and 4 GB of memory; check with
  `docker system df` and free space before starting
- Free host ports 80 and 5556 (DTaaS), 5672, 1883, 15672 and 8086 (services)
- Network access to GitHub, the Ubuntu archive and the OpenModelica servers

## Workflow

Run the commands from the repository root. `record.sh` is
`.agents/skills/record-workspace-examples/scripts/record.sh`.

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
   To record again on the same installation, run `record.sh reset` first;
   it stops the services, closes the terminals and removes the examples
   from the workspace, which the recording then sets up again.
   `record.sh record` empties the output directory, so fetch the previous
   recording before.
4. Follow the progress with `record.sh status` every 10 to 20 minutes. It
   prints the last steps and saves the current screen to
   `/tmp/recording-status.png`; look at the image when a step seems stuck.
   A full run takes about three hours.
5. When the status says `finished`, copy the results:
   `record.sh fetch <directory>`. The directory then holds
   - `dtaas-workspace-examples.mp4` with chapters per example
     (`dtaas-workspace-examples.mkv` is the raw recording)
   - `segments/`, one video per chapter: `NN-<example>.mp4` for each
     example (in recording order), `-retry-<n>` for retries, short
     segments for sign-in, getting the examples and the services, and
     `index.txt` with the start and duration of each segment
   - `web/`, one video per chapter and the full video with chapters, for
     web pages and documentation: sped up step by step (results such as
     plots at normal speed, long installs and runs at 16x, the rest at
     4x), at the full screen size so that the terminal text stays sharp
   - `gif/`, one GIF per example, made from its web video
   - `chapters.txt`, the chapter start times
   - `report.json`, evidence per example (output rows, plots, HTTP status,
     InfluxDB series) collected right after the step that produces it
   - `driver.log`, every typed step with its time

   The driver cuts the segments and post-processes them at the end of the
   recording. To redo these steps on an existing recording, for example
   with other settings, run `record.sh split` (add `--copy` for a fast cut
   that snaps to keyframes) and then `record.sh postprocess`. Pass `--web`
   or `--gif` to make only one of the two; `--speed`, `--fast-speed`,
   `--result-speed`, `--long`, `--crf`, `--gif-fps` and `--gif-colors`
   change the speeds and sizes (see `scripts/postprocess.py`). Do not run
   the post-processing while another recording is running; the Docker VM
   has too little memory for both.
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
change the installation or the workspace image, or when you add an example.

## Change the skill

Add an example to `EXAMPLES` in `scripts/examples.py` and its evidence to
`CHECKS` in `scripts/checks.py`. Then run the tests and the linters of the
DTaaS repository from `scripts/`; the tests check, among other things,
that every example and lifecycle script exists in the repository and that
every check follows a step of its example:

```bash
python3 -m unittest discover --pattern 'test_*.py'
flake8 . --max-complexity=10 --max-line-length=127
pylint --rcfile=<DTaaS repository>/.pylintrc *.py
shellcheck --severity=warning record.sh studio/entrypoint.sh
```

Keep the files under 250 lines and the functions under 25 lines.
`.claude/skills/record-workspace-examples/SKILL.md` is the stub that
Claude Code reads; keep its frontmatter the same as this file's.
