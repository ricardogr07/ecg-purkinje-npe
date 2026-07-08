# conduction_lens: build + run helpers. Two CPU-only images (CLI runner + demo server).
GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
ARTIFACT ?= outputs/day3_7d_snr_results.json

.PHONY: test lint cli-image demo-image bind-artifact demo-run cli-dryrun

test:
	uv run pytest -q

lint:
	uv run ruff check .

# --- CLI / pipeline image ---
cli-image:
	docker build -f Dockerfile.cli --build-arg GIT_SHA=$(GIT_SHA) -t conduction-lens .

cli-dryrun: cli-image
	docker run --rm -v "$(CURDIR)/runs:/app/runs" conduction-lens run --geometry crtdemo --dry-run --out runs/docker_dry

# --- Demo server image ---
# Bake the real Contract-B artifact into the UI bundle + the API before building the demo.
bind-artifact:
	cp "$(ARTIFACT)" ui/mock/results.json

demo-image:
	docker build -f Dockerfile.demo --build-arg GIT_SHA=$(GIT_SHA) -t conduction-lens-demo .

demo-run: demo-image
	docker run --rm -p 8000:8000 conduction-lens-demo
