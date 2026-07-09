# Verification ledger

The single public record of what this project checked against a primary source versus what it
asserted. Every load-bearing scientific claim in the docs, the demo, and the write-up traces to a
row here. It is the best evidence that the finding is trustworthy: it shows the honest edges, not
just the wins.

Consolidated from three internal verification passes (P0/P1, Batch 2, Batch 3). The raw batch
notes, with per-source DOIs/PMIDs and the full working, live in the internal research lane and are
not shipped; this file is their public distillation.

## Status words

Per the governance in [`scientific-process.md`](scientific-process.md), every claim carries one of:

- **VERIFIED** — a primary source was string-checked (arXiv/PubMed/PMC/PDF), or the arithmetic was
  reproduced in-kernel.
- **BOUNDED** — checked but inconclusive: body/paywalled, abstract-only, a convention, or not
  exhaustive (e.g. a "none found" negative). Honest but not airtight.
- **ASSERTED** — a reasoned design recommendation or a standard derivation, not attributed to an
  opened source. Forbidden in a load-bearing claim unless flagged as such.
- **REFUTED** — checked and found false; corrected everywhere.

House rule: **compute beats narrative, the ledger beats prose, a primary source beats everyone.**

## Simulator determinism (the founding invariant)

| Claim | Source checked | Status |
|---|---|---|
| `purkinje-uv` tree growth is stochastic (a PCG64 nuisance to exploit) | GitHub source: `config.py`, `branch.py`, `fractal_tree.py`, `edge.py`, `nodes.py`, `mesh.py` | REFUTED: `rng` is never consumed in growth; the branch angle is read directly from theta, so growth is deterministic given theta. Confirmed by a same-theta-twice runtime diff (bit-identical). |
| Consequence: an explicit observation-noise model is mandatory (no stochastic nuisance exists) | derivation from the above | VERIFIED (bit-identical forward confirmed in a test, `tests/test_forward_determinism.py`) |

## Observation-noise floor (Contract D)

| Claim | Source checked | Status |
|---|---|---|
| QRSense (Obregon-Rosas et al., J Electrocardiol 2026, PMID 42176693) resolves; DOI 10.1016/j.jelectrocard.2026.154368 | PubMed metadata | VERIFIED |
| QRS voltage 95% LoA -0.0958 to +0.1922 mV (bias +0.0482); QRS duration LoA -16.24 to +13.59 ms (bias -1.32) | QRSense abstract, verbatim | VERIFIED |
| LoA -> sigma_single = SD_diff/sqrt(2): 0.052 mV / 5.38 ms, rounded to 0.05 mV / 5 ms; waveform floor 0.025 mV = half the amplitude SD | in-kernel arithmetic | VERIFIED (reproduced) |
| QRSense first author is "Corrales" | PubMed author block | REFUTED: it is Santiago Obregon-Rosas; corrected in all files |
| Peak SNR ~28 at sigma 0.05 mV on a 1.4 mV peak | in-kernel peak/sigma | VERIFIED (reproduced) |
| Recommended sweep interval sigma in [0.025, 0.10] mV | synthesis of regimes | ASSERTED (design recommendation) |
| Research/SAECG best-case ~0.005-0.01 mV; ambulatory worst-case 0.10-0.20 mV | Breithardt 1991; MIT-BIH NSTDB (Moody/Muldrow/Mark 1984) | BOUNDED (regime confirmed; the exact mV thresholds are body/convention, not string-checked) |

## Amplitude scale (the physiological-mV defense)

| Claim | Source checked | Status |
|---|---|---|
| Rijnbeek 2014 (PMID 25194872) is a per-lead normal-limits ECG amplitude reference | green-OA PDF, full text | VERIFIED |
| Sokolow-Lyon ULN 3.5 mV (SV1 + max(RV5,RV6)); Cornell ULN 2.8 mV men / 2.0 mV women; P-wave ULN 0.25 mV | Rijnbeek 2014 PDF main text + Table 3 | VERIFIED (string-checked) |
| ~1.4 mV forward peak sits at the low-normal edge and understates SNR vs a typical normal peak (1.5-2.5 mV) | comparison + in-kernel SNR | VERIFIED as inequality; the per-lead 1.5-2.5 mV band is BOUNDED (Rijnbeek Supp. Tables 6/7, Wu 2003, Katibi 2013 bodies not string-checked) |
| Verdict: 1.4 mV is defensible, low-normal, SNR-conservative; optional 2.0 mV re-run | synthesis | ASSERTED (design recommendation) |

## Contract A priors provenance

| Claim | Source checked | Status |
|---|---|---|
| `delta_iv` measured envelope: LBBB RV-LV delay 77 +/- 38 ms | Gold 2018, PMID 30354310 (SMART-AV substudy) | VERIFIED (abstract) |
| `delta_iv` positive/paced anchor: VV pacing programmed LV-40 to LV+40 | Burri 2005, PMID 16171751 | VERIFIED (abstract) |
| Normal RV/LV breakthrough near-simultaneous (a wide box is a disease/pacing box) | Durrer 1970, PMID 5482907 | BOUNDED (metadata verified; 1970 body absent from PMC) |
| LBBB U-shaped activation, RV-first / LV-last around a line of block | Auricchio 2004, PMID 14993135 | BOUNDED (qualitative pattern from abstract; transseptal ms paywalled, marked UNVERIFIED) |
| `cv` control 2.2 m/s (1.5 in CHF); `cv_myo` from a human myocardial-CV compilation | Maguy 2009 (PMID 19359601); Fu 2024 (PMID 39484125) | VERIFIED (abstract) |
| Model-param ranges (`init_length`, `branch_angle`, `w`) trace to the generation method + a third-party SA | Sahli Costabal 2015 (PMID 26748729); Tanikella 2025 (arXiv:2505.16696) | VERIFIED (Tanikella Table 1 read at full text) |
| Tanikella: `init_length` 50 mm each, over 30-60, LV/RV split | arXiv:2505.16696 Table 1 | PARTLY REFUTED: init_length is FIXED at 50 mm (LV network only, not swept); the 30-60 range and LV/RV split are OUR modeling choices |
| Tanikella: `branch_angle` and `w` are simply low-sensitivity | arXiv:2505.16696 results | REFINED: S1 small but ST ~1 (interaction-dominated); prediction updated to weak-marginal + degeneracy for the diffuse block |

## Datasets

| Claim | Source checked | Status |
|---|---|---|
| Strocchi four-chamber cohort = Zenodo 3890034, CC-BY-4.0, 24 files, 22.5 GB | Zenodo API | VERIFIED at source |
| Strocchi et al., PLoS ONE 2020, DOI 10.1371/journal.pone.0235145, PMID 32589679, CC-BY-4.0 (journal record for the Zenodo 3890034 cohort) | PubMed metadata | VERIFIED |
| MedalCare-XL = Sci Data 2023 (PMID 37553349); Zenodo 8068944, CC-BY-4.0; 12-lead CSV, 500 Hz, mV; reaction-eikonal monodomain | PubMed + PMC10409805 + Zenodo API | VERIFIED (signals-only record; underlying meshes not separately pulled, BOUNDED) |
| EDGAR = J Electrocardiol 2015 (PMID 26320369), open-access ECGI/BSPM resource | live repository page + PMC4624576 | VERIFIED at source; moves to future work (not a drop-in 12-lead conduction target) |
| MyoFit46 = controlled-access CMR sub-study, no ECG/Purkinje ground truth | PubMed abstracts (PMID 41404671, 41796595) | VERIFIED; dropped from feasible inputs |

## Forward model and eikonal

| Claim | Source checked | Status |
|---|---|---|
| Standard 12-lead placement/recording; 0.05-150 Hz diagnostic bandwidth | Kligfield 2007, PMID 17322457 | VERIFIED prior batch (Strocchi ships NO electrode file, hence the disclosure) |
| Monodomain vs bidomain surface-potential differences are very small | Potse 2006, PMID 17153199 | VERIFIED (justifies the monodomain/eikonal + lead-field operator, synthesized with a `1/|r|` infinite-homogeneous-medium kernel at assumed standard electrode positions; no torso volume conductor) |
| Cardiac eikonal-curvature framework; bidomain reduces to eikonal via singular perturbation | Keener 1991 (PMID 1940663); Colli Franzone 1990/2004 | VERIFIED (framework) |
| CV proportional to sqrt(D) (the `cv_myo` rescale) | eikonal framework + traveling-wave theory | ASSERTED (standard derived consequence, not a quoted sentence; Costa FIMH-2013 recipe not PubMed-indexed) |
| Orthotropic myocardium, fiber:transverse CV ratio ~2.2:1 | Caldwell 2009, PMID 19808500 | BOUNDED (ratio from body/tables, not this-session abstract) |

## Prior art and calibration methodology

| Claim | Source checked | Status |
|---|---|---|
| Closest prior art: non-uniqueness existence + PMJ prior + DT ensemble | Grandits et al. 2024, arXiv:2411.00165 | VERIFIED (abstract); NOT an independent group (Pezzuto co-authors both it and our own line) |
| Our own line: BO+ABC network population, uncalibrated | Alvarez-Barrientos et al. 2025, arXiv:2312.09887 | VERIFIED (author block confirmed) |
| Forward Sobol sensitivity of QRS to HPS (the inverse counterpart of our work) | Tanikella 2025, arXiv:2505.16696 | VERIFIED (must-distinguish) |
| SBI calibration toolkit: SBC, expected coverage, TARP; the SBI overconfidence motivation | Talts 2018 (1804.06788); Lemos 2023 (2302.03026); Hermans 2021 (2110.06581) | VERIFIED (prior batch, reused) |
| No cardiac-conduction SBI paper reports SBC/coverage/TARP | targeted arXiv + PubMed searches | BOUNDED negative ("none found"), not proof of nonexistence; OpenAlex unavailable |
| "amortization mimics unidentifiability" supported by arXiv:2603.21752 | abstract | REFUTED: positive result about Kuramoto oscillators, not cardiac; dropped as evidence |

## The prior-width-invariant metric (Batch 3 cross-check)

| Claim | Source checked | Status |
|---|---|---|
| In the linear-Gaussian limit, EIG_k = -log(contraction_k) exactly, so expected information gain inherits contraction's prior-width dependence | in-kernel reproduction over 4 (prior_sd, noise_sd, n) settings | VERIFIED (reproduced): EIG is NOT a fix for the cv-floor-change confound |
| sigma_CRLB = noise_sd / sqrt(n) is prior-width invariant while contraction is not | in-kernel: widening prior 1.0 to 10.0 left sigma_CRLB fixed while contraction fell 0.277 to 0.029 | VERIFIED (reproduced): the Fisher-information object is the prior-invariant axis to report |
| Sloppy/stiff FIM eigenspectrum is a prior-free likelihood property | Gutenkunst 2007, PMID 17922568 | VERIFIED at source |
| Profile likelihood separates structural vs practical identifiability | Raue 2009, PMID 19505944 | VERIFIED at source |
| EIG foundational OED references | Lindley 1956; Ryan et al. 2016 | ASSERTED, NOT verified at source (standard references; identifiers from background knowledge, bodies not opened) |

## Honest edges (the bounded and asserted register)

Gathered so a reviewer sees every soft spot in one place:

- The `delta_iv` box [-90, 40] is a modeling choice contained in the ~[-115, +80] ms literature
  envelope; a symmetric [-90, 90] is equally sourced. It is asymmetric and its negative magnitude
  trails crtdemo's true ~-75 ms, which can read as tuned to the answer. Science's call, documented.
- The 7D contraction numbers are the upstream compute result, taken as given here, not re-derived in
  the verification passes.
- cv/cv_myo degeneracy is a reasoned shared-channel expectation, not an independent
  posterior-correlation measurement yet.
- Contraction magnitudes are properties of this fixed anatomy and fixed lead field; their
  anatomy/lead-geometry independence is NOT established.
- OpenAlex citation-graph corroboration was unavailable all project (credential declined), so
  "none found" negatives are bounded nulls, not proofs of absence.
- The forward-vs-real-ECG fidelity is a diagnosed, quantified gap (operating-point error, corr 0.199
  to 0.788 recovered, residual identified), NOT real-ECG validation. This ledger never launders it
  into "forward validated".
