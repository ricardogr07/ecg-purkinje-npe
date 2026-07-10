"""F5 baseline: load the Strocchi case, extract the CURRENT endocardial surfaces, and measure the
defects (open boundary edges, non-manifold edges) that make purkinje-uv's UV parametrization reject
them. No FIMPY eikonal here, so memory-moderate (mesh load + surface ops only). Grounds the repair.

Run: .venv/Scripts/python.exe experiments/f5_endo_assess.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adapter.strocchi import extract_endocardium, read_mesh  # noqa: E402

CASE = Path(__file__).resolve().parents[1] / "data" / "01" / "01.case"


def measure(surf, label):
    tri = surf.triangulate().clean()
    b = tri.extract_feature_edges(
        boundary_edges=True, non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    nm = tri.extract_feature_edges(
        boundary_edges=False, non_manifold_edges=True, feature_edges=False, manifold_edges=False
    )
    closed = b.n_cells == 0 and nm.n_cells == 0
    print(
        f"[f5] {label}: points={tri.n_points} tris={tri.n_cells} "
        f"open_boundary_edges={b.n_cells} non_manifold_edges={nm.n_cells} "
        f"closed_2manifold={closed}",
        flush=True,
    )
    return tri


def main():
    print("[f5] loading Strocchi case (memory-moderate, no FIMPY)...", flush=True)
    mesh = read_mesh(CASE)
    print(f"[f5] mesh points={mesh.n_points} cells={mesh.n_cells}", flush=True)
    endo = extract_endocardium(mesh)
    measure(endo.lv_endo, "LV endo (current)")
    measure(endo.rv_endo, "RV endo (current)")
    print("[f5] DONE baseline", flush=True)


if __name__ == "__main__":
    main()
