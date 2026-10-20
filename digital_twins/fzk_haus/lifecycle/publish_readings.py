"""Publish simulated room temperatures on the topics the manifest lists.

The numbers are simulated. The topics and the payload format are the ones a
real sensor would use, and the type field says simulation, so a subscriber can
tell the two apart. Each payload is one line of comma-separated fields:

    timestamp,measurement,type,unit,value
    20261013T10:00:00,temperature,simulation,°C,21.40

The broker is read from the environment: MQTT_HOST (default localhost),
MQTT_PORT (default 1883), MQTT_USERNAME and MQTT_PASSWORD when the broker
asks for them, and MQTT_TLS=1 to connect over TLS.

Usage:

    python lifecycle/publish_readings.py <model.manifest.json>
    python lifecycle/publish_readings.py <model.manifest.json> --rounds 10
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

# The payload says these values come from a simulation, not an instrument.
KIND = "simulation"

log = logging.getLogger("publish_readings")

# Hosts where a password without TLS stays on this machine
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class Walker:  # pylint: disable=too-few-public-methods
    """A temperature that drifts slowly inside its range.

    A fresh random number every round looks like noise and hides whether the
    page is updating. A slow walk looks like a room and makes a frozen value
    easy to see.
    """

    def __init__(self, low, high, start):
        self.low = low
        self.high = high
        self.step = (high - low) * 0.03
        self.value = start

    def next(self):
        """Take one small step and return the new value."""
        self.value += random.uniform(-self.step, self.step)
        self.value = min(self.high, max(self.low, self.value))
        return self.value


def sensors_of(manifest_path):
    """The (topic, unit, walker) of every binding that has a live topic."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    live = [b for b in manifest.get("bindings", [])
            if b.get("source", {}).get("live", {}).get("topic")]
    sensors = []
    for index, binding in enumerate(live):
        low, high = (float(bound) for bound in binding["display"]["ramp"])
        sensors.append((binding["source"]["live"]["topic"], binding["display"]["unit"],
                        Walker(low, high, spread_start(low, high, index, len(live)))))
    return sensors


def spread_start(low, high, index, count):
    """Where room index starts, spread over the inner 80% of the range.

    Rooms that start apart take different colours on the Buildings page, so
    the heatmap shows which room is warm and which is cold from the first
    reading on.
    """
    share = (index + 0.5) / count
    return low + (high - low) * (0.1 + 0.8 * share)


def payload_of(unit, value, now):
    """One reading in the comma-separated format."""
    timestamp = now.strftime("%Y%m%dT%H:%M:%S")
    return f"{timestamp},temperature,{KIND},{unit},{value:.2f}"


def connect():
    """A client connected to the broker the environment names."""
    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if os.environ.get("MQTT_TLS") == "1":
        # The system certificate store verifies the broker.
        client.tls_set()
    username = os.environ.get("MQTT_USERNAME")
    if username:
        client.username_pw_set(username, os.environ.get("MQTT_PASSWORD"))
        if os.environ.get("MQTT_TLS") != "1" and host not in LOCAL_HOSTS:
            log.warning("The password goes to %s unencrypted. Set MQTT_TLS=1.", host)
    client.connect(host, port)
    client.loop_start()
    log.info("Connected to %s:%d", host, port)
    return client


def publish_round(client, sensors):
    """Publish one reading per sensor. A failed send is logged, not fatal."""
    now = datetime.now()
    failed = 0
    for topic, unit, walker in sensors:
        result = client.publish(topic, payload_of(unit, walker.next(), now))
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            failed += 1
    if failed:
        log.warning("%d of %d readings were not sent", failed, len(sensors))


def main(argv=None):
    """Publish until stopped, or for the number of rounds asked for."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path, help="the manifest to read")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="seconds between rounds (default 2)")
    parser.add_argument("--rounds", type=int, default=0,
                        help="rounds to publish, 0 means until stopped (default 0)")
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        log.error("No manifest at %s. Run lifecycle/create first.", args.manifest)
        return 1
    sensors = sensors_of(args.manifest)
    if not sensors:
        log.error("%s lists no live topic", args.manifest.name)
        return 1
    if not os.environ.get("MQTT_PORT", "1883").isdigit():
        log.error("MQTT_PORT must be a port number")
        return 1
    try:
        client = connect()
    except OSError as error:
        log.error("Could not reach the MQTT broker: %s", error)
        return 1

    log.info("Publishing %d sensors every %.1f s", len(sensors), args.interval)
    rounds = 0
    try:
        while args.rounds == 0 or rounds < args.rounds:
            publish_round(client, sensors)
            rounds += 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        log.info("Stopped after %d rounds", rounds)
    finally:
        client.loop_stop()
        client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
