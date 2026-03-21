# pybrlcad

A prototype Python binding for the BRL-CAD CAD kernel.

## Architecture

- **Python API**: High-level, Pythonic interface.
- **CPython C Extension (`_brlcad`)**: Bridge between Python and C.
- **PyCapsule**: Manages native pointers (librt, libwdb) safely.
- **Adapter Layer**: Thin C layer to simplify interaction with BRL-CAD libraries.
- **BRL-CAD Libraries**: The underlying CAD kernel (librt, libwdb, etc.).

## Project Structure

- `src/brlcad/`: Python package.
- `src/_brlcad/`: C extension source.
- `src/adapter/`: C adapter layer.
- `examples/`: Usage examples.
- `tests/`: Unit tests.

## Requirements

- Python 3.8+
- BRL-CAD installed with development headers.

## Transform Policy

- Primary transform mechanism: combination matrices.
- Primitive transforms: supported as advanced/explicit operations.

In the high-level API, transforms are recorded on shapes and exported by default
as combination member matrices.

Use explicit primitive mode only when you want isolated transformed primitive
wrappers:

```python
from brlcad.high_level_api import Sphere

s_default = Sphere(10).translate(10, 0, 0)  # combination matrix path (default)
s_explicit = Sphere(10).translate(10, 0, 0).primitive_transforms()  # advanced mode
```

## MOOSE Bridge (Experimental)

`BRLCADExporter` now includes `export_moose(...)`.

Supported integration patterns:

- Preferred: pass objects implementing `to_brlcad()` returning a
	`brlcad.high_level_api.Shape`.
- Fallback: duck-typed nodes with attributes like `radius`, `(x, y, z)`,
	`(r, h)`, or CSG-style `operation/left/right`.

See `examples/moose_bridge_demo.py` for a quick test flow.
