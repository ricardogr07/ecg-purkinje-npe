# CLAUDE.md, `ecg-purkinje-npe`

Project context for coding agents. Read this first, then `docs/research-brief.md` (the source of
truth) and `docs/architecture.md`.

## What this is
Amortized, calibrated **identifiability** characterization of the Purkinje conduction system from the
surface ECG. We train a Neural Posterior Estimator (NPE, `sbi`) over conduction parameters at **fixed
anatomy** and report a **per-parameter contraction spectrum + posterior degeneracy/multimodality map**
with formal calibration (SBC / expected coverage / TARP), on a **public** heart mesh. The contribution
is a **scientific finding**, not a new method.

**Honest thesis (hold this line everywhere):** a calibrated, amortized identifiability
characterization of Purkinje conduction from a SIMULATED 12-lead ECG, at a stated observation-noise
floor. Alongside it we surfaced and corrected three of our own errors (SBC found overconfidence;
`ridge_confirm` refuted a degeneracy headline; an audit found a 3000x SNR error). That self-correction
record is the methods contribution.

**There is no real ECG in this project.** The pickled `True_ecg` is a simulator output used as a
regression fixture, not a patient recording. So the transplant result (corr 1.000) is a
self-consistency tautology, not evidence of fidelity, and Result B is a parameter-recovery check in
the inverse-crime setting. Never write "diverges from a real ECG", "forward-vs-real-ECG", or
"validated". Real-ECG comparison is future work.

The forward is a **pseudo-ECG in an unbounded homogeneous volume conductor** (Gima and Rudy 2002,
PMID 11988490), NOT a torso lead field. It has no absolute amplitude calibration: report arbitrary
units scaled to a stated mV operating point. Bishop and Plank 2011 (PMID 21536529) find this operator
under-estimates depolarization amplitude by over an order of magnitude versus a bounded forward.

## The science in one screen
- **Simulator (deterministic given θ):** `purkinje-uv` fractal tree → FIM eikonal → 12-lead ECG.
  Because it is deterministic, an **explicit observation-noise model is mandatory** or calibration is
  meaningless (waveform floor: white Gaussian, sigma = 0.025 mV per sample per lead).
- **θ (7D):** `cv`, `delta_iv` (LV-RV interventricular delay), `init_length` LV, `init_length` RV
  (constraint-candidate block); `branch_angle`, `w` (diffuse-candidate block); `cv_myo` (myocardial
  CV). Priors: physiological uniform ranges.
- **Observation x:** paired engineered ECG **features** AND the full 12-lead **waveform**, both from
  the same sweep (so the comparison costs training time, not sim time).
- **Inference:** amortized NPE (`sbi`, normalizing flow) with per-parameter conformal recalibration.
- **Finding:** contraction = posterior_std / prior_std per parameter + coverage + degeneracy corner
  plot, cross-checked against the forward-sensitivity CRLB.
- **Baseline = validation, not a race:** BO+ABC (`jax-bo`) must *agree* where trusted.

## Closest prior art (position against, never claim to have discovered non-uniqueness)
- Grandits et al. 2024 (arXiv:2411.00165), existence of non-uniqueness + PMJ prior + ensemble. Our
  edge: amortized + formally calibrated + per-parameter quantified.
- Alvarez-Barrientos et al., MedIA 2025 (arXiv:2312.09887), BO+ABC, uncalibrated.

## Conventions
- Python via `uv`; lint/format `ruff`; tests `pytest`; types where cheap. Keep a pure `core/` with
  zero I/O (importable, testable).
- Backend FastAPI; frontend Next.js + Tailwind; static export to S3 + CloudFront. **CPU-only, no GPU.**
- Conventional commits.
- **`main` is protected (from v0.2.0):** no direct commits or pushes. Every change lands via a branch
  and a pull request with the full CI matrix (python-ci, ui-ci, package-ci, docker-build) green before
  merge. The v0.2.0 tag and the deployed site are the stable fallback.
- **NEVER use em or en dashes** anywhere (code, comments, docs, commit messages, UI copy). Use a
  comma, parentheses, a colon, or a plain hyphen.
- **Verification discipline.** Every factual/scientific claim is checked against a primary source
  before it enters a doc, the demo, or the write-up (`docs/verification-ledger.md`). If you cannot
  verify, mark it "unverified", never assert.
- **Demo honesty.** Never show mock or placeholder data as real. Any surface (UI, API, figure) that
  renders mock data must be explicitly labeled illustrative until it is wired to the real artifact.

## Long-running jobs and the shared venv
- Never run a bare `uv run` while a long job shares the venv: `uv run` auto-syncs and can swap package
  versions under a running process. Use `uv run --no-sync`, activate the venv directly, or wait.
- Before any build, prune, or install that touches disk or the venv, confirm no job is running and
  check free space on the checkpoint volume.

## Where things live
- `docs/research-brief.md`, the source of truth (problem, method, prior art, priors + noise provenance).
- `docs/architecture.md`, the pipeline end to end; `docs/results-summary.md`, the headline result;
  `docs/verification-ledger.md`, the public claim ledger.
- `docs/contracts.md`, the θ / results-artifact / demo-API interfaces.
- `REPRODUCE.md`, how to regenerate results and build the images; the `v0.1.0-submission` release
  carries the trained weights, the sweeps, and the calibration artifacts.
