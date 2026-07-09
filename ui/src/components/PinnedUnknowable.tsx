"use client";

import { PARAM_ORDER, paramSummary, type ParamSummary } from "@/lib/artifact";
import { identifiabilityColor } from "@/lib/colormap";
import { Chip, EmptyState } from "@/components/Layout";

// The "pinned vs unknowable" reveal, driven by the contraction spectrum. For
// each parameter we draw the prior range as a track and overlay the posterior
// 90% interval: a narrow segment means the ECG pinned it, a segment that nearly
// fills the prior means the ECG cannot resolve it.

function fmt(v: number | undefined, unit: string): string {
  if (v === undefined || Number.isNaN(v)) return "-";
  const abs = Math.abs(v);
  const dp = unit === "ms" || abs >= 20 ? 0 : abs >= 1 ? 2 : 3;
  return v.toFixed(dp);
}

function Row({ s }: { s: ParamSummary }) {
  const ident = identifiabilityColor(s.contraction);
  const pr = s.prior;
  const ci = s.ci90;
  const hasBar = !!(pr && ci);
  let leftPct = 0;
  let widthPct = 0;
  let truthPct: number | null = null;
  if (pr) {
    const span = pr[1] - pr[0] || 1;
    if (ci) {
      leftPct = ((ci[0] - pr[0]) / span) * 100;
      widthPct = ((ci[1] - ci[0]) / span) * 100;
    }
    if (s.truth !== undefined) truthPct = ((s.truth - pr[0]) / span) * 100;
  }
  const barColor =
    ident.label === "pinned"
      ? "bg-emerald-400"
      : ident.label === "unknowable"
        ? "bg-rose-400"
        : "bg-amber-400";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-[190px_1fr_150px] items-center gap-x-4 gap-y-1 py-3 border-b border-zinc-800/70">
      <div>
        <div className="font-mono text-sm text-zinc-100">{s.meta.alias}</div>
        <div className="text-xs text-zinc-500">{s.meta.label}</div>
      </div>
      <div>
        {hasBar ? (
          <div
            className="relative h-6 overflow-hidden rounded-md bg-zinc-800/80 border border-zinc-700/60"
            role="img"
            aria-label={`${s.meta.alias}: posterior 90% interval ${fmt(ci![0], s.meta.unit)} to ${fmt(ci![1], s.meta.unit)} ${s.meta.unit} within prior ${fmt(pr![0], s.meta.unit)} to ${fmt(pr![1], s.meta.unit)}`}
          >
            <div
              className={`absolute top-0 h-full rounded ${barColor} opacity-80`}
              style={{ left: `${leftPct}%`, width: `${Math.max(widthPct, 1)}%` }}
            />
            {truthPct !== null ? (
              <div
                className="absolute top-[-3px] h-[30px] w-0.5 bg-amber-200"
                style={{ left: `${Math.min(99, Math.max(0, truthPct))}%` }}
                title="synthetic truth"
              />
            ) : null}
          </div>
        ) : (
          <div className="text-xs text-zinc-500">prior/interval unavailable</div>
        )}
        <div className="mt-0.5 flex justify-between font-mono text-[10px] text-zinc-600">
          <span>{pr ? fmt(pr[0], s.meta.unit) : ""}</span>
          <span>{s.meta.unit === "-" ? "prior range" : `prior range (${s.meta.unit})`}</span>
          <span>{pr ? fmt(pr[1], s.meta.unit) : ""}</span>
        </div>
      </div>
      <div className="text-right">
        <div className={`text-sm font-semibold ${ident.cls}`}>
          {s.contraction !== undefined ? s.contraction.toFixed(2) : "-"}
        </div>
        <div className="text-[10px] uppercase tracking-wide text-zinc-500">{ident.label}</div>
      </div>
    </div>
  );
}

export default function PinnedUnknowable() {
  const summaries = PARAM_ORDER.map(paramSummary).filter((s) => s.contraction !== undefined);
  if (!summaries.length) return <EmptyState label="No contraction spectrum in this run." />;

  const sorted = [...summaries].sort((a, b) => (a.contraction ?? 1) - (b.contraction ?? 1));
  const pinned = sorted[0];
  const unknowable = sorted[sorted.length - 1];

  return (
    <div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5">
          <Chip tone="emerald">most pinned</Chip>
          <div className="mt-3 font-mono text-2xl text-emerald-300">{pinned.meta.alias}</div>
          <p className="mt-1 text-sm text-zinc-300">{pinned.meta.label}</p>
          <p className="mt-3 text-sm text-zinc-400">
            The ECG narrows it to about{" "}
            <span className="font-mono text-emerald-300">
              {fmt(pinned.ci90?.[0], pinned.meta.unit)} to {fmt(pinned.ci90?.[1], pinned.meta.unit)}{" "}
              {pinned.meta.unit === "-" ? "" : pinned.meta.unit}
            </span>{" "}
            (90% interval), keeping only{" "}
            <span className="font-mono text-emerald-300">
              {Math.round((pinned.contraction ?? 0) * 100)}%
            </span>{" "}
            of the prior width.
          </p>
        </div>
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/5 p-5">
          <Chip tone="rose">essentially unknowable</Chip>
          <div className="mt-3 font-mono text-2xl text-rose-300">{unknowable.meta.alias}</div>
          <p className="mt-1 text-sm text-zinc-300">{unknowable.meta.label}</p>
          <p className="mt-3 text-sm text-zinc-400">
            The posterior still spans{" "}
            <span className="font-mono text-rose-300">
              {fmt(unknowable.ci90?.[0], unknowable.meta.unit)} to{" "}
              {fmt(unknowable.ci90?.[1], unknowable.meta.unit)}{" "}
              {unknowable.meta.unit === "-" ? "" : unknowable.meta.unit}
            </span>
            , keeping{" "}
            <span className="font-mono text-rose-300">
              {Math.round((unknowable.contraction ?? 0) * 100)}%
            </span>{" "}
            of the prior. The surface ECG barely constrains it.
          </p>
        </div>
      </div>

      <div className="mt-8">
        {sorted.map((s) => (
          <Row key={s.key} s={s} />
        ))}
      </div>
      <p className="mt-4 text-xs text-zinc-500">
        Contraction = posterior std / prior std, per parameter. Lower is better identified. Bars show
        the posterior 90% interval inside the prior range; the amber tick is the synthetic truth.
      </p>
    </div>
  );
}
