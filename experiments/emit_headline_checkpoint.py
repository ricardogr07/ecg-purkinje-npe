"""Regenerate the released headline NPE checkpoint and verify it reproduces the shipped posteriors.

The shipped headline artifact (ui/mock/results.real.json, aka outputs/hl_tarp_results.json) was
produced by an ad-hoc emit run whose exact config was never recorded in a committed script. This
closes that gap. The config was recovered by matching the cv contraction, TARP-post, and
init_length_rv contraction to the shipped artifact bit-for-bit:

    checkpoint = outputs/day3_7d_snr_ckpt.npz   (features sweep: theta + x_noised)
                 NOT day4_wave_ckpt.npz, whose row order differs and gives different numbers
    n_train=1000, n_calib=250, n_post=300, seed 0, emit_ecg=False

Writes outputs/release_posterior.{pt,json} (the portable checkpoint shipped in the release) and
asserts it reproduces the shipped headline. Run serialized (one torch job at a time):

    .venv/Scripts/python.exe experiments/emit_headline_checkpoint.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from npe.emit import emit_contract_b  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
HEADLINE_CKPT = REPO / "outputs" / "day3_7d_snr_ckpt.npz"


def main() -> None:
    art = emit_contract_b(
        HEADLINE_CKPT,
        REPO / "outputs" / "release_emit.json",
        emit_ecg=False,
        n_train=1000,
        n_calib=250,
        n_post=300,
        save_checkpoint_path=str(REPO / "outputs" / "release_posterior"),
    )
    shipped = json.loads((REPO / "ui" / "mock" / "results.real.json").read_text())
    gc, sc = art["posterior"]["contraction"], shipped["posterior"]["contraction"]
    maxd = max(abs(gc[k] - sc[k]) for k in gc)
    tarp_g = art["calibration"]["tarp_atc_post"]
    tarp_s = shipped["calibration"]["tarp_atc_post"]
    print(f"max contraction abs diff = {maxd:.2e}; tarp_post gen={tarp_g:.6f} shipped={tarp_s:.6f}")
    assert maxd < 1e-4, f"checkpoint does NOT reproduce the shipped posteriors (max diff {maxd})"
    assert abs(tarp_g - tarp_s) < 1e-4, "TARP-post does not match the shipped artifact"
    print("OK: release_posterior.{pt,json} reproduces the shipped headline bit-for-bit")


if __name__ == "__main__":
    main()
