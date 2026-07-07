# Interface Contracts (freeze by Day 2)

These three contracts decouple the tracks so they run in parallel against mocks. **Change them only with the director's sign-off**, because every track depends on them.

---

## Contract A, θ schema (Science ↔ Code)

The 6D parameter vector. Names, ranges, units. Frozen Thu Jul 9.

| name | block | units | prior (uniform) | notes |
|---|---|---|---|---|
| `cv` | constraint | m/s | [lo, hi] TBD | global conduction velocity → QRS duration |
| `delta_iv` | constraint | ms | [lo, hi] TBD | LV-RV interventricular delay → axis/morphology |
| `init_length_lv` | constraint | mm | [lo, hi] TBD | LV early-activation extent |
| `init_length_rv` | constraint | mm | [lo, hi] TBD | RV early-activation extent |
| `branch_angle` | diffuse | rad | [lo, hi] TBD | fine topology |
| `w` | diffuse | - | [lo, hi] TBD | branch divergence / PMJ spread |

Ranges come from the published `BOECGParameter` physiological bounds (flag in the eligibility question). Canonical order = the table order. Serialize as a JSON object keyed by name; never rely on positional order across module boundaries.

---

## Contract B, results artifact (Code ↔ Design ↔ Writeup)

One JSON per inference run. The frontend, the figures, and the write-up all read this shape. Design builds against a **mock** of it from Day 2.

```jsonc
{
  "run_id": "string",
  "geometry_id": "strocchi_01 | cardiac_demo",
  "theta_names": ["cv","delta_iv","init_length_lv","init_length_rv","branch_angle","w"],
  "observation_kind": "features | waveform",
  "input_ecg": { "leads": ["I","II",...], "signal": [[...12 leads x T...]], "fs_hz": 500 },
  "posterior": {
    "samples": [[...6 floats...]],        // for the corner/degeneracy plot
    "contraction": {"cv": 0.12, "...": 0.0},  // posterior_std / prior_std per param
    "coverage": {"cv": 0.94, "...": 0.0}      // empirical coverage per param
  },
  "posterior_predictive_ecg": { "signal": [[...]], "band_lo": [[...]], "band_hi": [[...]] },
  "activation_map": { "mesh_ref": "geometry_id", "values": [ ... per-node LAT ... ] },
  "noise_model": { "kind": "gaussian|waveform", "sigma": 0.0 },
  "meta": { "sim_budget": 5000, "sbi_method": "NPE", "seed": 1234, "git_sha": "..." }
}
```

Rule: a missing optional block (e.g., `activation_map`) must degrade gracefully in the UI, never crash.

---

## Contract C, demo API (Code ↔ Design)

FastAPI response shapes. Mocked Day 2; Design never waits on real inference.

- `GET  /geometry/{geometry_id}` → mesh for the 3D view (surface + fields).
- `POST /infer` → body `{geometry_id, input_ecg, observation_kind}` → **Contract B** artifact.
- `GET  /health` → `{status:"ok", git_sha}`.

Keep it one origin (nginx + uvicorn in one task, no CORS), per the shelter-pulse pattern.
