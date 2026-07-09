"""Thin env-driven CLI for the Contract-B emitter (logic lives in src/npe/emit.py).

Kept for the documented manual workflow:
  CKPT_PATH=outputs/day3_7d_ckpt.npz uv run python experiments/emit_contract_b.py
Fast structural check (no forward, tiny train):
  DRY=1 EMIT_ECG=0 CKPT_PATH=outputs/day2_sweep_ckpt.npz OUT_JSON=outputs/_emit_validate.json \
      uv run python experiments/emit_contract_b.py

The pipeline (conduction_lens) imports npe.emit.emit_contract_b directly; it does not call this.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from npe.emit import emit_contract_b  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ckpt = Path(os.getenv("CKPT_PATH", str(OUT / "day2_sweep_ckpt.npz")))
    out_json = Path(
        os.getenv("OUT_JSON", str(OUT / (ckpt.stem.replace("_ckpt", "") + "_results.json")))
    )
    dry = bool(int(os.getenv("DRY", "0")))
    emit_contract_b(
        ckpt,
        out_json,
        emit_ecg=bool(int(os.getenv("EMIT_ECG", "1"))),
        ppc_n=int(os.getenv("PPC_N", "6")),
        n_train=60 if dry else int(os.getenv("N_TRAIN", "1000")),
        n_calib=20 if dry else int(os.getenv("N_CALIB", "250")),
        n_post=100 if dry else int(os.getenv("N_POST", "300")),
    )


if __name__ == "__main__":
    main()
