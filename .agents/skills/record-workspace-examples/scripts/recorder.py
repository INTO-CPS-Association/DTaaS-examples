"""The virtual screen, its recording and the chapters of the recorded video."""

import subprocess
import time

import config


class Recorder:
    """Xvfb with openbox, recorded by ffmpeg to an MKV file."""

    def __init__(self, out=config.OUT):
        self.out = out
        self.video = f"{out}/{config.VIDEO}.mkv"
        self.processes = []

    def start(self):
        """Start the screen, the window manager and the recording."""
        # the processes run until stop(), so they are not started in a with block
        # pylint: disable=consider-using-with
        size = f"{config.SIZE}x24"
        self.processes.append(subprocess.Popen(
            ["Xvfb", config.DISPLAY, "-screen", "0", size, "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(2)
        self.processes.append(subprocess.Popen(
            ["openbox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(2)
        # a keyframe every 2 s keeps the cuts into segments accurate
        self.processes.append(subprocess.Popen(
            ["ffmpeg", "-loglevel", "error", "-y", "-f", "x11grab",
             "-framerate", str(config.FPS), "-video_size", config.SIZE, "-i", config.DISPLAY,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p",
             "-g", str(2 * config.FPS), self.video], stdin=subprocess.PIPE))

    def stop(self):
        """Stop the recording; the screen stays until the container stops."""
        ffmpeg = self.processes[-1]
        ffmpeg.stdin.write(b"q")
        ffmpeg.stdin.flush()
        ffmpeg.wait(timeout=120)

    def finish(self, chapters, duration):
        """Write the chapters and remux the recording into an MP4 with them."""
        with open(f"{self.out}/chapters.txt", "w", encoding="utf-8") as file:
            file.write(chapter_list(chapters))
        ffmeta = f"{self.out}/chapters.ffmeta"
        with open(ffmeta, "w", encoding="utf-8") as file:
            file.write(chapter_metadata(chapters, duration))
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", self.video, "-i", ffmeta,
             "-map_metadata", "1", "-map_chapters", "1", "-c", "copy",
             "-movflags", "+faststart", f"{self.out}/{config.VIDEO}.mp4"], check=True)


def chapter_list(chapters):
    """The chapters as lines of start time and title."""
    return "".join(f"{time.strftime('%H:%M:%S', time.gmtime(start))} {title}\n"
                   for start, title in chapters)


def chapter_metadata(chapters, duration):
    """The chapters in the FFMETADATA format; each lasts until the next one."""
    lines = [";FFMETADATA1"]
    ends = [start for start, _ in chapters[1:]] + [duration]
    for (start, title), end in zip(chapters, ends):
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(start * 1000)}",
                  f"END={int(end * 1000)}", f"title={title}"]
    return "\n".join(lines) + "\n"
