"""F3: per-parameter contraction vs training-N on the day4 waveform sweep (features NPE).

Answers the H3 question the brief calls part of decision 4: is the features-NPE contraction
DATA-limited (still tightening as N grows) or FEATURE / INFORMATION-limited (plateaued above
the information floor)? We train the same 15-feature NPE the headline uses at a rising N, and
at each N compute per-parameter contraction (raw and post per-parameter conformal) on a FIXED
held-out calibration split, so only the training budget changes between points.

Two reference lines are overlaid, both expressed as a contraction (value / prior_std) so they
sit on the same axis as the observed numbers:
  - crlb_floor: the WAVEFORM Cramer-Rao bound (outputs/jacobian.json fim.crlb). This is the
    best case an estimator that observed the full 12-lead waveform could reach at theta*. The
    15-feature NPE observes a lossy summary, so it cannot beat this and is expected to sit well
    above it. A large, N-independent gap to this floor is the signature of feature loss.

Design choices (stated for honesty): a single fixed calibration split (the last N_CALIB rows)
is held out from every fit; the contraction denominator prior_std is fixed (empirical std over
all 5000 theta) so only the posterior width moves with N; the CRLB is LOCAL at theta* while
contraction is prior-averaged, so the floor is a best-case reference, not a target the
features-NPE should reach.

Training-only, no forwards, no new sims.
Run: uv run --no-sync python experiments/f3_contraction_vs_n.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from calib.conformal import draw_sample_sets, fit_inflation  # noqa: E402
from core.theta import THETA_NAMES  # noqa: E402
from npe.emit import _train  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CKPT = REPO / "outputs" / "day4_wave_ckpt.npz"
JAC = REPO / "outputs" / "jacobian.json"
OUT = REPO / "outputs" / "f3_contraction_vs_n.json"

N_CALIB = 250
N_POST = 300
# Start at 1000 (the headline emit config) up to 4750. Default training (TRAIN_KWARGS={})
# gives well-trained flows with low prior leakage; capping epochs undertrained the flow and
# sent DirectPosterior.sample into a rejection-sampling spin, so we do NOT cap here.
N_SCHEDULE = [1000, 1500, 2000, 3000, 4000, 4750]
TRAIN_KWARGS: dict = {}  # {} reproduces the default training the headline used


def _contraction_at(th_tr, x_tr, th_ca, x_ca, prior_std, ncol):
    """Train on (th_tr, x_tr); return (raw, post) per-param contraction on the fixed calib set."""
    post = _train(th_tr, x_tr, **TRAIN_KWARGS)
    sets = draw_sample_sets(post, x_ca, N_POST)  # (M, N_POST, ncol)
    t = fit_inflation(th_ca, sets)
    contr_raw = np.median(sets.std(axis=1), axis=0) / prior_std
    return contr_raw, t * contr_raw


def main() -> None:
    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    ncol = theta.shape[1]
    names = list(THETA_NAMES[:ncol])
    prior_std = theta.std(axis=0)  # fixed denominator across all N

    # fixed held-out calibration split (last N_CALIB rows, never in any training set)
    th_ca, x_ca = theta[-N_CALIB:], x[-N_CALIB:]
    pool_th, pool_x = theta[:-N_CALIB], x[:-N_CALIB]
    schedule = [n for n in N_SCHEDULE if n <= pool_th.shape[0]]
    print(
        f"[f3] rows={theta.shape[0]} pool={pool_th.shape[0]} calib={N_CALIB} "
        f"schedule={schedule} params={names}",
        flush=True,
    )

    jac = json.loads(JAC.read_text())
    crlb = jac["fim"]["crlb"]
    crlb_floor = {k: float(crlb[k]) / float(prior_std[i]) for i, k in enumerate(names)}

    rows = []
    for n in schedule:
        t0 = time.perf_counter()
        raw, postc = _contraction_at(pool_th[:n], pool_x[:n], th_ca, x_ca, prior_std, ncol)
        rows.append(
            {
                "n_train": n,
                "raw": {k: float(raw[i]) for i, k in enumerate(names)},
                "post_conformal": {k: float(postc[i]) for i, k in enumerate(names)},
            }
        )
        dt = time.perf_counter() - t0
        pretty = "  ".join(f"{k}={postc[i]:.3f}" for i, k in enumerate(names))
        print(f"[f3] N={n:5d} ({dt:.0f}s) post-conformal: {pretty}", flush=True)

    # verdict per param: is it still decreasing at the top of the schedule, or plateaued?
    verdict = {}
    if len(rows) >= 2:
        last, prev = rows[-1]["post_conformal"], rows[-2]["post_conformal"]
        for k in names:
            drop = (prev[k] - last[k]) / prev[k] if prev[k] else 0.0
            verdict[k] = {
                "post_conformal_final": last[k],
                "rel_change_last_step": float(drop),
                "crlb_floor": crlb_floor[k],
                "gap_to_floor": float(last[k] - crlb_floor[k]),
                # >5% still-falling => data-limited; else plateaued (feature/information-limited)
                "label": "data-limited" if drop > 0.05 else "plateaued",
            }

    out = {
        "meta": {
            "analysis": "F3 contraction vs training-N, features NPE on the day4 waveform sweep",
            "ckpt": CKPT.name,
            "n_calib": N_CALIB,
            "n_post": N_POST,
            "schedule": schedule,
            "prior_std": {k: float(prior_std[i]) for i, k in enumerate(names)},
            "train_kwargs": TRAIN_KWARGS,
            "note": (
                "crlb_floor is the WAVEFORM Cramer-Rao bound (jacobian.json) as a contraction; "
                "a best-case local floor the lossy 15-feature NPE is not expected to reach. "
                "label: >5% relative drop on the last schedule step => data-limited, else "
                "plateaued (feature/information-limited at this feature set)."
            ),
        },
        "crlb_floor": crlb_floor,
        "curve": rows,
        "verdict": verdict,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(f"[f3] wrote {OUT}", flush=True)
    print("[f3] verdict:", flush=True)
    for k, v in verdict.items():
        print(
            f"  {k:16s} final={v['post_conformal_final']:.3f} "
            f"floor={v['crlb_floor']:.4f} last-step drop={v['rel_change_last_step']:+.1%} "
            f"-> {v['label']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
