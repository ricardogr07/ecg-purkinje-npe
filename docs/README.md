# Documentation index

Read in this order. Every doc here is current with the shipped codebase and the honest finding. The
full technical paper lives in `../technical-writeup/`.

## The finding
- [`results-summary.md`](results-summary.md) - the calibrated 7D identifiability spectrum, the
  calibration result, the FIM/CRLB reconciliation, and the honest caveats. Start here.
- [`verification-ledger.md`](verification-ledger.md) - every factual claim with a stable ID, its
  source, and its status (VERIFIED / BOUNDED / ASSERTED / REFUTED), plus the self-retractions. The
  checkable evidence behind the finding.

## Method and background
- [`research-brief.md`](research-brief.md) - the scientific source of truth: problem, method, priors
  and their provenance, prior art, the observation-noise model.
- [`related-work.md`](related-work.md) - source-verified prior-art positioning.
- [`architecture.md`](architecture.md) - how the pipeline works end to end.
- [`contracts.md`](contracts.md) - the frozen interfaces (parameters, results artifact, demo API,
  noise model).

## How the work stayed honest
- [`scientific-process.md`](scientific-process.md) - the rigor rules and the record of the errors
  caught and corrected during the build.

## Built with Claude
- [`built-with-claude.md`](built-with-claude.md) - how Claude Code was used to build this project.
