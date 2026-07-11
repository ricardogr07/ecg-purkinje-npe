# Scientific process: rigor rules and the source-of-truth discipline

This project makes claims about what a 12-lead ECG can and cannot tell you about the Purkinje
conduction system. Those claims are only worth as much as the process that produced them. This
document is that process, written down before it was convenient.

## Why this document exists

We caught three of our own errors, each one large enough to have carried a false headline.

**A forward model declared correct at correlation 0.86.** The number was a best-lag correlation, and
it was hiding a per-lead nRMSE near 1 with a 2.3x amplitude gap. The model was misaligned and
mis-scaled, and a single favorable statistic had laundered that away.

**A degeneracy that was not there.** A posterior correlation of rho = -0.72 between `delta_iv` and
`cv_myo` was read as "the ECG cannot separate these two, it constrains only a combination." It was a
compelling story. Then `ridge_confirm` recovered `cv_myo` at correlation 0.98. A tilted joint
posterior is still an identifiable one. **A correlation is not a non-identifiability.**

**An entire identifiability spectrum measured in a near-noiseless regime.** The forward model was
emitting roughly 73 mV against a 0.025 mV noise floor, an SNR near 3000x. Everything looked
recoverable because almost nothing was noisy. Rescaling to physiological millivolts and re-running
produced the honest spectrum.

Each error was found internally, before any reviewer. Each narrowed the claim and made it truer.
Every rule below exists because one of these nearly got through.

## Part I: Rigor rules

### 1. Identifiability is not a property of a parameter

It is a property of the forward map, **relative to a stated noise floor**, measured on a
**calibrated** posterior. A parameter is not "identifiable"; it is identifiable given sigma. Every
identifiability statement in this project names its sigma. Any statement that does not is incomplete,
and the third error above is what happens when you forget.

### 2. Contraction is prior-relative, and cannot be compared across runs with different priors

Contraction is `posterior_std / prior_std`. The denominator is the prior. Widen the prior and
contraction falls, with no change to the likelihood, the data, or the physics. We changed the `cv`
floor from 1.5 to 1.3 m/s mid-project and cv's contraction moved for reasons that had nothing to do
with the ECG.

Expected information gain does not fix this. In the Gaussian limit, `EIG_k = -log(contraction_k)`
exactly, so EIG is a log rescaling of the same ratio and inherits the same prior dependence. We
checked this numerically rather than assuming it.

The prior-free axis is Fisher information. `I(theta) = J^T Sigma^-1 J` contains no prior at all.
Report the per-parameter Cramer-Rao bound `sigma_CRLB_k` and the FIM eigenspectrum alongside
contraction. **Cross-run and cross-geometry comparisons use CRLB. Contraction is reported per-run,
against its own prior.**

### 3. Positive and negative claims have opposite worst cases

"Parameter X is identifiable" and "parameter Y is diffuse" are not symmetric claims, and they are not
stressed by the same test.

Understating the signal amplitude makes positive claims conservative and negative claims
anti-conservative. Raising sigma does the reverse. So each claim class is tested at **its own** worst
case: identifiable parameters at the highest defensible sigma, diffuse parameters at the lowest sigma
and the highest amplitude. A single mid-range operating point tests neither honestly.

### 4. Calibration is a chain, not a checkbox

- **SBC** (Talts 2018) ranks the true theta among posterior samples across many prior draws. If the
  posterior is correct, those ranks are uniform by construction. We test with a KS statistic per
  parameter and report the **p-value**. Low p means non-uniform means miscalibrated.
- **Conformal recalibration** fits a per-parameter variance inflation on a held-out calibration set
  so empirical central coverage hits nominal. It has a coverage guarantee under exchangeability,
  which is why the inflation is honest rather than a fudge.
- **TARP** (Lemos 2023) tests the **joint** posterior, because SBC is per-marginal and a posterior
  can pass every marginal while being wrong jointly.

That last point is not hypothetical here. After per-parameter conformal fixed the marginals,
`cv_myo`'s SBC remained broken, which told us that **marginal recalibration cannot repair a
correlated joint posterior.** The residual is a finding, not a failure.

A contraction number reported without a calibration result is meaningless. An overconfident posterior
contracts beautifully and lies.

### 5. Compute beats narrative

When a run contradicts a story, the story dies. `ridge_confirm` killed a headline that had already
been written, sharpened, and endorsed. We kill our own claims with computation rather than argument,
and when a claim cannot be tested by computation, we say so.

### 6. The simulator is deterministic, therefore the noise model is mandatory

We verified that the fractal-tree growth never consumes its RNG: the same theta produces a
bit-identical ECG. This is the project's founding invariant, and it has a test.

It also means the likelihood is a delta function. Without an **explicit, sourced observation-noise
model**, calibration is not merely imprecise, it is undefined. The noise model is not a modeling
nicety here. It is what makes the posterior exist.

### 7. Every number in the code cites its source

Any constant that came from a paper carries its ledger ID in a comment:

```python
SIGMA_AMP_MV = 0.05   # ledger L-B3-01, QRSense, Obregon-Rosas 2026, PMID 42176693
```

A magic number without a ledger ID is a bug. This rule, had it existed on day one, would have caught
a 3000x SNR error that went unnoticed for a day.

### 8. Never present a mock as real

If any surface (UI, API, figure, video) renders placeholder data, it carries a visible "illustrative"
label until it is wired to the real artifact. A demo that looks like it shows real results while
rendering a mock is a scientific-integrity failure, not a polish issue.

### 9. Disclose the inverse crime

Our observation is generated by the same forward model and noise model used for training.
"Identifiable" means identifiable in simulation, at the stated noise floor, on the stated anatomy. We
say this every time, unprompted.

### 10. Retract in the open

Wrong claims are not quietly edited away. They are retracted in place, dated, with the evidence that
killed them. The three errors above are recorded in this repository. That record is an asset. A
project that has never retracted anything has either been lucky or has not been looking.

## Part II: Sources of truth

`docs/` is the only place truth lives. Everything else is a working note: useful, disposable, never
citable. One fact class, one home. If a number appears in two documents, one is a copy and it will
drift; copies link, they do not restate.

`docs/results-summary.md` owns every reported number. `docs/architecture.md` describes machinery and
never reports results. `docs/verification-ledger.md` is the provenance gate for every claim. Compute
artifacts (`outputs/`, released separately) are citable as data. Results and architecture rot at
different rates and answer to different readers.

## Part III: Status vocabulary

Every factual claim carries exactly one status, in the ledger. These four words, and no others.

- **VERIFIED**: read at the primary source. State what was read: abstract, author block, a specific
  table, the source code.
- **BOUNDED**: checked, but not exhaustively, or not at the body. A canonical result cited at
  attribution level. A negative result from a non-exhaustive search. State what the bound is.
- **ASSERTED**: stated from background knowledge, source never opened. Allowed in working notes.
  **Forbidden in `docs/`.** Verify it or cut it.
- **REFUTED**: checked and found false. Never silently deleted. Recorded with its correction.

A bounded negative ("no calibrated cardiac-conduction SBI paper was found") is not proof of
nonexistence, and it says so.

## Part IV: How a fact enters docs

A claim becomes citable only after it is checked at a primary source and recorded in
`docs/verification-ledger.md` with a stable ID (for example `L-B4-03`; IDs never change and are never
reused). Every claim gets a row, including refuted ones, and a `docs/` sentence with no ledger row is
wrong until a row exists. Numbers enter the source code as named constants that cite their ledger ID.

Precedence when sources disagree: compute beats narrative; the ledger beats the prose; a primary
source beats an assertion. Agreement between two accounts is not verification, especially when both
inherited the same assumption.

## What this buys

A reviewer can take any sentence in `docs/` and ask: where did this come from, who checked it, and
against what. The ledger answers in one lookup. The constants in the code answer in the other
direction, from result back to primary source. And when we are wrong, which we have been three times,
the record shows exactly how we found out.
