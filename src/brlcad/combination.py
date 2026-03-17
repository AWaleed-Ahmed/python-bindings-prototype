import _brlcad
from .primitives.primitive import Transformable

class Combination(Transformable):
    """
    Pythonic interface to BRL-CAD combinations (assemblies/regions).
    
    A combination is a list of Boolean operations on primitives or other combinations.
    """
    def __init__(self, name, capsule):
        super().__init__()
        self.name = name
        self._capsule = capsule
        self._members = []
        self._db_capsule = None # Reference to database

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

    def get_region(self):
        if not self._db_capsule: return None
        val = _brlcad.get_region(self._db_capsule, self.name)
        return None if val == 0 else val

    def set_shader(self, shader: str):
        if not self._db_capsule: return self
        _brlcad.set_shader(self._db_capsule, self.name, str(shader))
        return self

    def get_shader(self):
        if not self._db_capsule: return None
        val = _brlcad.get_shader(self._db_capsule, self.name)
        return None if val == "" else val

    def set_los(self, los: int):
        if not self._db_capsule: return self
        _brlcad.set_los(self._db_capsule, self.name, int(los))
        return self

    def get_los(self):
        if not self._db_capsule: return 0
        return _brlcad.get_los(self._db_capsule, self.name)

    def set_material_id(self, mat_id: int):
        if not self._db_capsule: return self
        _brlcad.set_material_id(self._db_capsule, self.name, int(mat_id))
        return self

    def get_material_id(self):
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

    def get_region_raw(self):
        if not self._db_capsule: return 0
        return _brlcad.get_region(self._db_capsule, self.name)

    def get_shader_raw(self):
        if not self._db_capsule: return ""
        return _brlcad.get_shader(self._db_capsule, self.name)

    def add(self, member):
        """
        Adds a primitive or another combination to this combination.
        For now, defaults to Boolean UNION.
        """
        # Ensure we have the member name
        member_name = getattr(member, 'name', str(member))
        
        # Call internal C binding to update the native rt_comb_internal tree
        # We need the database capsule to resolve lookups if necessary in the future,
        # but for now we pass the pointer to the member name.
        # Note: In our current simple implementation, we rely on the member name existing in the .g file
        # when the combination is eventually written.
        
        # We'll handle the database context via the Database object that creates the combination.
        # This is a bit tricky since Combination doesn't have a direct link to Database yet.
        # We'll assume the Database object handles the binding.
        self._members.append(member)

    def __repr__(self):
        return f"Combination(name='{self.name}', members={len(self._members)})"
