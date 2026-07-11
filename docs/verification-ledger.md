# Verification ledger (public, consolidated)

Every factual claim in the finding, the results summary, and the manuscript, with a stable ID, the source checked, and the status word (VERIFIED / BOUNDED / ASSERTED / REFUTED). This is the checkable evidence behind the work. Consolidated from the batch ledgers; see docs/scientific-process.md for the status vocabulary and promotion rule.

## Batches 1 to 5 (consolidated)


*Consolidated checked-vs-asserted evidence ledger for the conduction-lens Purkinje-conduction identifiability project. This file collects every source-verification performed across Batches 1 to 5 into one public record, so the evidence that the project's claims are checkable ships to readers instead of sitting in a gitignored folder.*

## ID scheme

Every row carries a stable ID `L-B{batch}-{nn}`, assigned in batch-then-row order (`L-B1-01` is the first row of Batch 1, `L-B4-32` the last row of Batch 4, `L-B5-nn` the Batch-5 verifications added by this consolidation). IDs are immutable once assigned: cite a claim by its ID, not by its position. Within a batch the rows are grouped under the section headers used in that batch's original ledger; ID order follows reading order across those sections.

## Status words

- **VERIFIED**: the primary source was string-checked (abstract, body, author block, table cell, or code) or the arithmetic was reproduced in-kernel, at the level named in the Source column.
- **BOUNDED**: checked but inconclusive: body or supplement not reachable, a non-exhaustive negative, or a value confirmed only at a coarser level than the claim needs. Every bounded row states precisely what remains unchecked.
- **ASSERTED**: a definitional statement or a reasoned design recommendation, not attributed to an opened source.
- **REFUTED / PARTLY REFUTED / REFINED / verified / partly-verified**: status words carried verbatim from the original batch ledgers (Batches 1 and 2 used lowercase words; Batches 3 and 4 used uppercase). Text is preserved as written; only the leftmost ID column was added.

## Changelog

- **Batch-5 consolidation (this file).** Merged the four per-batch ledgers (verification_ledger_P0P1.md, verification_ledger_batch2.md, verification_ledger_batch3.md, verification_ledger_batch4.md) into one public document. Retrofitted stable `L-B{batch}-{nn}` IDs to all 114 pre-existing rows (Batch 4 shipped without any IDs; Batches 1 to 3 had none either). Each row's Claim, Source checked, and Result text and its status word are preserved verbatim; the only change is the added leftmost ID column. Added a `Batch 5 verifications` section with two new source-verifications: the TARP / Lemos 2023 ATC sign convention (L-B5-01) and the Rijnbeek 2014 per-lead R/S-wave percentiles (L-B5-02).
- No em-dashes or en-dashes anywhere (house style); verified in-kernel before saving.
- **UI display tiers (demo).** The identifiability spectrum sorts contraction into three display tiers: resolved < 0.5, moderate in [0.5, 0.85), diffuse >= 0.85 (ui/src/lib/colormap.ts). These boundaries are a presentation choice tuned so the shipped contractions partition as the paper states (2 well resolved, 2 moderate, 3 diffuse); they change no contraction value. ASSERTED (design decision).

## Batch 1 (P0/P1): QRSense noise floor, Tanikella sensitivity, author corrections

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B1-01 | QRSense paper (PMID 42176693) resolves; J Electrocardiol 2026; doi 10.1016/j.jelectrocard.2026.154368 | PubMed metadata (this session) | verified |
| L-B1-02 | Bland-Altman: voltage LoA -0.0958..+0.1922 mV (bias +0.0482); duration LoA -16.24..+13.59 ms (bias -1.32); Lin CCC 0.9527/0.9221 | PubMed abstract (verbatim) | verified |
| L-B1-03 | LoA->sigma: sigma_single=(hi-lo)/(2*1.96*sqrt(2)) -> 0.052 mV / 5.38 ms; rounded 0.05 mV / 5 ms | in-kernel recomputation | verified (arithmetic reproduced) |
| L-B1-04 | QRSense first author is 'Corrales' | PubMed author block | REFUTED - first author is Santiago Obregon-Rosas; no 'Corrales' present. Corrected in all files. |
| L-B1-05 | Tanikella 2025 gives LV/RV init_length ~50mm each over range 30-60 | arXiv:2505.16696 Table 1 + sec 2.3 | PARTLY REFUTED - init length FIXED at 50mm (not swept), LV network only; 30-60 range & LV/RV split are our modeling choices. |
| L-B1-06 | Tanikella Sobol: alpha and w both simply low-sensitivity/flat | arXiv:2505.16696 results | REFINED - S1 small but ST~1 (interaction-dominated); w flagged interaction-heavy. Prediction updated to weak-marginal + degeneracy. |

## Batch 2: datasets, Strocchi ECG forward setup, eikonal CV/anisotropy, write-up citations

### Datasets (step 1)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B2-01 | MedalCare-XL = Sci Data 2023, PMID 37553349, DOI 10.1038/s41597-023-02416-4, arXiv:2211.15997 | PubMed metadata + arXiv record | verified |
| L-B2-02 | MedalCare-XL on Zenodo record 8068944 (DOI 10.5281/zenodo.8068944), CC-BY-4.0, ~9.3 GB | Zenodo API (this session) | verified at source |
| L-B2-03 | MedalCare-XL = 12-lead ECG CSV, rows I,II,III,aVR,aVL,aVF,V1-V6, 500 Hz, mV; raw/noise/filtered; splits by anatomy | PMC full text PMC10409805, Data Records | verified (verbatim) |
| L-B2-04 | MedalCare-XL forward model = reaction-Eikonal, monodomain, no diffusion; lead fields precomputed once per model | PMC full text PMC10409805 | verified (verbatim) |
| L-B2-05 | MedalCare-XL ECG record ships signals, not per-sample meshes | PMC full text (Data Records) | verified (bounded: meshes live in the separate Gillette cohort framework, not the ECG record) |
| L-B2-06 | EDGAR = J Electrocardiol 2015, PMID 26320369, DOI 10.1016/j.jelectrocard.2015.08.008 | PubMed metadata | verified |
| L-B2-07 | EDGAR live, open-access, free registration required, Utah SCI/CIBC host, ecg-imaging.org | live repository page + PMC full text PMC4624576 | verified at source |
| L-B2-08 | EDGAR content = BSPM + epicardial/transmural potentials + torso/heart geometry; MATLAB-readable + ASCII/PDF metadata | PMC full text PMC4624576 | verified |
| L-B2-09 | EDGAR 2015 paper copyright = Elsevier all-rights-reserved (paper, not data) | PubMed copyright status PMID 26320369 | verified; data reuse terms are per-dataset at registration, NOT asserted as CC-BY |
| L-B2-10 | MyoFit46 = CMR sub-study of NSHD 1946 birth cohort, ~500 participants ~77 y, stress-perfusion + LGE | PubMed abstracts PMID 41404671, 41796595 | verified |
| L-B2-11 | MyoFit46 controlled-access CMR imaging, no ECG/Purkinje ground truth | PubMed abstracts | verified as controlled-access imaging cohort; exact access-portal URL NOT confirmed (bounded) |
| L-B2-12 | Strocchi four-chamber cohort = Zenodo 3890034, CC-BY-4.0, 24 .gz files, 22.5 GB | Zenodo API (this session) | verified at source |
### Strocchi 12-lead ECG forward setup (step 2)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B2-13 | Kligfield 2007 (PMID 17322457, Circulation, DOI 10.1161/CIRCULATIONAHA.106.180200) reviews standard 12-lead lead placement/recording | PubMed metadata + abstract | verified |
| L-B2-14 | Gima & Rudy 2002 (PMID 11988490, Circ Res, DOI 10.1161/01.res.0000016960.61087.86) computes ECG waveforms from cellular/transmembrane activity | PubMed metadata + abstract | verified |
| L-B2-15 | Potse 2006 (PMID 17153199, IEEE TBME) shows monodomain vs bidomain surface-potential differences are very small | PubMed abstract | verified (justifies monodomain/eikonal + lead-field forward operator) |
| L-B2-16 | Geodesic-BP (2308.08410) matches eikonal ECGs to clinical ECGs; Zappon (2407.17146) quantifies sim-vs-measured gap | verified prior session (related-work.md) | reused |
| L-B2-17 | Standard V1-V6 intercostal-space positions | Kligfield 2007 standardization statement | asserted as standard clinical convention, sourced to Kligfield rather than re-derived; Strocchi ships NO electrode file (this is why the disclosure exists) |
### Eikonal CV scaling + anisotropy (step 3)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B2-18 | Keener 1991 (PMID 1940663, J Math Biol, DOI 10.1007/BF00163916) derives the cardiac eikonal-curvature equation | PubMed metadata + abstract | verified (framework) |
| L-B2-19 | Colli Franzone 1990 (PMID 2319210) reduces the bidomain wavefront to eikonal equations via singular perturbation | PubMed metadata + abstract | verified |
| L-B2-20 | Colli Franzone 2004 (PMID 14766102, DOI 10.1016/j.mbs.2003.09.005) applies eikonal approximation, studies conductivity-tensor effects | PubMed metadata + abstract | verified |
| L-B2-21 | CV proportional to sqrt(D) scalar relation (the cv_myo rescale) | eikonal framework above + monodomain traveling-wave theory (textbook) | asserted as the standard derived consequence, NOT a verified abstract sentence; honestly flagged |
| L-B2-22 | Myocardium orthotropic, fastest along fiber; fiber:transverse CV ratio ~2.2:1 (Caldwell 2009, PMID 19808500) | verified prior session; abstract qualitative, m/s values body/tables | reused; ratio number from body/tables not this-session abstract |
| L-B2-23 | Roberts & Scher 1982 (PMID 7060230) = potential-field anisotropy, not a CV ratio | verified prior session | reused for anisotropy-matters, not for the CV ratio number |
| L-B2-24 | Costa FIMH-2013 explicit D-scaling recipe | attempted PubMed | NOT retrieved (not PubMed-indexed); sqrt(D) grounded in eikonal framework + traveling-wave theory instead (bounded) |
### Write-up citations (step 5, all reused from verified related-work.md)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B2-25 | Gold 2017 (PMID 29195547) interventricular delay vs HF outcomes; Gold 2018 (PMID 30354310) delay and CRT response | verified prior session | reused |
| L-B2-26 | LBBP-RESYNC (Wang 2022, PMID 36137670) LVEF diff 5.6% (95% CI 0.3-10.9, P=0.039) | verified prior session | reused (verbatim) |
| L-B2-27 | Hermans 2021 (2110.06581), Talts SBC (1804.06788), Lemos TARP (2302.03026), CANVI (2305.14275) | verified prior session | reused |
| L-B2-28 | Alvarez-Barrientos 2025 (2312.09887), Grandits 2024 (2411.00165) = uncalibrated BO+ABC / ensemble | verified prior session | reused |
| L-B2-29 | No cardiac-conduction SBI paper reports SBC/coverage/TARP | targeted arXiv+PubMed searches | bounded negative ("none found"), NOT proof of nonexistence; OpenAlex unavailable |

## Batch 3: source-defense of the honest 7D result (noise/amplitude, EP mechanism, adversarial + prior-invariant metric)

### Cross-check performed by the verification lead (not delegated)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B3-01 | In the linear-Gaussian limit, per-parameter EIG_k = -log(contraction_k) exactly, so expected information gain inherits the same prior-width dependence as contraction | in-kernel reproduction over 4 (prior_sd, noise_sd, n) settings: EIG (entropy reduction) matched -log(posterior_sd/prior_sd) to float precision in every case | VERIFIED (reproduced), elevating the track's ASSERTED derivation |
| L-B3-02 | sigma_CRLB = noise_sd / sqrt(n) is invariant to prior width while contraction is not | in-kernel: widening prior_sd 1.0 to 10.0 at fixed likelihood left sigma_CRLB unchanged (0.289) while contraction fell 0.277 to 0.029 | VERIFIED (reproduced): confirms the FIM/CRLB recommendation is the genuinely prior-invariant axis |
### Track P0a: Noise floor defense (Contract D)

| ID | Claim | Source checked | Result |
|---|---|---|---|
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
### Track P0b + P1: EP mechanism and parameter-to-feature map

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B3-24 | Durrer 1970 = Circulation 41(6):899-912, PMID 5482907, DOI 10.1161/01.cir.41.6.899, authors Durrer/van Dam/Freud/Janse/Meijler/Arzbaecher | PubMed get_article_metadata author block | VERIFIED at metadata level |
| L-B3-25 | Durrer 1970 body activation-timing specifics (early septal L-to-R, early anterior RV breakthrough, posterobasal LV last, ~80 ms total) | attempted full text; 1970 paper not in PMC | BOUNDED (canonical attribution; metadata verified, body not string-checked) |
| L-B3-26 | Modeling uses 1 mm fast-conducting endocardial layer in LV and RV; endocardial breakthrough = earliest-activation landmark | PMC8025079 full text string-checked | VERIFIED (secondary/methodological confirmation) |
| L-B3-27 | LV myocardial mass dominates the QRS mean vector (basis of LVH voltage criteria) | searched; candidate PMID 38151605 checked and REJECTED (neonatal, low LV-mass/QRS correlation) | BOUNDED (textbook vectorcardiography; no string-checked primary sentence this batch) |
| L-B3-28 | Gold 2018 PMID 30354310 = interventricular electrical delay as measurable ECG quantity modulating CRT timing | PubMed get_article_metadata title/journal/abstract | VERIFIED at metadata/abstract level |
| L-B3-29 | Gold 2017 PMID 29195547 = interventricular conduction delay predicts CRT response | PubMed get_article_metadata | VERIFIED at metadata/abstract level |
| L-B3-30 | Tanikella 2025 arXiv:2505.16696: QRS durations/peak amplitudes low sensitivity to individual HPS params; timing variability driven by branch/fascicle-angle and repulsivity interactions | arXiv API abstract string-checked (title, author block, 2025-05-22) | VERIFIED at abstract level |
| L-B3-31 | Keener 1991 PMID 1940663 eikonal CV controls activation time | reused verified anchor, not re-fetched | ASSERTED (prior-verified anchor) |
| L-B3-32 | cv and cv_myo partially degenerate (both scale global activation timing), explaining cv's weaker contraction | reasoned shared-channel argument | ASSERTED (degeneracy expectation, not an independent posterior-correlation measurement this batch) |
| L-B3-33 | LV/RV mechanism verdict: partly holds (directionally sound; LV-dominance limb bounded) | synthesis | ASSERTED (reasoned verdict) |
| L-B3-34 | Contraction magnitude (0.63 vs 1.0-1.2) may be anatomy/lead-geometry dependent (single coarse mesh, fixed lead field) | reasoned from fixed-anatomy design | BOUNDED (alternative not excluded) |
### Track P1 + P2: Refreshed adversarial pass and prior-width-invariant metric

| ID | Claim | Source checked | Result |
|---|---|---|---|
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

## Batch 4: Strocchi ingestion, torso/route gating result, cross-geometry protocol

### Track 1: Torso verdict + ingestion spec (P0-1, P0-2, P0-3)

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
### Track 2: Cross-geometry protocol + writeup notes (P0-4, P0-5, P1, P2)

| ID | Claim | Source checked | Result |
|---|---|---|---|
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

## Batch 5 verifications: TARP sign convention and Rijnbeek supplement string-check

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B5-01 | We report a coverage/calibration statistic we call ATC = -0.072 and describe it as 'mildly conservative', citing Lemos 2023 (arXiv:2302.03026, TARP) | Lemos 2023 arXiv abstract + PDF body (full text, string-checked: ATC-search, 'conservative'-search, over/underconfident case definitions, expected-coverage curve framing) | BOUNDED / LABEL-CORRECTION. String-checked in the paper: the token 'ATC' appears NOWHERE (the 4 apparent hits are substrings Match/batch/matching) and the word 'conservative' appears ZERO times. TARP = Tests of Accuracy with Random Points; the paper's reported quantity is the expected coverage probability ECP(p-hat, alpha) plotted vs credibility level 1-alpha, accurate iff ECP = 1-alpha (the diagonal, string-checked Sec on Fig 2). Paper's string-checked case definitions (Sec 4.1 / App B): drawing truths from N(theta*, 0.5 Sigma) makes the posterior too NARROW = OVERconfident; N(theta*, 2 Sigma) makes it too WIDE = UNDERconfident; for underconfident estimators the TARP coverage tends to ~0.5, for overconfident it tends to 0 or 1. STANDARD coverage convention (not a TARP-specific string in this paper): an under-confident / over-dispersed posterior OVER-covers (ECP above the diagonal) and is the 'conservative' case; an over-confident posterior UNDER-covers (below diagonal) and is 'anti-conservative'. VERDICT: 'ATC = -0.072' and 'mildly conservative' are OUR labels, NOT defined in Lemos 2023; the paper provides no signed scalar named ATC and no sign->conservative map, so the SIGN of -0.072 cannot be adjudicated from the paper. It resolves only against our own (here un-inspected) ATC formula and the code that produced -0.072. Keep BOUNDED until that formula is string-checked; do not assert 'conservative' as a Lemos-sourced fact. |
| L-B5-02 | Rijnbeek 2014 (PMID 25194872) per-lead R-wave and S-wave amplitude percentiles, Supplemental Tables 6 and 7 (previously BOUNDED, not string-checked) | Elsevier supplement mmc1.doc (PII S0022073614002969), Supplemental Tables 6 (R-wave) and 7 (S-wave), string-checked in-kernel from the .doc WordDocument stream | VERIFIED (string-checked at source). Both tables give median (98th percentile) amplitude in mV per lead x sex x 8 age groups (16-19..80-89). R-wave (Table 6) precordial peaks (Male, 16-19): V4 1.79 (3.93), V5 1.89 (2.97), V6 1.32 (2.37); limb II 1.39 (2.24). S-wave (Table 7) peaks (Male, 16-19): V2 2.01 (3.54), V1 1.01 (2.47), V3 1.27 (2.77). This CONFIRMS the prior BOUNDED inference: single-lead peak deflections reach ~1.5 to 2.5 mV (98th percentiles up to 3.93 mV in V4), corroborating the decomposition of the verified Sokolow-Lyon ULN of 3.5 mV. The ~1.4 mV modeled peak sits at the low-normal edge (SNR-conservative), as previously stated. |

## Batch 6


*Consolidated checked-vs-asserted ledger for Batch 6. Resolves whether the
well-conditioned local FIM vs diffuse prior-averaged posterior gap is a category
error or a real finding (P0-1), sources the accepted NPE diagnostics for the
retrain (P0-2), bounds whether the pseudo-ECG amplitude deficit is uniform or
lead-differential (P0-3), and formalizes the four-claim retraction ledger (P1) and
the rewritten falsification list (P1-2). Status words: VERIFIED (primary source
string-checked, arithmetic reproduced in-kernel, or textbook-standard),
BOUNDED (checked but inconclusive or a non-exhaustive negative), ASSERTED
(definitional, logical, or a reasoned design statement), REFUTED (a project claim
withdrawn with internal killing evidence). Stable IDs L-B6-nn. No em/en dashes.*

## Headline results

1. **P0-1 (load-bearing): CATEGORY ERROR at the level of the two numbers; the
   substantive reading is UNRESOLVED and must not be guessed.** The frequentist
   CRLB (a lower bound on the variance of an UNBIASED estimator, from the Fisher
   information at a point) and a Bayesian posterior_std under a proper prior are
   different quantities: the posterior can sit BELOW the CRLB (the prior adds
   information, van Trees J = J_D + J_P) or ABOVE it (an inefficient or
   budget-limited estimator does not attain the bound). Neither refutes the other,
   so "CRLB tight but contraction diffuse" is no contradiction (Part A, settled).
   Correction to the original claim: the CRLB is a FINITE-SAMPLE bound; the word
   "asymptotically" belongs to the MLE ATTAINING it (asymptotic efficiency), not
   to the bound. Whether the diffuseness means the ECG lacks the information
   (identifiability finding) or the N=5000 flow fails to extract present
   information (estimator finding) is NOT settled by the single-point FIM; it needs
   the multi-point FIM across the box plus the N-halving check (Part B, open). The
   lead reproduced both directions numerically in-kernel (posterior_std below the
   CRLB under an informative prior; above it for an information-discarding
   estimator).

2. **P0-2: accepted NPE diagnostics sourced.** Held-out log-probability, loss-curve
   saturation, N-halving convergence of contraction, posterior-predictive checks,
   and SBC / expected-coverage (Talts 2018, Lemos 2023, Hermans 2021; Lueckmann
   2021 benchmarking; Papamakarios/Greenberg NPE). Recommended battery for the
   retrain: held-out log-prob + loss saturation + N-halving on contraction,
   cross-checked by SBC/coverage. SBC tests calibration, which is necessary but
   distinct from "the flow extracts all the information."

3. **P0-3: DIFFERENTIAL, not uniform (BOUNDED).** VERIFIED at primary level: the
   deficit is distance-dependent (Bishop-Plank 2011 full text) and the 1/|r|
   operator is proximity-weighting (Gima-Rudy 2002 full text), so it is
   lead-dependent and peak normalization does NOT absorb it; cross-lead
   amplitude features carry a lead-dependent bias. BOUNDED: (a) per-lead
   numerical distortion factors for our unbounded-vs-bounded-torso pair are not
   published (Bishop-Plank leave the in-vivo torso magnitude "to be determined";
   the order-of-magnitude figure is the ex-vivo small-bath regime); (b) the SIGN
   of the precordial-vs-limb ordering is not established (a-priori near-field says
   precordial-ward, the measured small-bath distance-dependence says limb-ward,
   the torso case is declared open). The task's a-priori precordial-concentrated
   guess is REVERSED by the source and must not be asserted as known.

4. **P1: four claims formally REFUTED** (retraction_ledger.md, R-01 to R-04), each
   with a date, verbatim original claim, and the internal killing artifact
   (best-lag-corr-0.86 vs per-lead nRMSE ~1 + 2.3x amplitude gap; delta_iv-cv_myo
   ridge vs ridge_confirm cv_myo corr 0.98 + Jacobian v_min = init_length_lv;
   forward-diverges-from-real-ECG vs the fixture, True_ecg is pickled simulator
   output, transplant corr 1.000 a tautology; TARP-near-calibrated vs
   emit.py:226 pre-conformal). Framed as the methods contribution.

5. **P1-2: falsification list rewritten** to the current one-result-plus-methods
   framing (falsification_update.md): Result B demoted to inverse-crime parameter
   recovery, four Batch-5 falsifiers carried over, the P0-1 estimator-limitation
   falsifier added, the Result-B-residual falsifier dropped and its torso-forward
   concern folded into the ordering item. TARP ATC sign is now a code question
   (sbi.diagnostics.check_tarp), deferred, not re-sourced.

## Track: Estimation theory (P0-1, P0-2)

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

## Track: Forward distortion (P0-3)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B6D-01 | Unbounded pseudo-ECG uses phi_e = (1/4 pi sigma_b) integral (beta I_m / |r|) dOmega, tissue in an unbounded medium | Bishop and Plank 2011, PMID 21536529, full text eq. 11 (string checked) | VERIFIED at full text; matches our forward (Batch 5 code) |
| L-B6D-02 | Recovery-vs-bounded amplitude deficit is distance-dependent ('accentuated with distance from the tissue'), hence NOT a uniform scale | Bishop and Plank 2011, full text Results (Fig. 5 discussion, string checked) | VERIFIED at full text |
| L-B6D-03 | The over-an-order-of-magnitude deficit is the small-bath ex-vivo regime, NOT a verified in-vivo torso number | Bishop and Plank 2011, full text (Figs. 5 and 6, Discussion, string checked) | VERIFIED as ex-vivo small-bath; in-vivo torso magnitude declared 'remains to be determined' by the authors |
| L-B6D-04 | grad(1/r) is a proximity-weighting operator: near electrode reads local sources, remote electrode reads whole heart, so leads sample the source differently | Gima and Rudy 2002, PMID 11988490, full text (Batch 5, string checked) | VERIFIED at full text |
| L-B6D-05 | Brief's a-priori claim that distortion is precordial-concentrated (near-field deviates most) | Bishop and Plank 2011 distance-dependence passage | REVERSED / not supported: measured deficit grows with distance (limb-ward) in the small-bath slab; torso direction declared open. Flagged. |
| L-B6D-06 | ECG amplitude most sensitive to blood, skeletal muscle, heart, fat, lung conductivity; fat affects morphology | Keller 2010, PMID 20659824, abstract (prior batches) | VERIFIED at abstract; per-tissue not per-lead, does not pin the precordial-vs-limb differential |
| L-B6D-07 | A clean published per-lead uniform-vs-differential decomposition for the unbounded-vs-bounded-torso comparison | PubMed search (this batch); narrow query returned only Bishop-Plank 2011 | BOUNDED NULL: no such published decomposition found |
| L-B6D-08 | Per-lead numerical distortion factors for our specific forward pair | (none) | BOUNDED: not pinned by any published number |
| L-B6D-09 | Sign of the precordial-vs-limb ordering for our geometry | Bishop-Plank (limb-ward, small bath) vs a-priori near-field (precordial-ward); torso open | BOUNDED: direction not established |

## Track: Retraction ledger + falsification (P1, P1-2)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B6R-01 | R-01: 'Forward validated, corr 0.86' is refuted by per-lead nRMSE about 1 and a 2.3x amplitude gap behind a best-lag correlation | project artifacts (forward-validation diagnostics), internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-02 | R-02: delta_iv-cv_myo degeneracy claim is refuted by ridge_confirm (cv_myo corr 0.98) and the Jacobian (v_min dominated by init_length_lv) | project artifacts (ridge_confirm, Jacobian/FIM), internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-03 | R-03: 'forward diverges from a real ECG' is refuted by the fixture (True_ecg is pickled simulator output; transplant corr 1.000 is a tautology) | project fixture and forward/inverse operator, internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-04 | R-04: TARP ATC -0.072 'near-calibrated' claim is refuted because src/npe/emit.py:226 computes it PRE-CONFORMAL | project code src/npe/emit.py line 226, internal | VERIFIED internally (project artifact/code), not a literature claim |
| L-B6R-05 | This retraction ledger is part of the methods contribution (checkable, dated, artifact-backed claims) | framing statement about project process | ASSERTED (framing, internally consistent with the four rows above) |
| L-B6R-06 | Batch-5 falsification section, original wording and item list | limitations_and_falsification.md version 9a7bb6bc, read in full this batch | VERIFIED internally (project artifact), read directly |
| L-B6R-07 | TARP ATC sign is a code question (sbi.diagnostics.check_tarp), deferred, not re-sourced here | scoping decision, not yet run | ASSERTED (deferred to a code check; not a literature claim) |
| L-B6R-08 | FIM at REFERENCE_THETA: condition number 18.3, tight CRLBs, nothing sub-noise | given upstream compute result, internal | VERIFIED internally (upstream compute result), reused as given |
| L-B6R-09 | Falsification outcomes (cross-simulator coverage, ordering under torso, CRLB under alternative noise, multimodality, P0-1 estimator gap) | forward reasoning from the current framing | ASSERTED (falsifiable predictions, not yet run) |

## Lead's independent verification (this session)

- Reproduced the CRLB-vs-posterior_std relationship numerically in-kernel
  (lead_crlb_posterior_demo.md): a linear-Gaussian model with a proper prior gives
  posterior_std BELOW the CRLB (gap widening as the prior tightens, vanishing as
  the prior goes flat), and an information-discarding unbiased estimator gives std
  ABOVE the full-data CRLB. The two quantities bracket the bound from both sides;
  neither refutes the other. This is the demonstrated basis for Part A of the P0-1
  verdict.
- Re-pulled Cardone-Noott 2016 singly at PubMed: Europace, 10.1093/europace/euw346
  (cited by the distortion track only as a related, different-axis paper).
  Independently re-pulled the three NPE-diagnostics arXiv
  preprints singly at arXiv (records via literature arxiv_get_papers, title +
  author block confirmed by the lead this session): 1605.06376 Papamakarios and
  Murray 'Fast epsilon-free Inference of Simulation Models with Bayesian
  Conditional Density Estimation'; 1905.07488 Greenberg, Nonnenmacher, Macke
  'Automatic Posterior Transformation for Likelihood-Free Inference'; 2101.04653
  Lueckmann, Boelts, Greenberg, Goncalves 'Benchmarking Simulation-Based
  Inference'. The 'VERIFIED at arXiv abstract + author block' status on rows
  L-B6E-07, L-B6E-08, L-B6E-10 is thus lead-confirmed, not only child-track
  reported. Bishop-Plank 2011, Gima-Rudy 2002, Keller 2010 reused from
  prior-batch verification; the distortion track's full-text re-read upgraded PMC3378475 to
  lead-confirmed via the PMC header.

## Consolidated bounded-claim register

### Estimation theory
- P0-1 estimation-theory rows (Kay, Lehmann-Casella, Van Trees) are TEXTBOOK-STANDARD, stated from standard knowledge, NOT string-checked against the physical textbooks in this session.
- Gill and Levit 1995 (Bernoulli 1(1/2):59-79) is given as the standard van Trees / Bayesian-CRB reference but is NOT string-checked this session (citation asserted).
- P0-2 loss-curve saturation and posterior-predictive checks are ASSERTED as standard practice with no single primary SBI paper string-checked.
- The contraction-vs-N (N-halving) reduction is our project's application of the budget-benchmarking practice (2101.04653), ASSERTED as an instance, not itself a paper result.
- P0-1 given numbers (FIM cond 18.3; contraction branch_angle 1.05, w 1.15, init_length_lv 0.97; N=5000) are taken as GIVEN upstream results, not re-verified (out of scope).
- P0-1 Part B (data-uninformative vs flow-under-extracts) is a bounded-null: current evidence supports NEITHER reading decisively; flagged as requiring multi-point FIM + N-halving to settle.

### Forward distortion
- BOUNDED: per-lead numerical distortion factors for the unbounded-pseudo-ECG vs bounded-torso pair are not pinned by any published number (Bishop-Plank leave in-vivo torso magnitude 'to be determined').
- BOUNDED: the over-an-order-of-magnitude deficit is the small-bath ex-vivo (Langendorff) regime, not a verified in-vivo torso figure.
- BOUNDED: sign of the precordial-vs-limb ordering for our geometry is not established (small-bath slab points limb-ward, a-priori near-field points precordial-ward, torso case declared open).
- BOUNDED NULL: no published per-lead uniform-vs-differential decomposition for the specific unbounded-vs-bounded-torso comparison was found.
- FLAGGED REVERSAL: the brief's a-priori precordial-concentrated guess is contradicted by the source's measured distance-dependence.

### Retraction ledger
- TARP ATC sign deferred to a code check (sbi.diagnostics.check_tarp source); not settled here and not a literature claim (bounded-null on the sign until the code is read).
- P0-1 falsifier (FIM-vs-posterior gap = real estimator limitation vs category error) is a not-yet-run prediction; the headline reading it as a prior-width effect plus a near-null init_length_lv direction is ASSERTED pending that controlled check.
- All four killing items are VERIFIED internally (project artifact/code), NOT literature-sourced; per task they were not re-verified at external source.
- Falsification predictions (cross-simulator coverage, torso-forward ordering, CRLB under alternative noise, multimodality) are ASSERTED forward predictions, not yet run.

## Batch 7


*Consolidated checked-vs-asserted ledger for Batch 7. The trigger: the waveform CRLB
now reports < 0.5% of prior range for all seven parameters, against a diffuse
feature-based contraction block; if that survives, the diffuse block is a
summary-statistic artifact, not an ECG limitation, but the waveform CRLB rests on a
white, lead-independent noise model that had not been checked. This batch verifies
the lead redundancy (P0-1), characterizes the noise (P0-2), classifies the features
(P0-3), sources the summary-statistic information-loss framing (P1), and adds two
pre-registered falsifiable predictions (P1-2). Status words: VERIFIED (primary
source string-checked, arithmetic reproduced in-kernel, or a standard/textbook
result), BOUNDED (checked but inconclusive or a non-exhaustive negative), ASSERTED
(definitional, a reasoned design statement, or a pre-registered prediction not yet
tested), VERIFIED internally (a project artifact or code, not a literature claim).
Stable IDs L-B7-nn. No em/en dashes.*

## Headline results

1. **P0-1 (lead redundancy, NOT arguable): only 8 of 12 leads are independent, so
   the waveform CRLB is optimistic on the lead axis.** III = II - I,
   aVR = -(I+II)/2, aVL = I - II/2, aVF = II - I/2 are exact algebraic identities;
   the Wilson central terminal WCT = (RA+LA+LL)/3 defines the precordial leads. The
   12-lead signal has rank exactly 8 (I, II, V1..V6), lead-confirmed in-kernel over
   50 random electrode configs and by the lead's independent rank check. A 12 x 206
   observation carries at most 8 x 206 = 1648 independent samples, not 2472, a 1.5x
   over-count on the lead axis. A diagonal Sigma_n over 12 leads treats 2472 samples
   as independent and INFLATES the Fisher information, so the waveform CRLB is too
   tight. Correct treatment: use the 8 independent leads, or a rank-deficient
   (pseudo-inverse) covariance on the 8-dim signal subspace. Precision: on the clean
   signal the redundancy is exact (rank 8); under contract B's per-displayed-lead
   white noise the DATA are full-rank but the signal Jacobian is rank-8 at the lead
   level, so the FIM over-count is finite, not infinite. This is an information
   error for the WAVEFORM CRLB only; for the FEATURE CRLB, features on redundant
   leads are a harmless modeling choice, not an error. The correction is a bounded
   factor (order 12/8), NOT orders of magnitude, so it does not by itself overturn
   the summary-statistic reading, but the headline waveform CRLB must be recomputed
   on the 8 independent leads.

2. **P0-2 (is ECG noise white?): no; the white lead-independent CRLB is an
   optimistic bound, direction established, magnitude not.** Real 12-lead noise is
   baseline wander (< 0.5 Hz), powerline (narrowband 50/60 Hz), EMG (broadband but
   temporally correlated), and motion artifact, so it is decisively NOT white
   (strongly autocorrelated in time). It is also correlated ACROSS leads (the
   precordial leads all subtract the same WCT built from RA/LA/LL; limb leads share
   electrodes). Under correlated noise the effective sample size collapses (AR(1):
   N_eff = N(1-rho)/(1+rho); lead-confirmed in-kernel that N_eff and the exact
   mean-estimation FIM both fall sharply with rho, e.g. to ~5% of N at rho 0.9). No
   sourced number exists for the project's real spectrum, so the honest fallback
   ships: the waveform CRLB is computed under a white, lead-independent noise model
   and is therefore an optimistic bound (a lower bound on achievable variance that
   is itself too low); the DIRECTION of the bias is established (looser true CRLB),
   its MAGNITUDE is not. P0-1 is one specific, exact source of this broader optimism.

3. **P0-3 (classify the 15 features, at class level; enumeration BOUNDED): timing
   conclusions transfer to a bounded forward, the one amplitude conclusion does
   not.** Contract B already types features into AMPLITUDE (mV, sigma 0.05 mV) vs
   TIMING (ms, sigma 5 ms). Under the Batch-6 differential distortion, amplitude
   features carry a systematic lead-dependent bias that peak normalization does NOT
   absorb; timing features are robust to a per-lead gain. Stated plainly:
   init_length_rv is identifiable (~0.63) because it rides early V1-V2 forces, a
   NEAR-FIELD PRECORDIAL AMPLITUDE feature, exactly the class most distorted by the
   unbounded forward, so it is the identifiability conclusion MOST at risk of not
   transferring to a bounded torso forward. delta_IV (interlead timing) and cv_myo
   (QRS duration) transfer; cv transfers modulo its cv_myo degeneracy; branch_angle
   and w are diffuse regardless. The exact 15-feature-to-class mapping and the
   per-class counts are BOUNDED pending Code's list.

4. **P1 (summary-statistic information loss): the raw-FIM-vs-summary-FIM comparison
   IS a named diagnostic.** It is the Fisher-information form of the sufficiency /
   data-processing inequality: I_S(theta) <= I_X(theta) with equality iff the
   summary S is sufficient (Zamir 1998 for the Fisher-matrix version; Cover-Thomas
   for the DPI). The positive-semidefinite gap I_X - I_S is the Fisher information
   LOST by summarizing, and per parameter it is the ratio of the two CRLBs. The
   project computed this object by accident: the < 0.5% waveform CRLB vs the diffuse
   feature contraction is a quantitative statement that the hand-crafted feature
   vector is INSUFFICIENT for branch_angle, w, init_length_lv, not that the ECG
   lacks the information. Foundational construction of an information-preserving
   summary: semi-automatic ABC (Fearnhead and Prangle 2012, the posterior mean is
   the optimal summary under quadratic loss); modern fix: learned neural summaries
   (Chen et al. 2020; Wiqvist et al. 2019; the sbi embedding net). A waveform-trained
   NPE with an embedding net is the learned-summary answer. Bounded search found NO
   prior report of an identifiability VERDICT flip between summaries and raw data;
   the project would be a cleanly demonstrated instance of a known-in-principle
   phenomenon. State as bounded, do NOT overclaim novelty.

5. **P1-2: two pre-registered falsifiable predictions added** (falsification_update_batch7.md),
   each written as a prediction with mechanism, confirm, and falsify criteria: (1)
   under a bounded torso forward, init_length_rv degrades more than delta_IV or
   cv_myo (amplitude vs timing); (2) under a correlated non-white noise covariance,
   the waveform CRLB loosens and the features-vs-waveform gap narrows. Both sharpen
   symmetric Batch-6 falsifiers into directional, signed form; neither supersedes a
   Batch-6 item.

## Track: ECG signal, lead redundancy + noise (P0-1, P0-2)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B7S-01 | Kligfield 2007 is the AHA/ACC/HRS Part I ECG standardization statement; reviews lead placement, recording methods, waveform presentation | PubMed metadata + abstract, PMID 17322457, Circulation, DOI 10.1161/CIRCULATIONAHA.106.180200 | VERIFIED at abstract/metadata |
| L-B7S-02 | III = II - I (Einthoven's law) | Standard definition, verified by exact algebra in-kernel (np.isclose True) | ASSERTED-standard, VERIFIED-by-computation |
| L-B7S-03 | aVR = -(I+II)/2, aVL = I - II/2, aVF = II - I/2 | Standard Goldberger definitions, verified by exact algebra in-kernel (all np.isclose True) | ASSERTED-standard, VERIFIED-by-computation |
| L-B7S-04 | WCT = (RA+LA+LL)/3, V_i = phi_i - WCT | Standard Wilson central terminal definition | ASSERTED-standard |
| L-B7S-05 | Of 12 leads exactly 8 are linearly independent (I, II, V1..V6); rank of 12-lead signal matrix is 8 | In-kernel matrix rank over 50 random electrode configs (rank 8; 8-lead subset also rank 8) | VERIFIED-by-computation |
| L-B7S-06 | 12 x 206 = 2472 observation carries at most 8 x 206 = 1648 independent samples | Arithmetic from rank-8 lead structure | VERIFIED-by-computation |
| L-B7S-07 | Diagonal Sigma_n over 12 leads inflates the FIM and makes the waveform CRLB optimistic | FIM algebra J = G^T Sigma_n^-1 G with rank-8 G lead structure vs full-rank diagonal Sigma_n | VERIFIED (analytic), inflation factor BOUNDED not exact |
| L-B7S-08 | Redundancy is exact on clean signal but finite (not infinite) under per-displayed-lead white noise (contract B) | Rank argument on signal vs noise covariance; contract B adds noise per displayed lead | VERIFIED (analytic) |
| L-B7S-09 | Redundancy is an information error for the waveform CRLB but only a modeling choice for the feature CRLB | Likelihood mis-specification (diagonal over 12) vs redundant feature selection | VERIFIED (analytic) |
| L-B7S-10 | ECG noise sources are EMG, 60 Hz powerline, baseline drift (respiration), baseline shift, composite | Friesen 1990 abstract, PMID 2303275, IEEE TBME, DOI 10.1109/10.43620 | VERIFIED at abstract |
| L-B7S-11 | These are distinct colored/narrowband processes, treated separately (not a single white process) | Friesen 1990 abstract (five synthesized noise types) | VERIFIED at abstract |
| L-B7S-12 | Baseline wander below ~0.5 Hz; powerline narrowband 50/60 Hz; EMG broadband colored | ECG signal-processing standard (Sornmo and Laguna 2005); AHA bandwidth context in Kligfield 2007 abstract | ASSERTED-standard; Kligfield covers recording/DSP VERIFIED at abstract, numeric cutoffs NOT string-checked |
| L-B7S-13 | Narrowband/low-frequency noise has long temporal autocorrelation; ECG noise is not white | Spectral/autocorrelation reasoning from the sourced taxonomy | VERIFIED (analytic) from sourced taxonomy |
| L-B7S-14 | Precordial leads share the WCT = (RA+LA+LL)/3, so their noise is cross-lead correlated | WCT construction from P0-1 (verified lead definitions) | VERIFIED (analytic) from P0-1 |
| L-B7S-15 | Limb leads share RA/LA/LL electrodes, so limb-lead noise is cross-lead correlated | Lead construction from P0-1 | VERIFIED (analytic) from P0-1 |
| L-B7S-16 | N_eff = N(1-rho)/(1+rho) [AR(1)]; N_eff = N/(2 tau_int); N_eff = (sum lambda)^2 / sum lambda^2 [participation ratio] | Standard effective-sample-size / autocorrelation-time results | ASSERTED-standard, given as BOUNDED direction (no number) |
| L-B7S-17 | White + lead-independent overstates information; true CRLB is looser (larger variance floor) | Fisher information over-counting under correlated noise | VERIFIED (analytic), magnitude BOUNDED not established |

## Track: Feature classification (P0-3)

| ID | Claim | Source checked | Result |
|---|---|---|---|
| L-B7F-01 | Contract B splits engineered features into amplitude (mV, sigma 0.05 mV) and timing/duration (ms, sigma 5 ms) types | contract_b_OBSERVATION_MODEL.md section 1a (read this batch, version_id 8da74a92-3bb2-491a-9e66-2c2e233ada83) | VERIFIED at artifact |
| L-B7F-02 | Feature set membership (exact 15 features and per-feature type) is an OPEN decision needing Code's list | contract_b_OBSERVATION_MODEL.md section 4 item 1 (read this batch) | VERIFIED at artifact; exact 15-to-class mapping BOUNDED |
| L-B7F-03 | delta_IV rides interlead/interventricular timing; cv_myo rides QRS duration; init_length_rv rides early V1 to V2 R amplitude; cv rides global QRS timing; branch_angle and w are interaction-dominated | parameter_to_feature_map.md map table and per-parameter account (read this batch, version_id a58b7ebb-e52a-4ddb-a536-cc177bf0073e) | VERIFIED at artifact |
| L-B7F-04 | Unbounded 1/|r| pseudo-ECG amplitude deficit is DIFFERENTIAL (lead-dependent, distance-accentuated), so peak normalization does not absorb it and cross-lead amplitude features carry a lead-dependent bias | Batch-6 differential_distortion_note.md (version_id 0e341fa2-1ba5-48bd-b868-df0157b2524a); Bishop and Plank 2011 PMID 21536529 verified full text prior batch | VERIFIED at artifact / reused verified anchor |
| L-B7F-05 | A per-lead multiplicative amplitude gain does not move a zero-crossing time, onset, offset, duration, or interlead delay | Reasoned from definition of timing features (time coordinate invariant under voltage scaling) | ASSERTED (elementary invariance argument) |
| L-B7F-06 | init_length_rv identifiability (~0.63) rests on a near-field precordial AMPLITUDE feature and is the conclusion most at risk of not transferring to a bounded forward | Synthesis: parameter_to_feature_map.md plus Batch-6 differential distortion plus Bishop and Plank 2011 distance-accentuation | ASSERTED (reasoned, anchored on two verified artifacts and one verified primary source) |
| L-B7F-07 | SIGN of the precordial-versus-limb amplitude distortion ordering under a bounded torso forward | Batch-6 note leaves it open (near-field vs small-bath measurement disagree; torso case open) | BOUNDED (direction not established) |
| L-B7F-08 | Count of the 15 engineered features falling in each class | Not enumerated in either artifact | BOUNDED (needs Code's list) |

## Track: Summary-statistic framing + falsification (P1, P1-2)

| ID | Claim | Source checked | Result |
|---|---|---|---|
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
| L-B7M-12 | No prior report of an identifiability VERDICT flip between summaries and raw data | arXiv 3 framings + PubMed 1 query, abstracts only, OpenAlex unavailable | BOUNDED-NULL: none found in this bounded search |
| L-B7M-13 | init_length_rv rides amplitude feature; delta_IV and cv_myo ride timing features | feature_classification_note.md (P0-3), internal | VERIFIED internally |
| L-B7M-14 | Unbounded pseudo-ECG under-estimates amplitude, deficit distance-dependent hence lead-differential | Bishop and Plank 2011, PMID 21536529, full text (prior batch) | VERIFIED at full text (reused) |
| L-B7M-15 | Amplitude deficit is differential not uniform, not absorbed by peak normalization | differential_distortion_note.md (Batch-6 P0-3), version 0e341fa2 | VERIFIED internally |
| L-B7M-16 | Gaussian-noise FIM is J^T Sigma^-1 J; correlated Sigma reduces effective information vs diagonal with same marginals | standard linear-Gaussian information formula | VERIFIED as standard statement |
| L-B7M-17 | Prediction 1 outcome (init_length_rv degrades more than delta_IV/cv_myo under bounded forward) | forward reasoning; bounded-forward run NOT executed | ASSERTED (pre-registered prediction, not yet tested) |
| L-B7M-18 | Prediction 2 outcome (correlated noise loosens waveform CRLB and narrows the gap) | forward reasoning; correlated-noise recomputation NOT executed | ASSERTED (pre-registered prediction, not yet tested) |

## Lead's independent verification (this session)

- Reproduced the P0-1 lead-redundancy arithmetic in-kernel
  (lead_redundancy_noise_crosscheck.md): the 12x8 lead-derivation matrix has rank
  exactly 8, all Einthoven/Goldberger consistency identities hold (I - II + III = 0;
  aVR + aVL + aVF = 0; aVL = (I - III)/2; aVF = (II + III)/2), and 12 x 206 = 2472
  samples carry at most 8 x 206 = 1648 independent numbers (over-count factor 1.5).
- Reproduced the P0-2 effective-sample-size direction in-kernel: AR(1)
  N_eff = N(1-rho)/(1+rho) and the exact mean-estimation FIM = 1^T Sigma^{-1} 1 both
  fall sharply with rho and agree (info ratio ~0.057 at rho 0.9), confirming
  correlated noise loosens the CRLB.
- Independently re-verified every P1 citation singly at source this session: arXiv
  (arxiv_get_papers, title + author block) for Fearnhead-Prangle 1004.1112,
  Drovandi-Frazier 2103.02407, Chen et al. 2010.10079, Wiqvist et al. 1901.10230,
  Cranmer-Brehmer-Louppe 1911.01429; Crossref (from the python kernel, since Crossref
  is blocked from the repl kernel) for Zamir 1998 (IEEE Trans Inf Theory 44(3):1246
  to 1250) and the Fearnhead-Prangle published version (JRSS-B 74(3):419 to 474,
  2012); PubMed for Schaelte and Hasenauer 2023 (PLoS One,
  10.1371/journal.pone.0285836). Kligfield 2007 (PMID 17322457) reused from prior
  verification.

## Consolidated bounded-claim register

### ECG signal
- Waveform CRLB FIM inflation factor from lead redundancy: DIRECTION established (over-counted, bound too tight), MAGNITUDE bounded (order 12/8 in counted channels, not a single exact scalar; depends on per-parameter sensitivity of I/II vs precordial leads).
- Effective sample size N_eff under correlated ECG noise: FORM and DIRECTION established (N_eff < N via AR(1), integrated-autocorrelation, or participation-ratio forms), NUMBER not computable here (no project noise spectrum: rho, tau_int, Sigma_n eigenvalues unavailable).
- Overall white+lead-independent waveform CRLB optimism: DIRECTION established (true CRLB looser), MAGNITUDE not established. Honest fallback shipped verbatim.
- Kligfield 2007 numeric noise/bandwidth cutoffs: NOT string-checked in the body; abstract-level VERIFICATION only that it covers recording methods and digital signal processing. Bandwidth numbers ASSERTED-standard.
- Sign/exact value of derived-lead redundancy under contract B noise: on clean signal EXACT (rank 8); under per-displayed-lead white noise the over-count is FINITE not infinite (bounded by added per-lead noise level, not quantified to a number).

### Feature classification
- Exact 15-item feature enumeration and per-feature amplitude/timing labels are BOUNDED: the vector lives in Code's repo, contract B section 4 still lists feature-set membership as OPEN.
- Count of the 15 features in each class is BOUNDED (not licensed by map or contract).
- SIGN/direction of precordial-vs-limb amplitude distortion under a bounded torso forward is BOUNDED (Batch-6 leaves it open); only the DIFFERENTIAL nature is asserted.
- Per-FEATURE exposure verdict is BOUNDED pending Code's list: ratio/normalized-amplitude features or amplitude-threshold-defined timing features could deviate from the per-class default.

### Summary-statistic framing
- BOUNDED-NULL: no prior report of an identifiability-verdict flip between summaries and raw data found (3 arXiv framings + 1 PubMed query, abstracts only, OpenAlex citation graph unavailable). None found is not none exists; the absence is a bounded result supporting a cautious 'clean instance of a known-in-principle phenomenon' claim, NOT a novelty claim.
- Zamir 1998 Fisher information inequality VERIFIED at metadata only (author/title/venue/vol/issue/page/year via Crossref); the proof body was not re-derived.
- sbi embedding-network claim ASSERTED as standard practice/documentation, not re-fetched at a primary methods paper; load-bearing learned-summary primaries are Chen 2020 and Wiqvist 2019.
- Information-loss reading (equality iff sufficiency) is conditional on the assumed white sigma=0.025 mV waveform noise model; the <0.5% figure is an OPTIMISTIC bound, so the true waveform-vs-feature information gap is at most the reported one (this is exactly Prediction 2).
- Prediction 1 and Prediction 2 are pre-registered predictions, ASSERTED and not yet tested; their confirm/falsify criteria are fixed in advance of the runs.
- Sign of the precordial-vs-limb amplitude bias remains an open (bounded) item from Batch-6 P0-3; Prediction 1 is scoped to relative amplitude-vs-timing degradation, which does not depend on that sign.

## Batch 8b


Reconciliation only, no new experiments. Grades: VERIFIED (checked at source or
recomputed in-kernel this batch), BOUNDED (true within a stated scope or pending
a named artifact/run), ASSERTED (would be an unsupported claim; none used).
Numbers labeled "task-provided" are the Lane A results supplied in the batch note
and reused as given; the ground-truth repo files (crlb_comparison.json,
results-summary.md, emit.py, f3_contraction_vs_n.json) are not in this workspace,
so they are reconciled against the project's own reporting convention, not
re-read from source. Cross-check parser: ' | ' split; all cells dash-free.

| ID | Claim | Evidence | Grade |
|---|---|---|---|
| L-B8b-01 | The reported condition number 18.3 and "waveform CRLB < 0.5% of prior range for all 7" are the EXISTING 12-DISPLAYED-lead figures, which the project's own lead-redundancy result flags as optimistic (rank-8 over-count, factor ~12/8). The corrected 8-independent-lead (I, II, V1-V6) waveform CRLB is looser but has NOT been recomputed; it is a pending retrain. Only the CRLB-to-CRLB ratios (which cancel common waveform scaling) are robust to the pending correction; the absolute 18.3 and <0.5% must stay labeled as uncorrected 12-lead until Code runs the retrain | lead_redundancy_note.md lines 145-150 ("8-lead waveform CRLB is looser"; "headline waveform CRLB must be recomputed on the 8 independent leads before it can be trusted"); CHECKLIST.md lines 24-25 (8-lead retrain not-yet-landed); condition number 18.3 and <0.5% from manuscript.md line 250 / batch7_SUMMARY (12-lead) | BOUNDED (absolute figures are uncorrected 12-lead, correction pending; ratios robust) |
| L-B8b-02 | crlb_features exists for all 7 params, params_dropped = 0; timing features mapped 5 ms -> window fraction via fs = 500 Hz, sigma_feature_time_frac ~ 0.0121 | Task note (crlb_comparison.json); arithmetic 5 ms x 500 Hz = 2.5 samples / 206-sample window = 0.01214 recomputed in-kernel this batch | VERIFIED for the arithmetic; BOUNDED-task-provided for the json contents (artifact not in workspace) |
| L-B8b-03 | Per-parameter CRLB-to-CRLB ratio features/waveform (as computed in crlb_comparison.json; lead basis of that file not confirmed here): cv 70x, cv_myo 64x, init_length_rv 48x, w 43x, branch_angle 33x, delta_iv 32x, init_length_lv 21x; it is a Fisher data-processing/sufficiency ratio (I_S <= I_X, Zamir 1998), never CRLB-to-contraction | Ratios task-provided (crlb_comparison.json); sufficiency framing verified at source Batch 7 (summary_statistic_framing_note, Zamir 1998 DOI 10.1109/18.669301) | BOUNDED (ratios task-provided) + VERIFIED (framing/citation) |
| L-B8b-04 | Feature loss is roughly uniform (21x-70x) and does NOT order by block: lowest loss on diffuse init_length_lv (21x), highest on identifiable cv (70x); delta_iv (ident) and branch_angle (diffuse) nearly equal (32x vs 33x). Overturns frozen line 62 "diffuse block is feature-limited" | Sorted the ratios in-kernel this batch; block labels from contraction spectrum (parameter_to_feature_map.md, batch7_SUMMARY.md) | VERIFIED (ordering computed from the task-provided ratios) |
| L-B8b-05 | Units pivot: crlb_features[branch_angle] = 0.012 is 1.2% of prior range (H_norm, project convention) or 6% (H_raw, 0.012 rad / 0.2 rad range). Taking crlb_features directly, the gap to the NPE contraction (~105% of prior) is 105/1.2 = 88x (H_norm) or 105/6 = 18x (H_raw); under EITHER the feature channel over-determines branch_angle at the reference point by more than an order of magnitude, so it is NOT feature-limited regardless of units. (The "gap to local bound" table uses a more conservative >6x lower bound = 105/16.5, from the ratio x <0.5% waveform upper bound, not crlb_features directly.) | Both conventions and both gaps computed in-kernel this batch against prior range 0.2 rad (contract_a_parameter_ranges.csv): 105/1.2=87.5x, 105/6=17.5x, 105/16.5=6.4x. Project reports CRLB as fraction of prior range ("< 0.5% of prior range", batch7_SUMMARY / summary_statistic_framing / lead_redundancy_note) | VERIFIED (both gaps recomputed in-kernel; convention-independence holds, gap is order-of-magnitude, not 6x-9x). One-line repo check named for Code to confirm the crlb_features normalization |
| L-B8b-06 | The single-point feature CRLB rules out (a) feature-insufficiency-at-reference for the diffuse block (gap 5x-9x to local bound) but cannot separate (b) estimator/budget limit from (c) prior-averaging (local tight, box-averaged diffuse); parallels L-B6E for the waveform FIM | Gap factors computed in-kernel (contraction / (ratio x 0.5%)); coexistence of tight local CRLB and diffuse contraction established at L-B6E (fim_vs_posterior_note) | VERIFIED (arithmetic) + BOUNDED (b vs c undecided by single-point CRLB, by construction) |
| L-B8b-07 | F3 three-seed: init_length_lv tightens 1.248 -> 1.010, trend 0.238 > seed spread 0.183, suggesting estimator/budget limit (reading b); disjoint SBC set, 3 seeds, post-conformal, N <= 4000, suggestive not decisive. branch_angle and w show no comparable N-response; data cannot yet decide b vs c for them | Task note (F3 run). Contradicts frozen "diffuse block does not respond to data at all" | BOUNDED (suggestive; measurement caveats) and BOUNDED-pending-artifact (f3_contraction_vs_n.json fails to parse, see L-B8b-09) |
| L-B8b-08 | Ratios are computed under the white lead-independent noise model; a correlated/heavier waveform noise shrinks the waveform FIM, so the reported feature-to-waveform ratios are an OPTIMISTIC (upper) bound; direction established, magnitude not | falsification prediction 2 (falsification_update_batch7.md); ecg_noise_model_note P0-2 (N_eff collapse under AR(1), verified in-kernel Batch 7) | VERIFIED (direction) + BOUNDED (magnitude unsourced) |
| L-B8b-09 | Mechanical blocker: f3_contraction_vs_n.json does not parse (JSON error ~line 216, likely NaN/truncation). The init_length_lv F3 point is quoted from the task note, not re-read; flagged for Code to verify/regenerate, not fixed here | Task note; artifact not present in workspace to re-parse | BOUNDED (flagged, not fixed; eikonal owns CPU, no run performed) |

## Noise-floor statement (attached to every identifiability claim)

Every identifiability claim in the rewritten section names its noise floor in the
same sentence: the waveform channel is white Gaussian, sigma = 0.025 mV per sample
per lead, applied before feature extraction (the absolute waveform CRLB is the
uncorrected 12-lead figure; the 8-independent-lead correction is pending, see
L-B8b-01). The
feature channel floor is amplitude sigma = 0.05 mV and timing sigma = 5 ms
(mapped to sigma_feature_time_frac ~ 0.0121 at fs = 500 Hz).

## What was NOT done (reconciliation discipline)

- No new experiments run. f3_contraction_vs_n.json not regenerated (flagged for
  Code; the eikonal owns the CPU).
- No repo edit. Deliverables are drop-in section/edit text plus this ledger,
  staged for review before promotion into docs/.
- CRLB never conflated with contraction; every comparison of the two is labeled
  CRLB-to-contraction and used only to locate the binding constraint, never to
  claim one bounds the other. No correlation called a degeneracy.

## Retractions (claims the project refuted itself)


This ledger is the formal record of four project claims that the project itself later refuted. Each row
carries a stable ID (R-01 to R-04), the date the retraction was recorded, a status, the original claim
stated verbatim, the specific internal evidence (artifact or code) that killed it, and the consequence for
the claim.

## Why this ledger is part of the methods contribution

The scientific deliverable is an identifiability characterization. The methods contribution is the process
that produced it: calibrated Neural Posterior Estimation, verify at source, and a retraction ledger. A
project that names its own wrong claims with stable IDs, dates, and the killing artifact is demonstrating
that its claims are checkable and were in fact checked. Each row below was overturned by an internal
artifact or a line of the project's own code, not by an appeal to authority or to memory. This ledger is
therefore the strongest single piece of evidence that the project's claims are falsifiable and were
falsified where they were wrong. The retractions are not an embarrassment to be hidden in an appendix; they
are the demonstration that the checking machinery works.

Scope note: every killing item below is INTERNAL to the project (a project artifact or a line of project
code). None of these retractions rests on a literature claim, so none was re-verified against an external
source for this ledger. The verification status recorded for each row is "VERIFIED internally (project
artifact/code)", meaning the evidence was checked in the project's own materials, not that it is a
literature-sourced fact.

## Refuted claims

| ID | Date | Status | Original claim (verbatim) | Killing evidence (internal) | Consequence |
|---|---|---|---|---|---|
| R-01 | 2026-07-09 | REFUTED | "Forward validated, corr 0.86." | The 0.86 was a best-lag correlation. Under a fixed alignment the per-lead normalized RMSE is about 1, and there is a 2.3x amplitude gap between forward output and target. The single best-lag correlation masked both. | "Validated" was not supported. A correlation after best-lag alignment is not validation: it discards timing offset and is insensitive to a large amplitude mismatch, both of which are present here. |
| R-02 | 2026-07-09 | REFUTED | "The delta_iv-cv_myo ridge is a degeneracy; the ECG constrains only a combination." | ridge_confirm recovered cv_myo at corr 0.98, so cv_myo is individually identifiable, not constrained only as a combination. The Jacobian corroborates this: the minimum-singular-value direction v_min is dominated by init_length_lv, not by a delta_iv and cv_myo combination. | The claimed degeneracy was misattributed. The near-null direction of the forward is along init_length_lv, so calling the delta_iv, cv_myo pair the degenerate combination pointed at the wrong parameters. |
| R-03 | 2026-07-09 | REFUTED | "The forward diverges from a real ECG." | Reading the fixture shows True_ecg is pickled SIMULATOR output used as a regression target. There is no real ECG anywhere in the project, so "divergence from a real ECG" has no referent. The transplant corr 1.000 is a tautology, since the same operator is used forward and inverse. | The claim was a category error about what True_ecg is. With no real ECG in the project, no statement comparing the forward to a real ECG can be made, and the perfect transplant correlation reflects operator self-consistency, not agreement with any measurement. |
| R-04 | 2026-07-09 | REFUTED | "The joint posterior is near-calibrated (TARP ATC -0.072)." | src/npe/emit.py line 226: the TARP ATC number is computed PRE-CONFORMAL. It describes the posterior BEFORE recalibration, not the calibrated joint posterior. | The "near-calibrated" claim was about the wrong object. The reported ATC characterizes the raw flow output, so it cannot be cited as evidence that the calibrated (post-conformal) joint posterior is near-calibrated. |

## Closing note

These four corrections are, together, the methods contribution in concrete form. The identifiability result
survives because the claims around it were tested and the ones that failed were withdrawn with a dated,
identified, artifact-backed record. A reader can audit any row above by opening the named artifact or code
line. That auditability is the point.

## Verification ledger (checked vs asserted)

| Claim | Source checked | Result |
|---|---|---|
| R-01: "Forward validated, corr 0.86" is refuted by per-lead nRMSE about 1 and a 2.3x amplitude gap behind a best-lag correlation | project artifacts (forward-validation diagnostics), internal | VERIFIED internally (project artifact/code), not a literature claim |
| R-02: delta_iv-cv_myo degeneracy claim is refuted by ridge_confirm (cv_myo corr 0.98) and the Jacobian (v_min dominated by init_length_lv) | project artifacts (ridge_confirm, Jacobian/FIM), internal | VERIFIED internally (project artifact/code), not a literature claim |
| R-03: "forward diverges from a real ECG" is refuted by the fixture (True_ecg is pickled simulator output; transplant corr 1.000 is a tautology) | project fixture and forward/inverse operator, internal | VERIFIED internally (project artifact/code), not a literature claim |
| R-04: TARP ATC -0.072 "near-calibrated" claim is refuted because src/npe/emit.py:226 computes it PRE-CONFORMAL | project code src/npe/emit.py line 226, internal | VERIFIED internally (project artifact/code), not a literature claim |
| This retraction ledger is part of the methods contribution (checkable, dated, artifact-backed claims) | framing statement about project process | ASSERTED (framing, internally consistent with the four rows above) |
