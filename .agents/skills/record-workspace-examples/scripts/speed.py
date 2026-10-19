"""How fast each part of a chapter plays in the web videos, from the steps in driver.log.

A step lasts from the time the driver logged it until the next step or
chapter starts. Steps that show results play at the result speed, for a
limited time; long steps, whose output scrolls past, play fast; the rest
plays at the normal speed of the web videos.
"""

import re
from dataclasses import dataclass

from config import FPS

# Commands whose step shows results: plots and web pages in Firefox, the
# first lines of an output file, the o5g dashboard, and the show_ scripts an
# example keeps in its lifecycle folder, such as the readings of the BIM one
RESULT = re.compile(r"(firefox |head |tmux attach|\.venv/bin/python lifecycle/show_)")
LOG_LINE = re.compile(r"\[(\d\d):(\d\d):(\d\d)\] (?:CHAPTER |([\w.-]+): )(.*)")


@dataclass(frozen=True)
class Speeds:
    """Speed-up factors, and the step lengths that choose between them."""

    normal: float = 4
    fast: float = 16
    result: float = 1
    long: float = 20  # seconds; longer steps play fast
    result_seconds: float = 60  # how long a result plays at the result speed


def log_steps(text):
    """(time, command or None) of every step and chapter in the text of driver.log.

    A chapter starts without a step; evidence and other notes are not steps.
    """
    steps = []
    for line in text.splitlines():
        match = LOG_LINE.fullmatch(line)
        if not match or (match.group(4) and match.group(5).startswith("evidence")):
            continue
        hours, minutes, seconds = (int(match.group(i)) for i in (1, 2, 3))
        steps.append((hours * 3600 + minutes * 60 + seconds,
                      match.group(5) if match.group(4) else None))
    return steps


def step_parts(command, step, shown, speeds):
    """(from, to, speed) parts of the shown interval of one step.

    step is the (start, end) of the whole step, shown the part of it in the
    chapter. A result plays at its speed for result_seconds only, so that a
    stalled step does not become minutes of a still screen.
    """
    start, end = shown
    if command and RESULT.match(command):
        limit = step[0] + speeds.result_seconds
        if start < limit < end:
            return [(start, limit, speeds.result), (limit, end, speeds.fast)]
        return [(start, end, speeds.result if start < limit else speeds.fast)]
    if command and step[1] - step[0] > speeds.long:
        return [(start, end, speeds.fast)]
    return [(start, end, speeds.normal)]


def join_short(parts):
    """Join each part too short for a few frames to the part before (or after) it."""
    def short(part):
        return (part[1] - part[0]) / part[2] < 3 / FPS

    parts = list(parts)
    while len(parts) > 1 and any(short(p) for p in parts):
        i = next(i for i, p in enumerate(parts) if short(p))
        if i > 0:
            parts[i - 1:i + 1] = [(parts[i - 1][0], parts[i][1], parts[i - 1][2])]
        else:
            parts[0:2] = [(parts[0][0], parts[1][1], parts[1][2])]
    return parts


def merge_equal(parts):
    """Merge adjacent parts of equal speed."""
    merged = []
    for start, end, speed in parts:
        if merged and merged[-1][2] == speed:
            merged[-1] = (merged[-1][0], end, speed)
        else:
            merged.append((start, end, speed))
    return merged


def speed_plan(chapter, steps, speeds=Speeds()):
    """(from, to, speed) parts covering a chapter (start, end) of the recording."""
    marks = [(0, None)] + steps + [(float("inf"), None)]
    parts = []
    for (begin, command), (finish, _) in zip(marks, marks[1:]):
        shown = (max(begin, chapter[0]), min(finish, chapter[1]))
        if shown[0] < shown[1]:
            parts += step_parts(command, (begin, finish), shown, speeds)
    return merge_equal(join_short(parts))


def played(parts):
    """Seconds that the parts last in the web video."""
    return sum((end - start) / speed for start, end, speed in parts)
