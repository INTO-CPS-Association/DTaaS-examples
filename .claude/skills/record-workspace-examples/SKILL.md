---
name: record-workspace-examples
description: Screen-record the DTaaS workspace examples running in a terminal of the VNC desktop of a DTaaS workspace-dex-localhost installation, including the setup of the RabbitMQ and InfluxDB services some examples need, and make sped-up web videos and GIFs of them. Use this skill whenever the user wants a video, screen recording, demo recording, GIF or walkthrough of the DTaaS examples, wants to run all examples in the workspace desktop and capture it, or wants to re-record the examples after changing them, even if they do not say "skill" or name the installation.
compatibility: Requires Docker with about 30 GB of free disk and 4 GB of memory, and network access to GitHub, the Ubuntu archive and the OpenModelica servers. The recording container brings Python 3.12, Playwright, ffmpeg and the other tools.
---

# Record the DTaaS workspace examples

The skill lives in `.agents/skills/record-workspace-examples/`, where
agents that follow the Agent Skills standard find it. Read
`.agents/skills/record-workspace-examples/SKILL.md` and follow its steps.
Its script paths are relative to the repository root.
