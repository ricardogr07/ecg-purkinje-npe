"""Pytest config: gate sim-heavy tests behind RUN_SLOW so the default suite stays fast.

Tests marked ``@pytest.mark.slow`` load the crtdemo geometry and run the forward model
(seconds each). They run only when RUN_SLOW is set in the environment, e.g.
``RUN_SLOW=1 uv run --no-sync pytest``. Default CI runs the fast subset only.
"""

import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: sim-heavy test (geometry + forward); runs only when RUN_SLOW is set"
    )


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_SLOW"):
        return
    skip_slow = pytest.mark.skip(reason="slow sim test; set RUN_SLOW=1 to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
