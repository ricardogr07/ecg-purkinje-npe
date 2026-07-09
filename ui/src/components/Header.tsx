// Sticky header with storyboard anchor nav. Mirrors the shelter-pulse NavBar
// idiom (backdrop blur, zinc border) without the i18n machinery.
import { results } from "@/lib/artifact";

const LINKS = [
  { href: "#observation", label: "Observation" },
  { href: "#degeneracy", label: "Degeneracy" },
  { href: "#identifiability", label: "Pinned / unknowable" },
  { href: "#calibration", label: "Calibration" },
];

export default function Header() {
  // Demo-honesty rule (CLAUDE.md): a surface rendering mock data MUST be labeled illustrative
  // until it is wired to the real artifact. mock/gen-real.mjs stamps meta.is_mock: false when it
  // bakes a real outputs/day3_*results*.json in (see ui/mock/README.md); the committed fallback
  // (no real run available at build time) keeps meta.is_mock: true.
  const meta = (results.meta ?? {}) as Record<string, unknown>;
  const isMock = Boolean(meta.is_mock);
  const activationReal = Boolean(meta.activation_is_real);
  const gitSha = typeof meta.git_sha === "string" ? meta.git_sha : undefined;
  const bakedFrom = typeof meta.baked_from === "string" ? meta.baked_from : undefined;
  return (
    <>
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
      {isMock ? (
        <div
          role="note"
          className="border-b border-amber-500/40 bg-amber-500/10 px-4 py-2 text-center text-xs text-amber-200"
        >
          {activationReal ? (
            <>
              The <span className="font-semibold">activation map and 12-lead ECG are real</span>{" "}
              (forward model at the honest operating point). The{" "}
              <span className="font-semibold">posterior and calibration panels are illustrative</span>{" "}
              mock, real calibrated posteriors are served by the API at{" "}
              <code className="rounded bg-black/30 px-1">/infer</code>. Synthetic-truth, not
              real-ECG-validated.
            </>
          ) : (
            <>
              <span className="font-semibold">Illustrative demo.</span> These visualizations use
              representative <span className="font-semibold">mock</span> data; real calibrated
              posteriors are served at{" "}
              <code className="rounded bg-black/30 px-1">/infer</code>.
            </>
          )}
        </div>
      ) : (
        <div
          role="note"
          className="border-b border-zinc-800 bg-zinc-900/60 px-4 py-2 text-center text-xs text-zinc-400"
        >
          <span className="font-semibold text-zinc-300">Precomputed from a real run</span>:{" "}
          <code className="rounded bg-black/30 px-1">{results.run_id}</code>
          {gitSha ? (
            <>
              {" "}
              (commit <code className="rounded bg-black/30 px-1">{gitSha}</code>)
            </>
          ) : null}
          {bakedFrom ? <> from <code className="rounded bg-black/30 px-1">{bakedFrom}</code></> : null}.
          Static export, values are baked at build time, not fetched live.
          {results.synthetic_truth ? " Synthetic-truth study, not a real-patient fit." : ""}
        </div>
      )}
    </>
  );
}
