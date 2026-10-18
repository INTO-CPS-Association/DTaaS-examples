"""Post-process a recording: sped-up videos for the web and GIFs per example.

Run after split.py, inside the recording container.

Usage: python3 postprocess.py [--dir DIR] [--web] [--gif] [options]
  --dir      recording directory (default /opt/recording); it holds
             dtaas-workspace-examples.mp4 and driver.log
  --web      write web/: one H.264 video per chapter and the full video
             joined from them, sped up step by step (see speed.py)
  --gif      write gif/: one GIF per example, made from its web video
  Without --web or --gif, both are done; --gif needs the web videos.

Steps that show results play at --result-speed (1) for at most
--result-seconds (60), steps longer than --long seconds (20) at
--fast-speed (16), and the rest at --speed (4). The videos keep the size of
the screen so that the terminal text stays sharp; GIFs of scrolling output
are still large, so embed the web videos where size matters.
"""

import argparse
import shutil
import tempfile
from pathlib import Path

from config import FPS, OUT, VIDEO
from media import chapters, duration, ffmpeg, is_example, segment_name, size
from recorder import chapter_metadata
from speed import Speeds, log_steps, speed_plan


def web_video(video, parts, out, crf, tmp):
    """Speed up each part, join the parts and encode them once for the web.

    The parts stay lossless until the final encoding. Screen recordings are
    mostly flat areas and text: tune for animation, and keep the size of the
    screen, since scaling blurs the text.
    """
    files = []
    for i, (start, end, speed) in enumerate(parts):
        files.append(tmp / f"part{i:03d}.mkv")
        ffmpeg("-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", video,
               "-vf", f"setpts=(PTS-STARTPTS)/{speed},fps={FPS}", "-an",
               "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0", files[-1])
    listing = tmp / "parts.txt"
    listing.write_text("".join(f"file '{f}'\n" for f in files), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", listing, "-c:v", "libx264", "-preset", "slow",
           "-tune", "animation", "-crf", crf, "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out)
    for file in files + [listing]:
        file.unlink()


def join_videos(videos, titles, out):
    """Join the web videos of the chapters into one video with chapters."""
    starts, total = [], 0.0
    for video, title in zip(videos, titles):
        starts.append((total, title))
        total += duration(video)
    listing, ffmeta = out.with_suffix(".txt"), out.with_suffix(".ffmeta")
    listing.write_text("".join(f"file '{v.resolve()}'\n" for v in videos), encoding="utf-8")
    ffmeta.write_text(chapter_metadata(starts, total), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", listing, "-i", ffmeta, "-map", "0:v",
           "-map_metadata", "1", "-map_chapters", "1", "-c", "copy",
           "-movflags", "+faststart", out)
    listing.unlink()
    ffmeta.unlink()


def gif(video, out, fps, colors):
    """GIF of a web video at its size, with a palette made for it.

    mpdecimate drops frames in which nothing changes (a GIF frame can last
    any time); no dithering keeps the text sharp, and terminal text needs
    few colours, which compress much better.
    """
    ffmpeg("-i", video, "-filter_complex",
           f"fps={fps},mpdecimate,split[a][b];"
           f"[a]palettegen=max_colors={colors}:stats_mode=diff[p];"
           "[b][p]paletteuse=dither=none:diff_mode=rectangle", out)


def make_web(base, found, videos, args):
    """Write the web video of every chapter and the full web video."""
    speeds = Speeds(args.speed, args.fast_speed, args.result_speed, args.long,
                    args.result_seconds)
    steps = log_steps((base / "driver.log").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(dir=base) as tmp:
        for (start, end, _), video in zip(found, videos):
            parts = speed_plan((start, end), steps, speeds)
            web_video(base / f"{VIDEO}.mp4", parts, video, args.crf, Path(tmp))
            plan = " ".join(f"{b - a:.0f}s@{s:g}x" for a, b, s in parts)
            print(f"web  {video.relative_to(base)}  {size(video)}  {plan}", flush=True)
    full = base / "web" / f"{VIDEO}.mp4"
    join_videos(videos, [title for _, _, title in found], full)
    print(f"web  {full.relative_to(base)}  {size(full)}", flush=True)


def make_gifs(base, found, videos, args):
    """Write a GIF for every chapter of an example, from its web video."""
    shutil.rmtree(base / "gif", ignore_errors=True)
    (base / "gif").mkdir()
    for (_, _, title), video in zip(found, videos):
        if is_example(title):
            out = base / "gif" / f"{video.stem}.gif"
            gif(video, out, args.gif_fps, args.gif_colors)
            print(f"gif  {out.relative_to(base)}  {size(out)}", flush=True)


def parse_args():
    """The command line; the defaults of the speeds come from Speeds."""
    defaults = Speeds()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default=OUT)
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--gif", action="store_true")
    parser.add_argument("--speed", type=float, default=defaults.normal)
    parser.add_argument("--fast-speed", type=float, default=defaults.fast)
    parser.add_argument("--result-speed", type=float, default=defaults.result)
    parser.add_argument("--long", type=float, default=defaults.long)
    parser.add_argument("--result-seconds", type=float, default=defaults.result_seconds)
    parser.add_argument("--crf", type=int, default=24, help="H.264 quality of the web videos")
    parser.add_argument("--gif-fps", type=int, default=5)
    parser.add_argument("--gif-colors", type=int, default=32, help="at most 256")
    return parser.parse_args()


def main():
    """Make the web videos, the GIFs or both."""
    args = parse_args()
    base = Path(args.dir)
    found = chapters(base / f"{VIDEO}.mp4")
    (base / "web" / "segments").mkdir(parents=True, exist_ok=True)
    videos = [base / "web" / "segments" / segment_name(i, title)
              for i, (_, _, title) in enumerate(found, 1)]
    if args.web or not args.gif:
        make_web(base, found, videos, args)
    if args.gif or not args.web:
        make_gifs(base, found, videos, args)


if __name__ == "__main__":
    main()
