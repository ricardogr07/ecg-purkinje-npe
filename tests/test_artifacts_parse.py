"""Shipped-artifact integrity guard.

Two regressions this repo has hit before and must not ship:
  1. a NaN/Inf leaking into a JSON artifact. Python's json.dump writes bare ``NaN``, which the
     browser's JSON.parse rejects, so the demo silently falls back to the mock. We parse with
     ``parse_constant`` so this fails here exactly as it would in the browser.
  2. the spectrum's noise floor recorded as the feature channel (0.05 mV / 5 ms) instead of the
     APPLIED waveform floor (0.025 mV), which the provenance header then displays.

Run in the native/CI checkout where the artifacts are whole (a truncated sandbox mount is not a
real malformation). One test file, guards both regressions.
"""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]

# Shipped, git-tracked demo artifacts: must be present and browser-parseable.
_SHIPPED = [
    "ui/mock/results.real.json",
    "ui/mock/geometry.real.json",
    "ui/mock/results.strocchi.json",
    "ui/mock/results.strocchi_02.json",
    "ui/mock/results.json",
]
# outputs/ is gitignored (some artifacts are force-added); guard if present, skip if not.
_OPTIONAL = ["outputs/f3_contraction_vs_n.json"]


def _reject_constant(token):  # json calls this only for NaN, Infinity, -Infinity
    raise ValueError(f"invalid JSON constant {token!r}: the browser's JSON.parse would reject it")


@pytest.mark.parametrize("rel", _SHIPPED + _OPTIONAL)
def test_artifact_parses_like_a_browser(rel):
    p = _REPO / rel
    if rel in _OPTIONAL and not p.is_file():
        pytest.skip(f"{rel} not present in this checkout")
    assert p.is_file(), f"shipped artifact missing: {rel}"
    json.loads(p.read_text(), parse_constant=_reject_constant)  # raises on NaN/Inf


def test_real_artifact_records_the_applied_waveform_floor():
    nm = json.loads((_REPO / "ui/mock/results.real.json").read_text()).get("noise_model", {})
    assert nm.get("kind") == "waveform"
    assert nm.get("sigma") == 0.025, "spectrum floor must be the applied waveform sigma"
    # The feature-channel floor belongs to the CRLB comparison, never the shipped spectrum artifact.
    assert "amp_sigma_mv" not in nm and "timing_sigma_ms" not in nm
