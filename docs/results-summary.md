# Results summary

Status: the honest 7D result (branch `science/grind-2026-07-08`, not merged). Numbers are the physiological-mV artifact. Everything here is synthetic-truth and calibration-honest, NOT real-ECG validated. Route through the `critic` before anything ships.

## Headline (honest)
We built a calibrated, amortized identifiability characterization of the Purkinje conduction system from a simulated 12-lead ECG, at a stated observation-noise floor. Alongside it we surfaced and corrected three of our own errors, each of which would have carried a false headline.

**No real ECG appears anywhere in this work.** The forward is a pseudo-ECG in an unbounded homogeneous volume conductor (Gima and Rudy 2002), amplitudes are reported in arbitrary units scaled to a stated mV operating point, and every target is simulator output. Comparison against measured ECGs is future work.

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

Calibration: SBC ks median 0.004 to 0.150 after per-parameter conformal (passes). TARP ATC -0.072 is **pre-conformal** (measured on the raw posterior, before the per-parameter recalibration). In sbi's convention a negative ATC is **underdispersed, i.e. slightly overconfident**, not conservative; the post-conformal joint ATC is not yet measured (per-parameter conformal targets the marginals, TARP tests the joint), so we do not yet claim the joint is calibrated. `ridge_confirm` on the honest data: `cv_myo` is identifiable and calibrates at real SNR; the `delta_iv`-`cv_myo` correlation is a **mild ridge, not a degeneracy**.

Contraction at or above 1 for the diffuse block is conformal inflation of a near-flat, overconfident posterior, i.e. honest calibration revealing the posterior is no tighter than the prior. It is not a bug.

## How we got here (three self-corrections, and why they matter)
1. **Raw contraction looked great.** Calibration (SBC) showed the posterior was overconfident; per-parameter conformal fixed the spread. Without this we would have called the diffuse block identifiable.
2. **A posterior correlation looked like a degeneracy.** rho(delta_iv, cv_myo) = -0.72 was read as "the ECG cannot separate them." It was not: a tilted-but-thin joint is still identifiable. `ridge_confirm` refuted it. A correlation is not non-identifiability.
3. **The whole spectrum was measured in a near-noiseless regime.** The forward ran at ~73 mV against a 0.025 mV noise floor (~3000x SNR), so everything looked recoverable. Rescaling the forward to physiological millivolts and re-running produced this honest spectrum: magnitudes loosened, the ordering and the constraint/diffuse structure survived.

Each correction narrowed the claim and made it truer. This is the methodological contribution as much as the numbers are.

## Independent cross-check (not our result)
Tanikella 2025 (arXiv:2505.16696) Sobol analysis finds `branch_angle` and `w` weakly influential individually and interaction-heavy. Our inverse result (both diffuse after calibration) matches that forward prediction. Directional corroboration, not a per-parameter numeric transfer.

## Result B, parameter recovery against a synthetic target (NOT a real-ECG comparison)
**There is no real ECG in this project.** `True_ecg` is a pickled simulator output stored beside the true Purkinje trees and used as a regression fixture (`myocardial-mesh/tests/e2e/test_nb_parity.py`). It is not a patient recording.

So the transplant result (true activation reproduces `True_ecg` at corr 1.000) is a **self-consistency check, not evidence of fidelity**: the same operator applied to the same activation field on the same mesh necessarily returns the same ECG. Result B compares our forward at the inferred theta against our forward at the stored true theta. Correcting the operating point lifts per-lead correlation 0.199 to 0.788, and the remaining residual is **parameter error**: theta was not recovered exactly, and a different theta regrows a different tree.

This is a parameter-recovery sanity check in the inverse-crime setting. It is not a fidelity result. A real forward-vs-measured-ECG comparison is future work with a named path (a bounded torso forward; EDGAR; MedalCare-XL).

**Pre-registered prediction (not a present finding).** In a cross-forward setting (a target generated by a different, bounded operator) the volume conductor does not cancel, and the residual is predicted to concentrate in the precordial leads. Bishop and Plank 2011 (PMID 21536529) report that the unbounded pseudo-ECG under-estimates depolarization amplitude by over an order of magnitude versus a bounded forward, worst at high tissue-to-bath ratio, which is exactly our heart-only regime.

## Mechanism behind the spectrum (Science Batch 3, sourced)
The ordering is not an artifact of the feature set. `delta_iv` (0.15) drives interlead TIMING (Gold 2018). `cv_myo` (0.35) drives QRS DURATION, a robust high-SNR feature. `init_length_rv` (0.63) rides an early, comparatively isolated feature: early RV/anteroseptal breakthrough writes the initial V1-V2 forces before the large LV forces develop (Durrer 1970, metadata verified; body bounded). `cv` (0.67) is global but partly degenerate with `cv_myo`. `branch_angle` and `w` are diffuse because they barely move the QRS and are interaction-dominated (Tanikella 2025 Sobol: small first-order S1, ST near 1).

The **LV/RV asymmetry** is explained by QRS genesis, not by an estimator artifact: LV initial Purkinje extent perturbs the later, LV-mass-dominated bulk of the QRS, where it is confounded with `cv_myo`, `cv`, and `delta_iv`. The DIRECTION is grounded in the normal human activation sequence. The MAGNITUDE (0.63 vs 1.0 to 1.2) is a property of this fixed anatomy and lead field and is stated as such.

## FIM, CRLB, and why contraction is looser than the information bound (Jacobian analysis, `outputs/jacobian.json`)
The forward-Jacobian analysis is run at `REFERENCE_THETA` on the physiological-mV forward, sigma = 0.025 mV. It reconciles the contraction spectrum with the prior-free information content, and the reconciliation has two parts that must be stated together.

**What is compared, and what is not.** The clean, sourced Fisher information is the **full 12-lead waveform** CRLB (every sample carries the Contract D per-sample sigma). We do NOT report a features CRLB: 2 of the 15 engineered features are dimensionless time fractions with no sourced jitter sigma, so the feature-space FIM is relative-only. So the CRLB describes the waveform, while the NPE that produced the contraction spectrum observes the **15 features**, a lossy summary of that waveform. These are different observations.

**The gap.** Expressed as a fraction of prior range, the waveform CRLB is under 0.5% for every one of the seven parameters (`cv` 0.0025, `delta_iv` 0.0023, `init_length_lv` 0.0044, `init_length_rv` 0.0007, `branch_angle` 0.0018, `w` 0.0024, `cv_myo` 0.0020), including the diffuse `branch_angle`/`w`. The observed contraction is 0.15 to 1.2. That two-to-three-order gap is not a contradiction; it has two sources, and the analysis cannot yet separate them: (a) the 15 features discard waveform information, most severely for `branch_angle`/`w`, which barely move the summary features (consistent with the Tanikella Sobol picture); and (b) the CRLB is a **local**, best-case Gaussian-linear bound at one operating point, while contraction is **prior-averaged** over held-out observations on the **calibrated** (conformally inflated) posterior, so a flatter map away from `theta*` widens the prior-averaged spread without changing the local bound.

**What the analysis does settle.** The R-normalized waveform map is well conditioned at `theta*` (condition number 18.3, no sub-noise direction); the softest direction `v_min` is dominated by `init_length_lv` (loading -0.94), NOT a `delta_iv`/`cv_myo` antagonism; and the iso-ECG check along `v_min` is super-noise (a full-range step moves the ECG by more than one noise SD). So there is no structural degeneracy locally, consistent with `ridge_confirm`. Caveat: the smallest singular value is finite-difference-step sensitive (relative spread 0.69 across eps in {0.005, 0.01, 0.015}), so treat its exact magnitude as order-of-magnitude; the qualitative conclusions hold across steps.

**Two tests decide the rest (training-only, no new sims).** Retrain the features-NPE at larger N (is contraction data-limited or feature-limited?), and train a waveform-NPE on the stored waveforms (does the waveform close the gap the 15 features leave, especially for the diffuse block?). If the waveform-NPE contracts far more than the features-NPE, the gap is mostly feature loss (a); if the waveform-NPE is also loose, the local CRLB overstated global identifiability (b). The re-sweep now stores waveforms expressly to run this, the features-vs-waveform comparison the brief calls the linchpin.

## Scope and honest caveats
- **Synthetic-truth / inverse crime:** x_o comes from the same forward and noise model as training. "Identifiable" means identifiable in simulation, at the stated noise floor.
- **Geometry:** crtdemo, a simplistic model rig, not a real or synthetic heart. Public anatomy (Strocchi) is the next phase.
- **The `cv` number is confounded:** between runs BOTH the noise floor and the `cv` prior width changed (floor 1.5 to 1.3). A wider prior mechanically loosens contraction. **Never cross-compare `cv` contraction across runs with different prior widths.** Disclose this.
- **Local and noise-relative:** the spectrum is measured at one operating point and one sigma. Both are stated.
- **Our positive and negative claims have opposite worst cases.** The 1.4 mV amplitude sits on the low-normal edge of the human band, so it understates SNR. That makes "X is identifiable" conservative and "X is diffuse" anti-conservative. The diffuse block is therefore the exposed claim, and it is tested at sigma 0.025 mV and 2.0 mV amplitude, not at the operating point.
- **Prior-invariant companion.** Contraction stays the intuitive, calibration-linked headline, but it is prior-width dependent by construction. The FIM-derived per-parameter CRLB and the FIM eigenspectrum are reported alongside it as the prior-free measures (Gutenkunst 2007; Raue 2009). Note that expected information gain is NOT a fix: in the Gaussian limit EIG_k = -log(contraction_k), so it inherits the same dependence.

## Queued (for the critic and the write-up)
1. Report **pre-conformal contraction** per parameter so the before/after calibration story is a reported number, not a narrative.
2. **Forward-Jacobian analysis** DONE (`outputs/jacobian.json`; see the FIM/CRLB section above). It no longer gates the ridge claim (settled); it explains the mechanism, gives the prior-free waveform CRLB, and shows there is no local structural degeneracy. Remaining: the features-vs-waveform NPE test that separates feature loss from local-vs-global.
3. **Demo integrity:** the UI currently renders the design mock while `/infer` serves real posteriors. It must render real numbers, or be explicitly labeled illustrative, before recording or shipping.
