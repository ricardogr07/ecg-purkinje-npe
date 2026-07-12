// Sticky nav: section links + the paper. No provenance strip: the noise floor
// travels in-panel with the identifiability spectrum (the hero teaser and the
// finding section both print it), so the qualifier still cannot be cropped from
// the claim.

const LINKS = [
  { href: "#finding", label: "Finding" },
  { href: "#why", label: "Why" },
  { href: "#how", label: "Pipeline" },
  { href: "#spectrum", label: "Spectrum" },
  { href: "#calibration", label: "Calibration" },
  { href: "#correlation", label: "Correlation" },
  { href: "#reproduce", label: "Reproduce" },
];

export default function Header() {
  return (
    <nav
      aria-label="Section navigation"
      className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur"
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <a href="#finding" className="flex items-center gap-2 text-sm font-bold text-zinc-100">
          <span aria-hidden="true" className="text-indigo-400">
            ◎
          </span>
          Conduction Lens
        </a>
        <div className="hidden items-center gap-5 text-sm lg:flex">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="text-zinc-400 hover:text-indigo-300">
              {l.label}
            </a>
          ))}
          <a
            href="https://doi.org/10.5281/zenodo.21315609"
            className="text-zinc-400 hover:text-indigo-300"
          >
            Paper
          </a>
        </div>
      </div>
    </nav>
  );
}
