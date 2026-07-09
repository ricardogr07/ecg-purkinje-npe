# Parallelization & Agent Swarm Model

How to run **multiple Claude Code agents in parallel** without stepping on each other. The mechanism is **git worktrees**: each track (or each agent) gets its own working directory + branch, so they build simultaneously and integrate through the frozen contracts (`contracts.md`).

## Tracks → branches → owned paths

Each track owns **distinct paths**, which is what makes parallel work conflict-free. Do not edit outside your lane without a heads-up to the director.

| Track | Subagent | Branch | Owns (paths) | Depends on |
|---|---|---|---|---|
| **S, Science** (critical path) | `science` | `track/science` | `src/core/`, `src/sim/`, `src/npe/`, `src/calib/`, `experiments/` | Contract A |
| **I, Infra/Code** | `infra` | `track/infra` | `src/adapter/`, `src/api/`, `infra/`, `.github/`, `Dockerfile`, `docker-compose.yml` | Contracts A, B, C |
| **D, Design/Demo** | `design` | `track/design` | `ui/` | Contracts B, C (mocked) |
| **W, Writeup** | `writeup` | `track/writeup` | `docs/`, `README.md`, `SUBMISSION.md` | reads all |
| **(review)** | `critic` | any (read-only) |, | reads all |

Shared/append-only files (rarely edited, coordinate first): `CLAUDE.md`, `docs/contracts.md`, `pyproject.toml`. Treat contract changes as a director-gated event.

## Worktree workflow

```bash
# one-time, AFTER kickoff (12:30 ET) and an initial commit on main
git init && git add -A && git commit -m "chore: scaffold"   # director does this once

# spin up a parallel track (creates ../ecg-purkinje-npe-<track> on branch track/<track>)
scripts/new-agent-worktree.sh science
scripts/new-agent-worktree.sh infra
scripts/new-agent-worktree.sh design
scripts/new-agent-worktree.sh writeup

# in each worktree, launch Claude Code and point it at the matching subagent, e.g.:
#   cd ../ecg-purkinje-npe-science && claude
#   then delegate to the `science` subagent (or run the session as that role)
```

Each worktree is a full checkout on its own branch, four agents can run at once, each with its own context, editing only its owned paths.

## Sync cadence (three hard sync points only)

1. **Contracts frozen (Day 2):** after this, tracks run independent.
2. **Mock → real (Day 4→5):** Science's real results artifact replaces Design's mock; Infra swaps mock `/infer` for real inference.
3. **Integration (Day 5):** merge tracks into `main`; run full test + demo smoke.

Between sync points: each track merges `main` **into** its branch daily (stay current), but only merges **out** at sync points or when a unit is done + green. Rebased, small, frequent merges beat one big merge.

## Rules of the swarm

- **Own your paths.** Cross-lane edits require a director heads-up (avoids merge pain).
- **Green before merge.** `uv run pytest` (and `ui` type-check for Design) must pass before merging to `main`.
- **Contracts are law.** Build to `contracts.md`; propose changes to the director, don't unilaterally drift.
- **Critic is read-only.** The `critic` subagent reviews and reports; it never edits, mirrors the reviewer passes that caught the Grandits paper and the determinism bug.
- **Director integrates.** Ricardo (with Cowork) owns merges to `main`, the daily standup, and every scientific-claim approval.

## How to hand a task to a subagent

From a Claude Code session in the relevant worktree, delegate with a crisp spec: the goal, the owned paths, the contract it must honor, and the Definition of Done from `execution-plan.md`. Keep each agent scoped to its lane; use the `critic` for a read-only pass before anything merges.
