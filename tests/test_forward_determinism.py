"""Founding invariant: the forward model is deterministic given theta.

Same theta twice -> bit-identical 12-lead ECG. This is what makes the mandatory
observation-noise model (Contract D) meaningful: on a deterministic simulator, the
added noise is the only source of stochasticity, so calibration is a real test. If
determinism regresses, the whole calibration story is compromised. See docs/architecture.md
section 2 and brief 5.6; mirrors the determinism gate.

Slow: loads the crtdemo geometry and grows the LV/RV trees + eikonal twice (seconds
each), so it is gated behind RUN_SLOW (see conftest). Skips if the sim stack is absent.
"""

import numpy as np
import pytest

pytest.importorskip("myocardial_mesh")
pytest.importorskip("purkinje_uv")

pytestmark = pytest.mark.slow


def test_forward_bit_identical_for_same_theta():
    from sim.forward import REFERENCE_THETA, forward, load_geometry

    geom = load_geometry()
    a = forward(REFERENCE_THETA, geom)
    b = forward(REFERENCE_THETA, geom)

    assert a.shape[0] == 12, "expected a 12-lead ECG (12, T)"
    assert np.isfinite(a).all(), "ECG has non-finite values"
    assert np.array_equal(a, b), (
        f"forward is not bit-identical for identical theta: max|diff|={np.max(np.abs(a - b)):.3e}"
    )
