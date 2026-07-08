"""Contract A: the conduction parameter vector theta (frozen 6D box here; cv_myo is the
7th param, added when the forward exposes it).

Ranges are the FROZEN Contract A box (director-approved, see .localagent/FREEZE_AND_PLAN.md
and docs/priors.md), arrived at independently of the thesis BOECGParameter bounds (brief
section 8). Sourced anchors: cv (Maguy 2009 Purkinje CV), branch_angle / w (Sahli Costabal
2015 + Tanikella 2025), init_length labeled OUR modeling choice (Tanikella fixed 50 mm, LV).
delta_iv is the dyssynchrony regime; its lower bound [-90] is PROVENANCE-PENDING (Research
P0 sourcing a BBB/CRT interventricular-delay range), so the delta_iv contraction is not a
public claim until sourced. delta_iv is a RELATIVE LV-RV delay only (absolute timing is
normalized away in the ECG synthesis); it does not reproduce a real ECG on its own.

Canonical order is THETA_NAMES; serialize keyed by name, never by position.
"""

from __future__ import annotations

import numpy as np

THETA_NAMES: tuple[str, ...] = (
    "cv",  # global conduction velocity, m/s -> QRS duration
    "delta_iv",  # LV-RV interventricular delay, ms -> axis/morphology
    "init_length_lv",  # LV early-activation extent, mm
    "init_length_rv",  # RV early-activation extent, mm
    "branch_angle",  # inter-branch angle, rad (diffuse)
    "w",  # branch-divergence weight / PMJ spread (diffuse)
)

# name -> (lo, hi). FROZEN Contract A 6D box (cv_myo fixed at 0.67 until the forward
# exposes it as a 7th inferred param). delta_iv lower bound provenance-pending (see note).
PRIOR_BOUNDS: dict[str, tuple[float, float]] = {
    "cv": (1.5, 3.5),
    "delta_iv": (-90.0, 40.0),
    "init_length_lv": (30.0, 60.0),
    "init_length_rv": (30.0, 60.0),
    "branch_angle": (0.10, 0.30),
    "w": (0.05, 0.20),
}


def sample_prior(n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n theta rows uniformly from PRIOR_BOUNDS. Returns (n, 6) in THETA_NAMES order."""
    lo = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES])
    hi = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES])
    return lo + rng.uniform(size=(n, len(THETA_NAMES))) * (hi - lo)


def to_dict(theta_row: np.ndarray) -> dict[str, float]:
    """Map a positional theta row to a name-keyed dict (Contract A boundary form)."""
    return {k: float(v) for k, v in zip(THETA_NAMES, theta_row, strict=False)}
