"""Print the first readings that reach the broker on the topics of a manifest.

It shows that the publisher of lifecycle/execute is delivering, through the
same broker the Buildings page of DTaaS reads, and then stops. The broker
comes from the same environment variables as publish_readings.py.

Usage:
    python lifecycle/show_readings.py <manifest> [--count N] [--timeout S]
"""

import argparse
import json
import logging
import queue
import sys
from pathlib import Path

from publish_readings import connect

log = logging.getLogger("show_readings")


def topics_of(manifest_path):
    """The live topics of a manifest, with the label of each."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    topics = {}
    for binding in manifest.get("bindings", []):
        topic = binding.get("source", {}).get("live", {}).get("topic")
        if topic:
            topics[topic] = binding.get("label", topic)
    return topics


def line_of(label, payload):
    """One reading as a line a person reads: room, value with unit, time."""
    fields = payload.split(",")
    if len(fields) != 5:
        return f"{label}: {payload}"
    timestamp, _, _, unit, value = fields
    return f"{label}: {value} {unit} at {timestamp[-8:]}"


def collect(client, topics, count, timeout):
    """Subscribe and return up to count lines, or fewer after timeout seconds."""
    arrived = queue.Queue()
    client.on_message = lambda _c, _u, msg: arrived.put(
        line_of(topics.get(msg.topic, msg.topic), msg.payload.decode("utf-8", "replace")))
    client.subscribe([(topic, 0) for topic in topics])
    lines = []
    try:
        while len(lines) < count:
            lines.append(arrived.get(timeout=timeout))
    except queue.Empty:
        pass
    return lines


def main(argv=None):
    """Print the readings and return 0 when at least one arrived."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--count", type=int, default=7)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    if not args.manifest.is_file():
        log.error("No manifest at %s. Run lifecycle/create first.", args.manifest)
        return 1
    client = connect()
    lines = collect(client, topics_of(args.manifest), args.count, args.timeout)
    client.loop_stop()
    client.disconnect()
    for line in lines:
        print(line)
    if not lines:
        log.error("No reading arrived in %.0f s. Is lifecycle/execute running?", args.timeout)
    return 0 if lines else 1


if __name__ == "__main__":
    sys.exit(main())
