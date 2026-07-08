"""Observation-noise model (brief 5.6). The simulator is deterministic given theta, so
without added observation noise NPE trains on a deterministic map and calibration is
meaningless (artificially perfect coverage). Noise is a modeling assumption that shifts
the identifiability boundary honestly, and MUST be the same in training, BO+ABC, and
calibration.

Contract D (frozen, absolute-mV) is the current model: white i.i.d. Gaussian at the
waveform, sigma = 0.025 mV, added OUTSIDE purkinje-uv, fresh draw per (theta, x), logged
seed. It supersedes the day-1 relative model (5% of each lead's std), which flattered
identifiability on small-amplitude leads. Source: Obregon-Rosas et al. 2026 (QRSense),
J Electrocardiol, PMID 42176693.

Caveat: absolute-mV noise assumes the forward ECG is in mV; a global amplitude/units gap
(open forward-fidelity item) would rescale the effective SNR. It stays internally consistent
for the synthetic-truth SBC study (train and calibration share this exact model).
"""

from __future__ import annotations

import numpy as np

# Contract D frozen waveform sigma (mV).
DEFAULT_WAVEFORM_SIGMA_MV = 0.025

# Retired day-1 relative model, kept for the historical day-1 smoke only.
DEFAULT_NOISE_FRAC = 0.05


def add_waveform_noise_absolute(
    ecg: np.ndarray, sigma_mv: float, rng: np.random.Generator
) -> np.ndarray:
    """Contract D: add zero-mean white Gaussian noise, sigma_mv (mV) i.i.d. per sample per lead."""
    ecg = np.asarray(ecg, dtype=float)
    return ecg + rng.normal(scale=max(float(sigma_mv), 1e-12), size=ecg.shape)


def add_waveform_noise(ecg: np.ndarray, noise_frac: float, rng: np.random.Generator) -> np.ndarray:
    """Retired (day-1): per-lead Gaussian, sigma_lead = noise_frac * std(lead). Use the
    absolute model for all new work."""
    ecg = np.asarray(ecg, dtype=float)
    sigma = noise_frac * ecg.std(axis=1, keepdims=True)  # (12, 1)
    return ecg + rng.normal(scale=np.maximum(sigma, 1e-12), size=ecg.shape)
