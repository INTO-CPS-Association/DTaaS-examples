"""The clock, log, chapters and evidence of a recording, and the commands it runs."""

import json
import subprocess
import time

import config


class Session:
    """The clock of a recording with its log, chapters and evidence report."""

    def __init__(self, out=config.OUT):
        self.out = out
        self.start = time.time()
        self.chapters = []
        self.report = []

    def elapsed(self):
        """Seconds since the recording started."""
        return time.time() - self.start

    def restart_clock(self):
        """Start the clock again when the screen recording starts."""
        self.start = time.time()

    def log(self, message):
        """Print a message with the recording time and append it to driver.log."""
        stamp = time.strftime("%H:%M:%S", time.gmtime(self.elapsed()))
        line = f"[{stamp}] {message}"
        print(line, flush=True)
        with open(f"{self.out}/driver.log", "a", encoding="utf-8") as file:
            file.write(line + "\n")

    def chapter(self, title):
        """Start a chapter of the video at the current time."""
        self.chapters.append((self.elapsed(), title))
        self.log(f"CHAPTER {title}")

    def add_evidence(self, entry):
        """Add an entry to the evidence report."""
        self.report.append(entry)

    def write_report(self):
        """Write the evidence report to report.json."""
        with open(f"{self.out}/report.json", "w", encoding="utf-8") as file:
            json.dump(self.report, file, indent=2)


def shell(command):
    """Run a shell command in the recording container and return its result."""
    return subprocess.run(command, shell=True, capture_output=True, text=True, check=False)


def in_workspace(command):
    """Run a command as the user of the workspace container and return its output."""
    result = subprocess.run(
        ["docker", "exec", "-u", "user", config.WORKSPACE, "bash", "-c", command],
        capture_output=True, text=True, check=False)
    return result.stdout.strip()
