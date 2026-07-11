# IEEE / Zenodo manuscript

Self-publishable, IEEE two-column rendering of the calibrated identifiability finding.
Owned by the Cowork line. Source of truth for the numbers: `../../docs/results-summary.md`
and the `v0.1.0-submission` release artifacts.

## Build
```
python -c "import typst; typst.compile('paper.typ', output='paper.pdf')"
```
(`pip install typst` provides the bundled compiler; the charged-ieee registry package is
not required, the IEEE two-column style is vendored inline in `paper.typ`.)

## Contents
- `paper.typ`      the manuscript (self-contained IEEE template + content)
- `paper.pdf`      the built paper (7 pages)
- `refs.bib`       bibliography (copied from ../refs.bib so the folder is self-contained)
- `vancouver.csl`  citation style (numbered, hyphenated page ranges, no en dashes)
- `figures/`       the six figures used in the paper, generated from the release artifacts
- `scripts/`       figure-generation scripts (each writes into `figures/`)

## Figures (provenance)
All six are generated from the shipped artifacts, not hand-drawn:

- `fig6_crtdemo_purkinje.png`  crtdemo endocardial geometry + grown Purkinje network (`scripts/make_fig6.py`, from the endo `.obj` meshes and `f5_*_tree.vtu`)
- `fig5_pipeline.png`          pipeline schematic (`scripts/make_figures.py`)
- `fig1_contraction_spectrum.png`  calibrated contraction spectrum (`scripts/make_fig1.py`)
- `fig7_posterior_corner.png`  joint-posterior degeneracy map (`scripts/make_fig7.py`, from `hl_tarp_results.json` samples)
- `fig_calib_wide.png`         calibration: expected coverage + SBC (`scripts/make_wide.py`)
- `fig_bc_wide.png`            budget sensitivity + CRLB sufficiency gap (`scripts/make_wide.py`)

Regenerating requires the release artifacts under `../../outputs/` (`hl_tarp_results.json`,
`f3_contraction_vs_n.json`, `crlb_comparison.json`) and the geometry files.
