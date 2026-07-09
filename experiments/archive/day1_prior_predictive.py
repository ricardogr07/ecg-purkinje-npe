"""Day-1 Track S: prior-predictive check on crtdemo.

Draw theta from the provisional prior, run the forward model, and report:
  - tree-growth success rate (out-of-domain failures signal ranges too wide),
  - ECG finiteness + per-lead non-degeneracy,
  - a crude QRS-active width (fraction of the trace) as a physiology smell test.
Saves an overlay figure of the 12-lead vector magnitude across successful draws.

Run: uv run python experiments/day1_prior_predictive.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from core.theta import sample_prior, to_dict  # noqa: E402
from sim.forward import forward, load_geometry  # noqa: E402

N = 8
SEED = 0
OUT = Path(__file__).resolve().parents[1] / "outputs"


def _vector_magnitude(ecg: np.ndarray) -> np.ndarray:
    """Root sum of squares across the 12 leads, per time sample."""
    return np.sqrt((ecg**2).sum(axis=0))


def _qrs_active_frac(ecg: np.ndarray) -> float:
    mag = _vector_magnitude(ecg)
    return float((mag > 0.05 * mag.max()).sum()) / len(mag)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    thetas = sample_prior(N, rng)
    geom = load_geometry()

    ok, fails, qrs_fracs = 0, 0, []
    plt.figure(figsize=(9, 4))
    for i in range(N):
        td = to_dict(thetas[i])
        try:
            t = time.perf_counter()
            ecg = forward(td, geom)
            dt = time.perf_counter() - t
        except Exception as e:  # tree growth can go out of domain for wide draws
            fails += 1
            print(f"[{i}] FAIL {type(e).__name__}: {str(e)[:90]}")
            continue
        finite = bool(np.isfinite(ecg).all())
        min_var = float(np.var(ecg, axis=1).min())
        qf = _qrs_active_frac(ecg)
        ok += 1
        qrs_fracs.append(qf)
        print(
            f"[{i}] ok {dt:4.1f}s finite={finite} min_lead_var={min_var:.1e} "
            f"qrs_active_frac={qf:.2f}  cv={td['cv']:.2f} dIV={td['delta_iv']:+.0f} "
            f"ilLV={td['init_length_lv']:.0f} ilRV={td['init_length_rv']:.0f}"
        )
        plt.plot(_vector_magnitude(ecg), lw=0.9, alpha=0.8)

    print(f"\n[prior-predictive] success {ok}/{N}, failures {fails}/{N}")
    if qrs_fracs:
        q = np.array(qrs_fracs)
        print(
            f"[prior-predictive] QRS-active fraction: median {np.median(q):.2f} "
            f"range [{q.min():.2f}, {q.max():.2f}]"
        )

    plt.title(f"Prior-predictive 12-lead vector magnitude, {ok}/{N} draws (crtdemo)")
    plt.xlabel("sample")
    plt.ylabel("RSS across 12 leads (a.u.)")
    fig_path = OUT / "day1_prior_predictive_magnitude.png"
    plt.savefig(fig_path, dpi=120, bbox_inches="tight")
    print(f"[figure] {fig_path}")


if __name__ == "__main__":
    main()
