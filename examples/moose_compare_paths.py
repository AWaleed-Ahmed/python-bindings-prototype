"""
Compare implementation paths:
1) Direct high-level adapter path (Shape/CSG objects)
2) MOOSE-style path via exporter.export_moose(...)

This script exports equivalent scenes through both paths and prints
object layout + MGED listing snippets for quick comparison.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from brlcad.database import Database
from brlcad.exporter import BRLCADExporter
from brlcad.high_level_api import Box, Cylinder, Sphere


@dataclass
class MooseSphere:
    radius: float
    transforms: list | None = None
    transform_target: str = "combination_matrix"

    def __post_init__(self):
        if self.transforms is None:
            self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def rotate(self, x, y, z):
        self.transforms.append(("rotate", (x, y, z)))
        return self

    def scale(self, sx, sy, sz):
        self.transforms.append(("scale", (sx, sy, sz)))
        return self


@dataclass
class MooseBox:
    x: float
    y: float
    z: float
    transforms: list | None = None
    transform_target: str = "combination_matrix"

    def __post_init__(self):
        if self.transforms is None:
            self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def rotate(self, x, y, z):
        self.transforms.append(("rotate", (x, y, z)))
        return self


@dataclass
class MooseCylinder:
    r: float
    h: float
    transforms: list | None = None
    transform_target: str = "combination_matrix"

    def __post_init__(self):
        if self.transforms is None:
            self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self


@dataclass
class MooseCSG:
    operation: str
    left: object
    right: object


def build_direct_scene():
    s = Sphere(8).translate(20, 0, 0)
    b = Box(10, 8, 6).translate(-5, 0, 0).rotate(0, 0, 20)
    c = Cylinder(3, 20).translate(0, 0, -5)

    return (s + b) - c


def build_moose_scene():
    s = MooseSphere(8).translate(20, 0, 0)
    b = MooseBox(10, 8, 6).translate(-5, 0, 0).rotate(0, 0, 20)
    c = MooseCylinder(3, 20).translate(0, 0, -5)

    return MooseCSG("subtract", MooseCSG("union", s, b), c)


def mged_list(db_file: str, obj_name: str) -> str:
    proc = subprocess.run(
        ["mged", "-c", db_file, "l", obj_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return f"[mged list failed for {obj_name}]\n{proc.stderr.strip()}"
    output = proc.stdout.strip()
    if not output:
        output = proc.stderr.strip()
    return output


def export_direct(db_file: str):
    if os.path.exists(db_file):
        os.remove(db_file)

    exporter = BRLCADExporter(db_file)
    with Database(db_file, "w") as db:
        name = exporter.export(build_direct_scene(), db=db)
        objects = db.list_objects()

    return name, objects


def export_moose(db_file: str):
    if os.path.exists(db_file):
        os.remove(db_file)

    exporter = BRLCADExporter(db_file)
    with Database(db_file, "w") as db:
        name = exporter.export_moose(build_moose_scene(), db=db)
        objects = db.list_objects()

    return name, objects


def main():
    direct_db = "compare_direct.g"
    moose_db = "compare_moose.g"

    direct_name, direct_objects = export_direct(direct_db)
    moose_name, moose_objects = export_moose(moose_db)

    print("=== Implementation Effort View ===")
    print("Direct adapter path: no extra object model needed.")
    print("MOOSE path: requires conversion contract (to_brlcad or duck-typed fields).")
    print()

    print("=== Exported Object Inventory ===")
    print(f"Direct root: {direct_name}")
    print(f"Direct objects: {direct_objects}")
    print(f"MOOSE root: {moose_name}")
    print(f"MOOSE objects: {moose_objects}")
    print()

    print("=== MGED Root Listing ===")
    print("[Direct]")
    print(mged_list(direct_db, direct_name))
    print()
    print("[MOOSE]")
    print(mged_list(moose_db, moose_name))


if __name__ == "__main__":
    main()
