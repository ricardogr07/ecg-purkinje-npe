"""Engineered ECG features (core/features.py): fixed length and time-shift invariance."""

import numpy as np

from core.features import FEATURE_NAMES, extract_features


def test_feature_vector_is_fixed_length_regardless_of_T():
    rng = np.random.default_rng(0)
    for T in (50, 200, 377):
        f = extract_features(rng.normal(size=(12, T)))
        assert f.shape == (len(FEATURE_NAMES),) == (15,)


def test_features_are_time_shift_invariant_except_time_to_peak():
    rng = np.random.default_rng(1)
    ecg = rng.normal(size=(12, 200))
    f0 = extract_features(ecg)
    f1 = extract_features(np.roll(ecg, 37, axis=1))
    # p2p per lead (0..11), qrs_active_frac (12), vecmag_peak (13) survive a circular roll;
    # only time_to_peak_frac (14) tracks the shift.
    assert np.allclose(f0[:14], f1[:14])
