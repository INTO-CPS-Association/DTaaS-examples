"""ffmpeg and ffprobe helpers shared by split.py and postprocess.py."""

import json
import re
import subprocess

from examples import TITLES


def ffmpeg(*args):
    """Run ffmpeg quietly, overwriting the output; fail on an error."""
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *map(str, args)], check=True)


def probe(video, *args):
    """Output of ffprobe for a video."""
    return subprocess.run(["ffprobe", "-v", "error", *args, str(video)],
                          capture_output=True, text=True, check=True).stdout


def duration(video):
    """Length of a video in seconds."""
    return float(probe(video, "-show_entries", "format=duration", "-of", "csv=p=0"))


def chapters(video):
    """(start, end, title) of the chapters of a video."""
    found = json.loads(probe(video, "-print_format", "json", "-show_chapters"))["chapters"]
    return [(float(c["start_time"]), float(c["end_time"]), c.get("tags", {}).get("title", ""))
            for c in found]


def size(path):
    """Size of a file in megabytes, for printing."""
    return f"{path.stat().st_size / 1e6:.1f} MB"


def base_title(title):
    """Title of a chapter without its retry suffix."""
    return re.sub(r" \(retry \d+\)$", "", title)


def is_example(title):
    """Whether a chapter shows an example, not a setup step."""
    return base_title(title) in TITLES


def segment_name(index, title):
    """File name of a chapter: NN-<example directory>, with -retry-<n> for retries.

    Setup chapters are named after their title.
    """
    retry = re.fullmatch(r"(.*) \(retry (\d+)\)", title)
    base = base_title(title)
    name = TITLES.get(base) or re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "chapter"
    if retry:
        name += f"-retry-{retry.group(2)}"
    return f"{index:02d}-{name}.mp4"
