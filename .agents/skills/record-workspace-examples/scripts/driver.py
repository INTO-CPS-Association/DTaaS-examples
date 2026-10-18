"""Record a DTaaS workspace-dex-localhost session with the workspace examples.

Runs inside the recording container (Xvfb, xterm, Playwright Chromium, ffmpeg
and the Docker CLI). Commands of the DTaaS administrator are typed into
xterm; the examples are typed into a terminal of the VNC desktop through the
browser. At the end, the recording is cut into one video per chapter
(split.py) and post-processed (postprocess.py).

Usage: python driver.py [--skip-install] [example ...]
"""

import argparse
import asyncio
import os
import subprocess
import sys

# Playwright is installed in the recording container only
from playwright.async_api import async_playwright  # pylint: disable=import-error

import browser
import config
import examples
import setup_steps
from checks import check_after
from recorder import Recorder
from session import Session, in_workspace
from terminals import HostTerminal, VncTerminal


async def run_example(session, terminal, example):
    """Run the steps of an example; False when OpenModelica could not be installed."""
    name = example[0]
    for command, options in examples.steps(example):
        session.log(f"{name}: {command[:90]}")
        await terminal.run(command, options)
        check = check_after(name, command)
        if check:
            result = in_workspace(check)
            session.add_evidence({"example": name, "after": command, "evidence": result})
            session.log(f"{name} evidence: {result[:200]}")
        if command == "lifecycle/install" and not in_workspace("command -v omc"):
            session.log(f"{name}: OpenModelica missing after install")
            await terminal.run("# OpenModelica could not be downloaded; "
                               "this example is retried at the end", {})
            session.add_evidence({"example": name, "check": "OpenModelica download failed"})
            return False
    return True


async def run_examples(session, terminal, chosen, suffix=""):
    """Run examples, each in its own chapter; the ones to retry."""
    retry = []
    for example in chosen:
        session.chapter(example[1] + suffix)
        if not await run_example(session, terminal, example):
            retry.append(example)
    return retry


async def run_with_retries(session, terminal, chosen):
    """Run the examples, and retry those whose OpenModelica download failed."""
    retry = await run_examples(session, terminal, chosen)
    for attempt in range(1, config.RETRIES + 1):
        if not retry:
            break
        session.chapter(f"Retry {attempt} for OpenModelica examples")
        await terminal.run("# build.openmodelica.org was unreachable; "
                           "wait 10 minutes and retry", {})
        await terminal.run(f"sleep {config.RETRY_WAIT}", {})
        retry = await run_examples(session, terminal, retry, f" (retry {attempt})")


def show_installation(session, host, skip_install):
    """Install DTaaS in the host terminal, or show the existing installation."""
    if skip_install:
        session.chapter("Existing DTaaS workspace-dex-localhost installation")
        commands = setup_steps.EXISTING_INSTALL
    else:
        session.chapter("Install DTaaS workspace-dex-localhost")
        commands = setup_steps.INSTALL
    for command in commands:
        host.run(command)


async def prepare_workspace(session, host, terminal):
    """Get the examples in the workspace and start the services on the host."""
    session.chapter("Get the examples")
    for command in setup_steps.get_examples(config.EXAMPLES_REPOSITORY,
                                            config.EXAMPLES_BRANCH):
        await terminal.run(command, {})
    session.chapter("Start RabbitMQ and InfluxDB services")
    for command in setup_steps.SERVICES:
        host.run(command)
    await browser.back_to_desktop(terminal.page)
    for command in setup_steps.SERVICES_CHECK:
        await terminal.run(command, {})


async def record_desktop(session, host, chosen):
    """Sign in, prepare the workspace and run the examples in its desktop."""
    async with async_playwright() as playwright:
        chromium, context = await browser.launch(playwright)
        page = await context.new_page()
        session.chapter("Sign in and open the workspace desktop")
        await browser.sign_in(page)
        desktop = await browser.open_desktop(context, page)
        terminal = VncTerminal(desktop, session.log)
        await terminal.open()
        await prepare_workspace(session, host, terminal)
        await run_with_retries(session, terminal, chosen)
        session.chapter("Done")
        await terminal.run("# All workspace examples finished", {})
        await desktop.wait_for_timeout(5000)
        await chromium.close()


def post_process(session):
    """Cut the recording into one video per chapter and make the web videos and GIFs."""
    here = os.path.dirname(os.path.abspath(__file__))
    session.log("splitting the recording into one video per example")
    subprocess.run([sys.executable, "split.py", f"{session.out}/{config.VIDEO}.mp4"],
                   cwd=here, check=False)
    session.log("speeding up the videos for the web and making GIFs")
    subprocess.run([sys.executable, "postprocess.py", "--dir", session.out],
                   cwd=here, check=False)


def parse_args():
    """The command line: --skip-install and the examples to record."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-install", action="store_true",
                        help="use the running installation instead of recording one")
    parser.add_argument("examples", nargs="*", help="example directories; all by default")
    args = parser.parse_args()
    chosen = [e for e in examples.EXAMPLES if not args.examples or e[0] in args.examples]
    return args.skip_install, chosen


async def main():
    """Record the session, then write the chapters, the report and the videos."""
    skip_install, chosen = parse_args()
    os.environ["DISPLAY"] = config.DISPLAY
    os.makedirs(config.OUT, exist_ok=True)
    session, recorder = Session(), Recorder()
    recorder.start()
    session.restart_clock()
    session.log(f"recording to {recorder.video}")
    host = HostTerminal()
    show_installation(session, host, skip_install)
    await record_desktop(session, host, chosen)
    recorder.stop()
    recorder.finish(session.chapters, session.elapsed())
    session.write_report()
    post_process(session)
    session.log("finished")


if __name__ == "__main__":
    asyncio.run(main())
