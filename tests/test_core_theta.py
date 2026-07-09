"""Contract A theta box (core/theta.py): shape, bounds, and name-keyed serialization."""

import numpy as np

from core.theta import PRIOR_BOUNDS, THETA_NAMES, sample_prior, to_dict


def test_names_and_bounds_are_consistent():
    assert len(THETA_NAMES) == 7  # frozen 7D contract
    assert set(PRIOR_BOUNDS) == set(THETA_NAMES)
    for k in THETA_NAMES:
        lo, hi = PRIOR_BOUNDS[k]
        assert lo < hi, f"{k}: bound not ordered"


def test_sample_prior_shape_and_in_bounds():
    rng = np.random.default_rng(0)
    th = sample_prior(2000, rng)
    assert th.shape == (2000, 7)
    lo = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES])
    hi = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES])
    assert (th >= lo).all() and (th <= hi).all()


def test_to_dict_is_name_keyed_in_canonical_order():
    row = np.arange(7, dtype=float)
    d = to_dict(row)
    assert list(d.keys()) == list(THETA_NAMES)
    assert d["cv"] == 0.0 and d["cv_myo"] == 6.0
    assert all(isinstance(v, float) for v in d.values())
