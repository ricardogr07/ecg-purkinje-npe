"""Portable posterior persistence: save/load a trained sbi `DirectPosterior` safely.

This repo is not an installed package (`pyproject.toml` has `package = false`); `core`/
`sim`/`calib` resolve only because `src/` is bootstrapped onto `sys.path` (see
`conduction_lens/__init__.py`, pytest's `pythonpath`). A naive ``pickle.dump(posterior)``
risks embedding those module-qualified names in the pickle (e.g. anything the posterior's
graph closes over), which then fails to unpickle from a fresh clone or release tarball with
a different `sys.path`. So we never pickle the `DirectPosterior`. Instead we persist only:

- ``posterior.posterior_estimator.state_dict()`` (plain tensors, `torch.save`)
- a JSON sidecar with `theta_names`, `prior_bounds`, and the density-estimator build config
  (all plain/JSON-serializable data, no callables or project classes)

To load, we rebuild the exact same architecture via ``sbi.neural_nets.posterior_nn`` (the
same builder ``NPE`` uses internally, see ``npe/emit.py::_train`` and
``sbi/inference/trainers/npe/npe_base.py::_initialize_neural_network``), which only needs
dummy theta/x batches of the right shape for shape inference. The z-scoring layers inside
the network are `torch.nn.Module` buffers (persistent, part of `state_dict()`), so whatever
statistics the dummy batch produces get overwritten by `load_state_dict` regardless; the
rebuilt architecture is identical to the trained one once weights are loaded. Only `sbi` and
`torch` are needed to load, never `core`/`sim`/`calib`.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from sbi.inference.posteriors import DirectPosterior
from sbi.neural_nets import posterior_nn
from sbi.utils import BoxUniform

# Matches sbi.inference.NPE's default `density_estimator` arg, which npe/emit.py::_train
# never overrides.
DEFAULT_MODEL = "maf"


def _paths(path: str | Path) -> tuple[Path, Path]:
    path = Path(path)
    return path.with_suffix(".pt"), path.with_suffix(".json")


def save_posterior(
    posterior: DirectPosterior,
    theta_names: list[str],
    prior_bounds: dict[str, tuple[float, float]],
    path: str | Path,
    *,
    model: str = DEFAULT_MODEL,
    net_kwargs: dict | None = None,
) -> None:
    """Write a portable checkpoint: net weights (``<path>.pt``) + build-config JSON
    (``<path>.json``). Both are plain tensors / JSON, no pickled callables or project
    classes.

    model/net_kwargs: the ``posterior_nn(model=..., **net_kwargs)`` config used to build
    ``posterior.posterior_estimator``. Defaults match ``npe/emit.py::_train``'s
    ``NPE(prior=...)`` (density_estimator="maf", no overrides); pass the actual config if a
    caller trains with a non-default net (e.g. a smaller one for a fast test).
    """
    weights_path, meta_path = _paths(path)
    weights_path.parent.mkdir(parents=True, exist_ok=True)
    net = posterior.posterior_estimator
    torch.save(net.state_dict(), weights_path)
    meta = {
        "theta_names": list(theta_names),
        "prior_bounds": {k: [float(v) for v in prior_bounds[k]] for k in theta_names},
        "theta_dim": int(net.input_shape.numel()),
        "x_dim": int(net.condition_shape.numel()),
        "model": model,
        "net_kwargs": dict(net_kwargs or {}),
    }
    meta_path.write_text(json.dumps(meta, indent=1))


def load_posterior(path: str | Path) -> DirectPosterior:
    """Rebuild the density-estimator architecture, load trained weights, and return a
    working ``DirectPosterior`` (``.sample(...)`` / ``.log_prob(...)``). Only imports
    `sbi`/`torch`; safe to call from a fresh interpreter with no `core`/`sim`/`calib` on
    `sys.path`."""
    weights_path, meta_path = _paths(path)
    meta = json.loads(meta_path.read_text())
    names = meta["theta_names"]
    lo = torch.tensor([meta["prior_bounds"][k][0] for k in names], dtype=torch.float32)
    hi = torch.tensor([meta["prior_bounds"][k][1] for k in names], dtype=torch.float32)
    prior = BoxUniform(low=lo, high=hi)

    build_net = posterior_nn(model=meta["model"], **meta.get("net_kwargs", {}))
    dummy_theta = torch.randn(8, meta["theta_dim"])
    dummy_x = torch.randn(8, meta["x_dim"])
    net = build_net(dummy_theta, dummy_x)
    net.load_state_dict(torch.load(weights_path, map_location="cpu"))
    net.eval()

    return DirectPosterior(posterior_estimator=net, prior=prior)
