"""Per-parameter conformal recalibration of an overconfident NPE posterior.

The v0 features-NPE is right-location but ~1.3x too narrow (SBC fails; a scalar variance
inflation t~1.3 restores rank uniformity). This productizes that result principled and
per-parameter: on a held-out calibration split, pick an inflation factor t_d per dimension
that makes the marginal SBC ranks uniform (minimizes KS-to-uniform). Recalibrated sampling
is s -> mu + t_d * (s - mu) per dimension, so each parameter's posterior std scales by t_d.

Per-parameter, not one global scalar: each parameter is overconfident by a different amount.

The core math is pure numpy (operates on drawn sample sets), so it is testable without sbi
or a checkpoint (see __main__). Only draw_sample_sets touches the posterior.

CAVEAT: marginal inflation targets SBC (per-parameter rank uniformity). It does NOT
guarantee TARP (joint) coverage if parameters are correlated. Check TARP after applying it;
escalate to a covariance-aware recalibration only if TARP stays off.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import kstest

DEFAULT_T_GRID = np.round(np.arange(0.5, 3.0001, 0.05), 4)


def _ranks(theta_calib: np.ndarray, sample_sets: np.ndarray, t: np.ndarray) -> np.ndarray:
    """SBC rank of each truth after inflating samples by t (per dim). Returns (M, D) in [0, N]."""
    mu = sample_sets.mean(axis=1, keepdims=True)  # (M, 1, D)
    infl = mu + t * (sample_sets - mu)  # broadcast t over (M, N, D)
    return (infl < theta_calib[:, None, :]).sum(axis=1)  # (M, D)


def fit_inflation(
    theta_calib: np.ndarray, sample_sets: np.ndarray, t_grid: np.ndarray = DEFAULT_T_GRID
) -> np.ndarray:
    """Per-parameter inflation t_d minimizing SBC KS-to-uniform on the calibration split.

    theta_calib: (M, D) truths. sample_sets: (M, N, D) posterior samples per calib point.
    Returns t: (D,). t_d > 1 means dimension d was overconfident by ~t_d.
    """
    m, n, d = sample_sets.shape
    t_out = np.ones(d)
    for j in range(d):
        best_ks, best_t = np.inf, 1.0
        for t in t_grid:
            tvec = np.ones(d)
            tvec[j] = t
            r = _ranks(theta_calib, sample_sets, tvec)[:, j] / n
            ks = kstest(r, "uniform").statistic
            if ks < best_ks:
                best_ks, best_t = ks, float(t)
        t_out[j] = best_t
    return t_out


def recalibrate(samples: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Inflate (N, D) posterior samples by t (D,) around their per-column mean."""
    mu = samples.mean(axis=0, keepdims=True)
    return mu + np.asarray(t) * (samples - mu)


def sbc_ks_pvals(theta_calib: np.ndarray, sample_sets: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Per-dim SBC KS p-value after inflating by t. p > 0.05 => rank uniformity not rejected."""
    n = sample_sets.shape[1]
    r = _ranks(theta_calib, sample_sets, np.asarray(t)) / n
    return np.array([kstest(r[:, j], "uniform").pvalue for j in range(r.shape[1])])


def central_coverage(
    theta_calib: np.ndarray, sample_sets: np.ndarray, t: np.ndarray, level: float = 0.9
) -> np.ndarray:
    """Per-dim empirical coverage of the central `level` credible interval after inflating by t.

    Calibrated => coverage ~ level. Overconfident (t too small) => coverage < level.
    """
    mu = sample_sets.mean(axis=1, keepdims=True)
    infl = mu + np.asarray(t) * (sample_sets - mu)  # (M, N, D)
    lo = np.quantile(infl, (1 - level) / 2, axis=1)  # (M, D)
    hi = np.quantile(infl, (1 + level) / 2, axis=1)
    covered = (theta_calib >= lo) & (theta_calib <= hi)
    return covered.mean(axis=0)


def draw_sample_sets(posterior, x_calib, n_post: int = 300) -> np.ndarray:
    """(M, N, D) posterior samples, one N-sample set per calibration observation. Touches sbi."""
    import torch

    sets = []
    for x in x_calib:
        s = posterior.sample(
            (n_post,), x=torch.as_tensor(x, dtype=torch.float32), show_progress_bars=False
        )
        sets.append(np.asarray(s))
    return np.stack(sets)


def _selfcheck() -> None:
    """Conjugate-Gaussian SBC model, deliberately overconfident. Prior theta ~ N(0, tau^2),
    likelihood x|theta ~ N(theta, sigma_obs^2), exact posterior theta|x ~ N(mu_post, sd_post^2).
    Sampling from N(mu_post, (sd_post/over)^2) is too narrow, so SBC ranks are non-uniform and
    the central interval under-covers. fit_inflation should recover t ~ over and restore nominal
    coverage. No sbi, no checkpoint."""
    rng = np.random.default_rng(0)
    m, n, d = 400, 500, 3
    tau = np.array([1.0, 2.0, 0.5])  # prior std per dim
    sigma_obs = np.array([1.0, 1.0, 1.0])  # observation noise std per dim
    over = np.array([1.4, 1.25, 1.6])  # each dim overconfident by a different amount

    sd_post = tau * sigma_obs / np.sqrt(tau**2 + sigma_obs**2)
    shrink = tau**2 / (tau**2 + sigma_obs**2)
    theta = rng.normal(0.0, tau, size=(m, d))
    x = theta + rng.normal(0.0, sigma_obs, size=(m, d))
    mu_post = shrink * x  # prior mean 0
    samples = mu_post[:, None, :] + rng.normal(0.0, sd_post / over, size=(m, n, d))

    cov0 = central_coverage(theta, samples, np.ones(d), level=0.9)
    ks0 = sbc_ks_pvals(theta, samples, np.ones(d))
    t = fit_inflation(theta, samples)
    cov1 = central_coverage(theta, samples, t, level=0.9)
    ks1 = sbc_ks_pvals(theta, samples, t)

    print(f"[selfcheck] recovered t={np.round(t, 2)} (truth over={over})")
    print(f"[selfcheck] coverage@0.9 before={np.round(cov0, 3)} after={np.round(cov1, 3)}")
    print(f"[selfcheck] SBC ks p before={np.round(ks0, 3)} after={np.round(ks1, 3)}")
    assert np.all(cov0 < 0.88), "expected under-coverage before recalibration"
    assert np.all(np.abs(t - over) < 0.35), "inflation should approx recover the overconfidence"
    assert np.all(np.abs(cov1 - 0.9) < 0.06), "central coverage should be ~nominal after"
    print("[selfcheck] OK")


if __name__ == "__main__":
    _selfcheck()
