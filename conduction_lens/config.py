"""Typed run configuration for the conduction_lens pipeline (dataclass, CLI/YAML-loadable)."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass


@dataclass
class RunConfig:
    """One pipeline run. Serialized into the run manifest for reproducibility."""

    geometry: str = "crtdemo"  # crtdemo (wired) | strocchi | medalcare (Phase 2/3 stubs)
    dim: int = 7  # frozen Contract A is 7D; only 7 is supported
    budget: int = 5000  # total usable sims (train + calib)
    obs: str = "features"  # features (wired) | waveform (stretch)
    out: str = "runs/crtdemo_7d"
    seed: int = 1234
    noise_sigma_mv: float = 0.025  # Contract D waveform sigma
    ppc_n: int = 8  # posterior-predictive band forwards in the Contract-B emit
    workers: int = 0  # 0 = auto (min(cpu, 8))
    dry_run: bool = False

    def resolved_workers(self) -> int:
        return self.workers if self.workers > 0 else min(os.cpu_count() or 2, 8)

    def as_dict(self) -> dict:
        return asdict(self)
