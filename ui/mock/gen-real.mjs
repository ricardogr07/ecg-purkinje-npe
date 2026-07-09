// Regenerates ui/mock/results.real.json from the LATEST real Science artifact
// (outputs/day3_*results*.json), so the static-export bake is never stale.
// Wired as `prebuild` in package.json, so it runs before every `next build`
// (both the S3 static-export build and the Dockerfile.demo image build).
//
// geometry.real.json (the crtdemo mesh + real LV/RV Purkinje trees) is NOT
// touched here: day3 result files carry no mesh, that file's real source is
// experiments/export_geometry.py (a separate, Science-owned export). This
// script only regenerates the numeric Contract-B artifact, and overlays the
// real activation_map that export_geometry.py already merged into the
// committed results.real.json when the day3 artifact doesn't carry its own
// (none currently do; activation_map is an optional Contract-B block).
//
// Never fails the build: if outputs/ has no day3 artifact (e.g. a fresh
// worktree checkout, or CI without a populated outputs/), the existing
// committed results.real.json is left untouched.
//
// Run:  node ui/mock/gen-real.mjs

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(HERE, "..", "..");
const OUTPUTS_DIR = join(REPO_ROOT, "outputs");
const RESULTS_REAL = join(HERE, "results.real.json");

function latestDay3() {
  if (!existsSync(OUTPUTS_DIR)) return null;
  // Mirrors src/api/artifact.py::_resolve_path: sorted(...)[-1], newest by filename.
  const hits = readdirSync(OUTPUTS_DIR).filter((f) => /^day3_.*results.*\.json$/.test(f));
  hits.sort();
  return hits.length ? join(OUTPUTS_DIR, hits[hits.length - 1]) : null;
}

const src = latestDay3();
if (!src) {
  console.log("[gen-real] no outputs/day3_*results*.json found; leaving results.real.json as committed.");
  process.exit(0);
}

const day3 = JSON.parse(readFileSync(src, "utf8"));
const existing = existsSync(RESULTS_REAL) ? JSON.parse(readFileSync(RESULTS_REAL, "utf8")) : {};
const realActivation = day3.activation_map ?? existing.activation_map;

const merged = {
  ...day3,
  activation_map: realActivation,
  meta: {
    ...day3.meta,
    is_mock: false,
    activation_is_real: Boolean(realActivation),
    baked_from: basename(src),
  },
};

writeFileSync(RESULTS_REAL, JSON.stringify(merged));
console.log(`[gen-real] wrote results.real.json from ${basename(src)} (run_id=${merged.run_id})`);
