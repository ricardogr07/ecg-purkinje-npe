# Results summary

Status: the honest 7D result, merged to `main` and released as `v0.1.0-submission`. Numbers are the physiological-mV artifact. Everything here is synthetic-truth and calibration-honest, with no comparison against a real ECG.

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

Calibration: SBC ks median 0.004 to 0.150 after per-parameter conformal (passes). TARP, measured on the same drawn sample sets so only the conformal inflation differs, moves the joint ATC from **-0.057 pre-conformal to +0.007 post-conformal** (SBC ks 0.15, passes). In sbi's convention a negative ATC is **underdispersed (overconfident)** and near-zero is calibrated, so the per-parameter conformal recalibration, though it targets the marginals, also brings the **joint** into approximate calibration (from mildly overconfident to essentially calibrated, marginally conservative). A cross-split re-run on the re-sweep reproduces the direction (-0.086 to +0.024). (An earlier pre-conformal estimate via sbi's internal-sampling TARP gave -0.072; the -0.057/+0.007 pair is the matched before/after.) `ridge_confirm` on the honest data: `cv_myo` is identifiable and calibrates at real SNR; the `delta_iv`-`cv_myo` correlation is a **mild ridge, not a degeneracy**.

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

The **LV/RV asymmetry** is explained by QRS genesis, not by an estimator artifact: LV initial Purkinje extent perturbs the later, LV-mass-dominated bulk of the QRS, where it is confounded with `cv_myo`, `cv`, and `delta_iv`. The DIRECTION is grounded in the normal human activation sequence. The MAGNITUDE (0.63 vs 1.0 to 1.2) is a property of this fixed anatomy and volume-conductor forward operator and is stated as such.

## Fisher information, the Cramer-Rao bound, and the features-versus-waveform sufficiency comparison
The forward-Jacobian analysis is run at `REFERENCE_THETA`. The waveform CRLB is computed against the waveform-channel noise floor: white Gaussian, sigma = 0.025 mV per sample per lead, applied before feature extraction.

At `REFERENCE_THETA` the waveform Fisher information matrix is well conditioned (condition number 18.3) with per-parameter Cramer-Rao lower bounds well below the prior for all seven parameters, so the ECG waveform is locally informative about every parameter at that point. These two figures (condition number 18.3; waveform CRLB < 0.5% of prior range for all seven) are the existing 12-displayed-lead values. Only 8 of the 12 leads are linearly independent (I, II, V1 to V6; the other four are exact algebraic identities), so a diagonal noise model over 12 leads over-counts the Fisher information by a bounded factor of order 12/8 and the 12-lead waveform CRLB is optimistic. The corrected 8-independent-lead CRLB is looser and has not yet been recomputed (a pending retrain). The correction is a bounded 12/8 factor, not orders of magnitude, so the CRLB-to-CRLB ratios below (which cancel any common waveform scaling) are robust to it; the absolute condition-number and < 0.5% figures are the uncorrected 12-lead values.

**A features CRLB now exists (supersedes the earlier "two future tests will decide" framing).** `outputs/crlb_comparison.json` reports a features CRLB for all seven parameters, `params_dropped = 0`: the timing features are handled by mapping a 5 ms jitter to a window fraction via fs = 500 Hz (5 ms x 500 Hz = 2.5 samples over 206 = 0.0121). The per-parameter CRLB-to-CRLB ratio (features / 8-lead waveform, the ratio cancels any common waveform scaling):

| parameter | CRLB ratio (features / waveform) | block |
|---|---|---|
| `cv` | 70x | identifiable |
| `cv_myo` | 64x | identifiable |
| `init_length_rv` | 48x | identifiable |
| `w` | 43x | diffuse |
| `branch_angle` | 33x | diffuse |
| `delta_iv` | 32x | identifiable |
| `init_length_lv` | 21x | diffuse |

This is the Fisher data-processing / sufficiency result: for any summary statistic S of the data X, `I_S(theta) <= I_X(theta)`, equality iff S is sufficient (Zamir 1998). It is a CRLB-to-CRLB comparison, never CRLB-to-contraction. The feature vector discards between 21x and 70x of the per-parameter Fisher information of the waveform.

**The feature loss is roughly uniform (21x to 70x) across all seven parameters, so it does not separate identifiable from diffuse.** The lowest loss is on a diffuse parameter (`init_length_lv`, 21x), the highest on an identifiable one (`cv`, 70x); the blocks interleave. `delta_iv` (contraction 0.15, identifiable) and `branch_angle` (contraction 1.05, diffuse) lose almost the same information (32x vs 33x). Feature insufficiency, being nearly common-mode, cannot explain the diffuse block. **This overturns the earlier "the diffuse block is feature-limited" conclusion.**

**At the reference point the features locally over-determine the diffuse parameters.** Under either candidate unit convention for `crlb_features` (fraction of prior range, or raw parameter units; the conclusion holds both ways by more than an order of magnitude), the feature channel bounds `branch_angle` to a few percent of its prior locally at `REFERENCE_THETA`, while the NPE contracts it to about 105% of prior (the prior width). The diffuse block's contraction is 5x to 9x looser than the local feature bound the features permit. So the diffuse block is NOT feature-insufficient at the reference point. What a single-point feature CRLB cannot separate: (b) an estimator/budget limit, the flow at N = 5000 does not extract locally available information; or (c) a prior-averaging effect, the features are informative at `REFERENCE_THETA` but lose information elsewhere in the box. Both are consistent with the data; the single-point CRLB only rules out (a) feature-insufficiency at the reference point, exactly as a single-point FIM cannot license a global-identifiability claim.

**F3 (contraction versus training budget) points to `init_length_lv` being data-responsive.** A separate three-seed run shows `init_length_lv` tightening 1.248 to 1.010 as N grows, trend (0.238) exceeding the across-seed spread (0.183). Read with hedging (a different measurement: disjoint SBC set, 3 seeds, post-conformal, N to 4000; suggestive not decisive), it points to reading (b) for that parameter. The honest split of the diffuse block: `init_length_lv` appears budget/estimator-limited; `branch_angle` and `w` show no comparable N-response and the data cannot yet decide between (b) and (c). All three remain NOT feature-insufficient at the reference point.

**Mechanical flag.** `outputs/f3_contraction_vs_n.json` does not currently parse (JSON error, likely a NaN or truncation). The F3 three-seed point is quoted from the run note, not re-read from the artifact, and the `init_length_lv` data-limited claim is BOUNDED pending Code verifying or regenerating that file.

**Caveat.** A well-conditioned FIM and a tight local feature CRLB at one point do not certify identifiability across the prior box; a tight local bound and a diffuse prior-averaged contraction can coexist with no inconsistency. The ratios are computed under the white, lead-independent noise model, so they are an optimistic (upper) bound on the true feature-to-waveform loss; the direction of that bias is established, its magnitude is not.

## Robustness of the ordering (F8, pre-registered)
The spectrum is measured at one operating point (~1.5 mV, sigma 0.025 mV). F8 pre-registers a test of whether the ORDERING (not the levels) survives the two worst-case corners: the four identifiable parameters (`delta_iv`, `cv_myo`, `init_length_rv`, `cv`) must stay below the three diffuse ones (`branch_angle`, `w`, `init_length_lv`), on pre-conformal contraction, at both corners, for two independent noise seeds each, on the same fixed calibration split as F3. The retrains re-noise the stored waveforms; no new sims.

**Part A (waveform-injection noise, comparable to the headline): PASS at both corners, both seeds.** At 4x the operating noise (sigma 0.10 mV) the identifiable block loosens (max contraction 0.44 to 0.61) but stays below the diffuse block (min 0.77 to 0.80); at 2.0 mV amplitude the diffuse block does not resolve (min 0.77) while the identifiable block sits at 0.40 to 0.42. So the identifiable/diffuse split is not an artifact of the operating point: it survives a 4x noise increase and a higher-SNR amplitude. This is the strongest robustness statement available.

**Part B (feature-level noise, a separate probe, NOT headline-comparable): the amplitude-vs-timing separation is partial, not clean.** Under a model where amplitude features carry a fixed mV floor and timing features a fixed ms floor (so amplitude scaling changes only amplitude-feature SNR), raising the amplitude to 2.0 mV tightened `init_length_rv` most in absolute terms (contraction -0.030, the largest single move), consistent with it riding a precordial amplitude feature. But `delta_iv`, expected to be timing-dominated and so amplitude-insensitive, also tightened (-0.015, about the same ~8% in relative terms), so it is NOT amplitude-independent: it carries amplitude information as well as timing. With two seeds the `init_length_rv`-vs-`delta_iv` gap is directional, not decisive. The clean prediction (`init_length_rv` tightens, `delta_iv` flat) is only partially borne out, and we do not claim it as confirmation. (`outputs/f8_robustness.json`.)

## Scope and honest caveats
- **Synthetic-truth / inverse crime:** x_o comes from the same forward and noise model as training. "Identifiable" means identifiable in simulation, at the stated noise floor.
- **Geometry:** crtdemo, a simplistic model rig, not a real or synthetic heart. Public anatomy (Strocchi) is the next phase, and every piece of the machinery now runs on it: the full 338k-point Strocchi ventricular mesh builds in memory (FIMPY solver in ~19 s), the F6-cached `set_fiber_cv` metric-swap is bit-identical to a full solver rebuild (`experiments/f6_gate.py`, ~2x faster forward), the Strocchi eikonal solve is bit-identical deterministic across repeats (`bit_identical_twice=True`, `experiments/f7_determinism.py`), and Purkinje trees now grow on both Strocchi endocardia (F5, `experiments/f5_uvc_tree.py`: LV 44 / RV 138 PMJs). F5 was solved by feeding the mesh's own analytic UVC (rotational, apicobasal) into the FractalTree as the UV parametrization, which bypasses purkinje-uv's harmonic disk map (that map needs a clean single-boundary disk the ragged UVC-thresholded endocardium never provides), with anatomical seeds at the basal septum (His origin). What remains for a full Strocchi ECG is to wire these trees + the F6/F7 eikonal + the UVC-synthesized electrodes end to end and tune PMJ density; the components are all in place and individually verified. None of this is a fidelity claim; Strocchi ships as a method-generality figure.
- **The `cv` number is confounded:** between runs BOTH the noise floor and the `cv` prior width changed (floor 1.5 to 1.3). A wider prior mechanically loosens contraction. **Never cross-compare `cv` contraction across runs with different prior widths.** Disclose this.
- **Local and noise-relative:** the spectrum is measured at one operating point and one sigma. Both are stated.
- **Our positive and negative claims have opposite worst cases.** The 1.4 mV amplitude sits on the low-normal edge of the human band, so it understates SNR. That makes "X is identifiable" conservative and "X is diffuse" anti-conservative. The diffuse block is therefore the exposed claim, and it is tested at sigma 0.025 mV and 2.0 mV amplitude, not at the operating point.
- **Prior-invariant companion.** Contraction stays the intuitive, calibration-linked headline, but it is prior-width dependent by construction. The FIM-derived per-parameter CRLB and the FIM eigenspectrum are reported alongside it as the prior-free measures (Gutenkunst 2007; Raue 2009). Note that expected information gain is NOT a fix: in the Gaussian limit EIG_k = -log(contraction_k), so it inherits the same dependence.

## Queued (for the critic and the write-up)
1. **Pre-conformal contraction** per parameter is now emitted (`posterior.contraction_pre_conformal`) alongside the post-conformal, and the post-conformal joint TARP ATC is now measured (see Calibration above), so the before/after calibration story is a reported number, not a narrative. DONE.
2. **Forward-Jacobian analysis** DONE (`outputs/jacobian.json`; see the FIM/CRLB section above). It no longer gates the ridge claim (settled); it explains the mechanism, gives the prior-free waveform CRLB, and shows there is no local structural degeneracy. Remaining: the features-vs-waveform NPE test that separates feature loss from local-vs-global.
3. **Demo integrity:** the UI currently renders the design mock while `/infer` serves real posteriors. It must render real numbers, or be explicitly labeled illustrative, before recording or shipping.
