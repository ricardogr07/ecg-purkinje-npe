"""Strocchi biventricular mesh -> endocardial surfaces for Purkinje growth.

Ingest one Strocchi four-chamber / biventricular mesh (Strocchi et al. 2020,
Zenodo 3890034, CC-BY-4.0; the coarse ~1.1 mm cohort) and hand Science the two
endocardial SURFACES that purkinje-uv grows fractal trees on, mirroring the crtdemo
inputs that `src/sim/forward.py` already consumes:

    forward.py wants (by path)            this adapter produces
    ------------------------------------  --------------------------------------------
    crtdemo_LVendo_heart_cut.obj          EndoSurfaces.lv_endo  (-> write_forward_inputs)
    crtdemo_RVendo_heart_cut.obj          EndoSurfaces.rv_endo  (-> write_forward_inputs)
    crtdemo_f0_oriented.vtk               EndoSurfaces.fibers      (passthrough by path)
    electrode_pos.pkl                     EndoSurfaces.electrodes  (passthrough by path)

Expected Strocchi inputs
------------------------
- A volumetric OR a pre-labelled surface mesh readable by pyvista/meshio: Ensight
  (`case_XX.case` next to its `.geo`) or VTK. `pyvista.read` handles both formats.
- A per-cell integer label array. The Strocchi cohort ships anatomical region/surface
  labels; the LV- and RV-endocardium label VALUES are a dataset convention, so pass
  them in via `lv_tag` / `rv_tag`. `DEFAULT_LV_ENDO_TAG` / `DEFAULT_RV_ENDO_TAG` below
  are PLACEHOLDERS: confirm them against the downloaded cohort's label documentation
  before trusting a run. The label array name is auto-detected from a small candidate
  list, or pass `tag_field=...` explicitly.
- Fibres and electrodes are passed through by path (the ECG forward reads them
  directly); this adapter does not synthesise them.

Extraction is "surface by element tag": select the cells carrying the endo label, then
take their boundary surface. On a pre-labelled surface mesh this returns exactly the
labelled endo patch; on a volumetric region this returns that region's closed surface.
ponytail: element-region tags alone do not separate endo from epi, that split needs the
dataset's surface labels; wire the real endo label values into lv_tag/rv_tag once the
file is in hand.

purkinje-uv's FractalTree reads OBJ triangle surfaces only (Mesh.loadOBJ), so
`write_forward_inputs` emits triangulated `.obj`.

Pure + offline: reads local files, no network I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:  # annotations only; pyvista is imported lazily inside functions
    import pyvista as pv

__all__ = [
    "EndoSurfaces",
    "read_mesh",
    "extract_endocardium",
    "ingest",
    "DEFAULT_LV_ENDO_TAG",
    "DEFAULT_RV_ENDO_TAG",
    "TAG_FIELD_CANDIDATES",
]

# PLACEHOLDER label values. Confirm against the Strocchi cohort label documentation.
DEFAULT_LV_ENDO_TAG = 1
DEFAULT_RV_ENDO_TAG = 2

# Cell-data array names we try, in order, when tag_field is not given.
TAG_FIELD_CANDIDATES = ("tags", "elemTag", "Region", "region", "gmsh:physical", "cell_scalars")


@dataclass
class EndoSurfaces:
    """LV/RV endocardial surfaces plus by-path fibre/electrode hooks for the forward model."""

    lv_endo: pv.PolyData
    rv_endo: pv.PolyData
    fibers: Path | None = None
    electrodes: Path | None = None

    def write_forward_inputs(self, out_dir: str | Path) -> dict[str, Path | None]:
        """Write triangulated LV/RV endo OBJs and return the path dict forward.py consumes.

        Keys mirror the crtdemo inputs: lv_endo, rv_endo (OBJ paths), fibers, electrodes
        (passthrough, may be None).
        """
        import meshio

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path | None] = {}
        for key, surf in (("lv_endo", self.lv_endo), ("rv_endo", self.rv_endo)):
            tri = surf.triangulate()
            faces = np.asarray(tri.faces, dtype=int).reshape(-1, 4)[:, 1:]
            path = out / f"strocchi_{key}.obj"
            meshio.write_points_cells(
                str(path),
                np.asarray(tri.points, dtype=float),
                [("triangle", np.asarray(faces, dtype=int))],
            )
            paths[key] = path
        paths["fibers"] = self.fibers
        paths["electrodes"] = self.electrodes
        return paths


def read_mesh(path: str | Path) -> Any:
    """Read an Ensight `.case` or VTK Strocchi mesh into a pyvista dataset."""
    import pyvista as pv

    return pv.read(str(path))


def _tag_array(mesh: Any, tag_field: str | None) -> tuple[np.ndarray, str]:
    if tag_field is not None:
        return np.asarray(mesh.cell_data[tag_field]), tag_field
    for name in TAG_FIELD_CANDIDATES:
        if name in mesh.cell_data:
            return np.asarray(mesh.cell_data[name]), name
    raise KeyError(
        f"No cell-tag array found (tried {TAG_FIELD_CANDIDATES}). "
        f"Available cell_data: {list(mesh.cell_data.keys())}. Pass tag_field=... explicitly."
    )


def _surface_by_tag(mesh: Any, tag: int, tags: np.ndarray) -> Any:
    mask = tags == tag
    if not mask.any():
        raise ValueError(
            f"tag {tag} not present in mesh (present tags: {np.unique(tags).tolist()})"
        )
    # Pin algorithm: pyvista is changing the extract_surface default; keep today's behavior.
    sub = mesh.extract_cells(np.flatnonzero(mask))
    surf = sub.extract_surface(algorithm="dataset_surface").clean()
    if surf.n_points == 0:
        raise ValueError(f"tag {tag} produced an empty surface")
    return surf


def extract_endocardium(
    mesh: Any,
    lv_tag: int = DEFAULT_LV_ENDO_TAG,
    rv_tag: int = DEFAULT_RV_ENDO_TAG,
    tag_field: str | None = None,
) -> EndoSurfaces:
    """Extract LV and RV endocardial surfaces from a tagged pyvista mesh (pure, offline)."""
    tags, _ = _tag_array(mesh, tag_field)
    return EndoSurfaces(
        lv_endo=_surface_by_tag(mesh, lv_tag, tags),
        rv_endo=_surface_by_tag(mesh, rv_tag, tags),
    )


def ingest(
    case_path: str | Path,
    *,
    lv_tag: int = DEFAULT_LV_ENDO_TAG,
    rv_tag: int = DEFAULT_RV_ENDO_TAG,
    tag_field: str | None = None,
    fibers: str | Path | None = None,
    electrodes: str | Path | None = None,
) -> EndoSurfaces:
    """Read a Strocchi mesh file and return its LV/RV endo surfaces + fibre/electrode hooks."""
    surfaces = extract_endocardium(read_mesh(case_path), lv_tag, rv_tag, tag_field)
    surfaces.fibers = Path(fibers) if fibers is not None else None
    surfaces.electrodes = Path(electrodes) if electrodes is not None else None
    return surfaces
