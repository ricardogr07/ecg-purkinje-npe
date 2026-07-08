// Sticky header with storyboard anchor nav. Mirrors the shelter-pulse NavBar
// idiom (backdrop blur, zinc border) without the i18n machinery.
const LINKS = [
  { href: "#observation", label: "Observation" },
  { href: "#degeneracy", label: "Degeneracy" },
  { href: "#identifiability", label: "Pinned / unknowable" },
  { href: "#calibration", label: "Calibration" },
];

export default function Header() {
  return (
    <nav
      aria-label="Section navigation"
      className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur"
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <a href="#top" className="flex items-center gap-2 text-sm font-bold text-zinc-100">
          <span aria-hidden="true" className="text-indigo-400">
            {"</>"}
          </span>
          ECG to Purkinje
        </a>
        <div className="hidden items-center gap-6 text-sm md:flex">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="text-zinc-400 hover:text-indigo-300">
              {l.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
