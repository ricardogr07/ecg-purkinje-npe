// Contract-B artifact types + a safe loader.
//
// The demo currently reads the bundled MOCK (ui/mock/*.json). To swap to the
// real backend (Contract C, Day 4 to 5 sync), replace the two imports below with
// a fetch of `POST /infer` and `GET /geometry/{id}`; every component already
// treats optional blocks as possibly-missing, so a leaner real artifact degrades
// gracefully rather than crashing.

// The activation scene (surface + LAT + Purkinje network) and the ECG are REAL, exported from the
// forward at the honest operating point (experiments/export_geometry.py). The posterior/calibration
// panels still read the illustrative mock (see the Header banner). meta.activation_is_real marks it.
import rawGeometry from "@mock/geometry.real.json";
import rawResults from "@mock/results.real.json";

export type ParamKey =
  | "cv"
  | "delta_iv"
  | "init_length_lv"
  | "init_length_rv"
  | "branch_angle"
  | "w"
  | "cv_myo";

export interface ParamMeta {
  alias: string;
  unit: string;
  block: "constraint" | "diffuse";
  label: string;
}

export interface CoverageCurve {
  nominal: number[];
  before: number[];
  after: number[];
}

export interface Calibration {
  method?: string;
  nominal_level?: number;
  n_sbc_ranks?: number;
  sbc_bins?: number;
  sbc?: Record<string, { before: number[]; after: number[] }>;
  coverage_curve?: CoverageCurve;
  sbc_ks_pvalue?: { before: number; after: number };
  tarp_atc?: { before: number; after: number };
  conformal_t?: Partial<Record<ParamKey, number>>;
}

export interface EcgBlock {
  leads: string[];
  fs_hz?: number;
  times_ms?: number[];
  signal: number[][]; // [lead][sample]
}

export interface PosteriorPredictive {
  leads?: string[];
  signal: number[][];
  band_lo?: number[][];
  band_hi?: number[][];
}

export interface ResultsArtifact {
  run_id: string;
  geometry_id: string;
  synthetic_truth?: boolean;
  theta_names: ParamKey[];
  observation_kind?: string;
  prior?: Record<ParamKey, [number, number]>;
  param_meta?: Record<ParamKey, ParamMeta>;
  reference_theta?: Partial<Record<ParamKey, number>>;
  input_ecg?: EcgBlock;
  posterior?: {
    samples?: number[][];
    contraction?: Partial<Record<ParamKey, number>>;
    coverage?: Partial<Record<ParamKey, number>>;
  };
  posterior_predictive_ecg?: PosteriorPredictive;
  activation_map?: { mesh_ref?: string; units?: string; values?: number[] };
  calibration?: Calibration;
  noise_model?: { kind?: string; sigma?: number; timing_sigma_ms?: number; amp_sigma_mv?: number };
  meta?: Record<string, unknown>;
}

export interface PurkinjeTree {
  nodes: [number, number, number][];
  edges: [number, number][];
  n_pmj?: number;
}

export interface Geometry {
  geometry_id: string;
  units?: string;
  n_vertices: number;
  n_faces: number;
  chambers?: string[];
  vertices: [number, number, number][];
  faces: [number, number, number][];
  chamber?: number[]; // per-vertex chamber index
  purkinje?: { lv: PurkinjeTree; rv: PurkinjeTree }; // the real fractal Purkinje network
}

export const results = rawResults as unknown as ResultsArtifact;
export const geometry = rawGeometry as unknown as Geometry;

// Canonical param order (Contract A). Fall back to a sane default if the
// artifact omits theta_names.
export const PARAM_ORDER: ParamKey[] =
  results.theta_names && results.theta_names.length
    ? results.theta_names
    : ["cv", "delta_iv", "init_length_lv", "init_length_rv", "branch_angle", "w", "cv_myo"];

const FALLBACK_META: Record<ParamKey, ParamMeta> = {
  cv: { alias: "CV_pk", unit: "m/s", block: "constraint", label: "Purkinje conduction velocity" },
  delta_iv: { alias: "dIV", unit: "ms", block: "constraint", label: "Interventricular delay" },
  init_length_lv: { alias: "L0_LV", unit: "mm", block: "constraint", label: "LV init length" },
  init_length_rv: { alias: "L0_RV", unit: "mm", block: "constraint", label: "RV init length" },
  branch_angle: { alias: "theta_b", unit: "rad", block: "diffuse", label: "Branch angle" },
  w: { alias: "w", unit: "-", block: "diffuse", label: "PMJ spread" },
  cv_myo: { alias: "CV_myo", unit: "m/s", block: "constraint", label: "Myocardial CV" },
};

export function paramMeta(k: ParamKey): ParamMeta {
  return results.param_meta?.[k] ?? FALLBACK_META[k];
}

export function priorRange(k: ParamKey): [number, number] | undefined {
  return results.prior?.[k];
}

// Column of posterior samples for one param, in canonical order.
export function sampleColumn(k: ParamKey): number[] {
  const samples = results.posterior?.samples;
  if (!samples || !samples.length) return [];
  const i = PARAM_ORDER.indexOf(k);
  if (i < 0) return [];
  return samples.map((row) => row[i]);
}

export function mean(xs: number[]): number {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN;
}

export function std(xs: number[]): number {
  if (xs.length < 2) return NaN;
  const m = mean(xs);
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) * (b - m), 0) / (xs.length - 1));
}

export function quantile(sorted: number[], q: number): number {
  if (!sorted.length) return NaN;
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

export function pearson(xs: number[], ys: number[]): number {
  const n = Math.min(xs.length, ys.length);
  if (n < 2) return 0;
  const mx = mean(xs);
  const my = mean(ys);
  let sxy = 0;
  let sxx = 0;
  let syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx;
    const dy = ys[i] - my;
    sxy += dx * dy;
    sxx += dx * dx;
    syy += dy * dy;
  }
  const d = Math.sqrt(sxx * syy);
  return d > 0 ? sxy / d : 0;
}

// Per-param identifiability summary, derived only from what the artifact carries.
export interface ParamSummary {
  key: ParamKey;
  meta: ParamMeta;
  contraction?: number; // posterior_std / prior_std
  coverage?: number;
  prior?: [number, number];
  postMean?: number;
  postStd?: number;
  ci90?: [number, number]; // central 90% posterior interval
  truth?: number;
}

export function paramSummary(k: ParamKey): ParamSummary {
  const col = sampleColumn(k);
  const sorted = [...col].sort((a, b) => a - b);
  const s: ParamSummary = {
    key: k,
    meta: paramMeta(k),
    contraction: results.posterior?.contraction?.[k],
    coverage: results.posterior?.coverage?.[k],
    prior: priorRange(k),
    truth: results.reference_theta?.[k],
  };
  if (col.length) {
    s.postMean = mean(col);
    s.postStd = std(col);
    s.ci90 = [quantile(sorted, 0.05), quantile(sorted, 0.95)];
  }
  return s;
}
