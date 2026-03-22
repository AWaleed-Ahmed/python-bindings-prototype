"""MOOSE-first modeling API for BRL-CAD.

This module provides a lightweight object model that can be exported directly
without going through brlcad.high_level_api scene-graph classes.
"""


class MooseNode:
    """Base node for MOOSE-first modeling objects."""

    def __init__(self):
        self.name = None
        self.transforms = []
        self.color_value = (255, 255, 255)
        self.shader_name = "default"
        self.transform_target = "combination_matrix"

    def translate(self, x, y, z):
        self.transforms.append(("translate", (float(x), float(y), float(z))))
        return self

    def rotate(self, x, y, z):
        self.transforms.append(("rotate", (float(x), float(y), float(z))))
        return self

    def scale(self, s):
        self.transforms.append(("scale", (float(s),)))
        return self

    def color(self, r, g, b):
        self.color_value = (int(r), int(g), int(b))
        return self

    def shader(self, shader_name):
        self.shader_name = str(shader_name)
        return self

    def primitive_transforms(self):
        self.transform_target = "primitive_explicit"
        return self

    def combination_transforms(self):
        self.transform_target = "combination_matrix"
        return self

    def union(self, other):
        return MooseCSG("union", self, other)

    def subtract(self, other):
        return MooseCSG("subtract", self, other)

    def intersect(self, other):
        return MooseCSG("intersect", self, other)

    def __add__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return self.subtract(other)

    def __and__(self, other):
        return self.intersect(other)


class MooseSphere(MooseNode):
    def __init__(self, radius):
        super().__init__()
        self.radius = float(radius)


class MooseBox(MooseNode):
    def __init__(self, x, y, z):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


class MooseCylinder(MooseNode):
    def __init__(self, r, h):
        super().__init__()
        self.r = float(r)
        self.h = float(h)


class MooseELL(MooseNode):
    def __init__(self, center, a, b, c):
        super().__init__()
        self.center = list(center)
        self.a = list(a)
        self.b = list(b)
        self.c = list(c)


class MooseTGC(MooseNode):
    def __init__(self, base, height, a, b, c, d):
        super().__init__()
        self.base = list(base)
        self.height = list(height)
        self.a = list(a)
        self.b = list(b)
        self.c = list(c)
        self.d = list(d)


class MooseCSG(MooseNode):
    def __init__(self, operation, left, right):
        super().__init__()
        self.operation = operation
        self.left = left
        self.right = right


class Scene:
    """Container for MOOSE-first scenes."""

    def __init__(self, name="scene"):
        self.name = name
        self._roots = {}

    def add(self, name, node):
        node.name = name
        self._roots[name] = node
        return node

    def get(self, name):
        return self._roots[name]

    def export(self, filename, root_name=None):
        if not self._roots:
            raise ValueError("Scene has no roots to export")

        if root_name is None:
            root_name = next(iter(self._roots.keys()))

        node = self._roots[root_name]
        from .exporter import BRLCADExporter

        exporter = BRLCADExporter(filename)
        return exporter.export_moose(node)