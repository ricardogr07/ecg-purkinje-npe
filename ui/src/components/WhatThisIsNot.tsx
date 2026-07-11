// Limitations. A single card, one ordered list. These are the limits a reader
// must hold before they cite the finding. Copy verbatim from the frozen standalone.

const LIMITS = [
  "A simulated ECG. Not a recording from a patient.",
  "One geometry. Not a cohort.",
  "A pseudo-ECG in an unbounded homogeneous volume conductor. Amplitudes are arbitrary units scaled to a stated mV operating point. Absolute calibration is not claimed.",
  "A local Jacobian. Not a global sensitivity analysis.",
  "No patient data anywhere.",
];

export default function WhatThisIsNot() {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
      <ol className="list-decimal space-y-3 pl-6 marker:font-mono marker:text-zinc-500">
        {LIMITS.map((t) => (
          <li key={t} className="pl-1 text-sm leading-relaxed text-zinc-300">
            {t}
          </li>
        ))}
      </ol>
    </div>
  );
}
