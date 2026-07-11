"""Pipeline orchestration: sweep -> (NPE + conformal + Contract-B) with resumable artifacts.

Each stage writes into the run dir and is skip-if-exists, so a crash resumes. Reuses the proven
science: `sim.sweep.run_sweep_checkpointed` for the sweep, and `npe.emit.emit_contract_b` for the
NPE + per-parameter conformal + Contract-B artifact (called directly, in-process).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from . import geometry
from .config import RunConfig

_REPO = Path(__file__).resolve().parents[1]
log = logging.getLogger("conduction_lens")


def _setup_logging(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for h in (logging.FileHandler(out / "run.log"), logging.StreamHandler(sys.stdout)):
        h.setFormatter(fmt)
        log.addHandler(h)


def _git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=_REPO)
            .decode()
            .strip()
        )
    except Exception:
        return os.environ.get("GIT_SHA", "unknown")


def _pkg_versions() -> dict[str, str]:
    out = {}
    for m in ("numpy", "sbi", "torch"):
        try:
            out[m] = __import__(m).__version__
        except Exception:
            out[m] = "?"
    return out


def _write_manifest(cfg: RunConfig, out: Path) -> None:
    manifest = {
        "config": cfg.as_dict(),
        "git_sha": _git_sha(),
        "packages": _pkg_versions(),
        "python": sys.version.split()[0],
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2))


def run(cfg: RunConfig) -> Path:
    """Run the full pipeline into cfg.out; returns the run dir. Resumable (skip-if-exists)."""
    out = Path(cfg.out)
    _setup_logging(out)
    if cfg.dim != 7:
        raise SystemExit("only the frozen 7D Contract A is supported (--dim 7)")
    if cfg.obs != "features":
        raise SystemExit(f"--obs {cfg.obs} is not wired (features only)")
    geometry.validate(cfg.geometry)
    _write_manifest(cfg, out)

    budget = 24 if cfg.dry_run else cfg.budget
    ppc = 2 if cfg.dry_run else cfg.ppc_n
    log.info(
        f"run start: geometry={cfg.geometry} dim={cfg.dim} budget={budget} obs={cfg.obs} out={out}"
    )

    # --- Stage 1: sweep (resumable checkpoint) ---
    sweep_npz = out / "sweep.npz"
    if sweep_npz.exists():
        log.info(f"[sweep] skip (exists): {sweep_npz}")
    else:
        from sim.sweep import run_sweep_checkpointed

        t = time.perf_counter()
        theta, _xc, _xn, ndone = run_sweep_checkpointed(
            budget,
            cfg.noise_sigma_mv,
            cfg.resolved_workers(),
            seed=cfg.seed,
            checkpoint_path=str(sweep_npz),
        )
        log.info(
            f"[sweep] {theta.shape[0]} usable ({ndone} draws) in "
            f"{time.perf_counter() - t:.0f}s -> {sweep_npz}"
        )

    # --- Stage 2: report (train NPE + conformal + Contract-B) via the emitter ---
    results = out / "results.json"
    if results.exists():
        log.info(f"[report] skip (exists): {results}")
    else:
        n_calib = min(500, max(10, budget // 5))
        n_train = max(10, budget - n_calib)
        from npe.emit import emit_contract_b

        log.info(f"[report] training NPE + conformal + emitting Contract-B -> {results}")
        emit_contract_b(
            str(sweep_npz),
            str(results),
            emit_ecg=True,
            ppc_n=ppc,
            n_train=n_train,
            n_calib=n_calib,
        )

    log.info(f"[done] run artifacts in {out}: sweep.npz, results.json, run_manifest.json, run.log")
    report(str(out))
    return out


def report(out: str) -> None:
    """Print the headline contraction + calibration from a finished run's Contract-B JSON."""
    art = json.loads((Path(out) / "results.json").read_text())
    contr = art["posterior"]["contraction"]
    cal = art.get("calibration", {})
    order = sorted(contr, key=lambda k: contr[k])
    log.info("[report] contraction (post-conformal, most->least identifiable):")
    for k in order:
        log.info(f"    {k:16s} {contr[k]:.2f}")
    if cal:
        log.info(
            f"[report] SBC ks median (after)={cal.get('sbc_ks_pvalue')}, "
            f"TARP ATC={cal.get('tarp_atc')}, synthetic_truth={art.get('synthetic_truth')}"
        )
