"""Structural check for the promoted Contract-B emitter (npe.emit.emit_contract_b).

Runs the real NPE + conformal path on a tiny synthetic 7D checkpoint with emit_ecg=False
(no geometry / forward), then asserts the artifact has the frozen Contract-B shape. Slow
because it trains an sbi flow; gated behind RUN_SLOW.
"""

import numpy as np
import pytest

pytest.importorskip("sbi")
pytest.importorskip("torch")

pytestmark = pytest.mark.slow


def test_emit_produces_contract_b_shape(tmp_path):
    from core.theta import PRIOR_BOUNDS, THETA_NAMES
    from npe.emit import emit_contract_b

    rng = np.random.default_rng(0)
    k = 90
    lo = np.array([PRIOR_BOUNDS[name][0] for name in THETA_NAMES])
    hi = np.array([PRIOR_BOUNDS[name][1] for name in THETA_NAMES])
    theta = lo + rng.uniform(size=(k, 7)) * (hi - lo)
    x_noised = rng.normal(size=(k, 15))
    ckpt = tmp_path / "synth_ckpt.npz"
    np.savez(ckpt, theta=theta, x_noised=x_noised)

    out = tmp_path / "results.json"
    art = emit_contract_b(
        str(ckpt), str(out), emit_ecg=False, ppc_n=0, n_train=60, n_calib=20, n_post=30
    )

    assert out.is_file()
    assert len(art["theta_names"]) == 7
    for key in ("run_id", "posterior", "calibration", "input_ecg", "reference_theta"):
        assert key in art
    for key in ("samples", "mean", "std", "contraction", "coverage"):
        assert key in art["posterior"]
    assert art["meta"]["ecg_stub"] is True
