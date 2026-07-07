"""Observation-noise model (brief 5.6).

The simulator is deterministic given theta, so without added observation noise NPE
trains on a deterministic map and calibration is meaningless (artificially perfect
coverage). We add per-lead Gaussian noise at the waveform, magnitude stated as a
fraction of each lead's own standard deviation. This magnitude is a modeling assumption
and shifts the identifiability boundary honestly.
"""

from __future__ import annotations

import numpy as np

# Stated assumption for the day-1 smoke: 5% per-lead Gaussian. Revisit as an ablation.
DEFAULT_NOISE_FRAC = 0.05


def add_waveform_noise(ecg: np.ndarray, noise_frac: float, rng: np.random.Generator) -> np.ndarray:
    """Add zero-mean Gaussian noise per lead: sigma_lead = noise_frac * std(lead)."""
    ecg = np.asarray(ecg, dtype=float)
    sigma = noise_frac * ecg.std(axis=1, keepdims=True)  # (12, 1)
    return ecg + rng.normal(scale=np.maximum(sigma, 1e-12), size=ecg.shape)
