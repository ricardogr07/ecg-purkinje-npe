# Execution & Parallelization Plan, `ecg-purkinje-npe`

**Companion to:** Research Brief v5 · **Window:** Jul 7 (12:30 PM ET) → Jul 13 (9:00 PM ET, aim 7 PM) · **Director:** Ricardo

---

## 0. Repo name

**Recommended:** **`ecg-purkinje-npe`**, "a lens onto the conduction system: what an ECG lets you see, and what it can't." Memorable for the demo, credible for the researcher track, and, deliberately, **does not start with `purkinje-`**, which visually separates the new hackathon repo from your thesis repos (`purkinje-uv`, `purkinje-learning`) and reinforces the "new work" optics for the eligibility question.

**Alternatives (say the word and I'll swap it everywhere):** `beat-to-source`, `purkinje-scope`, `ecg-identifiability`.

Used as the working name throughout this doc. GitHub: `ricardogr07/ecg-purkinje-npe`, Apache-2.0, public from commit 1.

---

## 1. The four Claude workstreams (who owns what)

Think of these as four teammates you direct. Each has a home surface and a clear lane.

| Stream | Home surface | Owns | Does **not** touch |
|---|---|---|---|
| **Research** | Claude Science / Research | Prior-art positioning (done), calibration-study design, posterior interpretation, adversarial critique of the finding, the forward-sensitivity cross-check, scientific framing of the write-up | Writing production code, infra |
| **Code** | Claude Code (terminal, in the repo) | Mesh adapter, sim-sweep harness, NPE pipeline, calibration diagnostics, tests/CI, FastAPI backend, Terraform/AWS, the agentic identifiability loop | Scientific claims, visual design |
| **Design** | Claude + design skills (`design-critique`, `ux-copy`, `accessibility-review`, `design-handoff`) + Figma MCP, driven from Cowork/Code | Next.js frontend, 3D activation map, ECG overlay, corner/degeneracy plot, calibration panel, the "pinned vs. unknowable" reveal, demo-video storyboard, hero visuals | Model internals, infra |
| **Cowork** | This surface (orchestration) | Daily standup, cross-stream coordination, the technical write-up assembly, figure captions, the "Built with Claude" section, the 100-200-word summary, submission packaging, checklist/state tracking | Deep coding, model math |

> Note on "Claude Design": there isn't a standalone Design product, this stream is Claude plus the **design plugin skills** and the **Figma MCP**, run inside Cowork (for planning/copy) and Claude Code (for the actual Next.js). Treat it as a real lane regardless; it maps to the 30% Demo score.

---

## 2. You, the orchestrator/director

Your job is **not** to write code, it's to keep four streams pointed the same way, own the human-only actions, and be the final judgment on scientific claims. Concretely:

**Human-only actions (only you can do these):**
- Post the Day-1 **4-part eligibility question** in #questions (gates everything).
- Any **AWS console / credentials / billing** actions and GitHub repo/secrets setup.
- **Recruit a teammate** (Day 1, the single highest-leverage move; see §6).
- **Record the 3-min video** (your voice/face) and hit **submit**.
- **Approve every scientific claim** before it enters the write-up or demo.

**Daily director rhythm (≈30 min bookending each day):**
- **Morning (set direction):** read Cowork's standup, set the day's 3 goals per stream, resolve any open decision gate.
- **Midday (unblock):** 10-min check, is any stream blocked on a contract or a decision? Clear it.
- **Evening (review & merge):** review each stream's output against its Definition of Done, merge to `develop`, tell Cowork what to log for tomorrow.

**Decision gates you own (don't let a stream self-approve these):** eligibility answer interpretation · determinism-test result → noise-model path · sim-budget number after the forward-eval benchmark · "is the finding real / honestly stated" · AWS go/no-go at the Sat cutoff · final submit.

---

## 3. The parallelization model (how we generate parallel work)

The unlock is **decoupling via contracts**. If Science, Infra, and Design all agree on three interfaces on Day 1-2, they can run **in parallel against mocks** and only integrate at the end. Define these first; freeze them fast.

**Contract A, the θ schema (Science ↔ Code).** The 6D parameter vector, names, physiological ranges/priors, units. Once frozen (Thu), the sweep harness, NPE, and baseline all build against it.

**Contract B, the results artifact (Code ↔ Design ↔ Cowork).** A single JSON schema for a run: per-parameter contraction + coverage, posterior samples (for the corner plot), the posterior-predictive ECG, the input ECG, the activation map field. Design builds the whole frontend against a **mock artifact** while Science is still simulating.

**Contract C, the demo API (Code ↔ Design).** The FastAPI response shape the frontend calls (`POST /infer` → results artifact; `GET /geometry` → mesh for the 3D view). Mock it Day 2; Design never waits on real inference.

**Parallel tracks after the Day-1 foundation:**

```
Track S (Science, critical path):  forward model → sweep → NPE → calibration → finding
Track I (Infra/Code):              scaffold → mesh adapter → backend → Terraform/AWS
Track D (Design/Demo):             mock-data frontend → real-data swap → video
Track W (Cowork/Writeup):          prior-art (done) → methods → Built-with-Claude → submission
```

Track S is the **critical path**, protect it. Tracks I, D, W should never block on S because they run against the frozen contracts + mock data. The only hard sync points are: contracts frozen (Day 2), real artifact replaces mock (Day 4→5), integration (Day 5).

---

## 4. Day-by-day

Each day: **theme → per-track tasks (owner) → your director actions → decision gate → Definition of Done (DoD).**

### Tue Jul 7, Foundation & de-risk (half day, start 12:30 ET)
**Theme:** prove the pipeline runs and kill the two biggest unknowns (eligibility, forward-eval cost).
- **[Ricardo]** Post the **4-part eligibility question** at 12:30. Start **teammate recruiting**. Create GitHub repo `ecg-purkinje-npe` (Apache-2.0, public), set secrets.
- **[Code]** Repo scaffold: package layout, CI, Docker, pre-commit. **Benchmark one forward eval** (fractal tree + eikonal + ECG) → report the number. **Determinism test** (same θ twice, diff the ECG). Full NPE pipeline smoke-run on `cardiac-demo`.
- **[Research]** **Prior-predictive check**: do prior-drawn ECGs look physiological (QRS duration, axis in range)? First cheap figure.
- **[Design]** Stand up the Next.js skeleton + pick the visual language (start from the shelter-pulse aesthetic). Draft the demo storyboard.
- **[Cowork]** Open the project state doc; draft Contracts A/B/C v0.
- **Gate (Ricardo):** determinism result → confirms §5.6 mandatory. Forward-eval number → sets the sim budget.
- **DoD:** eligibility question posted; NPE runs end-to-end on the toy geometry; sim budget decided; determinism known.

### Wed Jul 8, Real anatomy in, contracts frozen
**Theme:** get Strocchi through the adapter; lock the interfaces so parallel work can start.
- **[Code]** Ensight→endocardial-surface **mesh adapter**; ingest one Strocchi mesh; produce sane 12-lead output on real anatomy. Stub FastAPI with **mock `/infer`** returning a fake results artifact.
- **[Research]** Finalize the 6D θ + priors (Contract A); define the ECG feature set precisely.
- **[Design]** Build the frontend **against the mock artifact**, activation-map view + ECG overlay shells.
- **[Cowork]** **Freeze Contracts A/B/C.** Start the methods section of the write-up.
- **[Ricardo]** Review adapter output (does the ECG look real?); approve the frozen contracts.
- **Gate:** contracts frozen, after this, streams run parallel and independent.
- **DoD:** real Strocchi ECG produced; mock API live; frontend rendering mock data; θ schema frozen.

### Thu Jul 9, Launch the sweep (parallel work peaks)
**Theme:** generate the dataset; everyone else builds against mocks.
- **[Code]** Add the **mandatory noise model (§5.6)**; wire the sweep harness to store **both features and waveforms**; **launch the fresh sim sweep** on a big CPU instance; dataset QC.
- **[Research]** **Forward-sensitivity probe** of the diffuse block (what should be unidentifiable?), setting expectations for the finding.
- **[Design]** Build the **corner/degeneracy plot** + **calibration panel** components (against mock posteriors); draft the "pinned vs. unknowable" reveal.
- **[Cowork]** Draft the **"Built with Claude"** section from the workflow so far; start the 100-200-word summary.
- **[Ricardo]** Approve the noise model magnitude (a stated assumption); confirm the sweep launched; keep an eye on teammate onboarding.
- **Gate:** sweep launched and producing valid rows.
- **DoD:** dataset generating; all demo components exist against mocks; write-up scaffold populated.

### Fri Jul 10, Train & calibrate (the finding takes shape)
**Theme:** first real posteriors and the headline result.
- **[Code]** Train NPE on **features and waveform**; run **SBC + expected coverage**; emit the real **contraction table** + first **degeneracy plot**.
- **[Research]** Interpret posteriors; **adversarially critique** the boundary ("argue this is an artifact"); check against the sensitivity probe.
- **[Design]** **Swap mock → real artifact** in the frontend; polish the reveal and calibration panel with real numbers.
- **[Cowork]** Write the results section around the real table/figure; caption figures.
- **[Ricardo]** **Approve the finding**, is it real, is it honestly stated, does it survive the adversarial pass?
- **Gate:** the finding is real and defensible (or pivots to the honest-negative framing).
- **DoD:** real calibrated posteriors; headline table + figure; frontend on real data.

### Sat Jul 11, Validate, integrate, deploy (AWS cutoff)
**Theme:** prove trust, wire it together, ship the page.
- **[Code]** **BO+ABC agreement/validation** on shared held-out ECGs + amortization-artifact check; **AWS deploy** via the reused shelter-pulse Terraform, **hard deadline EOD**; if not up, freeze and fall back to local Docker.
- **[Design]** Full **integration pass**: activation map + ECG overlay + corner plot + calibration panel in one coherent demo; accessibility/`ux-copy` polish.
- **[Research]** Sanity-check the baseline agreement (does NPE match ABC where trusted?).
- **[Cowork]** Assemble the near-final write-up; draft the video script from the storyboard.
- **[Ricardo]** **AWS go/no-go at EOD.** Review the integrated demo end to end.
- **Gate:** AWS live **or** local-Docker fallback locked; baseline validation done.
- **DoD:** working, trustworthy, integrated demo; deploy decision resolved.

### Sun Jul 12, Stretch + polish
**Theme:** the one stretch that lifts Impact, then lock the demo.
- **[Code/Research]** **Anatomy-generalization (locked stretch, §5.9):** train/eval on 2-3 geometries; show transfer. (If it fights back, drop cleanly, it's a stretch.)
- **[Design]** Final demo polish; pre-record demo b-roll; ensure it reads in 3 minutes.
- **[Cowork]** Finalize write-up + "Built with Claude"; tighten the 100-200-word summary.
- **[Ricardo]** Decide stretch in/out by midday; rehearse the video narration.
- **Gate:** stretch shipped or cleanly cut; demo frozen for recording.
- **DoD:** demo final; write-up final draft; stretch resolved.

### Mon Jul 13, Freeze, record, submit (due 21:00 ET; aim 19:00)
**Theme:** no new work, package and ship.
- **[Code]** Freeze results: seeds, source digests, CIs; tag a release; publish the model checkpoint.
- **[Cowork]** Final write-up + summary; assemble the submission package; run the rules checklist (open-source, licenses, attribution).
- **[Design]** Final render of the demo video.
- **[Ricardo]** **Record the 3-min video**; final review of every artifact; **submit by 7 PM ET** (2-hr buffer).
- **Gate:** final submit.
- **DoD:** submitted: video + repo + write-up + summary.

---

## 5. Daily cadence (the ritual)

- **09:00**, Cowork posts the standup (yesterday / today / blockers, per track) → you set the day's goals.
- **~14:00**, 10-min unblock check.
- **~20:00**, evening review: each track's DoD, merge to `develop`, log tomorrow.
- Cowork keeps the **single source of truth** (state doc + checklist); every stream reports to it, you direct from it.

---

## 6. Critical path, slip order, and the teammate question

- **Critical path:** forward-eval benchmark → sweep → NPE → calibration → finding (Track S). Everything else parallelizes around it.
- **If you fall behind, cut in this order:** (1) anatomy-generalization stretch → (2) waveform path (keep features-only, weaken but don't break the claim) → (3) AWS live (fall back to local Docker) → (4) Strocchi (fall back to `cardiac-demo`). Never cut: calibration, the honest finding, the video.
- **Teammate:** solo across Science + Infra + Design + video in 5.5 days is the top risk. If you recruit, the clean split is **you + Research + Code on Track S/I**, **teammate on Track D (Design/Demo) + video**, Cowork shared. Do it Day 1.

---

## 7. Backlog by track (kanban seed)

**Track S, Science:** forward-eval benchmark · determinism test · prior-predictive check · θ+priors freeze · noise model · sim sweep · NPE (features) · NPE (waveform) · SBC · expected coverage · contraction table · degeneracy plot · BO+ABC validation · sensitivity cross-check · anatomy-gen stretch.
**Track I, Infra/Code:** repo scaffold · CI · Docker · mesh adapter · sweep harness · results-artifact serializer · FastAPI (mock→real) · Terraform/Fargate · checkpoint publishing · release tagging.
**Track D, Design/Demo:** visual language · storyboard · activation-map view · ECG overlay · corner plot · calibration panel · "pinned vs. unknowable" reveal · integration pass · a11y/copy polish · video render.
**Track W, Cowork/Writeup:** state doc · contracts · methods · results · limitations · Built-with-Claude · 100-200-word summary · rules checklist · submission package.
