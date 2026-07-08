import Header from "@/components/Header";
import { Section, Card, Chip } from "@/components/Layout";
import EcgOverlay from "@/components/EcgOverlay";
import ActivationMap from "@/components/ActivationMap";
import CornerPlot from "@/components/CornerPlot";
import PinnedUnknowable from "@/components/PinnedUnknowable";
import CalibrationPanel from "@/components/CalibrationPanel";
import { results } from "@/lib/artifact";

function meta(key: string): string | number | undefined {
  const v = results.meta?.[key];
  return typeof v === "string" || typeof v === "number" ? v : undefined;
}

export default function Home() {
  const nSamples = results.posterior?.samples?.length;
  const noise = results.noise_model;

  return (
    <>
      <Header />
      <main id="main" className="flex-1">
        {/* hero */}
        <div id="top" className="border-b border-zinc-800">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:py-24">
            <div className="flex flex-wrap gap-2">
              <Chip tone="indigo">amortized NPE</Chip>
              <Chip tone="emerald">formally calibrated</Chip>
              {results.synthetic_truth ? <Chip tone="amber">synthetic-truth study</Chip> : null}
            </div>
            <h1 className="mt-5 max-w-4xl text-4xl font-bold tracking-tight text-zinc-50 sm:text-6xl">
              Which Purkinje conduction parameters can the surface ECG pin down?
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-zinc-300">
              We train a neural posterior over 7 conduction parameters at fixed anatomy and report,
              with formal calibration, exactly which ones the 12-lead ECG constrains and which it
              cannot. The answer is a per-parameter identifiability spectrum, not a single fit.
            </p>
            <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-500">
              This is a calibrated-identifiability study on the simulator (synthetic ground truth),
              not a fit to a real-patient ECG. The honest question is what the ECG can and cannot
              resolve, with uncertainty you can trust.
            </p>

            {/* run metadata */}
            <dl className="mt-8 grid max-w-3xl grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { k: "geometry", v: results.geometry_id },
                { k: "method", v: meta("sbi_method") },
                { k: "sim budget", v: meta("sim_budget") },
                { k: "posterior draws", v: nSamples },
                { k: "observation", v: results.observation_kind },
                { k: "noise model", v: noise?.kind },
                { k: "waveform sigma", v: noise?.sigma !== undefined ? `${noise.sigma} mV` : undefined },
                { k: "run", v: results.run_id },
              ]
                .filter((x) => x.v !== undefined)
                .map((x) => (
                  <div key={x.k} className="rounded-lg border border-zinc-800 bg-zinc-900/40 px-3 py-2">
                    <dt className="text-[10px] uppercase tracking-wide text-zinc-500">{x.k}</dt>
                    <dd className="mt-0.5 font-mono text-sm text-zinc-200 wrap-break-word">{String(x.v)}</dd>
                  </div>
                ))}
            </dl>
          </div>
        </div>

        {/* 1. observation + forward */}
        <Section
          id="observation"
          eyebrow="the observation and the forward"
          title="One 12-lead ECG, one activation sequence"
          lead="The input is a 12-lead waveform. The forward model turns conduction parameters into a ventricular activation sequence and, through it, the ECG. Watch the depolarization wavefront sweep the biventricular surface."
        >
          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="12-lead ECG" hint="observed vs posterior-predictive">
              <EcgOverlay />
            </Card>
            <Card title="Ventricular activation map" hint="local activation time (ms)">
              <ActivationMap />
            </Card>
          </div>
        </Section>

        {/* 2. degeneracy */}
        <Section
          id="degeneracy"
          eyebrow="the posterior"
          title="The posterior is degenerate, and that is the finding"
          lead="Different conduction parameters produce near-identical ECGs. The corner plot exposes it: a tight ridge between Purkinje conduction velocity and LV early-activation extent means the ECG constrains their combination, not each one alone."
        >
          <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
            <Card>
              <CornerPlot />
            </Card>
            <div className="space-y-4">
              <Card title="Reading the plot">
                <ul className="space-y-3 text-sm text-zinc-400">
                  <li>
                    <span className="font-mono text-zinc-200">Diagonal</span>: each parameter&apos;s
                    marginal posterior, colored by how well the ECG pins it.
                  </li>
                  <li>
                    <span className="font-mono text-zinc-200">Lower cells</span>: pairwise samples. A
                    diagonal cloud is a degeneracy: the pair trades off.
                  </li>
                  <li>
                    <span className="font-mono text-amber-300">The amber cell</span>: the cv to L0_LV
                    ridge, the headline non-identifiability.
                  </li>
                  <li>
                    <span className="font-mono text-zinc-200">Upper cells</span>: correlation between
                    parameters.
                  </li>
                </ul>
              </Card>
              <Card title="Why it matters">
                <p className="text-sm text-zinc-400">
                  A single best-fit would hide this. The calibrated posterior shows the ECG measures a
                  combination faithfully while leaving each ingredient uncertain, exactly the kind of
                  finding a point estimate cannot express.
                </p>
              </Card>
            </div>
          </div>
        </Section>

        {/* 3. pinned vs unknowable */}
        <Section
          id="identifiability"
          eyebrow="the identifiability spectrum"
          title="This one is pinned. This one is unknowable."
          lead="Contraction ranks each parameter by how much the ECG narrows it from its prior. Some collapse to a tight interval. Others barely move. Same ECG, opposite verdicts."
        >
          <PinnedUnknowable />
        </Section>

        {/* 4. calibration */}
        <Section
          id="calibration"
          eyebrow="findings you can trust"
          title="Calibrated, so the intervals mean what they say"
          lead="An identifiability claim is only as good as its calibration. Simulation-based calibration and expected coverage (TARP) test whether the posterior intervals are honest. Toggle conformal calibration and watch the ranks flatten and the coverage curve snap to the diagonal."
        >
          <CalibrationPanel />
        </Section>

        {/* footer */}
        <footer className="border-t border-zinc-800 py-12">
          <div className="mx-auto max-w-6xl px-4 text-sm text-zinc-500">
            <p className="max-w-3xl">
              Amortized calibrated identifiability of the Purkinje conduction system from the surface
              ECG. Neural Posterior Estimation (sbi) over conduction parameters at fixed anatomy on a
              public heart mesh. The contribution is a scientific finding: which parameters the ECG
              can and cannot resolve, with calibrated uncertainty.
            </p>
            <p className="mt-4 text-xs text-zinc-400">
              Synthetic-truth study on the simulator. Not validated against a real-patient ECG. Values
              shown are from a mock Contract-B artifact pending the production run. Strocchi mesh cohort
              is CC-BY-4.0.
            </p>
          </div>
        </footer>
      </main>
    </>
  );
}
