"""
Base class for all BRL-CAD geometry primitives.
"""
import _brlcad
from abc import ABC, abstractmethod

class Transformable(ABC):
    """Base class for objects that can be transformed."""
    def __init__(self):
        self._mat_capsule = _brlcad.create_mat()

    def translate(self, x, y, z):
        _brlcad.mat_translate(self._mat_capsule, float(x), float(y), float(z))
        return self

    def rotate_x(self, angle_deg):
        _brlcad.mat_rotate_x(self._mat_capsule, float(angle_deg))
        return self

    def rotate_y(self, angle_deg):
        _brlcad.mat_rotate_y(self._mat_capsule, float(angle_deg))
        return self

    def rotate_z(self, angle_deg):
        _brlcad.mat_rotate_z(self._mat_capsule, float(angle_deg))
        return self

    def scale(self, factor):
        _brlcad.mat_scale(self._mat_capsule, float(factor))
        return self

class Primitive(Transformable):
    """
    Base class representing a primitive geometry object (e.g., sphere, box).
    
    Provides standard interface for adding the primitive to a database.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._db_capsule = None # Must be set by database after creation / read

    def set_region(self, flag: bool):
        if not self._db_capsule: return self
        _brlcad.set_region_flag(self._db_capsule, self.name, int(flag))
        return self

    def is_region(self):
        if not self._db_capsule: return False
        return bool(_brlcad.get_region_flag(self._db_capsule, self.name))

    def set_region_id(self, region_id: int):
        if not self._db_capsule: return self
        _brlcad.set_region(self._db_capsule, self.name, int(region_id))
        return self

    def get_region(self) -> int:
        if not self._db_capsule: return None
        val = _brlcad.get_region(self._db_capsule, self.name)
        return None if val == 0 else val

    def set_shader(self, shader: str):
        if not self._db_capsule: return self
        _brlcad.set_shader(self._db_capsule, self.name, str(shader))
        return self

    def get_shader(self) -> str:
        if not self._db_capsule: return None
        val = _brlcad.get_shader(self._db_capsule, self.name)
        return None if val == "" else val

    def set_los(self, los: int):
        if not self._db_capsule: return self
        _brlcad.set_los(self._db_capsule, self.name, int(los))
        return self

    def get_los(self) -> int:
        if not self._db_capsule: return 0
        return _brlcad.get_los(self._db_capsule, self.name)

    def set_material_id(self, mat_id: int):
        if not self._db_capsule: return self
        _brlcad.set_material_id(self._db_capsule, self.name, int(mat_id))
        return self

    def get_material_id(self) -> int:
        if not self._db_capsule: return 0
        return _brlcad.get_material_id(self._db_capsule, self.name)

    def set_color(self, r: int, g: int, b: int):
        if not self._db_capsule: return self
        _brlcad.set_color(self._db_capsule, self.name, r, g, b)
        return self

    def get_color(self):
        if not self._db_capsule: return None
        val = _brlcad.get_color(self._db_capsule, self.name)
        return None if val == (0, 0, 0) else val

    def get_region_raw(self) -> int:
        if not self._db_capsule: return 0
        return _brlcad.get_region(self._db_capsule, self.name)

    def get_shader_raw(self) -> str:
        if not self._db_capsule: return ""
        return _brlcad.get_shader(self._db_capsule, self.name)

    @abstractmethod
    def create(self, database):
        """Implement primitive-specific creation using C extension wrappers."""
        pass
