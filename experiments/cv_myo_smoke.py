"""De-risk the cv_myo (Contract A param 7) plumbing before the 7D flip.

Checks, on crtdemo at REFERENCE_THETA:
  1. set_fiber_cv rescales the diffusion tensor exactly by (cv/cv_base)**2 (pure-math, cheap).
  2. cv_myo materially changes the 12-lead ECG (the eikonal, hence the observation, moves).
  3. Physics sanity: a slower myocardium (lower cv_myo) widens the QRS active window.
Also records the per-call set_fiber_cv (FIM-rebuild) wall cost, which sets the 7D sweep budget.

Run:  uv run python experiments/cv_myo_smoke.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from sim.forward import REFERENCE_THETA, forward, load_geometry  # noqa: E402

LOG = Path(__file__).resolve().parents[1] / "outputs" / "grind_log.txt"


def emit(s: str) -> None:
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write(s + "\n")


def _qrs_width_frac(ecg: np.ndarray) -> float:
    """Active-window width as a fraction of T: samples where the 12-lead RSS exceeds 5% of peak."""
    mag = np.sqrt((np.asarray(ecg, float) ** 2).sum(axis=0))
    return float((mag > 0.05 * mag.max()).sum()) / mag.shape[0]


def main() -> None:
    geom = load_geometry()
    base_cv = geom._cv_fiber_base
    emit(f"[cv_myo smoke] mesh longitudinal fiber CV base = {base_cv:.4f} m/s")

    # (1) exact tensor rescale, no solve needed
    for c in (0.5, 0.67, 1.0):
        t0 = time.perf_counter()
        geom.set_fiber_cv(c)
        dt = time.perf_counter() - t0
        got = float(np.median(geom.D / geom._D_base))
        want = (c / base_cv) ** 2
        assert abs(got - want) < 1e-9, f"D scale {got} != {want} at cv_myo={c}"
        emit(f"[cv_myo smoke] cv_myo={c:.2f}: D-scale ok ({got:.4f}); set_fiber_cv wall {dt:.3f}s")

    # (2)+(3) cv_myo moves the ECG; slower myocardium widens QRS
    theta = dict(REFERENCE_THETA)
    ecgs, widths = {}, {}
    for c in (0.5, 0.67, 1.0):
        theta["cv_myo"] = c
        t0 = time.perf_counter()
        ecg = forward(theta, geom)
        ft = time.perf_counter() - t0
        ecgs[c], widths[c] = ecg, _qrs_width_frac(ecg)
        emit(f"[cv_myo smoke] cv_myo={c:.2f}: forward {ft:.1f}s, qrs_active_frac={widths[c]:.3f}")

    rel = float(np.linalg.norm(ecgs[0.5] - ecgs[1.0]) / (np.linalg.norm(ecgs[1.0]) + 1e-12))
    emit(f"[cv_myo smoke] relative ECG L2 diff (cv_myo 0.5 vs 1.0) = {rel:.3f}")
    assert rel > 0.02, "cv_myo does not move the ECG; plumbing is a no-op"
    assert widths[0.5] >= widths[1.0] - 1e-6, "slower myocardium should not narrow the QRS window"
    emit("[cv_myo smoke] OK: cv_myo is a live, physically-sane forward input")


if __name__ == "__main__":
    main()
