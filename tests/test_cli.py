"""conduction-lens CLI + report (conduction_lens/cli.py, pipeline.report).

--help must exit clean, and `report` must summarize a finished run's Contract-B JSON.
The run pipeline itself needs the sim stack + a sweep, so it is not exercised here.
"""

import json
import logging

import pytest
from conduction_lens import pipeline
from conduction_lens.cli import main


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_report_summarizes_a_finished_run(tmp_path, caplog):
    (tmp_path / "results.json").write_text(
        json.dumps(
            {
                "posterior": {"contraction": {"cv": 0.21, "w": 0.93}},
                "calibration": {"sbc_ks_pvalue": 0.24, "tarp_atc": 0.9},
                "synthetic_truth": True,
            }
        )
    )
    with caplog.at_level(logging.INFO, logger="conduction_lens"):
        pipeline.report(str(tmp_path))
    text = caplog.text
    assert "contraction" in text
    assert "cv" in text and "w" in text  # both parameters reported, sorted by contraction
