"""T2: Purkinje network variation on crtdemo.

Generate distinct networks by varying the fractal-tree seed nodes at fixed (reference) theta,
compute each 12-lead ECG, and report:
  - the per-lead ECG spread across networks (the honest observation-noise floor),
  - each network's fidelity vs the ground-truth True_ecg (morphology correlation + nrmse),
  - a non-uniqueness read: do genuinely distinct networks give similar ECGs?

Run:      uv run python experiments/network_variation.py
Dry run:  DRY=1 uv run python experiments/network_variation.py
"""

import os
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from sim.forward import (  # noqa: E402
    DATA_DIR,
    LV_ENDO,
    REFERENCE_THETA,
    RV_ENDO,
    forward,
    load_geometry,
    sample_valid_seeds,
)

DRY = bool(int(os.getenv("DRY", "0")))
K = 3 if DRY else 16
L = 256  # common resample length
OUT = Path(__file__).resolve().parents[1] / "outputs"
RESULTS = OUT / "network_variation_results.txt"


def emit(s: str) -> None:
    print(s, flush=True)
    with open(RESULTS, "a") as f:
        f.write(s + "\n")


def _resample(ecg: np.ndarray) -> np.ndarray:
    xp = np.linspace(0, 1, ecg.shape[1])
    xq = np.linspace(0, 1, L)
    return np.vstack([np.interp(xq, xp, ecg[i]) for i in range(ecg.shape[0])])


def _norm(sig: np.ndarray) -> np.ndarray:
    m = sig.mean(axis=1, keepdims=True)
    s = sig.std(axis=1, keepdims=True) + 1e-12
    return (sig - m) / s


def _fidelity(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Morphology correlation (mean per-lead) and normalized RMSE between two (12, L) ECGs."""
    an, bn = _norm(a), _norm(b)
    corr = float(np.mean([np.corrcoef(an[i], bn[i])[0, 1] for i in range(12)]))
    rmse = float(np.sqrt(np.mean((an - bn) ** 2)))
    return corr, rmse


def _forward_net(theta, geom, sl, sr, scales=(1.0, 0.7, 0.5, 0.35)):
    """forward with grow-retry: shrink init_length on out-of-domain growth (notebook pattern)."""
    for s in scales:
        t = dict(theta)
        t["init_length_lv"] *= s
        t["init_length_rv"] *= s
        try:
            return forward(t, geom, seeds_lv=sl, seeds_rv=sr)
        except Exception:
            continue
    return None


def main() -> None:
    OUT.mkdir(exist_ok=True)
    RESULTS.write_text("")
    rng = np.random.default_rng(0)
    geom = load_geometry()

    with open(DATA_DIR / "nb" / "True_ecg", "rb") as f:
        rec = pickle.load(f)
    true = np.vstack([np.asarray(rec[n], float) for n in rec.dtype.names])
    true_L = _resample(true)
    emit(f"[true] loaded True_ecg shape={true.shape}")

    ref = forward(REFERENCE_THETA, geom)
    ref_L = _resample(ref)
    c, r = _fidelity(ref_L, true_L)
    emit(f"[reference network] fidelity vs True_ecg: corr={c:.3f} nrmse={r:.3f}")

    lv_seeds = sample_valid_seeds(LV_ENDO, K, rng)
    rv_seeds = sample_valid_seeds(RV_ENDO, K, rng)
    ecgs: list[np.ndarray] = []
    fids: list[tuple[float, float, int]] = []
    t0 = time.perf_counter()
    for k in range(K):
        e = _forward_net(REFERENCE_THETA, geom, lv_seeds[k], rv_seeds[k])
        if e is None:
            emit(f"[net {k}] grow fail (all scales)")
            continue
        eL = _resample(e)
        ecgs.append(eL)
        cc, rr = _fidelity(eL, true_L)
        fids.append((cc, rr, k))
    emit(f"[networks] {len(ecgs)}/{K} grew in {time.perf_counter() - t0:.0f}s")
    if len(ecgs) < 2:
        emit("[abort] need at least 2 networks")
        return

    stack = np.stack(ecgs)  # (n, 12, L)
    per_lead_std = stack.std(axis=0).mean(axis=1)  # (12,)
    per_lead_amp = np.abs(stack).mean(axis=(0, 2)) + 1e-12  # (12,)
    spread_frac = float(np.mean(per_lead_std / per_lead_amp))
    emit(
        f"[noise floor] network-induced ECG spread = {spread_frac * 100:.1f}% of amplitude "
        f"(current noise assumption is 5%)"
    )

    corrs = np.array(
        [_fidelity(ecgs[i], ecgs[j])[0] for i in range(len(ecgs)) for j in range(i + 1, len(ecgs))]
    )
    emit(
        f"[non-uniqueness] pairwise morphology corr across distinct networks: "
        f"median={np.median(corrs):.3f} range=[{corrs.min():.3f}, {corrs.max():.3f}]"
    )
    emit("  (high corr across genuinely different networks = topology hard to read from the ECG)")

    fids_sorted = sorted(fids, key=lambda x: -x[0])
    emit(f"[best match vs True_ecg] corr={fids_sorted[0][0]:.3f} (net {fids_sorted[0][2]})")

    plt.figure(figsize=(9, 4))
    plt.plot(_norm(true_L)[1], "k", lw=2, label="True_ecg")
    plt.plot(_norm(ref_L)[1], "b--", lw=1.5, label="reference net")
    for e in ecgs[:8]:
        plt.plot(_norm(e)[1], color="grey", lw=0.6, alpha=0.6)
    plt.title(f"Network variation vs True_ecg (one lead), {len(ecgs)} nets")
    plt.legend()
    plt.xlabel("resampled sample")
    plt.savefig(OUT / "network_variation.png", dpi=120, bbox_inches="tight")
    emit(f"[figure] {OUT / 'network_variation.png'}")
    emit("[ok] network variation complete")


if __name__ == "__main__":
    main()
