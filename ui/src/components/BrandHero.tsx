// Centered brand masthead at the very top of the page, above section 01. Landing
// hero styling: the large wordmark with a gradient accent on "Lens", and the
// one-line tagline. The manuscript proper starts below at "01 / the question".
// This carries the page's single h1; the section-01 question is an h2.
export default function BrandHero() {
  return (
    <section className="relative overflow-hidden border-b border-zinc-800">
      {/* ponytail: faint grid backdrop via inline style, robust across Tailwind versions */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px)," +
            "linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "44px 44px",
          maskImage: "radial-gradient(ellipse 60% 60% at 50% 38%, black, transparent 82%)",
          WebkitMaskImage: "radial-gradient(ellipse 60% 60% at 50% 38%, black, transparent 82%)",
        }}
      />
      <div className="relative mx-auto max-w-3xl px-4 py-20 text-center sm:py-28">
        <h1 className="font-serif text-5xl font-semibold tracking-tight text-zinc-50 sm:text-6xl">
          Conduction{" "}
          <span className="bg-linear-to-r from-cyan-300 to-indigo-400 bg-clip-text text-transparent">
            Lens
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-zinc-300 sm:text-xl">
          A calibrated lens on cardiac conduction: what a 12-lead ECG can and cannot resolve about
          the His-Purkinje system.
        </p>
      </div>
    </section>
  );
}
