"""F5 (Idea 1 + Idea 3): grow a Purkinje FractalTree on the Strocchi endocardium using the
mesh's OWN UVC as the parametrization, instead of purkinje-uv's harmonic disk map.

Why this works where f5_repair / f5_iso failed: Mesh.uvmap() solves a Laplace harmonic map that
REQUIRES a clean single closed boundary loop (uv_bc walks one loop and maps it to a circle). The
UVC-thresholded endocardium is ragged (hundreds of open edges = many loops), so uv_bc raises. But
the Strocchi mesh already ships an analytic 2D coordinate per node: (uvc_rotational in [-pi, pi],
uvc_longitudinal in [0, 1]). Feeding that straight in as the UV (via the new FractalTree(uv=...)
hook) bypasses the harmonic solve entirely, so raggedness no longer matters. The one wrinkle is
that rotational is periodic; we cut the seam (drop triangles whose rotational span > 3.0 rad) so
the endo unrolls to a clean strip.

Idea 3: seeds are anatomical, not arbitrary. The His / proximal conduction origin sits at the
BASAL SEPTUM: rotational ~ 0 (septum-anchored) and longitudinal near 1 (base). init_node is the
most basal septal vertex; second_node is a septal vertex just apical of it, so the trunk grows
DOWN the septum before fanning out.

Run: .venv/Scripts/python.exe experiments/f5_uvc_tree.py
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "packages" / "purkinje-uv" / "src"))

import meshio  # noqa: E402
import numpy as np  # noqa: E402
from purkinje_uv import FractalTree, FractalTreeParameters  # noqa: E402

from adapter.strocchi import extract_endocardium, read_mesh  # noqa: E402

CASE = ROOT / "data" / "01" / "01.case"
OUT = ROOT / "outputs"
SEAM_RAD = 3.0  # rotational span (rad) above which a triangle straddles the +/-pi seam


def open_edges(poly):
    b = poly.extract_feature_edges(
        boundary_edges=True, non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    return int(b.n_cells)


def prep_patch(patch):
    """Triangulate, then drop the triangles that break the UVC parametrization: (a) the +/-pi
    rotational seam, (b) the apex singularity (longitudinal -> 0, where all rotational values
    collapse), (c) any near-zero-area sliver in 3D or in UV space. These are exactly the
    degenerate triangles that make _eval_field's projection return tri=-1. Then keep the largest
    connected component. Returns (poly, rot, lon) aligned to poly.points."""
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

    keep = (span <= SEAM_RAD) & (area3d > 1e-6 * float(area3d.max())) & (uvarea > 1e-9) & (~apex)
    kf = faces[keep]
    poly = pv.PolyData(pts, np.hstack([np.full((kf.shape[0], 1), 3), kf]).ravel())
    poly.point_data["uvc_rotational"] = rot
    poly.point_data["uvc_longitudinal"] = lon
    poly = poly.clean().connectivity("largest").triangulate().clean()
    rot = np.asarray(poly.point_data["uvc_rotational"], float)
    lon = np.asarray(poly.point_data["uvc_longitudinal"], float)
    return poly, rot, lon


def pick_seeds(rot, lon):
    """His-origin seeds from UVC: init = most basal septal vertex; second = septal vertex just
    apical of it (sets a downward-the-septum initial direction)."""
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


# crtdemo fractal preset (src/sim/forward.py). Fascicles are mandatory: without them the trunk's
# branching edge is never re-queued and the tree stops at the trunk (0 PMJs). Angles are UV-space
# direction rotations (dimensionless, transfer as-is); lengths are mm (uvscaling absorbs the
# UV->3D scale, so the same mm values apply on the UVC parametrization).
FAS = {
    "lv": (
        [0.5 * 4.711579058738858, 0.5 * 9.129484609771032],
        [0.1 * 0.14448952070696136, 0.1 * 0.23561944901923448],
    ),
    "rv": (
        [0.5 * 21.703867933650002, 0.5 * 5.79561866201451],
        [0.1 * 0.23561944901923448, 0.1 * 0.23561944901923448],
    ),
}
INIT_LEN = {"lv": 15.0, "rv": 15.0}


def grow_one(label, patch):
    cut, rot, lon = prep_patch(patch)
    stats = (
        f"pts={cut.n_points} tris={cut.n_cells} open_edges={open_edges(cut)} "
        f"rot=[{rot.min():.2f},{rot.max():.2f}] lon=[{lon.min():.2f},{lon.max():.2f}]"
    )
    print(f"[f5uvc] {label} patch: {stats}", flush=True)

    obj = OUT / f"f5_{label}_endo_cut.obj"
    faces = np.asarray(cut.faces, int).reshape(-1, 4)[:, 1:]
    meshio.write_points_cells(str(obj), np.asarray(cut.points, float), [("triangle", faces)])
    uv = np.column_stack([rot, lon]).astype(float)

    init, second = pick_seeds(rot, lon)
    print(
        f"[f5uvc] {label} seeds: init={init} (rot={rot[init]:.2f} lon={lon[init]:.2f}) "
        f"second={second} (rot={rot[second]:.2f} lon={lon[second]:.2f})",
        flush=True,
    )

    fas_len, fas_ang = FAS[label]
    params = FractalTreeParameters(
        meshfile=str(obj),
        init_node_id=init,
        second_node_id=second,
        init_length=INIT_LEN[label],
        length=8.0,
        l_segment=1.0,
        w=0.1,
        branch_angle=0.175,
        N_it=int(os.environ.get("F5_NIT", "15")),
        fascicles_length=fas_len,
        fascicles_angles=fas_ang,
    )
    try:
        ft = FractalTree(params=params, uv=uv)
        ft.grow_tree()
        n_pmj = len(ft.end_nodes)
        n_nodes = len(ft.nodes_xyz)
        print(f"[f5uvc] {label} GROWN: nodes={n_nodes} PMJs={n_pmj}", flush=True)
        try:
            ft.save(str(OUT / f"f5_{label}_tree.vtu"))
        except Exception as e:  # noqa: BLE001
            print(f"[f5uvc] {label} save skipped: {type(e).__name__}: {e}", flush=True)
        return {"label": label, "nodes": n_nodes, "pmjs": n_pmj, "stats": stats, "err": None}
    except Exception as e:  # noqa: BLE001
        print(f"[f5uvc] {label} FAILED: {type(e).__name__}: {e}", flush=True)
        return {
            "label": label,
            "nodes": 0,
            "pmjs": 0,
            "stats": stats,
            "err": f"{type(e).__name__}: {e}",
        }


def main():
    print("[f5uvc] loading Strocchi mesh + extracting endocardium...", flush=True)
    mesh = read_mesh(CASE)
    endo = extract_endocardium(mesh)
    results = [grow_one("lv", endo.lv_endo), grow_one("rv", endo.rv_endo)]
    (OUT / "f5_uvc_tree.json").write_text(json.dumps(results, indent=2))
    ok = all(r["pmjs"] > 0 for r in results)
    print(
        f"[f5uvc] {'PASS' if ok else 'PARTIAL/FAIL'}: {[(r['label'], r['pmjs']) for r in results]}",
        flush=True,
    )


if __name__ == "__main__":
    main()
