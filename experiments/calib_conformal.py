"""Apply per-parameter conformal recalibration to the features NPE and report the honest
(calibrated) contraction spectrum: SBC ks + central coverage + contraction, before vs after.

Trains the NPE on a sweep checkpoint, fits inflation on a held-out calibration split, and
recalibrates. Parametrized by checkpoint path (CKPT_PATH env), so it runs now against the
existing [-40,40] sweep and re-points at the fresh [-90,40] sweep once that lands.

Run:   uv run python experiments/calib_conformal.py
       CKPT_PATH=outputs/day3_sweep_ckpt.npz uv run python experiments/calib_conformal.py
       DRY=1 ... for a tiny check
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

from calib.conformal import (  # noqa: E402
    central_coverage,
    draw_sample_sets,
    fit_inflation,
    sbc_ks_pvals,
)
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402

DRY = bool(int(os.getenv("DRY", "0")))
OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = Path(os.getenv("CKPT_PATH", str(OUT / "day2_sweep_ckpt.npz")))
RESULTS = OUT / "calib_conformal_results.txt"
N_TRAIN = 60 if DRY else 1000
N_CALIB = 30 if DRY else 250
N_POST = 100 if DRY else 300
LEVEL = 0.9
_LO = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], np.float32)
_HI = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], np.float32)


def emit(s: str) -> None:
    print(s, flush=True)
    with open(RESULTS, "a") as f:
        f.write(s + "\n")


def train_npe(theta, x, seed=0):
    torch.manual_seed(seed)
    inf = NPE(prior=BoxUniform(low=torch.tensor(_LO), high=torch.tensor(_HI)))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train()
    return inf.build_posterior()


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
    prior_std = th_tr.std(axis=0)
    emit(f"[data] ckpt={CKPT.name} train={n_tr} calib={len(th_ca)}")

    post = train_npe(th_tr, x_tr)
    sets = draw_sample_sets(post, x_ca, N_POST)  # (M, N, D)

    t = fit_inflation(th_ca, sets)
    ks0 = sbc_ks_pvals(th_ca, sets, np.ones(6))
    ks1 = sbc_ks_pvals(th_ca, sets, t)
    cov0 = central_coverage(th_ca, sets, np.ones(6), LEVEL)
    cov1 = central_coverage(th_ca, sets, t, LEVEL)
    contr0 = np.median(sets.std(axis=1), axis=0) / prior_std
    contr1 = t * contr0

    emit("\n[per-parameter recalibration]  t = fitted inflation")
    emit(
        f"  {'param':16s} {'t':>5s} {'ks_before':>10s} {'ks_after':>9s} "
        f"{'cov_before':>11s} {'cov_after':>10s} {'contr_before':>13s} {'contr_after':>12s}"
    )
    for i, k in enumerate(THETA_NAMES):
        emit(
            f"  {k:16s} {t[i]:5.2f} {ks0[i]:10.3f} {ks1[i]:9.3f} "
            f"{cov0[i]:11.3f} {cov1[i]:10.3f} {contr0[i]:13.2f} {contr1[i]:12.2f}"
        )
    emit(
        f"\n[calibrated?] SBC ks median before={np.median(ks0):.3f} after={np.median(ks1):.3f} "
        f"(want > 0.05).  central-{int(LEVEL * 100)}% coverage want ~{LEVEL:.2f}"
    )

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    xpos = np.arange(6)
    ax[0].bar(xpos, t, color="#4C78A8")
    ax[0].axhline(1.0, ls="--", c="grey")
    ax[0].set_xticks(xpos)
    ax[0].set_xticklabels(THETA_NAMES, rotation=40, ha="right", fontsize=7)
    ax[0].set_ylabel("inflation t_d")
    ax[0].set_title("Per-parameter conformal inflation")
    w = 0.38
    ax[1].bar(xpos - w / 2, ks0, w, label="before", color="#E45756")
    ax[1].bar(xpos + w / 2, ks1, w, label="after", color="#54A24B")
    ax[1].axhline(0.05, ls="--", c="grey", label="calibrated threshold")
    ax[1].set_xticks(xpos)
    ax[1].set_xticklabels(THETA_NAMES, rotation=40, ha="right", fontsize=7)
    ax[1].set_ylabel("SBC ks p-value")
    ax[1].set_title("Calibration before vs after")
    ax[1].legend(fontsize=7)
    fig.savefig(OUT / "calib_conformal.png", dpi=120, bbox_inches="tight")
    emit(f"[figure] {OUT / 'calib_conformal.png'}")
    emit("[ok] conformal recalibration complete")


if __name__ == "__main__":
    main()
