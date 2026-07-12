"""Export the grown LV/RV Purkinje trees for the Strocchi hearts and patch them into the
committed ui/mock/geometry.strocchi*.json (a method-generality overlay; NO identifiability claim).

No eikonal forward is run: the trees come from the fast adapter.strocchi.load_geometry, the same
call behind the shipped Strocchi activation maps. The serialized shape mirrors
experiments/export_geometry.py so ActivationMap renders it exactly as it does crtdemo.

Integrity gate: the exported PMJ count (int(tree.pmj.size), how meta.lv_pmj/rv_pmj was computed)
MUST equal the stored meta. On any mismatch the script exits non-zero and writes nothing, so a tree
that is not the one behind the shown map can never ship.

Run: uv run --no-sync python experiments/export_strocchi_purkinje.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from adapter.strocchi import load_geometry  # noqa: E402

MOCK = ROOT / "ui" / "mock"

HEARTS = [
    {"load_kwargs": {}, "geom": "geometry.strocchi.json", "results": "results.strocchi.json"},
    {
        "load_kwargs": {
            "case_path": str(ROOT / "data" / "02" / "02.case"),
            "cache_dir": str(ROOT / "data" / "02" / "_forward_inputs"),
        },
        "geom": "geometry.strocchi_02.json",
        "results": "results.strocchi_02.json",
    },
]


def tree_json(t):
    return {
        "nodes": np.round(t.xyz, 3).tolist(),
        "edges": np.asarray(t.connectivity, int).tolist(),
        "n_pmj": int(np.asarray(t.pmj).size),
    }


def main() -> None:
    # Pass 1: grow + gate every heart before writing any, so a late mismatch cannot leave a
    # partially-patched set of geometry files.
    patches = []
    for h in HEARTS:
        geom = load_geometry(**h["load_kwargs"])
        lv, rv = geom.tree_config.lv_tree, geom.tree_config.rv_tree
        n_lv = int(np.asarray(lv.pmj).size)
        n_rv = int(np.asarray(rv.pmj).size)
        meta = json.loads((MOCK / h["results"]).read_text())["meta"]
        assert n_lv == meta["lv_pmj"], f"{h['geom']}: LV PMJ {n_lv} != meta {meta['lv_pmj']}"
        assert n_rv == meta["rv_pmj"], f"{h['geom']}: RV PMJ {n_rv} != meta {meta['rv_pmj']}"
        patches.append((h["geom"], tree_json(lv), tree_json(rv)))
        print(
            f"[strocchi-purkinje] {h['geom']}: LV {n_lv} PMJs, RV {n_rv} PMJs (gate OK)", flush=True
        )

    # Pass 2: patch the geometry artifacts (same mm frame as the surface vertices, no transform).
    for geom_name, lv_json, rv_json in patches:
        gpath = MOCK / geom_name
        geometry = json.loads(gpath.read_text())
        geometry["purkinje"] = {"lv": lv_json, "rv": rv_json}
        gpath.write_text(json.dumps(geometry))
        print(f"[strocchi-purkinje] wrote purkinje into {geom_name}", flush=True)


if __name__ == "__main__":
    main()
