"""
Interface for BRL-CAD geometry databases (.g files).
"""
import _brlcad

class Database:
    """
    Represents a BRL-CAD geometry database.
    """
    def __init__(self, filename, mode="w"):
        self.filename = filename
        self._db_capsule = _brlcad.db_open(filename, mode)
        
    def create_sphere(self, name, radius):
        _brlcad.create_sphere(self._db_capsule, name, [0.0, 0.0, 0.0], float(radius))
        return name

    def create_box(self, name, x, y, z):
        _brlcad.create_box(self._db_capsule, name, float(x), float(y), float(z))
        return name

    def create_cylinder(self, name, r, h):
        _brlcad.create_cylinder(self._db_capsule, name, float(r), float(h))
        return name

    def create_tgc(self, name, base, height, a, b, c, d):
        _brlcad.create_tgc(
            self._db_capsule,
            name,
            list(base),
            list(height),
            list(a),
            list(b),
            list(c),
            list(d),
        )
        return name

    def create_ell(self, name, center, a, b, c):
        _brlcad.create_ell(
            self._db_capsule,
            name,
            list(center),
            list(a),
            list(b),
            list(c),
        )
        return name

    def set_color(self, name, r, g, b):
        _brlcad.set_color(self._db_capsule, name, int(r), int(g), int(b))

    def get_color(self, name):
        try:
            color = _brlcad.get_color(self._db_capsule, name)
            if color == (0, 0, 0) or color == [0, 0, 0] or color is None:
                return None
            return tuple(color)
        except:
            return None

    def set_shader(self, name, shader):
        _brlcad.set_shader(self._db_capsule, name, shader)

    def get_shader(self, name):
        try:
            shader = _brlcad.get_shader(self._db_capsule, name)
            if not shader or shader == "":
                return None
            return shader
        except:
            return None

    def list_objects(self):
        """
        Returns a list of names of all objects in the database.
        """
        objs = _brlcad.list_objects(self._db_capsule)
        return [obj['name'] for obj in objs]

    def close(self):
        if hasattr(self, '_db_capsule') and self._db_capsule:
            _brlcad.db_close(self._db_capsule)
            self._db_capsule = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
