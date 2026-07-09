"""Per-parameter conformal recalibration (calib/conformal.py).

The productized fix for the overconfident features-NPE: recalibrate scales each
parameter's posterior std by t_d around its mean, and fit_inflation recovers t_d from
a held-out SBC split. Both are pure numpy, so they are testable without sbi.
"""

import numpy as np

from calib.conformal import _selfcheck, fit_inflation, recalibrate


def test_recalibrate_scales_std_preserves_mean():
    rng = np.random.default_rng(0)
    samples = rng.normal(5.0, 2.0, size=(20000, 3))
    t = np.array([1.5, 0.5, 1.0])
    out = recalibrate(samples, t)
    # mean is the fixed point; std scales by exactly t per column
    assert np.allclose(out.mean(axis=0), samples.mean(axis=0), atol=1e-9)
    assert np.allclose(out.std(axis=0) / samples.std(axis=0), t, atol=1e-6)


def test_fit_inflation_recovers_overconfidence_on_gaussian():
    # Conjugate-Gaussian SBC model, deliberately overconfident per dim; fit_inflation
    # should recover t ~ over. Reuses the module's own seeded self-check assertions.
    _selfcheck()


def test_fit_inflation_leaves_calibrated_dim_near_one():
    # A dimension that is already calibrated (samples drawn at the exact posterior width)
    # should get an inflation factor close to 1.
    rng = np.random.default_rng(1)
    m, n = 400, 500
    theta = rng.normal(0.0, 1.0, size=(m, 1))
    x = theta + rng.normal(0.0, 1.0, size=(m, 1))
    sd_post = 1.0 / np.sqrt(2.0)
    mu_post = 0.5 * x
    samples = mu_post[:, None, :] + rng.normal(0.0, sd_post, size=(m, n, 1))
    t = fit_inflation(theta, samples)
    assert abs(t[0] - 1.0) < 0.2
