"""Re-sweep the frozen 7D snr run, storing the clean waveform, and gate on bit-reproduction.

Same seeds/theta draws as day3_7d_snr_ckpt.npz (seed=0, n=5000, sigma=Contract D 0.025 mV),
so the recomputed x_noised must reproduce the old checkpoint exactly. Because rows are stored
in completion order (nondeterministic), the gate aligns by exact theta match and compares
x_noised on the intersection, not by raw array order.

F2-GATE (hard stop): if aligned x_noised does NOT match, the forward is nondeterministic and
every calibration claim is in question. The result is written durably to
outputs/wave_resweep_gate.txt so a lost background stdout cannot hide it.

Run (overnight, ~5h): uv run --no-sync python experiments/wave_resweep.py
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from sim.sweep import run_sweep_checkpointed  # noqa: E402

SEED, N, SIGMA = 0, 5000, 0.025
OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = OUT / "day4_wave_ckpt.npz"
OLD = OUT / "day3_7d_snr_ckpt.npz"
GATE = OUT / "wave_resweep_gate.txt"


def _emit(s: str) -> None:
    print(s, flush=True)
    with open(GATE, "a") as f:
        f.write(s + "\n")


def reproduce_gate(theta_new: np.ndarray, xn_new: np.ndarray) -> bool:
    """Align new rows to the old checkpoint by exact theta match; compare x_noised."""
    old = np.load(OLD)
    th_old, xn_old = old["theta"], old["x_noised"]
    matched = tested = notfound = 0
    for k in range(theta_new.shape[0]):
        j = np.where(np.abs(th_old - theta_new[k]).max(axis=1) < 1e-9)[0]
        if len(j) == 0:
            notfound += 1
            continue
        tested += 1
        matched += int(np.array_equal(xn_new[k], xn_old[j[0]]))
    old.close()
    _emit(
        f"[gate] new={theta_new.shape[0]} matched-theta={tested} not-in-old={notfound} "
        f"| x_noised bit-identical {matched}/{tested}"
    )
    return tested > 0 and matched == tested


def main() -> None:
    OUT.mkdir(exist_ok=True)
    GATE.write_text("")
    n_workers = min(os.cpu_count() or 2, 8)
    _emit(
        f"[start] {time.strftime('%Y-%m-%d %H:%M:%S')} n={N} seed={SEED} "
        f"sigma={SIGMA} workers={n_workers}"
    )
    t = time.perf_counter()
    theta, _xc, xn, n_done = run_sweep_checkpointed(
        N, SIGMA, n_workers, seed=SEED, checkpoint_path=CKPT
    )
    _emit(f"[sweep] {theta.shape[0]} usable ({n_done} draws) in {time.perf_counter() - t:.0f}s")

    d = np.load(CKPT)
    _emit(f"[ckpt] keys={list(d.files)} x_wave={d['x_wave'].shape}")
    d.close()

    ok = reproduce_gate(theta, xn)
    _emit(
        "[F2-GATE] PASS: determinism holds, waveform asset trustworthy."
        if ok
        else "[F2-GATE] FAIL: STOP. Forward is nondeterministic; calibration in question."
    )


if __name__ == "__main__":
    main()
