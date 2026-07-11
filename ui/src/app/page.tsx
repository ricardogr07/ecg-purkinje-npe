import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Section, Card } from "@/components/Layout";
import ProvenanceChip, { type Provenance } from "@/components/ProvenanceChip";
import Pending from "@/components/Pending";
import Hero from "@/components/Hero";
import IdentifiabilitySpectrum from "@/components/IdentifiabilitySpectrum";
import WhyItMatters from "@/components/WhyItMatters";
import HowItWorks from "@/components/HowItWorks";
import CalibrationPanel from "@/components/CalibrationPanel";
import CornerPlot from "@/components/CornerPlot";
import WhatWeGotWrong from "@/components/WhatWeGotWrong";
import WhatThisIsNot from "@/components/WhatThisIsNot";
import Reproduce from "@/components/Reproduce";
import ActivationMap from "@/components/ActivationMap";
import { results } from "@/lib/artifact";
import type { Geometry, ResultsArtifact } from "@/lib/artifact";
import strocchiGeometry from "@mock/geometry.strocchi.json";
import strocchiResults from "@mock/results.strocchi.json";
import strocchiGeometry02 from "@mock/geometry.strocchi_02.json";
import strocchiResults02 from "@mock/results.strocchi_02.json";

// Spine order (argumentative, not workflow): finding first, then why it matters,
// how it works, is the uncertainty honest, the one correlated case, what we got
// wrong, the limits, reproduce, and the conditional real heart. See the demo
// brief and DESIGN_SPEC. Provenance is per section via chips, never a page banner.

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
        {/* 1. finding: the hero + the spectrum */}
        <section id="finding" className="scroll-mt-28 border-b border-zinc-800">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:py-24">
            <ProvenanceChip kind={posteriorKind} note={spectrumNote} />
            <div className="mt-5">
              <Hero />
            </div>
            <div className="mt-12">
              <IdentifiabilitySpectrum />
            </div>
            <div className="mt-8 max-w-2xl">
              <Pending
                label="Colouring the bars by CRLB"
                reason="The bars are coloured by contraction today. Once the Fisher information (CRLB) Jacobian lands, colour will come from CRLB so the bars do not shift when a prior is retuned. The printed contraction number stays as is."
                falsify="If CRLB and contraction disagree on which parameters are resolved, the spectrum ordering is not robust and needs a rethink."
              />
            </div>
          </div>
        </section>

        {/* 2. why it matters */}
        <Section
          id="why"
          eyebrow="why it matters"
          title="The ECG resolves the parameter clinicians actually use"
        >
          <WhyItMatters />
        </Section>

        {/* 3. how it works */}
        <Section
          id="how"
          eyebrow="how it works"
          title="Simulate many hearts, learn to invert, check the confidence is honest"
          lead="Four steps. This is the only technical section, and it reads without any prior knowledge of neural networks."
        >
          <HowItWorks />
        </Section>

        {/* 4. is the uncertainty honest? */}
        <Section
          id="calibration"
          eyebrow="is the uncertainty honest?"
          title="Calibrated, so the intervals mean what they say"
          lead="An identifiability claim is only as good as its calibration. Simulation based calibration checks, one parameter at a time, whether the posterior intervals are honest. Toggle conformal recalibration and watch the ranks flatten."
        >
          <div className="space-y-4">
            <ProvenanceChip kind={posteriorKind} note={calibrationNote} />
            <CalibrationPanel />
          </div>
        </Section>

        {/* 5. the correlated pair */}
        <Section
          id="correlation"
          eyebrow="the correlated pair"
          title="Correlated, but still identifiable"
          lead="Some parameters trade off against each other and the ECG constrains their combination tightly while leaving each one looser. That is correlation, not a failure to resolve."
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
                      <span className="font-mono text-amber-300">The amber cell</span>: the cv to
                      L0_LV pair, the clearest correlated but identifiable case.
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

        {/* 6. what we got wrong */}
        <Section
          id="corrections"
          eyebrow="what we got wrong"
          title="Four things we believed, and what changed our minds"
          lead="This is the most persuasive part of the page. It sits below the calibration section because you need to know what calibration is before you can see what it caught. The formal ledger lives in the paper."
        >
          <WhatWeGotWrong />
        </Section>

        {/* 7. what this is not */}
        <Section id="limits" eyebrow="what this is not" title="Read this before you cite it">
          <WhatThisIsNot />
        </Section>

        {/* 8. reproduce it */}
        <Section
          id="reproduce"
          eyebrow="reproduce it"
          title="Everything you need to run it yourself"
          lead="The finding is a static export from a named run. The code, the weights, and the environment are open."
        >
          <Reproduce />
        </Section>

        {/* 9. the real heart: method generalizes to public Strocchi anatomy (no finding claimed) */}
        <Section
          id="generalize"
          eyebrow="the real heart"
          title="The pipeline generalizes"
          lead="The same steps run on multiple public anatomies. This is a claim about the method, not a second result."
        >
          <div className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-2">
                <ActivationMap
                  geometry={strocchiGeometry as unknown as Geometry}
                  results={strocchiResults as unknown as ResultsArtifact}
                />
                <p className="text-xs text-zinc-500">
                  Strocchi heart 01: Purkinje network LV {strocchiResults.meta.lv_pmj} / RV{" "}
                  {strocchiResults.meta.rv_pmj} PMJs.
                </p>
              </div>
              <div className="space-y-2">
                <ActivationMap
                  geometry={strocchiGeometry02 as unknown as Geometry}
                  results={strocchiResults02 as unknown as ResultsArtifact}
                />
                <p className="text-xs text-zinc-500">
                  Strocchi heart 02: LV {strocchiResults02.meta.lv_pmj} / RV{" "}
                  {strocchiResults02.meta.rv_pmj} PMJs.
                </p>
              </div>
            </div>
            <p className="max-w-2xl text-sm text-zinc-400">
              The pipeline ingests public CC-BY-4.0 four-chamber meshes (Strocchi et al., PLoS ONE
              2020), derives each endocardium from the mesh&apos;s own universal ventricular
              coordinates, grows a Purkinje network, places electrodes from the heart&apos;s own axes,
              and synthesizes a pseudo-ECG. This demonstrates that the method generalizes to real
              anatomy. No identifiability result is claimed on any of these hearts (crtdemo&apos;s PMJ
              counts are 87 and 166 for reference).
            </p>
          </div>
        </Section>
      </main>
      <Footer />
    </>
  );
}
