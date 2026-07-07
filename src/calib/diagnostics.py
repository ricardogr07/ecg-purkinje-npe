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

    ATC near 0 and a high KS p-value indicate coverage consistent with calibration.
    """
    ecp, alpha = run_tarp(_t(theta_calib), _t(x_calib), posterior, num_posterior_samples=n_post)
    atc, ks_pval = check_tarp(ecp, alpha)
    return {
        "ecp": np.asarray(ecp),
        "alpha": np.asarray(alpha),
        "atc": float(atc),
        "ks_pval": float(ks_pval),
    }
