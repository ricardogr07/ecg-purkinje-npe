"""Strocchi end-to-end forward (UVC trees + cached FIM eikonal + 1/|r| pseudo-ECG),
plus the demo geometry/activation export.

Runs forward(REFERENCE_THETA, strocchi_geom) ONCE (the literal chain, on the Strocchi heart's own
trees, myocardium, and UVC-synthesized electrodes) and:
  - reports wall time, peak amplitude (arb units), the per-geometry scale to the 1.5 mV target,
    and that all 12 leads are finite,
  - sanity-checks activation-time finiteness/spread (QRS proxy) and that the ECG is NOT a scaled
    copy of crtdemo's (which would mean geom is being ignored),
  - emits ui/mock/geometry.strocchi.json + results.strocchi.json (decimated surface + per-vertex
    LAT) in the SAME schema the crtdemo ActivationMap already renders.

Method generality only: NO identifiability result is claimed on this geometry. Slow (the eikonal on
the ~338k-pt Strocchi mesh is minutes).

Run: uv run --no-sync python experiments/strocchi_forward.py
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402
from vtkmodules.numpy_interface import dataset_adapter as dsa  # noqa: E402

from adapter.strocchi import load_geometry  # noqa: E402
from core.noise import TARGET_QRS_PEAK_MV  # noqa: E402
from sim.forward import REFERENCE_THETA, forward  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ui" / "mock"
LEADS = ("I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6")
DECIM_TARGET_FACES = 12000  # browser budget (crtdemo is ~6k); ActivationMap painter-sorts per frame


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None, help="path to NN.case (default: adapter's heart 01)")
    ap.add_argument("--cache", default=None, help="per-heart forward-inputs cache dir")
    ap.add_argument(
        "--geom-id", default="strocchi_01", help="geometry_id (must contain 'strocchi')"
    )
    ap.add_argument(
        "--out-base", default="strocchi", help="ui/mock/geometry.<out-base>.json basename"
    )
    args = ap.parse_args()
    geom_id, out_base = args.geom_id, args.out_base

    t0 = time.time()
    load_kwargs = {}
    if args.case:
        load_kwargs["case_path"] = args.case
    if args.cache:
        load_kwargs["cache_dir"] = args.cache
    geom = load_geometry(**load_kwargs)
    tc = geom.tree_config
    n_lv = int(np.asarray(tc.lv_tree.pmj).size)
    n_rv = int(np.asarray(tc.rv_tree.pmj).size)
    print(
        f"[strocchi] geom + F5 trees in {time.time() - t0:.1f}s; LV {n_lv} PMJs, RV {n_rv} PMJs "
        f"(crtdemo has 87 / 166, so this network is sparser)",
        flush=True,
    )

    tf = time.time()
    ecg = np.asarray(forward(REFERENCE_THETA, geom), float)  # (12, T) raw pseudo-mV
    dt_fwd = time.time() - tf

    finite = bool(np.isfinite(ecg).all())
    peak = float(np.abs(ecg).max())
    scale = TARGET_QRS_PEAK_MV / peak if peak > 0 else float("nan")
    print(
        f"[strocchi] forward in {dt_fwd:.1f}s -> {ecg.shape}; 12 leads finite={finite}; "
        f"peak(arb)={peak:.4g}; per-geometry scale to 1.5 mV = {scale:.6g}",
        flush=True,
    )

    # --- activation-time (LAT) sanity from the coupled eikonal solve ---
    dd = dsa.WrapDataObject(geom.vtk_mesh)
    lat = np.asarray(dd.PointData["activation"], float)
    fin = np.isfinite(lat)
    lat_min, lat_max = float(lat[fin].min()), float(lat[fin].max())
    print(
        f"[strocchi] LAT {lat_min:.1f}..{lat_max:.1f} ms (spread {lat_max - lat_min:.1f} ms), "
        f"finite frac {fin.mean():.3f}",
        flush=True,
    )

    # --- not-a-scaled-copy-of-crtdemo check (guards against geom being ignored) ---
    try:
        cd = json.loads((OUT / "results.real.json").read_text()).get("input_ecg", {})
        cd_sig = np.asarray(cd.get("signal", []), float)
        if cd_sig.ndim == 2 and cd_sig.shape[0] == 12:
            tt = min(ecg.shape[1], cd_sig.shape[1])
            corrs = [abs(np.corrcoef(ecg[i, :tt], cd_sig[i, :tt])[0, 1]) for i in range(12)]
            mx = float(np.nanmax(corrs))
            verdict = (
                "OK, distinct from crtdemo" if mx < 0.999 else "SUSPICIOUS: ~identical to crtdemo"
            )
            print(f"[strocchi] max |per-lead corr| vs crtdemo = {mx:.4f} ({verdict})", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[strocchi] crtdemo compare skipped: {type(e).__name__}: {e}", flush=True)

    # --- decimated surface + per-vertex LAT (demo export, crtdemo schema) ---
    grid = pv.wrap(geom.vtk_mesh)
    lat_fill = lat.copy()
    lat_fill[~fin] = lat_max
    grid["activation"] = lat_fill
    surf = grid.extract_surface().triangulate()
    frac = max(0.0, 1.0 - DECIM_TARGET_FACES / max(surf.n_cells, 1))
    dec = surf.decimate_pro(frac).clean().triangulate() if frac > 0 else surf
    verts = np.asarray(dec.points, float)
    faces = np.asarray(dec.faces).reshape(-1, 4)[:, 1:]
    # Re-sample LAT onto decimated verts by nearest neighbour so values.length == vertices.length
    # holds regardless of whether decimation preserved point scalars (ActivationMap's hard gate).
    _, idx = cKDTree(np.asarray(surf.points, float)).query(verts)
    slat = np.asarray(surf.point_data["activation"], float)[idx]
    slat = slat - float(slat.min())
    print(
        f"[strocchi] decimated {surf.n_points}->{verts.shape[0]} verts, {faces.shape[0]} faces; "
        f"LAT 0..{slat.max():.0f} ms",
        flush=True,
    )

    geometry = {
        "geometry_id": geom_id,
        "units": "mm",
        "n_vertices": int(verts.shape[0]),
        "n_faces": int(faces.shape[0]),
        "vertices": np.round(verts, 3).tolist(),
        "faces": faces.tolist(),
    }
    (OUT / f"geometry.{out_base}.json").write_text(json.dumps(geometry))

    results = {
        "run_id": geom_id,
        "geometry_id": geom_id,
        "observation_kind": "features",
        "activation_map": {
            "mesh_ref": geom_id,
            "units": "ms",
            "values": np.round(slat, 2).tolist(),
        },
        "input_ecg": {
            "leads": list(LEADS),
            "signal": np.round(ecg * scale, 4).tolist(),  # per-geometry scaled to 1.5 mV
            "fs_hz": 500,
        },
        "meta": {
            "is_mock": False,
            "activation_is_real": True,
            "method_generality": True,
            "note": "Strocchi method-generality forward; no identifiability claim here.",
            "lv_pmj": n_lv,
            "rv_pmj": n_rv,
            "forward_seconds": round(dt_fwd, 1),
        },
    }
    (OUT / f"results.{out_base}.json").write_text(json.dumps(results))
    assert len(results["activation_map"]["values"]) == geometry["n_vertices"], "LAT/vertex mismatch"
    print(
        f"[strocchi] wrote geometry.{out_base}.json + results.{out_base}.json "
        f"(total {time.time() - t0:.1f}s)",
        flush=True,
    )


if __name__ == "__main__":
    main()
