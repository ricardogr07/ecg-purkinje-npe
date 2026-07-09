# Results summary

Status: the honest 7D result (branch `science/grind-2026-07-08`, not merged). Numbers are the physiological-mV artifact. Everything here is synthetic-truth and calibration-honest, NOT real-ECG validated. Route through the `critic` before anything ships.

## Headline (two-part, honest)
We built a calibrated, amortized identifiability characterization of the Purkinje conduction system from the ECG, and we surfaced and quantified where our synthetic forward model diverges from a real ECG.

**The sharpened contribution:** identifiability is not a property of a parameter. It is a property of the forward map relative to a **stated noise floor**, measured on a **calibrated** posterior. Contraction alone is meaningless without both.

## Result A, the calibrated 7D identifiability spectrum
Setup: crtdemo geometry, frozen Contract A (7 params, `cv` floor lowered to 1.3), Contract D absolute-mV noise on a **physiological-mV forward** (a ~1.4 mV ECG), 5000 usable sims, amortized NPE, per-parameter conformal recalibration. Contraction = posterior std / prior std; lower means better constrained.

| parameter | contraction (post-conformal) | verdict |
|---|---|---|
| `delta_iv` | 0.15 | identifiable (strongest) |
| `cv_myo` | 0.35 | identifiable |
| `init_length_rv` | 0.63 | identifiable (moderate) |
| `cv` | 0.67 | identifiable (mild) |
| `branch_angle`, `w`, `init_length_lv` | ~1.0 to 1.2 | diffuse, formally unidentified |

Calibration: SBC ks median 0.004 to 0.150 after per-parameter conformal (passes). TARP ATC -0.072, joint near-calibrated (mildly conservative). `ridge_confirm` on the honest data: `cv_myo` is identifiable and calibrates at real SNR; the `delta_iv`-`cv_myo` correlation is a **mild ridge, not a degeneracy**.

Contraction at or above 1 for the diffuse block is conformal inflation of a near-flat, overconfident posterior, i.e. honest calibration revealing the posterior is no tighter than the prior. It is not a bug.

## How we got here (three self-corrections, and why they matter)
1. **Raw contraction looked great.** Calibration (SBC) showed the posterior was overconfident; per-parameter conformal fixed the spread. Without this we would have called the diffuse block identifiable.
2. **A posterior correlation looked like a degeneracy.** rho(delta_iv, cv_myo) = -0.72 was read as "the ECG cannot separate them." It was not: a tilted-but-thin joint is still identifiable. `ridge_confirm` refuted it. A correlation is not non-identifiability.
3. **The whole spectrum was measured in a near-noiseless regime.** The forward ran at ~73 mV against a 0.025 mV noise floor (~3000x SNR), so everything looked recoverable. Rescaling the forward to physiological millivolts and re-running produced this honest spectrum: magnitudes loosened, the ordering and the constraint/diffuse structure survived.

Each correction narrowed the claim and made it truer. This is the methodological contribution as much as the numbers are.

## Independent cross-check (not our result)
Tanikella 2025 (arXiv:2505.16696) Sobol analysis finds `branch_angle` and `w` weakly influential individually and interaction-heavy. Our inverse result (both diffuse after calibration) matches that forward prediction. Directional corroboration, not a per-parameter numeric transfer.

## Result B, forward-vs-real-ECG fidelity (diagnosed, not validated)
Full diagnosis in `outputs/fidelity_diagnosis.md`. The synthesis is exact (transplanting the true activation reproduces `True_ecg` at corr 1.000). The gap is an operating-point error: correcting cv, delta_iv, init_length lifts per-lead correlation 0.199 to 0.788 with amplitude ratios near 1, leaving a named residual. Reported as a known gap with a named real-data closure path (EDGAR, UKBB-CDT), never as validation.

## Mechanism behind the spectrum (Science Batch 3, sourced)
The ordering is not an artifact of the feature set. `delta_iv` (0.15) drives interlead TIMING (Gold 2018). `cv_myo` (0.35) drives QRS DURATION, a robust high-SNR feature. `init_length_rv` (0.63) rides an early, comparatively isolated feature: early RV/anteroseptal breakthrough writes the initial V1-V2 forces before the large LV forces develop (Durrer 1970, metadata verified; body bounded). `cv` (0.67) is global but partly degenerate with `cv_myo`. `branch_angle` and `w` are diffuse because they barely move the QRS and are interaction-dominated (Tanikella 2025 Sobol: small first-order S1, ST near 1).

The **LV/RV asymmetry** is explained by QRS genesis, not by an estimator artifact: LV initial Purkinje extent perturbs the later, LV-mass-dominated bulk of the QRS, where it is confounded with `cv_myo`, `cv`, and `delta_iv`. The DIRECTION is grounded in the normal human activation sequence. The MAGNITUDE (0.63 vs 1.0 to 1.2) is a property of this fixed anatomy and lead field and is stated as such.

## Scope and honest caveats
- **Synthetic-truth / inverse crime:** x_o comes from the same forward and noise model as training. "Identifiable" means identifiable in simulation, at the stated noise floor.
- **Geometry:** crtdemo, a simplistic model rig, not a real or synthetic heart. Public anatomy (Strocchi) is the next phase.
- **The `cv` number is confounded:** between runs BOTH the noise floor and the `cv` prior width changed (floor 1.5 to 1.3). A wider prior mechanically loosens contraction. **Never cross-compare `cv` contraction across runs with different prior widths.** Disclose this.
- **Local and noise-relative:** the spectrum is measured at one operating point and one sigma. Both are stated.
- **Our positive and negative claims have opposite worst cases.** The 1.4 mV amplitude sits on the low-normal edge of the human band, so it understates SNR. That makes "X is identifiable" conservative and "X is diffuse" anti-conservative. The diffuse block is therefore the exposed claim, and it is tested at sigma 0.025 mV and 2.0 mV amplitude, not at the operating point.
- **Prior-invariant companion.** Contraction stays the intuitive, calibration-linked headline, but it is prior-width dependent by construction. The FIM-derived per-parameter CRLB and the FIM eigenspectrum are reported alongside it as the prior-free measures (Gutenkunst 2007; Raue 2009). Note that expected information gain is NOT a fix: in the Gaussian limit EIG_k = -log(contraction_k), so it inherits the same dependence.

## Queued (for the critic and the write-up)
1. Report **pre-conformal contraction** per parameter so the before/after calibration story is a reported number, not a narrative.
2. **Forward-Jacobian analysis** (`.localagent/jacobian-spec.md`). Its role has changed: it no longer gates the ridge claim (settled), it now *explains the mechanism* and quantifies how the identifiability boundary moves with sigma. Strong, cheap addition.
3. **Demo integrity:** the UI currently renders the design mock while `/infer` serves real posteriors. It must render real numbers, or be explicitly labeled illustrative, before recording or shipping.
