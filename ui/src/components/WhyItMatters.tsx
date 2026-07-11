// Why it matters. Prose left, a schematic of the interventricular delay right, so
// the section is not a wall of text. The schematic is a labeled concept diagram
// (not measured data): the dIV is the offset between LV and RV activation onset,
// the timing CRT devices program and the parameter the ECG resolves best.
export default function WhyItMatters() {
  return (
    <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
      <div className="space-y-4 text-lg leading-relaxed text-zinc-300">
        <p className="text-zinc-100">Most of what the ECG resolves is the part clinicians act on.</p>
        <p>
          The interventricular delay, the timing that clinicians program into CRT pacing devices, is
          the most resolved of the seven parameters.
        </p>
        <p>
          The tree shape parameters are not resolved at this noise floor, so any single value for them
          read off an ECG fit is a prior belief, not a measurement.
        </p>
      </div>

      <figure className="space-y-3">
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
          <svg
            viewBox="0 0 360 190"
            role="img"
            aria-label="Schematic timing diagram: left ventricular activation, then right ventricular activation offset later by the interventricular delay."
            className="h-auto w-full"
          >
            {/* delay dimension */}
            <line x1="95" y1="45" x2="95" y2="152" stroke="#52525b" strokeWidth="1" strokeDasharray="3 3" />
            <line x1="165" y1="45" x2="165" y2="152" stroke="#52525b" strokeWidth="1" strokeDasharray="3 3" />
            <line x1="95" y1="45" x2="165" y2="45" stroke="#34d399" strokeWidth="1.5" />
            <polygon points="95,45 104,41 104,49" fill="#34d399" />
            <polygon points="165,45 156,41 156,49" fill="#34d399" />
            <text x="130" y="34" textAnchor="middle" fill="#6ee7b7" fontFamily="ui-monospace, monospace" fontSize="13" fontWeight="600">
              dIV
            </text>

            {/* LV activation track */}
            <text x="18" y="86" fill="#a1a1aa" fontFamily="ui-monospace, monospace" fontSize="13">
              LV
            </text>
            <rect x="60" y="70" width="280" height="22" rx="6" fill="#27272a" />
            <rect x="95" y="70" width="170" height="22" rx="6" fill="#34d399" opacity="0.75" />

            {/* RV activation track */}
            <text x="18" y="136" fill="#a1a1aa" fontFamily="ui-monospace, monospace" fontSize="13">
              RV
            </text>
            <rect x="60" y="120" width="280" height="22" rx="6" fill="#27272a" />
            <rect x="165" y="120" width="170" height="22" rx="6" fill="#34d399" opacity="0.75" />

            {/* time hint */}
            <text x="60" y="172" fill="#71717a" fontFamily="ui-monospace, monospace" fontSize="10">
              activation onset
            </text>
            <text x="340" y="172" textAnchor="end" fill="#71717a" fontFamily="ui-monospace, monospace" fontSize="10">
              time
            </text>
          </svg>
        </div>
        <figcaption className="font-mono text-xs leading-relaxed text-zinc-500">
          Schematic. The interventricular delay (dIV) is the offset between when the left and right
          ventricles begin to activate, the timing CRT devices program and the parameter the ECG
          resolves best.
        </figcaption>
      </figure>
    </div>
  );
}
