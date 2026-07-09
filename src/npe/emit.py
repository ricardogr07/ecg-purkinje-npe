"""Emit a Contract-B JSON from a sweep checkpoint (features NPE + per-parameter conformal).

Promoted from experiments/emit_contract_b.py so the pipeline imports and calls it directly
instead of shelling out. The former module-level env-var configuration (CKPT_PATH, OUT_JSON,
EMIT_ECG, PPC_N, N_TRAIN, N_CALIB, N_POST) is now function parameters; the thin
experiments/emit_contract_b.py shim keeps the documented env-driven CLI working.

Trains the features NPE on the checkpoint, fits per-parameter conformal inflation on a held-out
split, and writes the Contract-B artifact (ui/mock/contract_b.schema.json) plus the approved
additive v2 fields (prior, reference_theta, param_meta, a calibration block, synthetic_truth).
Works on a 6D checkpoint (cv_myo padded as a fixed 7th param so theta_names stays length 7) or a
7D checkpoint. Everything is labeled synthetic-truth, never real-ECG-validated.

The single demo observation is the re-anchored REFERENCE operating point: input_ecg =
forward(REFERENCE_THETA restricted to the checkpoint's params), and the posterior is the NPE
conditioned on its features.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import torch
from sbi.inference import NPE
from sbi.utils import BoxUniform

from calib.conformal import (
    central_coverage,
    draw_sample_sets,
    fit_inflation,
    recalibrate,
    sbc_ks_pvals,
)
from core.features import extract_features
from core.noise import DEFAULT_WAVEFORM_SIGMA_MV, to_physiological_mv
from core.theta import PRIOR_BOUNDS, THETA_NAMES
from sim.forward import REFERENCE_THETA

_REPO = Path(__file__).resolve().parents[2]
LEADS = ("I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6")
FULL_NAMES = list(THETA_NAMES) + (["cv_myo"] if "cv_myo" not in THETA_NAMES else [])
N_DEMO_SAMPLES = 2000  # posterior draws for the single demo observation

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


def _per_param(inferred_vals, fixed_val, ncol):
    out = {}
    for i, k in enumerate(FULL_NAMES):
        out[k] = float(inferred_vals[i]) if i < ncol else float(fixed_val)
    return out


def emit_contract_b(
    ckpt_path,
    out_json,
    *,
    emit_ecg: bool = True,
    ppc_n: int = 6,
    n_train: int = 1000,
    n_calib: int = 250,
    n_post: int = 300,
    level: float = 0.9,
    save_checkpoint_path=None,
) -> dict:
    """Train the NPE on a checkpoint, conformally recalibrate, and write a Contract-B JSON.

    ckpt_path: an .npz sweep checkpoint with ``theta`` (rows, D) and ``x_noised`` (rows, F).
    out_json: destination path for the Contract-B artifact (also returned as a dict).
    emit_ecg: if True, the demo observation is forward(REFERENCE_THETA) (needs the sim stack);
    if False, a held-out calibration observation is used (fast, no geometry).
    save_checkpoint_path: if given, also persist the trained posterior there via
    ``npe.persist.save_posterior`` (writes ``<path>.pt`` + ``<path>.json``; portable, no
    project-code pickling). Off by default so existing callers are unaffected.
    """
    ckpt = Path(ckpt_path)
    out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    with np.load(ckpt) as d:
        theta = np.array(d["theta"], float)
        x = np.array(d["x_noised"], float)
    ncol = theta.shape[1]
    names = list(THETA_NAMES[:ncol])  # inferred params in this checkpoint (cv_myo appended last)
    print(
        f"[emit] ckpt={ckpt.name} rows={theta.shape[0]} inferred={ncol} params={names}", flush=True
    )

    n_tr = min(n_train, theta.shape[0] - n_calib)
    th_tr, x_tr = theta[:n_tr], x[:n_tr]
    th_ca, x_ca = theta[n_tr : n_tr + n_calib], x[n_tr : n_tr + n_calib]
    prior_std = th_tr.std(axis=0)

    post = _train(th_tr, x_tr)
    if save_checkpoint_path is not None:
        from npe.persist import save_posterior

        save_posterior(post, names, {k: _bounds(k) for k in names}, save_checkpoint_path)
        print(f"[emit] wrote posterior checkpoint {save_checkpoint_path}", flush=True)
    sets = draw_sample_sets(post, x_ca, n_post)  # (M, N, ncol)
    t = fit_inflation(th_ca, sets)
    ks_before = sbc_ks_pvals(th_ca, sets, np.ones(ncol))
    ks_after = sbc_ks_pvals(th_ca, sets, t)
    cov_after = central_coverage(th_ca, sets, t, level)
    contr_raw = np.median(sets.std(axis=1), axis=0) / prior_std
    contr_after = t * contr_raw
    # TARP pre AND post conformal, both from the same drawn sets so only the inflation differs.
    # Marginal conformal can pass SBC while the joint stays off, which is exactly what TARP tests.
    try:
        from calib.diagnostics import run_tarp_on_sets

        tarp_atc = float(run_tarp_on_sets(sets, th_ca, np.ones(ncol))["atc"])  # pre-conformal
        tarp_atc_post = float(run_tarp_on_sets(sets, th_ca, t)["atc"])  # post-conformal
    except Exception as e:
        print(f"[emit] TARP skipped: {type(e).__name__}: {e}", flush=True)
        tarp_atc = tarp_atc_post = None

    # --- the single demo observation: the re-anchored REFERENCE operating point ---
    obs_theta = {k: float(REFERENCE_THETA[k]) for k in names}  # 6D drops cv_myo -> default myo
    cv_myo_fixed = None
    if emit_ecg:
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
        post.sample(
            (N_DEMO_SAMPLES,), x=torch.tensor(x_obs, dtype=torch.float32), show_progress_bars=False
        )
    )
    samples = recalibrate(raw, t)  # per-parameter conformal-inflated posterior samples
    mean, std = samples.mean(axis=0), samples.std(axis=0)

    # --- posterior-predictive ECG (optional forwards) ---
    ppc = {"signal": input_ecg.tolist()}
    if emit_ecg and ppc_n > 0:
        from sim.forward import forward as _fwd

        sig = to_physiological_mv(
            np.asarray(_fwd({k: float(mean[i]) for i, k in enumerate(names)}, geom), float)
        )
        band = []
        for row in samples[np.random.default_rng(0).integers(0, samples.shape[0], ppc_n)]:
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
            length = min(b.shape[1] for b in [sig, *band])
            stack = np.stack([b[:, :length] for b in band])
            ppc["signal"] = sig[:, :length].tolist()
            ppc["band_lo"] = np.percentile(stack, 5, axis=0).tolist()
            ppc["band_hi"] = np.percentile(stack, 95, axis=0).tolist()

    posterior = {
        "samples": (
            np.column_stack([samples, np.full(samples.shape[0], cv_myo_fixed)]).tolist()
            if ncol < 7
            else samples.tolist()
        ),
        "mean": _per_param(mean, cv_myo_fixed, ncol),
        "std": _per_param(std, 0.0, ncol),
        "prior_bounds": {k: list(_bounds(k)) for k in FULL_NAMES},
        "contraction": _per_param(contr_after, 0.0, ncol),  # cv_myo fixed => 0 contraction
        "contraction_pre_conformal": _per_param(contr_raw, 0.0, ncol),  # raw NPE, before inflation
        "coverage": _per_param(cov_after, 1.0, ncol),
    }
    calibration = {
        "coverage_curve": _coverage_curve(th_ca, sets, t),
        "sbc": {
            k: {"before": float(ks_before[i]), "after": float(ks_after[i])}
            for i, k in enumerate(names)
        },
        "sbc_ks_pvalue": float(np.median(ks_after)),
        "tarp_atc": tarp_atc,  # pre-conformal (raw posterior)
        "tarp_atc_post": tarp_atc_post,  # post per-parameter conformal (joint after the fix)
        "conformal_t": {k: float(t[i]) for i, k in enumerate(names)},
        "note": (
            "conformal_t is per-parameter (marginal SBC). tarp_atc is pre-conformal, "
            "tarp_atc_post is post-conformal (joint). sbi sign: ATC<0 = overconfident (too narrow)."
        ),
    }
    artifact = {
        "run_id": f"{out_json.stem}-{_git_sha()}",
        "geometry_id": "cardiac_demo",
        "theta_names": FULL_NAMES,
        "observation_kind": "features",
        "synthetic_truth": True,
        "true_theta": _per_param([true_theta[k] for k in names], cv_myo_fixed, ncol),
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
            "ecg_stub": not emit_ecg,
        },
    }

    out_json.write_text(json.dumps(artifact, indent=1))
    print(f"[emit] wrote {out_json} ({out_json.stat().st_size} bytes)", flush=True)
    _validate(artifact)
    return artifact


def _validate(artifact: dict) -> None:
    """Check the artifact against the frozen schema (jsonschema if present, else required keys).

    The schema lives under ui/ which is not shipped in the CLI image; if it is absent, skip
    validation rather than fail the run (the artifact is already written)."""
    schema_path = _REPO / "ui" / "mock" / "contract_b.schema.json"
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
