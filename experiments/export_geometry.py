"""Export the REAL crtdemo activation scene for the demo: surface + LAT + the Purkinje network.

Runs the forward once at the honest operating point (REFERENCE_THETA, physiological cv_myo),
then writes a geometry.json the UI's ActivationMap can render for real:
  - vertices/faces: the crtdemo myocardial surface,
  - activation_map.values: per-vertex local activation time (ms) from the coupled eikonal solve,
  - purkinje: the actual LV+RV fractal Purkinje trees (nodes + edges) that seed the activation.

This is the network that generates the 12-lead ECG shown in the demo. Output goes to
ui/mock/geometry.real.json (+ activation/ecg merged into ui/mock/results.real.json), which the
UI can be pointed at to render REAL data instead of the illustrative mock.

Run:  uv run --no-sync python experiments/export_geometry.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402
from myocardial_mesh.orchestrator import run_ecg_core  # noqa: E402
from vtkmodules.numpy_interface import dataset_adapter as dsa  # noqa: E402

import sim.forward as fwd  # noqa: E402
from core.noise import to_physiological_mv  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ui" / "mock"
LEADS = ("I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6")


def _tree(meshfile, seeds, init_len, fas_len, fas_ang, theta):
    return fwd._build_tree(
        meshfile, seeds, init_len, fas_len, fas_ang, theta["branch_angle"], theta["w"]
    )


def main() -> None:
    theta = dict(fwd.REFERENCE_THETA)
    geom = fwd.load_geometry()
    geom.set_fiber_cv(theta["cv_myo"])
    lv = _tree(
        fwd.DATA_DIR / "crtdemo_LVendo_heart_cut.obj",
        fwd._LV_SEEDS,
        theta["init_length_lv"],
        fwd._LV_FAS_LEN,
        fwd._LV_FAS_ANG,
        theta,
    )
    rv = _tree(
        fwd.DATA_DIR / "crtdemo_RVendo_heart_cut.obj",
        fwd._RV_SEEDS,
        theta["init_length_rv"],
        fwd._RV_FAS_LEN,
        fwd._RV_FAS_ANG,
        theta,
    )

    ecg, _ = run_ecg_core(
        myocardium=geom,
        lv_tree=lv,
        rv_tree=rv,
        lv_root_idx=0,
        rv_root_idx=0,
        lv_root_time_ms=0.0,
        rv_root_time_ms=float(theta["delta_iv"]),
        purkinje_cv_m_per_s=float(theta["cv"]),
        kmax=2,
        verbose=False,
        return_diagnostics=False,
        compute_ecg_each_iter=False,
    )
    ecg_mv = to_physiological_mv(np.vstack([np.asarray(ecg[n], float) for n in ecg.dtype.names]))

    # --- myocardial surface + per-vertex LAT ---
    dd = dsa.WrapDataObject(geom.vtk_mesh)
    lat_full = np.asarray(dd.PointData["activation"], float)
    lat_full[~np.isfinite(lat_full)] = np.nanmax(lat_full[np.isfinite(lat_full)])
    grid = pv.wrap(geom.vtk_mesh)
    grid["activation"] = lat_full
    surf = grid.extract_surface().triangulate()
    verts = np.asarray(surf.points, float)
    faces = np.asarray(surf.faces).reshape(-1, 4)[:, 1:]  # triangles
    lat = np.asarray(surf.point_data["activation"], float)
    lat = lat - float(lat.min())  # zero the activation origin (relative LAT, ms)
    print(
        f"[export] surface: {verts.shape[0]} verts, {faces.shape[0]} faces; "
        f"LAT range 0..{lat.max():.0f} ms",
        flush=True,
    )

    def tree_json(t):
        return {
            "nodes": np.round(t.xyz, 3).tolist(),
            "edges": np.asarray(t.connectivity, int).tolist(),
            "n_pmj": int(np.asarray(t.pmj).size),
        }

    geometry = {
        "geometry_id": "crtdemo",
        "units": "mm",
        "n_vertices": int(verts.shape[0]),
        "n_faces": int(faces.shape[0]),
        "vertices": np.round(verts, 3).tolist(),
        "faces": faces.tolist(),
        "purkinje": {"lv": tree_json(lv), "rv": tree_json(rv)},
    }
    (OUT / "geometry.real.json").write_text(json.dumps(geometry))
    print(
        f"[export] wrote {OUT / 'geometry.real.json'} "
        f"(LV {lv.xyz.shape[0]} nodes / RV {rv.xyz.shape[0]} nodes)",
        flush=True,
    )

    # Merge the real activation + ECG into a copy of the honest Contract-B so the activation view
    # renders REAL while the (labeled) mock still drives the other panels if used standalone.
    results_src = OUT / "results.json"
    results = json.loads(results_src.read_text())
    results["activation_map"] = {
        "mesh_ref": "crtdemo",
        "units": "ms",
        "values": np.round(lat, 2).tolist(),
    }
    results["input_ecg"] = {
        "leads": list(LEADS),
        "signal": np.round(ecg_mv, 4).tolist(),
        "fs_hz": 500,
    }
    results.setdefault("meta", {})["activation_is_real"] = True
    (OUT / "results.real.json").write_text(json.dumps(results))
    print(
        f"[export] wrote {OUT / 'results.real.json'} with real activation_map + input_ecg",
        flush=True,
    )


if __name__ == "__main__":
    main()
