# ecg-purkinje-npe

**Calibrated, amortized identifiability of Purkinje conduction from the surface ECG.**

Built for *Built with Claude: Life Sciences* (Researcher Track), Jul 7-13. We train an amortized Neural Posterior Estimator over conduction parameters at fixed anatomy and characterize, with formal calibration, **which parts of the cardiac conduction system a surface ECG can and cannot recover**, on a public heart mesh.

> ⚠️ **New-work timeline:** this repo's scaffold (docs, agent config) is planning material. All project **code and git history begin after hacking opens at 12:30 ET on Jul 7**. `git init` and the first commit are the director's first post-kickoff action.

## Start here
- [`docs/research-brief-v5.md`](docs/research-brief-v5.md), the source of truth: problem, method, prior art, verification ledger.
- [`docs/execution-plan.md`](docs/execution-plan.md), day-by-day plan, roles, decision gates.
- [`docs/contracts.md`](docs/contracts.md), the θ / results-artifact / demo-API interfaces.
- [`docs/parallelization.md`](docs/parallelization.md), the git-worktree agent-swarm workflow.
- [`CLAUDE.md`](CLAUDE.md), project memory for Claude Code.
- [`.claude/agents/`](.claude/agents), the parallel track subagents · [`.localagent/`](.localagent), the orchestrator cockpit.

## Stack
Python (`uv`, `ruff`, `pytest`), `sbi` for NPE; the author's own libraries `purkinje-uv`, `myocardial-mesh`, and `jaxbo` vendored in-tree (see below). FastAPI + Next.js demo; Terraform to one ECS Fargate task (CPU-only). Data: Strocchi four-chamber mesh cohort (Zenodo 3890034, CC-BY-4.0).

## Attribution and vendored components
This project stands on the author's own open-source libraries, vendored in-tree and reworked during the event as part of the new work:
- `packages/purkinje-uv` (MIT), fractal-tree Purkinje generation and the FIM eikonal activation solver; its mesh-ingestion layer is reworked here. Upstream: https://github.com/ricardogr07/purkinje-uv
- `packages/myocardial-mesh` (MIT), the volumetric myocardial eikonal and the lead-field pseudo-ECG that produce the 12-lead ECG, plus the bundled crtdemo geometry (mesh, fibers, electrodes). Upstream: https://github.com/ricardogr07/purkinje-learning-myocardial-mesh
- `packages/jax-bo` (Apache-2.0, author's own fork), the Bayesian-optimization validation baseline (added later in the week).

Each vendored library retains its upstream LICENSE. The thesis analysis package `purkinje-learning` is deliberately not used. Data: Strocchi four-chamber cohort (Zenodo 3890034, CC-BY-4.0).

## License
Apache-2.0.
