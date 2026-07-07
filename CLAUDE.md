# CLAUDE.md, `ecg-purkinje-npe`

Project memory for Claude Code. Read this first, then `docs/research-brief-v5.md` (the source of truth) and `docs/execution-plan.md`.

## What this is
Amortized, calibrated **identifiability** characterization of the Purkinje conduction system from the surface ECG. We train a Neural Posterior Estimator (NPE, `sbi`) over conduction parameters at **fixed anatomy** and report a **per-parameter contraction spectrum + posterior degeneracy/multimodality map** with formal calibration (SBC / expected coverage / TARP), on a **public** heart mesh. The contribution is a **scientific finding**, not a new method. Full framing: `docs/research-brief-v5.md`.

## Non-negotiable rules (hackathon eligibility + honesty)
- **New work only.** All project code is written during the event (hacking starts 12:30 ET Jul 7). **Do not `git init` / first-commit until after kickoff.** Do not paste in pre-existing project code.
- **Open source.** Apache-2.0. Publish backend, frontend, infra, and trained weights.
- **Vendored own libraries, declared openly (director decision Jul 7).** `purkinje-uv`, `myocardial-mesh`, and `jaxbo` are the author's own already-published MIT/Apache libraries, **vendored in-tree under `packages/` and actively reworked during the event** (we need live edits, e.g., the mesh ingestion and the forward model). Intentional and disclosed in `README.md` and the writeup: standing on our own open-source shoulders, the analysis is new work. Retain each vendored lib's upstream LICENSE. **`myocardial-mesh` (upstream repo `purkinje-learning-myocardial-mesh`) is accepted (director decision Jul 7): it is a separate published MIT library that provides the volumetric myocardial eikonal and the 12-lead ECG forward, and is NOT the thesis analysis.** **Never vendor or import `purkinje-learning`** (the thesis analysis repo, stays out).
- **Attribute data:** Strocchi mesh cohort is CC-BY-4.0 (cite it).
- **Verification discipline.** Every factual/scientific claim is checked against a primary source before it enters a doc, the demo, or the write-up. Maintain the verification ledger (see brief §14). If you can't verify, mark it "unverified", never assert.

## The science in one screen
- **Simulator (deterministic given θ, verified):** `purkinje-uv` fractal tree → FIM eikonal → 12-lead ECG. Confirm determinism Day 1 (same θ twice → identical ECG). Because it's deterministic, an **explicit observation-noise model is MANDATORY** or calibration is meaningless.
- **θ (6D):** `cv`, `Δ_IV` (LV-RV interventricular delay), `init_length` LV, `init_length` RV  (constraint-candidate block); `branch_angle`, `w` (diffuse-candidate block). Priors: physiological uniform ranges.
- **Observation x:** paired, engineered ECG **features** AND full 12-lead **waveform** (+ small CNN embedding), both from the **same sweep** (so the comparison costs training time, not sim time).
- **Inference:** amortized NPE (`sbi`, normalizing flow). Fallback if coverage is poor at low budget: TSNPE/SNPE or drop to 4D.
- **Finding:** contraction = posterior_std / prior_std per parameter + coverage + degeneracy corner plot. Cross-check against forward-sensitivity (arXiv:2505.16696).
- **Baseline = validation, not a race:** BO+ABC (`JAX-BO`) must *agree* where trusted; also rules out amortization artifacts.

## Closest prior art (position against, never claim to have discovered non-uniqueness)
- Grandits et al. 2024 (arXiv:2411.00165), existence of non-uniqueness + PMJ prior + ensemble. **Not independent** (Pezzuto co-authors both this and our own line). Our edge: amortized + formally calibrated + per-parameter quantified.
- Álvarez-Barrientos et al., MedIA 2025 (arXiv:2312.09887), BO+ABC, uncalibrated (our own line).

## Conventions
- Python via `uv`; lint/format `ruff`; tests `pytest`; types where cheap. Keep a pure `core/` with zero I/O (importable, testable), like shelter-pulse.
- Backend: FastAPI. Frontend: Next.js + Tailwind (mirror shelter-pulse). Infra: Terraform → one ECS Fargate task, one URL (reuse shelter-pulse pattern). **CPU-only**, no GPU.
- Conventional commits. Branch/worktree model: see `docs/parallelization.md`.

## Parallelization (swarm model)
Four tracks run in parallel against three frozen **contracts** (`docs/contracts.md`): Science (S, critical path), Infra (I), Design (D), Writeup (W). Each track works in its **own git worktree** on its own branch and owns distinct paths to avoid conflicts. Spin one up with `scripts/new-agent-worktree.sh <track>`. Full model + subagent roster: `docs/parallelization.md` and `.claude/agents/`.

## Where things live
- `docs/research-brief-v5.md`, the source of truth (problem, method, prior art, ledger).
- `docs/execution-plan.md`, day-by-day, roles, decision gates.
- `docs/contracts.md`, the θ / results-artifact / demo-API interfaces that decouple the tracks.
- `docs/parallelization.md`, worktree swarm workflow.
- `.claude/agents/`, the track subagents. `.localagent/`, the orchestrator (Ricardo + Cowork) home + state log.

## Repo system rules (non-negotiable, apply to every agent and artifact)
### Commit and PR hygiene, no AI attribution
- Do NOT add `Co-Authored-By: Claude` (or any `noreply@anthropic.com` co-author) to commit messages.
- Do NOT add "Generated with Claude Code", robot emojis, or any AI/Claude attribution to commits or PR descriptions.
- Claude's involvement is disclosed ONCE, in the hackathon writeup/documentation. Individual commits and PRs stay clean of it.
- Safety net: `scripts/git-hooks/commit-msg` strips these trailers automatically. Install after `git init` with `git config core.hooksPath scripts/git-hooks`.

### Punctuation, no em or en dashes
- NEVER use em dashes or en dashes anywhere: not in code, comments, docs, commit messages, UI copy, or the writeup. Use a comma, parentheses, a colon, or a plain hyphen instead. This is a hard style rule for every generated artifact.

### Local-only config, keep internal notes out of the public repo
- `.claude/` and `.localagent/` are gitignored on purpose (internal orchestration and strategy notes, including eligibility discussion, stay out of the public open-source repo). Do not commit them or reference their contents in public docs.
