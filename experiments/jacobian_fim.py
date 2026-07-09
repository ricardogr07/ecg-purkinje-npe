"""Local Jacobian / Fisher-information / CRLB analysis at REFERENCE_THETA.

Purpose (director spec, see task brief): settle, in an SNR-explicit, noise-independent way,
whether the delta_iv-cv_myo posterior correlation (rho = -0.72, docs/scientific-process.md
error #2) is a structural degeneracy of the forward map or a correlated-but-identifiable
posterior. This is a LOCAL analysis at one operating point (REFERENCE_THETA), not a global
identifiability claim; every number below states the sigma it was measured against.

Runs on the RESCALED (physiological-mV) forward: core.noise.to_physiological_mv() is applied
to every raw forward() output before anything else, exactly as npe/emit.py does.

Steps (numbered to match the spec):
  1. Central-difference Jacobian J = dx/dtheta at REFERENCE_THETA, for both the engineered
     features (15-dim) and the flattened waveform, at three step sizes (eps sweep for
     finite-difference stability).
  2. Normalize: J_tilde = Sigma_n^-1 @ J @ R (R = diag(prior_range), Sigma_n = per-sample
     noise sigma). Only the waveform case has a real physical sigma for every sample; the
     two "time"-kind features have no sourced timing-jitter sigma, so the features case is
     reported unnormalized/relative (see PARAM in core.features.FEATURE_KINDS).
  3. SVD of J_tilde (waveform): singular spectrum, condition number, v_min loadings.
  4. Prior-free FIM I(theta) = J^T Sigma^-1 J (waveform, no R) and per-parameter CRLB.
  5. iso-ECG check: step theta* +/- delta*v_min, compare ECGs in units of noise SD.

Budget: 3 eps values x 7 params x 2 evals (central diff, features+waveform share one
forward() call) = 42 forward() calls, + 2 for the iso-ECG check, + 1 baseline = 45 total.
forward() is ~60-70s/call on crtdemo here, so this is a ~45-60 minute run, not "a few
minutes" (that estimate assumed forward() cost seen on a different machine/day; kept as-is
per the spec rather than cutting the step-size sanity check the director asked not to skip).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))

from core.features import FEATURE_KINDS, FEATURE_NAMES, extract_features  # noqa: E402
from core.noise import DEFAULT_WAVEFORM_SIGMA_MV, to_physiological_mv  # noqa: E402
from core.theta import PRIOR_BOUNDS, THETA_NAMES  # noqa: E402
from sim.forward import REFERENCE_THETA, forward, load_geometry  # noqa: E402

OUT_JSON = _REPO / "outputs" / "jacobian.json"
EPS_MAIN = 1e-2
# Top step lowered 2e-2 -> 1.5e-2: the crtdemo fractal tree projects a Purkinje node outside
# the mesh at some perturbations (see sim.forward REFERENCE_THETA note), and 2e-2 reliably hit
# it on branch_angle. Three distinct steps still bracket the finite-difference sanity sweep;
# per-forward try/except (below) makes any residual projection failure non-fatal regardless.
EPS_SWEEP = (5e-3, 1e-2, 1.5e-2)
ISO_DELTA_FRACTION = 0.5  # fraction of the max in-bounds step used for the iso-ECG check

PRIOR_RANGE = np.array([PRIOR_BOUNDS[k][1] - PRIOR_BOUNDS[k][0] for k in THETA_NAMES])


def _log(msg: str) -> None:
    print(f"[jacobian] {msg}", flush=True)


def _theta_at(base: dict, name: str, value: float) -> dict:
    out = dict(base)
    out[name] = value
    return out


def _forward_mv(theta: dict, geom, tag: str):
    """forward() -> physiological-mV ECG, or None if the fractal tree fails to grow (the
    known crtdemo projection fragility). Never raises: an expensive multi-pass run must not
    lose all its completed forwards to one bad perturbation."""
    t0 = time.time()
    try:
        ecg = to_physiological_mv(np.asarray(forward(theta, geom), float))
        _log(f"forward({tag}) -> shape={ecg.shape} in {time.time() - t0:.1f}s")
        return ecg
    except Exception as e:  # noqa: BLE001  (deliberately broad: any forward failure is skippable)
        _log(f"forward({tag}) FAILED in {time.time() - t0:.1f}s: {type(e).__name__}: {e}")
        return None


def central_diff_jacobian(theta_star: dict, geom, eps: float) -> dict:
    """Central-difference dx/dtheta at theta_star for both observation types.

    A failed perturbation (forward returns None) leaves that parameter's Jacobian column as
    NaN and is recorded in ``failures``; the pass still completes. Returns J_wave (12*T, 7),
    J_feat (15, 7), T, and the failure record.
    """
    h = eps * PRIOR_RANGE
    plus, minus, failures = {}, {}, []
    for i, name in enumerate(THETA_NAMES):
        for sign, store in ((1.0, plus), (-1.0, minus)):
            th = _theta_at(theta_star, name, theta_star[name] + sign * h[i])
            direction = "+" if sign > 0 else "-"
            ecg = _forward_mv(th, geom, f"eps={eps} {name}{direction}")
            store[name] = ecg
            if ecg is None:
                failures.append({"eps": eps, "param": name, "direction": direction})

    valid = [e for e in (*plus.values(), *minus.values()) if e is not None]
    T = min((e.shape[1] for e in valid), default=0)
    J_wave = np.full((12 * T, len(THETA_NAMES)), np.nan)
    J_feat = np.full((len(FEATURE_KINDS), len(THETA_NAMES)), np.nan)
    for i, name in enumerate(THETA_NAMES):
        ep, em = plus[name], minus[name]
        if ep is None or em is None or T == 0:
            continue  # column stays NaN
        J_wave[:, i] = (ep[:, :T] - em[:, :T]).ravel() / (2 * h[i])
        J_feat[:, i] = (extract_features(ep) - extract_features(em)) / (2 * h[i])
    return {
        "J_wave": J_wave,
        "J_feat": J_feat,
        "T": T,
        "eps": eps,
        "h": h.tolist(),
        "failures": failures,
        "failed_params": sorted({f["param"] for f in failures}),
    }


def normalize_waveform(J_wave: np.ndarray, sigma_mv: float) -> np.ndarray:
    """J_tilde = Sigma_n^-1 @ J @ R, Sigma_n = sigma_mv * I (iid per-sample noise)."""
    return (J_wave / sigma_mv) * PRIOR_RANGE[np.newaxis, :]


def _valid_cols(J: np.ndarray):
    """Column mask (True = no NaN) and the param names kept/dropped."""
    valid = ~np.isnan(J).any(axis=0)
    used = [n for n, v in zip(THETA_NAMES, valid, strict=True) if v]
    dropped = [n for n, v in zip(THETA_NAMES, valid, strict=True) if not v]
    return valid, used, dropped


def svd_report(J_tilde: np.ndarray) -> dict:
    valid, used, dropped = _valid_cols(J_tilde)
    _u, S, Vt = np.linalg.svd(J_tilde[:, valid], full_matrices=False)
    V = Vt.T  # columns are right singular vectors, S descending
    # Embed the smallest-s right singular vector back into the full 7-slot layout (0 for any
    # dropped param) so the iso-ECG step and v_min_named stay full-width and comparable.
    v_min_full = dict.fromkeys(THETA_NAMES, 0.0)
    for n, val in zip(used, V[:, -1].tolist(), strict=True):
        v_min_full[n] = val
    return {
        "singular_values": S.tolist(),
        "condition_number": float(S[0] / S[-1]),
        "V": V.tolist(),
        "v_min": [v_min_full[n] for n in THETA_NAMES],
        "v_min_named": v_min_full,
        "sub_noise_direction": [bool(s <= 1.0) for s in S],  # s_k <= 1 at this sigma
        "params_used": used,
        "params_dropped": dropped,
    }


def fim_report(J_wave: np.ndarray, sigma_mv: float) -> dict:
    """Prior-free FIM I = J^T Sigma^-1 J (no R normalization) and per-parameter CRLB.
    Computed over the valid (non-NaN) columns only; dropped params get CRLB None."""
    valid, used, dropped = _valid_cols(J_wave)
    Jv = J_wave[:, valid]
    fim = (Jv.T @ Jv) / (sigma_mv**2)
    eigvals, eigvecs = np.linalg.eigh(fim)  # ascending
    try:
        cov = np.linalg.inv(fim)
        singular = False
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(fim)
        singular = True
    crlb_vals = np.sqrt(np.clip(np.diag(cov), 0, None))
    crlb = dict.fromkeys(THETA_NAMES, None)
    for n, val in zip(used, crlb_vals.tolist(), strict=True):
        crlb[n] = val
    return {
        "eigenvalues_ascending": eigvals.tolist(),
        # eigvecs[:, k] is the eigenvector for eigenvalues_ascending[k]; transpose so
        # eigenvectors[k] IS that eigenvector (list-of-vectors, param order = params_used).
        "eigenvectors": eigvecs.T.tolist(),
        "condition_number": float(eigvals[-1] / max(eigvals[0], 1e-30)),
        "crlb": crlb,
        "params_used": used,
        "params_dropped": dropped,
        "fim_matrix_singular": singular,
    }


def features_report(J_feat: np.ndarray) -> dict:
    """Features Jacobian: no sourced per-feature noise sigma for the 2 timing-fraction
    features (core.features.FEATURE_KINDS), so this is reported unnormalized (R only), plus
    a secondary amp-only subset SNR-normalized with the waveform sigma as an approximation
    (peak-to-peak / vector-magnitude features are in the same physiological-mV units)."""
    valid, used, dropped = _valid_cols(J_feat)
    J_tilde_raw = (J_feat[:, valid]) * PRIOR_RANGE[valid][np.newaxis, :]  # R only, no sigma
    s_raw = np.linalg.svd(J_tilde_raw, compute_uv=False)

    amp_idx = [i for i, k in enumerate(FEATURE_KINDS) if k == "amp"]
    J_amp_tilde = (J_feat[np.ix_(amp_idx, valid)] / DEFAULT_WAVEFORM_SIGMA_MV) * PRIOR_RANGE[valid][
        np.newaxis, :
    ]
    s_amp = np.linalg.svd(J_amp_tilde, compute_uv=False)

    return {
        "feature_names": list(FEATURE_NAMES),
        "params_used": used,
        "params_dropped": dropped,
        "note": (
            "raw: J*R only, no noise sigma (2 of 15 features are dimensionless time "
            "fractions with no sourced jitter sigma), relative units not comparable across "
            "runs. amp_subset_snr: the 13 amplitude-kind features (mV) normalized with the "
            "waveform sigma as an approximation, comparable to the waveform SVD in kind."
        ),
        "raw_singular_values": s_raw.tolist(),
        "amp_subset_singular_values": s_amp.tolist(),
    }


def _max_feasible_delta(theta_star: dict, direction: np.ndarray) -> float:
    max_delta = np.inf
    for i, name in enumerate(THETA_NAMES):
        d = direction[i]
        if abs(d) < 1e-12:
            continue
        lo, hi = PRIOR_BOUNDS[name]
        room_pos = (hi - theta_star[name]) / abs(d)
        room_neg = (theta_star[name] - lo) / abs(d)
        max_delta = min(max_delta, room_pos, room_neg)
    return float(max_delta)


def iso_ecg_check(
    theta_star: dict, v_min: np.ndarray, geom, sigma_mv: float, baseline_ecg: np.ndarray
) -> dict:
    """Step theta* +/- delta*v_min (v_min in theta units, i.e. R @ v_min_normalized) and
    compare the resulting ECGs to the baseline in units of noise SD."""
    direction = PRIOR_RANGE * v_min  # v_min was defined in R-normalized (du) space
    max_delta = _max_feasible_delta(theta_star, direction)
    delta = ISO_DELTA_FRACTION * max_delta

    theta_plus = {k: theta_star[k] + delta * direction[i] for i, k in enumerate(THETA_NAMES)}
    theta_minus = {k: theta_star[k] - delta * direction[i] for i, k in enumerate(THETA_NAMES)}
    ecg_plus = _forward_mv(theta_plus, geom, "iso-ecg +delta*v_min")
    ecg_minus = _forward_mv(theta_minus, geom, "iso-ecg -delta*v_min")

    def _stats(pert):
        """ECG deviation from baseline in noise-SD units, or None if either forward failed
        (per-direction: one failed step must not discard the other's good result)."""
        if baseline_ecg is None or pert is None:
            return None
        T = min(baseline_ecg.shape[1], pert.shape[1])
        base = baseline_ecg[:, :T]
        diff = pert[:, :T] - base
        nrmse_per_lead = np.sqrt((diff**2).mean(axis=1)) / np.sqrt((base**2).mean(axis=1) + 1e-30)
        return {
            "nrmse_per_lead": nrmse_per_lead.tolist(),
            "max_abs_dev_mv": float(np.abs(diff).max()),
            "max_abs_dev_noise_sd": float(np.abs(diff).max() / sigma_mv),
            "rms_dev_noise_sd": float(np.sqrt((diff**2).mean()) / sigma_mv),
        }

    plus_stats = _stats(ecg_plus)
    minus_stats = _stats(ecg_minus)
    devs = [s["max_abs_dev_noise_sd"] for s in (plus_stats, minus_stats) if s is not None]
    if not devs:
        verdict = "unavailable (baseline and both perturbed forwards failed to grow)"
    elif max(devs) < 1.0:
        verdict = "sub-noise (direction unobservable at this sigma)"
    else:
        verdict = "super-noise (a full step along v_min moves the ECG by > 1 noise SD; "
        verdict += "the direction is observable at this sigma)"
    return {
        "delta_used": delta,
        "max_feasible_delta": max_delta,
        "delta_theta": dict(zip(THETA_NAMES, (delta * direction).tolist(), strict=True)),
        "theta_plus": theta_plus,
        "theta_minus": theta_minus,
        "plus": plus_stats,  # None if that direction's forward failed to grow
        "minus": minus_stats,
        "verdict": verdict,
    }


def step_size_stability(spectra: dict[float, list[float]]) -> dict:
    """Compare the smallest singular value across eps values; flag if it moves a lot."""
    eps_sorted = sorted(spectra)
    smallest = {eps: spectra[eps][-1] for eps in eps_sorted}
    vals = list(smallest.values())
    rel_spread = (max(vals) - min(vals)) / max(min(vals), 1e-30)
    return {
        "smallest_singular_value_by_eps": smallest,
        "relative_spread": rel_spread,
        "stable": bool(rel_spread < 0.2),  # test_jacobian.py checks the ~20% figure
        "note": (
            "if the smallest singular value moves a lot with the finite-difference step "
            "size, that direction is finite-difference noise, not a real degeneracy."
        ),
    }


def main() -> dict:
    geom = load_geometry()
    theta_star = {k: float(REFERENCE_THETA[k]) for k in THETA_NAMES}
    sigma_mv = DEFAULT_WAVEFORM_SIGMA_MV

    _log(f"REFERENCE_THETA = {theta_star}")
    _log(f"sigma_waveform_mv = {sigma_mv} (Contract D, physiological-mV rescaled forward)")

    baseline_ecg = _forward_mv(theta_star, geom, "baseline theta*")

    eps_results: dict[float, dict] = {}
    for eps in EPS_SWEEP:
        _log(f"=== eps={eps} central-difference pass (14 forward calls) ===")
        eps_results[eps] = central_diff_jacobian(theta_star, geom, eps)

    all_failures = [f for res in eps_results.values() for f in res["failures"]]
    # A param that failed at EVERY step size is itself a finding (its Jacobian column is
    # unrecoverable at theta*), distinct from a param that dropped only at the coarsest step.
    failed_all_eps = sorted(
        {
            name
            for name in THETA_NAMES
            if all(name in res["failed_params"] for res in eps_results.values())
        }
    )

    # Primary SVD/FIM/CRLB need the full 7-column Jacobian: prefer EPS_MAIN, else the finest
    # complete pass, else EPS_MAIN with its NaN columns dropped (heavily flagged).
    def _complete(res: dict) -> bool:
        return not res["failed_params"] and res["T"] > 0

    if _complete(eps_results[EPS_MAIN]):
        primary_eps = EPS_MAIN
    else:
        primary_eps = next((e for e in EPS_SWEEP if _complete(eps_results[e])), EPS_MAIN)
    main_run = eps_results[primary_eps]
    _log(f"primary eps for SVD/FIM/CRLB = {primary_eps} (dropped: {main_run['failed_params']})")

    J_tilde_wave = normalize_waveform(main_run["J_wave"], sigma_mv)
    svd_main = svd_report(J_tilde_wave)
    fim_main = fim_report(main_run["J_wave"], sigma_mv)
    feat_main = features_report(main_run["J_feat"])

    v_min = np.array(svd_main["v_min"])
    iso = iso_ecg_check(theta_star, v_min, geom, sigma_mv, baseline_ecg)

    # Step-size sweep only over COMPLETE passes (spectra of different column sets are not
    # comparable). With <2 complete passes the sweep is inconclusive, reported as such.
    step_spectra = {
        eps: svd_report(normalize_waveform(res["J_wave"], sigma_mv))["singular_values"]
        for eps, res in eps_results.items()
        if _complete(res)
    }
    if len(step_spectra) >= 2:
        step_check = step_size_stability(step_spectra)
    else:
        step_check = {
            "smallest_singular_value_by_eps": {eps: spec[-1] for eps, spec in step_spectra.items()},
            "stable": None,
            "note": f"only {len(step_spectra)} complete pass(es); step-sensitivity inconclusive.",
        }
    step_check["complete_passes"] = sorted(step_spectra)

    result = {
        "meta": {
            "analysis": "LOCAL Jacobian/FIM/CRLB at REFERENCE_THETA (crtdemo); not a global "
            "identifiability claim. Forward is "
            "core.noise.to_physiological_mv(sim.forward.forward(...)).",
            "theta_star": theta_star,
            "theta_names": list(THETA_NAMES),
            "prior_bounds": {k: list(PRIOR_BOUNDS[k]) for k in THETA_NAMES},
            "sigma_waveform_mv": sigma_mv,
            "sigma_source": "Contract D, Obregon-Rosas et al. 2026 (QRSense), PMID 42176693",
            "eps_requested_main": EPS_MAIN,
            "eps_primary_used": primary_eps,
            "eps_sweep": list(EPS_SWEEP),
            "waveform_T_at_primary_eps": main_run["T"],
            "baseline_forward_ok": baseline_ecg is not None,
        },
        "forward_failures": {
            "all": all_failures,
            "failed_at_every_step_size": failed_all_eps,
            "note": (
                "Each entry is a perturbation whose fractal-tree growth projected outside the "
                "crtdemo mesh (known fragility, sim.forward REFERENCE_THETA note). A param in "
                "failed_at_every_step_size has no recoverable Jacobian column at theta*."
            ),
        },
        "step_size_sweep": step_check,
        "waveform": svd_main,
        "fim": fim_main,
        "features": feat_main,
        "iso_ecg_check": iso,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=1))
    _log(f"wrote {OUT_JSON}")
    return result


if __name__ == "__main__":
    main()
