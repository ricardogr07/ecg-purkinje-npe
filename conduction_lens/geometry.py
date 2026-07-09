"""Geometry adapters. A common entry point so the pipeline is geometry-agnostic.

crtdemo and strocchi are wired. medalcare is a Phase 3 stub. NOTE: strocchi's MyocardialMesh
(volumetric mesh + fibers + electrodes) is wired, but `sim.forward.forward`'s Purkinje-tree
growth still hardcodes crtdemo's own endocardial OBJ paths (see
`adapter.strocchi.load_geometry`'s docstring) -- true cross-geometry parity needs that
parametrized, not yet done here.
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
            f"geometry '{name}' adapter is a Phase 3 stub (needs mesh ingestion + "
            f"body-surface electrode modeling); only {SUPPORTED} is wired"
        )
    raise ValueError(f"unknown geometry '{name}'; supported: {SUPPORTED + STUBS}")


def validate(name: str) -> None:
    if name not in SUPPORTED:
        load_geometry(name)  # raises NotImplementedError / ValueError with a clear message
