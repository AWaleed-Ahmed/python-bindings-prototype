"""
BRL-CAD primitives.
"""
from .sphere import Sphere

def _get_advanced_primitives():
    from .advanced_primitives import TGC, ELL
    return TGC, ELL

__all__ = ["Sphere"]
