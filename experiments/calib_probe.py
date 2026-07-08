"""T3: calibration hypothesis probe. Does honest (larger) observation noise fix overconfidence?

Reuses the existing 1250-sim checkpoint (outputs/day2_sweep_ckpt.npz): clean features + theta,
so NO re-simulation. Sweeps feature-level Gaussian noise at f x per-feature-std, retrains the
NPE at each f, and reports SBC ks + TARP ATC. If calibration improves as noise grows toward the
network-induced spread (T2), the overconfidence was a too-small-noise artifact.

Run:  uv run python experiments/calib_probe.py
Dry:  DRY=1 uv run python experiments/calib_probe.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from sbi.inference import NPE  # noqa: E402
from sbi.utils import BoxUniform  # noqa: E402

from calib.diagnostics import run_sbc_check, run_tarp_check  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402

DRY = bool(int(os.getenv("DRY", "0")))
OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = OUT / "day2_sweep_ckpt.npz"
RESULTS = OUT / "calib_probe_results.txt"
NOISE_GRID = [0.2, 0.6] if DRY else [0.05, 0.15, 0.30, 0.50, 0.80]
N_TRAIN = 60 if DRY else 1000
N_CALIB = 30 if DRY else 250
N_POST = 30 if DRY else 200

_LO = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], dtype=np.float32)
_HI = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], dtype=np.float32)


def emit(s: str) -> None:
    print(s, flush=True)
    with open(RESULTS, "a") as f:
        f.write(s + "\n")


def _train(theta, x):
    inf = NPE(prior=BoxUniform(low=torch.tensor(_LO), high=torch.tensor(_HI)))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train()
    return inf.build_posterior()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    RESULTS.write_text("")
    torch.manual_seed(0)

    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x_clean = np.array(d["x_clean"], float)
    emit(f"[data] reused checkpoint: theta{theta.shape} x_clean{x_clean.shape}")

    m = theta.shape[0]
    n_tr = min(N_TRAIN, m - N_CALIB)
    feat_std = x_clean[:n_tr].std(axis=0) + 1e-9

    emit("[noise sweep] calibrated target: SBC ks median > 0.05 and TARP ATC near 0")
    rows = []
    for f in NOISE_GRID:
        rng = np.random.default_rng(1)
        xn = x_clean + rng.normal(scale=f * feat_std, size=x_clean.shape)
        th_tr, x_tr = theta[:n_tr], xn[:n_tr]
        th_ca, x_ca = theta[n_tr : n_tr + N_CALIB], xn[n_tr : n_tr + N_CALIB]
        post = _train(th_tr, x_tr)
        try:
            _, sbc = run_sbc_check(post, th_ca, x_ca, n_post=N_POST)
            ks = float(np.median(sbc.get("ks_pvals", [np.nan])))
        except Exception as e:
            ks = float("nan")
            emit(f"  (sbc err {type(e).__name__})")
        try:
            atc = run_tarp_check(post, th_ca, x_ca, n_post=N_POST)["atc"]
        except Exception:
            atc = float("nan")
        rows.append((f, ks, atc))
        emit(f"  f={f:.2f}: SBC ks median={ks:.3f}, TARP ATC={atc:+.3f}")

    fs = [r[0] for r in rows]
    kss = [r[1] for r in rows]
    plt.figure(figsize=(5, 3.5))
    plt.axhline(0.05, ls="--", c="grey", label="calibrated threshold")
    plt.plot(fs, kss, "o-", color="#4C78A8")
    plt.xlabel("feature noise (fraction of feature std)")
    plt.ylabel("SBC ks p-value (median)")
    plt.title("Calibration vs observation-noise level")
    plt.legend()
    plt.savefig(OUT / "calib_probe_noise.png", dpi=120, bbox_inches="tight")
    emit(f"[figure] {OUT / 'calib_probe_noise.png'}")
    emit("[ok] calib probe complete")


if __name__ == "__main__":
    main()
