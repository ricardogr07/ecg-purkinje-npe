"""Determinism on the Strocchi geometry (C.8): same theta twice -> bit-identical ECG.

Sibling to test_forward_determinism.py (kept separate, not merged into it, to avoid touching
a Science-owned file and to gate independently: this needs data/01/01.case, which is
checkout-local and gitignored, not just the sim stack). load_geometry attaches the UVC-grown
Strocchi Purkinje trees to geom.tree_config, so this exercises determinism of the full,
geometrically-native Strocchi path: its own Purkinje network, myocardium, FIM eikonal, and
1/|r| pseudo-ECG.

Slow: builds the ~1.7M-tet Strocchi MyocardialMesh (FIM solver init alone is minutes on this
mesh, far slower than crtdemo's ~18k-cell mesh) and runs the forward model twice, so it is
gated behind RUN_SLOW same as the crtdemo determinism test.
"""

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("myocardial_mesh")
pytest.importorskip("purkinje_uv")

REAL_CASE_PATH = Path(__file__).resolve().parents[1] / "data" / "01" / "01.case"

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not REAL_CASE_PATH.exists(), reason="data/01/01.case not present"),
]


def test_forward_bit_identical_for_same_theta_strocchi():
    from adapter.strocchi import load_geometry
    from sim.forward import REFERENCE_THETA, forward

    geom = load_geometry()
    a = forward(REFERENCE_THETA, geom)
    b = forward(REFERENCE_THETA, geom)

    assert a.shape[0] == 12, "expected a 12-lead ECG (12, T)"
    assert np.isfinite(a).all(), "ECG has non-finite values"
    assert np.array_equal(a, b), (
        f"forward is not bit-identical for identical theta: max|diff|={np.max(np.abs(a - b)):.3e}"
    )
