from ._brlcad import create_tgc, create_ell
from .primitives.primitive import Transformable
class TGC(Transformable):
    def __init__(self, name, base, top, height):
        super().__init__()
        self._capsule = create_tgc(name, base, top, height)

class ELL(Transformable):
    def __init__(self, name, radii, center=None):
        super().__init__()
        self._capsule = create_ell(name, radii, center)