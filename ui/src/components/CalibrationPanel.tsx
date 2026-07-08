"use client";

import { useState } from "react";
import { PARAM_ORDER, paramMeta, results } from "@/lib/artifact";
import { Chip, EmptyState } from "@/components/Layout";

// Calibration panel: the "findings you can trust" moment. A coverage / TARP
// curve (empirical vs nominal) plus per-parameter SBC rank histograms, with a
// BEFORE vs AFTER conformal toggle. Uncalibrated posteriors sit below the
// diagonal with U-shaped ranks; conformal snaps both back.

type Mode = "before" | "after";

const CW = 320;
const CH = 240;
const CP = 34;

function CoverageCurve({ mode }: { mode: Mode }) {
  const cc = results.calibration?.coverage_curve;
  if (!cc?.nominal?.length) return null;
  const { nominal, before, after } = cc;
  const px = (v: number) => CP + v * (CW - CP - 10);
  const py = (v: number) => CH - CP - v * (CH - CP - 10);
  const path = (ys: number[]) =>
    ys.map((y, i) => `${i === 0 ? "M" : "L"} ${px(nominal[i]).toFixed(1)} ${py(y).toFixed(1)}`).join(" ");
  const ticks = [0, 0.25, 0.5, 0.75, 1];

  return (
    <svg viewBox={`0 0 ${CW} ${CH}`} className="w-full max-w-sm" role="img" aria-label="Expected coverage curve, empirical versus nominal">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={px(t)} y1={py(0)} x2={px(t)} y2={py(1)} className="stroke-zinc-800" strokeWidth={0.5} />
          <line x1={px(0)} y1={py(t)} x2={px(1)} y2={py(t)} className="stroke-zinc-800" strokeWidth={0.5} />
          <text x={px(t)} y={CH - CP + 14} textAnchor="middle" className="fill-zinc-500 text-[8px]">
            {t}
          </text>
          <text x={CP - 6} y={py(t) + 3} textAnchor="end" className="fill-zinc-500 text-[8px]">
            {t}
          </text>
        </g>
      ))}
      {/* perfect-calibration diagonal */}
      <line x1={px(0)} y1={py(0)} x2={px(1)} y2={py(1)} className="stroke-zinc-500" strokeWidth={1} strokeDasharray="3 3" />
      {/* inactive mode, faint */}
      <path d={path(mode === "after" ? before : after)} fill="none" className="stroke-zinc-700" strokeWidth={1} />
      {/* active mode */}
      <path
        d={path(mode === "after" ? after : before)}
        fill="none"
        className={mode === "after" ? "stroke-emerald-400" : "stroke-rose-400"}
        strokeWidth={2.4}
      />
      <text x={CP} y={16} className="fill-zinc-400 text-[9px]">
        empirical coverage
      </text>
      <text x={CW - 10} y={CH - CP + 26} textAnchor="end" className="fill-zinc-400 text-[9px]">
        nominal level
      </text>
    </svg>
  );
}

function RankHist({ counts, mode }: { counts: number[]; mode: Mode }) {
  const B = counts.length || 1;
  const total = counts.reduce((a, b) => a + b, 0) || 1;
  const expected = total / B;
  const mx = Math.max(...counts, expected) || 1;
  const w = 118;
  const h = 46;
  const bw = w / B;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" aria-hidden="true">
      {/* uniform expectation */}
      <line
        x1={0}
        y1={h - (expected / mx) * (h - 4)}
        x2={w}
        y2={h - (expected / mx) * (h - 4)}
        className="stroke-zinc-500"
        strokeWidth={0.6}
        strokeDasharray="2 2"
      />
      {counts.map((c, i) => {
        const bh = (c / mx) * (h - 4);
        return (
          <rect
            key={i}
            x={i * bw + 0.4}
            y={h - bh}
            width={Math.max(0.8, bw - 0.8)}
            height={bh}
            className={mode === "after" ? "fill-emerald-400/70" : "fill-rose-400/70"}
          />
        );
      })}
    </svg>
  );
}

export default function CalibrationPanel() {
  const [mode, setMode] = useState<Mode>("before");
  const cal = results.calibration;

  if (!cal || (!cal.coverage_curve && !cal.sbc)) {
    return <EmptyState label="No calibration diagnostics in this run." />;
  }

  const ks = cal.sbc_ks_pvalue?.[mode];
  const atc = cal.tarp_atc?.[mode];
  const ksPass = ks !== undefined && ks > 0.05;

  return (
    <div>
      {/* toggle */}
      <div className="flex items-center gap-3">
        <div className="inline-flex rounded-lg border border-zinc-700 p-0.5" role="group" aria-label="Calibration stage">
          {(["before", "after"] as Mode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              aria-pressed={mode === m}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                mode === m
                  ? m === "after"
                    ? "bg-emerald-500/20 text-emerald-200"
                    : "bg-rose-500/20 text-rose-200"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {m === "before" ? "Before conformal" : "After conformal"}
            </button>
          ))}
        </div>
        <span className="text-xs text-zinc-500">
          {mode === "before"
            ? "raw NPE posterior, overconfident"
            : "conformal-calibrated, trustworthy intervals"}
        </span>
      </div>

      <div className="mt-5 grid gap-6 lg:grid-cols-2">
        {/* coverage curve */}
        <div>
          <h3 className="mb-2 text-sm font-semibold text-zinc-200">Expected coverage (TARP)</h3>
          {cal.coverage_curve ? <CoverageCurve mode={mode} /> : <EmptyState label="No coverage curve." />}
          <div className="mt-2 flex flex-wrap gap-2">
            {ks !== undefined ? (
              <Chip tone={ksPass ? "emerald" : "rose"}>SBC KS p = {ks.toFixed(3)} {ksPass ? "pass" : "fail"}</Chip>
            ) : null}
            {atc !== undefined ? (
              <Chip tone={Math.abs(atc) < 0.03 ? "emerald" : "amber"}>TARP ATC = {atc.toFixed(3)}</Chip>
            ) : null}
          </div>
          <p className="mt-2 text-xs text-zinc-500">
            On the diagonal = calibrated. Below = overconfident (intervals too tight for the stated
            confidence).
          </p>
        </div>

        {/* SBC rank histograms */}
        <div>
          <h3 className="mb-2 text-sm font-semibold text-zinc-200">SBC rank histograms</h3>
          {cal.sbc ? (
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3">
              {PARAM_ORDER.map((k) => {
                const ranks = cal.sbc?.[k]?.[mode];
                if (!ranks) return null;
                return (
                  <div key={k} className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-2">
                    <div className="mb-1 font-mono text-[10px] text-zinc-400">{paramMeta(k).alias}</div>
                    <RankHist counts={ranks} mode={mode} />
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState label="No SBC ranks." />
          )}
          <p className="mt-2 text-xs text-zinc-500">
            Flat = well calibrated. U-shaped = overconfident; a hump = underconfident. Dashed line is
            the uniform expectation.
          </p>
        </div>
      </div>
    </div>
  );
}
