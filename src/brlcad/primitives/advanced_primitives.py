from .primitive import Primitive, Transformable
import _brlcad

class TGC(Primitive, Transformable):
    """
    Truncated General Cone (TGC).
    Defined by a base point, height vector, and two sets of orthogonal 
    vectors (A, B and C, D) for the base and top circles/ellipses.
    """
    def __init__(self, name, base, height, a, b, c, d):
        super().__init__(name)
        self.base = list(base)
        self.height = list(height)
        self.a = list(a)
        self.b = list(b)
        self.c = list(c)
        self.d = list(d)

    def create(self, database):
        _brlcad.create_tgc(
            database._db_capsule, 
            self.name, 
            self.base, 
            self.height, 
            self.a, 
            self.b, 
            self.c, 
            self.d
        )

class ELL(Primitive, Transformable):
    """
    Ellipsoid (ELL).
    Defined by a center point and three orthogonal vectors (A, B, C).
    """
    def __init__(self, name, center, a, b, c):
        super().__init__(name)
        self.center = list(center)
        self.a = list(a)
        self.b = list(b)
        self.c = list(c)

    def create(self, database):
        _brlcad.create_ell(
            database._db_capsule, 
            self.name, 
            self.center, 
            self.a, 
            self.b, 
            self.c
        )
