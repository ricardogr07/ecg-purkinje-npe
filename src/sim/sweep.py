"""Parallel simulation sweep: sample theta, run forward, extract clean + noised features.

On tree-growth failure the draw is dropped (reject and oversample), so the effective prior
is uniform over the growable region, a stated modeling choice to carry into calibration.
Geometry is built once per worker. This is the day-1 smoke harness and the seed of the
Thursday 5k sweep (scale by raising n_workers; 5k at 14.2s/theta needs ~20 cores for <1h).
"""

from __future__ import annotations

import os as _os

# Pin BLAS/VTK to one thread per process BEFORE numpy imports. Each sweep worker is one
# forward eval; multi-threaded BLAS across many workers oversubscribes cores (the day-1
# smoke saw ~3x slowdown). Set before numpy so the thread pools size to 1.
for _v in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    _os.environ.setdefault(_v, "1")

from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402

from core.features import extract_features  # noqa: E402
from core.noise import add_waveform_noise  # noqa: E402
from core.theta import sample_prior, to_dict  # noqa: E402
from sim.forward import forward, load_geometry  # noqa: E402

_GEOM = None


def _init_worker() -> None:
    global _GEOM
    _GEOM = load_geometry()


def _run_one(args):
    theta_row, noise_frac, seed = args
    rng = np.random.default_rng(seed)
    try:
        ecg = forward(to_dict(theta_row), _GEOM)
    except Exception:  # tree growth out of domain, etc: reject this draw
        return None
    x_clean = extract_features(ecg)
    x_noised = extract_features(add_waveform_noise(ecg, noise_frac, rng))
    return theta_row, x_clean, x_noised


def run_sweep(n: int, noise_frac: float, n_workers: int, seed: int = 0):
    """Return (theta, x_clean, x_noised, n_drawn). theta is (m, 6), features (m, D), m<=n_drawn."""
    rng = np.random.default_rng(seed)
    n_draw = int(np.ceil(n / 0.85))  # oversample for the ~12-15% growth-failure rate
    thetas = sample_prior(n_draw, rng)
    args = [(thetas[i], noise_frac, seed + 1000 + i) for i in range(n_draw)]

    if n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers, initializer=_init_worker) as ex:
            results = list(ex.map(_run_one, args))
    else:
        _init_worker()
        results = [_run_one(a) for a in args]

    ok = [r for r in results if r is not None]
    theta_ok = np.array([r[0] for r in ok], dtype=float)
    x_clean = np.array([r[1] for r in ok], dtype=float)
    x_noised = np.array([r[2] for r in ok], dtype=float)
    return theta_ok, x_clean, x_noised, n_draw
