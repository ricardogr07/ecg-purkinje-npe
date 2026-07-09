# Demo page brief

Guidance for the design lane. The page is a static export. It tells one story. The technical paper at `/paper` absorbs everything the story does not need.

## Audience

We do not know who the judges are. Assume a mixed panel: some machine-learning, some AI, some non technical. The page must land in ninety seconds for a generalist and still reward a specialist who scrolls. If a section cannot be said in one plain sentence, it belongs in the PDF, not on the page.

## The claim, in one sentence

A 12-lead ECG pins down four of seven Purkinje conduction parameters. Here is which ones, and here is how we know we are not fooling ourselves.

## Navigation

`/` the finding. `/paper` the technical PDF. `/heart` only if the export step lands; otherwise it does not appear in the nav at all.

## The spine

Order the page by what it means, not by how the work was done. The current page is ordered by workflow: ECG, then activation map, then corner plot, then the finding, then calibration. That is backwards. The finding is buried in position four and every card carries equal visual weight, so nothing reads as the point.

**0. Provenance strip.** Run id, noise floor, geometry, precomputed. Never leaves the frame.

**1. Hero and the spectrum.** The seven-bar contraction spectrum, green amber grey, under the claim sentence. This IS the finding. Colour by CRLB once the Jacobian lands so the bars do not shift when a prior is retuned; contraction stays as the printed number. Waits on Friday's reconciliation.

**2. Why it matters.** Three sentences, no jargon. The interventricular delay, the one parameter clinicians actually program into CRT devices, is the most identifiable of the seven. The tree-shape parameters are not identifiable at all, so any published value for them recovered from an ECG fit is a prior, not a measurement.

**3. How it works.** Four steps: simulate many hearts, train a network to invert, check its confidence is honest, report what survives. The only technical section. Readable by someone who has never heard of a normalizing flow.

**4. Is the uncertainty honest?** SBC before and after conformal recalibration. **Do not display TARP as evidence the joint is calibrated.** That number is currently pre-conformal and describes the posterior before the fix. Gate it behind a pending state until it is recomputed.

**5. The correlated pair.** The corner plot. Caption reads "correlated but identifiable," not "degenerate." The degeneracy reading was one of our retractions and the page still tells the old story.

**6. What we got wrong.** Narrative, not a table. Four beats, each: what we believed, what killed it, what we believe now. The `corr 0.86` validation that was hiding a per-lead nRMSE near 1. The ridge that a follow-up run showed was not a degeneracy. The 3000x SNR error that made everything look recoverable. The real-ECG framing, killed by reading our own fixture. This is the most persuasive section on the page. It sits below the calibration section, because the reader needs to know what calibration is before they can appreciate what it caught. The formal ledger lives in the PDF; link to it from here.

**7. What this is not.** A simulated ECG. One geometry. A pseudo-ECG in an unbounded homogeneous volume conductor, so amplitudes are arbitrary units scaled to a stated operating point. A local Jacobian. No patient data anywhere. Plain, unhedged, above the fold of the footer.

**8. Reproduce it.** Ledger, weights, container image, Apache-2.0, Strocchi CC-BY-4.0.

**9, conditional.** The real heart. Frame as "the pipeline generalizes," never as a second result, wireframe this.

**10. Footer.** Copyright, license, contact, acknowledgements, funding. Include the same as in shelterpulse where I have my github,linkedin, and personal webpage included with logos and links, see https://shelter-pulse.com/en or the repo for those elements: 
"ShelterPulse · Open-source simulation lab for cat shelter resource allocation

Built for #hackthekitty 2026

Built by Ricardo García Ramírez
//Then logos and links for github, linkedin, personal webpage"

But make the appropiate changes for the current work and built for the current hackathon. The footer is a static component, not a page-level banner.


## Provenance is per-section, not per-page

`results.real.json` carries `is_mock: true` and `activation_is_real: true` simultaneously. A single page-level banner therefore lies about one half or the other. Our sections land at different times.

Every card carries its own chip:

- **real** wired to the emitted artifact
- **precomputed** real numbers, baked at build time from a named run
- **illustrative** mock data, explicitly labelled
- **pending** not computed yet

A page that renders a mock as real is a scientific-integrity failure, not a polish issue. This is the component-level expression of that rule.

## The `Pending` primitive

The component we do not have and need most. An honest empty state that states what will appear here, why it is not here yet, and what result would falsify it. It lets the whole page be wireframed today and filled as data lands, without a single frame implying a number we do not have.

## `ActivationMap` upgrade

The component is solid. It is a 2.5D canvas projection, not `three.js`, painting local activation time with viridis. `geometry.real.json` already carries the `purkinje` field with the real LV and RV fractal trees, and the component already flattens both into nodes and edges and projects them each frame. The data is there. The controls are not.

Because a projection is already recomputed every frame, expose azimuth, elevation and zoom as component state and wire pointer-drag plus wheel. Roughly forty lines. Add a play/pause control and **default to paused**: a rotating element is a usability tax on the one component people will want to study.

Do not rewrite in `three.js` or `react-three-fiber`. It buys nothing and costs a day.

Caption it precisely. It shows the myocardial surface coloured by activation time, with the Purkinje network that produced it. It is an example of the forward model, not evidence for the finding.

**Hard gate:** do not render the Strocchi Purkinje network until the endocardial surface is repaired. Four PMJs per side against crtdemo's 87 and 166 will look wrong to a cardiologist because it is wrong. If the repair does not land, the real heart ships as a myocardial surface with an activation map and no tree, captioned honestly. That is still a good figure.

## Component inventory

Keep: `ActivationMap` (add controls), `CornerPlot` (recaption), `CalibrationPanel` (gate TARP), `Layout`.

Rename: `PinnedUnknowable` becomes `IdentifiabilitySpectrum`. Nothing here is unknowable. Parameters are unresolved **at a stated noise floor**, and `branch_angle` may well be resolvable at a lower one. The noise floor must appear in the component header so a screenshot cannot crop away the qualifier.

Recaption: `EcgOverlay` shows parameter recovery against a synthetic target. It is not a fidelity comparison against a real ECG. Demote it out of the hero position.

New: `Hero`, `ProvenanceChip`, `Pending`, `WhyItMatters`, `HowItWorks`, `WhatWeGotWrong`, `WhatThisIsNot`, `Reproduce`.

## Copy rules

Two layers everywhere: a plain-English top line, then a detail line with the number and the term of art.

Never write "validated," "solved," "diverges from a real ECG," or "lead field." The forward is a pseudo-ECG in an unbounded homogeneous volume conductor.

The noise floor travels with every identifiability claim, in the same frame.

Sentence case. No em dashes or en dashes anywhere, including chart labels and alt text.

Amplitudes are arbitrary units scaled to a stated mV operating point. Absolute calibration is not claimed.

## What must never appear

Any number rendered as real that is mock. Any identifiability claim without its sigma. TARP presented as joint calibration evidence while it remains pre-conformal. A Strocchi contraction spectrum, since there will not be one. The word "unknowable."
