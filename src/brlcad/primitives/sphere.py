"""
Sphere geometry primitive.
"""
import _brlcad
from .primitive import Primitive

class Sphere(Primitive):
    """
    Represents a sphere in BRL-CAD (ET_SPH).
    
    API:
        Sphere(name="sphere.s", origin=(0, 0, 0), radius=10)
    """
    def __init__(self, name, origin=(0, 0, 0), radius=1.0, center=None):
        super().__init__(name)
        self.origin = origin if center is None else center
        self.radius = radius

    def create(self, database):
        """
        Creates the sphere in the provided Database instance.
        
        Calls the C extension's wdb_export_sphere wrapper safely.
        """
        _brlcad.create_sphere(database._db_capsule, self.name, self.origin, self.radius)
