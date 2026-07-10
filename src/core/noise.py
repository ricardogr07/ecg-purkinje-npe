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

# Physiological-mV calibration (director Jul 8). The lead-field synthesis emits uncalibrated
# pseudo-mV: forward(REFERENCE_THETA) peaks ~73 mV, while a real 12-lead QRS peaks ~1.5 mV. Left
# uncalibrated, the 0.025 mV Contract D noise is ~3000x below the signal (near-noiseless), which
# flatters identifiability. Scaling the forward ECG to physiological mV BEFORE adding the (sourced,
# real-mV) 0.025 mV noise makes the SNR physiological (~60). Contract D (the noise) is unchanged;
# this is a forward units-calibration applied identically in training, calibration, and the demo.
# Amplitude ratios (fidelity) are scale-invariant, so the fidelity table is unaffected.
REFERENCE_QRS_PEAK_MV = 73.1  # measured peak of forward(REFERENCE_THETA), pseudo-mV
TARGET_QRS_PEAK_MV = 1.5  # physiological 12-lead QRS peak
ECG_MV_SCALE = TARGET_QRS_PEAK_MV / REFERENCE_QRS_PEAK_MV  # ~0.0205


def to_physiological_mv(ecg: np.ndarray) -> np.ndarray:
    """Scale a raw (pseudo-mV) forward ECG to physiological mV (see ECG_MV_SCALE)."""
    return np.asarray(ecg, dtype=float) * ECG_MV_SCALE


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


def add_feature_noise(
    features: np.ndarray,
    sigma_amp_mv: float,
    sigma_time_ms: float,
    t_samples: int,
    fs_hz: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Feature-level Contract D noise (the mode stubbed in features.FEATURE_KINDS).

    Adds noise per feature by kind: amp-kind features (mV) get sigma_amp_mv; timing-kind
    features are dimensionless fractions of T, so a sigma_time_ms floor is expressed in
    fraction-of-T units (sigma_time_ms / total_duration_ms, total = t_samples / fs_hz).

    Unlike add_waveform_noise_absolute, the timing floor is INDEPENDENT of signal amplitude,
    so scaling the waveform amplitude changes only the amp-feature SNR (leaving timing SNR
    fixed). This is what makes the amplitude-vs-timing corner a genuinely different point in
    observation space, not a reparameterization of a sigma corner.
    """
    from core.features import FEATURE_KINDS

    features = np.asarray(features, dtype=float)
    ms_per_sample = 1000.0 / float(fs_hz)
    sigma_time_frac = float(sigma_time_ms) / (float(t_samples) * ms_per_sample)
    out = features.copy()
    for i, kind in enumerate(FEATURE_KINDS):
        s = sigma_amp_mv if kind == "amp" else sigma_time_frac
        out[i] += rng.normal(scale=max(float(s), 1e-12))
    return out
