"""
Optional BRL-CAD/MOOSE (rt^3-style C++ API) backend integration.

This module intentionally does not replace the existing _brlcad pipeline.
It provides a separate backend workflow that can be enabled when a C bridge
library is present.
"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import c_char_p, c_double, c_int, c_size_t, c_void_p, POINTER, byref, create_string_buffer


class MooseBackendError(RuntimeError):
    pass


class MooseBridgeUnavailableError(MooseBackendError):
    pass


class _MooseBridge:
    def __init__(self, lib_path: str | None = None):
        self.lib_path = lib_path or os.environ.get("BRLCAD_MOOSE_BRIDGE_PATH", "libbrlcad_moose_bridge.so")
        try:
            self.lib = ctypes.CDLL(self.lib_path)
        except OSError as exc:
            raise MooseBridgeUnavailableError(
                f"Could not load MOOSE bridge library '{self.lib_path}'. "
                "Build and provide a C bridge over BRL-CAD/MOOSE first."
            ) from exc

        self._bind()

    def _bind(self):
        self.lib.moose_db_open.argtypes = [c_char_p, c_char_p, POINTER(c_void_p)]
        self.lib.moose_db_open.restype = c_int

        self.lib.moose_db_close.argtypes = [c_void_p]
        self.lib.moose_db_close.restype = c_int

        self.lib.moose_db_create_sphere.argtypes = [c_void_p, c_char_p, POINTER(c_double), c_double]
        self.lib.moose_db_create_sphere.restype = c_int

        self.lib.moose_db_create_arb8.argtypes = [c_void_p, c_char_p, POINTER(c_double)]
        self.lib.moose_db_create_arb8.restype = c_int

        self.lib.moose_db_create_bot.argtypes = [c_void_p, c_char_p, POINTER(c_double), c_size_t, POINTER(c_int), c_size_t]
        self.lib.moose_db_create_bot.restype = c_int

        self.lib.moose_comb_create.argtypes = [c_char_p, POINTER(c_void_p)]
        self.lib.moose_comb_create.restype = c_int

        self.lib.moose_comb_add_member.argtypes = [c_void_p, c_char_p, ctypes.c_char, POINTER(c_double)]
        self.lib.moose_comb_add_member.restype = c_int

        self.lib.moose_comb_write.argtypes = [c_void_p, c_char_p, c_void_p]
        self.lib.moose_comb_write.restype = c_int

        self.lib.moose_comb_free.argtypes = [c_void_p]
        self.lib.moose_comb_free.restype = c_int

        self.lib.moose_db_get_object_json.argtypes = [c_void_p, c_char_p, c_char_p, c_size_t]
        self.lib.moose_db_get_object_json.restype = c_int

        self.lib.moose_db_set_attribute.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        self.lib.moose_db_set_attribute.restype = c_int

        self.lib.moose_db_get_attribute.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_size_t]
        self.lib.moose_db_get_attribute.restype = c_int

        self.lib.moose_last_error.argtypes = []
        self.lib.moose_last_error.restype = c_char_p

    def _check(self, rc: int, action: str):
        if rc == 0:
            return
        raw = self.lib.moose_last_error()
        detail = raw.decode("utf-8") if raw else "unknown error"
        raise MooseBackendError(f"{action} failed: {detail} (status={rc})")

    def db_open(self, filename: str, mode: str) -> c_void_p:
        out = c_void_p()
        rc = self.lib.moose_db_open(filename.encode("utf-8"), mode.encode("utf-8"), byref(out))
        self._check(rc, "moose_db_open")
        return out

    def db_close(self, handle: c_void_p):
        if not handle:
            return
        rc = self.lib.moose_db_close(handle)
        self._check(rc, "moose_db_close")

    def create_sphere(self, handle: c_void_p, name: str, radius: float):
        center = (c_double * 3)(0.0, 0.0, 0.0)
        rc = self.lib.moose_db_create_sphere(handle, name.encode("utf-8"), center, c_double(radius))
        self._check(rc, "moose_db_create_sphere")

    def create_arb8(self, handle: c_void_p, name: str, points):
        if len(points) != 8:
            raise ValueError("arb8 requires exactly 8 points")
        flat = []
        for p in points:
            if len(p) != 3:
                raise ValueError("each arb8 point must have 3 coordinates")
            flat.extend([float(p[0]), float(p[1]), float(p[2])])
        arr = (c_double * 24)(*flat)
        rc = self.lib.moose_db_create_arb8(handle, name.encode("utf-8"), arr)
        self._check(rc, "moose_db_create_arb8")

    def create_bot(self, handle: c_void_p, name: str, vertices, faces):
        if not vertices or not faces:
            raise ValueError("bot requires non-empty vertices and faces")
        vflat = []
        for v in vertices:
            if len(v) != 3:
                raise ValueError("each vertex must have 3 coordinates")
            vflat.extend([float(v[0]), float(v[1]), float(v[2])])
        fflat = []
        for f in faces:
            if len(f) != 3:
                raise ValueError("each face must have 3 vertex indices")
            fflat.extend([int(f[0]), int(f[1]), int(f[2])])

        varr = (c_double * len(vflat))(*vflat)
        farr = (c_int * len(fflat))(*fflat)
        rc = self.lib.moose_db_create_bot(
            handle,
            name.encode("utf-8"),
            varr,
            c_size_t(len(vertices)),
            farr,
            c_size_t(len(faces)),
        )
        self._check(rc, "moose_db_create_bot")

    def write_combination(self, handle: c_void_p, name: str, members):
        if not members:
            raise ValueError("combination requires at least one member")

        comb = c_void_p()
        rc = self.lib.moose_comb_create(name.encode("utf-8"), byref(comb))
        self._check(rc, "moose_comb_create")

        try:
            for member in members:
                member_name = str(member["name"])
                op = str(member.get("op", "u"))
                if len(op) != 1:
                    raise ValueError("comb member op must be one character")

                matrix = member.get("matrix")
                matrix_arr = None
                if matrix is not None:
                    if len(matrix) != 16:
                        raise ValueError("comb member matrix must have 16 values")
                    matrix_arr = (c_double * 16)(*[float(v) for v in matrix])

                rc = self.lib.moose_comb_add_member(
                    comb,
                    member_name.encode("utf-8"),
                    op.encode("utf-8"),
                    matrix_arr,
                )
                self._check(rc, "moose_comb_add_member")

            rc = self.lib.moose_comb_write(handle, name.encode("utf-8"), comb)
            self._check(rc, "moose_comb_write")
        finally:
            self.lib.moose_comb_free(comb)

    def get_object(self, handle: c_void_p, name: str):
        buf = create_string_buffer(64 * 1024)
        rc = self.lib.moose_db_get_object_json(handle, name.encode("utf-8"), buf, c_size_t(len(buf)))
        self._check(rc, "moose_db_get_object_json")
        return json.loads(buf.value.decode("utf-8"))

    def set_attribute(self, handle: c_void_p, object_name: str, key: str, value: str):
        rc = self.lib.moose_db_set_attribute(
            handle,
            object_name.encode("utf-8"),
            key.encode("utf-8"),
            value.encode("utf-8"),
        )
        self._check(rc, "moose_db_set_attribute")

    def get_attribute(self, handle: c_void_p, object_name: str, key: str):
        buf = create_string_buffer(8 * 1024)
        rc = self.lib.moose_db_get_attribute(
            handle,
            object_name.encode("utf-8"),
            key.encode("utf-8"),
            buf,
            c_size_t(len(buf)),
        )
        self._check(rc, "moose_db_get_attribute")
        return buf.value.decode("utf-8")


class MooseRt3Database:
    """
    Separate database workflow backed by BRL-CAD/MOOSE through a C bridge.

    This is intentionally parallel to the existing Database class to avoid
    destabilizing the current _brlcad-based path.
    """

    def __init__(self, filename: str, mode: str = "w", bridge_path: str | None = None):
        self.filename = filename
        self.mode = mode
        self._bridge = _MooseBridge(bridge_path)
        self._db_handle = self._bridge.db_open(filename, mode)

    def create_sphere(self, name: str, radius: float):
        self._bridge.create_sphere(self._db_handle, name, float(radius))
        return name

    def create_arb8(self, name: str, points):
        self._bridge.create_arb8(self._db_handle, name, points)
        return name

    def create_bot(self, name: str, vertices, faces):
        self._bridge.create_bot(self._db_handle, name, vertices, faces)
        return name

    def write_combination(self, name: str, members):
        self._bridge.write_combination(self._db_handle, name, members)
        return name

    def get_object(self, name: str):
        return self._bridge.get_object(self._db_handle, name)

    def set_attribute(self, object_name: str, key: str, value: str):
        self._bridge.set_attribute(self._db_handle, object_name, key, value)

    def get_attribute(self, object_name: str, key: str):
        return self._bridge.get_attribute(self._db_handle, object_name, key)

    def close(self):
        if getattr(self, "_db_handle", None):
            self._bridge.db_close(self._db_handle)
            self._db_handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
