"""Portable posterior persistence (npe.persist): the reproducibility story.

Trains a tiny NPE, saves it, then loads it back **in a fresh subprocess that never
imports core/sim/calib** (only sbi/torch + npe.persist), proving the checkpoint is
loadable from a clean interpreter with a different sys.path (e.g. a release tarball),
not just within this repo's pytest bootstrap. See src/npe/persist.py module docstring for
why we never pickle.dump the DirectPosterior itself.

Slow (trains a real flow); gated behind RUN_SLOW like the other sim/sbi-heavy tests.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("sbi")
pytest.importorskip("torch")

pytestmark = pytest.mark.slow

SRC = Path(__file__).resolve().parents[1] / "src"

THETA_NAMES = ["a", "b", "c"]
PRIOR_BOUNDS = {"a": (0.0, 1.0), "b": (0.0, 1.0), "c": (0.0, 1.0)}
NET_KWARGS = {"hidden_features": 8, "num_transforms": 2}  # small net, fast test


def _train_tiny_posterior():
    import torch
    from sbi.inference import NPE
    from sbi.neural_nets import posterior_nn
    from sbi.utils import BoxUniform

    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    n, d, f = 400, 3, 5
    theta = rng.uniform(size=(n, d))
    mix = rng.normal(size=(d, f))
    x = theta @ mix + 0.02 * rng.normal(size=(n, f))

    lo = torch.zeros(d)
    hi = torch.ones(d)
    inf = NPE(
        prior=BoxUniform(low=lo, high=hi),
        density_estimator=posterior_nn(model="maf", **NET_KWARGS),
    )
    inf.append_simulations(
        torch.tensor(theta, dtype=torch.float32), torch.tensor(x, dtype=torch.float32)
    )
    inf.train(stop_after_epochs=8, show_train_summary=False)
    posterior = inf.build_posterior()
    x_obs = x[0]
    return posterior, x_obs


def test_save_and_load_roundtrip_same_process(tmp_path):
    from npe.persist import load_posterior, save_posterior

    posterior, x_obs = _train_tiny_posterior()
    ckpt = tmp_path / "post"
    save_posterior(posterior, THETA_NAMES, PRIOR_BOUNDS, ckpt, net_kwargs=NET_KWARGS)
    assert ckpt.with_suffix(".pt").is_file()
    assert ckpt.with_suffix(".json").is_file()

    import torch

    reloaded = load_posterior(ckpt)
    samples = reloaded.sample(
        (16,), x=torch.tensor(x_obs, dtype=torch.float32), show_progress_bars=False
    )
    assert samples.shape == (16, 3)
    assert np.isfinite(np.asarray(samples)).all()


def test_load_posterior_in_clean_subprocess(tmp_path):
    """The literal test the task demands: load + sample in a fresh interpreter that
    never had core/sim/calib importable, proving the checkpoint is portable."""
    posterior, x_obs = _train_tiny_posterior()
    ckpt = tmp_path / "post"
    from npe.persist import save_posterior

    save_posterior(posterior, THETA_NAMES, PRIOR_BOUNDS, ckpt, net_kwargs=NET_KWARGS)

    script = f"""
import sys
sys.path.insert(0, {str(SRC)!r})
assert "core" not in sys.modules and "sim" not in sys.modules and "calib" not in sys.modules

import numpy as np
import torch
from npe.persist import load_posterior

assert "core" not in sys.modules, "load must not pull in core/"
assert "sim" not in sys.modules, "load must not pull in sim/"
assert "calib" not in sys.modules, "load must not pull in calib/"

post = load_posterior({str(ckpt)!r})
x_obs = torch.tensor(np.load({str(tmp_path / "x_obs.npy")!r}), dtype=torch.float32)
samples = post.sample((16,), x=x_obs, show_progress_bars=False)
samples = np.asarray(samples)
assert samples.shape == (16, 3), samples.shape
assert np.isfinite(samples).all(), "non-finite posterior samples"
assert "core" not in sys.modules and "sim" not in sys.modules and "calib" not in sys.modules
print("OK")
"""
    np.save(tmp_path / "x_obs.npy", x_obs)

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert "OK" in result.stdout
