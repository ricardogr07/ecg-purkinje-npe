// The question the paper asks, as the section-01 lead, with its one-line answer
// underneath. Serif headline to read like a manuscript. No hedging, no jargon:
// it must land in ninety seconds. The spectrum below is the proof. The brand
// masthead (Conduction Lens) lives above this in BrandHero.
export default function Hero() {
  return (
    <div>
      <h2 className="font-serif text-4xl font-semibold tracking-tight text-zinc-50 sm:text-5xl">
        Which conduction parameters can an ECG actually determine?
      </h2>
      <p className="mt-5 text-lg leading-relaxed text-zinc-300 sm:text-xl">
        We trained a calibrated neural posterior estimator to answer it, one parameter at a time, at
        a stated noise floor.
      </p>
      <p className="mt-5 text-sm leading-relaxed text-zinc-500">
        Amortized neural posterior estimation over seven conduction parameters at fixed anatomy,
        graded with simulation based calibration on the simulator. Synthetic target, no patient
        data.
      </p>
    </div>
  );
}
