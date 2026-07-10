"""Strocchi biventricular mesh -> forward-model inputs for Purkinje/eikonal/ECG synthesis.

Ingest one Strocchi four-chamber / biventricular mesh (Strocchi et al. 2020, Zenodo 3890034,
CC-BY-4.0; the coarse ~1.1 mm cohort, EnSight `<id>.case` + `<id>.geo`) and produce the four
inputs `sim.forward`'s crtdemo pattern consumes:

    forward.py wants (by path)            this adapter produces
    ------------------------------------  --------------------------------------------
    crtdemo_LVendo_heart_cut.obj          EndoSurfaces.lv_endo  (-> write_forward_inputs)
    crtdemo_RVendo_heart_cut.obj          EndoSurfaces.rv_endo  (-> write_forward_inputs)
    crtdemo_mesh_oriented.vtk             the tag-{1,2} volumetric myo mesh (tetra, legacy .vtk)
    crtdemo_f0_oriented.vtk               CellData["fiber"] on that SAME point/cell set
    electrode_pos.pkl                     synth_electrodes_from_uvc() (UVC-derived, no torso)

Dataset contract (verified against the extracted `01.case` header + Zenodo record)
------------------------------------------------------------------------------
- Linear tetrahedra. Cell-data: `tags` (24 anatomical region labels; 1=LV myocardium,
  2=RV myocardium, 3=LA, 4=RA, 5-24=vessels/valve planes, not needed here), `fiber` and
  `sheet` (per-element unit vectors). Point-data: four UVC scalars (`uvc_transmural`
  0=endo/1=epi, `uvc_longitudinal` 0=apex/1=base, `uvc_rotational` -pi..0..+pi septum-anchored,
  `uvc_intraventricular` -1=LV/+1=RV) plus `electrode_endo_rv` (CRT pacing-site marker, unused
  here). Non-ventricular nodes carry UVC = -100 (sentinel); always exclude them explicitly,
  a naive `< threshold` comparison will wrongly admit them.
- There is no native LV-/RV-endocardium element tag (unlike the module's original placeholder
  assumption): endocardium must be derived from `uvc_transmural` on the tag-{1,2} node shell,
  split LV/RV by the sign of `uvc_intraventricular` (see `extract_endocardium`).
- Units are unstated in the record; `assert_millimetre_units` fails loudly if the loaded
  mesh's bounding box doesn't look like a human heart in mm (metres would read ~1000x smaller).

Pure + offline: reads local files, no network I/O.
"""

from __future__ import annotations

import pickle
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
    "assert_millimetre_units",
    "measure_base_to_apex",
    "synth_electrodes_from_uvc",
    "extract_ventricular_myocardium",
    "ingest",
    "DEFAULT_LV_TAG",
    "DEFAULT_RV_TAG",
    "TAG_FIELD_CANDIDATES",
]

# Verified against the extracted 01.case / Zenodo 3890034 label documentation: 1=LV
# myocardium, 2=RV myocardium (of 24 total anatomical region tags).
DEFAULT_LV_TAG = 1
DEFAULT_RV_TAG = 2

# Cell-data array names we try, in order, when tag_field is not given.
TAG_FIELD_CANDIDATES = ("tags", "elemTag", "Region", "region", "gmsh:physical", "cell_scalars")

# UVC point-data field names (verified against the extracted 01.case VARIABLE section).
TRANSMURAL_FIELD = "uvc_transmural"
LONGITUDINAL_FIELD = "uvc_longitudinal"
ROTATIONAL_FIELD = "uvc_rotational"
INTRAVENTRICULAR_FIELD = "uvc_intraventricular"
FIBER_FIELD = "fiber"

# UVC sentinel on non-ventricular nodes (atria, vessels, valve rings); all four UVC scalars
# carry this value there, so `>= 0` reliably drops them before any threshold comparison.
UVC_SENTINEL = -100.0

# "Near-endocardial" cutoff on the continuous uvc_transmural field (0=endo, 1=epi).
DEFAULT_TRANSMURAL_THRESHOLD = 0.05


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
    """Read an Ensight `.case` or VTK Strocchi mesh into a single pyvista dataset.

    `.case` reads as a `pyvista.MultiBlock` (one block per EnSight "part"); this cohort ships
    a single part, so `.combine()` it into one `UnstructuredGrid` so every downstream function
    can assume a flat dataset regardless of input format.
    """
    import pyvista as pv

    mesh = pv.read(str(path))
    if isinstance(mesh, pv.MultiBlock):
        mesh = mesh.combine()
    return mesh


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


def _point_array(mesh: Any, field: str) -> np.ndarray:
    if field not in mesh.point_data:
        raise KeyError(
            f"missing point-data field {field!r}; available: {list(mesh.point_data.keys())}"
        )
    return np.asarray(mesh.point_data[field], dtype=float)


def _endo_patch(surf: Any, mask: np.ndarray, label: str) -> Any:
    ids = np.flatnonzero(mask)
    if ids.size == 0:
        raise ValueError(f"{label} endocardial selection is empty; check UVC fields/threshold")
    patch = (
        surf.extract_points(ids, adjacent_cells=False)
        .extract_surface(algorithm="dataset_surface")
        .clean()
    )
    if patch.n_points == 0 or patch.n_cells == 0:
        raise ValueError(f"{label} endocardial patch has no cells; try a larger threshold")
    return patch


def extract_endocardium(
    mesh: Any,
    lv_tag: int = DEFAULT_LV_TAG,
    rv_tag: int = DEFAULT_RV_TAG,
    tag_field: str | None = None,
    transmural_field: str = TRANSMURAL_FIELD,
    intraventricular_field: str = INTRAVENTRICULAR_FIELD,
    transmural_threshold: float = DEFAULT_TRANSMURAL_THRESHOLD,
) -> EndoSurfaces:
    """Extract LV/RV endocardial surfaces from tag + UVC fields (pure, offline).

    Algorithm (there is no native endocardium element tag in this dataset, see module
    docstring): take the boundary surface of the combined tag-{lv_tag, rv_tag} cell
    selection (this cancels the internal LV/RV septal-interface faces, since each is shared
    by one tag-1 and one tag-2 cell and so is *not* part of the tag-union's exterior boundary
    -- verified empirically: extracting LV/RV boundaries separately double-counts ~4% of faces
    at that interface). Then keep only points with `uvc_transmural` near 0 (endocardial, not
    the -100 sentinel), split into LV/RV by the sign of `uvc_intraventricular`.
    """
    tags, _ = _tag_array(mesh, tag_field)
    present = set(np.unique(tags).tolist())
    for tag, label in ((lv_tag, "LV"), (rv_tag, "RV")):
        if tag not in present:
            raise ValueError(
                f"{label} tag {tag} not present in mesh (present tags: {sorted(present)})"
            )
    vent_mask = np.isin(tags, [lv_tag, rv_tag])
    vent = mesh.extract_cells(np.flatnonzero(vent_mask))
    surf = vent.extract_surface(algorithm="dataset_surface").clean()

    tm = _point_array(surf, transmural_field)
    iv = _point_array(surf, intraventricular_field)
    endo = (tm >= 0) & (tm < transmural_threshold)  # >=0 drops the UVC_SENTINEL
    return EndoSurfaces(
        lv_endo=_endo_patch(surf, endo & (iv < 0), "LV"),
        rv_endo=_endo_patch(surf, endo & (iv > 0), "RV"),
    )


def assert_millimetre_units(mesh: Any, min_mm: float = 50.0, max_mm: float = 300.0) -> float:
    """Hard, loud sanity check that mesh coordinates are millimetres, not metres.

    Neither the `.case` header nor the Zenodo record states units. A human heart spans
    roughly 100-150 mm base-to-apex / side-to-side; if the bounding-box extent comes back
    ~0.1-0.15, the coordinates are actually metres and every downstream conduction-velocity
    number (m/s over mm) would be wrong by 1000x. min_mm/max_mm intentionally bracket wider
    than a normal heart (this cohort is dilated heart-failure ventricles).
    """
    bounds = np.asarray(mesh.bounds, dtype=float).reshape(3, 2)
    max_span = float((bounds[:, 1] - bounds[:, 0]).max())
    if not (min_mm <= max_span <= max_mm):
        raise ValueError(
            f"mesh bounding-box max extent {max_span:.4f} is outside the expected "
            f"[{min_mm}, {max_mm}] mm range for a human heart; coordinates may be in metres "
            f"(or another unit), not millimetres. bounds={mesh.bounds}"
        )
    return max_span


def measure_base_to_apex(
    mesh: Any,
    intraventricular_sign: int,
    longitudinal_field: str = LONGITUDINAL_FIELD,
    intraventricular_field: str = INTRAVENTRICULAR_FIELD,
    apex_quantile: float = 0.02,
    base_quantile: float = 0.98,
) -> float:
    """Measure one ventricle's base-to-apex extent from apico-basal UVC + coordinates.

    Apex/base centroids are the mean position of points with `uvc_longitudinal` below/above
    the given quantile cutoffs, restricted to the requested ventricle (sign of
    `uvc_intraventricular`: -1 for LV, +1 for RV). Compare against the frozen
    `init_length_lv`/`init_length_rv` prior box (`src/core/theta.py`, [30, 60] mm) and Lang
    2015 (RV base-to-apex 71+/-6 mm normal) -- this cohort is heart-failure patients with
    dilated ventricles, so the box may not hold; report honestly either way.
    """
    ab = _point_array(mesh, longitudinal_field)
    iv = _point_array(mesh, intraventricular_field)
    pts = np.asarray(mesh.points, dtype=float)
    valid = ab >= 0
    vent = valid & (np.sign(iv) == intraventricular_sign)
    apex_pts = pts[vent & (ab < np.quantile(ab[vent], apex_quantile))]
    base_pts = pts[vent & (ab > np.quantile(ab[vent], base_quantile))]
    return float(np.linalg.norm(base_pts.mean(axis=0) - apex_pts.mean(axis=0)))


# ---------------------------------------------------------------------------------------
# C.6 electrode placement. See synth_electrodes_from_uvc docstring for the disclosed rule.
# ---------------------------------------------------------------------------------------

# (label, level along the long axis [0=apex, 1=base], angle in the (e_sept, e_lat) plane
# (degrees, 0=septum, +=toward RV free wall, -=toward LV lateral wall), standoff beyond the
# local epicardial radius in mm). V1->V6 sweep right (RV side) to left-lateral (LV free wall)
# at a fixed mid-ventricular level, mimicking the real precordial intercostal sweep; RA/LA
# sit near the base and further out (shoulder-like); LL sits beyond the apex (leg-like).
_STANDOFF_MM = 30.0
_LIMB_STANDOFF_MM = 50.0
_ELECTRODE_LAYOUT: tuple[tuple[str, float, float, float], ...] = (
    ("V1", 0.45, 100.0, _STANDOFF_MM),
    ("V2", 0.45, 60.0, _STANDOFF_MM),
    ("V3", 0.45, 20.0, _STANDOFF_MM),
    ("V4", 0.45, -20.0, _STANDOFF_MM),
    ("V5", 0.45, -60.0, _STANDOFF_MM),
    ("V6", 0.45, -100.0, _STANDOFF_MM),
    ("RA", 0.95, 130.0, _LIMB_STANDOFF_MM),
    ("LA", 0.95, -130.0, _LIMB_STANDOFF_MM),
    ("LL", -0.15, -130.0, _LIMB_STANDOFF_MM),
)


def synth_electrodes_from_uvc(
    mesh: Any,
    longitudinal_field: str = LONGITUDINAL_FIELD,
    rotational_field: str = ROTATIONAL_FIELD,
    transmural_field: str = TRANSMURAL_FIELD,
    intraventricular_field: str = INTRAVENTRICULAR_FIELD,
) -> dict[str, list[float]]:
    """Synthesize 9 electrode positions (V1-V6, LA, RA, LL) from this heart's own UVC frame.

    Disclosed modeling rule (no torso ships with this cohort, see module docstring, so the
    real Kligfield 2007 intercostal-space landmarks have no body surface to sit on):

    1. Build an orthonormal frame from the mesh's own UVC fields: `e_long` is the apex
       (uvc_longitudinal ~ 0) -> base (~ 1) direction; `e_sept` is the direction from the
       long axis toward the septum (uvc_rotational ~ 0, LV side) at mid-ventricle; `e_lat`
       completes the frame (`e_long x e_sept`).
    2. Estimate a characteristic epicardial radius (uvc_transmural ~ 1) at mid-ventricle,
       used as the base standoff distance so electrodes sit just outside the heart surface.
    3. Each of the 9 electrodes is placed at `apex + level * long_len * e_long + (radius +
       standoff) * (cos(theta) * e_sept + sin(theta) * e_lat)` for a fixed (level, theta,
       standoff) triple per `_ELECTRODE_LAYOUT`: V1->V6 sweep theta from the RV free-wall
       side to the LV lateral side at a fixed mid-ventricular level (mimicking the real
       precordial sweep); RA/LA sit near the base and further out (shoulder-like); LL sits
       beyond the apex (leg-like).

    This is a disclosed synthetic approximation (no real torso geometry, one constant radius
    reused at every level), not a body-surface measurement -- flag as such in any writeup.
    Returns a dict shaped exactly like crtdemo's electrode_pos.pkl: 9 keys, plain 3-float
    lists in mm.
    """
    ab = _point_array(mesh, longitudinal_field)
    rot = _point_array(mesh, rotational_field)
    tm = _point_array(mesh, transmural_field)
    iv = _point_array(mesh, intraventricular_field)
    pts = np.asarray(mesh.points, dtype=float)

    valid = ab >= 0
    apex = pts[valid & (ab < 0.02)].mean(axis=0)
    base = pts[valid & (ab > 0.98)].mean(axis=0)
    long_vec = base - apex
    long_len = float(np.linalg.norm(long_vec))
    e_long = long_vec / long_len
    heart_center = apex + 0.5 * long_len * e_long

    septal = valid & (np.abs(rot) < 0.15) & (ab > 0.4) & (ab < 0.6) & (iv < 0)
    v = pts[septal].mean(axis=0) - heart_center
    v = v - np.dot(v, e_long) * e_long
    e_sept = v / np.linalg.norm(v)
    e_lat = np.cross(e_long, e_sept)
    e_lat /= np.linalg.norm(e_lat)

    epi = valid & (tm > 0.9) & (ab > 0.4) & (ab < 0.6)
    rel = pts[epi] - heart_center
    rel_perp = rel - np.outer(rel @ e_long, e_long)
    radius = float(np.linalg.norm(rel_perp, axis=1).mean())

    out: dict[str, list[float]] = {}
    for label, level, theta_deg, standoff in _ELECTRODE_LAYOUT:
        theta = np.deg2rad(theta_deg)
        offset = (radius + standoff) * (np.cos(theta) * e_sept + np.sin(theta) * e_lat)
        point = apex + level * long_len * e_long + offset
        out[label] = [float(x) for x in point]
    return out


def extract_ventricular_myocardium(
    mesh: Any,
    lv_tag: int = DEFAULT_LV_TAG,
    rv_tag: int = DEFAULT_RV_TAG,
    tag_field: str | None = None,
    fiber_field: str = FIBER_FIELD,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Filter the volumetric mesh to tag-{lv_tag, rv_tag} tetrahedra (LV+RV myocardium only).

    Returns (points, tetra cell connectivity, per-cell fiber vectors), all on the SAME
    filtered point/cell set so a myo-mesh file and a fibers file built from them stay
    geometrically consistent (same points, same cell ordering).
    """
    tags, _ = _tag_array(mesh, tag_field)
    vent_mask = np.isin(tags, [lv_tag, rv_tag])
    vent = mesh.extract_cells(np.flatnonzero(vent_mask))
    points = np.asarray(vent.points, dtype=float)
    cells = np.asarray(vent.cells_dict[10], dtype=int)  # VTK_TETRA == 10
    fiber = np.asarray(vent.cell_data[fiber_field], dtype=float)
    if cells.shape[0] != fiber.shape[0]:
        raise ValueError(
            f"cell/fiber count mismatch after tag filtering: {cells.shape[0]} cells vs "
            f"{fiber.shape[0]} fiber vectors"
        )
    return points, cells, fiber


def write_volumetric_inputs(
    points: np.ndarray, cells: np.ndarray, fiber: np.ndarray, out_dir: str | Path
) -> dict[str, Path]:
    """Write the tag-filtered tetra myo mesh + a same-point/cell fibers file (legacy .vtk).

    Mirrors crtdemo_mesh_oriented.vtk / crtdemo_f0_oriented.vtk: the myo mesh carries no
    fiber data, the fibers file carries CellData["fiber"] (per-element, matching the CASE's
    native per-element fiber field -- no node/cell interpolation needed).
    """
    import meshio

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    myo_path = out / "strocchi_myo.vtk"
    fibers_path = out / "strocchi_fibers.vtk"
    meshio.write_points_cells(str(myo_path), points, [("tetra", cells)])
    meshio.write_points_cells(
        str(fibers_path), points, [("tetra", cells)], cell_data={"fiber": [fiber]}
    )
    return {"myo_mesh": myo_path, "fibers": fibers_path}


def write_electrodes(electrodes: dict[str, list[float]], out_dir: str | Path) -> Path:
    """Write the electrode dict as a pickle, matching crtdemo's electrode_pos.pkl format."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "strocchi_electrode_pos.pkl"
    with open(path, "wb") as f:
        pickle.dump(electrodes, f)
    return path


def ingest(case_path: str | Path, out_dir: str | Path, **kwargs: Any) -> dict[str, Path]:
    """Read a Strocchi `.case` mesh and write all four forward-model inputs to `out_dir`.

    Returns the same key shape `sim.forward.load_geometry`/`FractalTree` consume: lv_endo,
    rv_endo (OBJ), myo_mesh, fibers (volumetric .vtk), electrodes (pickle).
    """
    mesh = read_mesh(case_path)
    assert_millimetre_units(mesh)
    surfaces = extract_endocardium(mesh, **kwargs)
    paths = {
        k: v
        for k, v in surfaces.write_forward_inputs(out_dir).items()
        if k in ("lv_endo", "rv_endo")
    }
    points, cells, fiber = extract_ventricular_myocardium(mesh)
    paths.update(write_volumetric_inputs(points, cells, fiber, out_dir))
    electrodes = synth_electrodes_from_uvc(mesh)
    paths["electrodes"] = write_electrodes(electrodes, out_dir)
    return paths


# ---------------------------------------------------------------------------------------
# F5 Purkinje-tree growth on the Strocchi endocardium (the UVC-as-UV hook).
#
# The UVC-thresholded endo is ragged (hundreds of open edges), so purkinje-uv's harmonic disk
# map (Mesh.uvmap) fails. Instead feed the mesh's own analytic UVC (rotational, longitudinal)
# straight in as the UV via FractalTree(uv=...), which bypasses the harmonic solve. Seeds are
# anatomical (His origin at the basal septum). Constants mirror experiments/f5_uvc_tree.py
# (verified: LV 44 / RV 138 PMJs). ponytail: f5_uvc_tree.py duplicates _prep_endo_patch /
# _pick_his_seeds; fold that driver onto these once the Strocchi forward is settled.
# ---------------------------------------------------------------------------------------
_F5_SEAM_RAD = 3.0  # rotational span (rad) above which a triangle straddles the +/-pi seam
_F5_FAS: dict[str, tuple[list[float], list[float]]] = {
    "lv": (
        [0.5 * 4.711579058738858, 0.5 * 9.129484609771032],
        [0.1 * 0.14448952070696136, 0.1 * 0.23561944901923448],
    ),
    "rv": (
        [0.5 * 21.703867933650002, 0.5 * 5.79561866201451],
        [0.1 * 0.23561944901923448, 0.1 * 0.23561944901923448],
    ),
}
_F5_INIT_LEN = 15.0
_F5_LENGTH = 8.0
_F5_L_SEGMENT = 1.0
_F5_W = 0.1
_F5_BRANCH_ANGLE = 0.175


def _prep_endo_patch(patch: Any) -> tuple[Any, np.ndarray, np.ndarray]:
    """Triangulate, drop the triangles that break the UVC parametrization (the +/-pi rotational
    seam, the apex singularity where longitudinal -> 0, and near-zero-area slivers in 3D or UV),
    then keep the largest connected component. Returns (poly, rot, lon) aligned to poly.points."""
    import pyvista as pv

    tri = patch.triangulate().clean()
    pts = np.asarray(tri.points, float)
    rot = np.asarray(tri.point_data["uvc_rotational"], float)
    lon = np.asarray(tri.point_data["uvc_longitudinal"], float)
    faces = np.asarray(tri.faces, int).reshape(-1, 4)[:, 1:]

    v0, v1, v2 = pts[faces[:, 0]], pts[faces[:, 1]], pts[faces[:, 2]]
    area3d = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)
    uvv = np.column_stack([rot, lon])
    u0, u1, u2 = uvv[faces[:, 0]], uvv[faces[:, 1]], uvv[faces[:, 2]]
    uvarea = 0.5 * np.abs(np.cross(u1 - u0, u2 - u0))
    span = rot[faces].max(1) - rot[faces].min(1)
    apex = lon[faces].max(1) < 0.05  # triangle wholly in the singular apex cap

    keep = (
        (span <= _F5_SEAM_RAD) & (area3d > 1e-6 * float(area3d.max())) & (uvarea > 1e-9) & (~apex)
    )
    kf = faces[keep]
    poly = pv.PolyData(pts, np.hstack([np.full((kf.shape[0], 1), 3), kf]).ravel())
    poly.point_data["uvc_rotational"] = rot
    poly.point_data["uvc_longitudinal"] = lon
    poly = poly.clean().connectivity("largest").triangulate().clean()
    rot = np.asarray(poly.point_data["uvc_rotational"], float)
    lon = np.asarray(poly.point_data["uvc_longitudinal"], float)
    return poly, rot, lon


# Above this rot/lon 3D-scale ratio the UV is too anisotropic to grow on directly: the fractal
# tree (defined in mm) grows across the flattened parameter space instead of along the surface,
# producing radial chords. A full-2pi closed chamber (LV, ~3.9x) trips this; a partial-arc RV
# (~1.9x) does not and keeps its native UV byte-identical. ponytail: single threshold; if a future
# heart lands between these, revisit rather than hand-tune per heart.
_UV_ISOMETRIZE_ANISOTROPY = 2.5


def _uv_axis_scales(poly: Any, rot: np.ndarray, lon: np.ndarray) -> tuple[float, float]:
    """Median 3D mm per unit-rot and per unit-lon, from mesh edges that move mostly along one UV
    axis. A closed chamber unrolled over the full 2pi has rot-scale >> lon-scale; feeding that
    anisotropic UV straight in distorts the mm-defined growth into radial spokes."""
    faces = np.asarray(poly.faces, int).reshape(-1, 4)[:, 1:]
    pts = np.asarray(poly.points, float)
    e = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    d3 = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
    dr = np.abs(rot[e[:, 0]] - rot[e[:, 1]])
    dl = np.abs(lon[e[:, 0]] - lon[e[:, 1]])
    rot_e = (dr > 1e-3) & (dr > 5 * dl)
    lon_e = (dl > 1e-3) & (dl > 5 * dr)
    rs = float(np.median(d3[rot_e] / dr[rot_e])) if rot_e.any() else 1.0
    ls = float(np.median(d3[lon_e] / dl[lon_e])) if lon_e.any() else 1.0
    return rs, ls


def _growth_uv(poly: Any, rot: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """UV for FractalTree growth: isometric (rot, lon rescaled to mm) when the native UV is badly
    anisotropic (LV full chamber), else the native UV unchanged (RV, byte-identical)."""
    rs, ls = _uv_axis_scales(poly, rot, lon)
    if max(rs, ls) / max(min(rs, ls), 1e-9) > _UV_ISOMETRIZE_ANISOTROPY:
        return np.column_stack([rot * rs, lon * ls]).astype(float)
    return np.column_stack([rot, lon]).astype(float)


def _pick_his_seeds(rot: np.ndarray, lon: np.ndarray) -> tuple[int, int]:
    """His-origin seeds from UVC: init = most basal septal vertex; second = a septal vertex just
    apical of it (sets a downward-the-septum initial direction)."""
    septal = np.abs(rot) < 1.0
    for thr in (0.3, 0.6, 1.0):
        septal = np.abs(rot) < thr
        if septal.sum() >= 5:
            break
    init = int(np.argmax(np.where(septal, lon, -np.inf)))
    cand = np.flatnonzero(septal & (lon < lon[init]))
    if cand.size == 0:
        cand = np.flatnonzero(septal & (np.arange(rot.size) != init))
    d = (rot[cand] - rot[init]) ** 2 + (lon[cand] - lon[init]) ** 2
    second = int(cand[int(np.argmin(np.where(d > 0, d, np.inf)))])
    return init, second


def grow_purkinje_trees(mesh: Any, out_dir: str | Path, n_it: int | None = None) -> tuple[Any, Any]:
    """Grow LV and RV Purkinje trees on the Strocchi endocardium and return them as purkinje-uv
    ``PurkinjeTree`` objects (nodes + connectivity + PMJ end nodes), ready for ``run_ecg_core``.

    Fascicles are mandatory: without them the trunk's branching edge is never re-queued and the
    tree stops at the trunk (0 PMJs). N_it defaults to the F5_NIT env (else 15); the LV saturates
    near 44 PMJs by collision regardless."""
    import os

    import meshio
    from purkinje_uv import FractalTree, FractalTreeParameters, PurkinjeTree

    if n_it is None:
        n_it = int(os.environ.get("F5_NIT", "15"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    endo = extract_endocardium(mesh)

    trees = []
    for label, patch in (("lv", endo.lv_endo), ("rv", endo.rv_endo)):
        poly, rot, lon = _prep_endo_patch(patch)
        obj = out / f"strocchi_f5_{label}_endo_cut.obj"
        faces = np.asarray(poly.faces, int).reshape(-1, 4)[:, 1:]
        meshio.write_points_cells(str(obj), np.asarray(poly.points, float), [("triangle", faces)])
        init, second = _pick_his_seeds(rot, lon)
        fas_len, fas_ang = _F5_FAS[label]
        params = FractalTreeParameters(
            meshfile=str(obj),
            init_node_id=init,
            second_node_id=second,
            init_length=_F5_INIT_LEN,
            length=_F5_LENGTH,
            l_segment=_F5_L_SEGMENT,
            w=_F5_W,
            branch_angle=_F5_BRANCH_ANGLE,
            N_it=n_it,
            fascicles_length=fas_len,
            fascicles_angles=fas_ang,
        )
        ft = FractalTree(params=params, uv=_growth_uv(poly, rot, lon))
        ft.grow_tree()
        trees.append(
            PurkinjeTree(
                nodes=np.asarray(ft.nodes_xyz, dtype=float),
                connectivity=np.asarray(ft.connectivity, dtype=int),
                end_nodes=np.asarray(ft.end_nodes, dtype=int),
            )
        )
    return trees[0], trees[1]


# data/ is gitignored (see .gitignore); these are worktree-local defaults, not shipped in git.
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "01"
DEFAULT_CASE_PATH = DATA_DIR / "01.case"
DEFAULT_CACHE_DIR = DATA_DIR / "_forward_inputs"


def load_geometry(
    case_path: str | Path = DEFAULT_CASE_PATH, cache_dir: str | Path = DEFAULT_CACHE_DIR
) -> Any:
    """Build the Strocchi MyocardialMesh once (mesh + fibers + electrodes).

    Mirrors `sim.forward.load_geometry`'s crtdemo pattern (same MyocardialMesh(myo_mesh=,
    electrodes_position=, fibers=) call), only the geometry differs. Caches the derived
    forward-input files under `cache_dir` (`ingest` is a pure function of `case_path`, so
    reusing an existing cache is safe) so repeated calls don't re-run the ingest step.

    Grows the Strocchi LV/RV Purkinje trees (F5 UVC hook, `grow_purkinje_trees`) and attaches
    them to `geom.tree_config` so `forward(theta, load_geometry())` runs the literal chain on
    THIS heart's own trees, myocardium, and electrodes. Because the trees are pre-grown, the
    tree-growth theta keys (`init_length_*`, `branch_angle`, `w`) are inert for this geometry:
    the Strocchi forward is a single fixed-theta, method-generality run, not an identifiability
    sweep. No identifiability result is claimed on this geometry.
    """
    from myocardial_mesh import MyocardialMesh

    from sim.forward import TreeConfig

    cache_dir = Path(cache_dir)
    myo_path = cache_dir / "strocchi_myo.vtk"
    fibers_path = cache_dir / "strocchi_fibers.vtk"
    electrodes_path = cache_dir / "strocchi_electrode_pos.pkl"
    if not (myo_path.exists() and fibers_path.exists() and electrodes_path.exists()):
        ingest(case_path, cache_dir)
    geom = MyocardialMesh(
        myo_mesh=str(myo_path),
        electrodes_position=str(electrodes_path),
        fibers=str(fibers_path),
    )
    lv_tree, rv_tree = grow_purkinje_trees(read_mesh(case_path), cache_dir)
    # Pre-grown trees carry the Purkinje network; endo/seed fields below are inert placeholders
    # (forward short-circuits growth when lv_tree/rv_tree are set), kept for provenance.
    geom.tree_config = TreeConfig(
        lv_endo=str(cache_dir / "strocchi_f5_lv_endo_cut.obj"),
        rv_endo=str(cache_dir / "strocchi_f5_rv_endo_cut.obj"),
        lv_seeds=(0, 1),
        rv_seeds=(0, 1),
        lv_fas_len=_F5_FAS["lv"][0],
        rv_fas_len=_F5_FAS["rv"][0],
        lv_fas_ang=_F5_FAS["lv"][1],
        rv_fas_ang=_F5_FAS["rv"][1],
        lv_tree=lv_tree,
        rv_tree=rv_tree,
    )
    return geom
