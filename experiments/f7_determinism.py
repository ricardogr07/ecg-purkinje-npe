"""F7: eikonal determinism on the Strocchi mesh. Build the Strocchi MyocardialMesh, run the FIM
eikonal twice from the same seeds (using the F6 cached set_fiber_cv), and assert the activation is
bit-identical (guards against FP nondeterminism from threaded reductions on the larger mesh). This
does NOT need a valid Purkinje tree (F5), only seed points on the mesh. Memory-heavy (full-mesh
FIMPY build); run monitored.

Run: .venv/Scripts/python.exe experiments/f7_determinism.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from adapter.strocchi import load_geometry as load_strocchi  # noqa: E402


def main():
    print("[f7] building Strocchi geom (memory-heavy: FIMPY on the full mesh)...", flush=True)
    geom = load_strocchi()
    xyz = np.asarray(geom.xyz, float)
    npts = xyz.shape[0]
    print(f"[f7] geom built; npts={npts}", flush=True)
    idx = np.array([0, npts // 4, npts // 2, (3 * npts) // 4])
    x0 = xyz[idx]
    x0_vals = np.zeros(x0.shape[0])
    geom.set_fiber_cv(0.5)
    a1 = np.asarray(geom.activate_fim(x0, x0_vals), float).copy()
    a2 = np.asarray(geom.activate_fim(x0, x0_vals), float).copy()
    ident = np.array_equal(a1, a2)
    print(
        f"[f7] activation npts={a1.shape[0]} bit_identical_twice={ident} "
        f"max_abs_diff={np.abs(a1 - a2).max():.3e}",
        flush=True,
    )
    print("[f7] PASS" if ident else "[f7] FAIL: eikonal nondeterministic on Strocchi", flush=True)


if __name__ == "__main__":
    main()
