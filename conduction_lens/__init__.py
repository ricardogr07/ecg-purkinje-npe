"""conduction_lens: amortized, calibrated Purkinje conduction identifiability from the ECG.

An installable, CLI-driven wrapper over the science modules in `src/` (core, sim, npe, calib): it
runs the full pipeline (sweep -> NPE + conformal -> Contract-B artifact) with config, logging, a
run manifest, and resumable per-stage artifacts. The science lives under `src/` as flat top-level
packages, imported via the path bootstrap below in a source checkout.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap `src/` onto the path so `import core.*`, `import sim.*`, `import calib.*` resolve,
# matching pytest's `pythonpath = ["src"]`. Idempotent.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:  # source checkout only; a no-op once installed
    sys.path.insert(0, str(_SRC))

__version__ = "0.2.0"
