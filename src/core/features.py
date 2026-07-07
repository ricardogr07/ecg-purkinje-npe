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
