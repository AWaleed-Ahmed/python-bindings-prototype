import copy

class Shape:
    """Base class for all geometric shapes."""
    def __init__(self):
        self.transforms = []
        # Default policy: export transforms as member matrices on combinations.
        self.transform_target = "combination_matrix"
        self.color_value = (255, 255, 255)
        self.shader_name = "default"
        self.name = None # For tracking existing DB objects

    def translate(self, x, y, z):
        new_shape = copy.deepcopy(self)
        new_shape.transforms.append(('translate', (float(x), float(y), float(z))))
        return new_shape

    def rotate(self, x, y, z):
        new_shape = copy.deepcopy(self)
        new_shape.transforms.append(('rotate', (float(x), float(y), float(z))))
        return new_shape

    def scale(self, sx, sy, sz):
        new_shape = copy.deepcopy(self)
        new_shape.transforms.append(('scale', (float(sx), float(sy), float(sz))))
        return new_shape

    def primitive_transforms(self):
        """
        Advanced/explicit mode: request primitive-local transform materialization.

        In the current exporter this is represented by wrapping the primitive
        with a dedicated transformed combination node.
        """
        new_shape = copy.deepcopy(self)
        new_shape.transform_target = "primitive_explicit"
        return new_shape

    def combination_transforms(self):
        """Use combination member matrices (default transform behavior)."""
        new_shape = copy.deepcopy(self)
        new_shape.transform_target = "combination_matrix"
        return new_shape

    def color(self, r, g, b):
        new_shape = copy.deepcopy(self)
        new_shape.color_value = (int(r), int(g), int(b))
        return new_shape

    def shader(self, name):
        new_shape = copy.deepcopy(self)
        new_shape.shader_name = name
        return new_shape

    # Non-copying setters for dynamic manipulation
    def set_color(self, r, g, b):
        self.color_value = (int(r), int(g), int(b))
        return self

    def set_shader(self, name):
        self.shader_name = name
        return self

    def __add__(self, other):
        return CSGNode('union', self, other)

    def __sub__(self, other):
        return CSGNode('subtract', self, other)

    def __and__(self, other):
        return CSGNode('intersect', self, other)

class Sphere(Shape):
    def __init__(self, radius):
        super().__init__()
        self.radius = float(radius)

class Box(Shape):
    def __init__(self, x, y, z):
        super().__init__()
        self.x, self.y, self.z = float(x), float(y), float(z)

class Cylinder(Shape):
    def __init__(self, r, h):
        super().__init__()
        self.r, self.h = float(r), float(h)

class ELL(Shape):
    def __init__(self, center, a, b, c):
        super().__init__()
        self.center = tuple(float(v) for v in center)
        self.a = tuple(float(v) for v in a)
        self.b = tuple(float(v) for v in b)
        self.c = tuple(float(v) for v in c)

class TGC(Shape):
    def __init__(self, base, height, a, b, c, d):
        super().__init__()
        self.base = tuple(float(v) for v in base)
        self.height = tuple(float(v) for v in height)
        self.a = tuple(float(v) for v in a)
        self.b = tuple(float(v) for v in b)
        self.c = tuple(float(v) for v in c)
        self.d = tuple(float(v) for v in d)

class CSGNode(Shape):
    def __init__(self, operation, left, right):
        super().__init__()
        self.operation = operation
        self.left = left
        self.right = right
