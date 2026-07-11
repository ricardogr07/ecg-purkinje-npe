"""Contract C API: /health, /infer (fallback + real artifact), /geometry via TestClient."""

import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from api.app import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "git_sha" in body


def test_infer_fallback_is_valid_contract_b():
    r = client.post("/infer", json={"geometry_id": "cardiac_demo", "observation_kind": "features"})
    assert r.status_code == 200
    b = r.json()
    for key in ("run_id", "geometry_id", "theta_names", "posterior"):
        assert key in b
    assert b["geometry_id"] == "cardiac_demo"
    post = b["posterior"]
    # posterior mean/std amendment present.
    assert "prior_bounds" in post
    assert post["prior_bounds"]["cv"] == [1.3, 3.5]  # frozen cv floor lowered 1.5 -> 1.3 (Jul 8)
    if post.get("samples"):
        assert set(post["mean"]) and set(post["std"])


def test_infer_loads_real_artifact(tmp_path, monkeypatch):
    art = {
        "run_id": "r1",
        "geometry_id": "strocchi_01",
        "theta_names": ["cv", "w"],
        "posterior": {"samples": [[2.0, 0.10], [2.2, 0.12]]},
    }
    f = tmp_path / "day3_results.json"
    f.write_text(json.dumps(art), encoding="utf-8")
    monkeypatch.setenv("ECG_ARTIFACT", str(f))
    r = client.post("/infer", json={"geometry_id": "strocchi_01"})
    assert r.status_code == 200
    b = r.json()
    assert b["run_id"] == "r1"
    # mean derived from samples; prior_bounds attached from the frozen table.
    assert b["posterior"]["mean"]["cv"] == pytest.approx(2.1)
    assert b["posterior"]["prior_bounds"]["cv"] == [1.3, 3.5]


def test_geometry():
    r = client.get("/geometry/cardiac_demo")
    assert r.status_code == 200
    assert r.json()["geometry_id"] == "cardiac_demo"
