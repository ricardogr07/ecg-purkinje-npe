"""FastAPI backend, Contract C (Code <-> Design). One origin, no CORS (shelter-pulse pattern).

Endpoints:
  GET  /health                -> {status, git_sha}
  POST /infer                 -> Contract-B artifact (load-and-serve; real NPE swaps in Day 4->5)
  GET  /geometry/{geometry_id} -> mesh descriptor for the 3D view

Served in one nginx + uvicorn task; the frontend is same-origin so no CORS is configured.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from . import artifact

app = FastAPI(title="ecg-purkinje-npe", version="0.1.0")


class InferRequest(BaseModel):
    geometry_id: str = "cardiac_demo"
    observation_kind: str = "features"
    input_ecg: dict[str, Any] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "git_sha": artifact.git_sha()}


@app.post("/infer")
def infer(req: InferRequest) -> dict[str, Any]:
    art = artifact.load()
    # Echo the request context onto the served artifact (real inference conditions on
    # input_ecg at the Day 4->5 swap; tonight the artifact is the mock/real snapshot).
    art["geometry_id"] = req.geometry_id or art.get("geometry_id")
    art["observation_kind"] = req.observation_kind or art.get("observation_kind")
    if req.input_ecg is not None:
        art["input_ecg"] = req.input_ecg
    return art


@app.get("/geometry/{geometry_id}")
def geometry(geometry_id: str) -> dict[str, Any]:
    return artifact.geometry_view(geometry_id, artifact.load())


# Serve the built Next.js static export (out/) same-origin when UI_DIR points at it (demo image).
# Mounted last so the API routes above win; absent in the CLI image and in tests (no UI_DIR).
_ui_dir = os.environ.get("UI_DIR")
if _ui_dir and Path(_ui_dir).is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=_ui_dir, html=True), name="ui")
