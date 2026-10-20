"""The two terminals of the recording: xterm on the host and a terminal of the VNC desktop.

A step is typed into a terminal, which then waits until the step is done:
until the shell of the terminal has had no child process for two checks.
"""

import asyncio
import subprocess
import time

import browser
import config
from session import in_workspace, shell

RCFILE = "/tmp/demo-bashrc"
PROMPT = "PS1='\\[\\e[1;32m\\]dtaas@host\\[\\e[0m\\]:\\[\\e[1;34m\\]\\w\\[\\e[0m\\]\\$ '"

# sudo processes that are not zombies and have no child: waiting for a password
SUDO_WAITING = ("for p in $(pgrep -x sudo); do "
                "[ \"$(ps -o stat= -p $p | cut -c1)\" != Z ] "
                "&& [ -z \"$(pgrep -P $p)\" ] && echo $p; done")


class HostTerminal:
    """An xterm on the virtual screen, for the commands of the DTaaS administrator."""

    def __init__(self):
        with open(RCFILE, "w", encoding="utf-8") as file:
            file.write(f"{PROMPT}\ncd {config.BASE}\n")
        # the terminal runs until the recording ends
        subprocess.Popen(  # pylint: disable=consider-using-with
            ["xterm", "-title", "Host terminal - DTaaS installation and services",
             "-fa", "DejaVu Sans Mono", "-fs", "13", "-bg", "#1e1e1e", "-fg", "#e8e8e8",
             "-geometry", "160x40+0+0", "-maximized", "-e", "bash", "--rcfile", RCFILE, "-i"])
        time.sleep(3)
        self.window = shell("xdotool search --name 'Host terminal'").stdout.split()[0]
        self.shell = shell(f"pgrep -n -f 'bash --rcfile {RCFILE}'").stdout.strip()

    def activate(self):
        """Bring the terminal to the front."""
        shell(f"xdotool windowactivate --sync {self.window}")
        time.sleep(1)

    def run(self, command):
        """Type a command and wait until it is done or runs out of time."""
        self.activate()
        subprocess.run(["xdotool", "type", "--window", self.window, "--delay", "30", command],
                       check=False)
        subprocess.run(["xdotool", "key", "--window", self.window, "Return"], check=False)
        time.sleep(1.5)
        start, idle = time.time(), 0
        while idle < 2 and time.time() - start < config.STEP_LIMIT:
            idle = 0 if shell(f"pgrep -P {self.shell}").stdout.strip() else idle + 1
            time.sleep(1)
        time.sleep(1)


class VncTerminal:
    """A terminal of the workspace desktop, typed into through the browser."""

    def __init__(self, page, log):
        self.page = page
        self.log = log
        self.shell = None

    async def open(self):
        """Open a terminal from the Applications menu and maximise it."""
        await self.page.mouse.click(60, 15)  # Applications menu
        await self.page.wait_for_timeout(1500)
        await self.page.mouse.click(88, 75)  # Terminal Emulator
        await self.page.wait_for_timeout(5000)
        await self.page.keyboard.press("Alt+F10")
        await self.page.wait_for_timeout(2000)
        terminal = in_workspace("pgrep -n xfce4-terminal")
        self.shell = in_workspace(f"pgrep -n -P {terminal} bash")
        self.log(f"VNC terminal shell pid {self.shell}")

    async def answer_sudo(self):
        """Press Enter at a sudo password prompt; the workspace user has an empty password."""
        waiting = in_workspace(SUDO_WAITING)
        if waiting:
            await asyncio.sleep(2)
            still = in_workspace(SUDO_WAITING)
            if set(still.split()) & set(waiting.split()):
                self.log("answering sudo password prompt with Enter")
                await self.page.keyboard.press("Enter")

    async def run(self, command, options):
        """Type a command, handle its options and wait until it is done."""
        await self.page.keyboard.type(command, delay=28)
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(2)
        if "interrupt" in options:
            await self._interrupt_after(options["interrupt"])
        if "desktop" in options:
            await self._act_on_desktop(options["desktop"])
        if "dtaas_page" in options:
            await browser.show_dtaas_page(self.page, *options["dtaas_page"])
        if "tmux_view" in options:
            await asyncio.sleep(options["tmux_view"])
            await self.page.keyboard.press("Control+b")
            await self.page.keyboard.press("d")
        await self._wait_until_done(command)

    async def _act_on_desktop(self, actions):
        """Wait (a number of seconds), press a key (a string) or click ("click", x, y)."""
        for action in actions:
            if isinstance(action, (int, float)):
                await asyncio.sleep(action)
            elif isinstance(action, str):
                await self.page.keyboard.press(action)
                await asyncio.sleep(0.4)
            else:
                await self.page.mouse.click(action[1], action[2])

    async def _interrupt_after(self, seconds):
        """Let a long-running step run for a while, then press Ctrl+C."""
        start = time.time()
        while time.time() - start < seconds:
            await self.answer_sudo()
            await asyncio.sleep(3)
        self.log("pressing Ctrl+C")
        await self.page.keyboard.press("Control+c")

    async def _wait_until_done(self, command):
        """Wait until the shell has no child; interrupt a step that hangs."""
        start, idle = time.time(), 0
        while idle < 2:
            if time.time() - start > config.STEP_LIMIT:
                self.log(f"step exceeded {config.STEP_LIMIT}s, pressing Ctrl+C: {command[:60]}")
                await self.page.keyboard.press("Control+c")
                start = time.time()
            if in_workspace(f"pgrep -P {self.shell}"):
                idle = 0
                await self.answer_sudo()
            else:
                idle += 1
            await asyncio.sleep(2)
        await asyncio.sleep(1)
