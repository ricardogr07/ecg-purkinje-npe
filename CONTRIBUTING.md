# Contributing

Thanks for your interest. This repository is a scientific-finding project (a calibrated,
amortized identifiability characterization of the Purkinje conduction system from a simulated
12-lead ECG), so contributions are held to the same rigor as the finding itself.

## Development setup

Python is managed by [uv](https://docs.astral.sh/uv/). CPU-only, no GPU anywhere.

```
uv sync
uv run pytest            # full suite
uv run ruff check .      # lint
uv run ruff format .     # format
uv run conduction-lens --help
```

Source lives under `src/` (a pure, I/O-free `core/` plus `sim/`, `npe/`, `calib/`, `adapter/`,
`api/`) and the CLI package `conduction_lens/`. Tests import via pytest's `pythonpath` or
`PYTHONPATH=src`. To regenerate results and build the container images, see
[`REPRODUCE.md`](REPRODUCE.md).

## Ground rules

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, ...). Keep commits path-scoped and
  focused.
- **No em or en dashes** anywhere (code, comments, docs, commit messages). Use a comma,
  parentheses, a colon, or a plain hyphen.
- **Every scientific claim cites a primary source.** Numbers taken from a paper enter the code as
  named constants carrying their ledger ID; new claims get a row in
  [`docs/verification-ledger.md`](docs/verification-ledger.md). Unverified statements are marked
  "unverified", never asserted. See [`docs/scientific-process.md`](docs/scientific-process.md).
- **Never present mock or placeholder data as real.** Any surface (UI, API, figure) rendering mock
  data must be labeled illustrative until wired to the real artifact.
- **Keep a green suite.** `pytest` and `ruff` must pass; CI runs Python, UI, packaging, and Docker.

## Pull requests

As of v0.2.0, `main` is protected: it accepts no direct pushes, and every change lands through a
pull request with the full CI matrix green. This keeps the shipped, deployed version stable.

1. Branch from `main`, make focused commits.
2. Ensure `uv run pytest` and `uv run ruff check .` pass locally.
3. Open a PR describing the change and, for any scientific claim, its source. CI (Python, UI,
   packaging, Docker) must be green before merge.

## Reporting issues

Use the issue templates. For a suspected wrong result, include the exact command, the artifact or
run id, and what you expected versus observed.
