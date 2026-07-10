// The honest empty state. A block whose result is not computed yet renders here
// instead of a placeholder number: it states what will appear (label), why it is
// not here yet (reason), and what result would prove the plan wrong (falsify).
// The falsify line is a hard requirement, not decoration: a pending without a
// falsify condition is not honest, it is a promise. See docs PROVENANCE.md.

export default function Pending({
  label,
  reason,
  falsify,
}: {
  label: string;
  reason: string;
  falsify: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-zinc-700 bg-zinc-900/30 p-5">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center rounded-full border border-dashed border-zinc-600 px-2.5 py-0.5 text-xs font-mono text-zinc-400">
          pending
        </span>
        <span className="text-sm font-semibold text-zinc-200">{label}</span>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-zinc-400">{reason}</p>
      <p className="mt-3 text-xs leading-relaxed text-zinc-500">
        <span className="font-mono uppercase tracking-wide text-zinc-400">what would falsify it</span>{" "}
        {falsify}
      </p>
    </div>
  );
}
