"use client";

import { PARAM_ORDER, paramSummary, results, type ParamSummary } from "@/lib/artifact";
import { identifiabilityColor } from "@/lib/colormap";
import { EmptyState } from "@/components/Layout";

// The finding: a per-parameter contraction spectrum. For each parameter we draw
// the prior range as a track and overlay the posterior 90% interval. A narrow
// segment means the ECG resolved it; a segment that nearly fills the prior means
// the ECG does not resolve it AT THIS NOISE FLOOR, never in the absolute (it may
// resolve at a lower floor). The noise floor travels in the header so a screenshot
// cannot crop the qualifier.
// Bars are coloured by contraction today; colour moves to CRLB later (the one
// pending in the hero). The printed contraction number does not change.

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
    ident.label === "resolved"
      ? "bg-emerald-400"
      : ident.label === "moderate"
        ? "bg-amber-400"
        : "bg-zinc-500";

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
            aria-label={`${s.meta.alias}: posterior 90% interval ${fmt(ci![0], s.meta.unit)} to ${fmt(ci![1], s.meta.unit)} ${s.meta.unit} within prior ${fmt(pr![0], s.meta.unit)} to ${fmt(pr![1], s.meta.unit)}, ${ident.label} at this noise floor`}
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

export default function IdentifiabilitySpectrum({ compact = false }: { compact?: boolean } = {}) {
  const summaries = PARAM_ORDER.map(paramSummary).filter((s) => s.contraction !== undefined);
  if (!summaries.length) return <EmptyState label="No contraction spectrum in this run." />;

  const sorted = [...summaries].sort((a, b) => (a.contraction ?? 1) - (b.contraction ?? 1));
  const resolved = sorted[0];
  const mostDiffuse = sorted[sorted.length - 1];
  // Tier counts from the shared colormap so bars, row labels, and this header agree.
  const tier = (c: number | undefined) => identifiabilityColor(c).label;
  const nWell = summaries.filter((s) => tier(s.contraction) === "resolved").length;
  const nMod = summaries.filter((s) => tier(s.contraction) === "moderate").length;
  const nDiffuse = summaries.length - nWell - nMod;
  const countLabel = `${nWell + nMod} of ${summaries.length} carry information (${nWell} well resolved, ${nMod} moderate); ${nDiffuse} diffuse`;

  // The noise floor travels with the claim, in the header (PROVENANCE rule 2).
  const nm = results.noise_model;
  const noiseFloor =
    nm?.amp_sigma_mv !== undefined && nm?.timing_sigma_ms !== undefined
      ? `${nm.amp_sigma_mv} mV amplitude, ${nm.timing_sigma_ms} ms timing`
      : nm?.sigma !== undefined
        ? `${nm.sigma} mV`
        : null;

  // Compact teaser (hero): the bars are the proof, no framing cards or footer.
  // The floor is not repeated here (the hero subhead says "at a stated noise
  // floor"); the number travels with the full finding in section 04.
  if (compact) {
    return (
      <div>
        <div className="border-b border-zinc-800 pb-3">
          <h2 className="text-sm font-semibold text-zinc-200">
            Identifiability spectrum: {countLabel}
          </h2>
        </div>
        <div className="mt-4">
          {sorted.map((s) => (
            <Row key={s.key} s={s} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 border-b border-zinc-800 pb-3">
        <h2 className="text-sm font-semibold text-zinc-200">
          Identifiability spectrum: {countLabel}
        </h2>
        {noiseFloor ? (
          <p className="font-mono text-xs text-zinc-400">at a noise floor of {noiseFloor}</p>
        ) : null}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5">
          <span className="inline-flex items-center rounded-full border border-emerald-500/50 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-mono text-emerald-300">
            most resolved
          </span>
          <div className="mt-3 font-mono text-2xl text-emerald-300">{resolved.meta.alias}</div>
          <p className="mt-1 text-sm text-zinc-300">{resolved.meta.label}</p>
          <p className="mt-3 text-sm text-zinc-400">
            The ECG narrows it to about{" "}
            <span className="font-mono text-emerald-300">
              {fmt(resolved.ci90?.[0], resolved.meta.unit)} to{" "}
              {fmt(resolved.ci90?.[1], resolved.meta.unit)}{" "}
              {resolved.meta.unit === "-" ? "" : resolved.meta.unit}
            </span>{" "}
            (90% interval), keeping only{" "}
            <span className="font-mono text-emerald-300">
              {Math.round((resolved.contraction ?? 0) * 100)}%
            </span>{" "}
            of the prior width.
          </p>
        </div>
        <div className="rounded-2xl border border-zinc-700/60 bg-zinc-800/20 p-5">
          <span className="inline-flex items-center rounded-full border border-zinc-600 px-2.5 py-0.5 text-xs font-mono text-zinc-400">
            not resolved at this noise floor
          </span>
          <div className="mt-3 font-mono text-2xl text-zinc-200">{mostDiffuse.meta.alias}</div>
          <p className="mt-1 text-sm text-zinc-300">{mostDiffuse.meta.label}</p>
          <p className="mt-3 text-sm text-zinc-400">
            The posterior still spans{" "}
            <span className="font-mono text-zinc-200">
              {fmt(mostDiffuse.ci90?.[0], mostDiffuse.meta.unit)} to{" "}
              {fmt(mostDiffuse.ci90?.[1], mostDiffuse.meta.unit)}{" "}
              {mostDiffuse.meta.unit === "-" ? "" : mostDiffuse.meta.unit}
            </span>
            , keeping{" "}
            <span className="font-mono text-zinc-200">
              {Math.round((mostDiffuse.contraction ?? 0) * 100)}%
            </span>{" "}
            of the prior. Any single value read off an ECG fit for it is a prior belief, not a
            measurement.
          </p>
        </div>
      </div>

      <div className="mt-8">
        {sorted.map((s) => (
          <Row key={s.key} s={s} />
        ))}
      </div>
      <p className="mt-4 text-xs text-zinc-500">
        Contraction = posterior std / prior std, per parameter. Lower is better resolved. Bars show
        the posterior 90% interval inside the prior range; the amber tick is the synthetic truth.
        Resolved, moderate and diffuse are stated at the noise floor above, not in the absolute.
      </p>
    </div>
  );
}
