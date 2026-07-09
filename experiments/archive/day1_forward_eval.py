"""Day-1 Track S de-risk: forward-eval benchmark + determinism test on crtdemo.

Run: uv run python experiments/day1_forward_eval.py

Reports:
  - one-time geometry setup cost (MyocardialMesh build),
  - per-theta forward-eval time (median) -> sets the simulation budget,
  - determinism: same theta twice, diff the ECG (brief 5.5/5.6 gate).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from sim.forward import REFERENCE_THETA, forward, load_geometry  # noqa: E402


def main() -> None:
    t0 = time.perf_counter()
    geom = load_geometry()
    setup_s = time.perf_counter() - t0
    print(f"[setup] MyocardialMesh(crtdemo) built in {setup_s:.2f}s (one-time per geometry)")

    times, ecgs = [], []
    for i in range(3):
        t = time.perf_counter()
        ecg = forward(REFERENCE_THETA, geom)
        dt = time.perf_counter() - t
        times.append(dt)
        ecgs.append(ecg)
        print(f"[forward {i}] {dt:.2f}s  ecg shape={ecg.shape}")

    per_theta = float(np.median(times))
    print(f"\n[benchmark] per-theta forward-eval median = {per_theta:.2f}s")
    for budget in (2000, 5000, 10000):
        print(f"  budget {budget:>6}: ~{per_theta * budget / 3600:.2f} core-hours (serial)")

    d = float(np.max(np.abs(ecgs[0] - ecgs[1])))
    denom = float(np.max(np.abs(ecgs[0]))) + 1e-12
    print(f"\n[determinism] max|ecg_run0 - ecg_run1| = {d:.3e} (rel {d / denom:.3e})")
    if d < 1e-9:
        print("[determinism] DETERMINISTIC -> observation-noise model MANDATORY (brief 5.6)")
    else:
        print("[determinism] NON-deterministic -> nuisance-latent treatment (brief 5.5)")

    assert np.isfinite(ecgs[0]).all(), "ECG has non-finite values"
    print("\n[ok] forward eval + determinism check complete")


if __name__ == "__main__":
    main()
