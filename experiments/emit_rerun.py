"""Emit re-run: produce the real Contract-B artifact carrying the POST-conformal TARP
(calibration.tarp_atc_post, the last calibration number the manuscript needs), at the headline
config (n_train=1000). Uses the F2 re-sweep checkpoint (x_noised bit-identical to the headline
day3_7d_snr run) and the F4-fixed forward. Writes outputs/day4_7d_results.json.

Run (serialized, one torch job at a time): .venv/Scripts/python.exe experiments/emit_rerun.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from npe.emit import emit_contract_b  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    art = emit_contract_b(
        REPO / "outputs" / "day4_wave_ckpt.npz",
        REPO / "outputs" / "day4_7d_results.json",
        emit_ecg=True,
        n_train=1000,
        n_calib=250,
        n_post=300,
    )
    cal = art["calibration"]
    print(
        f"[emit_rerun] tarp_atc(pre)={cal['tarp_atc']} tarp_atc_post={cal['tarp_atc_post']}",
        flush=True,
    )
    print(f"[emit_rerun] sbc_ks_pvalue={cal['sbc_ks_pvalue']}", flush=True)
    print(f"[emit_rerun] contraction(post)={art['posterior']['contraction']}", flush=True)
    print("[emit_rerun] DONE", flush=True)


if __name__ == "__main__":
    main()
