"""F5 attempt 2: build the endocardial surface as a marching-tets ISOSURFACE of uvc_transmural
(0=endo, 1=epi) through the ventricular myocardium, which is a naturally closed/clean 2-manifold,
instead of the ragged point-threshold patch. Split LV/RV by uvc_intraventricular sign. Measure
topology and grow a FractalTree to count PMJs. No FIMPY (memory-moderate).

Run: .venv/Scripts/python.exe experiments/f5_iso.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import meshio  # noqa: E402
import numpy as np  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from adapter.strocchi import read_mesh  # noqa: E402

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


def grow_pmjs(surf, n_it=20):
    from purkinje_uv import FractalTree, FractalTreeParameters

    tri = surf.triangulate().clean()
    with tempfile.TemporaryDirectory() as td:
        obj = Path(td) / "s.obj"
        faces = np.asarray(tri.faces).reshape(-1, 4)[:, 1:]
        meshio.write_points_cells(str(obj), np.asarray(tri.points, float), [("triangle", faces)])
        pts = np.asarray(tri.points, float)
        _, nn = cKDTree(pts).query(pts[0], k=2)
        try:
            ft = FractalTree(
                params=FractalTreeParameters(
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
            )
            ft.grow_tree()
            return len(ft.end_nodes), None
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"


def main():
    print("[f5iso] loading mesh...", flush=True)
    mesh = read_mesh(CASE)
    from adapter.strocchi import _tag_array

    tags, _ = _tag_array(mesh, None)
    vent = mesh.extract_cells(np.flatnonzero(np.isin(tags, [1, 2]))).cell_data_to_point_data()
    for iso in (0.1, 0.2):
        vent.set_active_scalars("uvc_transmural")
        surf = vent.contour([iso]).clean().triangulate()
        if surf.n_points == 0:
            print(f"[f5iso] iso={iso}: empty contour", flush=True)
            continue
        iv = np.asarray(surf.point_data["uvc_intraventricular"])
        for label, mask in (("LV", iv < 0), ("RV", iv > 0)):
            ids = np.flatnonzero(mask)
            sub = (
                surf.extract_points(ids, adjacent_cells=False)
                .extract_surface()
                .clean()
                .connectivity("largest")
                .triangulate()
            )
            if sub.n_cells > 4000:
                try:
                    sub = sub.decimate_pro(1.0 - 4000 / sub.n_cells).clean().triangulate()
                except Exception as e:
                    print(
                        f"[f5iso] iso={iso} {label} decimate skipped: {type(e).__name__}",
                        flush=True,
                    )
            print(f"[f5iso] iso={iso} {label} {stats(sub)}", flush=True)
            n, err = grow_pmjs(sub)
            print(f"[f5iso] iso={iso} {label} PMJs={n} err={err}", flush=True)
    print("[f5iso] DONE", flush=True)


if __name__ == "__main__":
    main()
