# Submission: ecg-purkinje-npe

## Summary (draft, ~155 words)

We built a calibrated, amortized characterization of which Purkinje conduction
parameters are identifiable from a simulated 12-lead ECG, and which are not, at a
stated observation-noise floor. Using neural posterior estimation (sbi) over a
7-parameter conduction model at fixed anatomy, we report a per-parameter contraction
spectrum with formal calibration (SBC, expected coverage, per-parameter conformal
recalibration) rather than a single point estimate. The contribution is a scientific
finding, not a new method: interlead timing (`delta_iv`) and myocardial conduction
(`cv_myo`) are well constrained, while branch angle and the diffuse-block parameters are
formally unidentified at the operating noise floor. Along the way we surfaced and
corrected three of our own errors: calibration caught an overconfident posterior, a
ridge confirmation refuted a claimed degeneracy, and an audit found a 3000x
signal-to-noise error. That self-correction record, backed by a public verification
ledger, is the methodological contribution. No real ECG appears; comparison against
measured recordings is future work.

## Setup (the operating point every claim is relative to)
crtdemo geometry, fixed anatomy; a physiological-mV pseudo-ECG forward in an unbounded
homogeneous volume conductor (Gima and Rudy 2002), ~1.4 mV peak; Contract D observation
noise at sigma 0.025 mV; 5000 simulations; amortized NPE (sbi) with per-parameter
conformal recalibration. Identifiability is reported relative to this stated noise floor,
not as a property of a parameter in the abstract.

## Links (TODO before submit)
- [ ] Demo URL (S3 static site, Saturday deploy)
- [ ] GitHub repo (flipped public, Apache-2.0, Sunday)
- [ ] Video

## Pointers
- Finding + honest caveats: `docs/results-summary.md`
- Public claim ledger: `docs/verification-ledger.md`
- How Claude was used (single disclosure): `docs/built-with-claude.md`
- Method and priors: `docs/research-brief.md`

## Status
Draft. Final numbers, the shipped geometry (Strocchi gate is Saturday), and the demo
link land as the week closes. Route the summary through the `critic` before submitting.
