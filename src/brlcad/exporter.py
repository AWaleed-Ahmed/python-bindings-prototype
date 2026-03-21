import _brlcad
from .high_level_api import Shape, Sphere, Box, Cylinder, ELL, TGC, CSGNode
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
            'ell': 0,
            'tgc': 0,
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
                return self._export_node(node, new_db, as_member=False)
        return self._export_node(node, db, as_member=False)

    def _export_node(self, node, db, as_member=False) -> str:
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
            elif isinstance(node, ELL):
                name = self._get_unique_name('ell')
            elif isinstance(node, TGC):
                name = self._get_unique_name('tgc')
            else:
                name = "obj"
            node.name = name

        # Only create if it's not already in the DB (or if it's a node we need to rebuild)
        objs = db.list_objects()
        exists = name in objs

        if isinstance(node, CSGNode):
            left_name = self._export_node(node.left, db, as_member=True)
            right_name = self._export_node(node.right, db, as_member=True)
            op_map = {'union': 'u', 'subtract': '-', 'intersect': '+'}
            op = op_map.get(node.operation, 'u')

            geom_name = name
            needs_top_wrapper = bool(node.transforms) and self._use_combination_matrices(node) and not as_member
            if needs_top_wrapper:
                geom_name = f"{name}__geom"

            comb_capsule = _brlcad.create_combination(geom_name)
            _brlcad.comb_add_member(
                comb_capsule,
                db._db_capsule,
                left_name,
                'u',
                self._member_matrix(node.left),
            )
            _brlcad.comb_add_member(
                comb_capsule,
                db._db_capsule,
                right_name,
                op,
                self._member_matrix(node.right),
            )
            _brlcad.write_combination(db._db_capsule, geom_name, comb_capsule)

            if needs_top_wrapper:
                self._write_matrix_wrapper(name, geom_name, node, db)

        elif isinstance(node, Sphere):
            if self._requires_explicit_primitive_transform(node, as_member):
                self._write_transformed_primitive_wrapper(name, node, db)
            else:
                if not exists:
                    db.create_sphere(name, node.radius)

        elif isinstance(node, Box):
            if self._requires_explicit_primitive_transform(node, as_member):
                self._write_transformed_primitive_wrapper(name, node, db)
            else:
                if not exists:
                    db.create_box(name, node.x, node.y, node.z)

        elif isinstance(node, Cylinder):
            if self._requires_explicit_primitive_transform(node, as_member):
                self._write_transformed_primitive_wrapper(name, node, db)
            else:
                if not exists:
                    db.create_cylinder(name, node.r, node.h)

        elif isinstance(node, ELL):
            if self._requires_explicit_primitive_transform(node, as_member):
                self._write_transformed_primitive_wrapper(name, node, db)
            else:
                if not exists:
                    db.create_ell(name, node.center, node.a, node.b, node.c)

        elif isinstance(node, TGC):
            if self._requires_explicit_primitive_transform(node, as_member):
                self._write_transformed_primitive_wrapper(name, node, db)
            else:
                if not exists:
                    db.create_tgc(name, node.base, node.height, node.a, node.b, node.c, node.d)
        
        # Always apply attributes (effectively performs updates)
        self._apply_attributes(name, node, db)
        return name

    def _use_combination_matrices(self, node) -> bool:
        return getattr(node, "transform_target", "combination_matrix") != "primitive_explicit"

    def _requires_explicit_primitive_transform(self, node, as_member: bool) -> bool:
        if not bool(getattr(node, "transforms", [])):
            return False
        return (getattr(node, "transform_target", "combination_matrix") == "primitive_explicit") or (not as_member and self._use_combination_matrices(node))

    def _build_transform_matrix(self, transforms):
        if not transforms:
            return None

        mat_capsule = _brlcad.create_mat()
        for transform_name, values in transforms:
            if transform_name == 'translate':
                _brlcad.mat_translate(mat_capsule, *values)
            elif transform_name == 'rotate':
                # High-level API rotate(x, y, z) maps to Euler-like x/y/z rotations.
                _brlcad.mat_rotate_x(mat_capsule, values[0])
                _brlcad.mat_rotate_y(mat_capsule, values[1])
                _brlcad.mat_rotate_z(mat_capsule, values[2])
            elif transform_name == 'scale':
                _brlcad.mat_scale(mat_capsule, values[0])

        return mat_capsule

    def _member_matrix(self, member_node):
        transforms = getattr(member_node, "transforms", [])
        if not transforms:
            return None
        if not self._use_combination_matrices(member_node):
            return None
        return self._build_transform_matrix(transforms)

    def _write_matrix_wrapper(self, name, base_name, node, db):
        if base_name == name:
            base_name = self._ensure_top_level_base(name, node, db)

        wrapper_capsule = _brlcad.create_combination(name)
        _brlcad.comb_add_member(
            wrapper_capsule,
            db._db_capsule,
            base_name,
            'u',
            self._build_transform_matrix(getattr(node, "transforms", [])),
        )
        _brlcad.write_combination(db._db_capsule, name, wrapper_capsule)

    def _ensure_top_level_base(self, name, node, db):
        base_name = f"{name}__base"
        objs = db.list_objects()
        if base_name in objs:
            return base_name

        if isinstance(node, Sphere):
            db.create_sphere(base_name, node.radius)
        elif isinstance(node, Box):
            db.create_box(base_name, node.x, node.y, node.z)
        elif isinstance(node, Cylinder):
            db.create_cylinder(base_name, node.r, node.h)
        elif isinstance(node, ELL):
            db.create_ell(base_name, node.center, node.a, node.b, node.c)
        elif isinstance(node, TGC):
            db.create_tgc(base_name, node.base, node.height, node.a, node.b, node.c, node.d)
        else:
            return name
        return base_name

    def _write_transformed_primitive_wrapper(self, name, node, db):
        base_name = self._ensure_top_level_base(name, node, db)
        wrapper_capsule = _brlcad.create_combination(name)
        _brlcad.comb_add_member(
            wrapper_capsule,
            db._db_capsule,
            base_name,
            'u',
            self._build_transform_matrix(getattr(node, "transforms", [])),
        )
        _brlcad.write_combination(db._db_capsule, name, wrapper_capsule)

    def _convert_moose_node(self, moose_node):
        if isinstance(moose_node, Shape):
            return moose_node

        if hasattr(moose_node, "to_brlcad") and callable(moose_node.to_brlcad):
            converted = moose_node.to_brlcad()
            if not isinstance(converted, Shape):
                raise TypeError("moose_node.to_brlcad() must return a brlcad.high_level_api.Shape")
            return converted

        # Minimal duck-typed fallback for fast experimentation.
        if hasattr(moose_node, "operation") and hasattr(moose_node, "left") and hasattr(moose_node, "right"):
            left = self._convert_moose_node(moose_node.left)
            right = self._convert_moose_node(moose_node.right)
            converted = CSGNode(moose_node.operation, left, right)
        elif hasattr(moose_node, "radius"):
            converted = Sphere(moose_node.radius)
        elif hasattr(moose_node, "x") and hasattr(moose_node, "y") and hasattr(moose_node, "z"):
            converted = Box(moose_node.x, moose_node.y, moose_node.z)
        elif hasattr(moose_node, "r") and hasattr(moose_node, "h"):
            converted = Cylinder(moose_node.r, moose_node.h)
        elif (
            hasattr(moose_node, "center")
            and hasattr(moose_node, "a")
            and hasattr(moose_node, "b")
            and hasattr(moose_node, "c")
            and not hasattr(moose_node, "d")
        ):
            converted = ELL(moose_node.center, moose_node.a, moose_node.b, moose_node.c)
        elif (
            hasattr(moose_node, "base")
            and hasattr(moose_node, "height")
            and hasattr(moose_node, "a")
            and hasattr(moose_node, "b")
            and hasattr(moose_node, "c")
            and hasattr(moose_node, "d")
        ):
            converted = TGC(
                moose_node.base,
                moose_node.height,
                moose_node.a,
                moose_node.b,
                moose_node.c,
                moose_node.d,
            )
        else:
            raise TypeError(
                "Unsupported MOOSE node. Provide a to_brlcad() method that returns a Shape."
            )

        transforms = getattr(moose_node, "transforms", [])
        for transform_name, values in transforms:
            if transform_name == 'translate':
                converted = converted.translate(*values)
            elif transform_name == 'rotate':
                converted = converted.rotate(*values)
            elif transform_name == 'scale':
                converted = converted.scale(*values)

        transform_target = getattr(moose_node, "transform_target", None)
        if transform_target == "primitive_explicit":
            converted = converted.primitive_transforms()
        elif transform_target == "combination_matrix":
            converted = converted.combination_transforms()

        return converted

    def export_moose(self, moose_node, db=None) -> str:
        """
        Export a MOOSE-style node by converting it to the BRL-CAD high-level API.

        Contract for custom nodes: implement to_brlcad() -> Shape.
        """
        return self.export(self._convert_moose_node(moose_node), db=db)

    def _apply_attributes(self, name: str, node, db):
        # Apply color
        db.set_color(name, *node.color_value)
        # Apply shader
        if node.shader_name != "default":
            db.set_shader(name, node.shader_name)
