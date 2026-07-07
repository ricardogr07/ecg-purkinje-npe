# Status, Day 1 (Jul 7), Code / Track S+I

A grounded snapshot of where the build is after the Day-1 de-risk. Written by the Code lead for director review; reviewed by the critic (see review note at the end).

## Summary
The full forward map runs end to end on the crtdemo geometry, from the 6D conduction vector to a 12-lead ECG, and an amortized NPE trains and returns a posterior on it. The two decision gates are answered: forward eval is 14.2s per theta and the simulator is deterministic given theta. One load-bearing correction to the brief: purkinje-uv does not compute the ECG; that step lives in the myocardial-mesh library, now vendored.

## What is built
- Repo initialized post-kickoff on `main` + `develop`; Apache-2.0, CI (ruff + pytest), LF `.gitattributes`, no-attribution commit hook armed; `.claude` / `.localagent` untracked.
- Three own libraries vendored in-tree under `packages/`, consumed editable: `purkinje-uv` (fractal tree + Purkinje FIM eikonal), `myocardial-mesh` (volumetric myocardial eikonal + lead-field 12-lead ECG, ships crtdemo mesh/fibers/electrodes), `jaxbo` (BO baseline, install deferred to a `baseline` group). Each retains its upstream LICENSE. `purkinje-learning` (thesis analysis) is not used.
- Forward model `src/sim/forward.py`: theta -> LV/RV fractal trees (purkinje-uv) -> Purkinje-to-myocardium coupling loop (myocardial-mesh `run_ecg_core`) -> 12-lead ECG. theta maps as: `cv` to Purkinje conduction velocity, `delta_iv` to the LV-RV root-time offset, `init_length_lv/rv` to tree init lengths, `branch_angle` and `w` to tree topology.
- Supporting core: `src/core/theta.py` (6D schema + provisional prior), `src/core/features.py` (15-dim engineered features), `src/core/noise.py` (per-lead Gaussian waveform noise), `src/sim/sweep.py` (parallel reject-and-resample sweep).

## Key findings and measurements
- **Forward eval: 14.2s median per theta** (crtdemo, kmax=3, CPU); one-time geometry setup 0.4s. Trivially parallel.
- **Determinism: bit-identical** (max|delta| = 0.0 for same theta twice, same process). Simulator is deterministic given theta, so the observation-noise model is mandatory (brief 5.6). Determinism across the parallel sweep workers is not separately verified.
- **ECG-forward correction (brief 5.1):** purkinje-uv provides tree + activation only, not a 12-lead ECG. The ECG forward step is in myocardial-mesh (`MyocardialMesh.new_get_ecg` returns a 12 x T array). Vendoring it closed the gap.
- **Prior-predictive:** 7 of 8 provisional-prior draws give finite, non-degenerate 12-lead ECGs (QRS-active fraction 0.30 to 0.40); 1 wide-`init_length` draw grew outside the mesh domain, hence the reject-and-resample sweep.
- **NPE smoke (pipeline works end to end, seeded and reproducible; NOT a finding):** 169 usable sims (of 177) -> 15 features + 5% waveform noise -> sbi NPE (converged in 8s) -> posterior for a RANDOM held-out theta. Contraction (post_std / empirical-prior_std, lower = better constrained): `delta_iv` 0.17, `cv` 0.64, `init_length_rv` 0.67, `init_length_lv` 0.70, `w` 0.73, `branch_angle` 0.81. All below 1, which is necessary but NOT sufficient for identifiability (an overconfident NPE contracts too; ABC and SBC per brief 5.8 are the arbiters). Recovery, z = |post_mean - true| / post_std: five of six parameters within 1.6 sigma, but `init_length_lv` is 2.2 sigma off (post_mean 35.3 vs true 21.6), a posterior that is overconfident and mislocated, exactly the low-budget miscalibration calibration must adjudicate. Inverse crime: x_o uses the same forward and noise model as training. No identifiability direction is claimed at N=169.

## Decisions locked (Jul 7)
- Sim budget: 5,000 usable sims. Honest cost with the ~15% reject rate is ~5,900 draws x 14.2s = ~23 core-hours ideal. BLAS pinning brought the observed per-sim overhead from ~3x to ~1.8x (534s / 169 sims / 8 workers), so realistic cost is closer to ~40 core-hours until the overhead falls further. Fitting 1 hour needs ~40 physical cores at current efficiency, or more per-call optimization. Not yet demonstrated at 5k scale.
- Observation noise: included; day-1 assumption is 5% per-lead Gaussian at the waveform (a stated, revisable magnitude).
- Vendoring: own libraries vendored in-tree and reworked, disclosed in README, LICENSEs retained; `purkinje-learning` excluded.
- Team: solo. Bias to ruthless cuts and demo-first fallbacks; protect the Science critical path.

## Verification-ledger updates
- "purkinje-uv provides 12-lead ECG utilities": FALSE. Corrected; ECG is in myocardial-mesh.
- "simulator deterministic given theta": CONFIRMED at runtime (was source-inspection only).

## Open items and honest gaps
- Provisional theta ranges in `theta.py` are UNVERIFIED guesses; need literature grounding before the Contract A freeze (Thu). Deliberately not the thesis `BOECGParameter` bounds (eligibility).
- Reject-and-resample truncates the effective prior to the growable region; this is a modeling choice to state in calibration.
- Eligibility: `myocardial-mesh` (upstream `purkinje-learning-myocardial-mesh`) is ACCEPTED (director decision Jul 7) as a separate published MIT library that provides the 12-lead ECG forward, distinct from the forbidden `purkinje-learning` thesis analysis. It is disclosed in README and named in the organizer question (the 5-part post in `.localagent/eligibility-question.md`; the earlier 4-part count in the brief/plan is superseded). The general "own published libraries as dependencies" question is still out to organizers for confirmation, but we are proceeding.
- Features are a minimal 15-dim set; the paired features-vs-waveform comparison (brief 5.3) and a CNN waveform embedding are not yet built.
- Noise is applied one draw per theta in the smoke; calibration will want it treated properly (per-observation, multiple draws). Structural caveat: the noise is per-lead-relative (sigma = frac x lead std), which preserves near-silent leads almost exactly and leaks morphology, an undisclosed choice that flatters identifiability. The natural ablation (brief 5.6) is an absolute mV floor.
- Parallel-sweep efficiency: unpinned the first smoke ran 177 sims in 978s on 8 workers (~3x the 14.2s single-thread cost, BLAS/VTK oversubscription). `src/sim/sweep.py` now pins `OMP_NUM_THREADS=1` and the MKL/OpenBLAS equivalents before numpy import, which cut the re-run to 534s (~1.8x faster), but that is still ~1.8x above ideal linear (169/8 x 14.2 = ~300s), so per-call overhead remains. The 5k sweep needs a box with enough physical cores plus further overhead reduction to fit 1 hour.

## Next steps
- Wed: Ensight to endocardial-surface adapter; ingest one Strocchi mesh; sane 12-lead output on real anatomy.
- Thu: freeze Contract A (6D theta + literature-grounded priors + noise magnitude); launch the 5k parallel sweep storing features and waveforms.
- Fri: train NPE on features and waveform; SBC + expected coverage; contraction table + degeneracy plot.

## Review note (critic pass, Jul 7)
The critic subagent reviewed this doc read-only against the source and traced every number to the code. It flagged real defects, corrected here:
- "delta_iv is biased" was WRONG: with prior_std ~23 ms and contraction ~0.28, a mean of 9 vs true 0 is ~1.4 sigma, so truth sits inside the credible band. Corrected: the smoke paragraph now reports a z-score (|mean - true| / post_std) instead of a bias claim, and reports all six posterior means, not a selected two.
- Unseeded NPE: FIXED. `torch.manual_seed(0)` added, so the reported digits are reproducible.
- "contraction < 1 means it learns signal" was an invalid inference (overconfident/miscalibrated NPE also contracts). Corrected to necessary-but-not-sufficient, with ABC/SBC as the pending arbiter (brief 5.8).
- Contraction denominator used the nominal box; reject-and-resample truncates the prior. FIXED: the denominator is now the empirical std of the accepted training thetas.
- Recovery was circular: `REFERENCE_THETA` is the rig's design preset, not held out. FIXED: the observation is now a random interior held-out theta. The inverse crime (same forward + noise for x_o and training) is named in code and here.
- Cherry-picked "hypothesized direction": REMOVED (diffuse `branch_angle` beat constraint `cv`, so the hypothesis is not even directionally clean at N=169). No direction is claimed.
- Eligibility exposure on `myocardial-mesh` naming and the 4-vs-5-part drift: escalated to Open items for director action.
- Budget arithmetic that missed 1 hour: corrected in Decisions.

Deferred (next steps, not blockers): absolute-mV noise-floor ablation, ABC cross-check + SBC calibration, a multi-seed CI on the contraction numbers, and a parallel-worker determinism check.
