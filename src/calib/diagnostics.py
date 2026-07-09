"""Calibration diagnostics over a trained NPE posterior: SBC and TARP expected coverage.

Thin wrappers over sbi.diagnostics. SBC checks posterior rank uniformity (are the credible
intervals calibrated?); TARP estimates expected coverage without exact posteriors. Both take
an independent set of (theta, x) drawn from the prior and the trained posterior.
"""

from __future__ import annotations

import numpy as np
import torch
from sbi.diagnostics import check_tarp, run_sbc, run_tarp


def _t(a) -> torch.Tensor:
    return torch.as_tensor(np.asarray(a), dtype=torch.float32)


def run_sbc_check(posterior, theta_calib, x_calib, n_post: int = 200):
    """Return (ranks array (N, D), stats dict). Uniform ranks => calibrated."""
    from sbi.diagnostics import check_sbc

    ranks, dap = run_sbc(_t(theta_calib), _t(x_calib), posterior, num_posterior_samples=n_post)
    stats = check_sbc(ranks, _t(theta_calib), dap, num_posterior_samples=n_post)
    out = {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in stats.items()}
    return np.asarray(ranks), out


def run_tarp_check(posterior, theta_calib, x_calib, n_post: int = 200):
    """Return dict with the expected-coverage curve (ecp vs alpha), ATC, and KS p-value.

    ATC near 0 and a high KS p-value indicate coverage consistent with calibration. sbi's sign
    convention (check_tarp): ATC > 0 overdispersed (too wide), ATC < 0 underdispersed (too
    narrow / overconfident). This runs on the RAW posterior, so its ATC is PRE-conformal.
    """
    ecp, alpha = run_tarp(_t(theta_calib), _t(x_calib), posterior, num_posterior_samples=n_post)
    atc, ks_pval = check_tarp(ecp, alpha)
    return {
        "ecp": np.asarray(ecp),
        "alpha": np.asarray(alpha),
        "atc": float(atc),
        "ks_pval": float(ks_pval),
    }


def run_tarp_on_sets(sample_sets, theta_calib, t):
    """TARP on conformally-inflated sample sets, so joint coverage can be checked POST-conformal.

    Per-parameter conformal inflates each posterior around its mean (calib.conformal.recalibrate);
    marginal SBC can pass while the joint stays off if parameters are correlated, which is exactly
    what TARP tests. This reuses sbi's own ECP/ATC internals on pre-drawn, inflated samples, so the
    number is directly comparable to run_tarp_check (only the inflation differs).

    sample_sets: (M, N, D) posterior draws, one N-sample set per calib obs (draw_sample_sets).
    theta_calib: (M, D) truths. t: (D,) per-parameter inflation (ones(D) reproduces pre-conformal).
    """
    from sbi.diagnostics.tarp import _run_tarp, get_tarp_references

    sets = np.asarray(sample_sets, dtype=float)
    mu = sets.mean(axis=1, keepdims=True)  # (M,1,D), same mean sbc/coverage inflate around
    infl = mu + np.asarray(t) * (sets - mu)  # (M,N,D)
    ps = _t(np.transpose(infl, (1, 0, 2)))  # sbi wants (num_post_samples N, num_tarp M, D)
    th = _t(theta_calib)
    ecp, alpha = _run_tarp(ps, th, get_tarp_references(th), z_score_theta=True)
    atc, ks_pval = check_tarp(ecp, alpha)
    return {
        "ecp": np.asarray(ecp),
        "alpha": np.asarray(alpha),
        "atc": float(atc),
        "ks_pval": float(ks_pval),
    }
