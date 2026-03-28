"""Backend selection helpers for BRL-CAD Python workflows."""

from __future__ import annotations

import os

from .moose_rt3_backend import MooseRt3Database


BACKEND_NATIVE = "native"
BACKEND_MOOSE_RT3 = "moose_rt3"


def open_database(filename: str, mode: str = "w", backend: str | None = None):
    """
    Open a BRL-CAD database using the requested backend.

    Supported backends:
    - moose_rt3: BRL-CAD/MOOSE C++ workflow via C bridge (default)
    """
    selected = (backend or os.environ.get("BRLCAD_BACKEND", BACKEND_MOOSE_RT3)).strip().lower()

    if selected == BACKEND_MOOSE_RT3:
        return MooseRt3Database(filename, mode)

    raise ValueError(
        f"Unsupported backend '{selected}'. Supported: {BACKEND_MOOSE_RT3}"
    )
