# Reproducing ecg-purkinje-npe

How to regenerate the posteriors, the calibration diagnostics, and the container images from the
released artifacts. CPU-only, no GPU. All identifiability numbers are at the observation-noise floor:
white Gaussian sigma = 0.025 mV per sample per lead, applied to the physiological-mV forward before
feature extraction.

## Release bundle

The submission release carries the artifacts needed to regenerate the results without re-training:

| asset | what it is |
|---|---|
| `day3_7d_snr_ckpt.npz` | the headline features sweep (`theta`, features `x_noised`) that the reported NPE trains on |
| `day4_wave_ckpt.npz` | the paired waveform sweep (`theta`, features `x_noised`, full 12-lead waveforms `x_wave`) for the features-vs-waveform CRLB comparison |
| `release_posterior.pt` + `release_posterior.json` | the portable trained NPE checkpoint (flow weights + metadata; no project-code pickling, so it loads without the source on `sys.path`) |
| `hl_tarp_results.json` | the shipped Contract-B artifact: posterior, SBC ranks, coverage curve, TARP pre/post conformal |
| `crlb_comparison.json`, `f3_contraction_vs_n.json`, `jacobian_raw.npz` | the CRLB, budget-convergence, and raw-Jacobian analysis artifacts |

The Docker image is deliberately NOT attached: at 5.76 GB it exceeds GitHub's 2 GB per-file release
limit. Build it from source (below); the recorded build ids are in the release notes.

## Environment

Python >= 3.11, managed by [uv](https://docs.astral.sh/uv/). CPU-only torch is pinned in
`pyproject.toml` (the PyTorch CPU index).

```
uv sync
uv run --no-sync pytest        # full suite
```

Source is importable via pytest's `pythonpath` or `PYTHONPATH=src`.

## Regenerate the headline NPE checkpoint (and verify it matches the shipped posteriors)

The reported posteriors come from a features NPE trained on `day3_7d_snr_ckpt.npz` at n_train=1000,
n_calib=250, n_post=300, seed 0. The reproducer regenerates `release_posterior.{pt,json}` and asserts
it reproduces `ui/mock/results.real.json` bit-for-bit:

```
.venv/Scripts/python.exe experiments/emit_headline_checkpoint.py
```

## Build the container images from source

Both images pin the stack via `pyproject.toml` + `uv.lock`.

CLI / pipeline image:

```
docker build -f Dockerfile.cli -t conduction-lens --build-arg GIT_SHA=$(git rev-parse --short HEAD) .
docker run --rm conduction-lens --help
docker run --rm -v "$PWD/runs:/app/runs" conduction-lens run --geometry crtdemo --dry-run --out runs/d
```

Demo image (FastAPI `/infer` + the static UI on one URL):

```
make bind-artifact ARTIFACT=outputs/hl_tarp_results.json   # stage the real Contract-B artifact
docker build -f Dockerfile.demo -t conduction-lens-demo .
docker run --rm -p 8000:8000 conduction-lens-demo          # http://localhost:8000
```

Image ids vary across machines and build dates (layer timestamps), so treat them as a record, not a
content hash; for byte-stable reproduction, build from the release tag's pinned `Dockerfile.*` +
`uv.lock`. The recorded build ids for this release are in the release notes.
