"""A: why does forward(REFERENCE_THETA) match True_ecg only at corr ~0.2? Diagnostic.

Step 1 isolates the ECG synthesis: compute the ECG from the true activation field
(True_endo.vtu) and compare to True_ecg (should be ~1.0, the nb-parity check).
Step 2 scans the interventricular delay and a time-lag to see whether a timing/scenario
mismatch explains our full-forward gap, or whether our Purkinje trees/coupling are off.

Run:  uv run python experiments/forward_fidelity.py
"""

import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
from myocardial_mesh import MyocardialMesh  # noqa: E402

from sim.forward import DATA_DIR, REFERENCE_THETA, forward, load_geometry  # noqa: E402


def _stack(rec):
    return np.vstack([np.asarray(rec[n], float) for n in rec.dtype.names]), list(rec.dtype.names)


def _lead_corr(a, b):
    t = min(a.shape[1], b.shape[1])
    return float(np.mean([np.corrcoef(a[i, :t], b[i, :t])[0, 1] for i in range(a.shape[0])]))


def _shift_corr(x, y, lag):
    xa, ya = (x[lag:], y[: len(y) - lag]) if lag >= 0 else (x[: len(x) + lag], y[-lag:])
    return np.nan if len(xa) < 5 else np.corrcoef(xa, ya)[0, 1]


def _best_lag_corr(a, b, maxlag=40):
    t = min(a.shape[1], b.shape[1])
    return float(
        np.mean(
            [
                np.nanmax(
                    [_shift_corr(a[i, :t], b[i, :t], lag) for lag in range(-maxlag, maxlag + 1)]
                )
                for i in range(a.shape[0])
            ]
        )
    )


def main() -> None:
    with open(DATA_DIR / "nb" / "True_ecg", "rb") as f:
        true, true_names = _stack(pickle.load(f))
    print(f"[shapes] True_ecg {true.shape} leads={true_names[:3]}...")

    geom = load_geometry()

    # Step 1: nb-parity, ECG synthesized from the TRUE activation field.
    myo = MyocardialMesh(
        myo_mesh=str(DATA_DIR / "nb" / "True_endo.vtu"),
        electrodes_position=str(DATA_DIR / "electrode_pos.pkl"),
        fibers=str(DATA_DIR / "crtdemo_f0_oriented.vtk"),
    )
    nb, nb_names = _stack(myo.new_get_ecg(record_array=True))
    print(
        f"[nb-parity] leads_match={nb_names == true_names}  "
        f"ECG(True_endo) vs True_ecg: corr={_lead_corr(nb, true):.3f} (expect ~1.0)"
    )

    # Step 2: our full forward, scan interventricular delay + best time-lag.
    print("[forward scan] our trees + coupling vs True_ecg:")
    for div in (-100, -75, -50, -25, 0, 25, 50, 75, 100):
        th = dict(REFERENCE_THETA)
        th["delta_iv"] = div
        e = forward(th, geom)
        print(
            f"  delta_iv={div:+4d}: corr={_lead_corr(e, true):+.3f}  "
            f"best-lag corr={_best_lag_corr(e, true):+.3f}  (T_ours={e.shape[1]})"
        )


if __name__ == "__main__":
    main()
