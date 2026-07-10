"""Visualize the Strocchi Purkinje trees overlaid on their endocardial surfaces.

Reads the F5 artifacts in outputs/ and renders both ventricles: the derived
endocardial surface (translucent) with its grown Purkinje network on top, and the
PMJ endpoints marked. LV in blue, RV in red. Opens an interactive window you can
orbit and zoom; press a key or close the window to exit. Also writes a PNG.

This is a look at the forward-model geometry, not a scientific result. No
identifiability claim is made on this heart.

Usage (from the repo root, with the project venv active):
    python scripts/view_strocchi_purkinje.py
    python scripts/view_strocchi_purkinje.py --outputs outputs --png outputs/strocchi_purkinje.png
    python scripts/view_strocchi_purkinje.py --no-window     # PNG only, no display
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pyvista as pv


def _load(path: Path):
    if not path.exists():
        print(f"  missing: {path}", file=sys.stderr)
        return None
    return pv.read(str(path))


def _pmjs(tree):
    """PMJs are the tree leaves: points that terminate exactly one line cell."""
    from collections import Counter

    counts: Counter[int] = Counter()
    for cid in range(tree.n_cells):
        for pid in tree.get_cell(cid).point_ids:
            counts[pid] += 1
    leaves = [pid for pid, c in counts.items() if c == 1]
    return tree.points[leaves] if leaves else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", default="outputs", help="directory with the f5_* files")
    ap.add_argument("--png", default="outputs/strocchi_purkinje.png")
    ap.add_argument("--no-window", action="store_true", help="save the PNG, do not open a window")
    args = ap.parse_args()

    d = Path(args.outputs)
    sides = [
        ("lv", d / "f5_lv_endo_cut.obj", d / "f5_lv_tree.vtu", "#4f8cff", "#1e3a8a"),
        ("rv", d / "f5_rv_endo_cut.obj", d / "f5_rv_tree.vtu", "#ff6b6b", "#7f1d1d"),
    ]

    pl = pv.Plotter(off_screen=args.no_window, window_size=(1400, 1000))
    pl.set_background("white")

    for name, endo_path, tree_path, tree_color, pmj_color in sides:
        endo = _load(endo_path)
        tree = _load(tree_path)
        if endo is not None:
            pl.add_mesh(endo, color="lightgray", opacity=0.25, smooth_shading=True)
        if tree is not None:
            pl.add_mesh(tree, color=tree_color, line_width=2, render_lines_as_tubes=True)
            pmj = _pmjs(tree)
            if pmj is not None:
                pl.add_points(pmj, color=pmj_color, point_size=9, render_points_as_spheres=True)
            print(f"  {name}: tree {tree.n_points} nodes, {len(_pmjs(tree)) if tree else 0} PMJs")

    pl.add_text(
        "Strocchi four-chamber heart (Strocchi et al., PLoS ONE 2020, CC-BY-4.0)\n"
        "Endocardium from the mesh's own UVCs; Purkinje grown by the pipeline.\n"
        "LV blue, RV red, PMJs as spheres. Forward-model geometry, not a result.",
        font_size=10,
        color="black",
        position="upper_left",
    )
    pl.add_axes()
    pl.camera_position = "yz"

    Path(args.png).parent.mkdir(parents=True, exist_ok=True)

    if args.no_window:
        # off_screen plotter: render, capture, done.
        pl.screenshot(args.png)
        print(f"  wrote {args.png}")
    else:
        # show() renders the scene; ask it to capture the PNG and keep the window open.
        print("  opening viewer, orbit with the mouse, close the window to exit")
        pl.show(screenshot=args.png, auto_close=False)
        print(f"  wrote {args.png}")
    pl.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
