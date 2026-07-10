// Sticky header + provenance strip. The strip carries the run's factual metadata
// (run id, noise floor, geometry) and states that the page is a static export.
// It is NOT a real/mock provenance banner: results.real.json can be is_mock:true
// and activation_is_real:true at once, so that distinction lives per section in
// ProvenanceChip, never here. All values read from the artifact, never hard-coded.
import { results } from "@/lib/artifact";

const LINKS = [
  { href: "#finding", label: "Finding" },
  { href: "#why", label: "Why" },
  { href: "#how", label: "How" },
  { href: "#calibration", label: "Calibration" },
  { href: "#correlation", label: "Correlation" },
  { href: "#corrections", label: "Corrections" },
  { href: "#reproduce", label: "Reproduce" },
];

export default function Header() {
  const nm = results.noise_model ?? {};
  const noiseFloor =
    nm.amp_sigma_mv !== undefined && nm.timing_sigma_ms !== undefined
      ? `${nm.amp_sigma_mv} mV amplitude, ${nm.timing_sigma_ms} ms timing`
      : nm.sigma !== undefined
        ? `${nm.sigma} mV`
        : undefined;

  return (
    <>
      <nav
        aria-label="Section navigation"
        className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur"
      >
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <a href="#finding" className="flex items-center gap-2 text-sm font-bold text-zinc-100">
            <span aria-hidden="true" className="text-indigo-400">
              {"</>"}
            </span>
            ECG to Purkinje
          </a>
          <div className="hidden items-center gap-5 text-sm lg:flex">
            {LINKS.map((l) => (
              <a key={l.href} href={l.href} className="text-zinc-400 hover:text-indigo-300">
                {l.label}
              </a>
            ))}
            <a
              href="https://github.com/ricardogr07/ecg-purkinje-npe"
              className="text-zinc-400 hover:text-indigo-300"
            >
              Paper
            </a>
          </div>
        </div>
      </nav>

      {/* provenance strip: factual run metadata + delivery mechanism */}
      <div className="sticky top-14 z-40 border-b border-zinc-800 bg-zinc-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-1 px-4 py-1.5 font-mono text-[11px] text-zinc-500">
          {results.run_id ? (
            <span>
              run <span className="text-zinc-300">{results.run_id}</span>
            </span>
          ) : null}
          {noiseFloor ? (
            <span aria-hidden="true" className="text-zinc-700">
              ·
            </span>
          ) : null}
          {noiseFloor ? (
            <span>
              noise floor <span className="text-zinc-300">{noiseFloor}</span>
            </span>
          ) : null}
          {results.geometry_id ? (
            <>
              <span aria-hidden="true" className="text-zinc-700">
                ·
              </span>
              <span>
                geometry <span className="text-zinc-300">{results.geometry_id}</span>
              </span>
            </>
          ) : null}
          <span className="ml-auto inline-flex items-center gap-1.5">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
            precomputed static export
          </span>
        </div>
      </div>
    </>
  );
}
