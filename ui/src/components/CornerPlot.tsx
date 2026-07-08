"use client";

import {
  PARAM_ORDER,
  paramMeta,
  priorRange,
  results,
  sampleColumn,
  pearson,
  type ParamKey,
} from "@/lib/artifact";
import { identifiabilityColor } from "@/lib/colormap";
import { EmptyState } from "@/components/Layout";

// Corner / degeneracy matrix over the 7 parameters. Lower triangle: pairwise
// posterior scatter. Diagonal: marginal histogram, colored by identifiability,
// with the synthetic-truth marker. Upper triangle: correlation heat. The
// cv <-> init_length_lv ridge is highlighted as the headline degeneracy.

const CELL = 76;
const GUT = 42;
const PAD = 6;
const MAX_PTS = 220;

const RIDGE: [ParamKey, ParamKey] = ["cv", "init_length_lv"];

function heat(r: number): string {
  // -1 (blue) .. 0 (transparent) .. +1 (red)
  const a = Math.min(0.85, Math.abs(r) * 0.9);
  return r >= 0 ? `rgba(244,63,94,${a})` : `rgba(56,124,246,${a})`;
}

// Derived from module-level artifact data (constant across renders); the
// component itself is stateless and renders once.
function buildData() {
  const cols = PARAM_ORDER.map((k) => sampleColumn(k));
  if (!cols.length || !cols[0].length) return null;
  const ranges = PARAM_ORDER.map((k, i) => {
    const pr = priorRange(k);
    if (pr) return pr;
    const c = cols[i];
    return [Math.min(...c), Math.max(...c)] as [number, number];
  });
  const n = cols[0].length;
  const step = Math.max(1, Math.floor(n / MAX_PTS));
  const idx: number[] = [];
  for (let i = 0; i < n; i += step) idx.push(i);
  const corr = PARAM_ORDER.map((_, i) =>
    PARAM_ORDER.map((_, j) => (i === j ? 1 : pearson(cols[i], cols[j]))),
  );
  return { cols, ranges, idx, corr };
}

export default function CornerPlot() {
  const data = buildData();

  if (!data) return <EmptyState label="No posterior samples in this run." />;

  const { cols, ranges, idx, corr } = data;
  const N = PARAM_ORDER.length;
  const W = GUT + N * CELL + 6;
  const H = N * CELL + GUT + 6;
  const truth = results.reference_theta;

  const cellX = (col: number) => GUT + col * CELL;
  const cellY = (row: number) => row * CELL;
  const xIn = (col: number, v: number) => {
    const [lo, hi] = ranges[col];
    return cellX(col) + PAD + ((v - lo) / (hi - lo || 1)) * (CELL - 2 * PAD);
  };
  const yIn = (row: number, v: number) => {
    const [lo, hi] = ranges[row];
    return cellY(row) + PAD + (1 - (v - lo) / (hi - lo || 1)) * (CELL - 2 * PAD);
  };

  const ridgeI = PARAM_ORDER.indexOf(RIDGE[1]);
  const ridgeJ = PARAM_ORDER.indexOf(RIDGE[0]);
  const isRidge = (row: number, col: number) =>
    (row === ridgeI && col === ridgeJ) || (row === ridgeJ && col === ridgeI);

  function histBars(row: number) {
    const c = cols[row];
    const [lo, hi] = ranges[row];
    const B = 16;
    const counts = new Array(B).fill(0);
    for (const v of c) {
      const b = Math.min(B - 1, Math.max(0, Math.floor(((v - lo) / (hi - lo || 1)) * B)));
      counts[b]++;
    }
    const mx = Math.max(...counts) || 1;
    const w = (CELL - 2 * PAD) / B;
    return counts.map((ct, b) => {
      const h = (ct / mx) * (CELL - 2 * PAD);
      return {
        x: cellX(row) + PAD + b * w,
        y: cellY(row) + CELL - PAD - h,
        w: Math.max(1, w - 0.5),
        h,
      };
    });
  }

  return (
    <figure aria-label="Posterior corner plot over 7 conduction parameters, highlighting the cv to init_length_lv degeneracy ridge">
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full min-w-[520px] max-w-3xl" role="img">
          {PARAM_ORDER.map((_, row) =>
            PARAM_ORDER.map((__, col) => {
              const x = cellX(col);
              const y = cellY(row);
              const ridge = isRidge(row, col);
              return (
                <g key={`${row}-${col}`}>
                  <rect
                    x={x}
                    y={y}
                    width={CELL}
                    height={CELL}
                    className={ridge ? "fill-amber-400/5" : "fill-transparent"}
                    stroke={ridge ? "#fbbf24" : "#27272a"}
                    strokeWidth={ridge ? 1.4 : 0.5}
                  />
                  {/* diagonal: marginal histogram */}
                  {row === col
                    ? (() => {
                        const ident = identifiabilityColor(
                          results.posterior?.contraction?.[PARAM_ORDER[row]],
                        );
                        return (
                          <g>
                            {histBars(row).map((bar, bi) => (
                              <rect
                                key={bi}
                                x={bar.x}
                                y={bar.y}
                                width={bar.w}
                                height={bar.h}
                                fill={ident.hex}
                                opacity={0.7}
                              />
                            ))}
                            {truth?.[PARAM_ORDER[row]] !== undefined ? (
                              <line
                                x1={xIn(row, truth[PARAM_ORDER[row]]!)}
                                y1={cellY(row) + PAD}
                                x2={xIn(row, truth[PARAM_ORDER[row]]!)}
                                y2={cellY(row) + CELL - PAD}
                                stroke="#fbbf24"
                                strokeWidth={1.2}
                                strokeDasharray="2 2"
                              />
                            ) : null}
                          </g>
                        );
                      })()
                    : null}
                  {/* lower triangle: scatter */}
                  {row > col
                    ? (
                        <g>
                          {idx.map((si) => (
                            <circle
                              key={si}
                              cx={xIn(col, cols[col][si])}
                              cy={yIn(row, cols[row][si])}
                              r={0.9}
                              className={ridge ? "fill-amber-300" : "fill-indigo-400"}
                              opacity={ridge ? 0.55 : 0.4}
                            />
                          ))}
                          {truth?.[PARAM_ORDER[col]] !== undefined &&
                          truth?.[PARAM_ORDER[row]] !== undefined ? (
                            <circle
                              cx={xIn(col, truth[PARAM_ORDER[col]]!)}
                              cy={yIn(row, truth[PARAM_ORDER[row]]!)}
                              r={2.4}
                              className="fill-none stroke-amber-300"
                              strokeWidth={1.4}
                            />
                          ) : null}
                        </g>
                      )
                    : null}
                  {/* upper triangle: correlation heat */}
                  {row < col ? (
                    <g>
                      <rect x={x + 1} y={y + 1} width={CELL - 2} height={CELL - 2} fill={heat(corr[row][col])} />
                      <text
                        x={x + CELL / 2}
                        y={y + CELL / 2 + 4}
                        textAnchor="middle"
                        className="fill-zinc-100 font-mono"
                        fontSize={ridge ? 15 : 12}
                        fontWeight={ridge ? 700 : 400}
                      >
                        {corr[row][col].toFixed(2)}
                      </text>
                    </g>
                  ) : null}
                </g>
              );
            }),
          )}
          {/* bottom axis labels */}
          {PARAM_ORDER.map((k, col) => (
            <text
              key={`bx-${k}`}
              x={cellX(col) + CELL / 2}
              y={N * CELL + 16}
              textAnchor="middle"
              className="fill-zinc-400 font-mono"
              fontSize={10}
            >
              {paramMeta(k).alias}
            </text>
          ))}
          {/* left axis labels */}
          {PARAM_ORDER.map((k, row) => (
            <text
              key={`ly-${k}`}
              x={GUT - 6}
              y={cellY(row) + CELL / 2}
              textAnchor="end"
              className="fill-zinc-400 font-mono"
              fontSize={10}
            >
              {paramMeta(k).alias}
            </text>
          ))}
        </svg>
      </div>
      <figcaption className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-zinc-400">
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-indigo-400" /> posterior samples
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full border border-amber-300" /> synthetic truth
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm border border-amber-400 bg-amber-400/10" />{" "}
          cv to L0_LV ridge (corr {corr[ridgeI][ridgeJ].toFixed(2)})
        </span>
        <span className="text-zinc-600">upper cells: Pearson correlation (red +, blue -)</span>
      </figcaption>
    </figure>
  );
}
