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
N_SBC = 250
N_POST = 300
# Two points at 1000 and 4000, three training seeds each. 4750 is dropped: it leaves too few
# rows for two disjoint 250-row holdouts. Default training (TRAIN_KWARGS={}) reproduces the
# headline flow (capping epochs undertrained it and spun sampling), so we do NOT cap.
N_SCHEDULE = [1000, 4000]
SEEDS = (0, 1, 2)
TRAIN_KWARGS: dict = {}  # {} reproduces the default training the headline used


def _contraction_at(th_tr, x_tr, th_ca, x_ca, th_sbc, x_sbc, prior_std, seed):
    """Train on (th_tr, x_tr) at `seed`; fit conformal inflation on the calibration set, then
    return (raw, post) per-param contraction measured on the DISJOINT SBC set (never used to fit
    inflation), so the fit set and the reported set do not overlap."""
    post = _train(th_tr, x_tr, seed=seed, **TRAIN_KWARGS)
    t = fit_inflation(th_ca, draw_sample_sets(post, x_ca, N_POST))
    sets_sbc = draw_sample_sets(post, x_sbc, N_POST)  # (M, N_POST, ncol) on the held-out SBC set
    contr_raw = np.median(sets_sbc.std(axis=1), axis=0) / prior_std
    return contr_raw, t * contr_raw


def _agg(vals):
    """median + spread across seeds for one parameter."""
    return {
        "median": float(np.median(vals)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "spread": float(np.max(vals) - np.min(vals)),
    }


def main() -> None:
    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    ncol = theta.shape[1]
    names = list(THETA_NAMES[:ncol])
    prior_std = theta.std(axis=0)  # fixed denominator across all N

    # Two fixed, disjoint holdouts carved first, never in any training set: the calibration set
    # (last N_CALIB rows) fits the conformal inflation; the SBC set (the N_SBC rows before it)
    # is where contraction/SBC are measured. pool is everything before both.
    th_ca, x_ca = theta[-N_CALIB:], x[-N_CALIB:]
    th_sbc, x_sbc = theta[-(N_CALIB + N_SBC) : -N_CALIB], x[-(N_CALIB + N_SBC) : -N_CALIB]
    pool_th, pool_x = theta[: -(N_CALIB + N_SBC)], x[: -(N_CALIB + N_SBC)]
    schedule = [n for n in N_SCHEDULE if n <= pool_th.shape[0]]
    print(
        f"[f3] rows={theta.shape[0]} pool={pool_th.shape[0]} calib={N_CALIB} sbc={N_SBC} "
        f"schedule={schedule} seeds={SEEDS} params={names}",
        flush=True,
    )

    jac = json.loads(JAC.read_text())
    crlb = jac["fim"]["crlb"]
    crlb_floor = {k: float(crlb[k]) / float(prior_std[i]) for i, k in enumerate(names)}

    rows = []
    for n in schedule:
        per_seed = []
        for seed in SEEDS:
            t0 = time.perf_counter()
            raw, postc = _contraction_at(
                pool_th[:n], pool_x[:n], th_ca, x_ca, th_sbc, x_sbc, prior_std, seed
            )
            per_seed.append(
                {
                    "seed": seed,
                    "raw": {k: float(raw[i]) for i, k in enumerate(names)},
                    "post_conformal": {k: float(postc[i]) for i, k in enumerate(names)},
                }
            )
            pretty = "  ".join(f"{k}={postc[i]:.3f}" for i, k in enumerate(names))
            print(
                f"[f3] N={n:5d} seed={seed} ({time.perf_counter() - t0:.0f}s) post: {pretty}",
                flush=True,
            )
        agg = {k: _agg([ps["post_conformal"][k] for ps in per_seed]) for k in names}
        rows.append({"n_train": n, "per_seed": per_seed, "post_conformal_agg": agg})

    # Per-param verdict on the seed-median trend, and whether the seed spread swallows it.
    verdict = {}
    if len(rows) >= 2:
        lo_n, hi_n = rows[0], rows[-1]
        for k in names:
            med_lo = lo_n["post_conformal_agg"][k]["median"]
            med_hi = hi_n["post_conformal_agg"][k]["median"]
            trend = med_lo - med_hi  # positive = tightened with N
            max_spread = max(
                lo_n["post_conformal_agg"][k]["spread"], hi_n["post_conformal_agg"][k]["spread"]
            )
            verdict[k] = {
                "median_at_min_N": med_lo,
                "median_at_max_N": med_hi,
                "median_trend": float(trend),
                "max_seed_spread": float(max_spread),
                "crlb_floor": crlb_floor[k],
                # if the seed spread is >= the median trend, the curve is uninformative for k
                "label": "trend-below-seed-noise"
                if abs(trend) <= max_spread
                else ("data-limited" if trend > 0 else "widening"),
            }

    out = {
        "meta": {
            "analysis": "F3 contraction vs training-N, features NPE, 3 seeds, disjoint calib+SBC",
            "ckpt": CKPT.name,
            "n_calib": N_CALIB,
            "n_sbc": N_SBC,
            "n_post": N_POST,
            "schedule": schedule,
            "seeds": list(SEEDS),
            "prior_std": {k: float(prior_std[i]) for i, k in enumerate(names)},
            "train_kwargs": TRAIN_KWARGS,
            "note": (
                "Calibration and SBC sets are fixed and disjoint (inflation fit on calib, "
                "contraction measured on SBC). crlb_floor is the WAVEFORM Cramer-Rao bound "
                "(jacobian.json) as a contraction, a best-case local floor. label: "
                "'trend-below-seed-noise' means the seed spread swallows the N trend for that "
                "parameter (curve uninformative); else 'data-limited' (still tightening) or "
                "'widening'."
            ),
        },
        "crlb_floor": crlb_floor,
        "curve": rows,
        "verdict": verdict,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(f"[f3] wrote {OUT}", flush=True)
    print("[f3] verdict (seed-median trend vs seed spread):", flush=True)
    for k, v in verdict.items():
        print(
            f"  {k:16s} lo={v['median_at_min_N']:.3f} hi={v['median_at_max_N']:.3f} "
            f"trend={v['median_trend']:+.3f} spread={v['max_seed_spread']:.3f} -> {v['label']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
