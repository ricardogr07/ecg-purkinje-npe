"use client";

import { useMemo } from "react";
import { results } from "@/lib/artifact";
import { EmptyState } from "@/components/Layout";

// 12-lead ECG: observed waveform (input) overlaid with the posterior-predictive
// mean + uncertainty band. Pure SVG, one small panel per lead. Any missing block
// degrades gracefully: no ECG -> placeholder; no predictive -> observed only;
// no band -> mean line only.

const PANEL_W = 190;
const PANEL_H = 92;
const PAD_X = 6;
const PAD_Y = 10;

function linePath(vals: number[], xOf: (i: number) => number, yOf: (v: number) => number): string {
  let d = "";
  for (let i = 0; i < vals.length; i++) {
    d += `${i === 0 ? "M" : "L"} ${xOf(i).toFixed(1)} ${yOf(vals[i]).toFixed(1)} `;
  }
  return d.trim();
}

function areaPath(
  hi: number[],
  lo: number[],
  xOf: (i: number) => number,
  yOf: (v: number) => number,
): string {
  let d = "";
  for (let i = 0; i < hi.length; i++) d += `${i === 0 ? "M" : "L"} ${xOf(i).toFixed(1)} ${yOf(hi[i]).toFixed(1)} `;
  for (let i = lo.length - 1; i >= 0; i--) d += `L ${xOf(i).toFixed(1)} ${yOf(lo[i]).toFixed(1)} `;
  return `${d}Z`;
}

export default function EcgOverlay() {
  const ecg = results.input_ecg;
  const pp = results.posterior_predictive_ecg;

  const scale = useMemo(() => {
    if (!ecg?.signal?.length) return null;
    let maxAbs = 0;
    const scan = (m?: number[][]) => {
      if (!m) return;
      for (const lead of m) for (const v of lead) maxAbs = Math.max(maxAbs, Math.abs(v));
    };
    scan(ecg.signal);
    scan(pp?.band_lo);
    scan(pp?.band_hi);
    maxAbs = maxAbs || 1;
    const yMax = maxAbs * 1.1;
    return { yMax };
  }, [ecg, pp]);

  if (!ecg?.signal?.length || !scale) {
    return <EmptyState label="No ECG in this run (input_ecg missing)." />;
  }

  const leads = ecg.leads ?? ecg.signal.map((_, i) => `Lead ${i + 1}`);
  const T = ecg.signal[0].length;
  const xOf = (i: number) => PAD_X + (i / (T - 1)) * (PANEL_W - 2 * PAD_X);
  const yOf = (v: number) =>
    PANEL_H / 2 - (v / scale.yMax) * (PANEL_H / 2 - PAD_Y);

  const hasBand = !!(pp?.band_lo?.length && pp?.band_hi?.length);
  const hasMean = !!pp?.signal?.length;

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
        {ecg.signal.map((lead, li) => {
          const bandPath =
            hasBand && pp?.band_lo?.[li] && pp?.band_hi?.[li]
              ? areaPath(pp.band_hi[li], pp.band_lo[li], xOf, yOf)
              : "";
          return (
            <figure
              key={leads[li]}
              className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-1"
              aria-label={`Lead ${leads[li]} observed ECG with posterior-predictive band`}
            >
              <svg viewBox={`0 0 ${PANEL_W} ${PANEL_H}`} className="w-full h-auto">
                {/* baseline */}
                <line
                  x1={PAD_X}
                  y1={PANEL_H / 2}
                  x2={PANEL_W - PAD_X}
                  y2={PANEL_H / 2}
                  className="stroke-zinc-800"
                  strokeWidth="0.5"
                />
                {bandPath ? (
                  <path d={bandPath} className="fill-indigo-500/25" stroke="none" />
                ) : null}
                {hasMean && pp?.signal?.[li] ? (
                  <path
                    d={linePath(pp.signal[li], xOf, yOf)}
                    fill="none"
                    className="stroke-indigo-400/80"
                    strokeWidth="1"
                  />
                ) : null}
                <path
                  d={linePath(lead, xOf, yOf)}
                  fill="none"
                  className="stroke-emerald-300"
                  strokeWidth="1.1"
                />
                <text x={PAD_X + 1} y={12} className="fill-zinc-400 font-mono text-[9px]">
                  {leads[li]}
                </text>
              </svg>
            </figure>
          );
        })}
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-zinc-400">
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-emerald-300" /> Observed input
        </span>
        {hasMean ? (
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-4 bg-indigo-400" /> Posterior-predictive mean
          </span>
        ) : null}
        {hasBand ? (
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-4 rounded-sm bg-indigo-500/25" /> 90% predictive band
          </span>
        ) : null}
        {ecg.fs_hz ? <span className="text-zinc-600">fs = {ecg.fs_hz} Hz</span> : null}
      </div>
    </div>
  );
}
