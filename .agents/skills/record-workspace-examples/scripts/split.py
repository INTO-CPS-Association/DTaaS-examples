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
from pathlib import Path

from config import FPS, OUT, VIDEO
from media import chapters, ffmpeg, segment_name

ENCODE = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
          "-pix_fmt", "yuv420p", "-g", str(2 * FPS)]


def time_of(seconds):
    """Seconds as HH:MM:SS."""
    seconds = int(round(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def cut(video, chapter, out, codec):
    """Cut one chapter (start, end, title) of the video into out."""
    start, end, title = chapter
    ffmpeg("-ss", f"{start:.3f}", "-i", video, "-t", f"{end - start:.3f}", "-map", "0:v",
           *codec, "-metadata", f"title={title}", "-movflags", "+faststart", out)


def split(video, out, codec):
    """Cut every chapter and write index.txt; the rows of the index."""
    out.mkdir(parents=True, exist_ok=True)
    found = chapters(video)
    if not found:
        raise SystemExit(f"{video} has no chapters")
    index = []
    for i, (start, end, title) in enumerate(found, 1):
        name = segment_name(i, title)
        cut(video, (start, end, title), out / name, codec)
        index.append(f"{name}\t{time_of(start)}\t{time_of(end - start)}\t{title}")
        print(f"{name}  {time_of(end - start)}  {title}", flush=True)
    (out / "index.txt").write_text("file\tstart\tduration\ttitle\n" + "\n".join(index) + "\n",
                                   encoding="utf-8")
    return index


def main():
    """Cut the recording given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video", nargs="?", default=f"{OUT}/{VIDEO}.mp4")
    parser.add_argument("--out")
    parser.add_argument("--copy", action="store_true")
    args = parser.parse_args()
    video = Path(args.video)
    out = Path(args.out) if args.out else video.parent / "segments"
    split(video, out, ["-c", "copy"] if args.copy else ENCODE)


if __name__ == "__main__":
    main()
