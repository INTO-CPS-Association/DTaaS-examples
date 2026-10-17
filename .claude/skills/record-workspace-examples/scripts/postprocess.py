"""Post-process a recording: compressed videos for the web and GIFs per example.

Run after split.py, inside the recording container.

Usage: python3 postprocess.py [--dir DIR] [--web] [--gif] [options]
  --dir          recording directory (default /opt/recording); it holds
                 dtaas-workspace-examples.mp4 and segments/ from split.py
  --web          write web/: the full recording and every segment as H.264
                 MP4, scaled to --width, with faststart for streaming
  --gif          write gif/: one GIF per example, sped up so that it lasts at
                 most --gif-seconds; at the size of the screen unless
                 --gif-width is given, so that the terminal text stays sharp
  Without --web or --gif, both are done.

GIFs of scrolling terminal output are large because every frame changes;
embed the web MP4s where size matters.
"""
import argparse
import re
import subprocess
from pathlib import Path

from split import TITLES, chapters, segment_name

FULL = "dtaas-workspace-examples.mp4"


def size(path):
    return f"{path.stat().st_size / 1e6:.1f} MB"


def web(video, out, width, crf):
    """Screen recordings are mostly flat areas and text: tune for animation.

    Keep the default keyframe interval; the short one of the recording
    (for accurate cuts) more than doubles the size.
    """
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-map", "0:v",
         "-vf", f"scale={width}:-2:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
         "-tune", "animation", "-crf", str(crf), "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(out)], check=True)


def join(parts, chapters_from, out):
    """Join the web segments into the full video; encoding it again would
    double the work. The segments cover the recording, so the chapters of
    the recording fit."""
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-i", str(chapters_from), "-map", "0:v", "-map_metadata", "1", "-map_chapters", "1",
         "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    listing.unlink()


def gif(video, start, length, out, width, fps, colors, max_seconds):
    """GIF of a part of the recording, sped up to at most max_seconds.

    The part comes from the recording itself, not from a segment, to avoid
    a second lossy encoding that blurs the text. Scaling blurs it too, so
    the GIF keeps the size of the screen unless a width is given.
    mpdecimate drops frames in which nothing changes (a GIF frame can last
    any time); the palette is made for the part, without dithering. Terminal
    text needs few colours, and fewer colours compress much better.
    """
    speed = max(1.0, length / max_seconds)
    scale = f"scale={width}:-1:flags=lanczos," if width else ""
    graph = (f"setpts=PTS/{speed:.4f},fps={fps},mpdecimate,{scale}"
             f"split[a][b];[a]palettegen=max_colors={colors}:stats_mode=diff[p];"
             "[b][p]paletteuse=dither=none:diff_mode=rectangle")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{start:.3f}",
                    "-t", f"{length:.3f}", "-i", str(video),
                    "-filter_complex", graph, str(out)], check=True)
    return speed


def index(segments):
    """(segment, title) in recording order, from the index of split.py."""
    for row in (segments / "index.txt").read_text().splitlines()[1:]:
        name, _, _, title = row.split("\t", 3)
        yield segments / name, title


def example_chapters(video):
    """(name, start, length) of the chapters of examples, not of the setup
    steps; named like the segments of split.py."""
    for i, (start, end, title) in enumerate(chapters(video), 1):
        if re.sub(r" \(retry \d+\)$", "", title) in TITLES:
            yield Path(segment_name(i, title)).stem, start, end - start


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default="/opt/recording")
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--gif", action="store_true")
    parser.add_argument("--width", type=int, default=1280, help="width of the web videos")
    parser.add_argument("--crf", type=int, default=30, help="H.264 quality of the web videos")
    parser.add_argument("--gif-width", type=int, default=0,
                        help="width of the GIFs; 0 keeps the size of the screen")
    parser.add_argument("--gif-fps", type=int, default=5)
    parser.add_argument("--gif-colors", type=int, default=32,
                        help="palette size of the GIFs, at most 256")
    parser.add_argument("--gif-seconds", type=int, default=45, help="maximum GIF length")
    args = parser.parse_args()
    do_web = args.web or not args.gif
    do_gif = args.gif or not args.web

    base = Path(args.dir)
    segments = base / "segments"
    if not (segments / "index.txt").exists():
        raise SystemExit(f"{segments}/index.txt is missing; run split.py first")

    if do_web:
        (base / "web").mkdir(exist_ok=True)
        (base / "web" / "segments").mkdir(exist_ok=True)
        parts = []
        for src, _ in index(segments):
            dst = base / "web" / "segments" / src.name
            web(src, dst, args.width, args.crf)
            parts.append(dst)
            print(f"web  {dst.relative_to(base)}  {size(src)} -> {size(dst)}", flush=True)
        join(parts, base / FULL, base / "web" / FULL)
        print(f"web  web/{FULL}  {size(base / FULL)} -> {size(base / 'web' / FULL)}", flush=True)

    if do_gif:
        (base / "gif").mkdir(exist_ok=True)
        for name, start, length in example_chapters(base / FULL):
            dst = base / "gif" / (name + ".gif")
            speed = gif(base / FULL, start, length, dst, args.gif_width, args.gif_fps,
                        args.gif_colors, args.gif_seconds)
            print(f"gif  {dst.relative_to(base)}  {speed:.1f}x speed  {size(dst)}", flush=True)


if __name__ == "__main__":
    main()
