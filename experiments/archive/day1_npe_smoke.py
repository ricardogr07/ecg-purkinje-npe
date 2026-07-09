"""Day-1 Track S: NPE smoke end-to-end on crtdemo (sim -> features -> sbi NPE -> posterior).

Real-ish settings at a reduced smoke budget: 6D provisional prior, mandatory 5% per-lead
waveform noise (brief 5.6), engineered features. Trains an amortized NPE, recovers a known
theta_star, and reports the per-parameter contraction (posterior_std / prior_std).

Run: uv run python experiments/day1_npe_smoke.py
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

from core.features import extract_features  # noqa: E402
from core.noise import DEFAULT_NOISE_FRAC, add_waveform_noise  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES, sample_prior, to_dict  # noqa: E402
from sim.forward import forward, load_geometry  # noqa: E402
from sim.sweep import run_sweep  # noqa: E402

N_SMOKE = 150
NOISE = DEFAULT_NOISE_FRAC
OUT = Path(__file__).resolve().parents[1] / "outputs"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    torch.manual_seed(0)  # reproducible NPE weights + batch order
    n_workers = min(os.cpu_count() or 2, 8)
    print(f"[sweep] N={N_SMOKE} noise_frac={NOISE} workers={n_workers}")
    t = time.perf_counter()
    theta, _x_clean, x_noised, n_draw = run_sweep(N_SMOKE, NOISE, n_workers, seed=0)
    print(
        f"[sweep] {theta.shape[0]}/{n_draw} succeeded in {time.perf_counter() - t:.0f}s; "
        f"feature dim = {x_noised.shape[1]}"
    )

    # Held-out truth: a RANDOM interior theta (not the rig's design preset), so recovery is
    # not circular. Inverse crime: x_o is simulated by the same forward + noise as training,
    # acceptable for a smoke; real calibration varies noise seeds and uses SBC across draws.
    rng = np.random.default_rng(123)
    geom = load_geometry()
    theta_star, x_o = None, None
    for cand in sample_prior(20, rng):
        try:
            ecg_star = forward(to_dict(cand), geom)
        except Exception:
            continue
        theta_star = np.asarray(cand, dtype=float)
        x_o = extract_features(add_waveform_noise(ecg_star, NOISE, rng))
        break
    assert x_o is not None, "no growable held-out theta found"

    from sbi.inference import NPE
    from sbi.utils import BoxUniform

    lo = torch.tensor([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], dtype=torch.float32)
    hi = torch.tensor([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], dtype=torch.float32)
    inf = NPE(prior=BoxUniform(low=lo, high=hi))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x_noised, dtype=torch.float32)
    )
    t = time.perf_counter()
    inf.train()
    print(f"[npe] trained in {time.perf_counter() - t:.0f}s")

    post = inf.build_posterior()
    samples = post.sample((2000,), x=torch.tensor(x_o, dtype=torch.float32)).numpy()
    assert np.isfinite(samples).all(), "posterior samples not finite"

    # Denominator = empirical std of the ACCEPTED training thetas (the truncated effective
    # prior), not the nominal box, so reject-and-resample does not understate contraction.
    prior_std = theta.std(axis=0)
    post_std = samples.std(axis=0)
    contraction = post_std / prior_std
    post_mean = samples.mean(axis=0)

    print("\n[contraction] post_std/prior_std (empirical prior); z = |mean-true|/post_std")
    for i, k in enumerate(THETA_NAMES):
        z = abs(post_mean[i] - theta_star[i]) / (post_std[i] + 1e-12)
        print(
            f"  {k:16s} contraction={contraction[i]:.2f}  post_mean={post_mean[i]:+.2f} "
            f"(true {theta_star[i]:+.2f}, z={z:.1f})"
        )

    order = np.argsort(contraction)
    plt.figure(figsize=(7, 3.5))
    plt.bar([THETA_NAMES[i] for i in order], contraction[order], color="#4C78A8")
    plt.axhline(1.0, ls="--", c="grey", lw=1)
    plt.ylabel("contraction (post/prior std)")
    plt.xticks(rotation=30, ha="right")
    plt.title(f"NPE smoke contraction (N={theta.shape[0]}, noise={NOISE})")
    plt.tight_layout()
    fig_path = OUT / "day1_npe_smoke_contraction.png"
    plt.savefig(fig_path, dpi=120)
    print(f"[figure] {fig_path}")
    print("\n[ok] NPE smoke end-to-end complete")


if __name__ == "__main__":
    main()
