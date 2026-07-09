"""TARP on conformally-inflated sample sets (calib.diagnostics.run_tarp_on_sets).

Uses a synthetic, deliberately overconfident conjugate-Gaussian model (no forward, no training):
theta ~ N(0, tau^2), x | theta ~ N(theta, 1), exact posterior N(mu_post, sd_post^2), but we
sample too narrow (sd_post / over). TARP should read that as underdispersed (ATC < 0, sbi's sign
convention), and inflating the samples toward the true spread should move the joint ATC toward 0.
This is the joint analogue of calib.conformal._selfcheck, and it guards the post-conformal TARP
path emit.py now reports.
"""

import numpy as np
import pytest

pytest.importorskip("sbi")
pytest.importorskip("torch")

from calib.diagnostics import run_tarp_on_sets  # noqa: E402


def _overconfident_sets(seed=0, m=400, n=300, d=3, over=1.6):
    rng = np.random.default_rng(seed)
    tau = np.array([1.0, 2.0, 0.5])[:d]
    sigma_obs = np.ones(d)
    sd_post = tau * sigma_obs / np.sqrt(tau**2 + sigma_obs**2)
    shrink = tau**2 / (tau**2 + sigma_obs**2)
    theta = rng.normal(0.0, tau, size=(m, d))
    x = theta + rng.normal(0.0, sigma_obs, size=(m, d))
    mu_post = shrink * x
    sets = mu_post[:, None, :] + rng.normal(0.0, sd_post / over, size=(m, n, d))  # too narrow
    return theta, sets, over


def test_tarp_on_sets_runs_and_signs():
    theta, sets, over = _overconfident_sets()
    pre = run_tarp_on_sets(sets, theta, np.ones(sets.shape[2]))
    assert np.isfinite(pre["atc"]) and 0.0 <= pre["ks_pval"] <= 1.0
    # underdispersed (too narrow) => negative ATC in sbi's convention
    assert pre["atc"] < 0, f"expected ATC<0 for overconfident sets, got {pre['atc']:.3f}"


def test_inflation_moves_joint_atc_toward_zero():
    theta, sets, over = _overconfident_sets()
    pre = run_tarp_on_sets(sets, theta, np.ones(sets.shape[2]))
    post = run_tarp_on_sets(sets, theta, np.full(sets.shape[2], over))  # inflate ~ back to truth
    # inflating a too-narrow posterior should raise ATC toward 0 (less overconfident)
    assert post["atc"] > pre["atc"], (
        f"inflation did not raise ATC: pre={pre['atc']:.3f} post={post['atc']:.3f}"
    )
    assert abs(post["atc"]) < abs(pre["atc"]), "post-conformal joint ATC should be closer to 0"


if __name__ == "__main__":
    th, s, ov = _overconfident_sets()
    pre = run_tarp_on_sets(s, th, np.ones(s.shape[2]))
    post = run_tarp_on_sets(s, th, np.full(s.shape[2], ov))
    print(f"pre  ATC={pre['atc']:+.3f} ks={pre['ks_pval']:.3f}")
    print(f"post ATC={post['atc']:+.3f} ks={post['ks_pval']:.3f}  (inflated by {ov})")
