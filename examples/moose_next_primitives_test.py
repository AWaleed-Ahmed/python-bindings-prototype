"""
Test 3 additional MOOSE-style primitives with export_moose:
- RCC (mapped to Cylinder in current adapter layer)
- ELL (native advanced primitive)
- TGC (native advanced primitive)
"""

from brlcad.database import Database
from brlcad.exporter import BRLCADExporter
from brlcad.high_level_api import Cylinder, ELL, TGC


class MooseRCC:
    """
    RCC compatibility wrapper for current adapter.
    BRL-CAD RCC support is approximated via create_cylinder(r, h) in this layer.
    """

    def __init__(self, radius, height):
        self.radius = float(radius)
        self.height = float(height)
        self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = Cylinder(self.radius, self.height)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        return node


class MooseELL:
    def __init__(self, center, a, b, c):
        self.center = center
        self.a = a
        self.b = b
        self.c = c
        self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = ELL(self.center, self.a, self.b, self.c)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        return node


class MooseTGC:
    def __init__(self, base, height, a, b, c, d):
        self.base = base
        self.height = height
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = TGC(self.base, self.height, self.a, self.b, self.c, self.d)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        return node


class MooseCSG:
    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right


def main():
    db_file = "moose_next_primitives.g"
    exporter = BRLCADExporter(db_file)

    rcc = MooseRCC(2.0, 16.0).translate(-18, 0, 0)
    ell = MooseELL(
        center=(0, 0, 0),
        a=(6, 0, 0),
        b=(0, 3, 0),
        c=(0, 0, 4),
    ).translate(12, 0, 0)
    tgc = MooseTGC(
        base=(0, 0, -4),
        height=(0, 0, 10),
        a=(3, 0, 0),
        b=(0, 3, 0),
        c=(1.5, 0, 0),
        d=(0, 1.5, 0),
    ).translate(0, 12, 0)

    # (RCC union ELL) subtract TGC
    scene = MooseCSG("subtract", MooseCSG("union", rcc, ell), tgc)

    with Database(db_file, "w") as db:
        root = exporter.export_moose(scene, db=db)
        objs = db.list_objects()

    print(f"Exported root: {root}")
    print(f"Objects: {objs}")


if __name__ == "__main__":
    main()
