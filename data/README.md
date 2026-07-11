# data/

The public anatomy this project runs on. **Only this README and a `.gitkeep` are committed** here.
The raw meshes are hundreds of MB of CC-BY data that lives on Zenodo, so they are downloaded, not
vendored (see `.gitignore`).

## What we use

**Strocchi et al. 2020**, a virtual cohort of 24 four-chamber heart meshes.
Zenodo record `3890034`, DOI [10.5281/zenodo.3890034](https://doi.org/10.5281/zenodo.3890034),
licensed **CC-BY-4.0**. Cite it if you use it.

This project runs its method-generality demo on **heart 01** (and heart 02 for the gallery),
**coarse 1.1 mm** mesh. No identifiability result is claimed on any Strocchi heart; the identifiability
study runs on the bundled crtdemo geometry, which ships in-repo under `packages/purkinje-uv`.

## Get heart 01

1. Download `01.tar.gz` (about 821 MB) from the Zenodo record above.
2. Extract it here so the EnSight case file lands at `data/01/01.case`:

   ```
   tar -xzf 01.tar.gz -C data/
   ```

   You then have `data/01/01.case`, `data/01/01.geo`, the fiber/sheet `.ens` fields, and the
   `01_uvc_*.ens` universal-ventricular-coordinate files. Heart 02 is `02.tar.gz` into `data/02/`.

## Reproduce the Strocchi forward

The adapter (`src/adapter/strocchi.py`) reads `data/01/01.case`, ingests the myocardium, fibers, and
UVC-placed electrodes (caching the derived inputs under `data/01/_forward_inputs/`), grows the LV/RV
Purkinje trees on the heart's own universal ventricular coordinates, and runs the literal forward
chain once:

```
uv run --no-sync python experiments/strocchi_forward.py
uv run --no-sync python experiments/strocchi_forward.py --case data/02/02.case --geom-id strocchi_02 --out-base strocchi_02
```

This is slow: the eikonal on the roughly 338k-point mesh takes minutes. It writes the decimated demo
geometry and activation to `ui/mock/geometry.strocchi.json` and `results.strocchi.json`.

## Just want to see the result?

The decimated Strocchi 01 and 02 activation geometries are already committed under `ui/mock/` and
render in the demo, so you can view the method-generality result without downloading anything.

## Sizes (heart 01, for planning)

| item | size |
|---|---|
| `01.tar.gz` download | about 821 MB |
| extracted raw inputs (`01.geo`, `.ens` fields, UVC) | about 155 MB |
| regenerated forward cache (`_forward_inputs/*.vtk`) | about 210 MB |
