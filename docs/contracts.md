# Interface contracts

These interfaces decouple the pipeline components (parameters, results artifact, demo API, noise
model). Change them carefully: the sweep, the emitter, the demo, and the write-up all depend on them.

---

## Contract A, θ schema

The 7D parameter vector. Names, ranges, units.

| name | block | units | prior (uniform) | notes |
|---|---|---|---|---|
| `cv` | constraint | m/s | [lo, hi] TBD | global conduction velocity → QRS duration |
| `delta_iv` | constraint | ms | [lo, hi] TBD | LV-RV interventricular delay → axis/morphology |
| `init_length_lv` | constraint | mm | [lo, hi] TBD | LV early-activation extent |
| `init_length_rv` | constraint | mm | [lo, hi] TBD | RV early-activation extent |
| `branch_angle` | diffuse | rad | [lo, hi] TBD | fine topology |
| `w` | diffuse | - | [lo, hi] TBD | branch divergence / PMJ spread |

**Frozen: 7 parameters, canonical code-name order.** These supersede the TBD placeholders above. Ranges are literature-grounded and independent of the thesis `BOECGParameter` bounds (provenance and citations: `docs/research-brief.md` Appendix A).

| # | name | unit | [lo, hi] |
|---|---|---|---|
| 0 | `cv` | m/s | [1.3, 3.5]  (floor lowered from 1.5 to bracket crtdemo's true ~1.4 interior) |
| 1 | `delta_iv` | ms | [-90, 40]  (dyssynchrony regime) |
| 2 | `init_length_lv` | mm | [30, 60] |
| 3 | `init_length_rv` | mm | [30, 60] |
| 4 | `branch_angle` | rad | [0.10, 0.30] |
| 5 | `w` | - | [0.05, 0.20] |
| 6 | `cv_myo` | m/s | [0.5, 1.0]  (inferred as the 7th parameter) |

Canonical order = the table order. Serialize as a JSON object keyed by name; never rely on positional order across module boundaries. The observation-noise model is **Contract D** (`docs/research-brief.md` Appendix B).

---

## Contract B, results artifact

One JSON per inference run. The frontend, the figures, and the write-up all read this shape.

```jsonc
{
  "run_id": "string",
  "geometry_id": "strocchi_01 | cardiac_demo",
  "theta_names": ["cv","delta_iv","init_length_lv","init_length_rv","branch_angle","w","cv_myo"],
  "observation_kind": "features | waveform",
  "input_ecg": { "leads": ["I","II",...], "signal": [[...12 leads x T...]], "fs_hz": 500 },
  "posterior": {
    "samples": [[...7 floats...]],        // for the corner/degeneracy plot
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

## Contract C, demo API

FastAPI response shapes.

- `GET  /geometry/{geometry_id}` → mesh for the 3D view (surface + fields).
- `POST /infer` → body `{geometry_id, input_ecg, observation_kind}` → **Contract B** artifact.
- `GET  /health` → `{status:"ok", git_sha}`.

Keep it one origin (uvicorn in one task, no CORS).
