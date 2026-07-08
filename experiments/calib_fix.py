"""B: inference-side calibration fixes. Does post-hoc variance inflation or an NPE ensemble
calibrate the overconfident posterior? Reuses the 1250-sim checkpoint (no re-simulation).

Post-hoc inflation directly tests "right location, too narrow": if inflating the posterior
spread by a factor t makes SBC ranks uniform, the flow is simply overconfident by ~t.

Run:  uv run python experiments/calib_fix.py    |    DRY=1 for a tiny check
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
from scipy.stats import kstest  # noqa: E402

from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402

DRY = bool(int(os.getenv("DRY", "0")))
OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = OUT / "day2_sweep_ckpt.npz"
RESULTS = OUT / "calib_fix_results.txt"
N_TRAIN = 60 if DRY else 1000
N_CALIB = 30 if DRY else 250
N_POST = 100 if DRY else 300
N_ENS = 2 if DRY else 5
INFL = [1.0, 1.3, 1.6, 2.0, 2.5]
_LO = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], np.float32)
_HI = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], np.float32)


def emit(s: str) -> None:
    print(s, flush=True)
    with open(RESULTS, "a") as f:
        f.write(s + "\n")


def train_npe(theta, x, seed):
    torch.manual_seed(seed)
    inf = NPE(prior=BoxUniform(low=torch.tensor(_LO), high=torch.tensor(_HI)))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train()
    return inf.build_posterior()


def post_samples(post, x, n):
    return post.sample(
        (n,), x=torch.tensor(x, dtype=torch.float32), show_progress_bars=False
    ).numpy()


def ks_median(ranks, n_post):
    p = [kstest(ranks[:, d] / n_post, "uniform").pvalue for d in range(ranks.shape[1])]
    return float(np.median(p))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    RESULTS.write_text("")
    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    m = theta.shape[0]
    n_tr = min(N_TRAIN, m - N_CALIB)
    th_tr, x_tr = theta[:n_tr], x[:n_tr]
    th_ca, x_ca = theta[n_tr : n_tr + N_CALIB], x[n_tr : n_tr + N_CALIB]
    emit(f"[data] train={n_tr} calib={len(th_ca)}")

    base = train_npe(th_tr, x_tr, 0)
    samples = [post_samples(base, x_ca[i], N_POST) for i in range(len(th_ca))]

    emit("[post-hoc variance inflation] t: SBC ks median (calibrated if > 0.05)")
    infl_rows = []
    for t in INFL:
        ranks = np.zeros((len(th_ca), 6), int)
        for i, s in enumerate(samples):
            mu = s.mean(0)
            ranks[i] = ((mu + t * (s - mu)) < th_ca[i]).sum(0)
        k = ks_median(ranks, N_POST)
        infl_rows.append((t, k))
        emit(f"  t={t:.1f}: ks={k:.3f}")

    posts = [train_npe(th_tr, x_tr, seed) for seed in range(N_ENS)]
    per = max(1, N_POST // N_ENS)
    ranks = np.zeros((len(th_ca), 6), int)
    for i in range(len(th_ca)):
        s = np.vstack([post_samples(p, x_ca[i], per) for p in posts])
        ranks[i] = (s < th_ca[i]).sum(0)
    k_ens = ks_median(ranks, per * N_ENS)
    emit(f"[ensemble of {N_ENS}] SBC ks median = {k_ens:.3f}")

    ts = [r[0] for r in infl_rows]
    kss = [r[1] for r in infl_rows]
    plt.figure(figsize=(5, 3.5))
    plt.axhline(0.05, ls="--", c="grey", label="calibrated threshold")
    plt.plot(ts, kss, "o-", color="#4C78A8")
    plt.xlabel("posterior variance inflation t")
    plt.ylabel("SBC ks median")
    plt.title("Post-hoc calibration: inflation vs SBC")
    plt.legend()
    plt.savefig(OUT / "calib_fix_inflation.png", dpi=120, bbox_inches="tight")
    emit(f"[figure] {OUT / 'calib_fix_inflation.png'}")
    emit("[ok] calib fix complete")


if __name__ == "__main__":
    main()
