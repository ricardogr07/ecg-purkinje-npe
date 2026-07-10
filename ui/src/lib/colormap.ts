// Small perceptual colormap (viridis anchors) for the activation map, plus a
// couple of shared color helpers. No dependency, just linear interpolation
// between anchor RGB stops.

const VIRIDIS: [number, number, number][] = [
  [68, 1, 84],
  [72, 40, 120],
  [62, 74, 137],
  [49, 104, 142],
  [38, 130, 142],
  [31, 158, 137],
  [53, 183, 121],
  [110, 206, 88],
  [181, 222, 43],
  [253, 231, 37],
];

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

// t in [0, 1] -> "rgb(r,g,b)"
export function viridis(t: number): [number, number, number] {
  const x = Math.max(0, Math.min(1, t)) * (VIRIDIS.length - 1);
  const i = Math.floor(x);
  const f = x - i;
  const c0 = VIRIDIS[i];
  const c1 = VIRIDIS[Math.min(VIRIDIS.length - 1, i + 1)];
  return [
    Math.round(lerp(c0[0], c1[0], f)),
    Math.round(lerp(c0[1], c1[1], f)),
    Math.round(lerp(c0[2], c1[2], f)),
  ];
}

export function rgb([r, g, b]: [number, number, number], alpha = 1): string {
  return alpha >= 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${alpha})`;
}

// Identifiability -> semantic color, at a stated noise floor. Low contraction =
// resolved (emerald), mid = partial (amber), high = unresolved (grey). A parameter
// is unresolved at THIS noise floor and may resolve at a lower one, never a claim
// about the absolute. Thresholds are the spectrum's meaning: change only via a
// DECISIONS entry (docs PROVENANCE.md, colormap thresholds).
export function identifiabilityColor(contraction: number | undefined): {
  cls: string;
  hex: string;
  label: "resolved" | "partial" | "unresolved";
} {
  if (contraction === undefined || Number.isNaN(contraction)) {
    return { cls: "text-zinc-400", hex: "#a1a1aa", label: "partial" };
  }
  if (contraction <= 0.45) return { cls: "text-emerald-400", hex: "#34d399", label: "resolved" };
  if (contraction <= 0.6) return { cls: "text-amber-400", hex: "#fbbf24", label: "partial" };
  return { cls: "text-zinc-400", hex: "#a1a1aa", label: "unresolved" };
}
