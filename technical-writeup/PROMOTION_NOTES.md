# Promotion notes, Jul 10

Promoted from `.claude_research/manuscript.zip` after intake. The manuscript is 15,365 words, the PDF builds, all 33 BibTeX entries carry a DOI or PMID, no cited key is missing from the bibliography, and there are zero em or en dashes.

The PDF that shipped in the zip is **not** promoted. Do not build `/paper` until the TODOs resolve; a PDF with visible `\TODO{}` is worse than a `Pending` state, and the demo page already has one for exactly this.

## Changes made during promotion (three)

**1. Removed a reintroduced degeneracy claim.** The body said `cv` and `cv_myo` "are partially degenerate," resting on `L-B3-32`, whose status is ASSERTED (a reasoned shared-channel argument). This project retracted `R-02` for calling a correlated pair degenerate on exactly that kind of argument. Reworded to a shared timing channel and a posterior correlation, with the ASSERTED status disclosed in place so the mechanism reads as an explanation rather than as evidence.

**2. Reworded ledger row `L-B3-32`** to match, and to say explicitly that it is not a degeneracy claim.

**3. Normalized 31 status cells.** `L-B7S-02` (Einthoven's law, checked by exact algebra in-kernel) carried the invented status `ASSERTED-standard, VERIFIED-by-computation`. It is VERIFIED. Lowercase `verified` and `TOKEN-qualifier` hybrids were case-normalized and converted to `TOKEN (qualifier)` mechanically.

No fourth fix was needed: the TARP sign convention already appears in the Results calibration paragraph, in the same breath as the number, not buried in the appendix. I had claimed otherwise and was wrong.

## Residual status cells, for Science to resolve. Do not guess at these.

These inherited free-form statuses from seven batch ledgers and cannot be normalized mechanically without inventing meaning:

- **`reused` (8 rows, some with qualifiers).** Does this mean VERIFIED in an earlier batch and carried forward, or carried without re-checking? Those are different statuses. Whoever wrote the row knows; nobody else does.
- **`TEXTBOOK-STANDARD, confirmed` (4 rows).** Probably BOUNDED (canonical result cited at attribution level), but say so explicitly.
- **`NOT STATED` (2), `NOT retrieved` (1).** These are BOUNDED with a specific bound. State the bound.
- **`REVERSED / not supported` (1), `REFINED` (1), `PARTLY REFUTED` (1).** Each is a real finding wearing a non-standard label. Map to REFUTED or BOUNDED, keeping the detail in parentheses.

The four-word vocabulary is the whole point. A fifth word makes the other four negotiable.

## Two structural issues, unresolved

**The ledger now exists twice.** Appendix A of the manuscript and `docs/verification-ledger.md` contain the same rows. One of them will be stale by Sunday. Either generate the appendix from the ledger file at build time, or declare the appendix canonical and make the docs file a pointer.

**The verification command in `docs/scientific-process.md` produces false positives on this manuscript.** It flags `validated` and `diverges`, but every occurrence is inside a quoted retracted claim:

```
**Claim (withdrawn original wording):** "Forward validated, corr 0.86."
```

You cannot retract a claim without quoting it. The checker must exclude lines matching `withdrawn original wording` and the ledger tables. As written, it flags the most honest paragraphs in the paper. (This is the third time this week a context-free grep of mine reported a violation where the artifact was correct. The lesson generalizes: a word list cannot distinguish an assertion from a quotation of one.)

## Outstanding TODOs (15 markers, 10 distinct)

Landing Friday: F3's contraction-versus-N curve, `CRLB_features` versus `CRLB_waveform`, pre- and post-conformal contraction, SBC KS p-values.

Possibly landing: post-conformal TARP ATC, the robustness corners.

Not landing, and the marker must be replaced with prose rather than a number: the Strocchi heart index (we ship the ingestion figure only, no identifiability result).
