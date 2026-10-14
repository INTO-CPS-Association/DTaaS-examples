"""Write a binding manifest with one temperature sensor per room.

The model declares rooms (IfcSpace) but no sensors, so the manifest proposes
one temperature sensor for each room. A room is not drawn in the geometry, so
the sensor is bound to an object that is: the wall or column inside the room's
footprint nearest to its centre, or any drawn object there when it has
neither. The match is made by geometry, so it works for a model that relates
no element to a room. The Building Models page of DTaaS reads the manifest beside
the model and draws each reading on the object it is bound to.

Usage:

    python lifecycle/make_manifest.py <model.ifc> <model.manifest.json>
"""

import argparse
import hashlib
import json
import logging
import multiprocessing
import sys
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element

CONVERTER = "fzk_haus.make_manifest 0.1.0"
TOPIC_PREFIX = "dtaas/examples/fzk-haus"
HISTORY_BUCKET = "dtaas"

# The comfort band of a living or working room, in degrees Celsius. The page
# uses it as the colour scale and raises an alert outside it.
RAMP = [18, 26]

# What the geometry converter leaves out, so nothing can be bound to it. Slabs
# and roofs are drawn but span many rooms, so their centre says nothing about
# which room they belong to.
NOT_DRAWN = ("IfcSpace", "IfcSite", "IfcOpeningElement")
NOT_IN_ONE_ROOM = ("IfcSlab", "IfcRoof", "IfcCovering")

# A room sensor is fixed to a wall at chest height, or to a column in an open
# plan. A desk or a chair is nearer to the centre, and a sensor is not mounted
# on one.
MOUNTABLE = ("IfcWall", "IfcWallStandardCase", "IfcColumn")

# How far outside a room's footprint the centre of an object may lie and still
# count, in metres. A wall bounding the room has its centre in the middle of
# its own thickness, just outside the room.
MARGIN = 0.4

log = logging.getLogger("make_manifest")


def sha256_of(path):
    """The SHA-256 of a file, read in pieces so a large model fits in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def elevation_of(space):
    """The elevation of the storey that holds a room, or 0 when it has none."""
    storey = ifcopenshell.util.element.get_container(space)
    return getattr(storey, "Elevation", None) or 0.0


def label_of(space):
    """A readable room name: its name, then its long name when it has one."""
    name = space.Name or "Room"
    if space.LongName:
        return f"{name}, {space.LongName}"
    return name


def ordered_rooms(model):
    """The rooms from the lowest storey up, then by name, so ids are stable."""
    rooms = model.by_type("IfcSpace")
    return sorted(rooms, key=lambda room: (elevation_of(room), label_of(room)))


def shapes(model, include=None, exclude=None):
    """Yield (GlobalId, lowest corner, highest corner) for each drawn object."""
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    iterator = ifcopenshell.geom.iterator(
        settings, model, multiprocessing.cpu_count(), include=include, exclude=exclude
    )
    if not iterator.initialize():
        return
    while True:
        shape = iterator.get()
        verts = shape.geometry.verts
        if verts:
            low = tuple(min(verts[axis::3]) for axis in range(3))
            high = tuple(max(verts[axis::3]) for axis in range(3))
            yield shape.guid, low, high
        if not iterator.next():
            break


def centre_of(low, high):
    """The centre of a box."""
    return tuple((low[axis] + high[axis]) / 2 for axis in range(3))


def inside(point, low, high):
    """Whether a point lies in a room's box, widened by MARGIN sideways."""
    across = all(low[axis] - MARGIN <= point[axis] <= high[axis] + MARGIN for axis in (0, 1))
    return across and low[2] - MARGIN <= point[2] <= high[2]


def host_of(room_box, objects, model, used):
    """The drawn object a room's sensor is bound to, or None.

    Among the objects whose centre lies in the room, a wall or column nearest
    to the room's centre wins, and any object is the fallback. An object no
    other room has taken comes first, because a wall between two rooms would
    otherwise carry both their sensors on the same spot.
    """
    low, high = room_box
    middle = centre_of(low, high)
    candidates = []
    for guid, centre in objects:
        if inside(centre, low, high):
            distance = sum((centre[axis] - middle[axis]) ** 2 for axis in range(3))
            mountable = model.by_guid(guid).is_a() in MOUNTABLE
            # Sorts free before taken, then mountable before not, then nearest.
            candidates.append((guid in used, not mountable, distance, guid))
    return min(candidates)[3] if candidates else None


def binding_for(room, host, number):
    """The binding of one proposed sensor in one room, fixed to its host."""
    room_id = f"room-{number:02d}"
    return {
        "selector": {"globalId": host},
        "label": f"{label_of(room)} temperature",
        "source": {
            "live": {
                "transport": "mqtt",
                "topic": f"{TOPIC_PREFIX}/{room_id}/temperature",
            },
            "history": {
                "bucket": HISTORY_BUCKET,
                "measurement": "temperature",
                "tags": {"room": room_id},
            },
        },
        "display": {"unit": "°C", "ramp": RAMP},
    }


def manifest_for(model_path):
    """The whole manifest for one model file."""
    model = ifcopenshell.open(str(model_path))
    boxes = {guid: (low, high) for guid, low, high in shapes(model, include=["IfcSpace"])}
    objects = [
        (guid, centre_of(low, high))
        for guid, low, high in shapes(model, exclude=list(NOT_DRAWN + NOT_IN_ONE_ROOM))
    ]
    bindings = []
    used = set()
    for room in ordered_rooms(model):
        host = None
        if room.GlobalId in boxes:
            host = host_of(boxes[room.GlobalId], objects, model, used)
        if host is None:
            log.warning("No drawn object in %s, so it gets no sensor", label_of(room))
            continue
        used.add(host)
        bindings.append(binding_for(room, host, len(bindings) + 1))
    return {
        "model": {
            "source": model_path.name,
            "source_sha256": sha256_of(model_path),
            "converter": CONVERTER,
            "schema": model.schema,
            "proposed": True,
            "basis": "One temperature sensor per IfcSpace, on the wall or column"
                     " in the room nearest to its centre that no other room has"
                     " taken, or on another drawn object in the room.",
        },
        "bindings": bindings,
    }


def main(argv=None):
    """Write the manifest for the model named on the command line."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", type=Path, help="the IFC model to read")
    parser.add_argument("manifest", type=Path, help="the manifest to write")
    args = parser.parse_args(argv)

    if not args.model.is_file():
        log.error("No model at %s", args.model)
        return 1
    manifest = manifest_for(args.model)
    if not manifest["bindings"]:
        log.error("%s declares no IfcSpace, so there is no room to bind", args.model.name)
        return 1
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    log.info("Wrote %d bindings to %s", len(manifest["bindings"]), args.manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
