# Research Brief, Calibrated, Amortized Identifiability of Purkinje Conduction from the ECG

**Event:** Built with Claude: Life Sciences (Researcher Track) · **Window:** Jul 7 (12:30 PM ET) → Jul 13 (9:00 PM ET) · **Team size:** ≤ 2
**Status:** concept, pressure-tested. v5 folds in a reviewer critique (v1→v2), a prior-art verification pass (v2→v3), a source-code + competitor-paper verification pass (v3→v4), and two author-block/eligibility confirmations (v4→v5). See §13 for the changelog and §14 for the verification ledger.

---

## 0. One-line thesis

Purkinje inference from the ECG is famously non-unique, and, as of Grandits et al. 2024 (§2), the *existence* of that non-uniqueness is now published. What is **not** published is a **quantified, calibrated, amortized** characterization of it. We train an **amortized neural posterior estimator** (over conduction parameters, at **fixed anatomy**) and use it to deliver the scientific object the field still lacks: a **per-parameter contraction spectrum + posterior degeneracy/correlation structure + multimodality map**, with formal calibration guarantees (SBC / expected coverage / TARP), on a **public** cardiac anatomy.

The contribution is a **scientific characterization**, not a new inference method, plus the three adjectives that are load-bearing against the prior art: **amortized, formally calibrated, per-parameter quantified.**

> **Scope honesty (applies throughout):** MVP = **one heart, synthetic-only**. "Amortized" means *amortized over conduction parameters at fixed geometry*, **not** over anatomy. Cohort/population ("digital twins at scale") is explicit **future work**, or the single §5.9 stretch, never implied by the MVP.

---

## 1. The problem

Recovering the His-Purkinje network from a surface ECG is a canonical **ill-posed inverse problem**. It matters because the conduction system governs ventricular activation, and personalizing it underpins cardiac digital twins for device design (e.g., CRT), diagnosis, and in-silico trials.

Two facts define it:

1. **Non-uniqueness.** A surface ECG is a far-field, low-pass, spatially-integrating measurement; distinct networks / activation sequences can yield near-identical ECGs. The honest object is a *posterior*, possibly multimodal or degenerate along certain directions. (This non-uniqueness is now an established result, Grandits et al. 2024, §2, which sharpens, rather than weakens, our target.)
2. **Cost.** Existing personalization runs a fresh expensive search *per patient* (BO, ABC, MCMC, or ensemble fitting) and yields a per-patient answer without a general, calibrated statement of *what is identifiable in principle*.

**Target question:** *Given a surface ECG at fixed anatomy, how much is each conduction parameter constrained (a continuous contraction, not a binary), what is the correlation/degeneracy structure among parameters, and is the inference calibrated enough to trust?*

---

## 2. Where we're coming from (lineage & honesty)

**Published tools we consume (dependencies, not "new work"):**
- **`purkinje-uv`** (PyPI, MIT, own), fractal-tree Purkinje generation + Fast Iterative Method (FIM) eikonal solver + ECG utilities. **Verified against source:** a PCG64 RNG + reseed hooks exist in `config.py`, **but `rng` is not consumed anywhere in the growth code** (`branch.py`, `fractal_tree.py`, `edge.py`, `nodes.py`, `mesh.py`) and no random draws occur in growth, the branch angle is read directly from θ (`fractal_tree.py`: `theta = float(self.params.branch_angle)`), so the fractal growth is **deterministic given θ**; the RNG is backend/GPU-parity infrastructure, not a source of tree variability. This has a decisive method consequence (§5.5-§5.6): there is **no stochastic nuisance to exploit**, so an explicit observation-noise model is **mandatory**. (Confirm with a Day-1 same-θ-twice runtime diff, §10, §14.) We rework its mesh-ingestion layer during the event (§4), new work on a published library.
- **`JAX-BO`** (PyPI, own fork), GP Bayesian optimization; retained as a **validation baseline** (§5.8), not a speed strawman. (Own fork → included in the §8 eligibility question.)
- **`sbi`** (Apache/BSD), NPE + SBC + expected coverage + TARP.

**Prior research we extend / must distinguish from:**
- **Grandits, Gillette, Plank, Pezzuto, "Accurate and Efficient Cardiac Digital Twin from surface ECGs: Insights into Identifiability of Ventricular Conduction System"** (arXiv:2411.00165, Nov 2024). **THE closest prior art, verified accurate against the abstract.** It (i) demonstrates *for the first time* that distinct activation maps generate identical surface ECGs, (ii) introduces a Purkinje-muscle-junction physiological prior to tame the non-uniqueness, and (iii) builds a digital-twin **ensemble** for probabilistic inference of activation. **Independence caveat:** this is a *different lead group* (Graz, Plank/Gillette), **but Pezzuto co-authors both this and our own line below** (verified against both author blocks, §14), so it is the *same broader collaboration thread*, not a fully independent group. Do **not** describe it as independent; field reviewers know the overlap. Our differentiators, stated plainly: **amortized normalizing-flow NPE** (train once, infer in seconds) vs. a per-subject ensemble fit; **formal calibration diagnostics** (SBC/coverage/TARP) vs. an uncalibrated ensemble spread; **per-parameter contraction + degeneracy structure** (continuous quantification) vs. an existence-proof of non-uniqueness. Primary point of departure.
- **Álvarez-Barrientos, Salinas-Camus, Pezzuto, Sahli Costabal, "Probabilistic learning of the Purkinje network from the ECG"** (arXiv:2312.09887, *Medical Image Analysis* 2025). Anatomically accurate ventricles → rule-based fractal Purkinje → simulated ECG → **BO + ABC**, generating a population of plausible networks fitting the ECG within tolerance; addresses non-uniqueness heuristically (PMJ prior), **without amortization or formal calibration diagnostics**. This is **our own line** (see eligibility risk §8). First author confirmed from the arXiv author block: **Felipe Álvarez-Barrientos** (§14).
- **"Sensitivity of ECG QRS Complexes to His-Purkinje Structure in Computational Heart Models"** (arXiv:2505.16696, 2025). **Must-cite, must-distinguish.** A *forward sensitivity* study (fractal-tree HPS, 9 params, 10 QRS metrics, Sobol analysis): which structures move the QRS. Ours is the *inverse/identifiability* counterpart: which structures you can *recover with calibrated uncertainty*. Complementary; a forward-sensitivity result is a natural sanity check on our identifiability boundary (§5.7).
- **Dhamala et al.** (arXiv:2110.06851, 2021). **Verified:** Bayesian active learning for tissue-excitability posteriors in a 3D EP model. Not amortized, not Purkinje.
- **"Simulation-based Inference for Cardiovascular Models"** (arXiv:2307.13918, 2023). SBI for hemodynamics biomarkers, adjacent domain; establishes SBI as accepted for cardiovascular inverse problems.
- **Coleman, Camps, Hasaballa, Bueno-Orovio** (arXiv:2506.22243, Jun 2025). **Verified accurate.** Concurrent, adjacent: iterative refinement of activation (early sites + CV) then repolarisation from 12-lead + MRI anatomy; validated on 18 benchmark sims incl. HCM. Not amortized NPE, not Purkinje-topology-focused. Cited to show the SBI-for-ECG area is active (honest breadth).

**Methodological control (not a claim of prior art):** amortized estimators can, in principle, exhibit posterior over-smoothing / inflated variance that mimics unidentifiability. We control for this in §5.8 by cross-checking against non-amortized ABC. (Earlier drafts cited arXiv:2603.21752 "…limitations in Kuramoto models" for this; its abstract is positive and concerns Kuramoto oscillators, not cardiac, **dropped as evidence**. The concern is grounded instead in the SBI-diagnostics literature, Hermans et al., "A Crisis in Simulation-Based Inference," and the `sbi` coverage/TARP references. If cited, read the full text first.)

**The gap we fill:** a **calibrated, quantified, amortized identifiability characterization** of the Purkinje inverse problem, contraction + degeneracy + multimodality, on a public anatomy, controlling for amortization artifacts. Framed as a **finding**, positioned explicitly against **Grandits 2024** (existence, ensemble, uncalibrated) and **Álvarez-Barrientos 2025** (BO+ABC, uncalibrated).

---

## 3. What we want to achieve (deliverables & the finding)

**The finding (researcher-track deliverable):** the **quantified identifiability spectrum + degeneracy map**, deliberately NOT the a-priori-obvious "macro identifiable / micro not":
- a **per-parameter contraction ratio** (posterior std / prior std) with calibrated coverage, *where exactly is the identifiability boundary*;
- the **posterior correlation / degeneracy structure**, e.g., does `cv` trade off with early-activation extent along a ridge?, and **multimodality** where present (the non-uniqueness of Grandits / Álvarez-Barrientos made visible and measurable; a flow-based NPE represents it natively where point/ensemble estimates hide it);
- **pre-committed surprise reporting:** any parameter identifiable against expectation, or a nominally well-constrained parameter that turns out degenerate, reported regardless of outcome, so the finding is real either way.

Macro/micro stays only as the **narrative hook**; the measured boundary + correlation map is the deliverable.

**Concrete artifacts, all open-source:**
1. Reworked `purkinje-uv` ingestion for the public mesh format (PR-quality).
2. A fresh synthetic dataset storing **both** engineered features **and** full 12-lead waveforms per sample (one sweep, §5.3), seeded/reproducible, with a held-out test set.
3. Trained NPE model(s) (**published checkpoint**) + inference code.
4. Calibration report: SBC + expected coverage (+ TARP if time), under an explicit **noise model** (§5.6).
5. **The headline table:** parameter × contraction × coverage. **The headline figure:** posterior corner/degeneracy plot with a "pinned vs. unknowable" reveal.
6. **Paired features-vs-waveform** result on the diffuse parameters (§5.3), the credibility linchpin.
7. Baseline **agreement + speed** vs. BO+ABC on shared held-out ECGs (§5.8).
8. Packaged repo (tests, CI), Dockerized, demo page; technical write-up (problem → method → results → honest limitations → future work) + 3-min video.

---

## 4. Dataset & how we use it

**Primary (headline):** Strocchi et al. 2020, *Publicly Available Virtual Cohort of Four-chamber Heart Meshes* (Zenodo 3890034, **CC-BY-4.0**). Volumetric tetrahedral four-chamber meshes (Ensight `case`/`geo`; finer VTK), element tags (LV myo=1, RV myo=2, …), rule-based fibers, universal ventricular coordinates (UVCs), CRT RV electrode.

**MVP scope:** **one geometry, clean end-to-end.** Pull a single coarse (1.1 mm) mesh, not the full 22.5 GB.

**Ingestion rework (the `purkinje-uv` fork):** Ensight → VTK/OBJ (`meshio`/`pyvista`) → extract LV/RV **endocardial surface** by element tag (boundary of the tagged volume) → feed surface + fibers + UVCs into the fractal-tree + eikonal path; seed/define parameters in **UVC space** for anatomy-agnostic, reproducible setup.

**Dev/smoke fallback:** run the full pipeline first on the simplified `cardiac-demo` geometry, then swap in Strocchi. **If the adapter fights back, `cardiac-demo` becomes the headline**, a complete calibrated result on a simple geometry beats a broken one on a fancy mesh.

---

## 5. Method

### 5.1 Forward model (simulator)
`purkinje-uv` fractal tree → FIM eikonal activation → 12-lead ECG. Fixed per run: geometry, fibers, electrode positions, `N_it`.

### 5.2 Parameter vector θ, 7D (frozen Contract A)

> **Freeze note (Jul 7):** Contract A froze at **7D**, adding `cv_myo` (myocardial conduction velocity, inferred over [0.5, 1.0], Fu 2024) as the 7th parameter so nothing is fixed to flatter the result. Full reconciled priors, sources, and the `delta_iv` provenance are in **Appendix A**. The block hypothesis below is unchanged.

*Constraint-candidate block (hypothesis: constrained):*
1. `cv`, conduction velocity (global) → QRS **duration**.
2. **`Δ_IV`, LV-RV interventricular activation delay** *(replaces global `root_time`)* → axis/morphology; clinically meaningful (CRT). *Rationale: a global time-shift is trivially unidentifiable under shift-invariant features and would look like a bug; a relative LV-RV delay is the meaningful, recoverable quantity.*
3. `init_length` (LV), LV early-activation extent → early QRS morphology & axis.
4. `init_length` (RV), RV counterpart.

*Diffuse-candidate block (hypothesis: weakly constrained):*
5. `branch_angle`, inter-branch angle (fine topology).
6. `w`, branch-divergence weight (PMJ spread/density).

Priors: physiological uniform ranges (see eligibility note §8 re: reusing thesis ranges). 8D extension if time: `fascicles_angles` (LV/RV) → block 1; `l_segment` → block 2.

### 5.3 Observation x, paired features vs. waveform (core, not stretch)
**Generate both from the same simulation sweep**, features are computed *from* the waveform, so the paired comparison costs **training time, not simulation time.**
- **Features:** QRS duration, per-lead QRS amplitudes/integrals, frontal axis, R/S ratios.
- **Waveform:** full 12-lead + small CNN `embedding_net`.

Run NPE on **both** and compare the diffuse block. The honest claim requires this: feature-only supports "*these features* don't constrain X," while waveform-embedding supports "*the ECG* doesn't." If the waveform doesn't rescue the diffuse block, **that is the finding** (information isn't there, not discarded).

### 5.4 Inference
Amortized NPE (`sbi`, normalizing flow). Budget ~2-5k fresh sims (usable), ~10k if forward eval is cheap. **Fallback if 6D+flow coverage is poor at low budget:** switch to **sequential NPE / TSNPE** (spends budget better) or drop to 4D, decided *before* seeing bad coverage, so budget starvation isn't misread as unidentifiability.

### 5.5 Simulator determinism (verified by source; confirm Day 1)
**Verified by source inspection (§14):** `rng` is defined in `config.py` but **not referenced in any growth module**, and the branch angle is read directly from θ (`theta = float(self.params.branch_angle)`) rather than drawn from a distribution, so the simulator appears **deterministic given θ** (same θ → same tree → same ECG). The RNG is backend/GPU-parity infrastructure, not a source of variability. **Consequence:** the earlier "treat the tree realization as a stochastic nuisance / reseed per sim" plan is **void**, reseeding changes nothing because growth never reads the RNG. Diffuse-block unidentifiability is therefore **not** "many trees per θ"; it is purely **forward-map insensitivity + ECG projection**, probed by sensitivity analysis and cross-checked against the forward-sensitivity study (2505.16696, §5.7), not by seed variance.

> **Day-1 confirmation (2 lines):** run the same θ twice, diff the ECG. Identical → deterministic (expected) → §5.6 is mandatory. Different → the simulator *is* stochastic after all → revert to a nuisance-latent treatment and record seeds. This test sits at the top of Tuesday next to the forward-eval benchmark.

### 5.6 Observation-noise model (MANDATORY)

> Frozen as **Contract D** (absolute-mV white Gaussian, waveform floor 0.025 mV); the full model, realization discipline, and sourcing are in **Appendix B**.

Because the simulator is deterministic (§5.5), the explicit noise model is the **only** source of observation noise, without it, NPE trains on a deterministic map and calibration is meaningless (artificially perfect coverage). Add realistic noise at the observation: feature-level, and/or waveform-level (baseline wander, Gaussian, per-lead noise). Calibration **under this noise** is the credible version of the identifiability claim, and the noise magnitude becomes a stated modeling assumption that shifts the identifiability boundary honestly. (Sensitivity of the boundary to noise level is a natural, cheap ablation.)

### 5.7 Identifiability metric (defined now)
Headline number: **contraction = posterior_std / prior_std** per parameter (report posterior entropy too). Plus per-parameter coverage-band width. One crisp table (parameter × contraction × coverage) + the degeneracy corner plot = the deliverable. **Cross-check:** parameters that the forward-sensitivity study (2505.16696) finds barely move the QRS should show low contraction here, an independent consistency check on our boundary.

### 5.8 Baseline = validation, not a race
Run BO+ABC (`JAX-BO`) on the **same** 1-2 held-out ECGs and show **NPE's posterior agrees with ABC where ABC is trusted**, agreement + speed, not speed alone. Honest cost model: **amortize the 2-5k training sims into NPE's cost.** Use these non-amortized runs to also **rule out amortization-induced smoothing**: if ABC posteriors on the diffuse block are also wide, unidentifiability is physical, not an estimator artifact. (This control is the substantive point; it stands on its own without the dropped Kuramoto citation, §2.)

### 5.9 Anatomy-generalization (highest-value stretch, above TARP/diseased-ECG)
If the adapter is cheap, train/evaluate on 2-3 geometries and show the estimator transfers, even a tiny anatomy-generalization result is what would actually justify "amortized" language and massively strengthens Impact. Otherwise, explicit future work.

### 5.10 Compute
CPU-only is viable and recommended, cost is *simulation* (CPU), not the 6D flow (trains on CPU in minutes). Big multi-core instance for the sweep; inference is a cheap forward pass. GPU unnecessary.

---

## 6. Demo (30%, over-invest)
- **3D ventricular activation map** animating as parameters change.
- **Posterior-predictive ECG overlaid** on the input waveform.
- **Uncertainty bands** + the **degeneracy/corner plot**.
- Punchy reveal: **"this parameter is pinned, this one is unknowable"**, grounded in the measured contraction table.
- **Calibration panel** (coverage curve) = "findings you can trust."

Scored artifact is the **3-min video**; a local Dockerized demo records identically to a live one.

---

## 7. How we use Claude (Claude Use, 25%)
- **Claude Science / Research:** prior-art positioning (these verification passes are the example, they found the uncited **Grandits 2024** competitor, corrected an over-read Kuramoto citation, and caught a **source-code determinism error** that would have silently broken the noise model), calibration-study design, and adversarially interpreting posteriors ("argue against the identifiability boundary / the degeneracy claim").
- **Claude Code, the "surprise" moment:** an **agentic identifiability loop**, run sims → read SBC/coverage → automatically propose the next parameter/feature ablation or **detect a degeneracy direction** and narrate why. Closed-loop scientific reasoning reads as a *capability*, not a data-wrangling chore, and maps onto Impact. (The Ensight adapter is good engineering but reads as engineering, not a research surprise.)
- **Cowork:** orchestration, write-up, figures, demo-video script.
- Ship a first-class **"Built with Claude"** workflow section (meta-transparency).

---

## 8. Rules compliance
- [ ] **Open source:** repo Apache-2.0/MIT; publish backend, frontend, infra, and trained weights.
- [ ] **Rights:** attribute Strocchi (CC-BY-4.0); `sbi` (Apache/BSD); own libs (MIT).
- [ ] **New work, the true existential risk, broadened.** Post an explicit Day-1 #questions asking organizers about **all four**: (a) consuming our **own published PyPI libraries** as dependencies (`purkinje-uv`); (b) **reusing published parameter ranges/priors** (`BOECGParameter`), borderline "previous work"; (c) **forking our own library's ingestion layer**; (d) **using our own `JAX-BO` fork** as the baseline. New repo; all analysis/infra/demo code fresh; do **not** import `purkinje-learning`. Unarguable only if organizers say so, not a checkbox.
- [ ] **Team ≤ 2:** strongly consider a second person for frontend/demo.

---

## 9. Judging self-assessment (honest)
- **Impact (25%):** reproducible identifiability characterization others can build on. *Limit:* synthetic-only, one heart, methodological (not clinical). The degeneracy/multimodality result + anatomy-generalization stretch are what lift it above "confirmed the obvious", and above Grandits 2024's existence-proof.
- **Claude Use (25%):** weakest by default → the agentic identifiability loop (§7) is the deliberate standout.
- **Depth & Execution (20%):** home turf, calibration diagnostics, mandatory noise model, forward-sensitivity cross-check, amortization-artifact control, baseline-as-validation.
- **Demo (30%):** highest weight, biggest risk (abstract subject) → over-invest in visualization (§6).

---

## 10. Timeline (Jul 7 → Jul 13)
- **Tue Jul 7 (start 12:30 ET):** post the 4-part eligibility question; repo scaffold (Apache-2.0, CI, Docker); benchmark one forward eval; **confirm simulator determinism (same-θ-twice diff, §5.5)**; prior-predictive check (do prior-drawn ECGs look physiological?); full NPE pipeline on `cardiac-demo`.
- **Wed Jul 8:** Ensight→surface adapter; Strocchi single mesh ingested; sane 12-lead output on real anatomy.
- **Thu Jul 9:** freeze 6D θ (with `Δ_IV`) + priors + mandatory noise model (§5.6); store features and waveforms; launch fresh sim sweep (cloud CPU); dataset QC; forward-sensitivity probe of the diffuse block.
- **Fri Jul 10:** train NPE (features + waveform); SBC + expected coverage; contraction table + degeneracy plot v1.
- **Sat Jul 11:** BO+ABC agreement/validation + amortization-artifact check; demo frontend (activation map, ECG overlay, corner plot, calibration panel); AWS deploy via reused shelter-pulse Terraform, hard deadline EOD; if not up, freeze and fall back to local Docker.
- **Sun Jul 12:** locked stretch = anatomy-generalization (2-3 geometries); polish demo; write-up draft.
- **Mon Jul 13 (due 21:00 ET):** freeze results (seeds, digests, CIs); record 3-min video; finalize repo + write-up + 100-200-word summary; submit (buffer: aim 7 PM ET).

---

## 11. Risks & mitigations
1. **Forward eval too slow** → cap resolution/`N_it`, shrink budget, feature-based x.
2. **Strocchi adapter friction** → `cardiac-demo` becomes headline.
3. **Poor calibration at low budget** → TSNPE/SNPE or 4D (decide first); don't misread as unidentifiability.
4. **Apparent unidentifiability = amortization artifact** → cross-check with non-amortized/ABC (§5.8).
5. **Determinism test surprises** (simulator turns out stochastic) → revert §5.5 to nuisance-latent treatment, record seeds; noise model still fine to keep.
6. **Scope overload (solo)** → minimal infra, recruit teammate, video is what's scored.
7. **Eligibility ambiguity** → 4-part organizer question Day 1.
8. **Overclaim creep** ("cohorts / at scale") → policed in §0/§1; only claimable via §5.9.
9. **Novelty contested by Grandits 2024** → pre-empted in §2: lead with amortized + calibrated + per-parameter-quantified; never claim we discovered the non-uniqueness; never call Grandits "independent" (shared Pezzuto co-authorship).

---

## 12. Decisions (locked)
- **AWS live deploy, IN MVP (Ricardo owns it).** Guardrails: (1) reuse the shelter-pulse Terraform + one-Fargate-task + one-URL pattern verbatim, no new infra design; (2) CPU-only (§5.10), no GPU quota dependency; (3) hard timebox: if the live page isn't up by end of **Sat Jul 11**, freeze it and ship the local Dockerized demo for the video. Infra never consumes Fri/Sun science-and-demo time.
- **Top stretch, ANATOMY GENERALIZATION (§5.9), locked.** Prioritized above TARP and the diseased-ECG case.

---

## 13. What changed from v4 and why (for the reviewer)
Both v5 changes are cleanups closing open flags v4 left, each backed by a direct primary-source check this session, no substantive design change.

1. **§14 + §2 + references, the 2312.09887 author name is now confirmed, not flagged.** v4 hedged ("author block unseen; verify author order") because its own fetch returned the paper body, not the author list. A direct arXiv author-block query this session returns **Felipe Álvarez-Barrientos, Mariana Salinas-Camus, Simone Pezzuto, Francisco Sahli Costabal**, so the first-author name is confirmed, the "⚠ not confirmed" ledger row is upgraded to "✓ confirmed from author block," and the "(verify author order)" note is removed from the reference list. The same query confirmed **Pezzuto co-authors both 2312.09887 and 2411.00165** (Grandits: Thomas Grandits, Karli Gillette, Gernot Plank, Simone Pezzuto), so the "not independent" caveat (§2, §11) is now stated as verified rather than asserted.
2. **§8 + §10 + §11, eligibility question broadened from 3 parts to 4.** v4's §2 newly labeled `JAX-BO` as "(own fork)," but the eligibility question in §8 still listed only three own-library concerns. Since a fork of your own published library is the same class of question as `purkinje-uv`, `JAX-BO` is added as item (d). The timeline (§10) and risk (§11) references update from "3-part" to "4-part" for consistency.

---

## 14. Verification ledger (checked against primary sources this session)
| Claim | Source checked | Result |
|---|---|---|
| 2411.00165 (Grandits) = closest competitor; non-uniqueness existence + PMJ prior + DT ensemble | arXiv abstract | ✓ accurate; now the primary point of departure |
| Grandits author block = Grandits, Gillette, Plank, Pezzuto | arXiv author block | ✓ confirmed |
| Grandits is an "independent group" | arXiv author blocks (both papers) | ✗ overstated, Pezzuto co-authors both it and our own line; same thread (confirmed) |
| 2506.22243 (Coleman) = concurrent SBI activation+repolarisation, HCM | arXiv abstract | ✓ accurate |
| 2312.09887 first author = "Álvarez-Barrientos" | arXiv author block | ✓ confirmed, Felipe Álvarez-Barrientos (+ Salinas-Camus, Pezzuto, Sahli Costabal) |
| 2110.06851 = active learning, tissue excitability, not amortized/Purkinje | arXiv abstract | ✓ accurate |
| 2307.13918 = SBI for hemodynamics | arXiv abstract | ✓ accurate |
| 2505.16696 = forward Sobol sensitivity of QRS to HPS | arXiv abstract | ✓ accurate, must-distinguish |
| 2603.21752 supports "amortization mimics unidentifiability" | arXiv abstract only | ✗ not supported (positive result, Kuramoto), dropped as evidence |
| `purkinje-uv` tree growth is stochastic (PCG64 nuisance) | GitHub source: `config.py`, `branch.py`, `fractal_tree.py`, `edge.py`, `nodes.py`, `mesh.py` | ✗ rng not consumed in growth; branch angle read directly from θ → deterministic-given-θ; confirm with Day-1 same-θ runtime diff |

---

## References
- Strocchi et al. 2020 mesh cohort, https://zenodo.org/records/3890034 (CC-BY-4.0)
- Grandits, Gillette, Plank, Pezzuto 2024, Identifiability of the Ventricular Conduction System, https://arxiv.org/abs/2411.00165 (closest prior art)
- Álvarez-Barrientos, Salinas-Camus, Pezzuto, Sahli Costabal, Probabilistic learning of the Purkinje network from the ECG, MedIA 2025, https://arxiv.org/abs/2312.09887
- His-Purkinje → QRS sensitivity, 2025, https://arxiv.org/abs/2505.16696
- Coleman, Camps, Hasaballa, Bueno-Orovio, SBI twinning of activation/repolarisation, 2025, https://arxiv.org/abs/2506.22243
- Dhamala et al., Bayesian active learning (EP), https://arxiv.org/abs/2110.06851
- SBI for cardiovascular models, https://arxiv.org/abs/2307.13918
- Inverse ECG for cardiac digital twins: survey, https://arxiv.org/abs/2406.11445
- `sbi` toolkit (NPE, SBC, expected coverage, TARP), https://sbi-dev.github.io/sbi/
- `purkinje-uv` (own, MIT), https://github.com/ricardogr07/purkinje-uv

---

## Appendix A, Contract A priors (provenance, folded from priors.md)


Single source of truth for the Thursday Contract A freeze, reconciling two independent passes: the Research lane (`.claude_research/contract_a_*`, better-sourced numbers) and the Cowork lane (this file). Where they differed, this doc **defers to Research's sourced values**. Grounded in public literature, arrived at independently of the thesis `BOECGParameter` bounds (eligibility, brief section 8).

## Naming (resolved): code names are canonical
The serialization keys are the code names already wired into `src/core/theta.py`, the mock, and Contract B. Research's symbols are display aliases. Do not rename the keys (it would break the mock and Contract B).

## Two kinds of parameter (state this in the writeup)
- **Measured physiology:** `cv` (Purkinje CV), `delta_iv`. Ranges from electrophysiology measurements.
- **Fractal-tree model parameters:** `init_length_lv`, `init_length_rv`, `branch_angle`, `w`. Knobs of the Sahli Costabal 2015 generation method that `purkinje-uv` implements; ranges from that method paper plus the independent third-party Tanikella 2025 sensitivity study. Labeled model-plausibility, not measured anatomy.

## Recommended uniform priors (reconciled)

| code name (canonical) | alias | unit | [lo, hi] | nominal | kind | primary source |
|---|---|---|---|---|---|---|
| `cv` | CV_pk | m/s | [1.3, 3.5] | 2.2 | measured | Maguy 2009 (control 2.2 m/s, 1.5 in CHF); floor lowered 1.5 -> 1.3 (Jul 8) to bracket crtdemo true ~1.4 interior |
| `delta_iv` | dIV | ms | [-90, 40] (dyssynchrony + paced box) | ~-75 (crtdemo ref) | measured envelope + our box | Gold 2018 (measured LBBB RV-LV 77 +/- 38 ms, PMID 30354310); Burri 2005 (VV pacing +/- 40 ms, PMID 16171751); Durrer 1970 (normal, PMID 5482907). See "delta_iv provenance" below. |
| `init_length_lv` | L0_LV | mm | [30, 60] | 50 | model | OUR choice: Tanikella fixed 50 mm (LV only, not swept); the range + LV/RV split are ours |
| `init_length_rv` | L0_RV | mm | [30, 60] | 50 | model | OUR choice (see init_length_lv) |
| `branch_angle` | alpha | rad | [0.10, 0.30] | 0.175 | model | Sahli Costabal 2015 (0.15); Tanikella 2025 (0.2 +/- 30%), widened |
| `w` | w | - | [0.05, 0.20] | 0.10 | model | Sahli Costabal 2015; Tanikella 2025, widened |
| `cv_myo` | CV_myo | m/s | [0.5, 1.0] | 0.67 | measured | Fu 2024. INFERRED (7th param, director decision Jul 7) |

**FROZEN Jul 7:** 7 parameters (director chose to infer `cv_myo` rather than fix it, so no fixed nuisance remains). `cv_myo` is appended last so the first six keep their canonical order. Robustness supplement: also report at `cv_myo` = 0.5 and 1.0 to show conclusions do not hinge on it.

**Simulator constraints to respect when sampling:** `branch_angle` in (0, pi] (box is safe); `w` >= 0 (box is safe); `l_segment` <= min(init_length, length), so keep `l_segment` small (about 0.1 mm) or the 30 to 60 mm init_length box can trip the constraint.

## Freeze decisions (RESOLVED Jul 7)
1. **`init_length` LV vs RV: SEPARATE, both [30, 60]** (director). Update `src/core/theta.py` from its old asymmetric guess (LV [15,45], RV [45,95]) to symmetric [30,60] on each. Labeled our modeling choice (Tanikella fixed 50 mm, LV only).
2. **One CV or two: SEVEN params, infer `cv_myo` over [0.5, 1.0]** (director). More defensible (nothing fixed to flatter the result); costs calibration budget, so use the 5k sweep on the 7D contract. Report `cv_myo` = 0.5 / 1.0 slices as robustness.
3. **`delta_iv` width, now load-bearing (Science finding Jul 7).** The crtdemo reference is a dyssynchronous CRT case with a true `delta_iv` of about -75 ms, which is OUTSIDE the earlier [-25, 25] and [-40, 40] boxes, so the prior literally could not represent the truth and fed the miscalibration. The operative prior must span the dyssynchrony regime. Widening is a bug fix, not a preference. Two cautions: (a) prefer a SYMMETRIC sourced box (e.g. [-90, 90] or the sourced BBB range from Research P2.6) over an asymmetric box centered on -75, which would look like tuning the prior to the answer; (b) the width moves the headline, since contraction = post_std / prior_std, a wider `delta_iv` prior mechanically shrinks its contraction, so choose the width on physiology and document it. Interim Science value: [-90, 40].
4. **Other tightenings vs `theta.py`:** `cv` upper 3.5 (was 4.0), `branch_angle` [0.10, 0.30] (was [0.05, 0.40]), `w` [0.05, 0.20] (was [0.0, 0.25]). Adopt the reconciled, sourced values.

## delta_iv provenance (sourced; replaces the earlier "source-pending" placeholder)
This closes the circularity flag: the earlier [-90, 40] was reverse-engineered from crtdemo's true ~-75 ms minus a margin. The bound is now anchored to measured interventricular-timing literature. Keep the two kinds separate: what the clinic MEASURES vs the box WE choose.

**Sign convention (model):** `delta_iv = t_RV - t_LV` (RV root activation time minus LV root, LV pinned at 0). LBBB (the crtdemo regime) means the RV activates first, so LBBB `delta_iv` is negative (tens of ms). The clinical "RV-LV interventricular electrical delay" reported in CRT trials is the opposite sign (`t_LV - t_RV`, positive when the RV is early), so `delta_iv = -(RV-LV delay)`. Watch this sign when reading the numbers below.

**MEASURED physiology (the diseased + paced envelope):**
- *Normal is small.* Durrer 1970 (PMID 5482907): in the isolated normal human heart the RV and LV endocardial breakthroughs are near-simultaneous (RV breakthrough within roughly 5 to 10 ms of LV onset). So a wide `delta_iv` box is a disease/pacing box, never a normal-heart box.
- *LBBB / dyssynchrony is strongly negative (load-bearing anchor).* Gold 2018 (PMID 30354310, SMART-AV interventricular-delay substudy) measured the RV-LV interventricular electrical delay directly from the implanted leads (time between the RV and LV electrograms): LBBB 77 +/- 38 ms vs non-LBBB 40 +/- 37 ms; quartile cutoffs at 40 / 65 / 100 ms; the RV activated before the LV in 97% of LBBB (81% of non-LBBB) subjects. Mapping to our sign, LBBB `delta_iv` is centered near -77 ms with SD about 38 ms and a top quartile beyond -100 ms. crtdemo's true value (~-75 ms) sits essentially at the LBBB mean. Corroboration, same trial: Gold 2011 (PMID 21875862) reports QLV (QRS onset to LV electrogram) median 95 ms, IQR 70 to 120, up to 195 ms (n = 426), confirming the LV activates about 95 ms late in this population. Mechanism: Auricchio 2004 (PMID 14993135) mapped 24 heart-failure + LBBB hearts and found a U-shaped activation wavefront (23 of 24) travelling around a line of functional block (anterior 12, lateral 8, inferior 3): the RV activates first, the LV last via slow transseptal spread. (Auricchio's exact transseptal-time ms sit behind the paywall and are marked UNVERIFIED here; only the qualitative RV-first / LV-last pattern is taken from the abstract.)
- *Paced / RV-after-LV is positive.* Sequential biventricular pacing programs a VV offset that can pre-excite the LV, making the RV activate after the LV (positive `delta_iv`). Burri 2005 (PMID 16171751) programmed VV from LV-40 (LV pre-excited by 40 ms) to LV+40 (RV pre-excited by 40 ms); the LV-40 setting corresponds to `delta_iv` = +40 ms. A minority of CRT patients also show native LV-before-RV activation (3% of LBBB, 19% of non-LBBB, i.e. the complements of the Gold 2018 figures above), giving positive `delta_iv` with no pacing. Some devices allow VV offsets to +/- 80 ms, so +40 is conservative on this side.

**OUR modeling choice (the box):** uniform `delta_iv` over [-90, 40] ms. This is a modeling box, not a fitted or measured distribution. Each bound is chosen to CONTAIN the measured diseased + paced envelope while staying physiological:
- Lower bound -90 ms: inside the measured LBBB RV-LV distribution (Gold 2018 mean 77, SD 38, top quartile >= 100 ms), below the LBBB median and within one SD of the mean, so it represents deep-but-real LBBB dyssynchrony, not an extrapolation. crtdemo's -75 is comfortably interior.
- Upper bound +40 ms: the standard "LV pre-excited by 40 ms" sequential-pacing setting (Burri 2005), which also covers the native LV-first patients.
- The full literature envelope is roughly [-115, +80] ms (LBBB tail past the top quartile; VV pacing to +/- 80 ms in some devices), so [-90, 40] is a conservative subset and is defensible as-is.

**Honesty flag (open recommendation for Science).** The box is asymmetric and its negative magnitude (90) closely trails crtdemo's true -75, which can still read as tuned to the answer (exactly the caution in freeze-decision item 3). A symmetric [-90, 90] is equally supported by these same sources (LBBB reaches about -115; LV-preexcitation pacing reaches about +80) and would remove that appearance, at the cost of mechanically lowering `delta_iv`'s reported contraction (a wider prior). This is Science's call: the sourcing here backs either the current [-90, 40] or a symmetric [-90, 90]. It does NOT back the old narrow [-25, 25] / [-40, 40] boxes, which cannot even represent crtdemo's -75.

## Identifiability cross-check (independent corroboration)
Tanikella 2025 ran a Sobol sensitivity analysis on these same fractal-tree parameters: QRS timing is driven mainly by interactions among branch/fascicle angles and repulsivity, while single-parameter QRS features show low sensitivity to `branch_angle` and `w`. Prediction for our inverse problem: **`branch_angle` and `w` should show low posterior contraction** (the diffuse-block unidentifiability we expect). This is independent forward-model corroboration, not a result we originated. Use it as the §5.7 cross-check: low-sensitivity parameters there should be low-contraction here.

## Verification note (honesty ledger)
- The earlier Cowork gap (Sahli Costabal 2016 table unread behind a captcha) is now **closed** by the Research lane: the model-parameter ranges trace to Tanikella 2025 Table 1 (independent third party, read at full text) plus Sahli Costabal 2015 base values. Measured CVs from Maguy 2009 and Fu 2024.
- The `delta_iv` circularity flag is now **closed**: the [-90, 40] box was previously reverse-engineered from crtdemo's true ~-75 ms. It is now sourced to measured interventricular-timing literature (Durrer 1970 normal; Gold 2018 measured LBBB RV-LV delay 77 +/- 38 ms; Burri 2005 VV pacing +/- 40 ms; Auricchio 2004 mechanism). See "delta_iv provenance" above. Verdict: [-90, 40] is defensible as-is (contained in the ~[-115, +80] ms literature envelope); a symmetric [-90, 90] is equally sourced if Science prefers to avoid the appearance of tuning.
- **UNVERIFIED:** Auricchio 2004 exact transseptal-conduction-time ms (paywalled full text); only the qualitative RV-first / LV-last U-shaped pattern is checked from the abstract.
- Full source ledger with DOIs/PMIDs and the checked-vs-asserted breakdown: `.claude_research/contract_a_SOURCES.md`.

## References
- Durrer et al. 1970, Total excitation of the isolated human heart, Circulation. PMID 5482907. (normal RV/LV breakthrough near-simultaneous)
- Gold et al. 2018, Effect of Interventricular Electrical Delay on Atrioventricular Optimization for Cardiac Resynchronization Therapy, Circ Arrhythm Electrophysiol 11(8):e006055. PMID 30354310. doi:10.1161/CIRCEP.117.006055. (measured LBBB RV-LV delay 77 +/- 38 ms; `delta_iv` negative anchor)
- Gold et al. 2011, The relationship between ventricular electrical delay and left ventricular remodelling with cardiac resynchronization therapy, Eur Heart J 32(20):2516-2524. PMID 21875862. doi:10.1093/eurheartj/ehr329. (QLV median 95 ms, corroborates late LV activation)
- Auricchio et al. 2004, Characterization of left ventricular activation in patients with heart failure and left bundle-branch block, Circulation 109(9):1133-1139. PMID 14993135. doi:10.1161/01.CIR.0000118502.91105.f6. (U-shaped LBBB activation, line of block; mechanism)
- Burri et al. 2005, Optimizing sequential biventricular pacing using radionuclide ventriculography, Heart Rhythm 2(9):960-965. PMID 16171751. (VV pacing programmed LV-40 to LV+40; `delta_iv` positive anchor)
- Sahli Costabal, Hurtado, Kuhl 2015 (publ. 2016), Generating Purkinje networks in the human heart, J Biomech. PMID 26748729. (the method `purkinje-uv` implements)
- Maguy et al. 2009, Circ Res. PMID 19359601. (Purkinje CV 2.2 m/s)
- Fu et al. 2024, Rev Cardiovasc Med. PMID 39484125. (human myocardial CV compilation)
- Tanikella et al. 2025, Sensitivity of ECG QRS Complexes to His-Purkinje Structure, arXiv:2505.16696. (independent fractal-tree ranges + Sobol SA)


## Appendix B, Contract D observation-noise model (provenance, folded from observation-model.md)


Canonical, public version of the observation-noise model, reconciled from the Research lane (`.claude_research/contract_b_OBSERVATION_MODEL.md`, now gitignored). Renamed to **Contract D** to avoid the clash with Contract B (results artifact) in `docs/contracts.md`.

Naming, resolved: Contract A = theta schema (Appendix A); Contract B = results artifact; Contract C = demo API; **Contract D = observation model (this appendix)**.

## Why it exists (mandatory, not optional)
The simulator is deterministic given theta (verified: the `purkinje-uv` PCG64 rng is backend-parity infrastructure, never consumed by growth; same theta twice gives a bit-identical ECG). Training an NPE on a noise-free deterministic map gives meaninglessly perfect calibration. An explicit noise model on the ECG output is therefore required to make the identifiability question well-posed. The noise model IS the likelihood, so it must be **identical** in the training simulator, the BO+ABC baseline, and the SBC/coverage/TARP harness, or the calibration story compares different problems.

## Supersedes the Day-1 placeholder
Code's Day-1 build used 5% per-lead **relative** Gaussian noise, which the critic flagged as flattering identifiability (it preserves near-silent leads almost exactly). This Contract D replaces it with an **absolute-mV** model sourced from measured ECG reproducibility. Switch Code to this at the freeze.

## The model
Both channels come from the one theta-sweep (features are computed from the waveform), mirroring the Contract A features-vs-waveform split.

**Feature channel** (additive independent Gaussian per feature, by type):
- amplitude features (mV): sigma = 0.05 mV
- timing/duration features (ms): sigma = 5 ms

**Waveform channel** (additive white Gaussian, i.i.d. per sample per lead):
- floor: sigma = 0.025 mV (25 uV)
- robustness: optional SNR sweep 6, 12, 18, 24 dB (supplement, not the headline)

## Realization discipline (critical for a deterministic simulator)
- Add noise OUTSIDE `purkinje-uv`, at the feature/waveform stage. The simulator seed does not produce observation noise.
- Draw a FRESH noise realization per training pair (theta, x). Never reuse a fixed noise vector across the set (that reintroduces determinism).
- Fix a separate, logged noise seed so training, eval, and BO+ABC are reproducible and use the SAME model.
- The noise used to generate SBC/coverage observations must be the same model used in training.

## Day-1 verification (hand to Code)
1. Determinism: same theta twice, no noise, assert bit-identical (done, confirmed).
2. Noise-on: same theta twice WITH noise, assert outputs differ and empirical SD over N draws matches sigma (amplitude ~0.05 mV, timing ~5 ms, waveform ~0.025 mV).
3. Units sanity: confirm feature units are mV and ms (not V and s) before trusting sigma.

## Open decisions (freeze)
1. Feature-set membership: which engineered features exist and whether each is amplitude-type or timing-type (drives which sigma applies). Needs Code's final feature list.
2. Waveform sigma vs SNR: single sigma (0.025 mV) headline, SNR sweep as robustness supplement (recommended), or SNR sweep as the primary axis.
3. Correlated vs i.i.d.: i.i.d. Gaussian is the frozen default; lead-to-lead correlation and coloured artifacts (baseline wander, powerline, EMG) are documented stretches.

## Sources (independent of the thesis)
- Obregon-Rosas et al. 2026, QRSense: portable manual ECG measurement, agreement and reproducibility, J Electrocardiol. PMID 42176693. doi:10.1016/j.jelectrocard.2026.154368. (feature-noise anchor: QRS voltage LoA -0.096 to +0.192 mV -> single-measurement sigma ~0.05 mV; QRS duration LoA -16.24 to +13.59 ms -> ~5 ms) Note: first author is Obregon-Rosas, earlier drafts wrongly said "Corrales".
- Moody, Muldrow, Mark 1984, A noise stress test for arrhythmia detectors, Computers in Cardiology; MIT-BIH Noise Stress Test Database, PhysioNet. (conventional SNR-sweep protocol, descriptive citation only, not a per-sample sigma source)

Full checked-vs-asserted ledger: `.claude_research/contract_b_OBSERVATION_MODEL.md`.
