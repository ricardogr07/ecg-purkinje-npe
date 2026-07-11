// Per-section provenance chip. Provenance is per section, never a page banner
// (results.real.json can be is_mock:true and activation_is_real:true at once, so
// a single banner would contradict one half). Kinds:
//   real         wired to the emitted artifact
//   precomputed  real numbers, baked at build time from a named run
//   illustrative mock data, explicitly labelled
//   pending      not computed yet (rendered via the Pending primitive, not here)
// The chip carries a short note stating exactly which numbers it is vouching for.

export type Provenance = "real" | "precomputed" | "illustrative" | "pending";

const TONES: Record<Provenance, string> = {
  real: "border-emerald-500/50 text-emerald-300 bg-emerald-500/10",
  precomputed: "border-indigo-500/50 text-indigo-300 bg-indigo-500/10",
  illustrative: "border-amber-500/50 text-amber-300 bg-amber-500/10",
  pending: "border-dashed border-zinc-600 text-zinc-400",
};

export default function ProvenanceChip({ kind, note }: { kind: Provenance; note?: string }) {
  // Real/precomputed data needs no per-panel label: the honesty rule is only about
  // never presenting MOCK as real. Stay silent for genuine data so the chip stops
  // repeating "precomputed" on every panel, and auto-returns (amber) if is_mock flips.
  if (kind === "real" || kind === "precomputed") return null;
  return (
    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
      <span
        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-mono ${TONES[kind]}`}
      >
        {kind}
      </span>
      {note ? <span className="text-xs text-zinc-500">{note}</span> : null}
    </div>
  );
}
