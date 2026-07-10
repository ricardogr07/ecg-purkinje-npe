// What this is not. Five disclaimer tiles, plain and unhedged, above the fold of
// the footer. Copy verbatim from the frozen standalone. These are the limits a
// reader must hold before they cite the finding.

const TILES = [
  "A simulated ECG. Not a recording from a patient.",
  "One geometry. Not a cohort.",
  "A pseudo-ECG in an unbounded homogeneous volume conductor. Amplitudes are arbitrary units scaled to a stated mV operating point. Absolute calibration is not claimed.",
  "A local Jacobian. Not a global sensitivity analysis.",
  "No patient data anywhere.",
];

export default function WhatThisIsNot() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {TILES.map((t) => (
        <div key={t} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
          <p className="text-sm leading-relaxed text-zinc-300">{t}</p>
        </div>
      ))}
    </div>
  );
}
