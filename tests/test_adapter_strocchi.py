"""Strocchi adapter: extract endo surfaces by tag from a tiny in-memory mesh, round-trip OBJ.

No Strocchi file is present, so this exercises the tag-select + surface-extract + write path
on a synthetic labelled surface. Skips cleanly if pyvista/meshio are unavailable.
"""

import numpy as np
import pytest

pytest.importorskip("pyvista")
pytest.importorskip("meshio")

import pyvista as pv  # noqa: E402

from adapter import strocchi  # noqa: E402


def _tiny_tagged_mesh():
    # 3 triangles: two tagged LV(=1), one tagged RV(=2).
    pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]], dtype=float)
    faces = np.hstack([[3, 0, 1, 2], [3, 1, 3, 2], [3, 1, 4, 3]])
    mesh = pv.PolyData(pts, faces)
    mesh.cell_data["tags"] = np.array([1, 1, 2], dtype=int)
    return mesh


def test_extract_endocardium_by_tag():
    surfaces = strocchi.extract_endocardium(_tiny_tagged_mesh(), lv_tag=1, rv_tag=2)
    assert surfaces.lv_endo.n_points > 0
    assert surfaces.rv_endo.n_points > 0
    # LV had 2 tagged triangles, RV had 1.
    assert surfaces.lv_endo.n_cells == 2
    assert surfaces.rv_endo.n_cells == 1


def test_write_forward_inputs_roundtrip(tmp_path):
    surfaces = strocchi.extract_endocardium(_tiny_tagged_mesh(), lv_tag=1, rv_tag=2)
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
