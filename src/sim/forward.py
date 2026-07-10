"""Forward model on the crtdemo geometry: theta -> 12-lead ECG.

Chain: purkinje-uv fractal trees (LV, RV) -> Purkinje activation -> myocardial-mesh
coupling loop (myocardial eikonal + lead-field pseudo-ECG) -> 12-lead ECG. The geometry
(volumetric mesh + fibers + electrodes) is loaded once; theta varies per call.

Non-theta tree preset (seeds, fascicles, N_it) mirrors the myocardial-mesh e2e acceptance
test so we reproduce a valid crtdemo activation before sweeping theta.
"""

from __future__ import annotations

from dataclasses import dataclass
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

# Representative in-prior reference at the frozen Contract A nominals (dyssynchrony regime).
# NOT claimed to reproduce True_ecg: delta_iv is a RELATIVE LV-RV delay (absolute timing is
# normalized away) and the forward has a known fidelity gap vs the real ECG. This is a
# display / SBC sanity point; growth is verified in Stage 0.
# Best in-box operating point for crtdemo, estimated from the STORED True Purkinje trees
# (True_LVtree/RVtree.vtu arrival times), NOT fitted to True_ecg and NOT the literature
# nominals: True Purkinje CV ~1.4 m/s (frozen floor 1.5 brackets it at the edge), LV-RV
# relative delay ~-75 ms, init_length ~35/55 mm. At these values the forward reaches
# corr ~0.75 with amplitude ratios ~1 (the remaining gap is cv_myo, not yet exposed).
# Used only for the fidelity table / demo, never in the SBC study (which draws truths from
# the prior). il_rv=50 is skipped: it hits a fractal-tree projection failure with these seeds.
REFERENCE_THETA: dict[str, float] = {
    "cv": 1.5,
    "delta_iv": -75.0,
    "init_length_lv": 35.0,
    "init_length_rv": 55.0,
    "branch_angle": 0.175,
    "w": 0.10,
    "cv_myo": 0.67,  # Contract A nominal (Fu 2024); myocardial CV, now an exposed forward input
}


@dataclass
class TreeConfig:
    """Purkinje-tree inputs for a geometry: endocardial surfaces, root seeds, fascicles, and the
    fractal-growth constants. Attached to the geometry object (``geom.tree_config``) so ``forward``
    grows trees on the SAME heart it runs the eikonal on, instead of silently reusing crtdemo's."""

    lv_endo: str
    rv_endo: str
    lv_seeds: tuple[int, int]
    rv_seeds: tuple[int, int]
    lv_fas_len: list
    rv_fas_len: list
    lv_fas_ang: list
    rv_fas_ang: list
    length: float = _LENGTH
    l_segment: float = _L_SEGMENT
    n_it: int = _N_IT


CRTDEMO_TREE_CONFIG = TreeConfig(
    lv_endo=str(DATA_DIR / "crtdemo_LVendo_heart_cut.obj"),
    rv_endo=str(DATA_DIR / "crtdemo_RVendo_heart_cut.obj"),
    lv_seeds=_LV_SEEDS,
    rv_seeds=_RV_SEEDS,
    lv_fas_len=_LV_FAS_LEN,
    rv_fas_len=_RV_FAS_LEN,
    lv_fas_ang=_LV_FAS_ANG,
    rv_fas_ang=_RV_FAS_ANG,
)


def load_geometry() -> MyocardialMesh:
    """Build the crtdemo MyocardialMesh once (mesh + fibers + electrodes) and attach its Purkinje
    ``TreeConfig`` so ``forward`` is geometry-parametrized (grows trees on this geometry, not a
    hardcoded one)."""
    geom = MyocardialMesh(
        myo_mesh=str(DATA_DIR / "crtdemo_mesh_oriented.vtk"),
        electrodes_position=str(DATA_DIR / "electrode_pos.pkl"),
        fibers=str(DATA_DIR / "crtdemo_f0_oriented.vtk"),
    )
    geom.tree_config = CRTDEMO_TREE_CONFIG
    return geom


def _build_tree(
    meshfile,
    seeds,
    init_len,
    fas_len,
    fas_ang,
    branch_angle,
    w,
    length=_LENGTH,
    l_segment=_L_SEGMENT,
    n_it=_N_IT,
) -> PurkinjeTree:
    params = FractalTreeParameters(
        meshfile=str(meshfile),
        init_node_id=seeds[0],
        second_node_id=seeds[1],
        init_length=float(init_len),
        length=length,
        w=float(w),
        l_segment=l_segment,
        fascicles_length=fas_len,
        fascicles_angles=fas_ang,
        branch_angle=float(branch_angle),
        N_it=n_it,
    )
    ft = FractalTree(params=params)
    ft.grow_tree()
    return PurkinjeTree(
        nodes=np.asarray(ft.nodes_xyz, dtype=float),
        connectivity=np.asarray(ft.connectivity, dtype=int),
        end_nodes=np.asarray(ft.end_nodes, dtype=int),
    )


def forward(
    theta: dict[str, float],
    geom: MyocardialMesh,
    kmax: int = 2,
    seeds_lv: tuple[int, int] | None = None,
    seeds_rv: tuple[int, int] | None = None,
) -> np.ndarray:
    """Map a theta dict to a 12-lead ECG as a (12, T) float array on crtdemo.

    Perf: kmax=2 is the converged setting for crtdemo (the 3rd coupling iteration changes
    the ECG by 0.0, verified bit-identical to kmax=3/5), and the per-iteration ECG early-stop
    is skipped since we cap at a known-converged kmax. Together ~14.2s -> ~8s per call.

    delta_iv convention: LV root at 0 ms, RV root delayed by delta_iv ms. Only the
    LV-RV relative delay is encoded; the absolute time shift is intentionally not a
    parameter (it is unidentifiable under shift-invariant ECG features).

    seeds_lv / seeds_rv are the (init_node_id, second_node_id) endocardial root nodes; varying
    them (at fixed theta) yields a genuinely different Purkinje network (topology axis). They
    default to geom.tree_config's seeds; the endocardial surfaces and fascicles come entirely from
    geom.tree_config, so a Strocchi geom grows Strocchi trees, not crtdemo's.
    """
    tc = getattr(geom, "tree_config", None)
    if tc is None:
        raise ValueError(
            "forward(theta, geom) needs geom.tree_config (the Purkinje tree inputs for THIS "
            "geometry). Build geom via load_geometry() (crtdemo) or the mesh adapter, which attach "
            "it; forward no longer silently falls back to crtdemo's endocardium."
        )
    lv = _build_tree(
        tc.lv_endo,
        seeds_lv if seeds_lv is not None else tc.lv_seeds,
        theta["init_length_lv"],
        tc.lv_fas_len,
        tc.lv_fas_ang,
        theta["branch_angle"],
        theta["w"],
        tc.length,
        tc.l_segment,
        tc.n_it,
    )
    rv = _build_tree(
        tc.rv_endo,
        seeds_rv if seeds_rv is not None else tc.rv_seeds,
        theta["init_length_rv"],
        tc.rv_fas_len,
        tc.rv_fas_ang,
        theta["branch_angle"],
        theta["w"],
        tc.length,
        tc.l_segment,
        tc.n_it,
    )
    # Contract A param 7: myocardial CV. Inert for 6D theta (key absent); rebuilds D + FIM when
    # present. delta_iv/cv above drive the Purkinje pass; cv_myo drives the myocardial eikonal.
    if "cv_myo" in theta:
        geom.set_fiber_cv(theta["cv_myo"])
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
        compute_ecg_each_iter=False,
    )
    # run_ecg_core returns a structured (record) array of 12 named leads.
    return np.vstack([np.asarray(ecg[name], dtype=float) for name in ecg.dtype.names])


# Endocardial mesh paths, exposed so experiments can sample network seeds on them.
LV_ENDO = DATA_DIR / "crtdemo_LVendo_heart_cut.obj"
RV_ENDO = DATA_DIR / "crtdemo_RVendo_heart_cut.obj"


def _endo_points(meshfile) -> np.ndarray:
    import pyvista as pv

    return np.asarray(pv.read(str(meshfile)).points, dtype=float)


def sample_valid_seeds(meshfile, n: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    """Sample n (init_node_id, second_node_id) endocardial root pairs for tree growth.

    second is init's nearest distinct vertex, so the initial branch is a short valid step
    along the surface. Varying these at fixed theta yields distinct Purkinje networks.
    """
    from scipy.spatial import cKDTree

    pts = _endo_points(meshfile)
    tree = cKDTree(pts)
    idx = rng.integers(0, pts.shape[0], size=n)
    seeds: list[tuple[int, int]] = []
    for i in idx:
        _, nn = tree.query(pts[int(i)], k=2)
        seeds.append((int(i), int(nn[1])))
    return seeds
