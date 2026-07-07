"""Forward model on the crtdemo geometry: theta -> 12-lead ECG.

Chain: purkinje-uv fractal trees (LV, RV) -> Purkinje activation -> myocardial-mesh
coupling loop (myocardial eikonal + lead-field pseudo-ECG) -> 12-lead ECG. The geometry
(volumetric mesh + fibers + electrodes) is loaded once; theta varies per call.

Non-theta tree preset (seeds, fascicles, N_it) mirrors the myocardial-mesh e2e acceptance
test so we reproduce a valid crtdemo activation before sweeping theta.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from myocardial_mesh import MyocardialMesh
from myocardial_mesh.orchestrator import run_ecg_core
from purkinje_uv import FractalTree, FractalTreeParameters, PurkinjeTree

DATA_DIR = Path(__file__).resolve().parents[2] / "packages" / "myocardial-mesh" / "data" / "crtdemo"

# crtdemo fixed (non-theta) preset, from the library e2e acceptance test.
_LV_SEEDS = (388, 412)
_RV_SEEDS = (198, 186)
_LV_FAS_LEN = [0.5 * 4.711579058738858, 0.5 * 9.129484609771032]
_RV_FAS_LEN = [0.5 * 21.703867933650002, 0.5 * 5.79561866201451]
_LV_FAS_ANG = [0.1 * 0.14448952070696136, 0.1 * 0.23561944901923448]
_RV_FAS_ANG = [0.1 * 0.23561944901923448, 0.1 * 0.23561944901923448]
_LENGTH = 8.0
_L_SEGMENT = 1.0
_N_IT = 20

# A theta point known to grow cleanly on crtdemo (the paper preset). delta_iv=0.
REFERENCE_THETA: dict[str, float] = {
    "cv": 2.0,
    "delta_iv": 0.0,
    "init_length_lv": 35.931537038275316,
    "init_length_rv": 79.86354832236707,
    "branch_angle": 0.15,
    "w": 0.1,
}


def load_geometry() -> MyocardialMesh:
    """Build the crtdemo MyocardialMesh once (mesh + fibers + electrodes)."""
    return MyocardialMesh(
        myo_mesh=str(DATA_DIR / "crtdemo_mesh_oriented.vtk"),
        electrodes_position=str(DATA_DIR / "electrode_pos.pkl"),
        fibers=str(DATA_DIR / "crtdemo_f0_oriented.vtk"),
    )


def _build_tree(meshfile, seeds, init_len, fas_len, fas_ang, branch_angle, w) -> PurkinjeTree:
    params = FractalTreeParameters(
        meshfile=str(meshfile),
        init_node_id=seeds[0],
        second_node_id=seeds[1],
        init_length=float(init_len),
        length=_LENGTH,
        w=float(w),
        l_segment=_L_SEGMENT,
        fascicles_length=fas_len,
        fascicles_angles=fas_ang,
        branch_angle=float(branch_angle),
        N_it=_N_IT,
    )
    ft = FractalTree(params=params)
    ft.grow_tree()
    return PurkinjeTree(
        nodes=np.asarray(ft.nodes_xyz, dtype=float),
        connectivity=np.asarray(ft.connectivity, dtype=int),
        end_nodes=np.asarray(ft.end_nodes, dtype=int),
    )


def forward(theta: dict[str, float], geom: MyocardialMesh, kmax: int = 3) -> np.ndarray:
    """Map a theta dict to a 12-lead ECG as a (12, T) float array on crtdemo.

    delta_iv convention: LV root at 0 ms, RV root delayed by delta_iv ms. Only the
    LV-RV relative delay is encoded; the absolute time shift is intentionally not a
    parameter (it is unidentifiable under shift-invariant ECG features).
    """
    lv = _build_tree(
        DATA_DIR / "crtdemo_LVendo_heart_cut.obj",
        _LV_SEEDS,
        theta["init_length_lv"],
        _LV_FAS_LEN,
        _LV_FAS_ANG,
        theta["branch_angle"],
        theta["w"],
    )
    rv = _build_tree(
        DATA_DIR / "crtdemo_RVendo_heart_cut.obj",
        _RV_SEEDS,
        theta["init_length_rv"],
        _RV_FAS_LEN,
        _RV_FAS_ANG,
        theta["branch_angle"],
        theta["w"],
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
        kmax=kmax,
        verbose=False,
        return_diagnostics=False,
    )
    # run_ecg_core returns a structured (record) array of 12 named leads.
    return np.vstack([np.asarray(ecg[name], dtype=float) for name in ecg.dtype.names])
