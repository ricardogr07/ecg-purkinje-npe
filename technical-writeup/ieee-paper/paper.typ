// Self-contained IEEE two-column template (no external packages; registry is unreachable here).
// Cowork-owned Zenodo manuscript. Source of truth: docs/results-summary.md and the release artifacts.

#set document(
  title: "Which conduction parameters can an electrocardiogram determine? A calibrated identifiability characterization of the His-Purkinje system",
  author: "Ricardo Garcia Ramirez",
)
#set page(paper: "us-letter", margin: (x: 0.62in, y: 0.72in))
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true, leading: 0.55em)

// IEEE-style headings: level 1 centered small-caps roman; level 2 italic letter.
#set heading(numbering: "I.A.1.")
#show heading.where(level: 1): it => block(width: 100%, above: 10pt, below: 5pt)[
  #set align(center)
  #set text(size: 10pt, weight: "bold")
  #smallcaps[#it]
]
#show heading.where(level: 2): it => block(above: 6pt, below: 3pt)[
  #set text(size: 10pt, style: "italic", weight: "regular")
  #it
]
#show figure.caption: set text(size: 8pt)

// ---------- Title block (full width) ----------
#align(center)[
  #text(size: 17pt, weight: "bold")[
    Which conduction parameters can an electrocardiogram determine?
  ]
  #v(2pt)
  #text(size: 13pt, weight: "bold")[
    A calibrated identifiability characterization of the His-Purkinje system
  ]
  #v(10pt)
  #text(size: 12pt)[Ricardo García Ramírez]
  #v(8pt)
]

// ---------- Two-column body ----------
#columns(2, gutter: 16pt)[

#text(weight: "bold")[Abstract]: Conduction models are routinely fit to the
electrocardiogram (ECG) and their parameter values reported, but the prior
question of which conduction parameters an ECG can determine at all is rarely
asked, and a model can fit while its reported number carries no information. We
characterize the identifiability of seven His-Purkinje and myocardial conduction
parameters from the 12-lead ECG at fixed anatomy, using a single amortized neural
posterior estimator with a formal calibration audit (simulation-based calibration,
expected coverage, and TARP). Against an explicit observation-noise floor
(waveform noise, white Gaussian $sigma = 0.025$ mV per sample per lead, applied
before feature extraction), the prior-averaged posterior contraction orders the
parameters as interventricular delay (about 0.15) and myocardial velocity (about
0.35) well constrained, RV initial Purkinje extent moderately constrained (about
0.63), and LV extent, branch angle, and branch repulsivity diffuse (about 1.0 to
1.2). Per-parameter conformal recalibration moves the joint posterior from
overconfident (TARP ATC $-0.057$) to essentially calibrated ($+0.007$) without
disturbing that ordering. The forward is a pseudo-ECG in an unbounded homogeneous
volume conductor with arbitrary-unit amplitudes, not a torso model; there is no
measured ECG in the study, and the noise model is white where real ECG noise is
not, so the waveform bound is optimistic in a stated direction of unestablished
magnitude. Identifiability statements are conditional on that floor and that
forward.

#v(3pt)
#text(weight: "bold")[Index Terms]: Simulation-based inference, neural posterior
estimation, identifiability, calibration, His-Purkinje system, electrocardiogram,
cardiac digital twin.

= Introduction

The His-Purkinje conduction system sets the sequence in which the two ventricles
activate: an insulated network of fast-conducting fibers carries the activation
wavefront from the atrioventricular node to a distributed set of terminal
junctions on the endocardium, and the resulting breakthrough pattern shapes the
whole of ventricular depolarization @durrer1970. This network cannot be observed
directly in a living patient without an invasive study, so the routine
noninvasive window onto ventricular activation is the surface ECG, a far-field,
spatially integrating measurement @gimarudy2002. The clinical stakes are
concrete: interventricular electrical delay is a measurable predictor of who
benefits from cardiac resynchronization therapy @gold2017 @gold2018. A conduction
parameter recoverable from the ECG would therefore be one that could inform
therapy.

This has motivated a line of work that fits a conduction model to a measured or
simulated ECG and reports estimated parameter values. Grandits et al. build a
cardiac digital twin from the surface ECG and infer properties of the ventricular
conduction system @grandits2024; a related line learns a fractal Purkinje network
from the ECG with Bayesian optimization plus approximate Bayesian computation
@alvarezbarrientos2025. Both return conduction parameters. Neither first asks the
question that logically precedes any reported value: given this ECG and this
forward model, which conduction parameters can the ECG determine at all, and how
well.

That question is not rhetorical, because the ECG-to-conduction map is
non-injective. Grandits et al. demonstrate that distinct activation maps can
generate identical surface ECGs @grandits2024, which means a fitting procedure can
converge, report a tight-looking value, and have that value be a consequence of
the optimizer or the prior rather than a quantity the data constrain. A model can
fit and its reported number still carry no information. Reporting a point
estimate, or an ensemble spread, without a calibration audit does not distinguish
an identified parameter from an unconstrained one.

This work addresses that gap. We deliver a quantified identifiability
characterization of seven conduction parameters at fixed anatomy. The primary
quantity is a per-parameter #emph[contraction], defined as the posterior standard
deviation divided by the prior standard deviation and reported against the
waveform noise floor under which the estimator is trained. The characterization is
produced by a single amortized neural posterior estimator (NPE), a normalizing
flow trained once over the parameter space at fixed geometry
@papamakarios2016 @greenberg2019, and its reliability is then tested with formal
calibration diagnostics. The contribution is a measurement of the identifiability
structure, not a new inference method and not a claim about how closely the
forward reproduces any measurement.

The calibration step is load-bearing precisely because it is easy to over-read. A
calibration diagnostic checks whether the posterior's stated uncertainty is
self-consistent; it is necessary before any contraction is interpreted, but it is
not itself evidence that the ECG carries information about a parameter, because a
posterior equal to the prior is perfectly calibrated and maximally diffuse
@talts2018 @hermans2021 @lemos2023. We therefore report contraction against the
stated floor and audit calibration separately, and we read a near-prior posterior
as a weakly constrained parameter under that floor, not as an estimator failure.

= Methods

== Forward model and simulator

The forward map is deterministic given the conduction parameters $theta$. A
fractal Purkinje tree is grown on the endocardium and its activation computed with a
fast iterative eikonal method; the resulting activation-time field drives a
12-lead pseudo-ECG computed as an unbounded homogeneous volume-conductor recovery
of the extracellular potential @gimarudy2002. Working at the activation-time level
rather than a full ionic solve is what makes a large parameter sweep tractable,
and monodomain-to-surface recovery is defensible because the monodomain and
bidomain surface potentials differ very little @potse2006 @keener1991. The full
pipeline is shown in #ref(<fig:pipeline>). The fixed endocardial geometry and a
representative grown fractal Purkinje network are shown in #ref(<fig:geom>).

#place(top, scope: "parent", float: true)[
  #figure(
    image("figures/fig6_crtdemo_purkinje.png", width: 100%),
    caption: [The crtdemo endocardial geometry (light point cloud) with a
    representative grown fractal Purkinje network, LV in red and RV in blue, from
    two viewpoints. The identifiability characterization fixes this anatomy and
    infers only the conduction parameters.],
  ) <fig:geom>
]


Two properties of this forward matter for the interpretation. First, it is
deterministic in $theta$; there is no simulator noise, so an explicit observation
noise model is mandatory or calibration is meaningless. Second, the unbounded
homogeneous recovery has no absolute amplitude calibration and is known to
under-estimate depolarization amplitude by over an order of magnitude relative to
a bounded torso forward, a deficit that is distance-dependent and therefore acts
as a differential distortion across leads rather than a single uniform gain
@bishopplank2011. Amplitudes are reported in arbitrary units scaled to a stated mV
operating point.

#place(top, scope: "parent", float: true)[
  #figure(
    image("figures/fig5_pipeline.png", width: 100%),
    caption: [The identifiability pipeline. Conduction parameters $theta$ generate
    a fractal Purkinje tree and eikonal activation, then a 12-lead pseudo-ECG;
    engineered features and the full waveform, each under an explicit noise floor,
    are the observation for a single amortized NPE whose posterior is summarized as
    a contraction spectrum and audited by SBC, expected coverage, and TARP.],
  ) <fig:pipeline>
]

== Parameters, priors, and noise floor

The inference target is the seven-dimensional vector $theta$ with components
#raw("cv") (conduction velocity), #raw("delta_iv") (LV-RV interventricular delay),
#raw("init_length_lv") and #raw("init_length_rv") (LV and RV initial Purkinje
extent), #raw("branch_angle"), #raw("w") (branch repulsivity), and #raw("cv_myo")
(myocardial conduction velocity). The prior is an
independent uniform box over physiological ranges. Parameter order is canonical
and fixes the column order of every posterior artifact.

Because the forward is deterministic, the observation noise is stated explicitly.
The contraction spectrum is measured under a waveform noise floor: white Gaussian
$sigma = 0.025$ mV per sample per lead, added to the 12-lead ECG before feature
extraction. A separate feature-channel model (amplitude $sigma = 0.05$ mV, timing
$sigma = 5$ ms) is used only as the reference noise for the feature Cramer-Rao
bound in the sufficiency analysis (Section IV-C); it is not the floor under which
the spectrum is measured. The noise is white where real ECG noise is colored, so
the resulting bound is optimistic in a stated direction.

== Inference and calibration

A single normalizing-flow NPE is trained once over $theta$ at fixed geometry
(#raw("cardiac_demo")) from a seeded sweep of 5000 simulations that stores, per
sample, both the engineered feature vector and the full 12-lead waveform, so the
paired feature-versus-waveform comparison costs training time, not simulation
time. The primary quantity is the per-parameter contraction, posterior standard
deviation over prior standard deviation; values near or above one indicate a
posterior no tighter than the prior.

Calibration is a three-stage stack. Simulation-based calibration (SBC) tests
whether posterior rank statistics of prior draws are uniform @talts2018.
Per-parameter conformal recalibration is then applied to the raw flow output.
Expected coverage and the TARP test assess whether credible regions attain their
nominal frequentist coverage @lemos2023, motivated by the documented failure mode
in which NPE posteriors can be overconfident @hermans2021. In the sbi sign
convention a negative TARP ATC denotes an underdispersed (overconfident)
posterior and a value near zero denotes calibration. Simulation-budget
sensitivity is assessed by recomputing contraction as the training budget is
varied @lueckmann2021.

= Results

== The calibrated identifiability spectrum

Against the waveform noise floor the per-parameter contraction orders cleanly
(#ref(<fig:spectrum>)): interventricular delay (#raw("delta_iv"), about 0.15) and
myocardial velocity (#raw("cv_myo"), about 0.35) are well constrained; RV initial
Purkinje extent (#raw("init_length_rv"), about 0.63) and global conduction
velocity (#raw("cv"), about 0.67) are moderately constrained; and LV initial
extent (#raw("init_length_lv")), branch repulsivity (#raw("w")), and branch angle
(#raw("branch_angle")) are diffuse, at about 1.0 to 1.2. Contraction at or above
one for the diffuse block is not a defect: it is honest calibration revealing that
the posterior for those parameters is no tighter than the prior.

#figure(
  image("figures/fig1_contraction_spectrum.png", width: 100%),
  caption: [Calibrated identifiability spectrum. Per-parameter contraction
  (posterior std / prior std) before and after conformal recalibration, sorted by
  the post-conformal value. Green marks identifiable parameters, red the diffuse
  block; the dashed line at one is the prior (no information). Measured against the
  waveform noise floor, $sigma = 0.025$ mV per sample per lead.],
) <fig:spectrum>

The ordering has a mechanistic reading. Interventricular delay drives interlead
timing and myocardial velocity drives QRS duration, both robust high-signal
features; RV extent rides an early, comparatively isolated precordial feature
(early V1-V2 forces from RV apical breakthrough); the diffuse trio barely moves
the QRS and is interaction-dominated, matching an independent forward Sobol
analysis @tanikella2025. The full joint posterior (#ref(<fig:corner>)) makes the
same point directly: the marginals for interventricular delay and myocardial
velocity are tight around the ground truth, while branch angle, branch
repulsivity, and LV extent stay broad, and the mild delta_iv to cv_myo tilt is a
ridge, not a degeneracy.

#place(top, scope: "parent", float: true)[
  #figure(
    image("figures/fig7_posterior_corner.png", width: 82%),
    caption: [Joint posterior over the seven conduction parameters at a
    representative operating point (filled contours at 50 and 90 percent; red lines
    mark the ground truth). Tight marginals (interventricular delay, myocardial
    velocity) indicate identifiable parameters; broad marginals (branch angle,
    branch repulsivity, LV extent) the diffuse block.],
  ) <fig:corner>
]

== Calibration

The calibration audit is shown in #ref(<fig:calib>). Before recalibration the
empirical coverage sits below nominal (overconfident); after per-parameter
conformal recalibration it tracks the diagonal, and the joint TARP ATC moves from
$-0.057$ (overconfident) to $+0.007$ (essentially calibrated, marginally
conservative), with SBC KS median about 0.15. Calibration is necessary but not
sufficient for information: it certifies that the diffuse parameters are honestly
diffuse, not that the ECG constrains them.

#place(top, scope: "parent", float: true)[
  #figure(
    image("figures/fig_calib_wide.png", width: 100%),
    caption: [Calibration audit. (a) Expected coverage: before conformal
    recalibration the empirical coverage falls below nominal (overconfident); after
    recalibration it tracks the ideal diagonal. (b) SBC uniformity KS p-value per
    parameter, before and after. The joint TARP ATC moves from $-0.057$
    (overconfident) to $+0.007$ (calibrated).],
  ) <fig:calib>
]

== Budget sensitivity and summary-statistic sufficiency

Two readings of the diffuse block are separable, and #ref(<fig:budgetcrlb>) tests
both. Panel (a) recomputes contraction as the training budget grows from 1000 to
4000 draws over three seeds: four parameters (#raw("cv"), #raw("delta_iv"),
#raw("init_length_lv"), #raw("init_length_rv")) tighten with budget, a
budget-limited rather than information-limited regime at this scale, while the
remaining three are flat or widen within seed noise. This is a two-point trend,
not a converged curve.

The second reading is that the hand-crafted feature vector is an insufficient
summary of the waveform. For any summary statistic $S$ of the data $X$, the Fisher
information obeys $I_S (theta) <= I_X (theta)$, with equality iff $S$ is sufficient
@zamir1998 @coverthomas2006; summarizing can only destroy information. Panel (b)
reports the per-parameter ratio of the feature Cramer-Rao bound to the eight-lead
waveform bound, from about 21x to 70x across parameters. The gap is real but
roughly common-mode across the spectrum, so it is a candidate summary-statistic
insufficiency, testable by a waveform-trained estimator with a learned embedding,
not an established ECG information limit.

#place(top, scope: "parent", float: true)[
  #figure(
    image("figures/fig_bc_wide.png", width: 100%),
    caption: [Diffuse-block diagnostics. (a) Contraction versus training budget $N$
    (post-conformal median over three seeds): green parameters tighten as budget
    grows, red parameters are flat or widen within seed noise. (b) Fisher
    information lost to feature compression, the per-parameter ratio of the feature
    Cramer-Rao bound to the eight-lead waveform bound; values above one mean the
    feature summary is less informative than the full waveform.],
  ) <fig:budgetcrlb>
]

= Discussion

== What the spectrum is, and is not

The result is a statement about a forward map relative to a stated noise floor,
measured on a calibrated posterior. Identifiability here is not a property of a
parameter in the abstract: it is the property of #emph[this] forward at #emph[this]
floor. The sharpened contribution is exactly that framing. Contraction without a
stated floor and without a calibration audit is uninterpretable, which is why a
fit that converges is not evidence of identifiability.

The calibration audit is also where the study corrected itself. A raw contraction
spectrum initially looked sharp across all seven parameters; SBC and expected
coverage showed the posterior was overconfident, and per-parameter conformal
recalibration loosened the diffuse block to at or above the prior width. A posterior
correlation between interventricular delay and myocardial velocity (about $-0.72$)
was at first read as a degeneracy and then refuted: a tilted but thin joint is
still identifiable, and a correlation is not non-identifiability. An audit further
found the spectrum had first been measured in a near-noiseless regime; rescaling
the forward to physiological millivolts and re-running loosened the magnitudes
while preserving the ordering and the identifiable-versus-diffuse structure. Each
correction narrowed the claim and made it truer.

== Limitations

No measured ECG appears anywhere in this work; every target is simulator output,
so parameter-recovery checks are in the inverse-crime setting and are not fidelity
results. The forward is an unbounded homogeneous pseudo-ECG, not a torso model,
and its lead-dependent amplitude deficit means amplitude-borne conclusions (most
exposed: RV initial extent, which rides a precordial amplitude feature) may not
transfer unchanged to a bounded forward. The noise floor is white, whereas real
ECG noise is colored; the waveform bound is therefore optimistic in a stated
direction of unestablished magnitude. The identifiability characterization reported here is established on a single reference geometry. Extending it across the publicly available Strocchi virtual cohort is a natural continuation of this work, and preliminary runs on two of those hearts already exercise the full pipeline end to end; we present them as groundwork for a cohort-level study rather than as identifiability claims in their own right.

= Conclusion

We reported a calibrated, amortized characterization of which His-Purkinje and
myocardial conduction parameters the 12-lead ECG can determine at fixed anatomy
and a stated observation-noise floor. Interventricular delay and myocardial
velocity are well constrained, RV initial Purkinje extent and global conduction
velocity moderately so, and LV extent, branch angle, and branch repulsivity are
formally diffuse, no tighter than the prior. The finding is delivered with a
calibration audit that moves the joint posterior from overconfident to calibrated,
so the diffuse verdict is an honest information statement rather than an estimator
artifact. The methodological point is that identifiability is a property of the
forward map at a stated floor, measured on a calibrated posterior, and that
reporting a fitted value without that audit cannot distinguish a constrained
parameter from an unconstrained one.

== Future work

Three steps, in order of leverage, each trading a stated caveat for a harder test.
First, anatomy generalization: repeat the calibrated characterization across a
public cohort of geometries to separate what is a property of the forward map from
what is a property of one fixed anatomy. Second, a bounded forward: replace the
unbounded pseudo-ECG with a torso volume conductor, which changes depolarization
amplitude by over an order of magnitude @bishopplank2011, and re-measure the
spectrum against that operator. Third, real recordings: move from simulator output
to measured 12-lead ECGs, breaking the inverse-crime setting, with a
waveform-trained learned embedding as the route past hand-crafted summaries.

== Data and code availability

Code, the trained NPE checkpoint, the simulation sweeps, and the calibration
artifacts are released under tag #raw("v0.1.0-submission") at
#link("https://github.com/ricardogr07/ecg-purkinje-npe")[github.com/ricardogr07/ecg-purkinje-npe].
The container builds from source per the repository; recorded image digests are in
the release notes. An interactive demonstration is available at the project site.

#heading(level: 1, numbering: none)[Acknowledgment]

The author thanks Professor Francisco Sahli Costabal for the foundational work and guidance that underpin the forward-modeling pipeline used in this study, in particular the fractal Purkinje network generation and eikonal activation on which the identifiability analysis builds @sahlicostabal2015.

#bibliography("refs.bib", title: "References", style: "vancouver.csl")

]
