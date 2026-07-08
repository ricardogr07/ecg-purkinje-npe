# Status, Day 1 (Jul 7), Code / Track S+I

A grounded snapshot of where the build is after the Day-1 de-risk. Written by the Code lead for director review; reviewed by the critic (see review note at the end).

## Summary
The full forward map runs end to end on the crtdemo geometry, from the 6D conduction vector to a 12-lead ECG, and an amortized NPE trains and returns a posterior on it. The two decision gates are answered: forward eval is 14.2s per theta and the simulator is deterministic given theta. One load-bearing correction to the brief: purkinje-uv does not compute the ECG; that step lives in the myocardial-mesh library, now vendored.

## Update, Day-2 v0 identifiability snapshot (1250 sims, ~53 min, checkpointed)
First real (still low-budget, uncalibrated) run: 1250 usable sims (1330 draws) in 3169s, features NPE, artifacts in `outputs/day2_*` and `outputs/day2_results.txt`.
- **Contraction table** (median over 20 held-out obs, 1000-sim model, post_std / empirical-prior_std): `delta_iv` 0.20 (tightest), `w` 0.53, `init_length_lv` 0.56, `cv` 0.59, `init_length_rv` 0.70, `branch_angle` 0.81 (loosest). Roughly consistent with delta_iv being the most identifiable and branch_angle the least, but the diffuse/constraint split is not clean (`w` is tighter than `cv`).
- **Budget-adequacy: NOT starved.** Contraction is flat to noisy from 250 -> 500 -> 1000 sims (no steep downward trend; some params even rise), so more sims alone will not sharpen the spectrum much.
- **Calibration: FAILS at this setup.** SBC ks p-values are all below 0.05 (most below 0.01), TARP ATC is -0.096 (mild overconfidence), and in the corner plot the true theta sits in the tails or outside the posterior bulk for delta_iv, init_length_rv, and branch_angle. The posteriors are overconfident and mislocated, so the contraction numbers are NOT a trustworthy finding yet. This is the low-budget / amortization-artifact overconfidence the brief 5.8 and the critic flagged, now demonstrated.
- **Verdict on the 5k run:** the bottleneck is CALIBRATION, not budget. A 5-hour 5k sweep would not fix the SBC failure. Higher-value next moves are the brief's calibration fallbacks: TSNPE / sequential NPE (spends a small budget better and is better calibrated), a richer observation (waveform + embedding, or more features), and revisiting the noise model. Recommend NOT spending the 5 hours on 5k yet.

## Update, Day-2 evening (network variation + calibration probes, PRELIMINARY)
Ran `PLAN.md` (roadmap + mermaid), `experiments/network_variation.py`, and `experiments/calib_probe.py`. Several results contradict the earlier plan hypothesis, kept honest:
- **The "honest noise fixes calibration" hypothesis is REFUTED.** Sweeping feature-noise from 5% to 80% of feature std does not fix SBC (ks stays below 0.05 at every level); TARP ATC hovers near -0.06 to -0.10 throughout. Since train and calibration share the same noise model, SBC failing means the flow is not learning a calibrated posterior even for its own likelihood. **The miscalibration is inference-side (the density estimator), not the observation-noise floor.**
- **More data helps calibration only weakly.** SBC ks median went 0.006 (250) -> 0.003 (500) -> 0.027 (1000): a slight upward drift but still failing at 1000. A 5k run is unlikely to fully calibrate on its own.
- **Non-uniqueness, preliminary and noisy.** Only 8 of 16 random-seed networks grew (seed sampling is fragile), so treat as directional: pairwise ECG morphology correlation across distinct networks ranges -0.22 to 0.90 (median 0.44). Some network pairs are near-degenerate (0.90, distinct topology, near-identical ECG), consistent with the non-uniqueness premise, but this needs a cleaner experiment that perturbs around physiological seeds.
- **Network-induced ECG spread ~94% of amplitude** is an OVERESTIMATE inflated by non-physiological random-seed networks; not a usable noise floor as-is.
- **Forward fidelity flag:** `forward(REFERENCE_THETA)` matches the ground-truth `True_ecg` at only corr 0.20. The ECG-synthesis step is bit-exact given the true activation (myocardial-mesh `test_nb_parity`), so our Purkinje trees + coupling do not reproduce the paper's true activation at the reference theta. Needs a focused debug (scenario / root-time / coupling config), a real concern for simulator validity.
- **Redirect:** the calibration fix is inference-side, try an NPE ensemble and post-hoc (conformal / temperature) calibration before more sims; separately, debug the forward-vs-`True_ecg` gap; and redo the network experiment with physiological seed perturbations. Route the non-uniqueness read through the critic before it becomes a claim.

## What is built
- Repo initialized post-kickoff on `main` + `develop`; Apache-2.0, CI (ruff + pytest), LF `.gitattributes`, no-attribution commit hook armed; `.claude` / `.localagent` untracked.
- Three own libraries vendored in-tree under `packages/`, consumed editable: `purkinje-uv` (fractal tree + Purkinje FIM eikonal), `myocardial-mesh` (volumetric myocardial eikonal + lead-field 12-lead ECG, ships crtdemo mesh/fibers/electrodes), `jaxbo` (BO baseline, install deferred to a `baseline` group). Each retains its upstream LICENSE. `purkinje-learning` (thesis analysis) is not used.
- Forward model `src/sim/forward.py`: theta -> LV/RV fractal trees (purkinje-uv) -> Purkinje-to-myocardium coupling loop (myocardial-mesh `run_ecg_core`) -> 12-lead ECG. theta maps as: `cv` to Purkinje conduction velocity, `delta_iv` to the LV-RV root-time offset, `init_length_lv/rv` to tree init lengths, `branch_angle` and `w` to tree topology.
- Supporting core: `src/core/theta.py` (6D schema + provisional prior), `src/core/features.py` (15-dim engineered features), `src/core/noise.py` (per-lead Gaussian waveform noise), `src/sim/sweep.py` (parallel reject-and-resample sweep).

## Key findings and measurements
- **Forward eval: 7.6s median per theta** after optimization (was 14.2s at kmax=3). The crtdemo coupling converges in 2 iterations, so `kmax=2` with the per-iteration ECG early-stop skipped gives a bit-identical ECG (rel diff 0.0) at 1.87x speed, no fidelity loss. One-time geometry setup 0.4s.
- **Determinism: bit-identical** (max|delta| = 0.0 for same theta twice, same process). Simulator is deterministic given theta, so the observation-noise model is mandatory (brief 5.6). Determinism across the parallel sweep workers is not separately verified.
- **ECG-forward correction (brief 5.1):** purkinje-uv provides tree + activation only, not a 12-lead ECG. The ECG forward step is in myocardial-mesh (`MyocardialMesh.new_get_ecg` returns a 12 x T array). Vendoring it closed the gap.
- **Prior-predictive:** 7 of 8 provisional-prior draws give finite, non-degenerate 12-lead ECGs (QRS-active fraction 0.30 to 0.40); 1 wide-`init_length` draw grew outside the mesh domain, hence the reject-and-resample sweep.
- **NPE smoke (pipeline works end to end, seeded and reproducible; NOT a finding):** 169 usable sims (of 177) -> 15 features + 5% waveform noise -> sbi NPE (converged in 8s) -> posterior for a RANDOM held-out theta. Contraction (post_std / empirical-prior_std, lower = better constrained): `delta_iv` 0.17, `cv` 0.64, `init_length_rv` 0.67, `init_length_lv` 0.70, `w` 0.73, `branch_angle` 0.81. All below 1, which is necessary but NOT sufficient for identifiability (an overconfident NPE contracts too; ABC and SBC per brief 5.8 are the arbiters). Recovery, z = |post_mean - true| / post_std: five of six parameters within 1.6 sigma, but `init_length_lv` is 2.2 sigma off (post_mean 35.3 vs true 21.6), a posterior that is overconfident and mislocated, exactly the low-budget miscalibration calibration must adjudicate. Inverse crime: x_o uses the same forward and noise model as training. No identifiability direction is claimed at N=169.

## Decisions locked (Jul 7)
- Sim budget: 5,000 usable sims, laptop-only (no cloud box). After the forward optimization (7.6s/theta) and BLAS pinning, measured laptop throughput is ~1,250 usable sims/hour (2.89s wall/sim on 8 workers, ~2.6x effective parallelism, the laptop is core/memory-bandwidth bound). So 5k = ~4.7 hours wall on this laptop; 1 hour fits ~1,000 sims. Under-1-hour at 5k is NOT reachable on the laptop without a fidelity cut (reduce `N_it`, fewer PMJs) or deeper library work (cache the per-call FIM solver, speed tree growth). Options for the director: run 5k as a ~5h background job Thursday, or reduce the budget to ~1k for a 1-hour run.
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
- Parallel-sweep efficiency: BLAS pinning (`src/sim/sweep.py` sets `OMP_NUM_THREADS=1` and the MKL/OpenBLAS equivalents before numpy) plus the forward optimization (14.2s -> 7.6s, `kmax=2` + skipped per-iteration ECG) give ~1,250 usable sims/hour on the laptop (2.89s wall/sim, 8 workers). Remaining per-call levers, all with tradeoffs: reduce `N_it` (fewer PMJs, a fidelity change needing sign-off), cache the per-call FIM solver in `myocardial-mesh`, or speed `purkinje-uv` tree growth (~3.5s of the 7.6s).

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
