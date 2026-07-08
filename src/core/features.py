"""Engineered ECG features (waveform -> fixed-length vector), Contract-A-adjacent.

Kept deliberately small and I/O-free. These are the "features" observation used in the
paired features-vs-waveform comparison (brief 5.3). Fixed dimension regardless of trace
length T, so variable-length ECGs are handled without resampling.
"""

from __future__ import annotations

import numpy as np

FEATURE_NAMES: tuple[str, ...] = (
    *(f"p2p_lead{i}" for i in range(12)),  # per-lead peak-to-peak amplitude
    "qrs_active_frac",  # width of the active window / T
    "vecmag_peak",  # peak of the 12-lead RSS
    "time_to_peak_frac",  # argmax of the RSS / T
)

# Contract D feature typing (for the feature-channel noise: "amp" ~0.05 mV, "time" ~5 ms).
# This run injects noise at the WAVEFORM before extraction, so this is for the later
# feature-level mode; the two fractional timing features would need scaling by T to take ms.
FEATURE_KINDS: tuple[str, ...] = (
    *("amp",) * 12,  # p2p per lead (mV)
    "time",  # qrs_active_frac
    "amp",  # vecmag_peak (mV)
    "time",  # time_to_peak_frac
)


def _vector_magnitude(ecg: np.ndarray) -> np.ndarray:
    return np.sqrt((ecg**2).sum(axis=0))


def extract_features(ecg: np.ndarray) -> np.ndarray:
    """Map a (12, T) ECG to a (15,) feature vector in FEATURE_NAMES order."""
    ecg = np.asarray(ecg, dtype=float)
    p2p = ecg.max(axis=1) - ecg.min(axis=1)  # (12,)
    mag = _vector_magnitude(ecg)
    peak = float(mag.max())
    active_frac = float((mag > 0.05 * peak).sum()) / mag.shape[0]
    ttp = float(int(np.argmax(mag))) / mag.shape[0]
    return np.concatenate([p2p, [active_frac, peak, ttp]]).astype(float)
