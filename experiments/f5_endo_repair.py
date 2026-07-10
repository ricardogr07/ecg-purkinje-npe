"""F5 endo repair: turn the ragged Strocchi endocardial patch into a clean, parametrizable open
surface so purkinje-uv grows a full Purkinje tree (PMJ count in the tens-to-hundreds, not 4).

Repair = largest connected component -> fill spurious interior holes -> decimate to a tractable
resolution -> clean/triangulate. Reports current-vs-repaired surface topology AND the PMJ count from
actually growing a FractalTree on each. No FIMPY eikonal, so memory-moderate.

Run: .venv/Scripts/python.exe experiments/f5_endo_repair.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import meshio  # noqa: E402
import numpy as np  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from adapter.strocchi import extract_endocardium, read_mesh  # noqa: E402

CASE = Path(__file__).resolve().parents[1] / "data" / "01" / "01.case"


def stats(s):
    b = s.extract_feature_edges(
        boundary_edges=True, non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    nm = s.extract_feature_edges(
        boundary_edges=False, non_manifold_edges=True, feature_edges=False, manifold_edges=False
    )
    nreg = len(np.unique(s.connectivity("all")["RegionId"]))
    return (
        f"pts={s.n_points} tris={s.n_cells} open_edges={b.n_cells} "
        f"nonman={nm.n_cells} regions={nreg}"
    )


def repair(surf, target_tris=4000, hole_size=8.0):
    s = surf.triangulate().clean().connectivity("largest")
    s = s.fill_holes(hole_size).clean().triangulate()
    if s.n_cells > target_tris:
        s = s.decimate(1.0 - target_tris / s.n_cells).clean().triangulate()
    return s


def grow_pmjs(surf, label, n_it=20):
    from purkinje_uv import FractalTree, FractalTreeParameters

    tri = surf.triangulate().clean()
    with tempfile.TemporaryDirectory() as td:
        obj = Path(td) / f"{label}.obj"
        faces = np.asarray(tri.faces).reshape(-1, 4)[:, 1:]
        meshio.write_points_cells(str(obj), np.asarray(tri.points, float), [("triangle", faces)])
        pts = np.asarray(tri.points, float)
        _, nn = cKDTree(pts).query(pts[0], k=2)
        try:
            params = FractalTreeParameters(
                meshfile=str(obj),
                init_node_id=0,
                second_node_id=int(nn[1]),
                init_length=8.0,
                length=8.0,
                w=0.1,
                l_segment=1.0,
                fascicles_length=[],
                fascicles_angles=[],
                branch_angle=0.175,
                N_it=n_it,
            )
            ft = FractalTree(params=params)
            ft.grow_tree()
            return len(ft.end_nodes), None
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"


def main():
    print("[f5r] loading mesh...", flush=True)
    mesh = read_mesh(CASE)
    endo = extract_endocardium(mesh)
    for label, surf in (("LV", endo.lv_endo), ("RV", endo.rv_endo)):
        cur = surf.triangulate().clean()
        print(f"[f5r] {label} CURRENT  {stats(cur)}", flush=True)
        n_cur, err_cur = grow_pmjs(cur, f"{label}_cur")
        print(f"[f5r] {label} CURRENT  PMJs={n_cur} err={err_cur}", flush=True)
        rep = repair(surf)
        print(f"[f5r] {label} REPAIRED {stats(rep)}", flush=True)
        n_rep, err_rep = grow_pmjs(rep, f"{label}_rep")
        print(f"[f5r] {label} REPAIRED PMJs={n_rep} err={err_rep}", flush=True)
    print("[f5r] DONE", flush=True)


if __name__ == "__main__":
    main()
