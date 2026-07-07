"""First real (low-budget) identifiability snapshot on crtdemo + budget-adequacy check.

~1 hour of laptop compute: sweep ~1250 sims, train a features NPE, and produce the headline
artifacts at v0:
  - per-parameter contraction table (median over held-out observations, empirical prior),
  - degeneracy corner plot (the flow's joint posterior),
  - SBC rank check + TARP expected coverage (calibration),
  - contraction-vs-budget curve at 250/500/1000 sims (is 1k starved or plateauing?).

Run:        uv run python experiments/day2_snapshot.py
Dry run:    DRY=1 uv run python experiments/day2_snapshot.py   (tiny N, validates the path)
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from sbi.analysis import pairplot  # noqa: E402
from sbi.inference import NPE  # noqa: E402
from sbi.utils import BoxUniform  # noqa: E402

from calib.diagnostics import run_sbc_check, run_tarp_check  # noqa: E402
from core.noise import DEFAULT_NOISE_FRAC  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402
from sim.sweep import run_sweep  # noqa: E402

DRY = bool(int(os.getenv("DRY", "0")))
if DRY:
    N_TRAIN, N_CALIB, BUDGETS, N_POST, N_OBS = 24, 12, [12, 24], 30, 5
else:
    N_TRAIN, N_CALIB, BUDGETS, N_POST, N_OBS = 1000, 250, [250, 500, 1000], 200, 20

OUT = Path(__file__).resolve().parents[1] / "outputs"
_LO = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], dtype=np.float32)
_HI = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], dtype=np.float32)


def _train(theta, x):
    inf = NPE(prior=BoxUniform(low=torch.tensor(_LO), high=torch.tensor(_HI)))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train()
    return inf.build_posterior()


def _median_contraction(post, x_obs, prior_std, n=1000):
    """Median per-parameter contraction (post_std / prior_std) over several observations."""
    out = []
    for xo in x_obs:
        s = post.sample((n,), x=torch.tensor(xo, dtype=torch.float32), show_progress_bars=False)
        out.append(s.numpy().std(axis=0) / prior_std)
    return np.median(np.asarray(out), axis=0)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    torch.manual_seed(0)
    n_workers = min(os.cpu_count() or 2, 8)

    t = time.perf_counter()
    theta, _xc, x, n_draw = run_sweep(N_TRAIN + N_CALIB, DEFAULT_NOISE_FRAC, n_workers, seed=0)
    print(f"[sweep] {theta.shape[0]}/{n_draw} usable in {time.perf_counter() - t:.0f}s")

    m = theta.shape[0]
    n_tr = min(N_TRAIN, m - N_CALIB)
    th_tr, x_tr = theta[:n_tr], x[:n_tr]
    th_ca, x_ca = theta[n_tr:], x[n_tr:]
    prior_std = th_tr.std(axis=0)
    print(f"[split] train={n_tr} calib={th_ca.shape[0]}")

    # --- budget-adequacy curve: contraction vs training budget ---
    obs_idx = np.arange(min(N_OBS, th_ca.shape[0]))
    x_obs = [x_ca[i] for i in obs_idx]
    curve = {}
    post_full = None
    for b in [x for x in BUDGETS if x <= n_tr] or [n_tr]:
        post = _train(th_tr[:b], x_tr[:b])
        curve[b] = _median_contraction(post, x_obs, prior_std)
        print(
            f"[budget {b}] median contraction: "
            + ", ".join(f"{k}={curve[b][i]:.2f}" for i, k in enumerate(THETA_NAMES))
        )
        post_full = post
    b_full = max(curve)

    # --- headline contraction table (full model) ---
    print("\n[contraction table] median over held-out obs (post_std / empirical-prior_std)")
    for i, k in enumerate(THETA_NAMES):
        print(f"  {k:16s} {curve[b_full][i]:.2f}")

    # --- degeneracy corner plot for one held-out observation ---
    xo0 = x_ca[obs_idx[0]]
    s0 = post_full.sample(
        (2000,), x=torch.tensor(xo0, dtype=torch.float32), show_progress_bars=False
    )
    fig, _ = pairplot(
        s0,
        points=torch.tensor(th_ca[obs_idx[0]], dtype=torch.float32),
        labels=list(THETA_NAMES),
        limits=list(zip(_LO.tolist(), _HI.tolist(), strict=False)),
    )
    fig.savefig(OUT / "day2_corner.png", dpi=110, bbox_inches="tight")
    print(f"[figure] {OUT / 'day2_corner.png'}")

    # --- calibration: SBC + TARP coverage ---
    try:
        ranks, sbc = run_sbc_check(post_full, th_ca, x_ca, n_post=N_POST)
        print(f"\n[SBC] ks_pvals per param: {sbc.get('ks_pvals')}")
        fig, axes = plt.subplots(1, len(THETA_NAMES), figsize=(2 * len(THETA_NAMES), 2))
        for i, ax in enumerate(np.atleast_1d(axes)):
            ax.hist(ranks[:, i], bins=10, color="#4C78A8")
            ax.set_title(THETA_NAMES[i], fontsize=7)
            ax.set_yticks([])
        fig.suptitle(f"SBC rank histograms (flat = calibrated), N={th_ca.shape[0]}")
        fig.savefig(OUT / "day2_sbc.png", dpi=110, bbox_inches="tight")
        print(f"[figure] {OUT / 'day2_sbc.png'}")
    except Exception as e:
        print(f"[SBC] skipped: {type(e).__name__}: {e}")

    try:
        tarp = run_tarp_check(post_full, th_ca, x_ca, n_post=N_POST)
        print(f"[TARP] ATC={tarp['atc']:+.3f} (0 = calibrated), KS p={tarp['ks_pval']:.3f}")
        plt.figure(figsize=(4, 4))
        plt.plot([0, 1], [0, 1], "--", c="grey", lw=1)
        plt.plot(tarp["alpha"], tarp["ecp"], color="#E45756")
        plt.xlabel("credibility level")
        plt.ylabel("expected coverage")
        plt.title(f"TARP coverage (ATC={tarp['atc']:+.3f})")
        plt.savefig(OUT / "day2_tarp.png", dpi=110, bbox_inches="tight")
        print(f"[figure] {OUT / 'day2_tarp.png'}")
    except Exception as e:
        print(f"[TARP] skipped: {type(e).__name__}: {e}")

    # --- budget curve figure ---
    plt.figure(figsize=(6, 4))
    bs = sorted(curve)
    for i, k in enumerate(THETA_NAMES):
        plt.plot(bs, [curve[b][i] for b in bs], marker="o", label=k)
    plt.xlabel("training sims")
    plt.ylabel("median contraction")
    plt.title("Contraction vs budget (flattening = enough sims)")
    plt.legend(fontsize=7)
    plt.savefig(OUT / "day2_budget_curve.png", dpi=110, bbox_inches="tight")
    print(f"[figure] {OUT / 'day2_budget_curve.png'}")
    print("\n[ok] snapshot complete")


if __name__ == "__main__":
    main()
