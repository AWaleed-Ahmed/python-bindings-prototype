"""
Demo for experimental MOOSE-style integration via BRLCADExporter.export_moose().

This uses lightweight mock classes to emulate a MOOSE object model.
"""
from brlcad.database import Database
from brlcad.exporter import BRLCADExporter
from brlcad.high_level_api import Box, Cylinder, Sphere


class MooseSphere:
    def __init__(self, radius):
        self.radius = radius
        self.transforms = []
        self.transform_target = "combination_matrix"

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = Sphere(self.radius)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        if self.transform_target == "primitive_explicit":
            node = node.primitive_transforms()
        return node


class MooseCSG:
    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right


class MooseBox:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = Box(self.x, self.y, self.z)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        return node


class MooseCylinder:
    def __init__(self, r, h):
        self.r = r
        self.h = h
        self.transforms = []

    def translate(self, x, y, z):
        self.transforms.append(("translate", (x, y, z)))
        return self

    def to_brlcad(self):
        node = Cylinder(self.r, self.h)
        for tname, values in self.transforms:
            if tname == "translate":
                node = node.translate(*values)
        return node


def main():
    db_file = "moose_bridge_demo.g"
    exporter = BRLCADExporter(filename=db_file)

    s1 = MooseSphere(10).translate(25, 0, 0)
    s2 = MooseSphere(4).translate(-8, 0, 0)
    b1 = MooseBox(8, 5, 4).translate(0, 10, 0)
    c1 = MooseCylinder(2, 12).translate(0, 0, -6)

    # Default path: combination matrix transforms
    base_union = MooseCSG("union", s1, s2)

    # Advanced path: explicit primitive transform mode on one object
    s2.transform_target = "primitive_explicit"

    scene = MooseCSG("subtract", MooseCSG("union", base_union, b1), c1)

    with Database(db_file, "w") as db:
        name = exporter.export_moose(scene, db=db)
        print(f"Exported MOOSE-style scene as: {name}")
        print(f"Objects: {db.list_objects()}")


if __name__ == "__main__":
    main()
