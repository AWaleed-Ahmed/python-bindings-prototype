# pybrlcad

A prototype Python binding for the BRL-CAD CAD kernel.

## Architecture

- **Python package (`brlcad`)**: User-facing API.
- **Backend selector (`open_database`)**: Defaults to `moose_rt3`.
- **ctypes binding (`src/brlcad/moose_rt3_backend.py`)**: Loads C bridge ABI and marshals arguments.
- **C bridge (`src/moose_bridge/moose_c_api.*`)**: Thin C ABI over MOOSE C++ classes.
- **MOOSE C++ API**: Authoritative geometry/database behavior.
- **BRL-CAD database**: Persistent `.g` output for file-backed sessions.

Legacy `_brlcad` path remains in the repository for compatibility, but the current workflow is the MOOSE bridge path.

## Project Structure

- `src/brlcad/`: Python package.
- `src/moose_bridge/`: C bridge layer for MOOSE (`moose_c_api.h/.cpp`).
- `third_party/MOOSE/`: MOOSE source submodule.
- `build_moose_bridge.sh`: Build script for MOOSE and bridge library.
- `examples/`: Usage examples.
- `tests/`: Unit tests.

## Requirements

- Python 3.8+
- CMake and a C/C++ toolchain.
- Git submodule support (for `third_party/MOOSE`).
- Linux environment with system zlib available.

## Clone and Setup

This repository uses a Git submodule for MOOSE at `third_party/MOOSE`.

For a fresh clone:

```bash
git clone --recurse-submodules <repo-url>
cd prottest1
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

If the submodule is updated in the main repository later, sync and pull it with:

```bash
git submodule update --init --recursive --remote
```

Then build the bridge:

```bash
bash ./build_moose_bridge.sh
```

## Transform Policy

- Primary mechanism: combination-member matrices.
- Matrices are represented as 16-value arrays (conceptually 4x4, row-major).
- Primitive definitions remain canonical and reusable; placement is stored on members.

Example matrix helpers used in smoke tests:

```python
def _identity_matrix16():
	return [
		1.0, 0.0, 0.0, 0.0,
		0.0, 1.0, 0.0, 0.0,
		0.0, 0.0, 1.0, 0.0,
		0.0, 0.0, 0.0, 1.0,
	]


def _translate_matrix16(tx, ty, tz):
	m = _identity_matrix16()
	m[3] = float(tx)
	m[7] = float(ty)
	m[11] = float(tz)
	return m
```

## Current Backend Path (moose_rt3)

Open a database with the current bridge-backed workflow:

```python
from brlcad import BACKEND_MOOSE_RT3, open_database

with open_database("scene.g", mode="w", backend=BACKEND_MOOSE_RT3) as db:
	db.create_sphere("sph", 12.5)
	db.write_combination(
		"combo",
		[
			{"name": "sph", "op": "u", "matrix": _identity_matrix16()},
		],
	)
```

Session modes currently supported by the bridge:

- `r`: read-only file mode (rejects writes)
- `w`: writable file mode (persists to `.g`)
- `memory`: writable in-memory mode (non-persistent)

## Smoke Test

Run the end-to-end smoke test:

```bash
python examples/test_moose_rt3_smoke.py
```

It validates:

- primitive creation
- combination-member matrix writes
- persistence and reopen behavior
