import { Card } from "@/components/Layout";
import ProvenanceChip, { type Provenance } from "@/components/ProvenanceChip";
import ActivationMap from "@/components/ActivationMap";
import EcgOverlay from "@/components/EcgOverlay";
import { results } from "@/lib/artifact";

// How it works. The only technical section, written to read without any ML
// background: four steps, then two examples of the forward model. EcgOverlay is
// demoted into this section (never above the spectrum) and recaptioned. Copy
// verbatim from the frozen standalone.

const STEPS = [
  {
    n: "01",
    title: "Simulate many hearts",
    body: "Draw conduction parameters from a prior and run a heart simulator thousands of times to build many parameter to ECG pairs.",
  },
  {
    n: "02",
    title: "Train a network to invert",
    body: "Train a network to run it backwards: give it an ECG, it returns a distribution over the parameters that could have produced it.",
  },
  {
    n: "03",
    title: "Check its confidence is honest",
    body: "Grade the network with simulation based calibration, which asks whether its stated uncertainty matches reality, and correct it where it is overconfident.",
  },
  {
    n: "04",
    title: "Report what survives",
    body: "Report only what the ECG actually narrows, with the noise floor stated, and flag plainly what it cannot resolve.",
  },
];

export default function HowItWorks() {
  // The forward scene (surface + LAT + ECG) is exported from the forward model.
  // Honest, data-driven provenance: real numbers baked from a named run when the
  // export is present, illustrative otherwise. Never label a mock as real.
  const meta = (results.meta ?? {}) as Record<string, unknown>;
  const forwardReal = Boolean(meta.activation_is_real) || meta.is_mock === false;
  const forwardKind: Provenance = forwardReal ? "precomputed" : "illustrative";
  const forwardNote = forwardReal ? "crtdemo forward run" : "mock forward scene, pending the production run";

  return (
    <div>
      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        {/* the fixed anatomy and its grown Purkinje network (static paper figure) */}
        <figure className="space-y-3">
          <Card>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/figures/fig6_crtdemo_purkinje_dark.png"
              width={1407}
              height={765}
              alt="The fixed crtdemo biventricular anatomy with a grown fractal Purkinje network overlaid on the endocardium."
              className="h-auto w-full rounded-lg"
            />
          </Card>
          <figcaption className="font-mono text-xs leading-relaxed text-zinc-500">
            Figure 1. The fixed crtdemo anatomy and a grown Purkinje network; conduction parameters
            flow through the simulator to a 12-lead ECG, then an amortized NPE to a calibrated
            posterior.
          </figcaption>
        </figure>
        {/* the four steps of the pipeline */}
        <div className="grid gap-4 sm:grid-cols-2">
          {STEPS.map((s) => (
            <div key={s.n} className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-5">
              <div className="font-mono text-sm text-indigo-400">{s.n}</div>
              <h3 className="mt-2 text-sm font-semibold text-zinc-100">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{s.body}</p>
            </div>
          ))}
        </div>
      </div>

      <p className="mt-12 text-xs font-mono uppercase tracking-widest text-zinc-500">
        the forward model, in two examples
      </p>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <ProvenanceChip kind={forwardKind} note={forwardNote} />
          <Card title="Activation map" hint="local activation time (ms)">
            <ActivationMap />
          </Card>
          <p className="text-xs leading-relaxed text-zinc-500">
            The myocardial surface coloured by activation time, with the Purkinje network that
            produced it. An example of the forward model, not evidence for the finding.
          </p>
        </div>
        <div className="space-y-3">
          <ProvenanceChip kind={forwardKind} note={forwardNote} />
          <Card title="Forward 12-lead ECG" hint="synthetic target at the reference parameters">
            <EcgOverlay />
          </Card>
          <p className="text-xs leading-relaxed text-zinc-500">
            The forward-model 12-lead pseudo-ECG at the reference conduction parameters. Amplitudes are
            arbitrary units scaled to a stated mV operating point. This is not a comparison against a
            real ECG.
          </p>
        </div>
      </div>
    </div>
  );
}
