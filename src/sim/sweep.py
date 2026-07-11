"""Parallel simulation sweep: sample theta, run forward, extract clean + noised features.

On tree-growth failure the draw is dropped (reject and oversample), so the effective prior
is uniform over the growable region, a stated modeling choice to carry into calibration.
Geometry is built once per worker. This is the smoke harness and the seed of the
5k sweep (scale by raising n_workers; 5k at 14.2s/theta needs ~20 cores for <1h).
"""

from __future__ import annotations

import os as _os

# Pin BLAS/VTK to one thread per process BEFORE numpy imports. Each sweep worker is one
# forward eval; multi-threaded BLAS across many workers oversubscribes cores (an early
# smoke test saw ~3x slowdown). Set before numpy so the thread pools size to 1.
for _v in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    _os.environ.setdefault(_v, "1")

from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

from core.features import extract_features  # noqa: E402
from core.noise import add_waveform_noise_absolute, to_physiological_mv  # noqa: E402
from core.theta import sample_prior, to_dict  # noqa: E402
from sim.forward import forward, load_geometry  # noqa: E402

_GEOM = None


def _stack_waves(xw: list) -> tuple[np.ndarray, np.ndarray]:
    """Zero-pad a list of (12, T_i) clean waveforms to one (N, 12, T_max) array + true lengths.
    T varies per draw (features collapse it, but the raw waveform does not), so we pad and carry
    the lengths; a consumer slices ``x_wave[k, :, :x_wave_len[k]]`` to recover the exact trace."""
    if not xw:
        return np.zeros((0, 12, 0), dtype=float), np.zeros((0,), dtype=int)
    lens = np.array([w.shape[1] for w in xw], dtype=int)
    tmax = int(lens.max())
    arr = np.zeros((len(xw), 12, tmax), dtype=float)
    for k, w in enumerate(xw):
        arr[k, :, : w.shape[1]] = w
    return arr, lens


def _init_worker() -> None:
    global _GEOM
    _GEOM = load_geometry()


def _run_one(args):
    theta_row, noise_sigma_mv, seed = args
    rng = np.random.default_rng(seed)
    # FractalTree.grow_tree draws from the GLOBAL numpy RNG, so growth (and which draws fail)
    # is otherwise nondeterministic across worker processes. Seed it per draw for a
    # reproducible sweep and a defensible determinism claim.
    np.random.seed(seed & 0xFFFFFFFF)
    try:
        ecg = forward(to_dict(theta_row), _GEOM)
    except Exception:  # tree growth out of domain, etc: reject this draw
        return None
    ecg = to_physiological_mv(ecg)  # calibrate to physiological mV so the 0.025 mV noise is real
    x_clean = extract_features(ecg)
    x_noised = extract_features(add_waveform_noise_absolute(ecg, noise_sigma_mv, rng))
    # Return the CLEAN (12, T) waveform too. Additive only: it adds no RNG draw and does not
    # touch x_clean/x_noised, so the features stay byte-identical to the pre-waveform sweep.
    # Storing it lets sigma/amplitude retrains re-noise + re-feature with no re-simulation.
    return theta_row, x_clean, x_noised, ecg


def run_sweep(n: int, noise_sigma_mv: float, n_workers: int, seed: int = 0):
    """Return (theta, x_clean, x_noised, n_drawn); features (m, D), m<=n_drawn.
    noise_sigma_mv is the Contract D absolute waveform sigma (mV)."""
    rng = np.random.default_rng(seed)
    n_draw = int(np.ceil(n / 0.85))  # oversample for the ~12-15% growth-failure rate
    thetas = sample_prior(n_draw, rng)
    args = [(thetas[i], noise_sigma_mv, seed + 1000 + i) for i in range(n_draw)]

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


def run_sweep_checkpointed(
    n: int,
    noise_sigma_mv: float,
    n_workers: int,
    seed: int = 0,
    checkpoint_path: str | Path | None = None,
    save_every: int = 64,
):
    """Resumable sweep. Draws are deterministic from seed; progress is saved to
    checkpoint_path every save_every completions and reloaded on restart, so a crash (or a
    laptop reboot) costs at most save_every sims instead of the whole run. Same return shape
    as run_sweep: (theta, x_clean, x_noised, n_done). Reuse for the 5k run.
    """
    n_draw = int(np.ceil(n / 0.85))
    thetas = sample_prior(n_draw, np.random.default_rng(seed))
    done: set[int] = set()
    th_ok: list = []
    xc: list = []
    xn: list = []
    xw: list = []  # clean (12, T_i) waveforms, variable length per draw

    if checkpoint_path and Path(checkpoint_path).exists():
        with np.load(checkpoint_path) as d:  # context-close so the later atomic replace works
            done = {int(i) for i in d["done"]}
            th_ok = list(d["theta"]) if d["theta"].size else []
            xc = list(d["x_clean"]) if d["x_clean"].size else []
            xn = list(d["x_noised"]) if d["x_noised"].size else []
            if "x_wave" in d and d["x_wave"].size:  # unpad back to per-draw (12, T_i)
                lens = d["x_wave_len"]
                xw = [d["x_wave"][k, :, : int(lens[k])] for k in range(d["x_wave"].shape[0])]
        print(f"[sweep] resumed: {len(th_ok)} usable from {len(done)} done draws", flush=True)

    def _save() -> None:
        if not checkpoint_path:
            return
        tmp = str(checkpoint_path) + ".tmp.npz"  # must end in .npz; np.savez appends it otherwise
        wave, wave_len = _stack_waves(xw)
        np.savez(
            tmp,
            done=np.array(sorted(done), dtype=int),
            theta=np.array(th_ok, dtype=float),
            x_clean=np.array(xc, dtype=float),
            x_noised=np.array(xn, dtype=float),
            x_wave=wave,  # (usable, 12, T_max) zero-padded clean waveforms
            x_wave_len=wave_len,  # (usable,) true T_i per draw
        )
        _os.replace(tmp, checkpoint_path)

    todo = [i for i in range(n_draw) if i not in done]
    if todo and len(th_ok) < n:
        with ProcessPoolExecutor(max_workers=n_workers, initializer=_init_worker) as ex:
            futs = {
                ex.submit(_run_one, (thetas[i], noise_sigma_mv, seed + 1000 + i)): i for i in todo
            }
            completed = 0
            for fut in as_completed(futs):
                done.add(futs[fut])
                r = fut.result()
                if r is not None:
                    th_ok.append(r[0])
                    xc.append(r[1])
                    xn.append(r[2])
                    xw.append(np.asarray(r[3], dtype=float))
                completed += 1
                if completed % save_every == 0:
                    _save()
                    print(f"[sweep] {len(th_ok)} usable, {len(done)}/{n_draw} draws", flush=True)
                if len(th_ok) >= n:
                    break
    _save()
    return (
        np.array(th_ok, dtype=float),
        np.array(xc, dtype=float),
        np.array(xn, dtype=float),
        len(done),
    )
