#!/usr/bin/env python3
"""Quick smoke test for the moose_rt3 backend path.

Usage:
  BRLCAD_MOOSE_BRIDGE_PATH=/abs/path/libbrlcad_moose_bridge.so \
  python examples/test_moose_rt3_smoke.py

Optional:
    BRLCAD_TEST_G_PATH=/tmp/moose_rt3_example.g
    BRLCAD_TEST_MODE=memory
"""

from __future__ import annotations

import os
from pathlib import Path

from brlcad import BACKEND_MOOSE_RT3, MooseBackendError, MooseBridgeUnavailableError, open_database


def _assert(cond: bool, message: str):
    if not cond:
        raise AssertionError(message)


def _try_step(label: str, fn):
    try:
        fn()
        print(f"[ok] {label}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[warn] {label} skipped: {exc}")


def _identity_matrix16():
    return [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def _translate_matrix16(tx: float, ty: float, tz: float):
    m = _identity_matrix16()
    m[3] = float(tx)
    m[7] = float(ty)
    m[11] = float(tz)
    return m


def _find_bridge_path() -> Path | None:
    env_path = os.environ.get("BRLCAD_MOOSE_BRIDGE_PATH")
    if env_path:
        p = Path(env_path)
        return p if p.exists() else None

    # Common local build output for this repository.
    repo_root = Path(__file__).resolve().parents[1]
    candidates = [
        repo_root / "build" / "moose_bridge" / "libbrlcad_moose_bridge.so",
        repo_root / "build" / "libbrlcad_moose_bridge.so",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def run_smoke_test() -> int:
    bridge = _find_bridge_path()
    if not bridge:
        print("[fail] Could not locate libbrlcad_moose_bridge.so")
        print("       Build it with: bash ./build_moose_bridge.sh")
        print("       Or set BRLCAD_MOOSE_BRIDGE_PATH explicitly.")
        return 1

    # Ensure ctypes loader sees the bridge path without requiring shell exports.
    os.environ["BRLCAD_MOOSE_BRIDGE_PATH"] = str(bridge)

    # Default is writable file output so test runs produce a real .g file.
    db_path = os.environ.get("BRLCAD_TEST_G_PATH", "moose_rt3_smoke.g")
    mode = os.environ.get("BRLCAD_TEST_MODE", "w").strip().lower()
    if mode not in {"w", "memory", "r"}:
        print(f"[warn] invalid BRLCAD_TEST_MODE={mode}, falling back to w")
        mode = "w"

    if mode != "w":
        print("[warn] this transform workflow requires writable file mode; forcing mode=w")
        mode = "w"

    print(f"[info] bridge={bridge}")
    print(f"[info] backend={BACKEND_MOOSE_RT3} mode={mode} db={db_path}")

    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()

    # Phase 1: create primitives and persist a new .g file.
    with open_database(db_path, mode="w", backend=BACKEND_MOOSE_RT3) as db:
        sphere_name = db.create_sphere("sph_smoke", 12.5)
        db.set_attribute(sphere_name, "color", "255/0/0")

        vertices = [
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (0.0, 10.0, 0.0),
            (0.0, 0.0, 10.0),
        ]
        faces = [
            (0, 1, 2),
            (0, 1, 3),
            (1, 2, 3),
            (2, 0, 3),
        ]
        bot_name = db.create_bot("bot_smoke", vertices, faces)

        sphere_obj = db.get_object(sphere_name)
        sphere_color = db.get_attribute(sphere_name, "color")
        _assert(sphere_obj.get("name") == sphere_name, "sphere name mismatch")
        _assert(sphere_obj.get("type") == "Sphere", "sphere type mismatch")
        _assert(sphere_color == "255/0/0", "sphere color attribute mismatch")
        print(f"[ok] phase1 wrote primitives: {sphere_name}, {bot_name}")

    _assert(db_file.exists(), f"expected .g file to exist after phase1: {db_file}")
    print(f"[ok] phase1 file created: {db_file}")

    # Phase 2: reopen same .g and add combination member transforms.
    with open_database(db_path, mode="w", backend=BACKEND_MOOSE_RT3) as db:
        members = [
            {
                "name": "sph_smoke",
                "op": "u",
                "matrix": _identity_matrix16(),
            },
            {
                "name": "bot_smoke",
                "op": "u",
                "matrix": _translate_matrix16(25.0, 0.0, 0.0),
            },
        ]
        comb_name = db.write_combination("combo_transformed", members)
        comb_obj = db.get_object(comb_name)
        _assert(comb_obj.get("name") == comb_name, "combination name mismatch")
        _assert(comb_obj.get("type") == "Combination", "combination type mismatch")
        print(f"[ok] phase2 updated file with transformed combination: {comb_obj}")

    # Phase 3: reopen read-only and verify updated object exists.
    with open_database(db_path, mode="r", backend=BACKEND_MOOSE_RT3) as db:
        comb_obj = db.get_object("combo_transformed")
        _assert(comb_obj.get("type") == "Combination", "updated combination missing in final read")
        print(f"[ok] phase3 verified persisted update: {comb_obj}")

    print("[pass] moose_rt3 smoke test completed")
    return 0


def main() -> int:
    try:
        return run_smoke_test()
    except MooseBridgeUnavailableError as exc:
        print(f"[fail] bridge unavailable: {exc}")
        return 1
    except MooseBackendError as exc:
        print(f"[fail] backend error: {exc}")
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[fail] unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
