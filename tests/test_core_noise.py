"""Observation-noise model (core/noise.py): physiological-mV scaling and the Contract D floor.

The simulator is deterministic, so this noise is the ONLY stochasticity NPE sees; it must be
reproducible from a seed (same seed -> identical draw) and honour its stated sigma.
"""

import numpy as np

from core.noise import (
    DEFAULT_WAVEFORM_SIGMA_MV,
    ECG_MV_SCALE,
    add_waveform_noise_absolute,
    to_physiological_mv,
)


def test_to_physiological_mv_applies_the_scale():
    ecg = np.ones((12, 5))
    assert np.allclose(to_physiological_mv(ecg), ECG_MV_SCALE)
    assert 0.0 < ECG_MV_SCALE < 1.0  # pseudo-mV forward peak is downscaled toward ~1.5 mV


def test_waveform_noise_is_seed_reproducible_and_matches_sigma():
    ecg = np.zeros((12, 1000))
    a = add_waveform_noise_absolute(ecg, DEFAULT_WAVEFORM_SIGMA_MV, np.random.default_rng(0))
    b = add_waveform_noise_absolute(ecg, DEFAULT_WAVEFORM_SIGMA_MV, np.random.default_rng(0))
    c = add_waveform_noise_absolute(ecg, DEFAULT_WAVEFORM_SIGMA_MV, np.random.default_rng(1))
    assert np.array_equal(a, b)  # same seed -> identical draw
    assert not np.array_equal(a, c)  # different seed -> different draw
    assert abs(a.mean()) < 0.005  # zero-mean (sigma / sqrt(12000) ~ 2e-4)
    assert abs(a.std() - DEFAULT_WAVEFORM_SIGMA_MV) < 0.005
