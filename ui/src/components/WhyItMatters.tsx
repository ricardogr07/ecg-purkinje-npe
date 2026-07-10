// Why it matters. Three sentences, no jargon. Prose only, no chip: it makes no
// numeric claim of its own, it reads the finding above. Copy verbatim from the
// frozen standalone.
export default function WhyItMatters() {
  return (
    <div className="max-w-3xl space-y-4 text-lg leading-relaxed text-zinc-300">
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
  );
}
