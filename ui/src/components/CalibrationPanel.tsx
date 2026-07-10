"use client";

import { useState } from "react";
import { PARAM_ORDER, paramMeta, results } from "@/lib/artifact";
import { EmptyState } from "@/components/Layout";
import Pending from "@/components/Pending";

// Calibration panel: is the uncertainty honest? Simulation-based calibration
// (SBC) rank histograms per parameter, with a BEFORE vs AFTER conformal toggle:
// overconfident posteriors give U-shaped ranks; conformal recalibration flattens
// them. This checks the MARGINALS, one parameter at a time.
//
// TARP (expected coverage) is deliberately NOT shown as joint-calibration
// evidence: the number on hand is pre-conformal (it describes the raw posterior
// before the fix), so presenting it here would be dishonest. It is gated behind a
// Pending until the post-conformal joint ATC is recomputed on the production emit
// re-run. See docs/demo-page-brief.md section 4.

type Mode = "before" | "after";

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

  if (!cal || !cal.sbc) {
    return <EmptyState label="No calibration diagnostics in this run." />;
  }

  const sbcIsHistogram = Object.values(cal.sbc ?? {}).some(
    (v) => Array.isArray(v.before) || Array.isArray(v.after),
  );

  return (
    <div>
      {/* toggle */}
      <div className="flex flex-wrap items-center gap-3">
        <div
          className="inline-flex rounded-lg border border-zinc-700 p-0.5"
          role="group"
          aria-label="Calibration stage"
        >
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
            : "conformal-recalibrated, ranks flatten"}
        </span>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {/* SBC rank histograms: the marginals, one parameter at a time */}
        <div>
          <h3 className="mb-2 text-sm font-semibold text-zinc-200">
            {sbcIsHistogram ? "SBC rank histograms (per parameter)" : "SBC KS p-values (per parameter)"}
          </h3>
          <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
            {PARAM_ORDER.map((k) => {
              const v = cal.sbc?.[k]?.[mode];
              if (v === undefined) return null;
              return (
                <div key={k} className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-2">
                  <div className="mb-1 font-mono text-[10px] text-zinc-400">{paramMeta(k).alias}</div>
                  {Array.isArray(v) ? (
                    <RankHist counts={v} mode={mode} />
                  ) : (
                    // Real runs emit a p-value per param, not rank counts: no bars to draw.
                    <div
                      className={`font-mono text-lg ${v > 0.05 ? "text-emerald-300" : "text-rose-300"}`}
                    >
                      {v.toFixed(3)}
                      <span className="ml-1.5 font-sans text-[9px] text-zinc-500">SBC KS p</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          <p className="mt-2 text-xs text-zinc-500">
            {sbcIsHistogram
              ? "Flat = well calibrated. U-shaped = overconfident, a hump = underconfident. The dashed line is the uniform expectation. These are marginal checks, one parameter at a time."
              : "SBC rank-uniformity test per parameter, p above 0.05 (green) does not reject calibration."}
          </p>
        </div>

        {/* TARP joint coverage: gated, not shown as evidence while pre-conformal */}
        <div>
          <h3 className="mb-2 text-sm font-semibold text-zinc-200">
            Joint coverage after conformal (TARP)
          </h3>
          <Pending
            label="Post-conformal joint coverage (TARP)"
            reason="The expected-coverage (TARP) number on hand is pre-conformal: it describes the raw posterior before the recalibration fix, so it is not evidence the joint is calibrated. The post-conformal joint ATC is recomputed on the production emit re-run, then it appears here."
            falsify="If the post-conformal TARP curve does not land on the diagonal, the conformal step fixes the marginals but not the joint, and the joint intervals cannot be trusted."
          />
        </div>
      </div>
    </div>
  );
}
