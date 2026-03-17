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
