# Scientific process: rigor rules and the research SOP

This project makes claims about what a 12-lead ECG can and cannot tell you about the Purkinje conduction system. Those claims are only worth as much as the process that produced them. This document is that process, written down before it was convenient, and enforced on every lane including the director.

Three Claude lanes write here (Science, Code, Cowork/orchestration), plus a human director. Three lanes with no promotion rule produce three truths. What follows is the rule.

## Why this document exists

We have caught three of our own errors, each one large enough to have carried a false headline into publication.

**A forward model declared "validated" at correlation 0.86.** The number was a best-lag correlation, and it was hiding a per-lead nRMSE near 1 with a 2.3x amplitude gap. The model was not validated. It was misaligned and mis-scaled, and a single favorable statistic had laundered that away.

**A degeneracy that was not there.** A posterior correlation of rho = -0.72 between `delta_iv` and `cv_myo` was read as "the ECG cannot separate these two, it constrains only a combination." It was a compelling story. Then `ridge_confirm` recovered `cv_myo` at correlation 0.98. A tilted joint posterior is still an identifiable one. **A correlation is not a non-identifiability.**

**An entire identifiability spectrum measured in a near-noiseless regime.** The forward model was emitting roughly 73 mV against a 0.025 mV noise floor, an SNR near 3000x. Everything looked recoverable because almost nothing was noisy. Rescaling to physiological millivolts and re-running produced the honest spectrum.

Each error was found internally, before any reviewer. Each narrowed the claim and made it truer. Every rule below exists because one of these nearly got through.

## Part I: Rigor rules

### 1. Identifiability is not a property of a parameter

It is a property of the forward map, **relative to a stated noise floor**, measured on a **calibrated** posterior. A parameter is not "identifiable"; it is identifiable given sigma. Every identifiability statement in this project names its sigma. Any statement that does not is incomplete, and the third error above is what happens when you forget.

### 2. Contraction is prior-relative, and cannot be compared across runs with different priors

Contraction is `posterior_std / prior_std`. The denominator is the prior. Widen the prior and contraction falls, with no change to the likelihood, the data, or the physics. We changed the `cv` floor from 1.5 to 1.3 m/s mid-project and cv's contraction moved for reasons that had nothing to do with the ECG.

Expected information gain does not fix this. In the Gaussian limit, `EIG_k = -log(contraction_k)` exactly, so EIG is a log rescaling of the same ratio and inherits the same prior dependence. We checked this numerically rather than assuming it.

The prior-free axis is Fisher information. `I(theta) = J^T Sigma^-1 J` contains no prior at all. Report the per-parameter Cramer-Rao bound `sigma_CRLB_k` and the FIM eigenspectrum alongside contraction. **Cross-run and cross-geometry comparisons use CRLB. Contraction is reported per-run, against its own prior.**

### 3. Positive and negative claims have opposite worst cases

"Parameter X is identifiable" and "parameter Y is diffuse" are not symmetric claims, and they are not stressed by the same test.

Understating the signal amplitude makes positive claims conservative and negative claims anti-conservative. Raising sigma does the reverse. So each claim class is tested at **its own** worst case: identifiable parameters at the highest defensible sigma, diffuse parameters at the lowest sigma and the highest amplitude. A single mid-range operating point tests neither honestly.

### 4. Calibration is a chain, not a checkbox

- **SBC** (Talts 2018) ranks the true theta among posterior samples across many prior draws. If the posterior is correct, those ranks are uniform by construction. We test with a KS statistic per parameter and report the **p-value**. Low p means non-uniform means miscalibrated.
- **Conformal recalibration** fits a per-parameter variance inflation on a held-out calibration set so empirical central coverage hits nominal. It has a coverage guarantee under exchangeability, which is why the inflation is honest rather than a fudge.
- **TARP** (Lemos 2023) tests the **joint** posterior, because SBC is per-marginal and a posterior can pass every marginal while being wrong jointly.

That last point is not hypothetical here. After per-parameter conformal fixed the marginals, `cv_myo`'s SBC remained broken, which told us that **marginal recalibration cannot repair a correlated joint posterior.** The residual is a finding, not a failure.

A contraction number reported without a calibration result is meaningless. An overconfident posterior contracts beautifully and lies.

### 5. Compute beats narrative

When a run contradicts a story, the story dies. `ridge_confirm` killed a headline that had already been written, sharpened, and endorsed. We kill our own claims with computation rather than argument, and when a claim cannot be tested by computation, we say so.

### 6. The simulator is deterministic, therefore the noise model is mandatory

We verified that the fractal-tree growth never consumes its RNG: the same theta produces a bit-identical ECG. This is the project's founding invariant, and it has a test.

It also means the likelihood is a delta function. Without an **explicit, sourced observation-noise model**, calibration is not merely imprecise, it is undefined. The noise model is not a modeling nicety here. It is what makes the posterior exist.

### 7. Every number in the code cites its source

Any constant that came from a paper carries its ledger ID in a comment:

```python
SIGMA_AMP_MV = 0.05   # ledger L-B3-01, QRSense, Obregon-Rosas 2026, PMID 42176693
```

A magic number without a ledger ID is a bug. This rule, had it existed on day one, would have caught a 3000x SNR error that went unnoticed for a day.

### 8. Never present a mock as real

If any surface (UI, API, figure, video) renders placeholder data, it carries a visible "illustrative" label until it is wired to the real artifact. A demo that looks like it shows real results while rendering a mock is a scientific-integrity failure, not a polish issue.

### 9. Disclose the inverse crime

Our observation is generated by the same forward model and noise model used for training. "Identifiable" means identifiable in simulation, at the stated noise floor, on the stated anatomy. We say this every time, unprompted.

### 10. Retract in the open

Wrong claims are not quietly edited away. They are retracted in place, dated, with the evidence that killed them. The three errors above are recorded in this repository. That record is an asset. A project that has never retracted anything has either been lucky or has not been looking.

## Part II: Sources of truth

`docs/` is the only place truth lives. Everything else is a working note: useful, disposable, never citable.

| Kind | Location | Public | Citable as truth |
|---|---|---|---|
| Canonical docs | `docs/` | yes | yes |
| Science working notes | `.claude_research/` | no (gitignored) | no |
| Orchestration notes, state log | `.localagent/` | no (gitignored) | no |
| Compute artifacts | `outputs/`, `runs/` | released separately | yes, as data |

One fact class, one home, one owner. If a number appears in two documents, one is a copy and it will drift. Copies link, they do not restate.

| Fact class | Source of truth | Owner | Gate |
|---|---|---|---|
| Problem, method, prior art | `docs/research-brief.md` | Science | critic |
| Findings and numbers | `docs/results-summary.md` | Science + Code | critic |
| Interfaces (Contracts A/B/C/D) | `docs/contracts.md` | Code | director (frozen) |
| How the system works | `docs/architecture.md` | Code | none |
| Prior-art detail | `docs/related-work.md` | Science | critic |
| Claim provenance | `docs/verification-ledger.md` | Science | it IS the gate |
| Design surfaces | `docs/design-system.md`, `docs/heart-viewer-spec.md` | Design | none |

`docs/results-summary.md` owns every reported number. `docs/architecture.md` describes machinery and never reports results. Results and architecture rot at different rates and answer to different readers.

## Part III: Status vocabulary

Every factual claim carries exactly one status, in the ledger. These four words, and no others.

- **VERIFIED**: read at the primary source. State what was read: abstract, author block, a specific table, the source code.
- **BOUNDED**: checked, but not exhaustively, or not at the body. A canonical result cited at attribution level. A negative result from a non-exhaustive search. State what the bound is.
- **ASSERTED**: stated from background knowledge, source never opened. Allowed in working notes. **Forbidden in `docs/`.** Verify it or cut it.
- **REFUTED**: checked and found false. Never silently deleted. Recorded with its correction.

A bounded negative ("no calibrated cardiac-conduction SBI paper was found") is not proof of nonexistence, and it says so.

## Part IV: The research SOP

How a question becomes a verified fact becomes a line of code. Six steps, one owner each.

**1. REQUEST (director).** A numbered batch, prioritized P0/P1/P2. Every item states what changes if the answer is different than expected. An item whose answer changes nothing is not worth asking. Items gating a running or imminent job are marked with their deadline.

**2. DELIVER (Science).** Science returns a bundle, never a chat message:

```
conduction_lens_batchN/
  SUMMARY.md                     # headline findings, contents, bounded edges
  <one file per task>.md         # the work
  verification_ledger_batchN.md  # every claim, one row, one status, one ID
```

Ledger rows carry stable IDs (`L-B4-03`). IDs never change and are never reused. Every claim gets a row, including refuted ones. **Science never writes to the repository.** The bundle is the entire interface.

**3. INTAKE (Cowork).** The bundle lands unmodified in gitignored `.claude_research/`. Nothing in it is truth yet. Cowork checks:

- Every prose claim has a ledger row. No orphan assertions.
- The status vocabulary is used correctly.
- Every ASSERTED row is verified now or cut.
- **At least one VERIFIED row is spot-checked at its primary source.** Trust, then verify the verifier. This is how the "Corrales" misattribution was caught: the first author was Obregon-Rosas.
- Nothing contradicts a compute result. If something does, compute wins.
- No asymmetry has been glossed. A defense that protects the positive claims may quietly weaken the negative ones.

Cowork writes an intake verdict: **ACCEPT / ACCEPT WITH CUTS / REJECT**, plus four lists: promotable, cut and why, became a Code task, still open.

**4. PROMOTE (Cowork).** Only cleared lines cross into `docs/`, into the one document that owns that fact class. Ledger rows append to `docs/verification-ledger.md` with IDs intact. The raw bundle stays private forever.

**5. GATE (critic, then director).** Scientific claims pass the read-only critic before they are public. The critic never edits. The director signs every scientific claim, including the ones the director proposed.

**6. CONSUME (Code).** **Code never reads `.claude_research/`.** Code reads `docs/`. Numbers enter the source as named constants citing their ledger ID (rule 7 above).

### Precedence when lanes disagree

1. Compute beats narrative.
2. The ledger beats the prose. A doc claim with no ledger row is wrong until a row exists.
3. A primary source beats all of us, including the director.
4. The critic breaks ties.
5. The director signs.

Agreement between two lanes is not verification, especially when both inherited the same assumption.

### The two structural rules

**Science never writes code. Code never reads working notes.** Everything crosses at `docs/`, and everything that crosses carries an ID recording who checked it and against what.

## What this buys

A reviewer can take any sentence in `docs/` and ask: where did this come from, who checked it, and against what. The ledger answers in one lookup. The constants in the code answer in the other direction, from result back to primary source.

And when we are wrong, which we have been three times, the record shows exactly how we found out.
