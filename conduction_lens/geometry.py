"""Geometry adapters. A common entry point so the pipeline is geometry-agnostic.

crtdemo is wired (the vendored myocardial-mesh crtdemo). strocchi/medalcare are Phase 2/3 stubs;
the sweep is currently crtdemo-bound (sim.forward), so non-crtdemo geometries raise until their
adapter + electrode modeling land.
"""

from __future__ import annotations

SUPPORTED = ("crtdemo",)
STUBS = ("strocchi", "medalcare")


def load_geometry(name: str):
    """Return the loaded forward geometry object for `name` (crtdemo only, for now)."""
    if name == "crtdemo":
        from sim.forward import load_geometry as _load

        return _load()
    if name in STUBS:
        raise NotImplementedError(
            f"geometry '{name}' adapter is a Phase 2/3 stub (needs mesh ingestion + "
            f"body-surface electrode modeling); only {SUPPORTED} is wired"
        )
    raise ValueError(f"unknown geometry '{name}'; supported: {SUPPORTED + STUBS}")


def validate(name: str) -> None:
    if name not in SUPPORTED:
        load_geometry(name)  # raises NotImplementedError / ValueError with a clear message
