"""F6 gate (HARD): prove the cached metric-swap set_fiber_cv produces a BIT-IDENTICAL activation
field to a full FIMPY rebuild, on crtdemo. If it is not bit-identical, the F6 change is a different
forward operator and must be reverted (the crtdemo honest 7D result was produced on the rebuild
path).

Run: .venv/Scripts/python.exe experiments/f6_gate.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
from fimpy.solver import FIMPY  # noqa: E402

from sim.forward import load_geometry  # noqa: E402


def main():
    geom = load_geometry()  # crtdemo; FIM solver built once in __init__
    xyz = np.asarray(geom.xyz, float)
    npts = xyz.shape[0]
    idx = np.array([0, npts // 4, npts // 2, (3 * npts) // 4])
    x0 = xyz[idx]
    x0_vals = np.zeros(x0.shape[0])
    cv = 0.5

    # cached path: F6 set_fiber_cv overwrites self.fim.metrics in place (no rebuild)
    geom.set_fiber_cv(cv)
    a_cached = np.asarray(geom.activate_fim(x0, x0_vals), float).copy()

    # rebuild path: force a full create_fim_solver at the same scaled D
    geom.D = geom._D_base * (cv / geom._cv_fiber_base) ** 2
    geom.fim = FIMPY.create_fim_solver(geom.xyz, geom.cells, geom.D, device=geom.device)
    a_rebuild = np.asarray(geom.activate_fim(x0, x0_vals), float).copy()

    ident = np.array_equal(a_cached, a_rebuild)
    print(f"[f6gate] shapes cached={a_cached.shape} rebuild={a_rebuild.shape}", flush=True)
    print(f"[f6gate] max_abs_diff={np.abs(a_cached - a_rebuild).max():.3e}", flush=True)
    print(f"[f6gate] BIT-IDENTICAL={ident}", flush=True)
    print("[f6gate] PASS" if ident else "[f6gate] FAIL: revert F6", flush=True)


if __name__ == "__main__":
    main()
