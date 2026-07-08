"""Resolve, load, and Contract-B-shape the results artifact the API serves.

Resolution order (first hit wins), so `/infer` is always live for the demo:
  1. $ECG_ARTIFACT                 explicit path override
  2. outputs/day3_*results*.json   newest real Science snapshot (Contract B)
  3. ui/mock/results.json          the Design track's mock bundle
  4. a built-in placeholder        prior-drawn, no fabricated inference

Tonight this is load-and-serve: `/infer` returns the resolved Contract-B artifact.
Real NPE inference swaps in behind `load()` at the Day 4->5 sync.

Cowork amendment: we attach `posterior.mean`/`std` (derived from `posterior.samples`
when absent) and `posterior.prior_bounds` (frozen Contract A). `posterior.true_theta`
is passed through only, never synthesised for a real run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Frozen Contract A (7 params), duplicated here on purpose: the source of truth is
# docs/contracts.md + .localagent/FREEZE_AND_PLAN.md, not the provisional src/core/theta.py
# (still 6D). ponytail: single small table; re-point at core once core is frozen to 7D.
PRIOR_BOUNDS: dict[str, list[float]] = {
    "cv": [1.5, 3.5],
    "delta_iv": [-90.0, 40.0],
    "init_length_lv": [30.0, 60.0],
    "init_length_rv": [30.0, 60.0],
    "branch_angle": [0.10, 0.30],
    "w": [0.05, 0.20],
    "cv_myo": [0.5, 1.0],
}
THETA_NAMES: list[str] = list(PRIOR_BOUNDS)


def git_sha() -> str:
    """Best-effort commit SHA. Docker sets $GIT_SHA at build; unknown locally."""
    return os.environ.get("GIT_SHA", "unknown")


def _resolve_path() -> Path | None:
    override = os.environ.get("ECG_ARTIFACT")
    if override:
        p = Path(override)
        return p if p.is_file() else None
    day3 = sorted((_REPO_ROOT / "outputs").glob("day3_*results*.json"))
    if day3:
        return day3[-1]
    mock = _REPO_ROOT / "ui" / "mock" / "results.json"
    return mock if mock.is_file() else None


def _builtin_artifact() -> dict[str, Any]:
    """Valid, renderable placeholder Contract B: prior-drawn samples, contraction ~1 (nothing
    learned). Keeps the endpoint live in a fresh checkout / CI when no real artifact exists."""
    rng = np.random.default_rng(0)
    lo = np.array([PRIOR_BOUNDS[n][0] for n in THETA_NAMES])
    hi = np.array([PRIOR_BOUNDS[n][1] for n in THETA_NAMES])
    samples = lo + rng.uniform(size=(32, len(THETA_NAMES))) * (hi - lo)
    return {
        "run_id": "placeholder",
        "geometry_id": "cardiac_demo",
        "theta_names": THETA_NAMES,
        "observation_kind": "features",
        "posterior": {
            "samples": np.round(samples, 6).tolist(),
            "contraction": {n: 1.0 for n in THETA_NAMES},
            "coverage": {},
        },
        "meta": {
            "placeholder": True,
            "note": "No real Contract-B artifact or ui/mock/results.json found; "
            "serving a prior-drawn placeholder so the endpoint is live.",
        },
    }


def _amend_posterior(art: dict[str, Any]) -> dict[str, Any]:
    post = art.setdefault("posterior", {})
    names = art.get("theta_names") or THETA_NAMES
    samples = post.get("samples")
    if samples:
        arr = np.asarray(samples, dtype=float)
        post.setdefault("mean", dict(zip(names, np.round(arr.mean(0), 6).tolist(), strict=False)))
        post.setdefault("std", dict(zip(names, np.round(arr.std(0), 6).tolist(), strict=False)))
    post.setdefault("prior_bounds", {n: PRIOR_BOUNDS.get(n) for n in names})
    return art


def load() -> dict[str, Any]:
    """Return the resolved Contract-B artifact with the Cowork posterior amendment applied.

    Re-read each call so a freshly written day3 snapshot hot-swaps without a restart.
    """
    path = _resolve_path()
    art = json.loads(path.read_text(encoding="utf-8")) if path else _builtin_artifact()
    return _amend_posterior(art)


def geometry_view(geometry_id: str, art: dict[str, Any]) -> dict[str, Any]:
    """Contract C GET /geometry payload. Serves the artifact's activation map field if present.

    ponytail: a real surface+fields serializer lands with the Strocchi adapter output at
    integration (Day 4+); tonight this is a graceful descriptor, never a 500.
    """
    return {
        "geometry_id": geometry_id,
        "mesh_ref": art.get("geometry_id", geometry_id),
        "activation_map": art.get("activation_map"),
        "note": "mesh surface+fields pending adapter integration; activation_map is null "
        "until a run provides it (UI degrades gracefully per Contract B).",
    }
