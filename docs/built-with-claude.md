# Built with Claude

How this project was built with Claude across four surfaces, under a human director. This is the single, disclosed account of Claude's involvement (per the repo rule, individual commits and PRs stay clean of AI attribution; the disclosure lives here). Skeleton now, filled as the week closes. TODO markers flag what to complete before submission.

## One line
A solo researcher (Ricardo, director) ran a four-surface Claude workflow, Research + Code + Design + Cowork orchestration, to produce a calibrated, amortized identifiability characterization of the Purkinje conduction system from the ECG, with a verification-first culture that repeatedly caught its own errors before they shipped.

## The four surfaces (who did what)
| Surface | Tool | Role |
|---|---|---|
| Research | Claude (Science / web research) | prior-art positioning, calibration-study design, literature-grounded priors, adversarial interpretation of results |
| Code | Claude Code | forward model, sweep, NPE, calibration, mesh adapter, backend, infra, tests |
| Design | Claude + design skills + Figma | the demo (activation map, ECG overlay, corner plot, calibration panel) and the video |
| Cowork | Claude (orchestration) | the plan, the contracts, the mock fixtures, the standup single-source-of-truth, this writeup, submission |

The director is not a coder in this setup. He sets direction, owns the human-only actions (eligibility post, credentials, recording, submit), and is the final judgment on every scientific claim. Full model: `docs/parallelization.md`, `.localagent/`.

## The standout: a verification-first culture
The most distinctive use of Claude here was not code generation but a repeated, adversarial checked-versus-asserted discipline. Concrete, real examples from this build:

- **Found an uncited competitor.** A verification pass surfaced Grandits et al. 2024 (arXiv:2411.00165), which already publishes the non-uniqueness existence result. This reframed the entire novelty claim from "we show non-uniqueness" to "amortized + formally calibrated + per-parameter quantified", before a judge could.
- **Dropped an over-read citation.** A paper (Kuramoto amortization limits) had a title that fit the argument but an abstract that did not support it; it was removed as evidence rather than cited on the strength of its title.
- **Caught a source-code determinism error.** The plan assumed the simulator was stochastic and needed reseeding; reading the actual library source showed the RNG is not consumed in tree growth, so the simulator is deterministic given theta. Confirmed at runtime (bit-identical), which is why the explicit observation-noise model is mandatory. A silent version of this error would have made the whole calibration meaningless.
- **Corrected a forward-model misattribution.** The brief said `purkinje-uv` produces the 12-lead ECG; it does not. The ECG forward lives in `myocardial-mesh`. Found while wiring the pipeline, corrected in the brief and the disclosure.
- **A read-only critic caught eight defects in one Day-1 snapshot:** a false bias claim (actually within 1.4 sigma), an unseeded run, an invalid "contraction below 1 means it learns" inference, a wrong contraction denominator, a circular recovery test, a cherry-picked direction, an eligibility drift, and bad budget arithmetic. All corrected before anything was claimed.

The brief itself was hardened across five adversarial passes (v1 to v5), each one verifying the last against primary sources. The running ledger is `docs/verification-ledger.md` (and `docs/research-brief.md` section 14).

## The agentic / parallel workflow
- Four tracks (Science, Infra, Design, Writeup) defined with owned paths and three frozen interface contracts (`docs/contracts.md`), so work decouples and runs in parallel against mocks.
- A read-only `critic` subagent gates scientific claims before merge. It never edits.
- A single source of truth (`.localagent/state.md`) carries the daily standup, decisions, and open gates; the director directs from it.
- TODO: the planned agentic identifiability loop (run sims, read SBC/coverage, propose the next ablation or flag a degeneracy direction) as the closed-loop "surprise" moment. Describe what it actually did once built.

## Reproducibility and honesty
- Everything seeded; the forward map is deterministic given theta; noise is an explicit, stated model.
- Claims are traceable to a primary source or marked unverified (example: the fractal-tree model-parameter ranges are labeled model-plausibility because the 2016 source table was not read directly, see `docs/research-brief.md` Appendix A).
- Honest limitations are stated, not hidden: synthetic-only, one heart for the MVP, and the specific noise-model caveat that flatters identifiability.

## What Claude did NOT decide
Every scientific claim, every scope cut, the vendoring/eligibility posture, and the final submission were the director's calls. Claude executed, verified, and flagged; the human integrated and approved.

## What we would do next
Three directions, in order of leverage. (1) Anatomy generalization: repeat the calibrated identifiability characterization across the public Strocchi cohort rather than one geometry, to separate what is a property of the forward map from what is a property of this fixed anatomy and electrode set. (2) A bounded forward: replace the unbounded homogeneous pseudo-ECG (Gima and Rudy 2002) with a torso volume conductor, which Bishop and Plank 2011 (PMID 21536529) report changes depolarization amplitude by over an order of magnitude, and re-measure the spectrum against that operator. (3) Real recordings: move from simulator output to measured 12-lead ECGs (EDGAR and MedalCare-XL are the named entry points), where the target is generated by a different operator and the inverse-crime setting is broken. Each step trades a stated caveat in this work for a harder test.

## To complete before submission (TODO)
- [x] Final numbers: the calibrated 7D contraction spectrum, SBC/coverage, the FIM/CRLB reconciliation, the contraction-vs-N retrains (F3), the pre-registered robustness ordering (F8), and the post-conformal joint TARP are settled on the 5000-sim sweep and live in `docs/results-summary.md` (canonical, not duplicated here to avoid drift).
- [ ] Which geometry shipped (Strocchi or the crtdemo fallback) and why.
- [ ] The agentic identifiability loop: what it did, with an example.
- [ ] Demo link + a screenshot or two.
- [ ] The organizer eligibility answer, recorded.
- [x] A one-paragraph "what we would do next" (anatomy generalization, real ECGs). See the "What we would do next" section above.
