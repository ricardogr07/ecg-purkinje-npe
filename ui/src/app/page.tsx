import type { ReactNode } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Section, Card } from "@/components/Layout";
import ProvenanceChip, { type Provenance } from "@/components/ProvenanceChip";
import Hero from "@/components/Hero";
import IdentifiabilitySpectrum from "@/components/IdentifiabilitySpectrum";
import WhyItMatters from "@/components/WhyItMatters";
import HowItWorks from "@/components/HowItWorks";
import CalibrationPanel from "@/components/CalibrationPanel";
import CornerPlot from "@/components/CornerPlot";
import WhatThisIsNot from "@/components/WhatThisIsNot";
import Reproduce from "@/components/Reproduce";
import ActivationMap from "@/components/ActivationMap";
import { results } from "@/lib/artifact";
import type { Geometry, ResultsArtifact } from "@/lib/artifact";
import strocchiGeometry from "@mock/geometry.strocchi.json";
import strocchiResults from "@mock/results.strocchi.json";
import strocchiGeometry02 from "@mock/geometry.strocchi_02.json";
import strocchiResults02 from "@mock/results.strocchi_02.json";

// Spine order follows the paper's arc (argumentative, not workflow): the question
// and its proof, why it matters, the heart and the pipeline, the finding in full,
// is the uncertainty honest, the one correlated case, the limits, the pipeline
// generalizes, reproduce. Provenance is per section via chips, never a page banner.
// Connective lines hand off between sections; copy owned by Cowork.

// A short connective sentence that hands off to the next section.
function Connective({ children }: { children: ReactNode }) {
  return <p className="mt-10 text-base leading-relaxed text-zinc-400">{children}</p>;
}

export default function Home() {
  // Data-driven provenance: the posterior-derived panels are the honest 7D run
  // once it bakes in (is_mock:false -> precomputed), and mock until then
  // (is_mock:true -> illustrative). Never label a mock as real.
  const meta = (results.meta ?? {}) as Record<string, unknown>;
  const isMock = Boolean(meta.is_mock);
  const posteriorKind: Provenance = isMock ? "illustrative" : "precomputed";
  const spectrumNote = isMock
    ? "mock contraction numbers, pending the production run"
    : "contraction numbers from the 7D posterior run";
  const calibrationNote = isMock
    ? "mock calibration diagnostics, pending the production run"
    : "calibration diagnostics from the 7D posterior run";
  const cornerNote = isMock
    ? "mock posterior samples, pending the production run"
    : "posterior samples from the 7D posterior run";

  return (
    <>
      <Header />
      <main id="main" className="flex-1">
        {/* 01. the question: the hero + the spectrum as proof */}
        <section id="finding" className="scroll-mt-20 border-b border-zinc-800">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:py-24">
            <p className="mb-4 text-xs font-mono uppercase tracking-widest text-indigo-400">
              <span className="text-zinc-500">01 / </span>the question
            </p>
            <Hero />
            <div className="mt-12">
              <ProvenanceChip kind={posteriorKind} note={spectrumNote} />
              <div className="mt-4">
                <IdentifiabilitySpectrum compact />
              </div>
            </div>
            <Connective>
              Before trusting any of those numbers, two questions: does it matter, and is the
              uncertainty honest.
            </Connective>
          </div>
        </section>

        {/* 02. why it matters */}
        <Section
          id="why"
          number="02"
          eyebrow="why it matters"
          title="The ECG resolves the parameter clinicians actually use"
        >
          <WhyItMatters />
          <Connective>
            That is the stake. Here is the machine that turns a heart into an ECG, and the ECG back
            into a distribution over parameters.
          </Connective>
        </Section>

        {/* 03. the heart and the pipeline */}
        <Section
          id="how"
          number="03"
          eyebrow="the heart and the pipeline"
          title="The heart, and the pipeline that inverts it"
          lead="The anatomy is fixed. Conduction parameters flow through the simulator to a 12-lead ECG; an amortized posterior estimator inverts it. Four steps, no neural-network background needed."
        >
          <HowItWorks />
          <Connective>
            Run that pipeline across the prior and read off, parameter by parameter, how much the ECG
            actually narrows.
          </Connective>
        </Section>

        {/* 04. the finding, in full */}
        <Section
          id="spectrum"
          number="04"
          eyebrow="the finding, in full"
          title="Four of seven parameters carry information"
          lead="At the waveform floor (sigma 0.025 mV per sample per lead) the ordering is clear. Interventricular delay (contraction about 0.15) and myocardial velocity (about 0.35) are well constrained; RV initial extent (about 0.63) and conduction velocity (about 0.67) are moderate; LV extent, branch angle and branch repulsivity stay diffuse (about 1.0 to 1.2), no tighter than the prior."
        >
          <div className="space-y-6">
            <ProvenanceChip kind={posteriorKind} note={spectrumNote} />
            <IdentifiabilitySpectrum />
          </div>
        </Section>

        {/* 05. is the uncertainty honest? */}
        <Section
          id="calibration"
          number="05"
          eyebrow="is the uncertainty honest?"
          title="Calibrated, so the intervals mean what they say"
          lead="An identifiability claim is only as good as its calibration. The raw posterior was overconfident; per-parameter conformal recalibration flattens the simulation based calibration ranks and brings the joint coverage to the diagonal. Toggle before and after."
        >
          <div className="space-y-4">
            <ProvenanceChip kind={posteriorKind} note={calibrationNote} />
            <CalibrationPanel />
          </div>
          <Connective>
            Calibrated marginals still hide how parameters trade off against each other. One pair
            shows it clearly.
          </Connective>
        </Section>

        {/* 06. the correlated pair */}
        <Section
          id="correlation"
          number="06"
          eyebrow="the correlated pair"
          title="Correlated, but still identifiable"
          lead="Interventricular delay and RV initial extent trade off against each other: the ECG constrains their combination more tightly than either alone, while leaving each one looser. That is correlation, not a failure to resolve."
        >
          <div className="space-y-4">
            <ProvenanceChip kind={posteriorKind} note={cornerNote} />
            <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
              <Card>
                <CornerPlot />
              </Card>
              <div className="space-y-4">
                <Card title="Reading the plot">
                  <ul className="space-y-3 text-sm text-zinc-400">
                    <li>
                      <span className="font-mono text-zinc-200">Diagonal</span>: each parameter&apos;s
                      marginal posterior, coloured by how well the ECG resolves it.
                    </li>
                    <li>
                      <span className="font-mono text-zinc-200">Lower cells</span>: pairwise samples.
                      A tilted cloud means the pair is correlated.
                    </li>
                    <li>
                      <span className="font-mono text-amber-300">The amber cell</span>: the dIV to
                      L0_RV pair, the strongest correlation where both parameters are still
                      individually identifiable.
                    </li>
                    <li>
                      <span className="font-mono text-zinc-200">Upper cells</span>: correlation
                      strength between parameters.
                    </li>
                  </ul>
                </Card>
                <Card title="Why it matters">
                  <p className="text-sm text-zinc-400">
                    A single best fit would hide this. The calibrated posterior shows the ECG
                    measures a combination faithfully while leaving each ingredient looser, the kind
                    of finding a point estimate cannot express.
                  </p>
                </Card>
              </div>
            </div>
          </div>
        </Section>

        {/* 07. limitations */}
        <Section id="limits" number="07" eyebrow="limitations" title="Limitations">
          <WhatThisIsNot />
        </Section>

        {/* 08. the pipeline generalizes to public Strocchi anatomy (no finding claimed) */}
        <Section
          id="generalize"
          number="08"
          eyebrow="the pipeline generalizes"
          title="The pipeline generalizes"
          lead="The same steps run on multiple public anatomies. This is a claim about the method, not a second result."
        >
          <div className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-2">
                <ProvenanceChip
                  kind={strocchiResults.meta?.is_mock ? "illustrative" : "precomputed"}
                  note="Strocchi method-generality panel"
                />
                <ActivationMap
                  geometry={strocchiGeometry as unknown as Geometry}
                  results={strocchiResults as unknown as ResultsArtifact}
                />
                <p className="font-mono text-xs text-zinc-500">
                  Figure 2. Strocchi heart 01: grown LV / RV Purkinje network,{" "}
                  {strocchiResults.meta.lv_pmj} / {strocchiResults.meta.rv_pmj} Purkinje-muscle
                  junctions.
                </p>
              </div>
              <div className="space-y-2">
                <ProvenanceChip
                  kind={strocchiResults02.meta?.is_mock ? "illustrative" : "precomputed"}
                  note="Strocchi method-generality panel"
                />
                <ActivationMap
                  geometry={strocchiGeometry02 as unknown as Geometry}
                  results={strocchiResults02 as unknown as ResultsArtifact}
                />
                <p className="font-mono text-xs text-zinc-500">
                  Figure 3. Strocchi heart 02: grown LV / RV Purkinje network,{" "}
                  {strocchiResults02.meta.lv_pmj} / {strocchiResults02.meta.rv_pmj} Purkinje-muscle
                  junctions.
                </p>
              </div>
            </div>
            <p className="text-sm text-zinc-400">
              The pipeline ingests public CC-BY-4.0 four-chamber meshes (Strocchi et al., PLoS ONE
              2020), derives each endocardium from the mesh&apos;s own universal ventricular
              coordinates, grows a Purkinje network, places electrodes from the heart&apos;s own axes,
              and synthesizes a pseudo-ECG. This demonstrates that the method generalizes to real
              anatomy. No identifiability result is claimed on any of these hearts (crtdemo&apos;s PMJ
              counts are 87 and 166 for reference).
            </p>
          </div>
          <Connective>
            Everything above is a static export from a named run. Here is how to reproduce it.
          </Connective>
        </Section>

        {/* 09. reproduce and read the paper */}
        <Section
          id="reproduce"
          number="09"
          eyebrow="reproduce and read the paper"
          title="Everything you need to run it yourself"
          lead="The finding is a static export from a named run. The code, the weights, and the environment are open."
        >
          <Reproduce />
        </Section>
      </main>
      <Footer />
    </>
  );
}
