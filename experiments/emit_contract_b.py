"""Emit a Contract-B JSON from a sweep checkpoint so the demo and /infer bind to REAL posteriors.

Trains the features NPE on the checkpoint, fits per-parameter conformal inflation on a held-out
split, and writes outputs/<tag>_results.json in the frozen Contract-B shape
(ui/mock/contract_b.schema.json) plus the approved additive v2 fields (prior, reference_theta,
param_meta, a calibration block, synthetic_truth). Works on a 6D checkpoint (cv_myo was fixed at
the mesh default; padded as a fixed 7th param so theta_names stays length 7) or a 7D checkpoint.

The single demo observation is the re-anchored REFERENCE operating point: input_ecg =
forward(REFERENCE_THETA restricted to the checkpoint's params), and the posterior is the NPE
conditioned on its features. Everything is labeled synthetic-truth, never real-ECG-validated.

Run:  CKPT_PATH=outputs/day3_6d_ckpt.npz uv run python experiments/emit_contract_b.py
Fast structural check (no forward, tiny train):
      DRY=1 EMIT_ECG=0 CKPT_PATH=outputs/day2_sweep_ckpt.npz OUT_JSON=outputs/_emit_validate.json \
      uv run python experiments/emit_contract_b.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from sbi.inference import NPE  # noqa: E402
from sbi.utils import BoxUniform  # noqa: E402

from calib.conformal import (  # noqa: E402
    central_coverage,
    draw_sample_sets,
    fit_inflation,
    recalibrate,
    sbc_ks_pvals,
)
from calib.diagnostics import run_tarp_check  # noqa: E402
from core.features import extract_features  # noqa: E402
from core.noise import DEFAULT_WAVEFORM_SIGMA_MV, to_physiological_mv  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402
from sim.forward import REFERENCE_THETA  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
CKPT = Path(os.getenv("CKPT_PATH", str(OUT / "day2_sweep_ckpt.npz")))
DRY = bool(int(os.getenv("DRY", "0")))
EMIT_ECG = bool(int(os.getenv("EMIT_ECG", "1")))  # 0 = no forward (fast structural check)
PPC_N = int(os.getenv("PPC_N", "6"))  # posterior-predictive band samples (extra forwards)
N_CALIB = 20 if DRY else int(os.getenv("N_CALIB", "250"))
N_TRAIN = 60 if DRY else int(os.getenv("N_TRAIN", "1000"))
N_POST = 100 if DRY else int(os.getenv("N_POST", "300"))
LEVEL = 0.9
FULL_NAMES = list(THETA_NAMES) + (["cv_myo"] if "cv_myo" not in THETA_NAMES else [])
LEADS = ("I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6")

# Contract A param 7 fallback bounds (present in PRIOR_BOUNDS only after the 7D flip).
CV_MYO_PRIOR = (0.5, 1.0)
PARAM_META = {
    "cv": ("CV_pk", "m/s", "constraint", "Purkinje conduction velocity"),
    "delta_iv": ("dIV", "ms", "constraint", "LV-RV interventricular delay"),
    "init_length_lv": ("L0_LV", "mm", "constraint", "LV initial length"),
    "init_length_rv": ("L0_RV", "mm", "constraint", "RV initial length"),
    "branch_angle": ("alpha", "rad", "diffuse", "branch angle"),
    "w": ("w", "-", "diffuse", "branch divergence"),
    "cv_myo": ("CV_myo", "m/s", "constraint", "myocardial conduction velocity"),
}


def _bounds(name: str) -> tuple[float, float]:
    return PRIOR_BOUNDS.get(name, CV_MYO_PRIOR if name == "cv_myo" else (0.0, 1.0))


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def _train(theta, x):
    torch.manual_seed(0)
    lo = torch.tensor([_bounds(k)[0] for k in THETA_NAMES], dtype=torch.float32)
    hi = torch.tensor([_bounds(k)[1] for k in THETA_NAMES], dtype=torch.float32)
    inf = NPE(prior=BoxUniform(low=lo, high=hi))
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train()
    return inf.build_posterior()


def _coverage_curve(theta_ca, sets, t):
    levels = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    before = [
        float(central_coverage(theta_ca, sets, np.ones(sets.shape[2]), lv).mean()) for lv in levels
    ]
    after = [float(central_coverage(theta_ca, sets, t, lv).mean()) for lv in levels]
    return {"nominal": levels, "before": before, "after": after}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    out_json = Path(
        os.getenv("OUT_JSON", str(OUT / (CKPT.stem.replace("_ckpt", "") + "_results.json")))
    )

    with np.load(CKPT) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    ncol = theta.shape[1]
    names = list(THETA_NAMES[:ncol])  # inferred params in this checkpoint (cv_myo appended last)
    print(
        f"[emit] ckpt={CKPT.name} rows={theta.shape[0]} inferred={ncol} params={names}", flush=True
    )

    n_tr = min(N_TRAIN, theta.shape[0] - N_CALIB)
    th_tr, x_tr = theta[:n_tr], x[:n_tr]
    th_ca, x_ca = theta[n_tr : n_tr + N_CALIB], x[n_tr : n_tr + N_CALIB]
    prior_std = th_tr.std(axis=0)

    post = _train(th_tr, x_tr)
    sets = draw_sample_sets(post, x_ca, N_POST)  # (M, N, ncol)
    t = fit_inflation(th_ca, sets)
    ks_before = sbc_ks_pvals(th_ca, sets, np.ones(ncol))
    ks_after = sbc_ks_pvals(th_ca, sets, t)
    cov_after = central_coverage(th_ca, sets, t, LEVEL)
    contr_raw = np.median(sets.std(axis=1), axis=0) / prior_std
    contr_after = t * contr_raw
    try:
        tarp = run_tarp_check(post, th_ca, x_ca, n_post=min(N_POST, 200))
        tarp_atc = float(tarp["atc"])
    except Exception as e:
        print(f"[emit] TARP skipped: {type(e).__name__}: {e}", flush=True)
        tarp_atc = None

    # --- the single demo observation: the re-anchored REFERENCE operating point ---
    obs_theta = {k: float(REFERENCE_THETA[k]) for k in names}  # 6D drops cv_myo -> default myo
    cv_myo_fixed = None
    if EMIT_ECG:
        from sim.forward import forward, load_geometry

        geom = load_geometry()
        cv_myo_fixed = float(geom._cv_fiber_base) if ncol < 7 else None
        input_ecg = to_physiological_mv(np.asarray(forward(obs_theta, geom), float))  # (12, T) mV
        x_obs = extract_features(input_ecg)
        true_theta = dict(obs_theta)
    else:
        # structural / fast path: use a held-out calibration observation (features already stored)
        input_ecg = np.zeros((12, 2), float)
        x_obs = x_ca[0]
        true_theta = {k: float(v) for k, v in zip(names, th_ca[0], strict=False)}
        cv_myo_fixed = 0.866 if ncol < 7 else None

    raw = np.asarray(
        post.sample((2000,), x=torch.tensor(x_obs, dtype=torch.float32), show_progress_bars=False)
    )
    samples = recalibrate(raw, t)  # per-parameter conformal-inflated posterior samples
    mean, std = samples.mean(axis=0), samples.std(axis=0)

    # --- posterior-predictive ECG (optional forwards) ---
    ppc = {"signal": input_ecg.tolist()}
    if EMIT_ECG and PPC_N > 0:
        from sim.forward import forward as _fwd

        sig = to_physiological_mv(
            np.asarray(_fwd({k: float(mean[i]) for i, k in enumerate(names)}, geom), float)
        )
        band = []
        for row in samples[np.random.default_rng(0).integers(0, samples.shape[0], PPC_N)]:
            try:
                band.append(
                    to_physiological_mv(
                        np.asarray(
                            _fwd({k: float(row[i]) for i, k in enumerate(names)}, geom), float
                        )
                    )
                )
            except Exception:
                continue
        ppc = {"signal": sig.tolist()}
        if band:
            T = min(b.shape[1] for b in [sig, *band])
            stack = np.stack([b[:, :T] for b in band])
            ppc["signal"] = sig[:, :T].tolist()
            ppc["band_lo"] = np.percentile(stack, 5, axis=0).tolist()
            ppc["band_hi"] = np.percentile(stack, 95, axis=0).tolist()

    # --- assemble per-parameter maps over the full 7-name contract (pad fixed cv_myo) ---
    def per_param(inferred_vals, fixed_val):
        out = {}
        for i, k in enumerate(FULL_NAMES):
            out[k] = float(inferred_vals[i]) if i < ncol else float(fixed_val)
        return out

    posterior = {
        "samples": (
            np.column_stack([samples, np.full(samples.shape[0], cv_myo_fixed)]).tolist()
            if ncol < 7
            else samples.tolist()
        ),
        "mean": per_param(mean, cv_myo_fixed),
        "std": per_param(std, 0.0),
        "prior_bounds": {k: list(_bounds(k)) for k in FULL_NAMES},
        "contraction": per_param(contr_after, 0.0),  # cv_myo fixed => 0 contraction
        "coverage": per_param(cov_after, 1.0),
    }
    calibration = {
        "coverage_curve": _coverage_curve(th_ca, sets, t),
        "sbc": {
            k: {"before": float(ks_before[i]), "after": float(ks_after[i])}
            for i, k in enumerate(names)
        },
        "sbc_ks_pvalue": float(np.median(ks_after)),
        "tarp_atc": tarp_atc,
        "conformal_t": {k: float(t[i]) for i, k in enumerate(names)},
        "note": "conformal_t is per-parameter (marginal SBC); tarp_atc is pre-conformal (joint).",
    }
    artifact = {
        "run_id": f"{out_json.stem}-{_git_sha()}",
        "geometry_id": "cardiac_demo",
        "theta_names": FULL_NAMES,
        "observation_kind": "features",
        "synthetic_truth": True,
        "true_theta": per_param([true_theta[k] for k in names], cv_myo_fixed),
        "reference_theta": {k: float(REFERENCE_THETA[k]) for k in FULL_NAMES},
        "prior": {k: list(_bounds(k)) for k in FULL_NAMES},
        "param_meta": {
            k: dict(zip(("alias", "unit", "block", "label"), PARAM_META[k], strict=False))
            for k in FULL_NAMES
        },
        "input_ecg": {"leads": list(LEADS), "signal": input_ecg.tolist(), "fs_hz": 500},
        "posterior": posterior,
        "posterior_predictive_ecg": ppc,
        "calibration": calibration,
        "noise_model": {"kind": "waveform", "sigma": DEFAULT_WAVEFORM_SIGMA_MV},
        "meta": {
            "sim_budget": int(theta.shape[0]),
            "sbi_method": "NPE",
            "seed": 0,
            "git_sha": _git_sha(),
            "synthetic_truth": True,
            "n_params_inferred": ncol,
            "cv_myo_fixed": cv_myo_fixed,
            "ecg_stub": not EMIT_ECG,
        },
    }

    out_json.write_text(json.dumps(artifact, indent=1))
    print(f"[emit] wrote {out_json} ({out_json.stat().st_size} bytes)", flush=True)
    _validate(artifact)


def _validate(artifact: dict) -> None:
    """Check the artifact against the frozen schema (jsonschema if present, else required keys).

    The schema lives under ui/ which is not shipped in the CLI image; if it is absent, skip
    validation rather than fail the run (the artifact is already written)."""
    schema_path = Path(__file__).resolve().parents[1] / "ui" / "mock" / "contract_b.schema.json"
    if not schema_path.is_file():
        print(f"[emit] schema check skipped (schema not present at {schema_path})", flush=True)
        return
    schema = json.loads(schema_path.read_text())
    try:
        import jsonschema

        jsonschema.validate(artifact, schema)
        print("[emit] schema OK (jsonschema)", flush=True)
    except ModuleNotFoundError:
        missing = [k for k in schema["required"] if k not in artifact]
        assert not missing, f"missing required Contract-B keys: {missing}"
        assert len(artifact["theta_names"]) == 7, (
            "theta_names must be length 7 (frozen 7D contract)"
        )
        for k in ("samples", "contraction", "coverage"):
            assert k in artifact["posterior"], f"posterior.{k} missing"
        print("[emit] schema OK (required-key check; jsonschema not installed)", flush=True)


if __name__ == "__main__":
    main()
