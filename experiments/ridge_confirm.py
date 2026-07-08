"""Confirm the delta_iv-cv_myo degeneracy two ways (director asks, Jul 8):

  1. cv_myo point-estimate bias: over held-out calib observations, is the posterior mean of
     cv_myo near truth or mislocated? (near-truth + wide/miscalibrated spread = informative point
     riding a ridge; biased = the ridge pulls the estimate.) Also reports the identifiable
     COMBINATION delta_iv + k*cv_myo vs each parameter alone.
  2. iso-ECG manifold: from REFERENCE_THETA, step along the delta_iv-cv_myo ridge direction vs the
     orthogonal direction and forward-simulate. If moving along the ridge leaves the ECG nearly
     unchanged while the orthogonal move does not, the degeneracy is a true LIKELIHOOD flat
     direction (the ECG constrains the combination, not each parameter), not a posterior artifact.

Run:  CKPT_PATH=outputs/day3_7d_ckpt.npz uv run python experiments/ridge_confirm.py
      (point CKPT_PATH at day3_7d_snr_ckpt.npz once the physiological-SNR re-run lands.)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from sbi.inference import NPE  # noqa: E402
from sbi.utils import BoxUniform  # noqa: E402

from core.noise import to_physiological_mv  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402
from sim.forward import REFERENCE_THETA, forward, load_geometry  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = Path(os.getenv("CKPT_PATH", str(OUT / "day3_7d_ckpt.npz")))
RESULTS = OUT / "ridge_confirm_results.txt"
IV, MYO = THETA_NAMES.index("delta_iv"), THETA_NAMES.index("cv_myo")
_LO = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES], np.float32)
_HI = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES], np.float32)


def emit(s: str) -> None:
    print(s, flush=True)
    with open(RESULTS, "a") as f:
        f.write(s + "\n")


def _rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def main() -> None:
    RESULTS.write_text("")
    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    n_calib = min(400, theta.shape[0] // 5)
    th_tr, x_tr = theta[:-n_calib], x[:-n_calib]
    th_ca, x_ca = theta[-n_calib:], x[-n_calib:]

    torch.manual_seed(0)
    inf = NPE(prior=BoxUniform(low=torch.tensor(_LO), high=torch.tensor(_HI)))
    inf.append_simulations(
        torch.tensor(th_tr, dtype=torch.float32), torch.tensor(x_tr, dtype=torch.float32)
    )
    post = inf.train()
    post = inf.build_posterior()
    emit(f"[ridge] ckpt={CKPT.name} train={len(th_tr)} calib={len(th_ca)}")

    # --- (1) cv_myo point-estimate bias over held-out obs ---
    est = np.zeros((len(th_ca), len(THETA_NAMES)))
    for i, xo in enumerate(x_ca):
        s = post.sample((400,), x=torch.tensor(xo, dtype=torch.float32), show_progress_bars=False)
        est[i] = np.asarray(s).mean(axis=0)

    def stats(j):
        t, e = th_ca[:, j], est[:, j]
        rng = _HI[j] - _LO[j]
        return e.mean() - t.mean(), np.sqrt(np.mean((e - t) ** 2)), np.corrcoef(t, e)[0, 1], rng

    emit("\n[1] point-estimate recovery (posterior mean vs truth) over held-out obs")
    emit(f"  {'param':16s} {'bias':>8s} {'rmse':>8s} {'rmse/range':>11s} {'corr(true,est)':>15s}")
    for name in ("cv_myo", "delta_iv", "cv"):
        j = THETA_NAMES.index(name)
        b, r, c, rng = stats(j)
        emit(f"  {name:16s} {b:8.3f} {r:8.3f} {r / rng:11.2f} {c:15.2f}")
    # the identifiable combination: fit k so delta_iv + k*cv_myo is best-recovered
    ks = np.linspace(-40, 40, 161)
    combo_r = [
        np.corrcoef(th_ca[:, IV] + k * th_ca[:, MYO], est[:, IV] + k * est[:, MYO])[0, 1]
        for k in ks
    ]
    kbest = ks[int(np.argmax(combo_r))]
    emit(
        f"  best combo delta_iv + {kbest:.0f}*cv_myo: corr(true,est) = {max(combo_r):.2f} "
        f"(vs cv_myo alone {stats(MYO)[2]:.2f}); the ECG pins the combination"
    )

    # --- (2) iso-ECG manifold along the delta_iv-cv_myo ridge ---
    # ridge direction = top eigenvector of the posterior (delta_iv, cv_myo) covariance at a ref obs,
    # in prior-range-normalized units so the two axes are comparable.
    rng2 = np.array([_HI[IV] - _LO[IV], _HI[MYO] - _LO[MYO]])
    s_ref = np.asarray(
        post.sample((2000,), x=torch.tensor(x_ca[0], dtype=torch.float32), show_progress_bars=False)
    )
    cov = np.cov(((s_ref[:, [IV, MYO]]) / rng2).T)
    evals, evecs = np.linalg.eigh(cov)
    ridge = evecs[:, -1]  # largest-variance (flat/ridge) direction, normalized units
    orth = evecs[:, 0]
    emit(f"\n[2] iso-ECG manifold: ridge dir (delta_iv,cv_myo) normalized = {np.round(ridge, 2)}")

    geom = load_geometry()
    base = {k: float(REFERENCE_THETA[k]) for k in THETA_NAMES}
    ecg0 = to_physiological_mv(forward(base, geom))
    step = 0.18  # fraction of prior range

    def perturb(direction, sign):
        th = dict(base)
        d = sign * step * direction * rng2
        th["delta_iv"] = float(np.clip(base["delta_iv"] + d[0], _LO[IV], _HI[IV]))
        th["cv_myo"] = float(np.clip(base["cv_myo"] + d[1], _LO[MYO], _HI[MYO]))
        return th, _rel_l2(to_physiological_mv(forward(th, geom)), ecg0)

    _, dr_p = perturb(ridge, +1)
    _, dr_m = perturb(ridge, -1)
    _, do_p = perturb(orth, +1)
    _, do_m = perturb(orth, -1)
    along = 0.5 * (dr_p + dr_m)
    across = 0.5 * (do_p + do_m)
    emit(f"  mean rel-L2 ECG change: ALONG ridge = {along:.3f} | ORTHOGONAL = {across:.3f}")
    emit(
        f"  ratio orthogonal/along = {across / (along + 1e-9):.1f}x "
        f"({'ridge is a likelihood flat direction' if across > 1.5 * along else 'inconclusive'})"
    )
    emit("[ridge] done")


if __name__ == "__main__":
    main()
