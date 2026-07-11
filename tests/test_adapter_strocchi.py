"""Strocchi adapter: UVC-based endocardium extraction, round-trip OBJ, and real-mesh checks.

The real algorithm (see src/adapter/strocchi.py) selects the boundary surface of the
combined tag-{lv_tag, rv_tag} cell region, then keeps only near-endocardial points
(uvc_transmural close to 0, excluding the -100 sentinel on non-ventricular nodes), split
LV/RV by the sign of uvc_intraventricular. `_tiny_tagged_mesh` (no UVC fields) exercises
the tag-presence error paths, which fire before any UVC lookup. `_tiny_uvc_mesh` (UVC
fields, LV/RV point sets kept disjoint to avoid shared-boundary-point sign ambiguity)
exercises the real extraction logic. The real-mesh test runs against the extracted
data/01/01.case (Strocchi et al. 2020, Zenodo 3890034, CC-BY-4.0) and skips cleanly if
that file isn't present in this checkout.
"""

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyvista")
pytest.importorskip("meshio")

import pyvista as pv  # noqa: E402

from adapter import strocchi  # noqa: E402

REAL_CASE_PATH = Path(__file__).resolve().parents[1] / "data" / "01" / "01.case"


def _tiny_tagged_mesh():
    # 3 triangles: two tagged LV(=1), one tagged RV(=2). No UVC fields (tag-error-path only).
    pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]], dtype=float)
    faces = np.hstack([[3, 0, 1, 2], [3, 1, 3, 2], [3, 1, 4, 3]])
    mesh = pv.PolyData(pts, faces)
    mesh.cell_data["tags"] = np.array([1, 1, 2], dtype=int)
    return mesh


def _tiny_uvc_mesh():
    """LV (tag=1): 5 points, 3 triangles; one endocardial (kept), one epicardial (excluded),
    one carrying the -100 sentinel (excluded). RV (tag=2): 3 points, 1 triangle, endocardial.
    LV and RV point sets are disjoint so sign/threshold selection can't collide across them.
    """
    pts = np.array(
        [
            [0, 0, 0],  # 0 LV endo
            [1, 0, 0],  # 1 LV endo
            [0, 1, 0],  # 2 LV endo
            [0, 0, 1],  # 3 LV epicardial (transmural high, excluded)
            [1, 1, 0],  # 4 LV sentinel (non-ventricular, excluded)
            [3, 0, 0],  # 5 RV endo
            [4, 0, 0],  # 6 RV endo
            [3, 1, 0],  # 7 RV endo
        ],
        dtype=float,
    )
    faces = np.hstack(
        [
            [3, 0, 1, 2],  # all-endo LV triangle -> kept
            [3, 0, 1, 3],  # touches the epicardial point -> excluded
            [3, 0, 2, 4],  # touches the sentinel point -> excluded
            [3, 5, 6, 7],  # RV triangle -> kept
        ]
    )
    mesh = pv.PolyData(pts, faces)
    mesh.cell_data["tags"] = np.array([1, 1, 1, 2], dtype=int)
    mesh.point_data["uvc_transmural"] = np.array([0.0, 0.0, 0.0, 0.9, -100.0, 0.0, 0.0, 0.0])
    mesh.point_data["uvc_intraventricular"] = np.array(
        [-1.0, -1.0, -1.0, -1.0, -100.0, 1.0, 1.0, 1.0]
    )
    return mesh


def test_extract_endocardium_by_uvc():
    surfaces = strocchi.extract_endocardium(_tiny_uvc_mesh(), lv_tag=1, rv_tag=2)
    assert surfaces.lv_endo.n_points == 3
    assert surfaces.lv_endo.n_cells == 1
    assert surfaces.rv_endo.n_points == 3
    assert surfaces.rv_endo.n_cells == 1


def test_write_forward_inputs_roundtrip(tmp_path):
    surfaces = strocchi.extract_endocardium(_tiny_uvc_mesh(), lv_tag=1, rv_tag=2)
    surfaces.fibers = tmp_path / "f0.vtk"
    paths = surfaces.write_forward_inputs(tmp_path)
    assert set(paths) == {"lv_endo", "rv_endo", "fibers", "electrodes"}
    assert paths["fibers"] == tmp_path / "f0.vtk"
    assert paths["electrodes"] is None
    # OBJ is re-readable as a non-empty triangle surface (what purkinje-uv consumes).
    lv = pv.read(str(paths["lv_endo"]))
    assert lv.n_points > 0 and lv.n_cells > 0


def test_missing_tag_raises():
    with pytest.raises(ValueError):
        strocchi.extract_endocardium(_tiny_tagged_mesh(), lv_tag=1, rv_tag=99)


def test_missing_tag_field_raises():
    mesh = _tiny_tagged_mesh()
    del mesh.cell_data["tags"]
    with pytest.raises(KeyError):
        strocchi.extract_endocardium(mesh, lv_tag=1, rv_tag=2)


def test_missing_uvc_field_raises():
    mesh = _tiny_uvc_mesh()
    del mesh.point_data["uvc_transmural"]
    with pytest.raises(KeyError):
        strocchi.extract_endocardium(mesh, lv_tag=1, rv_tag=2)


def test_assert_millimetre_units_rejects_metre_scale():
    mesh = _tiny_uvc_mesh()  # coordinates span ~4 units, well under the 50 mm floor
    with pytest.raises(ValueError):
        strocchi.assert_millimetre_units(mesh)


@pytest.mark.skipif(not REAL_CASE_PATH.exists(), reason="data/01/01.case not present")
def test_extract_endocardium_real_strocchi_mesh():
    """Real-mesh integration check (Strocchi et al. 2020 patient 01, coarse ~1.1 mm cohort).

    Skips cleanly if the file isn't present (mirrors the RUN_SLOW gating in
    test_forward_determinism.py for the other real-mesh-dependent test, but this one is
    file-existence gated since the extracted case is checkout-local, not RUN_SLOW gated,
    since it does not require the full sim stack).
    """
    mesh = strocchi.read_mesh(REAL_CASE_PATH)
    span = strocchi.assert_millimetre_units(mesh)
    assert 100.0 < span < 200.0  # sanity: human heart scale, not metres

    surfaces = strocchi.extract_endocardium(mesh)
    for label, surf in (("LV", surfaces.lv_endo), ("RV", surfaces.rv_endo)):
        assert surf.n_points > 1000, f"{label} endocardium suspiciously small"
        conn = surf.extract_surface(algorithm="dataset_surface").connectivity("all")
        n_components = len(np.unique(conn.point_data["RegionId"]))
        assert n_components == 1, f"{label} endocardium is not a single connected surface"

    lv_len = strocchi.measure_base_to_apex(mesh, intraventricular_sign=-1)
    rv_len = strocchi.measure_base_to_apex(mesh, intraventricular_sign=1)
    assert 30.0 < lv_len < 150.0
    assert 30.0 < rv_len < 150.0
