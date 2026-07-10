# CHECKLIST.md

Status ledger for the Batch-8 technical manuscript (manuscript.md). Three parts:
open TODOs (numbers not yet measured), superseded framings reconciled with the
newer-ledger-row-wins rule, and claims still marked BOUNDED. Markdown is the
source of truth; the PDF is a rendering.

## 1. Open TODOs (\TODO{} markers in manuscript.md)

These are numbers or artifacts not yet measured or not yet released. They are
marked \TODO{} in the source and must be filled before the manuscript is final.
None was invented.

### Landing Friday (per the task note)
- F3 contraction-versus-N curve (Section 4.5, and the FIM-versus-posterior
  resolver in Section 7). \TODO{F3 contraction-vs-N curve, landing Friday}
- CRLB_features versus CRLB_waveform, the CRLB-to-CRLB sufficiency comparison
  (Section 4.4): LANDED. Feature CRLB looser than the 8-independent-lead waveform
  CRLB for every parameter (about 21x to 70x; outputs/crlb_comparison.json).

### Possibly landing (per the task note)
- Post-conformal joint TARP value on the calibrated posterior (Sections 4.2, 6):
  LANDED. Matched sample sets, pre-conformal ATC about -0.057 to post-conformal
  about +0.007; the pre-conformal number alone cannot stand in for it (R-04).
- SBC KS p-values pre and post conformal (Section 4.2). \TODO{SBC KS p-values pre and post conformal}
- Pre- and post-conformal per-parameter contraction (Section 4.2). \TODO{pre- and post-conformal contraction}
- The corrected 8-lead noise retrain is referenced as not-yet-landed in Section 6
  (lead-redundancy limitation).

### Reproducibility-bundle identifiers (Section 8)
- Exact Strocchi heart index NN used. \TODO{exact Strocchi heart index NN used}
- Released sweep dataset location and DOI. \TODO{released sweep dataset location and DOI}
- Released NPE checkpoint location and DOI. \TODO{released NPE checkpoint location and DOI}
- Released container image reference and digest. \TODO{released container image reference and digest}
- Released post-conformal calibration artifacts. \TODO{released post-conformal calibration artifacts}

### Not landing at all (per the task note), marked as method generality only
- The exact 15-feature engineered vector with per-feature amplitude/timing type
  lives in Code's feature-extraction module and is not in any accessible project
  artifact (contract_b_OBSERVATION_MODEL section 4 still lists feature-set
  membership as an OPEN decision). Section 3.5 gives the class-level typing
  (amplitude = mV peak/wave voltages; timing = ms durations/delays) and marks the
  enumeration \TODO{publish the exact 15-feature vector ...}. The per-class count
  is BOUNDED pending that list. This was confirmed with the user, who directed
  proceeding on the map's feature classes with the enumeration BOUNDED.
- No Strocchi identifiability result (Section 4.7 is method generality only).

## 2. Superseded framings reconciled (newer ledger row wins)

The source material was written across five days; the following framings were
superseded and the manuscript uses the newer version. Each disagreement is a line
here per the task rule.

- "Forward validated, corr 0.86" (early framing) is SUPERSEDED and formally
  retracted (R-01). The manuscript never states the forward is validated; the
  banned word "validated" appears only inside the R-01 withdrawn-wording row.
- "delta_IV-cv_myo ridge is a degeneracy" (early framing) is SUPERSEDED and
  retracted (R-02); the near-null direction is along init_length_lv, and cv_myo is
  individually recoverable (corr 0.98). The manuscript uses the R-02 version.
- "the forward diverges from a real ECG" (early framing) is SUPERSEDED and
  retracted (R-03). There is no measured ECG anywhere in the project; True_ecg is
  a simulator fixture and the transplant correlation of 1.000 is a tautology. The
  banned phrase appears only inside the R-03 withdrawn-wording row.
- "joint posterior is near-calibrated (TARP ATC -0.072)" (early framing) is
  SUPERSEDED and retracted (R-04); that ATC is pre-conformal and describes the raw
  flow output, not the calibrated joint posterior. Post-conformal TARP now landed:
  the matched pre/post pair is about -0.057 to about +0.007.
- "lead field" language from earlier batch notes (e.g. the Strocchi ECG-setup
  note) is SUPERSEDED: the forward is named a pseudo-ECG in an unbounded
  homogeneous volume conductor throughout, never a lead field. Two Appendix-A
  ledger rows that originally used "lead field" (a B2 row describing MedalCare's
  precomputed operators, and a B3 row on fixed electrode geometry) were reworded
  in the manuscript appendix to "source-to-electrode transfer operators" and
  "fixed electrode geometry" respectively, to honor the absolute ban; the internal
  batch ledgers retain their original wording.
- TARP ATC sign: earlier framing labelled ATC -0.072 "mildly conservative." That
  label is OURS, not Lemos's; Lemos 2023 uses neither the token ATC nor
  "conservative." The manuscript states the sign convention as the sbi
  implementation's (negative ATC = underdispersed = overconfident) and does not
  attribute it to Lemos. The ATC sign remains a code question, not resolvable at
  the paper.
- Contraction spectrum was reported in different batches with minor value drift;
  the manuscript uses delta_IV ~0.15 > cv_myo ~0.35 > init_length_rv ~0.63 >
  cv ~0.67 >> branch_angle, w, init_length_lv ~1.0 to 1.2, all against the
  feature-channel noise floor (amplitude sigma 0.05 mV, timing sigma 5 ms), the
  value set carried in the newest parameter_to_feature and fim_vs_posterior notes.

## 3. Claims still marked BOUNDED

23 Appendix-A ledger rows carry BOUNDED status. The load-bearing ones in the body:

- The lead-redundancy Fisher-information inflation is a BOUNDED factor (order 12/8
  in the counted-channel sense), direction exact, magnitude bounded not exact
  (Section 3.4, 6; L-B7S).
- The white-noise waveform CRLB is optimistic: direction established (true CRLB is
  looser), MAGNITUDE not established (no real noise spectrum) (Section 3.4, 6; L-B7S).
- init_length_rv is the conclusion most at risk of not transferring to a bounded
  torso forward; the SIGN of the precordial-versus-limb amplitude bias is NOT
  established (Section 6, Prediction 1; L-B7F, bounded).
- The per-lead amplitude decomposition behind the 1.4 mV operating point is
  consistent with the normal-limits text but the exact per-lead percentiles were
  string-checked from a supplement in a prior batch (Section 3.2; L-B ledger).
- No published work computes a 12-lead ECG directly from a Strocchi cohort mesh;
  the ingestion route is "method after the cohort group, applied to the cohort
  mesh" (Section 4.7; L-B4).
- The calibration bounded-negative (no cardiac-conduction SBI paper reports
  SBC/coverage/TARP) is bounded by an incomplete citation-graph search (OpenAlex
  forward-citation traversal was unavailable) (Section 2.4).

## 4. Citation and build notes

- refs.bib: 33 entries, every one carries a DOI. All 33 verified singly at source
  (arxiv_get_papers author blocks for the arXiv preprints; PubMed +
  Crossref for the journal entries; Crossref for coverthomas2006, DOI
  10.1002/047174882X confirmed as Cover and Thomas, Elements of Information
  Theory, Wiley). Note: sahlicostabal2015 is cited by the label "2015" in the text
  but Crossref records the DOI's publication year as 2016 (J Biomech vol 49); the
  bib entry uses 2016. coverthomas2006 uses the key label "2006" but the 2nd-ed
  DOI's Crossref year is 2005; the bib entry uses 2005. These are edition/label
  nuances, not citation errors; both DOIs resolve to the correct works.
- Toolchain: pandoc 3.10 with the typst 0.15 PDF engine (no LaTeX, no network at
  render time). The Makefile invocation renders technical-writeup.pdf. The
  vancouver.csl was fetched from zotero.org and patched in two places
  (page-range-delimiter and citation-number collapse) so the RENDERED bibliography
  and collapsed citation ranges use plain hyphens, keeping even the PDF free of
  en/em dashes.
- Two referenced repo docs, docs/results-summary.md and docs/scientific-process.md,
  are NOT in the accessible artifact store; their content was reconstructed from
  the batch deliverables and ledgers. Flag for Code: reconcile the manuscript
  against those two docs when promoting to technical-writeup/.

## 5. Compliance sweep results (run in-kernel on manuscript.md)

- em/en/figure/hyphen/non-breaking-hyphen dashes: 0 in source, 0 in rendered PDF.
- Banned words: "validated" and "diverges from a real ECG" appear only inside the
  R-01/R-03 withdrawn-wording rows (as required); "solved", "unknowable", and
  "lead field" appear 0 times.
- "ASSERTED" as a live claim status: 0 in the body (Sections 1 to 8); it appears
  only in the Appendix-A verification-ledger status column, which preserves each
  row's historical status word for auditability.
- Every factual claim in the body carries a ledger ID (82 L-B references, 19 R-0n
  references in Sections 1 to 8).
- Every identifiability sentence that states a contraction number names its noise
  floor in the same sentence: 0 violations found.
- Every refs.bib key is cited; every citation resolves (31 keys cited, 0
  unresolved markers in the citeproc render).
