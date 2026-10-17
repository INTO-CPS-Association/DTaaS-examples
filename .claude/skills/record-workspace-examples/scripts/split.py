"""Cut the recording into one video per chapter, that is, one per example.

The chapters come from the recording itself (the driver writes them into the
MP4). Example chapters are named after the example directory, for example
05-drobotti_rmqfmu.mp4; retries get a -retry-<n> suffix; the setup chapters
(sign-in, examples download, services) get their own segments too.

Usage: python3 split.py [video] [--out DIR] [--copy]
  video   recording with chapters (default /opt/recording/dtaas-workspace-examples.mp4)
  --out   output directory (default: "segments" next to the video)
  --copy  cut without re-encoding; fast, but cuts snap to keyframes
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import plan

TITLES = {title: name for name, title, _ in plan.EXAMPLES}


def chapters(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_chapters", str(video)],
        capture_output=True, text=True, check=True).stdout
    return [(float(c["start_time"]), float(c["end_time"]), c.get("tags", {}).get("title", ""))
            for c in json.loads(out)["chapters"]]


def segment_name(index, title):
    retry = re.fullmatch(r"(.*) \(retry (\d+)\)", title)
    base = retry.group(1) if retry else title
    name = TITLES.get(base) or re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "chapter"
    if retry:
        name += f"-retry-{retry.group(2)}"
    return f"{index:02d}-{name}.mp4"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video", nargs="?", default="/opt/recording/dtaas-workspace-examples.mp4")
    parser.add_argument("--out")
    parser.add_argument("--copy", action="store_true")
    args = parser.parse_args()

    video = Path(args.video)
    out = Path(args.out) if args.out else video.parent / "segments"
    out.mkdir(parents=True, exist_ok=True)
    found = chapters(video)
    if not found:
        raise SystemExit(f"{video} has no chapters")

    if args.copy:
        codec = ["-c", "copy"]
    else:
        codec = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                 "-pix_fmt", "yuv420p", "-g", "20"]
    index = []
    for i, (start, end, title) in enumerate(found, 1):
        name = segment_name(i, title)
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", str(video),
             "-t", f"{end - start:.3f}", "-map", "0:v", *codec,
             "-metadata", f"title={title}", "-movflags", "+faststart", str(out / name)],
            check=True)
        index.append(f"{name}\t{time_of(start)}\t{time_of(end - start)}\t{title}")
        print(f"{name}  {time_of(end - start)}  {title}", flush=True)
    (out / "index.txt").write_text("file\tstart\tduration\ttitle\n" + "\n".join(index) + "\n")


def time_of(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


if __name__ == "__main__":
    main()
