# Web videos of the examples

Each example has a demo video, `digital_twins/<example>/demo.mp4`, linked
from the example list in the top-level README. The videos are the web
videos that this skill makes; GIFs are not committed.

## How the videos are made

1. Record the examples (`record.sh record`, see `SKILL.md`). The recording
   is 1600x900 at 10 frames per second, with a chapter per example.
2. `split.py` cuts one video per chapter (`segments/`), at normal speed.
3. `postprocess.py` makes the web video of every chapter (`web/segments/`)
   and joins them into the full video with chapters. The speed of each
   step comes from `driver.log` (`speed.py`):
   - steps that show results (Firefox with a plot or web page, `head` of
     an output file, the o5g dashboard) play at normal speed for up to
     60 seconds, the rest of such a step at 16x; the heart digital twin
     is shown zoomed out, after its Apply Settings and Reset Position
     buttons are pressed, so that the beating heart and the ECG are both
     visible
   - steps longer than 20 seconds (installations, builds, runs whose
     output scrolls past) play at 16x
   - everything else plays at 4x

   The parts are sped up losslessly and encoded once with H.264 (CRF 24,
   tuned for animation, `faststart` for streaming), at the size of the
   screen: scaling makes the terminal text unreadable. GIFs (`gif/`) are
   made from the web videos with a 32-colour palette.
4. When examples were recorded in several takes, `record.sh assemble`
   combines them; every example comes from the latest take that recorded
   it with evidence.

To update the demo videos, copy each `web/segments/NN-<example>.mp4` of
the assembled set to `digital_twins/<example>/demo.mp4`.

## The current videos

Recorded on 17 and 18 October 2026 with DTaaS v1.0
(`workspace-dex-localhost`) and the examples of this repository, in five
takes. Raw is the cut of the recording at normal speed; web is the demo
video.

| # | Example | Raw MB | Raw time | Web MB | Web time | GIF MB | GIF time |
|---|---|--:|--:|--:|--:|--:|--:|
| 01 | existing installation | 0.3 | 0:12 | 0.1 | 0:03 | – | – |
| 02 | sign in, open desktop | 0.9 | 0:44 | 0.2 | 0:11 | – | – |
| 03 | get the examples | 1.5 | 1:03 | 0.2 | 0:16 | – | – |
| 04 | start RabbitMQ and InfluxDB | 4.7 | 1:07 | 1.0 | 0:17 | – | – |
| 05 | mass-spring-damper | 8.8 | 1:36 | 1.5 | 0:20 | 3.6 | 0:19 |
| 06 | water_tank_FI | 30.5 | 4:03 | 6.4 | 0:54 | 16.2 | 0:52 |
| 07 | water_tank_swap | 18.0 | 2:25 | 3.8 | 0:48 | 9.7 | 0:47 |
| 08 | heart_dt | 16.7 | 3:18 | 3.5 | 1:15 | 8.0 | 1:15 |
| 09 | drobotti_rmqfmu | 15.7 | 2:39 | 2.9 | 0:30 | 7.3 | 0:29 |
| 10 | opc-ua-waterplant | 66.9 | 9:52 | 8.5 | 0:42 | 21.3 | 0:41 |
| 11 | three-tank | 63.6 | 5:04 | 11.2 | 0:34 | 27.5 | 0:32 |
| 12 | flex-cell | 49.6 | 8:21 | 7.1 | 1:25 | 16.1 | 1:23 |
| 13 | incubator | 26.8 | 4:38 | 3.3 | 0:34 | 12.0 | 0:33 |
| 14 | o5g | 35.5 | 5:43 | 9.1 | 1:32 | 25.2 | 1:30 |
| 15 | mass-spring-damper-monitor | 10.9 | 3:01 | 1.7 | 0:51 | 4.5 | 0:49 |
| 16 | water_tank_FI_monitor | 18.2 | 3:06 | 3.4 | 0:53 | 8.8 | 0:52 |
| 17 | incubator-NuRV-monitor-validation | 10.7 | 2:51 | 1.9 | 0:50 | 5.1 | 0:50 |
| 18 | incubator-NuRV-monitor-service | 59.2 | 8:54 | 6.9 | 0:43 | 18.2 | 0:42 |
| 19 | incubator-NuRV-fmu-monitor-service | 27.0 | 6:14 | 2.3 | 0:31 | 6.9 | 0:31 |
| 20 | incubator-TeSSLa-monitor-service | 37.4 | 7:24 | 3.9 | 0:37 | 11.3 | 0:36 |
| 21 | incubator-TeSSLa-active-control | 33.3 | 6:51 | 3.7 | 0:35 | 9.8 | 0:33 |
| | **Total** | **536.4** | **1:29:08** | **82.6** | **14:20** | **211.6** | **13:13** |

The web videos of the 17 examples (rows 05 to 21) are the demo videos,
81.1 MB in all. The setup chapters (rows 01 to 04) are part of the full
web video only. The full web video lasts 14:20 and has 82.6 MB.

`opc-ua-waterplant-complete` has no lifecycle scripts and is not
recorded.

The BIM example (`fzk_haus`) was added after these takes and recorded on
20 October 2026 in a take of its own. Its chapter ends in the Buildings page,
which the dtaas-web 1.0.2 of the release does not have, so that take served a
build of the client of DTaaS `feature/distributed-demo`, the upcoming release,
mounted over the image's build by a second compose file. That client draws
the model and its sensors and receives no readings, which the terminal shows
instead:

| Example | Raw MB | Raw time | Web MB | Web time | GIF MB | GIF time |
|---|--:|--:|--:|--:|--:|--:|
| fzk_haus | 11.3 | 3:15 | 2.6 | 1:39 | 5.3 | 1:38 |
