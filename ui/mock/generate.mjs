// Deterministic generator for the Contract-B MOCK bundle (Design track, Day 2).
//
// Produces:
//   results.json   a faithful Contract-B artifact (7-param theta, 12-lead ECG,
//                  ~1500 posterior samples with a deliberate cv <-> init_length_lv
//                  ridge, contraction + coverage, calibration extension block).
//   geometry.json  a biventricular surface (LV + RV parametric shells) with
//                  per-vertex chamber labels; the per-vertex activation (LAT)
//                  lives in results.json activation_map.values, indexed 1:1.
//
// These are MOCK numbers, chosen to be physiologically plausible and consistent
// with the Day-2 identifiability snapshot (delta_iv tightest, branch_angle
// loosest, a cv/init_length_lv ridge). They are NOT measured results. The real
// artifact from Contract B replaces this file wholesale at the Day 4 to 5 sync.
//
// Run:  node ui/mock/generate.mjs
// Deterministic: fixed seed, byte-stable output.

import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));

// ---- seeded RNG (mulberry32) + gaussian (Box-Muller) ---------------------
function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(1234);
function gauss() {
  let u = 0;
  let v = 0;
  while (u === 0) u = rand();
  while (v === 0) v = rand();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

// ---- Contract A: frozen 7-param theta ------------------------------------
const THETA_NAMES = [
  "cv",
  "delta_iv",
  "init_length_lv",
  "init_length_rv",
  "branch_angle",
  "w",
  "cv_myo",
];
// [lo, hi] per FREEZE_AND_PLAN.md / contracts.md Contract A.
const PRIOR = {
  cv: [1.5, 3.5],
  delta_iv: [-90, 40],
  init_length_lv: [30, 60],
  init_length_rv: [30, 60],
  branch_angle: [0.1, 0.3],
  w: [0.05, 0.2],
  cv_myo: [0.5, 1.0],
};
// Display aliases + units + block, so the UI never has to invent labels.
const PARAM_META = {
  cv: { alias: "CV_pk", unit: "m/s", block: "constraint", label: "Purkinje conduction velocity" },
  delta_iv: { alias: "dIV", unit: "ms", block: "constraint", label: "Interventricular delay (LV to RV)" },
  init_length_lv: { alias: "L0_LV", unit: "mm", block: "constraint", label: "LV early-activation extent" },
  init_length_rv: { alias: "L0_RV", unit: "mm", block: "constraint", label: "RV early-activation extent" },
  branch_angle: { alias: "theta_b", unit: "rad", block: "diffuse", label: "Fascicle branch angle" },
  w: { alias: "w", unit: "-", block: "diffuse", label: "Branch divergence / PMJ spread" },
  cv_myo: { alias: "CV_myo", unit: "m/s", block: "constraint", label: "Myocardial conduction velocity" },
};

// Synthetic ground truth (this is a synthetic-truth identifiability study, not a
// real patient). Values sit inside the prior box.
const REFERENCE_THETA = {
  cv: 2.2,
  delta_iv: -75,
  init_length_lv: 50,
  init_length_rv: 50,
  branch_angle: 0.175,
  w: 0.1,
  cv_myo: 0.67,
};

// Contraction = posterior_std / prior_std. Consistent with Day-2: delta_iv the
// tightest ("pinned"), branch_angle the loosest ("unknowable"), and a
// cv <-> init_length_lv ridge that loosens both marginals.
const CONTRACTION = {
  delta_iv: 0.19,
  cv: 0.34,
  cv_myo: 0.42,
  init_length_lv: 0.58,
  init_length_rv: 0.66,
  w: 0.83,
  branch_angle: 0.91,
};
// Empirical central-interval coverage AFTER conformal calibration (nominal 0.90).
const COVERAGE = {
  cv: 0.9,
  delta_iv: 0.91,
  init_length_lv: 0.89,
  init_length_rv: 0.9,
  branch_angle: 0.92,
  w: 0.88,
  cv_myo: 0.9,
};

const priorStd = (name) => {
  const [lo, hi] = PRIOR[name];
  return (hi - lo) / Math.sqrt(12);
};

// ---- posterior samples with a deliberate cv <-> init_length_lv ridge ------
const N_SAMPLES = 1500;
const RIDGE_RHO = -0.9; // strong negative correlation = the degeneracy ridge
function makeSamples() {
  const samples = [];
  const mu = REFERENCE_THETA;
  const sd = {};
  for (const n of THETA_NAMES) sd[n] = CONTRACTION[n] * priorStd(n);
  for (let i = 0; i < N_SAMPLES; i++) {
    // correlated pair (cv, init_length_lv)
    const z1 = gauss();
    const z2 = gauss();
    const cv = mu.cv + sd.cv * z1;
    const illv =
      mu.init_length_lv +
      sd.init_length_lv * (RIDGE_RHO * z1 + Math.sqrt(1 - RIDGE_RHO * RIDGE_RHO) * z2);
    const row = {
      cv,
      delta_iv: mu.delta_iv + sd.delta_iv * gauss(),
      init_length_lv: illv,
      init_length_rv: mu.init_length_rv + sd.init_length_rv * gauss(),
      branch_angle: mu.branch_angle + sd.branch_angle * gauss(),
      w: mu.w + sd.w * gauss(),
      cv_myo: mu.cv_myo + sd.cv_myo * gauss(),
    };
    // keep inside the prior box (physiological support)
    const vec = THETA_NAMES.map((n) => clamp(row[n], PRIOR[n][0], PRIOR[n][1]));
    samples.push(vec);
  }
  return samples;
}

// ---- 12-lead ECG (QRS-dominant single beat) -------------------------------
const LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"];
const FS = 500;
const T = 400; // 0.8 s window
// Per-lead morphology signs/scales for a normal-ish beat (illustrative).
const LEAD_SHAPE = {
  //        P     Q      R      S      T
  I: [0.08, -0.02, 0.7, -0.05, 0.18],
  II: [0.12, -0.03, 1.1, -0.05, 0.28],
  III: [0.05, -0.02, 0.5, -0.08, 0.12],
  aVR: [-0.08, 0.0, -0.8, 0.0, -0.22],
  aVL: [0.04, -0.03, 0.35, -0.06, 0.08],
  aVF: [0.09, -0.02, 0.8, -0.06, 0.2],
  V1: [0.05, 0.0, 0.25, -0.9, -0.15],
  V2: [0.06, 0.0, 0.5, -1.4, 0.3],
  V3: [0.07, -0.02, 0.9, -0.9, 0.4],
  V4: [0.08, -0.04, 1.5, -0.3, 0.45],
  V5: [0.09, -0.05, 1.3, -0.12, 0.35],
  V6: [0.08, -0.04, 1.0, -0.08, 0.25],
};
function gaussPulse(t, center, width, amp) {
  const z = (t - center) / width;
  return amp * Math.exp(-0.5 * z * z);
}
// One beat template for a lead, sampled at times (ms). QRS ~ 100 ms wide.
function beat(shape, t, jitter = 0) {
  const [P, Q, R, S, Tw] = shape;
  const pC = 120,
    qC = 205 + jitter,
    rC = 220 + jitter,
    sC = 238 + jitter,
    tC = 360;
  return (
    gaussPulse(t, pC, 12, P) +
    gaussPulse(t, qC, 6, Q) +
    gaussPulse(t, rC, 9, R) +
    gaussPulse(t, sC, 8, S) +
    gaussPulse(t, tC, 40, Tw)
  );
}
const NOISE_MV = 0.025; // Contract D waveform sigma
function makeEcg() {
  const times = Array.from({ length: T }, (_, i) => (i / FS) * 1000); // ms
  const observed = [];
  const ppMean = [];
  const ppLo = [];
  const ppHi = [];
  const K = 40; // posterior-predictive ensemble size
  for (let li = 0; li < LEADS.length; li++) {
    const shape = LEAD_SHAPE[LEADS[li]];
    const obs = times.map((t) => beat(shape, t) + NOISE_MV * gauss());
    // ensemble with small QRS-timing + amplitude variation
    const ens = [];
    for (let k = 0; k < K; k++) {
      const j = 6 * gauss(); // ms QRS jitter
      const ampScale = 1 + 0.06 * gauss();
      ens.push(times.map((t) => ampScale * beat(shape, t, j)));
    }
    const mean = times.map((_, ti) => ens.reduce((a, e) => a + e[ti], 0) / K);
    const lo = [];
    const hi = [];
    for (let ti = 0; ti < T; ti++) {
      const col = ens.map((e) => e[ti]).sort((a, b) => a - b);
      lo.push(col[Math.floor(0.05 * K)]); // ~5th pct
      hi.push(col[Math.floor(0.95 * K)]); // ~95th pct
    }
    observed.push(obs);
    ppMean.push(mean);
    ppLo.push(lo);
    ppHi.push(hi);
  }
  return { times, observed, ppMean, ppLo, ppHi };
}

// ---- biventricular surface + per-vertex activation (LAT) ------------------
// Two parametric ellipsoid shells (LV full, RV free-wall crescent). Faces from
// the (theta, phi) grid. Activation = distance from initiation sites / cv, with
// an interventricular offset on the RV.
function ellipsoidShell({ a, b, c, center, nTheta, nPhi, thetaMax, phiRange, chamber }) {
  const verts = [];
  const faces = [];
  const [px, py, pz] = center;
  const [phi0, phi1] = phiRange;
  for (let i = 0; i < nTheta; i++) {
    const th = (i / (nTheta - 1)) * thetaMax; // 0 = apex
    for (let j = 0; j < nPhi; j++) {
      const ph = phi0 + (j / (nPhi - 1)) * (phi1 - phi0);
      const x = px + a * Math.sin(th) * Math.cos(ph);
      const y = py + b * Math.sin(th) * Math.sin(ph);
      const z = pz - c * Math.cos(th); // apex at -c
      verts.push([x, y, z]);
    }
  }
  const idx = (i, j) => i * nPhi + j;
  for (let i = 0; i < nTheta - 1; i++) {
    for (let j = 0; j < nPhi - 1; j++) {
      faces.push([idx(i, j), idx(i + 1, j), idx(i + 1, j + 1)]);
      faces.push([idx(i, j), idx(i + 1, j + 1), idx(i, j + 1)]);
    }
  }
  const chambers = verts.map(() => chamber);
  return { verts, faces, chambers };
}

function makeGeometry() {
  const lv = ellipsoidShell({
    a: 24,
    b: 24,
    c: 42,
    center: [0, 0, 0],
    nTheta: 26,
    nPhi: 48,
    thetaMax: (115 * Math.PI) / 180,
    phiRange: [0, 2 * Math.PI],
    chamber: 0,
  });
  const rv = ellipsoidShell({
    a: 30,
    b: 22,
    c: 40,
    center: [24, 0, 2],
    nTheta: 24,
    nPhi: 34,
    thetaMax: (112 * Math.PI) / 180,
    phiRange: [(-105 * Math.PI) / 180, (105 * Math.PI) / 180],
    chamber: 1,
  });
  const verts = [...lv.verts, ...rv.verts];
  const off = lv.verts.length;
  const faces = [...lv.faces, ...rv.faces.map((f) => f.map((v) => v + off))];
  const chambers = [...lv.chambers, ...rv.chambers];
  return { verts, faces, chambers };
}

function makeActivation(geom) {
  // Initiation sites: LV septal + LV apex + RV septal (His/Purkinje first junctions).
  const lvSites = [
    [6, 0, -20], // LV apical-septal
    [-4, 10, -6], // LV mid free wall
  ];
  const rvSites = [
    [28, 2, -16], // RV apical
  ];
  const cv = REFERENCE_THETA.cv; // mm/ms == m/s
  const rvOffset = 18; // ms interventricular offset (illustrative from delta_iv)
  const dist = (p, q) =>
    Math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2);
  const values = geom.verts.map((v, i) => {
    const isRv = geom.chambers[i] === 1;
    const sites = isRv ? rvSites : lvSites;
    let dmin = Infinity;
    for (const s of sites) dmin = Math.min(dmin, dist(v, s));
    let lat = dmin / cv; // ms
    if (isRv) lat += rvOffset;
    return lat;
  });
  return values;
}

// ---- calibration extension block ------------------------------------------
// SBC rank histograms per param (nBins counts) + a coverage/TARP curve, both
// BEFORE and AFTER conformal calibration. Contract B does not yet name these
// fields; the real artifact is expected to carry them (see mock/README.md).
function makeCalibration() {
  const nBins = 20;
  const nRanks = 400;
  // Before conformal: overconfident => U-shaped ranks (mass at the edges).
  // After conformal: closer to uniform.
  function ranks(uShape) {
    const counts = new Array(nBins).fill(0);
    for (let i = 0; i < nRanks; i++) {
      let r = rand();
      if (uShape > 0) {
        // push mass toward 0 and 1
        r = r < 0.5 ? r * (1 - uShape) : 1 - (1 - r) * (1 - uShape);
        if (rand() < uShape * 0.5) r = rand() < 0.5 ? rand() * 0.1 : 1 - rand() * 0.1;
      }
      counts[Math.min(nBins - 1, Math.floor(r * nBins))]++;
    }
    return counts;
  }
  const sbc = {};
  for (const n of THETA_NAMES) {
    sbc[n] = { before: ranks(0.55), after: ranks(0.06) };
  }
  // Expected-coverage (TARP) curve: nominal vs empirical.
  const nominal = Array.from({ length: 11 }, (_, i) => i / 10);
  const before = nominal.map((p) => clamp(p - 0.14 * Math.sin(Math.PI * p), 0, 1)); // below diagonal = overconfident
  const after = nominal.map((p) => clamp(p - 0.02 * Math.sin(Math.PI * p) + 0.01 * gauss() * 0, 0, 1));
  return {
    method: "SBC + TARP + conformal",
    nominal_level: 0.9,
    n_sbc_ranks: nRanks,
    sbc_bins: nBins,
    sbc,
    coverage_curve: { nominal, before, after },
    sbc_ks_pvalue: { before: 0.017, after: 0.242 },
    tarp_atc: { before: -0.096, after: -0.012 },
    conformal_t: {
      cv: 1.28,
      delta_iv: 1.22,
      init_length_lv: 1.35,
      init_length_rv: 1.31,
      branch_angle: 1.19,
      w: 1.26,
      cv_myo: 1.24,
    },
  };
}

// ---- assemble + write ------------------------------------------------------
function round(obj, dp) {
  const f = (x) => (typeof x === "number" && Number.isFinite(x) ? Number(x.toFixed(dp)) : x);
  const walk = (o) => {
    if (Array.isArray(o)) return o.map(walk);
    if (o && typeof o === "object") {
      const r = {};
      for (const k of Object.keys(o)) r[k] = walk(o[k]);
      return r;
    }
    return f(o);
  };
  return walk(obj);
}

const geom = makeGeometry();
const activation = makeActivation(geom);
const ecg = makeEcg();
const samples = makeSamples();

const results = {
  run_id: "mock-cardiac-demo-0001",
  geometry_id: "cardiac_demo",
  synthetic_truth: true,
  theta_names: THETA_NAMES,
  observation_kind: "features",
  prior: PRIOR,
  param_meta: PARAM_META,
  reference_theta: REFERENCE_THETA,
  input_ecg: {
    leads: LEADS,
    fs_hz: FS,
    times_ms: round(ecg.times, 2),
    signal: round(ecg.observed, 4),
  },
  posterior: {
    samples: round(samples, 4),
    contraction: CONTRACTION,
    coverage: COVERAGE,
  },
  posterior_predictive_ecg: {
    leads: LEADS,
    signal: round(ecg.ppMean, 4),
    band_lo: round(ecg.ppLo, 4),
    band_hi: round(ecg.ppHi, 4),
  },
  activation_map: {
    mesh_ref: "cardiac_demo",
    units: "ms",
    values: round(activation, 1),
  },
  calibration: makeCalibration(),
  // Spectrum/identifiability floor is the applied WAVEFORM sigma only. The feature-channel
  // floor (0.05 mV / 5 ms) belongs to the CRLB-vs-CRLB comparison, not this artifact; keeping
  // it here made the header (Header.tsx) show the wrong floor if the mock is ever imported.
  noise_model: { kind: "waveform", sigma: NOISE_MV },
  meta: {
    sim_budget: 5000,
    sbi_method: "NPE",
    seed: 1234,
    n_posterior_samples: N_SAMPLES,
    git_sha: "mock",
    note: "MOCK artifact. Synthetic-truth identifiability. Not a real-patient fit.",
  },
};

const geometry = {
  geometry_id: "cardiac_demo",
  units: "mm",
  n_vertices: geom.verts.length,
  n_faces: geom.faces.length,
  chambers: ["LV", "RV"],
  vertices: round(geom.verts, 2),
  faces: geom.faces,
  chamber: geom.chambers,
};

writeFileSync(join(HERE, "results.json"), JSON.stringify(results));
writeFileSync(join(HERE, "geometry.json"), JSON.stringify(geometry));

console.log(
  `wrote results.json (${LEADS.length} leads x ${T} samples, ${N_SAMPLES} posterior samples)`,
);
console.log(
  `wrote geometry.json (${geom.verts.length} vertices, ${geom.faces.length} faces, ${activation.length} LAT values)`,
);
