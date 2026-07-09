# Sources of truth, and how a claim becomes one

This project runs three Claude lanes (Science, Code, Cowork/orchestration) plus a human director. All three write. Without a promotion rule, three lanes produce three truths. This document is the rule.

We have already been bitten twice. A "forward model validated, corr 0.86" claim reached a doc before anyone checked that best-lag correlation was hiding a per-lead nRMSE near 1. A "cv_myo is entangled, the ECG only constrains a combination" headline reached a doc before `ridge_confirm` ran and refuted it. Both were caught, both were retracted. Neither should have gotten that far.

## 1. One public location

`docs/` is the only place truth lives. Everything else is a **working note**: useful, disposable, never citable.

| Kind | Location | Public | Citable as truth |
|---|---|---|---|
| Canonical docs | `docs/` | yes | yes |
| Science working notes | `.claude_research/` | no (gitignored) | no |
| Orchestration notes, state log | `.localagent/` | no (gitignored) | no |
| Compute artifacts | `outputs/`, `runs/` | no (released separately) | yes, as data |

Working notes are gitignored on purpose: they contain internal strategy and half-formed reasoning. They are never promoted wholesale. Only distilled, verified content crosses into `docs/`.

## 2. One fact class, one home, one owner

If a number appears in two documents, one of them is a copy and will drift. Copies link, they do not restate.

| Fact class | Source of truth | Owner | Gate before it changes |
|---|---|---|---|
| Problem, method, prior art | `docs/research-brief.md` | Science | critic |
| Findings and numbers | `docs/results-summary.md` | Science + Code | critic |
| Interfaces (Contracts A/B/C/D) | `docs/contracts.md` | Code | director (frozen) |
| How the system works | `docs/architecture.md` | Code | none |
| Prior-art detail | `docs/related-work.md` | Science | critic |
| Claim provenance | `docs/verification-ledger.md` | Science | it IS the gate |
| Design surfaces | `docs/design-system.md`, `docs/heart-viewer-spec.md` | Design | none |
| Priors, observation model | folded into `docs/research-brief.md` | Science | critic |

`docs/results-summary.md` owns every reported number. The architecture doc describes machinery, never results. That separation is deliberate: results and architecture rot at different rates and answer to different reviewers.

## 3. Status vocabulary (use these words, only these)

Every factual claim carries one status, in the ledger:

- **VERIFIED**: read at the primary source this session. Say what was read (abstract, author block, table, source code).
- **BOUNDED**: checked, but not exhaustively or not at the body. A canonical result cited at attribution level. A negative result from a non-exhaustive search. Say what the bound is.
- **ASSERTED**: stated from background knowledge, source not opened. Permitted in working notes. **Not permitted in `docs/`.** Either verify it or cut it.
- **REFUTED**: checked and found false. Never silently deleted, always recorded with the correction.

A bounded negative ("no calibrated cardiac-conduction SBI paper found") is not proof of nonexistence. Say so.

## 4. Promotion path (the only way into `docs/`)

```
lane working note
  -> claim gets a row in docs/verification-ledger.md with a status
    -> ASSERTED rows are verified or cut  (they cannot proceed)
      -> critic reads it (scientific claims only)
        -> director signs
          -> docs/
```

No shortcuts. A claim that cannot be verified is marked unverified and stays in the working note, or it is dropped. We never assert.

## 5. Precedence when lanes disagree

1. **Compute beats narrative.** A run that contradicts a story kills the story. `ridge_confirm` beat a beautiful degeneracy headline, and the headline was wrong.
2. **The ledger beats the prose.** If a doc asserts something with no ledger row, the doc is wrong until a row exists.
3. **A primary source beats all of us.** Including the director.
4. **The critic breaks ties.** It is read-only and never edits.
5. **The director signs.** Every scientific claim, without exception.

Correlation is not degeneracy. Agreement between two lanes is not verification, especially when both inherited the same assumption.

## 6. Retraction protocol

Wrong claims are not quietly edited away. They are retracted, in place, with a date and the evidence that killed them, in `.localagent/state.md` and in the affected doc's history.

Two retractions are already on the record: the forward-fidelity `corr 0.86` claim, and the `delta_iv`-`cv_myo` degeneracy headline. Both were surfaced by us, not by a reviewer. That is the system working, and the record of it is an asset, not an embarrassment.

## 7. What this buys

A reviewer can ask, of any sentence in `docs/`: where did this come from, who checked it, and against what. The ledger answers in one lookup. That is the whole point.

---

# The research handoff SOP

How a question becomes a verified fact becomes a line of code. Six steps, one owner each.

## 1. REQUEST (director)
The director appends a numbered batch to the research backlog, prioritized P0/P1/P2. Every item states **what changes if the answer is different than expected**. An item that changes nothing is not worth asking.

Items that gate a running or imminent job are marked P0 and say so explicitly, including the deadline ("needed within hours, blocks ingestion tonight").

## 2. DELIVER (Science)
Science returns a bundle, never a chat message:

```
conduction_lens_batchN/
  SUMMARY.md                    # headline findings, contents table, bounded edges
  <one file per task>.md        # the actual work
  verification_ledger_batchN.md # every claim, one row, with a status
```

Each ledger row carries a stable **ID**: `L-B4-03` (ledger, batch 4, row 3). IDs never change and are never reused. Every claim gets a row, including the ones that were refuted.

**Science never writes to the repository.** It produces a bundle. That is the whole interface.

## 3. INTAKE (Cowork, orchestrator)
The bundle lands, unmodified, at `.claude_research/conduction_lens_batchN/`. That directory is gitignored. Nothing in it is truth yet.

Cowork then performs the intake check:

- Every claim has a ledger row. No orphan assertions in the prose.
- The status vocabulary is used correctly (VERIFIED / BOUNDED / ASSERTED / REFUTED).
- **Every ASSERTED row is either verified now or cut.** ASSERTED never reaches `docs/`.
- **Spot-check at least one VERIFIED row at its primary source.** Trust, then verify the verifier. This is not an insult to Science; it is how we caught the "Corrales" attribution error.
- Look for any claim that contradicts a compute result. Compute wins.
- Look for asymmetries the summary glossed. (Batch 3's "SNR-conservative" defense protected the positive claims and silently weakened the negative ones.)

Cowork writes `.localagent/intake-batchN.md`: a verdict of **ACCEPT / ACCEPT WITH CUTS / REJECT**, plus four lists: what is promotable, what is cut and why, what became a Code task, what is still open.

## 4. PROMOTE (Cowork)
Only promotable lines cross into `docs/`. Cowork makes the edit, into the one document that owns that fact class. The ledger rows append to `docs/verification-ledger.md` with their IDs intact.

The raw bundle stays private forever. It contains half-formed reasoning and internal strategy. Only the distilled, verified, ID-bearing result ships.

## 5. GATE (critic, then director)
Scientific claims go through the read-only critic before they are public. The director signs. No exceptions, including for claims the director proposed.

## 6. CONSUME (Code)
**Code never reads `.claude_research/`.** Code reads `docs/`.

When Science produces a number that Code must use, it lands in the source as a named constant with a citation to its ledger ID:

```python
# src/core/noise.py
SIGMA_AMP_MV = 0.05   # ledger L-B3-01, QRSense, Obregon-Rosas 2026, PMID 42176693
SIGMA_TIME_MS = 5.0   # ledger L-B3-01
```

That single comment closes the loop: primary source, to ledger row, to constant, to result. A reviewer can walk it in either direction. Any magic number in the codebase that lacks a ledger ID is a bug, and it is exactly the kind of bug that produced a 3000x SNR error nobody noticed for a day.

## The two rules that make this work

**Science never writes code. Code never reads working notes.** Everything crosses at `docs/`, and everything that crosses carries an ID that says who checked it and against what.
