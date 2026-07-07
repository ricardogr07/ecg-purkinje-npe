"""Contract A (provisional): the 6D conduction parameter vector theta.

Ranges here are PROVISIONAL and literature-ballpark, flagged UNVERIFIED. They are
deliberately NOT the thesis BOECGParameter bounds (open eligibility question, brief
section 8). Freeze on Thu with director sign-off after the forward-sensitivity probe.

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

# name -> (lo, hi). PROVISIONAL / UNVERIFIED, centered near the crtdemo paper preset.
PRIOR_BOUNDS: dict[str, tuple[float, float]] = {
    "cv": (1.5, 4.0),
    "delta_iv": (-40.0, 40.0),
    "init_length_lv": (15.0, 45.0),
    "init_length_rv": (45.0, 95.0),
    "branch_angle": (0.05, 0.40),
    "w": (0.0, 0.25),
}


def sample_prior(n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n theta rows uniformly from PRIOR_BOUNDS. Returns (n, 6) in THETA_NAMES order."""
    lo = np.array([PRIOR_BOUNDS[k][0] for k in THETA_NAMES])
    hi = np.array([PRIOR_BOUNDS[k][1] for k in THETA_NAMES])
    return lo + rng.uniform(size=(n, len(THETA_NAMES))) * (hi - lo)


def to_dict(theta_row: np.ndarray) -> dict[str, float]:
    """Map a positional theta row to a name-keyed dict (Contract A boundary form)."""
    return {k: float(v) for k, v in zip(THETA_NAMES, theta_row, strict=False)}
