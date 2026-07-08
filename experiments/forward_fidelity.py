"""Honest forward-vs-True_ecg fidelity metric (critic-corrected).

The earlier version reported mean best-lag correlation (~0.86), which launders three real
defects because correlation is scale/offset invariant and per-lead lag-max hides broken
leads. This reports per-lead nRMSE (residual std / true std) and amplitude ratio
(std(ours)/std(true)) plus a lead-III diagnostic, which do NOT launder. It is a KNOWN GAP,
not a pass: the forward does not yet reproduce True_ecg (nb-parity clears synthesis only).

Step 1: nb-parity (ECG synthesized from the TRUE activation vs True_ecg, expect ~1.0).
Step 2: our full forward at REFERENCE_THETA vs True_ecg, per-lead nRMSE + amplitude ratio.
Step 3: coarse delta_iv scan showing nRMSE stays ~1 across the range (delta_iv cannot fix it).

Run:  uv run python experiments/forward_fidelity.py
"""

import hashlib
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
from myocardial_mesh import MyocardialMesh  # noqa: E402

from sim.forward import DATA_DIR, REFERENCE_THETA, forward, load_geometry  # noqa: E402

SEED = 0


def _stack(rec):
    return np.vstack([np.asarray(rec[n], float) for n in rec.dtype.names]), list(rec.dtype.names)


def _lead_corr(a, b):
    t = min(a.shape[1], b.shape[1])
    return np.array([np.corrcoef(a[i, :t], b[i, :t])[0, 1] for i in range(a.shape[0])])


def _nrmse(a, b):
    """Per-lead residual std / true std (b = truth). ~0 is a match, ~1 is 'residual == signal'."""
    t = min(a.shape[1], b.shape[1])
    a, b = a[:, :t], b[:, :t]
    resid = np.std(a - b, axis=1)
    denom = np.maximum(np.std(b, axis=1), 1e-12)
    return resid / denom


def _amp_ratio(a, b):
    t = min(a.shape[1], b.shape[1])
    return np.std(a[:, :t], axis=1) / np.maximum(np.std(b[:, :t], axis=1), 1e-12)


def main() -> None:
    np.random.seed(SEED)  # tree growth uses the global RNG; seed for a reproducible table
    raw = (DATA_DIR / "nb" / "True_ecg").read_bytes()
    print(f"[digest] True_ecg sha256={hashlib.sha256(raw).hexdigest()[:16]}  seed={SEED}")
    true, true_names = _stack(pickle.loads(raw))
    print(f"[shapes] True_ecg {true.shape} leads={true_names}")

    geom = load_geometry()

    # Step 1: nb-parity, ECG synthesized from the TRUE activation field.
    myo = MyocardialMesh(
        myo_mesh=str(DATA_DIR / "nb" / "True_endo.vtu"),
        electrodes_position=str(DATA_DIR / "electrode_pos.pkl"),
        fibers=str(DATA_DIR / "crtdemo_f0_oriented.vtk"),
    )
    nb, _ = _stack(myo.new_get_ecg(record_array=True))
    print(
        f"\n[nb-parity] ECG(True_endo) vs True_ecg: mean corr={_lead_corr(nb, true).mean():.3f}"
        f"  mean nRMSE={_nrmse(nb, true).mean():.3f}  (synthesis exact => ~1.0 / ~0.0)"
    )

    # Step 2: our full forward at the reference, honest per-lead table.
    e = forward(REFERENCE_THETA, geom)
    corr, nrmse, amp = _lead_corr(e, true), _nrmse(e, true), _amp_ratio(e, true)
    print(
        f"\n[forward @ REFERENCE_THETA] ours {e.shape}  ours-std range "
        f"{np.std(e, axis=1).min():.3g}..{np.std(e, axis=1).max():.3g} (mV if calibrated)"
    )
    print(f"  {'lead':6s} {'corr':>7s} {'nRMSE':>7s} {'amp_ratio':>10s}")
    for i, nm in enumerate(true_names):
        flag = "  <- broken" if corr[i] < 0.2 else ""
        print(f"  {nm:6s} {corr[i]:7.2f} {nrmse[i]:7.2f} {amp[i]:10.2f}{flag}")
    print(f"  {'MEAN':6s} {corr.mean():7.2f} {nrmse.mean():7.2f} {amp.mean():10.2f}")
    print(
        "  READ: mean nRMSE near 1 and amp_ratio far from 1 => KNOWN GAP, not real-ECG validated."
    )

    # Step 3: coarse delta_iv scan, nRMSE stays ~1 (a relative delay cannot close the gap).
    print("\n[delta_iv scan] mean nRMSE / mean corr vs relative LV-RV delay:")
    for div in (-100, -75, -50, -25, 0, 25):
        th = dict(REFERENCE_THETA)
        th["delta_iv"] = div
        ei = forward(th, geom)
        print(
            f"  delta_iv={div:+4d}: nRMSE={_nrmse(ei, true).mean():.3f}  "
            f"corr={_lead_corr(ei, true).mean():+.3f}"
        )


if __name__ == "__main__":
    main()
