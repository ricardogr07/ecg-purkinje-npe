---
title: "Which conduction parameters can an electrocardiogram determine? A calibrated identifiability characterization of the His-Purkinje system"
author:
  - The conduction-lens project
date: 2026-07-10
abstract-title: Abstract
---

## Abstract {-}

Conduction models are routinely fit to the electrocardiogram (ECG) and their parameter values reported, but the prior question of which conduction parameters an ECG can determine at all is rarely asked, and a model can fit while its reported number carries no information. We characterize the identifiability of seven His-Purkinje and myocardial conduction parameters from the 12-lead ECG at fixed anatomy, using a single amortized neural posterior estimator with a formal calibration audit (simulation-based calibration, expected coverage, and TARP). Against an explicit observation-noise floor (feature channel: amplitude 0.05 mV, timing 5 ms), the prior-averaged posterior contraction orders the parameters as interventricular delay (about 0.15) and myocardial velocity (about 0.35) well constrained, RV initial Purkinje extent moderately constrained (about 0.63), and LV extent, branch angle, and branch repulsivity diffuse (about 1.0 to 1.2). The forward is a pseudo-ECG in an unbounded homogeneous volume conductor with arbitrary-unit amplitudes, not a torso lead model; there is no measured ECG in the study, and the noise model is white where real ECG noise is not, so the waveform bound is optimistic in a stated direction of unestablished magnitude. Identifiability statements are conditional on that floor and that forward.


# Introduction

The His-Purkinje conduction system sets the sequence in which the two ventricles activate: an insulated network of fast-conducting fibers carries the activation wavefront from the atrioventricular node to a spatially distributed set of terminal junctions on the endocardium, and the resulting endocardial breakthrough pattern shapes the whole of ventricular depolarization [@durrer1970] (purkinje_brief). This network cannot be observed directly in a living patient without an invasive electroanatomical study, so the routine noninvasive window onto ventricular activation is the surface electrocardiogram (ECG), a far-field, spatially integrating measurement of the potentials that activation produces at the body surface [@gimarudy2002] (forward_operator_note). The clinical stakes are concrete: interventricular electrical delay is a measurable predictor of who benefits from cardiac resynchronization therapy [@gold2017; @gold2018] (related-work). A conduction parameter that could be recovered from the ECG would therefore be a conduction parameter that could inform therapy.

This has motivated a line of work that fits a conduction model to a measured or simulated ECG and reports estimated parameter values. Grandits et al. build a cardiac digital twin from the surface ECG and infer properties of the ventricular conduction system [@grandits2024], and a related line learns a fractal Purkinje network from the ECG with Bayesian optimization plus approximate Bayesian computation [@alvarezbarrientos2025]. Both return conduction parameters. Neither first asks the question that logically precedes any reported value: given this ECG and this forward model, which conduction parameters can the ECG determine at all, and how well.

That question is not rhetorical, because the ECG-to-conduction map is non-injective. Grandits et al. demonstrate that distinct activation maps can generate identical surface ECGs [@grandits2024] (related-work), which means a fitting procedure can converge, report a tight-looking value, and have that value be a consequence of the optimizer or the prior rather than a quantity the data actually constrain. A model can fit and its reported number still carry no information. Reporting a point estimate, or an ensemble spread, without a calibration audit does not distinguish an identified parameter from an unconstrained one.

This work addresses that gap. We deliver a quantified identifiability characterization of the seven conduction parameters $\theta = \{cv,\ cv\_myo,\ \delta_{IV},\ init\_length\_lv,\ init\_length\_rv,\ branch\_angle,\ w\}$ at fixed anatomy. The primary quantity is a per-parameter contraction, defined as the posterior standard deviation divided by the prior standard deviation and reported against an explicit observation-noise model (feature channel: amplitude $\sigma = 0.05$ mV and timing $\sigma = 5$ ms; waveform channel: white Gaussian $\sigma = 0.025$ mV per sample per lead), together with the posterior correlation and degeneracy structure among the parameters (observation_model, purkinje_brief). The characterization is produced by a single amortized neural posterior estimator, a normalizing flow trained once over the parameter space at fixed geometry [@papamakarios2016; @greenberg2019], and its reliability is then tested with formal calibration diagnostics. The contribution is a measurement of the identifiability structure, not a new inference method and not a statement about how closely the forward reproduces any measurement.

The calibration step is load-bearing precisely because it is easy to over-read. A calibration diagnostic checks whether the posterior's stated uncertainty is self-consistent; it is necessary before any contraction is interpreted, but it is not itself evidence that the ECG carries information about a parameter, because a posterior equal to the prior is perfectly calibrated and maximally diffuse [@talts2018; @hermans2021; @lemos2023] (related-work). We therefore report contraction against the stated noise floor and audit calibration separately, and we read a near-prior posterior as a weakly constrained parameter under that floor, not as a failure of the estimator.

# Background and antecedents

## Purkinje anatomy and function

The His-Purkinje system is the specialized rapid-conduction pathway of the ventricles. Activation leaves the atrioventricular node, descends the bundle of His, divides into the bundle branches, and arborizes into a dense subendocardial Purkinje network that terminates at Purkinje-myocardial junctions, the discrete sites at which the fast-conducting network hands the wavefront off to working myocardium. Because these junctions are spatially distributed over the endocardium and fire in a characteristic order, the network fixes the earliest endocardial activation sites and therefore the initial direction and timing of ventricular depolarization. The reference description of the normal human sequence comes from direct intramural mapping of the isolated human heart [@durrer1970], which established the timing and spatial order of ventricular activation that any conduction model must reproduce.

The activation sequence is sensitive to the network structure, but not uniformly so. A forward sensitivity analysis of QRS morphology to His-Purkinje structure finds that most small structural changes move individual QRS features only slightly, while specific parameter combinations produce large effects [@tanikella2025] (related-work). This mixed picture, where some structural degrees of freedom strongly shape the QRS and others barely register in it, is the forward-side counterpart of the identifiability question this work quantifies from the posterior: parameters that a forward analysis finds barely move the QRS are the parameters we expect to be weakly constrained under the stated noise floor.

## Conduction modelling: eikonal and monodomain

Two levels of description are standard for ventricular activation. The monodomain reaction-diffusion model represents the transmembrane potential across the tissue and propagates a wavefront whose speed is set by the balance of the diffusive and ionic terms. The eikonal model is the large-scale limit of that front: it solves directly for the activation-time field, with the local front speed governed by the tissue conductivity or diffusivity tensor. Keener derived the eikonal-curvature equation for cardiac action-potential propagation as the computationally efficient limit of the full ionic model [@keener1991] (modeling_sources). Working at the activation-time level is what makes a large parameter sweep tractable.

Two modelling facts justify the choices this level of description entails. First, using a monodomain or eikonal activation with a surface-potential recovery rather than a full bidomain solve is defensible because the difference between monodomain and bidomain surface potentials is very small [@potse2006] (strocchi_ecg_setup, modeling_sources). Second, ventricular tissue conducts orthotropically, fastest along the fiber direction and slower transverse and sheet-normal, with a fiber to transverse conduction-velocity ratio near 2:1 to 3:1 that is stable enough across preparations to be treated as a fixed structural constant while the overall speed varies [@caldwell2009] (modeling_sources). This background sketch fixes the modelling family; the specific solver settings and parameterization are given in Methods.

## The ECG forward problem

The ECG forward problem is the map from a ventricular activation sequence to the potentials recorded at the body-surface electrodes. The lineage this work draws on is the pseudo-ECG, in which each surface potential is computed as a functional of the transmembrane-voltage field of the cardiac source: Gima and Rudy showed that body-surface-like ECG waveforms can be computed directly from the cellular transmembrane activity of a cardiac model [@gimarudy2002] (forward_operator_note, strocchi_ecg_setup). The map from activation to surface potentials depends in general on the assumed volume conductor between the heart and the electrodes, and both the fidelity and the assumptions of that map matter for any downstream inference. The specific forward operator used in this project, including its volume-conductor assumption, its electrode-geometry convention, and its amplitude reporting, is defined in Methods and is not pre-empted here.

## Prior art, positioned honestly

The two closest works on inferring conduction from the ECG are not independent of this project, and we state that plainly rather than presenting them as external corroboration.

Grandits et al. build a cardiac digital twin from surface ECGs and, for the first time, demonstrate that distinct activation maps can generate identical surface ECGs, responding with a physiological Purkinje-myocardial-junction prior and a digital-twin ensemble for probabilistic inference [@grandits2024] (related-work). This is the closest prior art and the reason we do not claim the non-uniqueness finding as ours. It is not an independent group: its author list shares coauthors with this project's line, including Plank and Pezzuto (related-work). Our point of departure from it is that we produce an amortized normalizing-flow posterior rather than a per-subject ensemble fit, we audit calibration formally, and we report a per-parameter contraction and degeneracy structure rather than an existence proof of non-uniqueness.

Alvarez-Barrientos et al. learn a fractal Purkinje network from the ECG using Bayesian optimization plus approximate Bayesian computation, generating a population of plausible networks that fit the ECG within tolerance [@alvarezbarrientos2025] (related-work). This is this project's own prior-work line, sharing Pezzuto and Sahli Costabal as coauthors (related-work). It is therefore a baseline and a point of departure, not independent evidence: relative to it we add amortization, formal calibration diagnostics, and a per-parameter identifiability quantification.

The closest amortized cardiac simulation-based inference is in a different organ system. Manduchi et al. train an amortized neural posterior estimator on cardiac simulations, but for whole-body hemodynamics, mapping pressure waveforms to physiological parameters, not for the ECG or conduction [@manduchi2024] (related-work). That amortized cardiac neural posterior estimation already exists in hemodynamics sharpens rather than weakens the present contribution: it locates our contribution as the conduction-from-ECG instance with a formal identifiability characterization, not the amortized method itself.

Our differentiator relative to this Bayesian cardiac-conduction literature is calibration. In targeted searches of arXiv and PubMed combining simulation-based inference, neural posterior estimation, and amortized inference with cardiac and electrocardiogram terms and with calibration and coverage terms, no cardiac-conduction personalization paper was found that reports a formal posterior-calibration diagnostic, that is, simulation-based calibration [@talts2018], expected coverage [@hermans2021], or TARP [@lemos2023]; the Bayesian cardiac-conduction works we did verify report accuracy or ensemble spread rather than calibration (related-work). This is a bounded negative, not a proof of nonexistence: no such paper was found in the searches performed, and the negative is bounded by an incomplete citation-graph search, because the OpenAlex forward-citation traversal could not be run for this review (related-work). The neural posterior estimation methods we build on are standard [@papamakarios2016; @greenberg2019], as is the broader simulation-based inference framework [@cranmer2020]; what is not standard, and what we contribute, is applying the calibration audit to a Purkinje-conduction posterior from the ECG and using it to license a per-parameter identifiability statement.

# Methods

## Forward model

The forward operator maps a conduction parameter vector $\theta$ to a 12-lead surface signal through a fixed chain: a `purkinje-uv` fractal-tree His-Purkinje network, a fast iterative method (FIM) eikonal activation solve on that tree, and a pseudo-ECG readout. The pipeline runs at fixed anatomy on a single four-chamber mesh from the Strocchi et al. cohort [@strocchi2020]; anatomy is not inferred.

The ECG readout is a pseudo-ECG computed in an unbounded, homogeneous volume conductor [@gimarudy2002]. The operator returns classic $1/|r|$ node-wise weights per electrode: an infinite, homogeneous medium with no torso, no lungs, no blood pool, and no tissue-conductivity boundaries (forward_operator_note, L-B6). It is not a bounded torso forward, and it is not treated as one. The pseudo-ECG follows the Gima and Rudy form, in which the extracellular unipolar potential $\phi_e$ at a field point is proportional to $\int (-\nabla V_m)\cdot\nabla(1/r)\,dv$ over active tissue, with $r$ the distance from source to field point and the medium conductivity constant [@gimarudy2002]. The $1/|r|$ term is the infinite-medium Green's function of the volume-conductor problem; the code implements it node-wise (forward_operator_note, L-B6).

The consequence of the unbounded assumption is a known amplitude deficit relative to a bounded (torso or bath) forward. Bishop and Plank name this same pseudo-ECG family (the $\phi_e$ recovery method) as one that assumes bioelectric sources immersed in an unbounded homogeneous volume conductor, and report that it under-estimates whole-ventricular depolarization amplitude by over an order of magnitude versus a bounded reference forward [@bishopplank2011]. That deficit is distance-dependent: it is accentuated with distance from the tissue and is largest at high tissue-to-bath volume ratio, which is exactly the heart-only geometry regime this pipeline sits in [@bishopplank2011] (forward_operator_note, L-B6). Because the deficit differs from lead to lead, it acts as a differential distortion across leads, not as a single uniform gain (forward_operator_note, L-B6).

Two nearby literature quantities are on different axes and are not used as the unbounded-versus-bounded amplitude figure. Monodomain versus bidomain surface potentials differ by an amount reported as very small, with propagation a few percent faster in the bidomain [@potse2006]; this is a source-model axis, not a torso axis. The pseudo-bidomain versus full-bidomain bath-loading differences (trace amplitude up to about 10 mV in repolarization) are a bath-loading effect on the source, again a different axis [@bishopplank2011]. Neither is imported here as the no-torso effect (forward_operator_note, L-B6).

A per-lead comparison of the unbounded pseudo-ECG against a full-torso 12-lead forward, with precordial R and S ratio differences tabulated, is a bounded null: no such published comparison was found at the level needed, so the precordial morphology error the unbounded forward incurs is not pinned to a single published number, while the amplitude effect is (over an order of magnitude, above) (forward_operator_note, L-B6).

Because a heart-only mesh has no body surface for standard resting placement [@kligfield2007], electrode positions are a disclosed modeling choice: fixed field points prescribed from a standard torso atlas registered to the heart mesh, at which the $1/|r|$ weights are computed. They are prescribed from an atlas, not derived from a subject body surface. A canonical published offset table for heart-only precordial placement is a bounded item (the torso-embedded and single-field-point pseudo-ECG practices are established, but no single canonical heart-only offset table was found) (forward_operator_note, L-B6).

## Amplitude

The unbounded homogeneous forward has no absolute calibration: the $1/|r|$ node-wise construction and a chosen scale factor set the millivolt value, so the amplitude is whatever the scale factor makes it and is not fixed by physics the way a 1D fiber with real physical constants would fix it (forward_operator_note, L-B6; ecg_amplitude_scale_defense). We therefore report in arbitrary units scaled to a stated millivolt operating point, and we do not claim absolute calibration.

The operating point is a peak deflection of about 1.4 mV, chosen at the low-normal end of the human amplitude band [@rijnbeek2014] (ecg_amplitude_scale_defense). The anchor is the Sokolow-Lyon upper limit of normal of 3.5 mV on the two-wave precordial sum $S_{V1}+\max(R_{V5},R_{V6})$ [@rijnbeek2014], from which a single largest normal precordial deflection is on the order of 1.5 to 2.5 mV (this per-lead decomposition is bounded: it is consistent with the normal-limits text, but the exact per-lead percentiles live in supplemental tables not string-checked at source) (ecg_amplitude_scale_defense). A peak of 1.4 mV sits at or just below the lower edge of that normal precordial band, so it is a conservative operating point: it does not inflate the signal-to-noise ratio relative to a typical normal ECG (ecg_amplitude_scale_defense).

This is a scaling choice, not a measured calibration. Because the physics does not set the scale, every downstream identifiability result must be invariant to the overall amplitude scale, or the scale must be treated as a nuisance (forward_operator_note, L-B6; ecg_amplitude_scale_defense).

## Parameters, priors, and provenance

The inference target is seven conduction parameters at fixed anatomy. Contract A carried an open decision between six parameters (fixing myocardial conduction velocity) and seven (inferring it); the project settled on seven, inferring `cv_myo` over its literature range, which is the more honest statement of what the ECG constrains (contract_a_PARAMETERS). Parameter order is canonical and fixed, because it defines the column order of the prior, the design matrix, and every posterior artifact (contract_a_PARAMETERS). The prior is an independent uniform box over the seven parameters.

| Parameter | Range | Unit | Primary anchor (see note on citation gaps) |
|---|---|---|---|
| `cv` (Purkinje network CV) | 1.5 to 3.5 | m/s | Control Purkinje-fibre CV about 2.2 m/s [@maguy2009]; textbook 2 to 4 m/s (contract_a_parameter_ranges) |
| `cv_myo` (myocardial longitudinal CV) | 0.5 to 1.0 | m/s | Healthy human LV longitudinal CV 0.56 to 0.95 m/s [@fu2024] (contract_a_parameter_ranges) |
| `delta_IV` (LV to RV interventricular delay) | -25 to +25 | ms | RV endocardial breakthrough 5 to 10 ms after LV onset; box brackets normal to mild block-like asymmetry [@durrer1970] (contract_a_parameter_ranges) |
| `init_length_lv` (LV initial branch length) | 30 to 60 | mm | Nominal 50 mm in an independent fractal-tree study [@tanikella2025]; the LV versus RV split and the range are our modeling choice, not inherited (contract_a_PARAMETERS; contract_a_parameter_ranges) |
| `init_length_rv` (RV initial branch length) | 30 to 60 | mm | Same nominal source [@tanikella2025]; separate RV strand is our modeling choice (contract_a_PARAMETERS; contract_a_parameter_ranges) |
| `branch_angle` (branch angle) | 0.10 to 0.30 | rad | Union of two fractal-tree studies about 0.105 to 0.26 [@sahlicostabal2015; @tanikella2025], rounded outward for prior-boundary safety (contract_a_parameter_ranges) |
| `w` (branch repulsion weight) | 0.05 to 0.20 | dimensionless | Two studies use base 0.10 [@sahlicostabal2015; @tanikella2025]; box widened to about twice the sweep because `w` is expected to be weakly identifiable, to avoid boundary truncation (contract_a_parameter_ranges) |

The ranges are grounded in a lineage independent of the project's own prior-work line: the fractal-tree geometry parameters trace to the original growth method [@sahlicostabal2015] plus an independent third-party sensitivity study [@tanikella2025]; the conduction velocities to experimental electrophysiology [@maguy2009 for Purkinje; @fu2024 for myocardium]; and the interventricular timing to the canonical isolated-human-heart mapping [@durrer1970] (contract_a_parameter_ranges). The `branch_angle` hard constraint is $(0,\pi]$ and `w` must be non-negative; both prior boxes sit safely inside those constraints (contract_a_PARAMETERS).

Conduction velocity enters the eikonal solve through the tissue diffusivity: myocardial CV rescales the eikonal diffusivity via the eikonal relation $\mathrm{CV}\propto\sqrt{D}$ [@keener1991], with anisotropy held near a 2:1 to 3:1 longitudinal-to-transverse ratio [@caldwell2009].

## Observation model (Contract D)

The observation model, labeled Contract D here and sourced from the frozen observation-model contract (contract_b_OBSERVATION_MODEL), defines the likelihood. It must be identical in the training simulator, the baseline comparison, and the calibration harness, or the calibration story would compare different problems (contract_b_OBSERVATION_MODEL).

**Lead redundancy, disclosed.** Noise is applied to all twelve displayed leads, but only eight of them are linearly independent: I, II, V1, V2, V3, V4, V5, V6. The remaining four limb leads are exact linear combinations of I and II under the standard definitions,
$$\mathrm{III}=\mathrm{II}-\mathrm{I},\quad a\mathrm{VR}=-(\mathrm{I}+\mathrm{II})/2,\quad a\mathrm{VL}=\mathrm{I}-\mathrm{II}/2,\quad a\mathrm{VF}=\mathrm{II}-\mathrm{I}/2,$$
with the Wilson central terminal $\mathrm{WCT}=(\mathrm{RA}+\mathrm{LA}+\mathrm{LL})/3$ and each precordial lead $V_i=\phi_i-\mathrm{WCT}$ [@kligfield2007]. The clean 12-lead signal matrix has row rank 8, verified by matrix rank over 50 random electrode configurations (lead_redundancy_note, L-B7S). A waveform Cramer-Rao bound built on a diagonal noise covariance over all twelve leads therefore treats redundant channels as independent and over-counts the Fisher information, making that waveform bound optimistic (too tight); the inflation is finite (bounded, of order the counted-to-independent channel ratio 12 to 8, not a single exact scalar) and the correct treatment restricts the likelihood to the eight independent leads (lead_redundancy_note, L-B7S).

**White where real noise is not.** The additive noise here is white and lead-independent, whereas clinical ECG noise is not: the dominant sources (baseline wander below about 0.5 Hz, powerline interference at 50 or 60 Hz, EMG, motion) are colored and cross-lead correlated, sharing the common Wilson central terminal and the same limb electrodes [@kligfield2007] (ecg_noise_model_note, L-B7S). A white, lead-independent model over-counts independent samples in both the time and lead dimensions, so the waveform Cramer-Rao bound is an optimistic lower bound. The direction of that bias is established; its magnitude is not, because the project does not have the real ECG noise spectrum (ecg_noise_model_note, L-B7S).

**The two channels.** The single $\theta$-sweep produces both engineered features and the full waveform, and each carries its own additive Gaussian noise (contract_b_OBSERVATION_MODEL):

- Feature channel: independent additive Gaussian per feature, with amplitude features at $\sigma = 0.05$ mV and timing or duration features at $\sigma = 5$ ms.
- Waveform channel: white additive Gaussian at $\sigma = 0.025$ mV per sample per lead.

The feature-channel sigmas are anchored to inter-observer measurement-reproducibility limits of agreement (a defensible lower bound on real observation noise); the underlying primary measurement source is a manual-ECG reproducibility study [@qrsense2026] (contract_b_OBSERVATION_MODEL). A fresh noise realization is drawn per training pair, with a separate logged seed, and the same noise model is used everywhere including the calibration observations (contract_b_OBSERVATION_MODEL).

**Why the noise model is mandatory.** The simulator is deterministic given $\theta$ (Section 3.6). Without an explicit observation-noise model the NPE would train on a deterministic map, where the posterior collapses to the forward inverse wherever the map is injective and calibration diagnostics become uninformative. The observation noise is what makes the identifiability question well-posed, so it is required, not optional (contract_b_OBSERVATION_MODEL; contract_a_PARAMETERS).

## Amortized NPE and the engineered feature vector

Inference is amortized Neural Posterior Estimation: a conditional normalizing flow $q_\phi(\theta\mid x)$ is trained by maximizing the average conditional log-probability over simulated pairs, so a single trained flow yields a posterior for any observation without a per-observation inference loop [@papamakarios2016; @greenberg2019] (npe_diagnostics_note). The implementation uses the `sbi` package. The observation $x$ is a vector of engineered ECG features rather than learned summaries, a design choice in the tradition of constructing informative summary statistics for likelihood-free inference [@fearnheadprangle2012; @chen2020].

Each engineered feature is typed by physical unit, and the type sets which feature-channel sigma applies (Section 3.4): amplitude features are millivolt peak or wave voltages (for example an early V1 to V2 R-wave amplitude), and timing features are millisecond durations and interlead delays (feature_classification_note, L-B7F). This class-level typing is fixed by the contract's amplitude-versus-timing split (contract_b_OBSERVATION_MODEL; feature_classification_note, L-B7F). The exact fifteen-item feature vector is not enumerated in any accessible project artifact: it lives in the code's feature-extraction module, and the observation-model contract still lists feature-set membership as an open decision (contract_b_OBSERVATION_MODEL; feature_classification_note, L-B7F). The per-feature type assignment, and therefore the count of features in each class, is bounded pending that list.

\TODO{publish the exact 15-feature vector with per-feature amplitude/timing type from Code's feature-extraction module}

Calibration is a three-stage stack. Simulation-based calibration (SBC) tests whether the posterior rank statistics of prior draws are uniform, which detects miscalibration but does not establish sharpness (a posterior equal to the prior is perfectly SBC-calibrated and maximally diffuse) [@talts2018] (npe_diagnostics_note). Conformal recalibration is then applied to the raw flow output. Expected coverage and the TARP test (accuracy testing with random points, which does not require density evaluation) assess whether credible regions attain their nominal frequentist coverage [@lemos2023]; the motivation is the documented failure mode in which NPE posteriors can be overconfident (unfaithful) [@hermans2021] (npe_diagnostics_note). Calibration is necessary but is not evidence of information extraction: a well-calibrated posterior can still be diffuse, so a calibration pass is never read as full information extraction (npe_diagnostics_note). Simulation-budget sensitivity of the result is assessed by recomputing per-parameter contraction as the training budget is halved, an instance of budget-convergence reporting in SBI benchmarking [@lueckmann2021] (npe_diagnostics_note). The post-conformal TARP number and the contraction-versus-budget curve are reported in the results, not here.

\TODO{post-conformal joint TARP value (the pre-conformal number cannot stand in for it)}
\TODO{contraction-vs-training-budget (N-halving) curve}

## Determinism

The `purkinje-uv` fractal-tree growth code consumes no random number generator: the PCG64 generator present in the configuration is backend and GPU parity infrastructure and is never consumed by growth (contract_a_PARAMETERS; contract_b_OBSERVATION_MODEL). A same-$\theta$-twice run through the growth, eikonal, and 12-lead stages produces a bit-identical ECG, verified bit-identical across 5000 samples (contract_b_OBSERVATION_MODEL). This determinism is precisely why the explicit observation-noise model of Section 3.4 is mandatory: with a deterministic forward map, all stochasticity in the likelihood must be injected externally at the ECG output stage, or the trained flow has no noise to calibrate against (contract_a_PARAMETERS; contract_b_OBSERVATION_MODEL).

# Results

The scientific deliverable of this work is a quantified identifiability
characterization: which of the seven conduction parameters $\theta = \{cv,
cv\_myo, delta\_IV, init\_length\_lv, init\_length\_rv, branch\_angle, w\}$ the
12-lead pseudo-ECG can determine at fixed anatomy, and how well. Throughout,
identifiability is reported as the per-parameter posterior contraction,
$\text{contraction}_k = \text{posterior\_std}_k / \text{prior\_std}_k$, measured
against an explicit observation-noise model, because a deterministic simulator
makes such a noise model mandatory. The feature channel uses amplitude
$\sigma = 0.05$ mV and timing $\sigma = 5$ ms; the waveform channel uses white
Gaussian $\sigma = 0.025$ mV per sample per lead. A contraction near unity means
the marginal posterior is as wide as the prior (diffuse) against that floor; a
small contraction means the ECG narrowed the parameter against that floor. A
posterior correlation between parameters is not by itself a non-identifiability,
and calibration is necessary but is not evidence of information extraction: a
posterior equal to the prior is perfectly calibrated and maximally diffuse.

## The calibrated contraction spectrum, against its noise floor

Against the feature-channel noise floor (amplitude $\sigma = 0.05$ mV, timing
$\sigma = 5$ ms), the prior-averaged contraction spectrum orders the seven
parameters as follows (smaller contraction is more identifiable)
(L-B7F, parameter\_to\_feature\_map):

| Rank | Parameter | Contraction (against the feature floor) | ECG feature it moves |
|---|---|---|---|
| 1 | `delta_IV` | about 0.15 | inter-ventricular timing (relative RV vs LV onset across leads) |
| 2 | `cv_myo` | about 0.35 | total QRS duration |
| 3 | `init_length_rv` | about 0.63 | early QRS forces in V1 to V2 (initial RV / anteroseptal activation) |
| 4 | `cv` | about 0.67 | global QRS timing / activation spread |
| 5 to 7 (tied, diffuse) | `init_length_lv` | about 1.04 (diffuse) | later, LV-mass-dominated bulk of the QRS |
| 5 to 7 (tied, diffuse) | `w` (repulsivity) | about 1.07 (diffuse) | barely moves QRS features; interaction-dominated |
| 5 to 7 (tied, diffuse) | `branch_angle` | about 1.21 (diffuse) | barely moves QRS duration or peak amplitude; interaction-dominated |

The spectrum is defended as reported upstream, not recomputed here. Compactly,
against the feature-channel floor (amplitude $\sigma = 0.05$ mV, timing
$\sigma = 5$ ms):
`delta_IV` about 0.15 > `cv_myo` about 0.35 > `init_length_rv` about 0.63 >
`cv` about 0.67 $\gg$ `branch_angle`, `w`, `init_length_lv` about 1.0 to 1.2
(diffuse) (L-B7F, parameter\_to\_feature\_map).

The ordering tracks a physically meaningful axis rather than an arbitrary choice
of features. `delta_IV` is a pure inter-ventricular timing offset between the
RV-dominated (V1 to V2) and lateral LV leads, the most directly measurable and
least amplitude-confounded quantity in the QRS against the 5 ms timing floor, so
it is the most identifiable (L-B7F, parameter\_to\_feature\_map)
[@gold2018; @gold2017]. `cv_myo` scales total ventricular activation time and
therefore QRS duration, a global scalar measured against the same 5 ms timing
floor, so it contracts well (L-B7F, parameter\_to\_feature\_map)
[@durrer1970; @keener1991]. `cv` also scales global activation timing and therefore
shares that channel with `cv_myo`; their posteriors are correlated and `cv`
contracts less than an independent timing parameter would against the feature
floor (L-B7F, parameter\_to\_feature\_map). We describe this as a shared timing
channel and a posterior correlation, not as a degeneracy: R-02 records that this
project once named a correlated pair degenerate on a reasoned argument and was
wrong. The supporting row L-B3-32 is ASSERTED, so the mechanism is offered as an
explanation, not as evidence. `branch_angle` and `w` move QRS
duration and peak amplitudes only through parameter interactions (low first-order
sensitivity, high total-order sensitivity), so their marginal posteriors stay at
the prior and they are diffuse against the feature-channel floor (amplitude
$\sigma = 0.05$ mV, timing $\sigma = 5$ ms) (L-B7F, parameter\_to\_feature\_map)
[@tanikella2025]. That this posterior contraction ordering agrees with an
independent forward-sensitivity analysis on the same class of fractal-tree model
[@tanikella2025] is evidence the spectrum reflects QRS-genesis physics, not the
estimator's choice of summary features (L-B7F, parameter\_to\_feature\_map).

The `init_length_lv` versus `init_length_rv` split is the most informative
asymmetry: the two parameters are structurally identical in the simulator, yet
against the feature-channel floor (amplitude $\sigma = 0.05$ mV, timing
$\sigma = 5$ ms) only the RV extent contracts (about 0.63) while the LV extent
stays diffuse (about 1.04) (L-B7F, parameter\_to\_feature\_map;
lvrv\_asymmetry\_mechanism). The explanation is QRS genesis, not an estimator
artifact: RV initial Purkinje extent perturbs an early, comparatively isolated
feature (initial forces in V1 to V2 from early RV / anteroseptal breakthrough)
that the ECG constrains, whereas LV initial Purkinje extent perturbs the later,
LV-mass-dominated bulk of the QRS where it is confounded with `cv_myo`, `cv`, and
`delta_IV`, so the ECG does not separately constrain it
(lvrv\_asymmetry\_mechanism). The direction of the asymmetry is grounded in the
normal human activation sequence [@durrer1970]; the exact magnitude (0.63 versus
about 1.0 to 1.2 against the feature floor) is a property of this fixed anatomy
and pseudo-ECG configuration and is stated as such (lvrv\_asymmetry\_mechanism).

One methodological caution attaches to the contraction axis itself: contraction
is not invariant to prior width, because the denominator is the prior standard
deviation, so a change in a prior floor moves contraction with no change in the
likelihood or the signal-to-noise ratio (contraction\_normalization\_note). The
prior-width-invariant companion measure is the Fisher-information-derived
per-parameter Cramer-Rao lower bound plus the FIM eigenspectrum, reported
alongside contraction in Section 4.3 (contraction\_normalization\_note).

## Calibration

Calibration is reported as simulation-based calibration (SBC) [@talts2018] and as
expected-coverage / TARP [@lemos2023; @hermans2021]. Calibration is necessary but
is explicitly distinct from information extraction: a posterior equal to the prior
is perfectly SBC-calibrated and maximally diffuse, so an SBC pass is never read as
"the flow extracts all available information" (npe\_diagnostics\_note).

SBC is summarized by the Kolmogorov-Smirnov (KS) p-values of the rank statistics,
before and after conformal recalibration. These are p-values, not the KS
statistic itself; a reader who reads the statistic in place of the p-value reads
the calibration result backwards. The frozen values are
\TODO{SBC KS p-values pre and post conformal}. The pre-conformal and
post-conformal per-parameter contraction values are
\TODO{pre- and post-conformal contraction}.

For TARP, the sign convention is stated in words: a negative ATC is
underdispersed, that is, overconfident, per the sbi package implementation of the
diagnostic; this is the sbi convention and is not a convention of [@lemos2023],
who do not use the token ATC. On matched calibration sample sets the pre-conformal
TARP ATC is about -0.057 (negative, i.e. mildly underdispersed / overconfident),
describing the raw normalizing-flow posterior before recalibration; R-04 records
that this pre-conformal number cannot be cited as evidence about the calibrated
joint posterior. After per-parameter conformal recalibration the joint TARP ATC is
about +0.007, bringing the recalibrated joint posterior to approximate coverage
(marginally conservative), against the same $\sigma = 0.025$ mV waveform floor.

## Fisher information and the Cramer-Rao lower bound, reported alongside contraction

The Fisher information is reported alongside contraction and is never treated as a
refutation of it. The anchor result is:

At REFERENCE\_THETA the Fisher information matrix is well-conditioned (condition
number 18.3) with per-parameter Cramer-Rao lower bounds above the
observation-noise floor, indicating the ECG is locally informative about all
seven parameters at that point; separately, the prior-averaged posterior
contraction (posterior standard deviation divided by prior standard deviation) is
near unity for `branch_angle` (1.21), `w` (1.07), and `init_length_lv` (1.04)
(L-B6E, fim\_vs\_posterior\_note).

The CRLB is a local, finite-sample bound on the variance of an unbiased estimator
built from the Fisher information at a single point; contraction is a
prior-averaged posterior width; neither bounds the other, and we report both
without treating the tight local CRLB as evidence against the diffuse contraction,
nor the reverse (L-B6E, fim\_vs\_posterior\_note). A well-conditioned FIM at one
point does not certify global identifiability across the prior box: a tight local
CRLB and a diffuse prior-averaged contraction can coexist with no statistical
inconsistency, so the tight FIM at REFERENCE\_THETA does not license a
global-identifiability claim, and this caveat accompanies the diffuse block
(L-B6E, fim\_vs\_posterior\_note).

Whether the diffuse contraction for `branch_angle`, `w`, and `init_length_lv`
reflects genuinely limited information across the prior box (an identifiability
limit) or information that is present but not extracted by the amortized flow at
the training budget $N = 5000$ (an estimator limit) is not determined by the
single-point FIM, and is left open here pending the multi-point FIM across the box
and the budget-convergence check of Section 4.5 (L-B6E, fim\_vs\_posterior\_note).

## Summary-statistic sufficiency

The diffuse block admits a second reading that is testable and must not be
conflated with an ECG information limit: the hand-crafted feature vector may be an
insufficient summary of the waveform for `branch_angle`, `w`, and
`init_length_lv`. For any summary statistic $S$ of the data $X$, the Fisher
information obeys $I_S(\theta) \le I_X(\theta)$ in the positive-semidefinite sense,
with equality if and only if $S$ is sufficient for $\theta$ [@zamir1998;
@coverthomas2006]. Processing the waveform into a feature vector can only destroy
Fisher information, never create it, and the per-parameter gap between the
waveform CRLB and the feature CRLB is exactly the per-parameter Fisher information
lost by summarizing (L-B7M, summary\_statistic\_framing\_note). This is a
CRLB-to-CRLB comparison between the waveform channel (white Gaussian
$\sigma = 0.025$ mV per sample per lead) and the feature channel (amplitude
$\sigma = 0.05$ mV, timing $\sigma = 5$ ms); it is never a comparison of a CRLB to
the posterior contraction (L-B7M, summary\_statistic\_framing\_note). The paired
numbers, at REFERENCE\_THETA and with the waveform restricted to the 8 independent
leads (I, II, V1 to V6; III, aVR, aVL, aVF are exact linear combinations of I and
II, so a 12-lead diagonal noise model would over-count the Fisher information by
roughly 12/8), give a feature CRLB looser than the 8-lead waveform CRLB for every
parameter: about 21x for `init_length_lv`, 33x for `branch_angle`, and 43x for `w`
(the diffuse block), and about 32x, 48x, 64x, 70x for `delta_IV`, `init_length_rv`,
`cv_myo`, `cv` respectively (outputs/crlb\_comparison.json). Restricting from 12 to
8 leads raises the waveform CRLB by only a few percent, so the gap is the Fisher
information lost to the 15-feature summary, not a lead-redundancy artifact. That the
diffuse-block parameters carry order-of-magnitude more local Fisher information in
the waveform than in the feature vector is consistent with the summary-insufficiency
reading, though it is a local statement at one operating point and is not read as
evidence about the prior-averaged contraction (L-B7M, summary\_statistic\_framing\_note).

Under this reading the diffuse block is a candidate summary-statistic
insufficiency, testable by the waveform-versus-feature comparison, not an
established ECG information limit (L-B7M, summary\_statistic\_framing\_note). The
construction of information-preserving summaries is foundational
[@fearnheadprangle2012], and learned neural summaries are the modern route
[@chen2020; @wiqvist2019; @schaelte2023], and the value of moving beyond
hand-crafted summaries in likelihood-free inference is documented directly
[@drovandifrazier2021]; a waveform-trained estimator with a learned embedding
is the corresponding fix if the diffuse parameters are recovered from the full
waveform (L-B7M, summary\_statistic\_framing\_note). A bounded literature search
(three arXiv query framings and one PubMed query, abstracts only, citation-graph
corroboration not performed) found no prior report of an identifiability verdict
flipping between summaries and the raw data, so the work would be a cleanly
demonstrated instance of a known-in-principle phenomenon (information loss under
an insufficient summary), and no discovery of the phenomenon or priority is
claimed (L-B7M, summary\_statistic\_framing\_note).

## Contraction versus training budget $N$

The pre-conformal per-parameter contraction is reported as a function of the
training budget $N$ (the simulation-budget-convergence axis of SBI benchmarking
[@lueckmann2021]) to separate a real information limit from an estimator limit at
$N = 5000$. The curve itself is \TODO{F3 contraction-vs-N curve, landing Friday}.
What it is designed to show, against the feature-channel floor (amplitude
$\sigma = 0.05$ mV, timing $\sigma = 5$ ms): if contraction for the diffuse block
keeps tightening as $N$ grows, the diffuseness at $N = 5000$ is budget-limited
(an estimator effect); if it has plateaued, the diffuseness is not merely a budget
artifact (L-B6E, npe\_diagnostics\_note). Which of the two holds is settled by
this curve together with the multi-point FIM of Section 4.3, and is currently
open; it is not guessed here (L-B6E, fim\_vs\_posterior\_note).

## Parameter recovery against the synthetic target

Parameter recovery is reported against a synthetic target and is a
self-consistency check, not a fidelity result. The regression target True\_ecg is
pickled simulator output used as a fixture, so any transplant correlation of 1.000
is a tautology reflecting operator self-consistency (the same operator forward and
inverse), not agreement with a measurement; there is no measured ECG anywhere in
this project (R-03). Within that self-consistency scope, an individual-recovery
check recovered `cv_myo` at correlation 0.98 from the synthetic target,
establishing that `cv_myo` is individually recoverable rather than constrained
only in combination (R-02). Recovery of the diffuse parameters is not asserted;
the near-null direction of the forward at the checked point is dominated by
`init_length_lv`, consistent with its diffuse contraction against the
feature-channel floor (amplitude $\sigma = 0.05$ mV, timing $\sigma = 5$ ms)
(R-02).

## Method generality

The pipeline ingests a publicly available real four-chamber heart mesh from the
Strocchi cohort (24 meshes, CC-BY-4.0, Zenodo record 3890034, average edge length
about 1.1 mm) [@strocchi2020] (L-B4, strocchi\_torso\_verdict; data\_availability).
Only a single coarse mesh is used. This subsection reports method generality only:
no Strocchi identifiability result is claimed, because none is produced here
(L-B4, strocchi\_torso\_verdict). No published work computes a 12-lead ECG
directly from a Strocchi cohort mesh; the ingestion route follows the method of
the cohort's own group applied to the cohort mesh, and is reported as such, not as
an existing Strocchi-cohort ECG result (L-B4, strocchi\_torso\_verdict). The
released synthetic sweep stores, per sample, both the engineered ECG features and
the full 12-lead waveforms from one deterministic simulation, seeded and
reproducible, which is the reproducibility anchor for the identifiability results
above (data\_availability).

# What we got wrong

This section is the methods contribution in concrete form. The scientific
deliverable is an identifiability characterization; the methods contribution is
the process that produced it, and a central piece of that process is a retraction
ledger that names the project's own wrong claims with stable IDs, dates, and the
internal artifact or line of code that overturned each one. A project that records
its refuted claims this way is demonstrating that its claims are checkable and were
in fact checked. The four rows below are each overturned by an internal project
artifact or a line of project code, not by an appeal to authority or to memory,
and each is recorded as "VERIFIED internally (project artifact/code)", meaning the
evidence was checked in the project's own materials, not that it is a
literature-sourced fact. Section 5 and the demo page paraphrase the same
retraction ledger and must agree.

## R-01 (2026-07-09, REFUTED)

**Claim (withdrawn original wording):** "Forward validated, corr 0.86."
**Killing evidence (internal):** the 0.86 was a best-lag correlation; under a
fixed alignment the per-lead normalized RMSE is about 1, and there is a 2.3x
amplitude gap between the forward output and the target; the single best-lag
correlation masked both (R-01). **Consequence:** a correlation after best-lag
alignment does not support the forward; it discards the timing offset and is
insensitive to a large amplitude mismatch, both of which are present here (R-01).
Verified internally (project artifact/code).

## R-02 (2026-07-09, REFUTED)

**Claim (withdrawn original wording):** "the delta\_IV-cv\_myo ridge is a
degeneracy; the ECG constrains only a combination." **Killing evidence
(internal):** ridge\_confirm recovered `cv_myo` at correlation 0.98, so `cv_myo`
is individually identifiable rather than constrained only as a combination, and
the Jacobian minimum-singular-value direction $v_{\min}$ is dominated by
`init_length_lv`, not by a `delta_IV` / `cv_myo` combination (R-02).
**Consequence:** the near-null direction of the forward is along `init_length_lv`;
naming the `delta_IV` / `cv_myo` pair the degenerate combination pointed at the
wrong parameters (R-02). Verified internally (project artifact/code).

## R-03 (2026-07-09, REFUTED)

**Claim (withdrawn original wording):** "the forward diverges from a real ECG."
**Killing evidence (internal):** True\_ecg is pickled simulator output used as a
regression fixture; there is no measured ECG in the project, so the withdrawn
statement has no referent; the transplant correlation of 1.000 is a tautology,
since the same operator is used forward and inverse (R-03). **Consequence:** the
withdrawn claim was a category error about what True\_ecg is; the perfect
transplant correlation reflects operator self-consistency, not agreement with any
measurement (R-03). Verified internally (project artifact/code).

## R-04 (2026-07-09, REFUTED)

**Claim (withdrawn original wording):** "the joint posterior is near-calibrated
(TARP ATC -0.072)." **Killing evidence (internal):** `src/npe/emit.py` line 226
computes the TARP ATC pre-conformal, so the number describes the posterior before
recalibration, not the calibrated joint posterior (R-04). **Consequence:** the
"near-calibrated" claim was about the wrong object; the reported ATC characterizes
the raw flow output and cannot be cited as evidence that the calibrated
post-conformal joint posterior is near-calibrated (R-04). Verified internally
(project artifact/code).

# Limitations

This section scopes the identifiability characterization honestly. The deliverable is a quantified statement of which conduction parameters the 12-lead ECG constrains at a fixed anatomy, and how well, under a stated observation-noise floor and a stated forward operator. Each limitation below is an explicit boundary on that claim. Where an item is an identifiability statement, its noise floor is named in the same sentence.

**Inverse crime (training and evaluation share the forward operator).** The posterior is trained and evaluated on samples from the same forward operator, so the reported calibration and per-parameter contraction are conditional on that forward being correct, and parameter recovery is a self-consistency check rather than agreement with an independent measurement (L-B5-01). There is no real ECG anywhere in this project: the fixture used as an inversion target is pickled simulator output, so the transplant correlation of 1.000 is operator self-consistency (the same operator serves as forward and inverse), not agreement with a measurement (R-03). No model-mismatch term is present, which can flatter both calibration and identifiability; all coverage and contraction results should therefore be read as in-distribution until a cross-simulator evaluation is run (L-B5-01).

**Single fixed anatomy.** All results use one Strocchi four-chamber mesh (one coarse 1.1 mm heart) [@strocchi2020], and amortization is over conduction parameters at fixed geometry, not over anatomy (L-B5-02). The contraction ordering, degeneracy structure, and per-parameter verdicts are therefore anatomy-specific and are not claimed to generalize across hearts; inter-subject variability in chamber size, orientation, and torso pose is outside the current scope (L-B5-02).

**Unbounded homogeneous pseudo-ECG with arbitrary-unit amplitudes.** The forward is a pseudo-ECG in an infinite, homogeneous, unbounded volume conductor with no torso, lungs, or blood pool, using the node-wise $1/|r|$ route [@gimarudy2002], not a bounded inhomogeneous torso forward (L-B5-03). ECG amplitudes are in arbitrary units scaled to a stated mV operating point [@rijnbeek2014]; no absolute mV calibration of the forward is claimed, and any result that depends on absolute amplitude inherits this scale choice, whereas morphology, timing, and per-lead correlation summaries are robust to it (L-B5-03). The pseudo-ECG under-estimates depolarization amplitude by over an order of magnitude, and the deficit is distance-dependent hence lead-differential [@bishopplank2011]; the monodomain versus bidomain source-model choice is not the concern here, since those surface-potential differences are extremely small [@potse2006], the concern is the volume conductor specifically (L-B5-03).

**Differential lead distortion, and the conclusion most at risk.** Because the amplitude deficit is differential (lead-dependent, accentuated with distance from tissue) rather than a single uniform scale factor, it is not absorbed by peak normalization, so cross-lead amplitude features carry a lead-dependent bias while timing features (read from when a deflection occurs, not how large it is) are robust to a per-lead amplitude gain [@bishopplank2011] (L-B7F-01). Consequently `init_length_rv` is our conclusion most at risk of not transferring to a bounded torso forward, because its moderate identifiability (contraction about 0.63 against the feature-channel noise floor, amplitude sigma 0.05 mV and timing sigma 5 ms) rests on a near-field precordial amplitude feature (the early V1 to V2 R-wave from RV apical breakthrough), whereas `delta_IV` (contraction about 0.15 against the same feature-channel floor, amplitude sigma 0.05 mV and timing sigma 5 ms) and `cv_myo` (contraction about 0.35 against the same feature-channel floor, amplitude sigma 0.05 mV and timing sigma 5 ms) ride interlead delay and QRS duration, which the volume-conductor boundary does not move (L-B7F-01). The sign of the precordial versus limb amplitude bias under a bounded torso is not established; this item asserts only that amplitude-borne conclusions are differentially exposed, not the direction of the bias (L-B7F-02, bounded).

**Twelve-lead noise applied to eight independent leads.** Of the 12 displayed leads only 8 are linearly independent (I, II, V1 to V6); the four remaining limb leads are exact linear combinations of I and II, namely $\mathrm{III}=\mathrm{II}-\mathrm{I}$, $\mathrm{aVR}=-(\mathrm{I}+\mathrm{II})/2$, $\mathrm{aVL}=\mathrm{I}-\mathrm{II}/2$, and $\mathrm{aVF}=\mathrm{II}-\mathrm{I}/2$ [@kligfield2007] (L-B7S-01). The waveform observation model adds white Gaussian noise (sigma 0.025 mV per sample per lead) across all 12 displayed leads and treats them as independent measurement channels, so the Fisher information is over-counted: the clean signal has only 8 lead degrees of freedom per time sample, and a $12\times206=2472$ waveform observation carries at most $8\times206=1648$ linearly independent samples (L-B7S-01). The resulting waveform CRLB (reported against the waveform-channel floor, white Gaussian sigma 0.025 mV per sample per lead) is therefore optimistic at the lead level; the direction of the over-count is exact, the factor is bounded (order $12/8$ in the counted-channel sense, not orders of magnitude), not established, and the corrected 8-lead retrain has not landed (L-B7S-01, bounded).

**White noise where real noise is not.** The waveform CRLB (reported against the waveform-channel floor, white Gaussian sigma 0.025 mV per sample per lead) is an optimistic bound because clinical ECG noise is not white and not lead-independent: baseline wander, powerline interference, and EMG are colored or narrowband and are correlated both across time and across leads (through the shared Wilson central terminal and shared limb electrodes), so a white, lead-independent model over-counts the effective number of independent samples along both axes (L-B7S-02). The direction of this bias is established (the true CRLB is looser, a larger variance floor), its magnitude is not established because the project does not have the real noise spectrum (L-B7S-02, bounded).

**Local Jacobian at one operating point.** Identifiability is characterized with local sensitivity (Jacobian, Fisher information, CRLB, and the FIM eigenspectrum) at operating points, so the FIM and CRLB are local, finite-sample statements: at REFERENCE_THETA the FIM is well-conditioned (condition number 18.3) with per-parameter CRLBs above the observation-noise floor, indicating the ECG is locally informative about all seven parameters at that point (L-B6E). This captures local contraction and degeneracy but does not map global posterior structure; multimodality, disconnected high-likelihood regions, and strongly nonlinear degeneracy away from the operating point are not fully characterized (L-B6E).

**Per-marginal conformal recalibration does not repair a correlated joint.** Coverage is calibrated per parameter, marginally, not jointly across the full 7D posterior, and marginal calibration does not guarantee joint coverage: the 7D credible regions can be miscalibrated even when every 1D marginal is well calibrated, particularly given the correlation and degeneracy structure in theta (L-B5-06). A posterior correlation is not a non-identifiability, and calibration is necessary but is not evidence of information extraction: a posterior equal to the prior is perfectly calibrated and maximally diffuse (L-B5-06). The pre-conformal TARP ATC (about -0.057 on matched sample sets) was computed before recalibration and describes the raw flow output, not the calibrated post-conformal joint posterior, so it alone cannot be cited as joint-calibration evidence (R-04). The post-conformal joint TARP has since landed at about +0.007, bringing the joint to approximate coverage on these sample sets; this is reported as an empirical result, not a guarantee, since per-marginal conformal recalibration carries no general guarantee of joint coverage.

# What would falsify this

The claims that can be refuted are (i) the per-parameter identifiability ordering with its named ECG-feature mechanisms, and (ii) the calibration claim (per-marginal conformal coverage) under the stated forward and noise floor. This section states the falsifiers as predictions, each with its mechanism, what would confirm it, and what would falsify it. Two are new pre-registered directional predictions; the remaining standing falsifiers are carried by reference from the Batch-5 and Batch-6 lists and are not re-derived here.

## Prediction 1: under a bounded torso forward, `init_length_rv` identifiability degrades more than `delta_IV` or `cv_myo`

**Mechanism.** `init_length_rv` rides a near-field precordial amplitude feature (early V1 to V2 R-wave), whereas `delta_IV` and `cv_myo` ride timing features (interlead delay and QRS duration), and a bounded torso forward changes the amplitude map lead-differentially far more than it changes activation timing, because timing is set by the eikonal activation sequence, which the volume-conductor boundary does not move [@bishopplank2011] (L-B7F-01). An amplitude-borne parameter therefore loses information under the forward change while a timing-borne parameter is comparatively protected (L-B7F-01).

**What would confirm it.** Re-running the characterization under a bounded torso forward and observing that the contraction and CRLB of `init_length_rv` (against the feature-channel floor, amplitude sigma 0.05 mV and timing sigma 5 ms) worsen (move toward 1) by a strictly larger factor than those of both `delta_IV` and `cv_myo` at the same floor (L-B7F-01).

**What would falsify it.** Any of: (a) `delta_IV` or `cv_myo` degrades by as much as or more than `init_length_rv` (timing not protected); (b) `init_length_rv` is unchanged or improves (the amplitude channel it rides is not the binding constraint, or the bounded forward adds precordial amplitude information); (c) all three change by an indistinguishable amount (the forward change does not separate amplitude from timing parameters). The prediction concerns the relative degradation of an amplitude-borne versus a timing-borne parameter and does not depend on the sign of the precordial versus limb amplitude bias, which is not established (L-B7F-02, bounded).

## Prediction 2: correlated noise loosens the waveform CRLB and narrows the features-versus-waveform gap

**Mechanism.** The white, lead-independent waveform model (sigma 0.025 mV per sample per lead, independent across all $12\times206=2472$ entries) treats all 2472 numbers as independent measurements, which maximizes the Fisher information the waveform appears to carry (L-B7S-01, L-B7S-02). Under a Gaussian noise model the Fisher information is $J^{\top}\Sigma^{-1}J$, so replacing a diagonal $\Sigma$ with a correlated one of the same marginal variances reduces the effective information along the correlated modes and raises the CRLB; because the white model is what drives the waveform CRLB to a small fraction of the prior range, correcting it removes an optimistic bias that is largest for the waveform (many assumed-independent samples) and comparatively smaller for the low-dimensional feature vector (L-B7S-02).

**What would confirm it.** Recomputing the waveform CRLB under a defensible correlated covariance (for example AR(1) or a measured temporal autocorrelation within a lead, plus an empirical inter-lead correlation) and observing, against the waveform-channel floor (white baseline sigma 0.025 mV per sample per lead), that (1) every waveform per-parameter CRLB loosens relative to the white value, and (2) the ratio of feature CRLB to waveform CRLB shrinks for the diffuse parameters (`branch_angle`, `w`, `init_length_lv`) (L-B7S-02).

**What would falsify it.** Any of: (a) the waveform CRLB is essentially unchanged (the sensitivity directions are orthogonal to the correlated noise modes); (b) the waveform CRLB loosens but the features-versus-waveform gap widens or is unchanged (the feature CRLB loosens by as much or more); (c) the waveform CRLB tightens (which would contradict the information-reducing role of correlation and indicate an error in the covariance construction) (L-B7S-02).

## Standing falsifiers (carried by reference)

The following predate this batch and still stand; they are referenced, not re-derived (L-B5 and L-B6 ledgers).

1. Cross-forward coverage miscalibration: if, on targets generated by a different forward, the per-marginal (or joint) credible intervals miss nominal coverage by a wide margin, the calibration claim does not survive model mismatch and the inverse-crime caveat becomes the headline (L-B5-04).
2. Identifiability ordering not surviving a torso-embedded forward: if a bounded inhomogeneous torso forward materially reorders which parameters are identifiable, the ordering is an artifact of the unbounded homogeneous forward rather than a property of the conduction problem (L-B5-05). Prediction 1 above sharpens this symmetric falsifier into a directional one.
3. The FIM-versus-posterior gap being a real estimator limitation: the current headline reads the diffuse contraction of `branch_angle` (about 1.21), `w` (about 1.07), and `init_length_lv` (about 1.04), all against the feature-channel floor (amplitude sigma 0.05 mV, timing sigma 5 ms), together with a locally well-conditioned FIM (condition number 18.3, CRLBs above the noise floor), as a prior-width effect on contraction plus a genuine near-null direction along `init_length_lv`, not as the estimator failing to reach the information the FIM reports (L-B6E). If a controlled check (a larger training budget than the working N, a different density estimator, or an amortization-gap diagnostic) shows the posterior is systematically wider than the FIM-derived CRLB allows, the gap is a real estimator limitation and part of the reported diffuseness is an estimator shortfall rather than an intrinsic identifiability property; the contraction-versus-N curve is the resolving check and has not landed (L-B6E, \TODO{contraction-versus-N curve resolving the FIM-versus-posterior gap}).

Stating these explicitly is deliberate. The value of the project is a bounded, falsifiable identifiability characterization, and an honest negative on any of the above is a more useful result than an oversold positive.

# Reproducibility and data availability

**Anatomy.** All experiments use the publicly available virtual cohort of four-chamber heart meshes of Strocchi et al., PLoS ONE 2020, DOI 10.1371/journal.pone.0235145, PMID 32589679, archived on Zenodo (record 3890034, DOI 10.5281/zenodo.3890034) under the Creative Commons Attribution 4.0 International (CC-BY-4.0) license [@strocchi2020]. The cohort comprises 24 four-chamber heart meshes, one per heart-failure patient, each archived as a single compressed folder (NN.tar.gz, NN in 01 to 24) containing both a coarse 1.1 mm and a fine 0.39 mm mesh of the same heart; this study uses the coarse 1.1 mm mesh of a single representative heart, so the single-heart selection is reproducible from the Zenodo record by specifying the heart index (L-B5-02, \TODO{exact Strocchi heart index NN used}). No new patient data were generated in this work, and no real patient data are used anywhere in the project; the inversion target is simulator output (R-03).

**License compatibility.** The one third-party dataset in the released pipeline is CC-BY-4.0 (Strocchi), which permits reuse with attribution and is compatible with an Apache-2.0 or MIT code release; attribution is provided as the license requires (L-B5-08). No controlled-access or non-CC-BY dataset enters the release (L-B5-08).

**Reproducibility bundle.** The release is built to regenerate the posteriors, the contraction table, and the calibration diagnostics without re-training, and rests on a deterministic simulator (the fractal-tree growth is deterministic given theta, verified by source inspection: the RNG is defined but consumed in no growth module), so the only stochastic element is the explicit observation-noise model, whose seed is recorded (L-B5-07). The bundle comprises:

1. **Frozen inputs.** The parameter vector theta, its physiological priors with a per-parameter source ledger, the mandatory observation-noise model (feature channel: amplitude sigma 0.05 mV, timing sigma 5 ms; waveform channel: white Gaussian sigma 0.025 mV per sample per lead), and the seed, all recorded in the repository (L-B5-07).
2. **Simulation sweep.** A single seeded sweep storing, per sample, both the engineered ECG features and the full 12-lead waveforms, with a held-out test split, so the paired features-versus-waveform comparison costs training time, not simulation time, and both observation models regenerate exactly from the same stored data (L-B5-07, \TODO{released sweep dataset location and DOI}).
3. **Trained weights.** The NPE checkpoint(s) released alongside the inference code so the posteriors regenerate without re-training (L-B5-07, \TODO{released NPE checkpoint location and DOI}).
4. **Container.** A container pinning the software stack (purkinje-uv for the fractal-tree Purkinje generation and FIM eikonal solver, sbi for NPE, SBC, expected coverage, and TARP) so the environment is reproducible (L-B5-07, \TODO{released container image reference and digest}).
5. **Calibration artifacts.** The SBC ranks, expected-coverage and TARP outputs, and the seeds used, released so the calibration claim is independently checkable (L-B5-07, \TODO{released post-conformal calibration artifacts, including the joint-posterior TARP not yet landed}).

**Method generality note.** Any cross-anatomy identifiability result across the full Strocchi cohort is future work and is not part of this release; the fixed-anatomy design is a deliberate scoping choice, and cohort-level identifiability is stated as method generality only, not as a landed result (L-B5-02).

# References {-}

::: {#refs}
:::

# Appendix A: The verification ledger {-}

This appendix is the checkable record behind every factual claim in the manuscript. Each row carries a stable ID, the claim, the source that was checked, and the result (VERIFIED, BOUNDED, ASSERTED, or VERIFIED internally). The identifiability rows name their noise floor where relevant. Rows are grouped by batch (B1 through B7); the four retractions R-01 to R-04 follow. This appendix is on the never-cut list.

## A.1 Batch 1 (parameter and noise-floor sourcing)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B1-01 | QRSense paper (PMID 42176693) resolves; J Electrocardiol 2026; doi 10.1016/j.jelectrocard.2026.154368 | PubMed metadata (this session) | VERIFIED |
| L-B1-02 | Bland-Altman: voltage LoA -0.0958..+0.1922 mV (bias +0.0482); duration LoA -16.24..+13.59 ms (bias -1.32); Lin CCC 0.9527/0.9221 | PubMed abstract (verbatim) | VERIFIED |
| L-B1-03 | LoA->sigma: sigma_single=(hi-lo)/(2*1.96*sqrt(2)) -> 0.052 mV / 5.38 ms; rounded 0.05 mV / 5 ms | in-kernel recomputation | VERIFIED (arithmetic reproduced) |
| L-B1-04 | QRSense first author is 'Corrales' | PubMed author block | REFUTED - first author is Santiago Obregon-Rosas; no 'Corrales' present. Corrected in all files. |
| L-B1-05 | Tanikella 2025 gives LV/RV init_length ~50mm each over range 30-60 | arXiv:2505.16696 Table 1 + sec 2.3 | PARTLY REFUTED - init length FIXED at 50mm (not swept), LV network only; 30-60 range & LV/RV split are our modeling choices. |
| L-B1-06 | Tanikella Sobol: alpha and w both simply low-sensitivity/flat | arXiv:2505.16696 results | REFINED - S1 small but ST~1 (interaction-dominated); w flagged interaction-heavy. Prediction updated to weak-marginal + degeneracy. |

## A.2 Batch 2 (datasets, forward setup, conduction modelling)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B2-01 | MedalCare-XL = Sci Data 2023, PMID 37553349, DOI 10.1038/s41597-023-02416-4, arXiv:2211.15997 | PubMed metadata + arXiv record | VERIFIED |
| L-B2-02 | MedalCare-XL on Zenodo record 8068944 (DOI 10.5281/zenodo.8068944), CC-BY-4.0, ~9.3 GB | Zenodo API (this session) | VERIFIED at source |
| L-B2-03 | MedalCare-XL = 12-lead ECG CSV, rows I,II,III,aVR,aVL,aVF,V1-V6, 500 Hz, mV; raw/noise/filtered; splits by anatomy | PMC full text PMC10409805, Data Records | VERIFIED (verbatim) |
| L-B2-04 | MedalCare-XL forward model = reaction-Eikonal, monodomain, no diffusion; source-to-electrode transfer operators precomputed once per model | PMC full text PMC10409805 | VERIFIED (verbatim) |
| L-B2-05 | MedalCare-XL ECG record ships signals, not per-sample meshes | PMC full text (Data Records) | VERIFIED (bounded: meshes live in the separate Gillette cohort framework, not the ECG record) |
| L-B2-06 | EDGAR = J Electrocardiol 2015, PMID 26320369, DOI 10.1016/j.jelectrocard.2015.08.008 | PubMed metadata | VERIFIED |
| L-B2-07 | EDGAR live, open-access, free registration required, Utah SCI/CIBC host, ecg-imaging.org | live repository page + PMC full text PMC4624576 | VERIFIED at source |
| L-B2-08 | EDGAR content = BSPM + epicardial/transmural potentials + torso/heart geometry; MATLAB-readable + ASCII/PDF metadata | PMC full text PMC4624576 | VERIFIED |
| L-B2-09 | EDGAR 2015 paper copyright = Elsevier all-rights-reserved (paper, not data) | PubMed copyright status PMID 26320369 | VERIFIED; data reuse terms are per-dataset at registration, NOT asserted as CC-BY |
| L-B2-10 | MyoFit46 = CMR sub-study of NSHD 1946 birth cohort, ~500 participants ~77 y, stress-perfusion + LGE | PubMed abstracts PMID 41404671, 41796595 | VERIFIED |
| L-B2-11 | MyoFit46 controlled-access CMR imaging, no ECG/Purkinje ground truth | PubMed abstracts | VERIFIED as controlled-access imaging cohort; exact access-portal URL NOT confirmed (bounded) |
| L-B2-12 | Strocchi four-chamber cohort = Zenodo 3890034, CC-BY-4.0, 24 .gz files, 22.5 GB | Zenodo API (this session) | VERIFIED at source |
| L-B2-13 | Kligfield 2007 (PMID 17322457, Circulation, DOI 10.1161/CIRCULATIONAHA.106.180200) reviews standard 12-lead lead placement/recording | PubMed metadata + abstract | VERIFIED |
| L-B2-14 | Gima & Rudy 2002 (PMID 11988490, Circ Res, DOI 10.1161/01.res.0000016960.61087.86) computes ECG waveforms from cellular/transmembrane activity | PubMed metadata + abstract | VERIFIED |
| L-B2-15 | Potse 2006 (PMID 17153199, IEEE TBME) shows monodomain vs bidomain surface-potential differences are very small | PubMed abstract | VERIFIED (justifies monodomain/eikonal + lead-field forward operator) |
| L-B2-16 | Geodesic-BP (2308.08410) matches eikonal ECGs to clinical ECGs; Zappon (2407.17146) quantifies sim-vs-measured gap | verified prior session (related-work.md) | reused |
| L-B2-17 | Standard V1-V6 intercostal-space positions | Kligfield 2007 standardization statement | ASSERTED as standard clinical convention, sourced to Kligfield rather than re-derived; Strocchi ships NO electrode file (this is why the disclosure exists) |
| L-B2-18 | Keener 1991 (PMID 1940663, J Math Biol, DOI 10.1007/BF00163916) derives the cardiac eikonal-curvature equation | PubMed metadata + abstract | VERIFIED (framework) |
| L-B2-19 | Colli Franzone 1990 (PMID 2319210) reduces the bidomain wavefront to eikonal equations via singular perturbation | PubMed metadata + abstract | VERIFIED |
| L-B2-20 | Colli Franzone 2004 (PMID 14766102, DOI 10.1016/j.mbs.2003.09.005) applies eikonal approximation, studies conductivity-tensor effects | PubMed metadata + abstract | VERIFIED |
| L-B2-21 | CV proportional to sqrt(D) scalar relation (the cv_myo rescale) | eikonal framework above + monodomain traveling-wave theory (textbook) | ASSERTED as the standard derived consequence, NOT a verified abstract sentence; honestly flagged |
| L-B2-22 | Myocardium orthotropic, fastest along fiber; fiber:transverse CV ratio ~2.2:1 (Caldwell 2009, PMID 19808500) | verified prior session; abstract qualitative, m/s values body/tables | reused; ratio number from body/tables not this-session abstract |
| L-B2-23 | Roberts & Scher 1982 (PMID 7060230) = potential-field anisotropy, not a CV ratio | verified prior session | reused for anisotropy-matters, not for the CV ratio number |
| L-B2-24 | Costa FIMH-2013 explicit D-scaling recipe | attempted PubMed | NOT retrieved (not PubMed-indexed); sqrt(D) grounded in eikonal framework + traveling-wave theory instead (bounded) |
| L-B2-25 | Gold 2017 (PMID 29195547) interventricular delay vs HF outcomes; Gold 2018 (PMID 30354310) delay and CRT response | verified prior session | reused |
| L-B2-26 | LBBP-RESYNC (Wang 2022, PMID 36137670) LVEF diff 5.6% (95% CI 0.3-10.9, P=0.039) | verified prior session | reused (verbatim) |
| L-B2-27 | Hermans 2021 (2110.06581), Talts SBC (1804.06788), Lemos TARP (2302.03026), CANVI (2305.14275) | verified prior session | reused |
| L-B2-28 | Alvarez-Barrientos 2025 (2312.09887), Grandits 2024 (2411.00165) = uncalibrated BO+ABC / ensemble | verified prior session | reused |
| L-B2-29 | No cardiac-conduction SBI paper reports SBC/coverage/TARP | targeted arXiv+PubMed searches | BOUNDED negative ("none found"), NOT proof of nonexistence; OpenAlex unavailable |

## A.3 Batch 3 (noise floor, amplitude scale, LV/RV mechanism)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B3-01 | In the linear-Gaussian limit, per-parameter EIG_k = -log(contraction_k) exactly, so expected information gain inherits the same prior-width dependence as contraction | in-kernel reproduction over 4 (prior_sd, noise_sd, n) settings: EIG (entropy reduction) matched -log(posterior_sd/prior_sd) to float precision in every case | VERIFIED (reproduced), elevating the track's ASSERTED derivation |
| L-B3-02 | sigma_CRLB = noise_sd / sqrt(n) is invariant to prior width while contraction is not | in-kernel: widening prior_sd 1.0 to 10.0 at fixed likelihood left sigma_CRLB unchanged (0.289) while contraction fell 0.277 to 0.029 | VERIFIED (reproduced): confirms the FIM/CRLB recommendation is the genuinely prior-invariant axis |
| L-B3-03 | QRSense first author is Obregon-Rosas not Corrales | PubMed author block PMID 42176693 | VERIFIED |
| L-B3-04 | QRS voltage 95% LoA -0.0958 to +0.1922 mV, bias +0.0482 | QRSense abstract | VERIFIED at abstract level |
| L-B3-05 | QRS duration 95% LoA -16.24 to +13.59 ms, bias -1.32 | QRSense abstract | VERIFIED at abstract level |
| L-B3-06 | SD_diff voltage 0.0735 mV -> sigma_single 0.052 -> 0.05 mV | in-kernel arithmetic | VERIFIED (reproduced) |
| L-B3-07 | SD_diff duration 7.61 ms -> sigma_single 5.38 -> 5 ms | in-kernel arithmetic | VERIFIED (reproduced) |
| L-B3-08 | Waveform-sample floor 0.025 mV = half amplitude SD | in-kernel arithmetic 0.052/2=0.026 | VERIFIED (reproduced) |
| L-B3-09 | Clinical resting is a measurement-reproducibility floor not raw SNR | QRSense inter-observer design | VERIFIED (interpretation) |
| L-B3-10 | Diagnostic bandwidth 0.05 to 150 Hz adult clinical ECG | Kligfield 2007 PMID 17322457 | VERIFIED prior batch (full text closed here) |
| L-B3-11 | Research/SAECG floor ~0.005-0.01 mV (few microV RMS) | Breithardt 1991 PMID 2065682/2013173 | BOUNDED (method/regime abstract-confirmed, microV threshold body/convention) |
| L-B3-12 | Ambulatory sigma 0.10-0.20 mV worst case | MIT-BIH NSTDB Moody/Muldrow/Mark 1984 | BOUNDED (descriptive paradigm, not PubMed-indexed mV measurement) |
| L-B3-13 | Recommended sweep interval sigma in [0.025, 0.10] mV | synthesis of regimes | ASSERTED (design recommendation) |
| L-B3-14 | peak-SNR table at 1.4 mV peak (28 at sigma 0.05) | in-kernel arithmetic peak/sigma | VERIFIED (reproduced) |
| L-B3-15 | Rijnbeek 2014 is a per-lead normal-limits ECG amplitude reference | green-OA PDF read, PMID 25194872 | VERIFIED (full text) |
| L-B3-16 | Sokolow-Lyon ULN 3.5 mV = SV1+max(RV5,RV6) | Rijnbeek 2014 PDF main text + Table 3 | VERIFIED (string-checked) |
| L-B3-17 | Cornell voltage ULN 2.8 mV men / 2.0 mV women | Rijnbeek 2014 PDF main text + Table 3 | VERIFIED (string-checked) |
| L-B3-18 | P-wave ULN 0.25 mV; deflection-present floor >= 0.025 mV | Rijnbeek 2014 PDF main text | VERIFIED (string-checked) |
| L-B3-19 | Each contributing precordial wave ~1.5-2.0 mV; single largest deflection ~1.5-2.5 mV | decomposition of verified 3.5 mV sum + Rijnbeek R/S text | BOUNDED (per-lead percentiles in Supplemental Tables 6/7, not string-checked) |
| L-B3-20 | Wu 2003 (5360 subjects) reports per-lead 2nd/98th-percentile amplitudes | abstract PMID 12468053 | BOUNDED (body tables paywalled) |
| L-B3-21 | Katibi 2013 automated per-lead normal ranges | abstract PMID 23702151 | BOUNDED (body tables paywalled) |
| L-B3-22 | ~1.4 mV peak sits at low-normal edge and understates SNR vs typical normal peak | comparison 1.4 vs 1.5-2.5 mV band + in-kernel SNR | VERIFIED as inequality + reproduced |
| L-B3-23 | Verdict: 1.4 mV defensible/low-normal/SNR-conservative, optional 2.0 mV re-run | synthesis | ASSERTED (design recommendation) |
| L-B3-24 | Durrer 1970 = Circulation 41(6):899-912, PMID 5482907, DOI 10.1161/01.cir.41.6.899, authors Durrer/van Dam/Freud/Janse/Meijler/Arzbaecher | PubMed get_article_metadata author block | VERIFIED at metadata level |
| L-B3-25 | Durrer 1970 body activation-timing specifics (early septal L-to-R, early anterior RV breakthrough, posterobasal LV last, ~80 ms total) | attempted full text; 1970 paper not in PMC | BOUNDED (canonical attribution; metadata verified, body not string-checked) |
| L-B3-26 | Modeling uses 1 mm fast-conducting endocardial layer in LV and RV; endocardial breakthrough = earliest-activation landmark | PMC8025079 full text string-checked | VERIFIED (secondary/methodological confirmation) |
| L-B3-27 | LV myocardial mass dominates the QRS mean vector (basis of LVH voltage criteria) | searched; candidate PMID 38151605 checked and REJECTED (neonatal, low LV-mass/QRS correlation) | BOUNDED (textbook vectorcardiography; no string-checked primary sentence this batch) |
| L-B3-28 | Gold 2018 PMID 30354310 = interventricular electrical delay as measurable ECG quantity modulating CRT timing | PubMed get_article_metadata title/journal/abstract | VERIFIED at metadata/abstract level |
| L-B3-29 | Gold 2017 PMID 29195547 = interventricular conduction delay predicts CRT response | PubMed get_article_metadata | VERIFIED at metadata/abstract level |
| L-B3-30 | Tanikella 2025 arXiv:2505.16696: QRS durations/peak amplitudes low sensitivity to individual HPS params; timing variability driven by branch/fascicle-angle and repulsivity interactions | arXiv API abstract string-checked (title, author block, 2025-05-22) | VERIFIED at abstract level |
| L-B3-31 | Keener 1991 PMID 1940663 eikonal CV controls activation time | reused verified anchor, not re-fetched | ASSERTED (prior-verified anchor) |
| L-B3-32 | cv and cv_myo share a global activation-timing channel, offered as an explanation for cv's weaker contraction | reasoned shared-channel argument | ASSERTED (mechanism expectation, not an independent posterior-correlation measurement; not a degeneracy claim, see R-02) |
| L-B3-33 | LV/RV mechanism verdict: partly holds (directionally sound; LV-dominance limb bounded) | synthesis | ASSERTED (reasoned verdict) |
| L-B3-34 | Contraction magnitude (0.63 vs 1.0-1.2) may be anatomy/lead-geometry dependent (single coarse mesh, fixed electrode geometry) | reasoned from fixed-anatomy design | BOUNDED (alternative not excluded) |
| L-B3-35 | QRSense sigma anchor (QRS voltage ~0.05 mV, QRS duration ~5 ms, sigma_single=SD_diff/sqrt(2)) | Obregon-Rosas et al. J Electrocardiol 2026 PMID 42176693 | VERIFIED (prior batch, reused) |
| L-B3-36 | SBI overconfidence motivating calibration audit | Hermans et al. arXiv:2110.06581 | VERIFIED (prior batch, reused) |
| L-B3-37 | SBC posterior-calibration diagnostic | Talts et al. arXiv:1804.06788 | VERIFIED (prior batch, reused) |
| L-B3-38 | Expected coverage / TARP | Lemos et al. arXiv:2302.03026 | VERIFIED (prior batch, reused) |
| L-B3-39 | Strocchi 2020 four-chamber meshes, Zenodo 3890034, CC-BY-4.0 | project dataset record | VERIFIED (prior batch, reused) |
| L-B3-40 | EIG = expected KL prior-to-posterior; foundational OED measure | Lindley 1956 Ann. Math. Statist. 27(4):986-1005 DOI 10.1214/aoms/1177728069 | ASSERTED, NOT verified at source. Well-known standard reference; citation identifiers and definitional content stated from background knowledge; article body NOT opened or read within this project |
| L-B3-41 | EIG standard Bayesian-OED utility; computational-algorithm review | Ryan, Drovandi, McGree, Pettitt 2016 Int. Stat. Rev. 84(1):128-154 DOI 10.1111/insr.12107 | ASSERTED, NOT verified at source. Standard OED review reference; citation identifiers stated from background knowledge; article body NOT opened or read within this project |
| L-B3-42 | Sloppy/stiff FIM eigenspectrum is a prior-free likelihood property | Gutenkunst et al. 2007 PLoS Comput Biol 3(10):e189 PMID 17922568 DOI 10.1371/journal.pcbi.0030189 | VERIFIED at source this batch (PubMed metadata + abstract) |
| L-B3-43 | Profile likelihood separates structural vs practical identifiability | Raue et al. 2009 Bioinformatics 25(15):1923-1929 PMID 19505944 DOI 10.1093/bioinformatics/btp358 | VERIFIED at source this batch (PubMed metadata + title) |
| L-B3-44 | Gaussian-limit per-parameter EIG_k = -log(contraction_k), so EIG inherits prior-width dependence | derived from linear-Gaussian EIG=0.5 log(prior_var/post_var) | ASSERTED (standard derivation, uncited) |
| L-B3-45 | Fisher information I=J^T Sigma^-1 J contains no prior, so sigma_CRLB is prior-width invariant | definitional (Cramer-Rao / Gauss-Newton FIM) | ASSERTED (definitional) |
| L-B3-46 | Inverse crime inflates accuracy but cannot manufacture a flat marginal or degeneracy ridge | inverse-problem reasoning | ASSERTED (methodological argument) |
| L-B3-47 | MedalCare-XL / reaction-Eikonal monodomain as distinct forward map for OOD check | named as planned validation | ASSERTED (planned; forward-map difference is the argument, not a measured result) |

## A.4 Batch 4 (Strocchi cohort, torso, cross-geometry)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B4-01 | Cohort ships no torso/body-surface/electrode mesh | Zenodo 3890034 24-label element list | VERIFIED (all cardiac) |
| L-B4-02 | Cohort paper = PLoS ONE 2020 not Med Image Anal | PubMed metadata PMID 32589679 + author block | VERIFIED (corrects prior note) |
| L-B4-03 | Cohort paper ran activation+mechanics, no ECG | PLoS ONE abstract string-checked | VERIFIED |
| L-B4-04 | Reference-torso lead-field 12-lead ECG from heart mesh | Gillette 2022 Front Physiol full text (Sec 2.2.5, 2.4) | VERIFIED (MRI mesh, not cohort mesh) |
| L-B4-05 | 12-lead ECG simulated from reference torso at scale | Qian 2023 medRxiv full text | VERIFIED (CMR mesh, not cohort mesh; Strocchi co-author) |
| L-B4-06 | Reaction-eikonal + lead-field ECG engine | Neic 2017 J Comput Phys PMID 28819329 metadata | VERIFIED metadata; body BOUNDED |
| L-B4-07 | Fixed-field-point pseudo-ECG, no torso | Gima-Rudy 2002 PMID 11988490 (prior batch) | VERIFIED defensible no-torso route |
| L-B4-08 | MedalCare-XL is a different torso-bearing cohort | Gillette-cohort description | VERIFIED NOT direct Strocchi precedent |
| L-B4-09 | Strocchi cohort CRT/CSP papers report activation times not ECG | Abstracts PMID 32603781/36738149/40394990 | VERIFIED |
| L-B4-10 | Linear tetrahedral volume mesh | PLoS ONE abstract string-checked | VERIFIED |
| L-B4-11 | Units mm | Zenodo record | VERIFIED |
| L-B4-12 | World-coordinate origin/common frame | Zenodo record | NOT STATED |
| L-B4-13 | Tag 1 = LV myo, tag 2 = RV myo (24 cardiac tags) | Zenodo record label list | VERIFIED |
| L-B4-14 | No native endo/septum element tag; endo via transmural UVC=0 | Zenodo record | VERIFIED (UVC-derived, not native tag) |
| L-B4-15 | Fibres ship 80(endo) to -60(epi) deg; sheets ship | Zenodo record + PLoS ONE abstract | VERIFIED |
| L-B4-16 | Fibre/sheet field names in CASE files | Zenodo record | NOT STATED (confirm on load) |
| L-B4-17 | LV transverse diastolic dim M 50.2 (42.0-58.4)/F 45.0 (37.8-52.2) mm | Lang 2015 PDF table string-checked | VERIFIED |
| L-B4-18 | RV basal 33 (25-41), RV longitudinal 71 (59-83) mm | Lang 2015 Table 8 string-checked | VERIFIED |
| L-B4-19 | [30,60] mm init_length physiological | comparison vs Lang chamber dims | VERIFIED plausible bound |
| L-B4-20 | No published 12-lead ECG from a Strocchi Zenodo cohort mesh | absence across checked cohort-using papers | BOUNDED null |
| L-B4-21 | contraction=posterior_std/prior_std NOT prior-invariant; prior-invariant axis is FIM/CRLB | Batch 3 finding 6 (in-kernel, reused) | VERIFIED |
| L-B4-22 | FIM scales 1/noise_var so cross-geometry CRLB needs identical fixed noise model | FIM definition | ASSERTED (definitional) |
| L-B4-23 | Strocchi meshes ship node UVCs (apico-basal 0 apex to 1 base) usable as chamber length scale | Zenodo 3890034 (reused) | VERIFIED (reused) |
| L-B4-24 | delta_IV/cv/cv_myo/branch_angle/w anatomy-independent; init_length_lv/rv scale with heart size | dimensional reasoning | ASSERTED (definitional) |
| L-B4-25 | Cohort paper = Strocchi et al., PLoS ONE 2020, DOI 10.1371/journal.pone.0235145, PMID 32589679, PMCID PMC7319311, 16 authors | PubMed record author block this session | VERIFIED (correction: brief said Med Image Anal) |
| L-B4-26 | PLoS ONE vol 15 / issue 6 / article e0235145 | PubMed record citation field {volume 15, issue 6, pages e0235145}, read this session | VERIFIED (audit fix: was mislabeled ASSERTED) |
| L-B4-27 | Zenodo 3890034, DOI 10.5281/zenodo.3890034, CC-BY-4.0, 24 NN.tar.gz each with 1.1mm+0.39mm mesh | Zenodo API (reused) | VERIFIED (reused) |
| L-B4-28 | Caldwell 2009 CV ~0.67/0.30/0.17 m/s, fibre:transverse ~2.2:1, PMID 19808500; crtdemo cv_myo 0.866 m/s | reused prior batch | VERIFIED (reused) |
| L-B4-29 | 0.866 m/s high side of Caldwell fibre but within broad ~0.6 to 1.0 m/s adult range | comparison to anchor + general range | ASSERTED (bounded) |
| L-B4-30 | SBI benchmark: sequential estimation improves sample efficiency, metric choice critical, no uniformly best algorithm | arXiv:2101.04653 abstract+authors this session | VERIFIED (abstract level) |
| L-B4-31 | No clean primary single-number N rule for 7D NPE | literature search this session; OpenAlex unavailable | BOUNDED NULL |
| L-B4-32 | Ordering claims robust at smaller N than calibrated contraction; verify via N-halving + CRLB agreement + coverage/SBC | reasoning | ASSERTED (reasoned, bounded) |

## A.5 Batch 5 (forward operator, residual diagnosis, limitations)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B5-01 | We report a coverage/calibration statistic we call ATC = -0.072 and describe it as 'mildly conservative', citing Lemos 2023 (arXiv:2302.03026, TARP) | Lemos 2023 arXiv abstract + PDF body (full text, string-checked: ATC-search, 'conservative'-search, over/underconfident case definitions, expected-coverage curve framing) | BOUNDED / LABEL-CORRECTION. String-checked in the paper: the token 'ATC' appears NOWHERE (the 4 apparent hits are substrings Match/batch/matching) and the word 'conservative' appears ZERO times. TARP = Tests of Accuracy with Random Points; the paper's reported quantity is the expected coverage probability ECP(p-hat, alpha) plotted vs credibility level 1-alpha, accurate iff ECP = 1-alpha (the diagonal, string-checked Sec on Fig 2). Paper's string-checked case definitions (Sec 4.1 / App B): drawing truths from N(theta*, 0.5 Sigma) makes the posterior too NARROW = OVERconfident; N(theta*, 2 Sigma) makes it too WIDE = UNDERconfident; for underconfident estimators the TARP coverage tends to ~0.5, for overconfident it tends to 0 or 1. STANDARD coverage convention (not a TARP-specific string in this paper): an under-confident / over-dispersed posterior OVER-covers (ECP above the diagonal) and is the 'conservative' case; an over-confident posterior UNDER-covers (below diagonal) and is 'anti-conservative'. VERDICT: 'ATC = -0.072' and 'mildly conservative' are OUR labels, NOT defined in Lemos 2023; the paper provides no signed scalar named ATC and no sign->conservative map, so the SIGN of -0.072 cannot be adjudicated from the paper. It resolves only against our own (here un-inspected) ATC formula and the code that produced -0.072. Keep BOUNDED until that formula is string-checked; do not assert 'conservative' as a Lemos-sourced fact. |
| L-B5-02 | Rijnbeek 2014 (PMID 25194872) per-lead R-wave and S-wave amplitude percentiles, Supplemental Tables 6 and 7 (previously BOUNDED, not string-checked) | Elsevier supplement mmc1.doc (PII S0022073614002969), Supplemental Tables 6 (R-wave) and 7 (S-wave), string-checked in-kernel from the .doc WordDocument stream | VERIFIED (string-checked at source). Both tables give median (98th percentile) amplitude in mV per lead x sex x 8 age groups (16-19..80-89). R-wave (Table 6) precordial peaks (Male, 16-19): V4 1.79 (3.93), V5 1.89 (2.97), V6 1.32 (2.37); limb II 1.39 (2.24). S-wave (Table 7) peaks (Male, 16-19): V2 2.01 (3.54), V1 1.01 (2.47), V3 1.27 (2.77). This CONFIRMS the prior BOUNDED inference: single-lead peak deflections reach ~1.5 to 2.5 mV (98th percentiles up to 3.93 mV in V4), corroborating the decomposition of the verified Sokolow-Lyon ULN of 3.5 mV. The ~1.4 mV modeled peak sits at the low-normal edge (SNR-conservative), as previously stated. |

## A.6 Batch 6 (FIM vs posterior, differential distortion, retractions)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B6E-01 | Unbiased CRLB cov >= I(theta)^-1 is a finite-sample bound; MLE attains it only asymptotically | Kay Vol.I Ch.3; Lehmann-Casella Ch.2 (not string-checked this session) | TEXTBOOK-STANDARD, confirmed; corrected the claim's misplaced 'asymptotically' |
| L-B6E-02 | A biased estimator (posterior mean, shrinkage, ridge, James-Stein) can have variance below the unbiased CRLB | Kay Vol.I Ch.3; Lehmann-Casella Ch.5 (not string-checked) | TEXTBOOK-STANDARD, confirmed |
| L-B6E-03 | van Trees/Bayesian CRB bounds Bayesian MSE by inverse of J=J_D+J_P; prior adds a PSD information term | Van Trees Part I; Gill-Levit 1995 Bernoulli 1(1/2):59-79 (citation asserted, not string-checked) | TEXTBOOK-STANDARD, confirmed |
| L-B6E-04 | A lower bound is not attainment: posterior_std can sit far above the CRLB for inefficient/budget-limited estimators | Definition of a statistical lower bound (Kay, Van Trees) | TEXTBOOK-STANDARD, confirmed |
| L-B6E-05 | Contraction=posterior_std/prior_std is not prior-width invariant; prior-invariant axis is FIM-CRLB plus FIM eigenspectrum | Batch 3 finding 6, verified in-kernel in a prior batch | VERIFIED (prior batch, in-kernel) |
| L-B6E-06 | Local FIM at one point cannot certify global identifiability across the prior box | Logical consequence of pointwise FIM curvature | ASSERTED (logical, not empirical) |
| L-B6E-07 | NPE trains a conditional density estimator to approximate the posterior directly | arXiv:1605.06376 abstract + author block (Papamakarios, Murray) | VERIFIED |
| L-B6E-08 | APT/SNPE-C is the amortized NPE variant the validation log-prob monitors | arXiv:1905.07488 abstract + author block (Greenberg, Nonnenmacher, Macke) | VERIFIED |
| L-B6E-09 | Loss-curve saturation is the optimization-convergence check | Standard ERM training practice, sbi workflow | ASSERTED (no single primary paper) |
| L-B6E-10 | SBI performance is benchmarked as a function of simulation budget | arXiv:2101.04653 abstract + author block (Lueckmann, Boelts, Greenberg, Goncalves) | VERIFIED |
| L-B6E-11 | Contraction-vs-N (N-halving) is an instance of budget-convergence reporting | Project application of 2101.04653 practice | ASSERTED (project instance) |
| L-B6E-12 | Posterior-predictive checks test data-space consistency of the posterior | Standard Bayesian workflow (Gelman et al.), adopted in sbi | ASSERTED (not string-checked to an SBI primary) |
| L-B6E-13 | SBC tests calibration via rank uniformity; a prior-equal posterior is SBC-calibrated and maximally diffuse | arXiv:1804.06788 abstract + author block (Talts, Betancourt, Simpson, Vehtari) | VERIFIED (paper); prior-equal corollary ASSERTED (definitional) |
| L-B6E-14 | TARP is a coverage test for general posterior estimators not requiring density evaluation | arXiv:2302.03026 abstract + author block (Lemos, Coogan, Hezaveh) | VERIFIED |
| L-B6E-15 | SBI algorithms including NPE can produce overconfident (unfaithful) posteriors | arXiv:2110.06581 abstract + author block (Hermans, Delaunoy, Rozet) | VERIFIED |
| L-B6E-16 | Calibration (SBC, coverage) is necessary but distinct from information extraction | Logical consequence of the definitions | ASSERTED (definitional) |
| L-B6D-01 | Unbounded pseudo-ECG uses phi_e = (1/4 pi sigma_b) integral (beta I_m / \|r\|) dOmega, tissue in an unbounded medium | Bishop and Plank 2011, PMID 21536529, full text eq. 11 (string checked) | VERIFIED at full text; matches our forward (Batch 5 code) |
| L-B6D-02 | Recovery-vs-bounded amplitude deficit is distance-dependent ('accentuated with distance from the tissue'), hence NOT a uniform scale | Bishop and Plank 2011, full text Results (Fig. 5 discussion, string checked) | VERIFIED at full text |
| L-B6D-03 | The over-an-order-of-magnitude deficit is the small-bath ex-vivo regime, NOT a verified in-vivo torso number | Bishop and Plank 2011, full text (Figs. 5 and 6, Discussion, string checked) | VERIFIED as ex-vivo small-bath; in-vivo torso magnitude declared 'remains to be determined' by the authors |
| L-B6D-04 | grad(1/r) is a proximity-weighting operator: near electrode reads local sources, remote electrode reads whole heart, so leads sample the source differently | Gima and Rudy 2002, PMID 11988490, full text (Batch 5, string checked) | VERIFIED at full text |
| L-B6D-05 | Brief's a-priori claim that distortion is precordial-concentrated (near-field deviates most) | Bishop and Plank 2011 distance-dependence passage | REVERSED / not supported: measured deficit grows with distance (limb-ward) in the small-bath slab; torso direction declared open. Flagged. |
| L-B6D-06 | ECG amplitude most sensitive to blood, skeletal muscle, heart, fat, lung conductivity; fat affects morphology | Keller 2010, PMID 20659824, abstract (prior batches) | VERIFIED at abstract; per-tissue not per-lead, does not pin the precordial-vs-limb differential |
| L-B6D-07 | A clean published per-lead uniform-vs-differential decomposition for the unbounded-vs-bounded-torso comparison | PubMed search (this batch); narrow query returned only Bishop-Plank 2011 | BOUNDED NULL: no such published decomposition found |
| L-B6D-08 | Per-lead numerical distortion factors for our specific forward pair | (none) | BOUNDED: not pinned by any published number |
| L-B6D-09 | Sign of the precordial-vs-limb ordering for our geometry | Bishop-Plank (limb-ward, small bath) vs a-priori near-field (precordial-ward); torso open | BOUNDED: direction not established |
| L-B6R-01 | R-01: 'Forward validated, corr 0.86' is refuted by per-lead nRMSE about 1 and a 2.3x amplitude gap behind a best-lag correlation | project artifacts (forward-validation diagnostics), internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-02 | R-02: delta_iv-cv_myo degeneracy claim is refuted by ridge_confirm (cv_myo corr 0.98) and the Jacobian (v_min dominated by init_length_lv) | project artifacts (ridge_confirm, Jacobian/FIM), internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-03 | R-03: 'forward diverges from a real ECG' is refuted by the fixture (True_ecg is pickled simulator output; transplant corr 1.000 is a tautology) | project fixture and forward/inverse operator, internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-04 | R-04: TARP ATC -0.072 'near-calibrated' claim is refuted because src/npe/emit.py:226 computes it PRE-CONFORMAL | project code src/npe/emit.py line 226, internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-05 | This retraction ledger is part of the methods contribution (checkable, dated, artifact-backed claims) | framing statement about project process | ASSERTED (framing, internally consistent with the four rows above) |
| L-B6R-06 | Batch-5 falsification section, original wording and item list | limitations_and_falsification.md version 9a7bb6bc, read in full this batch | VERIFIED internally (project artifact), read directly |
| L-B6R-07 | TARP ATC sign is a code question (sbi.diagnostics.check_tarp), deferred, not re-sourced here | scoping decision, not yet run | ASSERTED (deferred to a code check; not a literature claim) |
| L-B6R-08 | FIM at REFERENCE_THETA: condition number 18.3, tight CRLBs, nothing sub-noise | given upstream compute result, internal | VERIFIED internally (upstream compute result), reused as given |
| L-B6R-09 | Falsification outcomes (cross-simulator coverage, ordering under torso, CRLB under alternative noise, multimodality, P0-1 estimator gap) | forward reasoning from the current framing | ASSERTED (falsifiable predictions, not yet run) |

## A.7 Batch 7 (lead redundancy, noise whiteness, feature classes, summary statistics)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B7S-01 | Kligfield 2007 is the AHA/ACC/HRS Part I ECG standardization statement; reviews lead placement, recording methods, waveform presentation | PubMed metadata + abstract, PMID 17322457, Circulation, DOI 10.1161/CIRCULATIONAHA.106.180200 | VERIFIED at abstract/metadata |
| L-B7S-02 | III = II - I (Einthoven's law) | Standard definition, checked by exact algebra in-kernel (np.isclose True) | VERIFIED (by computation) |
| L-B7S-03 | aVR = -(I+II)/2, aVL = I - II/2, aVF = II - I/2 | Standard Goldberger definitions, verified by exact algebra in-kernel (all np.isclose True) | ASSERTED (standard), VERIFIED-by-computation |
| L-B7S-04 | WCT = (RA+LA+LL)/3, V_i = phi_i - WCT | Standard Wilson central terminal definition | ASSERTED (standard) |
| L-B7S-05 | Of 12 leads exactly 8 are linearly independent (I, II, V1..V6); rank of 12-lead signal matrix is 8 | In-kernel matrix rank over 50 random electrode configs (rank 8; 8-lead subset also rank 8) | VERIFIED (by computation) |
| L-B7S-06 | 12 x 206 = 2472 observation carries at most 8 x 206 = 1648 independent samples | Arithmetic from rank-8 lead structure | VERIFIED (by computation) |
| L-B7S-07 | Diagonal Sigma_n over 12 leads inflates the FIM and makes the waveform CRLB optimistic | FIM algebra J = G^T Sigma_n^-1 G with rank-8 G lead structure vs full-rank diagonal Sigma_n | VERIFIED (analytic), inflation factor BOUNDED not exact |
| L-B7S-08 | Redundancy is exact on clean signal but finite (not infinite) under per-displayed-lead white noise (contract B) | Rank argument on signal vs noise covariance; contract B adds noise per displayed lead | VERIFIED (analytic) |
| L-B7S-09 | Redundancy is an information error for the waveform CRLB but only a modeling choice for the feature CRLB | Likelihood mis-specification (diagonal over 12) vs redundant feature selection | VERIFIED (analytic) |
| L-B7S-10 | ECG noise sources are EMG, 60 Hz powerline, baseline drift (respiration), baseline shift, composite | Friesen 1990 abstract, PMID 2303275, IEEE TBME, DOI 10.1109/10.43620 | VERIFIED at abstract |
| L-B7S-11 | These are distinct colored/narrowband processes, treated separately (not a single white process) | Friesen 1990 abstract (five synthesized noise types) | VERIFIED at abstract |
| L-B7S-12 | Baseline wander below ~0.5 Hz; powerline narrowband 50/60 Hz; EMG broadband colored | ECG signal-processing standard (Sornmo and Laguna 2005); AHA bandwidth context in Kligfield 2007 abstract | ASSERTED (standard); Kligfield covers recording/DSP VERIFIED at abstract, numeric cutoffs NOT string-checked |
| L-B7S-13 | Narrowband/low-frequency noise has long temporal autocorrelation; ECG noise is not white | Spectral/autocorrelation reasoning from the sourced taxonomy | VERIFIED (analytic) from sourced taxonomy |
| L-B7S-14 | Precordial leads share the WCT = (RA+LA+LL)/3, so their noise is cross-lead correlated | WCT construction from P0-1 (verified lead definitions) | VERIFIED (analytic) from P0-1 |
| L-B7S-15 | Limb leads share RA/LA/LL electrodes, so limb-lead noise is cross-lead correlated | Lead construction from P0-1 | VERIFIED (analytic) from P0-1 |
| L-B7S-16 | N_eff = N(1-rho)/(1+rho) [AR(1)]; N_eff = N/(2 tau_int); N_eff = (sum lambda)^2 / sum lambda^2 [participation ratio] | Standard effective-sample-size / autocorrelation-time results | ASSERTED (standard), given as BOUNDED direction (no number) |
| L-B7S-17 | White + lead-independent overstates information; true CRLB is looser (larger variance floor) | Fisher information over-counting under correlated noise | VERIFIED (analytic), magnitude BOUNDED not established |
| L-B7F-01 | Contract B splits engineered features into amplitude (mV, sigma 0.05 mV) and timing/duration (ms, sigma 5 ms) types | contract_b_OBSERVATION_MODEL.md section 1a (read this batch, version_id 8da74a92-3bb2-491a-9e66-2c2e233ada83) | VERIFIED at artifact |
| L-B7F-02 | Feature set membership (exact 15 features and per-feature type) is an OPEN decision needing Code's list | contract_b_OBSERVATION_MODEL.md section 4 item 1 (read this batch) | VERIFIED at artifact; exact 15-to-class mapping BOUNDED |
| L-B7F-03 | delta_IV rides interlead/interventricular timing; cv_myo rides QRS duration; init_length_rv rides early V1 to V2 R amplitude; cv rides global QRS timing; branch_angle and w are interaction-dominated | parameter_to_feature_map.md map table and per-parameter account (read this batch, version_id a58b7ebb-e52a-4ddb-a536-cc177bf0073e) | VERIFIED at artifact |
| L-B7F-04 | Unbounded 1/\|r\| pseudo-ECG amplitude deficit is DIFFERENTIAL (lead-dependent, distance-accentuated), so peak normalization does not absorb it and cross-lead amplitude features carry a lead-dependent bias | Batch-6 differential_distortion_note.md (version_id 0e341fa2-1ba5-48bd-b868-df0157b2524a); Bishop and Plank 2011 PMID 21536529 verified full text prior batch | VERIFIED at artifact / reused verified anchor |
| L-B7F-05 | A per-lead multiplicative amplitude gain does not move a zero-crossing time, onset, offset, duration, or interlead delay | Reasoned from definition of timing features (time coordinate invariant under voltage scaling) | ASSERTED (elementary invariance argument) |
| L-B7F-06 | init_length_rv identifiability (~0.63) rests on a near-field precordial AMPLITUDE feature and is the conclusion most at risk of not transferring to a bounded forward | Synthesis: parameter_to_feature_map.md plus Batch-6 differential distortion plus Bishop and Plank 2011 distance-accentuation | ASSERTED (reasoned, anchored on two verified artifacts and one verified primary source) |
| L-B7F-07 | SIGN of the precordial-versus-limb amplitude distortion ordering under a bounded torso forward | Batch-6 note leaves it open (near-field vs small-bath measurement disagree; torso case open) | BOUNDED (direction not established) |
| L-B7F-08 | Count of the 15 engineered features falling in each class | Not enumerated in either artifact | BOUNDED (needs Code's list) |
| L-B7M-01 | Field consensus: summaries reduce dimensionality incurring information loss; full-data approaches avoid it | Drovandi and Frazier 2021, arXiv:2103.02407, abstract | VERIFIED at abstract |
| L-B7M-02 | Fearnhead and Prangle 2012, JRSS-B 74(3):419 to 474, DOI 10.1111/j.1467-9868.2011.01010.x, authors Paul Fearnhead and Dennis Prangle | Crossref + arXiv:1004.1112 author block | VERIFIED at metadata + author block |
| L-B7M-03 | Semi-automatic ABC: optimal summary under quadratic loss is the posterior mean, estimated via a regression stage | arXiv:1004.1112 abstract | VERIFIED at abstract |
| L-B7M-04 | Fisher-information data-processing inequality I_S(theta) <= I_X(theta), equality iff S sufficient | Cover and Thomas (standard); Fisher-matrix form Zamir 1998 | VERIFIED as standard statement; Zamir metadata verified |
| L-B7M-05 | Zamir 1998, proof of Fisher information inequality via data processing, IEEE TIT 44(3):1246 to 1250 | Crossref DOI 10.1109/18.669301 | VERIFIED at metadata |
| L-B7M-06 | Raw-FIM-vs-summary-FIM is the Fisher-information form of the sufficiency test; gap is Fisher information loss = ratio of per-parameter CRLBs | Derived from DPI + sufficiency + CRLB = inverse FIM | VERIFIED as naming/derivation from verified anchors |
| L-B7M-07 | Chen et al. 2020 frames summary construction as mutual-information maximisation (approx sufficiency) | arXiv:2010.10079 abstract + author block | VERIFIED at abstract |
| L-B7M-08 | Wiqvist et al. 2019, PENs for learning ABC summaries, ICML PMLR 97:6798 to 6807 | arXiv:1901.10230 journal_ref + abstract | VERIFIED at metadata + abstract |
| L-B7M-09 | Cranmer, Brehmer, Louppe 2020, frontier of SBI, PNAS DOI 10.1073/pnas.1912789117 | arXiv:1911.01429 DOI + abstract | VERIFIED at metadata + abstract |
| L-B7M-10 | sbi trains an embedding network on the raw observation (learned automatic summary) | standard sbi practice, not re-fetched at a primary methods paper | ASSERTED (supported by Chen 2020 and Wiqvist 2019 primaries) |
| L-B7M-11 | Schaelte and Hasenauer 2023, PMID 37216372, PLoS ONE, DOI 10.1371/journal.pone.0285836, two authors (Yannik Schaelte, Jan Hasenauer); summaries can cause information loss | PubMed metadata (authors/journal/year/DOI) + abstract | VERIFIED at metadata + abstract |
| L-B7M-12 | No prior report of an identifiability VERDICT flip between summaries and raw data | arXiv 3 framings + PubMed 1 query, abstracts only, OpenAlex unavailable | BOUNDED (NULL): none found in this bounded search |
| L-B7M-13 | init_length_rv rides amplitude feature; delta_IV and cv_myo ride timing features | feature_classification_note.md (P0-3), internal | VERIFIED internally |
| L-B7M-14 | Unbounded pseudo-ECG under-estimates amplitude, deficit distance-dependent hence lead-differential | Bishop and Plank 2011, PMID 21536529, full text (prior batch) | VERIFIED at full text (reused) |
| L-B7M-15 | Amplitude deficit is differential not uniform, not absorbed by peak normalization | differential_distortion_note.md (Batch-6 P0-3), version 0e341fa2 | VERIFIED internally |
| L-B7M-16 | Gaussian-noise FIM is J^T Sigma^-1 J; correlated Sigma reduces effective information vs diagonal with same marginals | standard linear-Gaussian information formula | VERIFIED as standard statement |
| L-B7M-17 | Prediction 1 outcome (init_length_rv degrades more than delta_IV/cv_myo under bounded forward) | forward reasoning; bounded-forward run NOT executed | ASSERTED (pre-registered prediction, not yet tested) |
| L-B7M-18 | Prediction 2 outcome (correlated noise loosens waveform CRLB and narrows the gap) | forward reasoning; correlated-noise recomputation NOT executed | ASSERTED (pre-registered prediction, not yet tested) |

## A.8 Retractions

| ID | Date | Original claim (withdrawn wording) | Killing evidence (internal) | Result |
|---|---|---|---|---|
| R-01 | 2026-07-09 | "Forward validated, corr 0.86." | The 0.86 was a best-lag correlation; under a fixed alignment the per-lead normalized RMSE is about 1 and there is a 2.3x amplitude gap; the single best-lag correlation masked both. | REFUTED, VERIFIED internally (project artifact/code) |
| R-02 | 2026-07-09 | "The delta_IV-cv_myo ridge is a degeneracy; the ECG constrains only a combination." | ridge_confirm recovered cv_myo at corr 0.98 (individually identifiable), and the Jacobian minimum-singular-value direction v_min is dominated by init_length_lv. | REFUTED, VERIFIED internally (project artifact/code) |
| R-03 | 2026-07-09 | "The forward diverges from a real ECG." | True_ecg is pickled simulator output used as a regression fixture; there is no measured ECG in the project, so the withdrawn statement has no referent; the transplant correlation of 1.000 is a tautology (same operator forward and inverse). | REFUTED, VERIFIED internally (project artifact/code) |
| R-04 | 2026-07-09 | "The joint posterior is near-calibrated (TARP ATC -0.072)." | src/npe/emit.py line 226 computes the TARP ATC pre-conformal, so the number describes the raw flow output, not the calibrated post-conformal joint posterior. | REFUTED, VERIFIED internally (project artifact/code) |
