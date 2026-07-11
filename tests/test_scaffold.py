"""Scaffold smoke test: the src-layout science packages import cleanly.

This validates the package layout and the pytest pythonpath wiring without pulling
in heavy dependencies (the __init__ modules import nothing).
"""

import importlib

import pytest


@pytest.mark.parametrize("mod", ["core", "sim", "npe", "calib"])
def test_science_package_imports(mod):
    assert importlib.import_module(mod) is not None
