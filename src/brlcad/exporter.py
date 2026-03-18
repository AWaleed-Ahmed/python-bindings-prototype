import _brlcad
from .high_level_api import Shape, Sphere, Box, Cylinder, CSGNode
from .database import Database

class BRLCADExporter:
    """
    Translates high-level Python geometry into BRL-CAD objects.
    Supports attribute updates for existing objects if 'name' is specified.
    """
    def __init__(self, filename=None):
        self._counts = {
            'sph': 0,
            'box': 0,
            'cyl': 0,
            'comb': 0
        }
        self.filename = filename

    def _get_unique_name(self, prefix: str) -> str:
        self._counts[prefix] += 1
        return f"{prefix}_{self._counts[prefix]}"

    def export(self, node, db=None) -> str:
        if db is None:
            if self.filename is None:
                raise ValueError("Database or filename must be provided.")
            with Database(self.filename) as new_db:
                return self._export_node(node, new_db)
        return self._export_node(node, db)

    def _export_node(self, node, db) -> str:
        # Check if we are updating an existing object or creating a new one
        if node.name:
            name = node.name
        else:
            if isinstance(node, CSGNode):
                name = self._get_unique_name('comb')
            elif isinstance(node, Sphere):
                name = self._get_unique_name('sph')
            elif isinstance(node, Box):
                name = self._get_unique_name('box')
            elif isinstance(node, Cylinder):
                name = self._get_unique_name('cyl')
            else:
                name = "obj"
            node.name = name

        # Only create if it's not already in the DB (or if it's a node we need to rebuild)
        objs = db.list_objects()
        exists = name in objs

        if isinstance(node, CSGNode):
            left_name = self._export_node(node.left, db)
            right_name = self._export_node(node.right, db)
            op_map = {'union': 'u', 'subtract': '-', 'intersect': '+'}
            op = op_map.get(node.operation, 'u')

            comb_capsule = _brlcad.create_combination(name)
            _brlcad.comb_add_member(comb_capsule, db._db_capsule, left_name, 'u', None)
            _brlcad.comb_add_member(comb_capsule, db._db_capsule, right_name, op, None)
            _brlcad.write_combination(db._db_capsule, name, comb_capsule)

        elif isinstance(node, Sphere):
            if not exists:
                db.create_sphere(name, node.radius)
        elif isinstance(node, Box):
            if not exists:
                db.create_box(name, node.x, node.y, node.z)
        elif isinstance(node, Cylinder):
            if not exists:
                db.create_cylinder(name, node.r, node.h)
        
        # Always apply attributes (effectively performs updates)
        self._apply_attributes(name, node, db)
        return name

    def _apply_attributes(self, name: str, node, db):
        # Apply color
        db.set_color(name, *node.color_value)
        # Apply shader
        if node.shader_name != "default":
            db.set_shader(name, node.shader_name)
