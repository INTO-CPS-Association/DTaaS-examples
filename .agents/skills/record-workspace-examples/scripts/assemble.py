"""Assemble one set of videos of all examples from several recordings (takes).

Usage: python3 assemble.py OUT TAKE [TAKE ...]

Each take is a fetched recording directory, post-processed: it holds
segments/ with index.txt, web/segments/, gif/ and report.json. The setup
chapters before the first example come from the first take. Every example
comes from the latest take, in the order given, that recorded it with
evidence; when no take has evidence for it, from the latest take that
recorded it. OUT then holds segments/, web/segments/, gif/, the full web
video with chapters, index.txt with the take of each chapter, and
report.json.
"""

import argparse
import json
import shutil
from pathlib import Path

from config import VIDEO
from examples import EXAMPLES, TITLES
from media import base_title, duration, is_example
from postprocess import join_videos


def chapters_of(take):
    """(file stem, title) of the chapters of a take, from segments/index.txt."""
    rows = (take / "segments" / "index.txt").read_text(encoding="utf-8").splitlines()[1:]
    return [(row.split("\t")[0].removesuffix(".mp4"), row.split("\t")[3]) for row in rows]


def evidence_of(take):
    """Evidence entries of a take by example."""
    path = take / "report.json"
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return {entry["example"]: entry for entry in entries}


def has_evidence(entry):
    """Whether an evidence entry shows that the example worked."""
    return bool(entry) and "check" not in entry and entry.get("evidence", "") not in ("", "0")


def setup_chapters(take):
    """(take, stem, title) of the chapters before the first example of a take."""
    chosen = []
    for stem, title in chapters_of(take):
        if is_example(title):
            break
        chosen.append((take, stem, title))
    return chosen


def example_chapters(takes):
    """(take, stem, title) of every example, from the take chosen for it.

    A retry counts as a recording of its example; it comes after the first
    attempt, and the evidence of a take is the last one of the example.
    """
    found = {}  # title -> [(take, stem, evidence)] in the order of the takes
    for take in takes:
        report = evidence_of(take)
        for stem, title in chapters_of(take):
            if is_example(title):
                name = TITLES[base_title(title)]
                found.setdefault(base_title(title), []).append((take, stem, report.get(name)))
    chosen = []
    for _, title, _ in EXAMPLES:
        candidates = found.get(title, [])
        good = [c for c in candidates if has_evidence(c[2])]
        if good or candidates:
            take, stem, _ = (good or candidates)[-1]
            chosen.append((take, stem, title))
    return chosen


def copy_chapter(take, stem, out, new):
    """Copy the segment, web video and GIF of a chapter to the new file stem."""
    for sub, suffix in (("segments", ".mp4"), ("web/segments", ".mp4"), ("gif", ".gif")):
        source = take / sub / f"{stem}{suffix}"
        if source.exists():
            shutil.copy(source, out / sub / f"{new}{suffix}")
    return new


def assemble(out, takes):
    """Copy the chosen chapters into out and write its index and report."""
    for sub in ("segments", "web/segments", "gif"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    chosen = setup_chapters(takes[0]) + example_chapters(takes)
    index, report = [], []
    for number, (take, stem, title) in enumerate(chosen, 1):
        new = f"{number:02d}-{TITLES.get(title) or stem.split('-', 1)[1]}"
        copy_chapter(take, stem, out, new)
        index.append((new, take.name, title))
        entry = evidence_of(take).get(TITLES.get(title))
        if entry:
            report.append({**entry, "take": take.name})
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return index


def main():
    """Assemble the takes given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument("takes", type=Path, nargs="+")
    args = parser.parse_args()
    index = assemble(args.out, args.takes)
    videos = [args.out / "web" / "segments" / f"{new}.mp4" for new, _, _ in index]
    join_videos(videos, [title for _, _, title in index], args.out / "web" / f"{VIDEO}.mp4")
    rows = [f"{new}.mp4\t{take}\t{duration(args.out / 'segments' / f'{new}.mp4'):.0f}s\t{title}"
            for new, take, title in index]
    text = "file\ttake\tduration\ttitle\n" + "\n".join(rows) + "\n"
    (args.out / "index.txt").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
