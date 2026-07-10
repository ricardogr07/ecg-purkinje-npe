"""F8 robustness retrains on the stored waveforms (pre-registered, no forwards, no new sims).

Reads outputs/day4_wave_ckpt.npz (theta, x_wave clean physiological-mV waveforms, x_wave_len).
Re-noises + re-features + retrains the same features NPE the headline uses, on the SAME fixed
calibration split as F3 (pool = first 4750, calib = last 250, prior_std over all 5000,
n_post = 300). Primary metric: PRE-conformal contraction (post-conformal recorded for context).

PRE-REGISTERED PASS CRITERION (ordering, not levels): at each stressed corner, for BOTH noise
seeds, max(identifiable-4 pre-conformal contraction) < min(diffuse-3). identifiable-4 =
{delta_iv, cv_myo, init_length_rv, cv}; diffuse-3 = {branch_angle, w, init_length_lv}. A flip on
either seed at either corner is FAIL/inconclusive, reported honestly.

Part A (waveform-injection noise, comparable to headline/F3): operating (0.025 mV, x1.0),
Corner A high-noise (0.10 mV, x1.0), Corner B high-amplitude (0.025 mV, 2.0 mV = x1.333).
Part B (feature-level noise, amp mV floor + timing fixed ms floor, NOT headline-comparable):
operating and 2.0 mV amplitudes. Because the timing floor is amplitude-independent here, the
amplitude-vs-timing prediction is testable: init_length_rv should tighten between operating and
2.0 mV while delta_iv should not move.

Run (serialized, one torch job at a time): .venv/Scripts/python.exe experiments/f8_robustness.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from calib.conformal import draw_sample_sets, fit_inflation  # noqa: E402
from core.features import extract_features  # noqa: E402
from core.noise import add_feature_noise, add_waveform_noise_absolute  # noqa: E402
from core.theta import THETA_NAMES  # noqa: E402
from npe.emit import _train  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CKPT = REPO / "outputs" / "day4_wave_ckpt.npz"
OUT = REPO / "outputs" / "f8_robustness.json"

N_TRAIN = 4750  # F3's most-stable point; pool = first 4750
N_CALIB = 250  # last 250 (F3 split)
N_POST = 300
FS_HZ = 500.0
SEEDS = [0, 1]

IDENTIFIABLE = ["delta_iv", "cv_myo", "init_length_rv", "cv"]
DIFFUSE = ["branch_angle", "w", "init_length_lv"]

AMP_OP = 1.0  # operating amplitude (x_wave already at physiological ~1.5 mV)
AMP_HI = 2.0 / 1.5  # re-anchor the 1.5 mV target to 2.0 mV (uniform scalar)

# feature-level floors: QRSense single-measurement LoA (ledger): 0.05 mV amp, 5 ms timing
SIGMA_AMP_MV = 0.05
SIGMA_TIME_MS = 5.0

WAVEFORM_CORNERS = [
    {"name": "operating", "amp": AMP_OP, "sigma": 0.025, "stress": "anchor"},
    {"name": "cornerA_highnoise", "amp": AMP_OP, "sigma": 0.10, "stress": "identifiable"},
    {"name": "cornerB_highamp", "amp": AMP_HI, "sigma": 0.025, "stress": "diffuse"},
]
FEATURELEVEL_CORNERS = [
    {"name": "fl_operating", "amp": AMP_OP},
    {"name": "fl_highamp", "amp": AMP_HI},
]


def _features_waveform(x_wave, lens, amp, sigma_mv, seed):
    rng = np.random.default_rng(seed)
    X = np.empty((len(lens), 15), dtype=float)
    for i in range(len(lens)):
        w = x_wave[i, :, : int(lens[i])] * amp
        X[i] = extract_features(add_waveform_noise_absolute(w, sigma_mv, rng))
    return X


def _features_featurelevel(x_wave, lens, amp, seed):
    rng = np.random.default_rng(seed)
    X = np.empty((len(lens), 15), dtype=float)
    for i in range(len(lens)):
        w = x_wave[i, :, : int(lens[i])] * amp
        clean = extract_features(w)
        X[i] = add_feature_noise(clean, SIGMA_AMP_MV, SIGMA_TIME_MS, int(lens[i]), FS_HZ, rng)
    return X


def _contraction(X, theta, prior_std, names):
    """Train on first N_TRAIN, calib on last N_CALIB; return (raw, post) per-param contraction."""
    th_tr, x_tr = theta[:N_TRAIN], X[:N_TRAIN]
    th_ca, x_ca = theta[-N_CALIB:], X[-N_CALIB:]
    post = _train(th_tr, x_tr)
    sets = draw_sample_sets(post, x_ca, N_POST)  # (N_CALIB, N_POST, D)
    t = fit_inflation(th_ca, sets)
    raw = np.median(sets.std(axis=1), axis=0) / prior_std
    return {k: float(raw[i]) for i, k in enumerate(names)}, {
        k: float((t * raw)[i]) for i, k in enumerate(names)
    }


def _ordering_ok(raw: dict) -> bool:
    return max(raw[k] for k in IDENTIFIABLE) < min(raw[k] for k in DIFFUSE)


def main() -> None:
    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x_wave = np.array(d["x_wave"], float)
        lens = np.array(d["x_wave_len"], int)
    names = list(THETA_NAMES[: theta.shape[1]])
    prior_std = theta.std(axis=0)
    print(
        f"[f8] rows={theta.shape[0]} x_wave={x_wave.shape} N_train={N_TRAIN} params={names}",
        flush=True,
    )

    results = {
        "meta": {
            "ckpt": CKPT.name,
            "n_train": N_TRAIN,
            "n_calib": N_CALIB,
            "n_post": N_POST,
            "seeds": SEEDS,
            "identifiable": IDENTIFIABLE,
            "diffuse": DIFFUSE,
            "amp_operating": AMP_OP,
            "amp_high": AMP_HI,
            "sigma_amp_mv": SIGMA_AMP_MV,
            "sigma_time_ms": SIGMA_TIME_MS,
            "criterion": "pre-conformal: max(identifiable-4) < min(diffuse-3), both seeds",
            "prior_std": {k: float(prior_std[i]) for i, k in enumerate(names)},
        },
        "part_a_waveform": [],
        "part_b_featurelevel": [],
    }

    # --- Part A: waveform-injection ordering ---
    for corner in WAVEFORM_CORNERS:
        seed_rows = []
        for seed in SEEDS:
            t0 = time.perf_counter()
            X = _features_waveform(x_wave, lens, corner["amp"], corner["sigma"], seed)
            raw, post = _contraction(X, theta, prior_std, names)
            ok = _ordering_ok(raw)
            seed_rows.append({"seed": seed, "raw": raw, "post_conformal": post, "ordering_ok": ok})
            mx = max(raw[k] for k in IDENTIFIABLE)
            mn = min(raw[k] for k in DIFFUSE)
            print(
                f"[f8][A] {corner['name']} seed={seed} ({time.perf_counter() - t0:.0f}s) "
                f"max(ident)={mx:.3f} min(diff)={mn:.3f} ordering={'OK' if ok else 'FLIP'}",
                flush=True,
            )
        results["part_a_waveform"].append(
            {
                "corner": corner["name"],
                "amp": corner["amp"],
                "sigma": corner["sigma"],
                "stress": corner["stress"],
                "seeds": seed_rows,
                "pass": all(r["ordering_ok"] for r in seed_rows),
            }
        )

    # --- Part B: feature-level amp-vs-timing ---
    for corner in FEATURELEVEL_CORNERS:
        seed_rows = []
        for seed in SEEDS:
            t0 = time.perf_counter()
            X = _features_featurelevel(x_wave, lens, corner["amp"], seed)
            raw, post = _contraction(X, theta, prior_std, names)
            seed_rows.append({"seed": seed, "raw": raw, "post_conformal": post})
            print(
                f"[f8][B] {corner['name']} seed={seed} ({time.perf_counter() - t0:.0f}s) "
                f"init_length_rv={raw['init_length_rv']:.3f} delta_iv={raw['delta_iv']:.3f}",
                flush=True,
            )
        results["part_b_featurelevel"].append(
            {
                "corner": corner["name"],
                "amp": corner["amp"],
                "seeds": seed_rows,
            }
        )

    # Part B readout: op -> hiamp deltas (mean over seeds), for the amp-vs-timing prediction
    fl = {c["corner"]: c for c in results["part_b_featurelevel"]}
    if "fl_operating" in fl and "fl_highamp" in fl:

        def mean_raw(c, k):
            return float(np.mean([r["raw"][k] for r in fl[c]["seeds"]]))

        deltas = {k: mean_raw("fl_highamp", k) - mean_raw("fl_operating", k) for k in names}
        results["part_b_amp_vs_timing"] = {
            "note": "contraction change operating -> 2.0mV under feature-level noise; "
            "prediction: init_length_rv < 0 (tightens, amp feature), delta_iv ~ 0 (timing)",
            "delta_contraction": deltas,
        }

    OUT.write_text(json.dumps(results, indent=1))
    print(f"[f8] wrote {OUT}", flush=True)
    print("[f8] Part A ordering verdicts:", flush=True)
    for c in results["part_a_waveform"]:
        print(f"  {c['corner']:20s} stress={c['stress']:12s} PASS={c['pass']}", flush=True)
    if "part_b_amp_vs_timing" in results:
        dc = results["part_b_amp_vs_timing"]["delta_contraction"]
        print(
            f"[f8] Part B (feature-level, op->2.0mV): "
            f"init_length_rv={dc['init_length_rv']:+.3f} delta_iv={dc['delta_iv']:+.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
