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
Python (`uv`, `ruff`, `pytest`), `sbi` for NPE; `purkinje-uv` + `JAX-BO` as pinned dependencies (own, MIT). FastAPI + Next.js demo; Terraform → one ECS Fargate task (CPU-only). Data: Strocchi four-chamber mesh cohort (Zenodo 3890034, CC-BY-4.0).

## License
Apache-2.0.
