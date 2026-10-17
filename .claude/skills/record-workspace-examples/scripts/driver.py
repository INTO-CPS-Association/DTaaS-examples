"""Record a DTaaS workspace-dex-localhost session with all workspace examples.

Runs inside the recording container (Xvfb display, xterm, Playwright Chromium,
ffmpeg, docker CLI). Host-side commands are typed into xterm; example commands
are typed into a terminal of the VNC desktop through the browser.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import time

from playwright.async_api import async_playwright

import plan

DISPLAY = ":99"
SIZE = "1600x900"
# Directory of the DTaaS installation; a path inside the Docker VM, so that
# the bind mounts of the installation are on a native file system
BASE = os.environ.get("DTAAS_BASE", "/var/lib/dtaas-demo")
INSTALL = f"{BASE}/workspace-dex-localhost"
OUT = os.environ.get("REC_OUT", "/opt/recording")
WS = os.environ.get("WORKSPACE_CONTAINER", "dtaas-user-1")
RELEASE = os.environ.get(
    "DTAAS_RELEASE",
    "https://github.com/INTO-CPS-Association/DTaaS/releases/download/v1.0/workspace-dex-localhost-1.0.zip")
EXAMPLES_REPOSITORY = os.environ.get("EXAMPLES_REPOSITORY", "INTO-CPS-Association/DTaaS-examples")
EXAMPLES_BRANCH = os.environ.get("EXAMPLES_BRANCH", "main")
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]
SKIP_HOST_INSTALL = "--skip-install" in sys.argv
STEP_LIMIT = 45 * 60  # seconds before a hanging step is interrupted

os.environ["DISPLAY"] = DISPLAY
env = dict(os.environ)
T0 = time.time()
chapters = []
report = []


def log(msg):
    stamp = time.strftime("%H:%M:%S", time.gmtime(time.time() - T0))
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    with open(f"{OUT}/driver.log", "a") as f:
        f.write(line + "\n")


def sh(cmd, check=False):
    return subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True, check=check)


def ws(cmd):
    """Run a command in the workspace container and return stdout."""
    r = subprocess.run(["docker", "exec", "-u", "user", WS, "bash", "-c", cmd],
                       capture_output=True, text=True)
    return r.stdout.strip()


def chapter(title):
    chapters.append((time.time() - T0, title))
    log(f"CHAPTER {title}")


# ---------------------------------------------------------------- xterm (host)
class HostTerminal:
    def __init__(self):
        subprocess.Popen(
            ["xterm", "-title", "Host terminal - DTaaS installation and services",
             "-fa", "DejaVu Sans Mono", "-fs", "13", "-bg", "#1e1e1e", "-fg", "#e8e8e8",
             "-geometry", "160x40+0+0", "-maximized", "-e",
             "bash", "--rcfile", "/tmp/demo-bashrc", "-i"], env=env)
        time.sleep(3)
        self.win = sh("xdotool search --name 'Host terminal'").stdout.split()[0]
        self.shell = sh("pgrep -n -f 'bash --rcfile /tmp/demo-bashrc'").stdout.strip()

    def activate(self):
        sh(f"xdotool windowactivate --sync {self.win}")
        time.sleep(1)

    def run(self, cmd, limit=STEP_LIMIT):
        self.activate()
        subprocess.run(["xdotool", "type", "--window", self.win, "--delay", "30", cmd], env=env)
        subprocess.run(["xdotool", "key", "--window", self.win, "Return"], env=env)
        time.sleep(1.5)
        start = time.time()
        idle = 0
        while idle < 2 and time.time() - start < limit:
            busy = sh(f"pgrep -P {self.shell}").stdout.strip()
            idle = 0 if busy else idle + 1
            time.sleep(1)
        time.sleep(1)


# sudo processes that are not zombies and have no child: waiting for a password
SUDO_WAITING = ("for p in $(pgrep -x sudo); do "
                "[ \"$(ps -o stat= -p $p | cut -c1)\" != Z ] && [ -z \"$(pgrep -P $p)\" ] && echo $p; "
                "done")


# --------------------------------------------------- VNC desktop terminal
class VncTerminal:
    def __init__(self, page):
        self.page = page
        self.shell = None

    async def open(self):
        p = self.page
        await p.mouse.click(60, 15)            # Applications menu
        await p.wait_for_timeout(1500)
        await p.mouse.click(88, 75)            # Terminal Emulator
        await p.wait_for_timeout(5000)
        await p.keyboard.press("Alt+F10")      # maximise
        await p.wait_for_timeout(2000)
        term = ws("pgrep -n xfce4-terminal")
        self.shell = ws(f"pgrep -n -P {term} bash")
        log(f"VNC terminal shell pid {self.shell}")

    async def busy(self):
        return bool(ws(f"pgrep -P {self.shell}"))

    async def answer_sudo(self):
        """Press Enter at a sudo password prompt (the workspace user has an empty password)."""
        waiting = ws(SUDO_WAITING)
        if waiting:
            await asyncio.sleep(2)
            again = ws(SUDO_WAITING)
            if again and set(again.split()) & set(waiting.split()):
                log("answering sudo password prompt with Enter")
                await self.page.keyboard.press("Enter")

    async def run(self, cmd, opt):
        p = self.page
        await p.keyboard.type(cmd, delay=28)
        await p.keyboard.press("Enter")
        await asyncio.sleep(2)
        start = time.time()
        if "interrupt" in opt:
            while time.time() - start < opt["interrupt"]:
                await self.answer_sudo()
                await asyncio.sleep(3)
            log("pressing Ctrl+C")
            await p.keyboard.press("Control+c")
        if "tmux_view" in opt:
            await asyncio.sleep(opt["tmux_view"])
            await p.keyboard.press("Control+b")
            await p.keyboard.press("d")
        idle = 0
        while idle < 2:
            if time.time() - start > STEP_LIMIT:
                log(f"step exceeded {STEP_LIMIT}s, pressing Ctrl+C: {cmd[:60]}")
                await p.keyboard.press("Control+c")
                start = time.time()
            if await self.busy():
                idle = 0
                await self.answer_sudo()
            else:
                idle += 1
            await asyncio.sleep(2)
        await asyncio.sleep(1)


def influx_count(measurement):
    """Count the series of a measurement written to InfluxDB in the last 5 minutes."""
    token = ("TOKEN=$(grep -m1 token /workspace/examples/digital_twins/incubator/simulation.conf "
             "| cut -d'\"' -f2); ")
    return (token + "curl -s -X POST 'http://influxdb-server:8086/api/v2/query?org=incubator' "
            "-H \"Authorization: Token $TOKEN\" -H 'Content-Type: application/vnd.flux' "
            f"-d 'from(bucket:\"incubator\") |> range(start: -5m) |> filter(fn: (r) => r._measurement == \"{measurement}\") |> count()' "
            "| grep -c _result")


E = "/workspace/examples"
# example -> (step after which to look, command whose output is the evidence)
CHECKS = {
    "mass-spring-damper": ("lifecycle/execute", f"wc -l < {E}/data/mass-spring-damper/output/outputs.csv"),
    "water_tank_FI": ("lifecycle/analyze", f"ls {E}/data/water_tank_FI/output/plots"),
    "water_tank_swap": ("lifecycle/analyze", f"ls {E}/data/water_tank_swap/output/plots"),
    "heart_dt": ("sleep 20", "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:5001/ecg-data"),
    "drobotti_rmqfmu": ("lifecycle/execute", f"wc -l < {E}/digital_twins/drobotti_rmqfmu/target/outputs.csv"),
    "opc-ua-waterplant": ("lifecycle/execute", f"grep -c 'Simulation time' {E}/data/opc-ua-waterplant/output/execute.log"),
    "three-tank": ("lifecycle/execute", f"wc -l < {E}/data/three-tank/output/outputs.csv"),
    "flex-cell": ("lifecycle/execute", f"wc -l < {E}/data/flex-cell/output/outputs.csv"),
    "incubator": ("lifecycle/execute", influx_count("controller")),
    "o5g": ("tmux attach -t o5g", influx_count("prediction")),
    "mass-spring-damper-monitor": ("lifecycle/analyze", f"ls {E}/data/mass-spring-damper-monitor/output/plots"),
    "water_tank_FI_monitor": ("lifecycle/analyze", f"ls {E}/data/water_tank_FI_monitor/output/plots"),
    "incubator-NuRV-monitor-validation": ("lifecycle/analyze", f"ls {E}/data/incubator-NuRV-monitor-validation/output/plots"),
    "incubator-NuRV-monitor-service": ("lifecycle/execute", "ls /workspace/examples/digital_twins/incubator-NuRV-monitor-service/data | wc -l"),
    "incubator-NuRV-fmu-monitor-service": ("lifecycle/execute", "grep -c \"'_output': 1\" /tmp/nurv-fmu-service.log"),
    "incubator-TeSSLa-monitor-service": ("lifecycle/execute", "grep -c 'alert' /tmp/tessla.log"),
    "incubator-TeSSLa-active-control": ("lifecycle/execute", "grep -c 'Valid Message' /tmp/tessla.log"),
}


async def run_example(term, ex):
    """Run all steps of an example; False when OpenModelica could not be installed."""
    for cmd, opt in plan.steps(ex):
        log(f"{ex[0]}: {cmd[:90]}")
        await term.run(cmd, opt)
        step, check = CHECKS.get(ex[0], (None, None))
        if cmd == step:
            result = ws(check)
            report.append({"example": ex[0], "after": step, "evidence": result})
            log(f"{ex[0]} evidence: {result[:200]}")
        if cmd == "lifecycle/install" and not ws("command -v omc"):
            log(f"{ex[0]}: OpenModelica missing after install")
            await term.run("# OpenModelica could not be downloaded; this example is retried at the end", {})
            report.append({"example": ex[0], "check": "OpenModelica download failed"})
            return False
    return True


async def main():
    os.makedirs(OUT, exist_ok=True)
    with open("/tmp/demo-bashrc", "w") as f:
        f.write("PS1='\\[\\e[1;32m\\]dtaas@host\\[\\e[0m\\]:\\[\\e[1;34m\\]\\w\\[\\e[0m\\]\\$ '\n"
                "cd " + BASE + "\n")

    # screen + window manager + recorder
    sh(f"Xvfb {DISPLAY} -screen 0 {SIZE}x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &")
    time.sleep(2)
    subprocess.Popen(["openbox"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    video = f"{OUT}/dtaas-workspace-examples.mkv"
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "x11grab", "-framerate", "10",
         "-video_size", SIZE, "-i", DISPLAY, "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "26", "-pix_fmt", "yuv420p", "-g", "20", video],  # keyframe every 2 s
        env=env, stdin=subprocess.PIPE)
    global T0
    T0 = time.time()
    log(f"recording to {video}")

    host = HostTerminal()
    if not SKIP_HOST_INSTALL:
        chapter("Install DTaaS workspace-dex-localhost")
        for cmd in [
            "# DTaaS v1.0 workspace-dex-localhost installation",
            f"cd {BASE}",
            f"curl -LO {RELEASE}",
            "unzip -q workspace-dex-localhost-1.0.zip && cd workspace-dex-localhost && ls",
            "sed -n '/Quick Demo/,/Stop the demo/p' README.md",
            "cp .env.example .env",
            "cp config/dex-config.yaml.example config/dex-config.yaml",
            "# give the user workspace files to the workspace user (DTaaS installation docs)",
            "sudo chown -R 1000:100 files/*",
            "ls -ln files",
            "docker compose up -d",
            "sleep 20 && docker compose ps",
        ]:
            host.run(cmd)
    else:
        chapter("Existing DTaaS workspace-dex-localhost installation")
        host.run(f"cd {INSTALL} && docker compose ps")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False, ignore_default_args=["--enable-automation"],
            args=["--window-position=0,0", f"--window-size={SIZE.replace('x', ',')}",
                  "--no-first-run", "--disable-infobars"])
        ctx = await browser.new_context(no_viewport=True,
                                        permissions=["clipboard-read", "clipboard-write"])
        page = await ctx.new_page()

        chapter("Sign in and open the workspace desktop")
        await page.goto("http://localhost/")
        await page.wait_for_timeout(3000)
        await page.get_by_role("button", name="SignIn").click()
        await page.wait_for_url("**/dex/**", timeout=30000)
        await page.wait_for_timeout(1500)
        await page.locator("input[name=login]").type("user@intocps.org", delay=60)
        await page.locator("input[name=password]").type("user", delay=120)
        await page.wait_for_timeout(1000)
        await page.keyboard.press("Enter")
        await page.wait_for_url(re.compile(r".*/[Ll]ibrary.*"), timeout=60000)
        await page.wait_for_timeout(4000)
        await page.get_by_text("Workbench", exact=True).first.click()
        await page.wait_for_timeout(4000)
        async with ctx.expect_page(timeout=20000) as newp:
            await page.locator('button[title="Desktop-btn"]').click()
        vnc = await newp.value
        await vnc.wait_for_timeout(15000)
        term = VncTerminal(vnc)
        await term.open()

        chapter("Get the examples")
        for cmd in [f"# Get the DTaaS examples ({EXAMPLES_REPOSITORY}, branch {EXAMPLES_BRANCH})",
                    f"cd ~ && wget -q https://raw.githubusercontent.com/{EXAMPLES_REPOSITORY}/{EXAMPLES_BRANCH}/getExamples.sh",
                    f"REPOSITORY={EXAMPLES_REPOSITORY} BRANCH={EXAMPLES_BRANCH} bash getExamples.sh",
                    "ls /workspace/examples /workspace/examples/digital_twins"]:
            await term.run(cmd, {})

        chapter("Start RabbitMQ and InfluxDB services")
        for cmd in [
            "# RabbitMQ (with MQTT) and InfluxDB services used by some examples",
            "cd files/user/examples/common/digital_twins/incubator",
            "(cd incubator/communication/installation && docker compose up -d --build)",
            "(cd digital_twin/data_access/influxdbserver && unzip -q influxdb.zip -d influxdb && docker compose up -d --build)",
            "docker network connect dtaas_default rabbitmq-server && docker network connect dtaas_default influxdb-server",
            "sleep 15 && docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}'",
        ]:
            host.run(cmd)

        # back to the desktop
        sh("wmctrl -a Chromium || xdotool search --class chromium windowactivate")
        await vnc.bring_to_front()
        await vnc.wait_for_timeout(2000)
        await vnc.mouse.click(800, 500)
        await term.run("# Services are reachable from the workspace by name: rabbitmq-server, influxdb-server", {})
        await term.run("curl -s http://influxdb-server:8086/health; echo; (echo > /dev/tcp/rabbitmq-server/5672) && echo rabbitmq-server:5672 reachable", {})

        retry = []
        for ex in plan.EXAMPLES:
            if ONLY and ex[0] not in ONLY:
                continue
            chapter(ex[1])
            if not await run_example(term, ex):
                retry.append(ex)
        for attempt in range(1, 4):
            if not retry:
                break
            chapter(f"Retry {attempt} for OpenModelica examples")
            await term.run("# build.openmodelica.org was unreachable; wait 10 minutes and retry", {})
            await term.run("sleep 600", {})
            again = []
            for ex in retry:
                chapter(f"{ex[1]} (retry {attempt})")
                if not await run_example(term, ex):
                    again.append(ex)
            retry = again

        chapter("Done")
        await term.run("# All workspace examples finished", {})
        await vnc.wait_for_timeout(5000)
        await browser.close()

    ffmpeg.stdin.write(b"q")
    ffmpeg.stdin.flush()
    ffmpeg.wait(timeout=120)
    duration = time.time() - T0
    with open(f"{OUT}/chapters.txt", "w") as f:
        for t, title in chapters:
            f.write(f"{time.strftime('%H:%M:%S', time.gmtime(t))} {title}\n")
    meta = [";FFMETADATA1"]
    for i, (t, title) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else duration
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(t * 1000)}", f"END={int(end * 1000)}", f"title={title}"]
    with open(f"{OUT}/chapters.ffmeta", "w") as f:
        f.write("\n".join(meta) + "\n")
    sh(f"ffmpeg -loglevel error -y -i {video} -i {OUT}/chapters.ffmeta -map_metadata 1 -map_chapters 1 "
       f"-c copy -movflags +faststart {OUT}/dtaas-workspace-examples.mp4")
    with open(f"{OUT}/report.json", "w") as f:
        json.dump(report, f, indent=2)
    log("splitting the recording into one video per example")
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, "split.py", f"{OUT}/dtaas-workspace-examples.mp4"], cwd=here)
    log("compressing the videos for the web and making GIFs")
    subprocess.run([sys.executable, "postprocess.py", "--dir", OUT], cwd=here)
    log("finished")


if __name__ == "__main__":
    asyncio.run(main())
