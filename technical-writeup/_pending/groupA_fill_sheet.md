# Group-A TODO fill-sheet (values + sources) for Cowork

Code owns the numbers; Cowork owns the prose. Every value below is pulled from a committed
artifact (cited). The 4 Group-B TODOs (491-494) are release-gated and are NOT in here (no value
exists until the release is cut; do not manufacture a DOI). Honesty flags are called out in bold.

All identifiability numbers are at the waveform noise floor: white Gaussian sigma = 0.025 mV per
sample per lead, applied before feature extraction. Name it in-sentence wherever these land.

---

## L123 - the 15-feature vector (source: `src/core/features.py`, `FEATURE_NAMES`/`FEATURE_KINDS`)

15 features, in this exact order:
- `p2p_lead0` .. `p2p_lead11` (12): per-lead peak-to-peak amplitude (max - min over T). Units mV. kind = amp.
- `qrs_active_frac` (1): fraction of samples where the 12-lead vector magnitude exceeds 5% of its
  peak (active-window width / T). Dimensionless. kind = time.
- `vecmag_peak` (1): peak of the 12-lead root-sum-square magnitude. Units mV. kind = amp.
- `time_to_peak_frac` (1): argmax of the vector magnitude / T. Dimensionless fraction. kind = time.

Counts: **13 amp + 2 time = 15**. The two timing features are FRACTIONAL (of trace length T);
to express in ms, multiply by T. (This is why the feature-channel CRLB converts the 5 ms floor to a
fraction via T; see `experiments/jacobian_fim.py`.)

## L127 - post-conformal joint TARP ATC (source: `results.real.json` `calibration`)

- **Post-conformal joint TARP ATC = +0.0072** (joint, after per-parameter conformal).
- Pre-conformal joint TARP ATC = -0.0565.
- sbi sign convention: ATC < 0 = overconfident (too narrow). The conformal fix moves the JOINT from
  -0.0565 (overconfident) to +0.0072 (nominal, marginally conservative). The pre-conformal number
  cannot stand in for the post value.

## L128 / L332 / L478 - contraction vs training budget N (source: `outputs/f3_contraction_vs_n.json`)

Setup: features NPE, 3 seeds (0,1,2), schedule N = {1000, 4000}, disjoint calib (250) + SBC (250),
inflation fit on calib, contraction measured on SBC. `crlb_floor` = waveform CRLB expressed as a
contraction (a best-case local reference, not a target).

Post-conformal median contraction, seed spread at N = 4000, and the json's label:

| param | N=1000 | N=4000 | median trend | max seed spread | label |
|---|---|---|---|---|---|
| cv             | 0.767 | 0.491 |  0.276 | 0.210 | data-limited (still tightening) |
| delta_iv       | 0.190 | 0.147 |  0.043 | 0.029 | data-limited |
| init_length_lv | 1.248 | 1.010 |  0.238 | 0.183 | data-limited |
| init_length_rv | 0.581 | 0.413 |  0.168 | 0.159 | data-limited |
| branch_angle   | 0.976 | 1.047 | -0.072 | 0.105 | trend within seed noise |
| w              | 1.026 | 1.108 | -0.082 | 0.062 | widening (no tightening) |
| cv_myo         | 0.300 | 0.326 | -0.026 | 0.045 | trend within seed noise |

Data-level reading (not a claim): cv, delta_iv, init_length_lv, init_length_rv keep tightening as N
grows 1000 -> 4000 (trend exceeds the across-seed spread for cv and init_length_lv; comparable for
the other two), i.e. budget-responsive over this range. branch_angle, w, cv_myo do not tighten
(w slightly widens; the others' trend is within/below the seed spread), i.e. not budget-responsive
over this range.

**Flag (Cowork):** only two N points (1000, 4000). State it as a two-point trend, not a converged
curve. **Flag (pre vs post):** manuscript line 329 says "PRE-conformal contraction vs N," but the
json's verdict/labels are computed on POST-conformal medians (table above). Pick one and be
consistent; `per_seed.raw` (pre) and `per_seed.post_conformal` (post) are both in the json.

## L234 - SBC KS p-values pre/post conformal (source: `results.real.json` `calibration.sbc`)

per-param KS p-value (before -> after conformal):

| param | before | after |
|---|---|---|
| cv             | 0.031   | 0.111 |
| delta_iv       | 0.444   | 0.613 |
| init_length_lv | 0.0043  | 0.630 |
| init_length_rv | 0.055   | 0.055 |
| branch_angle   | 0.00002 | 0.023 |
| w              | 0.00035 | 0.413 |
| cv_myo         | 0.00007 | 0.150 |

Median KS p-value (after) = 0.150. Before conformal, several params fail KS at 0.05 (init_length_lv,
branch_angle, w, cv_myo; cv marginal at 0.031). After conformal all clear 0.05 except branch_angle
(0.023, still a ~1000x improvement). init_length_rv stays 0.055 (already > 0.05, inflation t = 1).

## L236 - pre/post conformal contraction (source: `results.real.json` `posterior`)

per-param contraction (pre-conformal -> post-conformal, headline single-observation run):

| param | pre | post |
|---|---|---|
| cv             | 0.559 | 0.671 |
| delta_iv       | 0.137 | 0.151 |
| init_length_lv | 0.799 | 1.039 |
| init_length_rv | 0.628 | 0.628 |
| branch_angle   | 0.804 | 1.206 |
| w              | 0.793 | 1.070 |
| cv_myo         | 0.265 | 0.345 |

Conformal inflation loosens every contraction (as it must, correcting overconfidence); the
constraint/diffuse ordering survives (cv, delta_iv, cv_myo tight; branch_angle, w, init_length_lv
near or above prior width). init_length_rv unchanged (t = 1).

## L484 - Strocchi heart index - HONESTY FLAG (Cowork reconciles the prose)

**The headline identifiability result is on crtdemo / cardiac_demo, NOT on any Strocchi heart.**
Strocchi hearts (indices 01 and 02) appear ONLY in the "method generalizes" demo; no identifiability
claim is made on them. Manuscript line 484 currently reads "All experiments use the publicly
available virtual cohort ... Strocchi", which is inaccurate. Reconcile: the identifiability study is
on crtdemo; Strocchi 01/02 are method-generality demonstrations only. Fill the "\TODO{exact Strocchi
heart index NN}" with "01 and 02 (method-generality demo only)".

---

## Additional flag (belongs with Cowork's floor-occurrence pass)

`technical-writeup/figures/fig3_contraction_vs_N.md` placeholder caption says "feature-channel noise
floor (amplitude 0.05 mV, timing 5 ms)". WRONG for F3: it was measured under the waveform 0.025 mV
floor (manuscript body line 333 already says so). Fix the fig3 caption when reconciling the four
spectrum floor occurrences (353, 442, 460, 178/181).

## Group-B (release-gated) - not fillable yet

491 sweep location, 492 checkpoint location, 493 container digest, 494 calibration-artifacts
location. Fill with the GitHub release URL + tag + image digest once the release is cut. Soften the
manuscript's "DOI" to "release URL/tag"; a Zenodo DOI is future work, not manufactured this weekend.
