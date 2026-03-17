"""
Interface for BRL-CAD geometry databases (.g files).
"""
import _brlcad

class Database:
    """
    Represents a BRL-CAD geometry database.
    
    This class provides a high-level Pythonic interface for opening and managing
    BRL-CAD .g files. Native pointers (struct rt_wdb/db_i) are stored safely 
    internally using PyCapsule, ensuring they are hidden from users.
    """
    def __init__(self, filename, mode="w"):
        """
        Opens a BRL-CAD .g geometry database and stores the native handle in a PyCapsule.
        """
        self.filename = filename
        self._db_capsule = _brlcad.db_open(filename, mode)
        
    def create_sphere(self, name, radius):
        """
        Creates a sphere primitive in the database.
        """
        from .primitives import Sphere
        _brlcad.create_sphere(self._db_capsule, name, float(radius))
        s = Sphere(name, radius=radius)
        s._db_capsule = self._db_capsule # Store reference for attribute management
        return s

    def list_objects(self):
        """
        Returns a list of all objects in the database as dictionaries.
        """
        return _brlcad.list_objects(self._db_capsule)

    def get_sphere(self, name):
        """
        Reads a sphere primitive from the database and returns a Sphere object.
        """
        data = _brlcad.get_sphere(self._db_capsule, name)
        from .primitives import Sphere
        s = Sphere(name, radius=data['radius'], center=data['center'])
        s._db_capsule = self._db_capsule
        return s

    def create_combination(self, name, members=None):
        """
        Creates a new combination geometry and writes it to the database.
        """
        from .combination import Combination
        comb_capsule = _brlcad.create_combination(name)
        comb = Combination(name, comb_capsule)
        comb._db_capsule = self._db_capsule # Store reference
        
        if members:
            for member in members:
                member_name = getattr(member, 'name', str(member))
                mat_capsule = getattr(member, '_mat_capsule', None)
                
                # Update the native combination tree structure with matrix
                _brlcad.comb_add_member(comb_capsule, self._db_capsule, member_name, mat_capsule)
                comb._members.append(member)
        
        # Finally write the combination to the database file
        _brlcad.write_combination(self._db_capsule, name, comb_capsule)
        return comb

    def close(self):
        """Close the database and free native resources."""
        if self._db_capsule:
            _brlcad.db_close(self._db_capsule)
            self._db_capsule = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
