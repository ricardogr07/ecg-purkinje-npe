"""Geometry adapters. A common entry point so the pipeline is geometry-agnostic.

crtdemo and strocchi are wired; medalcare is a stub. Both crtdemo and strocchi attach a
`geom.tree_config`, so `sim.forward.forward` builds the Purkinje trees on the SAME heart it runs
the eikonal on: crtdemo grows fractal trees on its own endocardium, strocchi carries the
UVC-grown trees (see `adapter.strocchi.load_geometry`). No identifiability result is claimed on
the strocchi geometry (method generality only).
"""

from __future__ import annotations

SUPPORTED = ("crtdemo", "strocchi")
STUBS = ("medalcare",)


def load_geometry(name: str):
    """Return the loaded forward geometry object for `name`."""
    if name == "crtdemo":
        from sim.forward import load_geometry as _load

        return _load()
    if name == "strocchi":
        from adapter.strocchi import load_geometry as _load

        return _load()
    if name in STUBS:
        raise NotImplementedError(
            f"geometry '{name}' adapter is a stub (needs mesh ingestion + "
            f"body-surface electrode modeling); only {SUPPORTED} is wired"
        )
    raise ValueError(f"unknown geometry '{name}'; supported: {SUPPORTED + STUBS}")


def validate(name: str) -> None:
    if name not in SUPPORTED:
        load_geometry(name)  # raises NotImplementedError / ValueError with a clear message
