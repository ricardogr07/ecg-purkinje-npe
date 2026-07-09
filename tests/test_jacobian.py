"""Self-check for experiments/jacobian_fim.py's numerical core (SVD / FIM / step-size
stability), on a small synthetic fixture. The real analysis loads the crtdemo geometry and
makes 45 forward() calls (~45-60 min here, see the module docstring), far too slow for any
gated test tier, so this exercises the pure-numpy building blocks instead: singular values
come back finite and sorted descending, CRLB/FIM shapes are right, and the step-size
stability check correctly classifies a stable vs. an unstable synthetic spectrum.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from jacobian_fim import (  # noqa: E402
    THETA_NAMES,
    fim_report,
    normalize_waveform,
    step_size_stability,
    svd_report,
)


def _synthetic_J_wave(rng, n_rows=200, scale=None):
    """A (n_rows, 7) Jacobian with a deliberately small last singular direction, standing in
    for the delta_iv/cv_myo-style near-degenerate direction."""
    J = rng.normal(size=(n_rows, len(THETA_NAMES)))
    if scale is not None:
        J = J * scale[np.newaxis, :]
    return J


def test_svd_report_finite_and_sorted_descending():
    rng = np.random.default_rng(0)
    J = _synthetic_J_wave(rng)
    report = svd_report(J)
    s = np.array(report["singular_values"])
    assert np.isfinite(s).all()
    assert len(s) == len(THETA_NAMES)
    assert np.all(np.diff(s) <= 0), "singular values must be sorted descending"
    assert np.isclose(np.linalg.norm(report["v_min"]), 1.0)
    assert set(report["v_min_named"]) == set(THETA_NAMES)
    assert report["condition_number"] >= 1.0


def test_nan_column_is_dropped_not_fatal():
    """A failed perturbation leaves a NaN Jacobian column; svd/fim must drop it, report the
    dropped param, and still return finite numbers (the resilience the coordinator asked for)."""
    rng = np.random.default_rng(3)
    J = _synthetic_J_wave(rng)
    J[:, 4] = np.nan  # simulate branch_angle failing to grow
    dropped_name = THETA_NAMES[4]

    svd = svd_report(J)
    assert svd["params_dropped"] == [dropped_name]
    assert len(svd["singular_values"]) == len(THETA_NAMES) - 1
    assert np.isfinite(svd["singular_values"]).all()
    assert svd["v_min_named"][dropped_name] == 0.0  # zero loading for the dropped slot

    fim = fim_report(J, sigma_mv=0.025)
    assert fim["params_dropped"] == [dropped_name]
    assert fim["crlb"][dropped_name] is None
    assert all(np.isfinite(v) for k, v in fim["crlb"].items() if k != dropped_name)


def test_fim_report_shapes_and_finite_crlb():
    rng = np.random.default_rng(1)
    J = _synthetic_J_wave(rng)
    report = fim_report(J, sigma_mv=0.025)
    eig = np.array(report["eigenvalues_ascending"])
    assert np.isfinite(eig).all()
    assert np.all(np.diff(eig) >= -1e-9), "FIM eigenvalues must be ascending"
    assert np.all(eig >= -1e-6), "FIM (J^T J) must be PSD"
    assert set(report["crlb"]) == set(THETA_NAMES)
    assert all(np.isfinite(v) and v >= 0 for v in report["crlb"].values())


def test_normalize_waveform_scales_by_sigma_and_prior_range():
    rng = np.random.default_rng(2)
    J = _synthetic_J_wave(rng)
    sigma = 0.025
    J_tilde = normalize_waveform(J, sigma)
    # column i scales by PRIOR_RANGE[i] / sigma relative to the raw Jacobian
    from core.theta import PRIOR_BOUNDS

    prior_range = np.array([PRIOR_BOUNDS[k][1] - PRIOR_BOUNDS[k][0] for k in THETA_NAMES])
    expected = (J / sigma) * prior_range[np.newaxis, :]
    assert np.allclose(J_tilde, expected)


def test_step_size_stability_flags_stable_vs_unstable():
    stable_spectra = {
        5e-3: [10, 8, 6, 4, 2, 1, 0.50],
        1e-2: [10, 8, 6, 4, 2, 1, 0.52],
        2e-2: [10, 8, 6, 4, 2, 1, 0.48],
    }
    stable = step_size_stability(stable_spectra)
    assert stable["stable"] is True
    assert stable["relative_spread"] < 0.2

    unstable_spectra = {
        5e-3: [10, 8, 6, 4, 2, 1, 0.05],
        1e-2: [10, 8, 6, 4, 2, 1, 0.50],
        2e-2: [10, 8, 6, 4, 2, 1, 5.0],
    }
    unstable = step_size_stability(unstable_spectra)
    assert unstable["stable"] is False
    assert unstable["relative_spread"] >= 0.2
