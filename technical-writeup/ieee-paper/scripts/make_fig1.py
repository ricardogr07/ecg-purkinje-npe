import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

plt.rcParams.update(
    {
        "font.family": "DejaVu Serif",
        "font.size": 9,
        "axes.labelsize": 9,
        "legend.fontsize": 7.3,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
    }
)
OUT = "technical-writeup/ieee-paper/figures"
hl = json.load(open("outputs/hl_tarp_results.json"))
post = hl["posterior"]
C_PRE = "#c7ccd1"
C_ID = "#1f6f43"
C_DIFF = "#b23a48"
order = sorted(post["contraction"], key=lambda k: post["contraction"][k])
pre = [post["contraction_pre_conformal"][k] for k in order]
pst = [post["contraction"][k] for k in order]
pcol = [C_ID if v < 0.85 else C_DIFF for v in pst]
x = np.arange(len(order))
w = 0.38
fig, ax = plt.subplots(figsize=(3.5, 2.75))
ax.bar(x - w / 2, pre, w, color=C_PRE, zorder=2)
ax.bar(x + w / 2, pst, w, color=pcol, zorder=2)
ax.axhline(1.0, color="0.45", lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.set_xticks(x)
ax.set_xticklabels([k for k in order], rotation=35, ha="right")
ax.set_ylabel("contraction  (posterior std / prior std)")
ax.set_ylim(0, 1.4)
leg = [
    Patch(fc=C_PRE, label="pre-conformal"),
    Patch(fc=C_ID, label="post: identifiable"),
    Patch(fc=C_DIFF, label="post: diffuse"),
    Line2D([0], [0], color="0.45", lw=0.9, ls=(0, (4, 3)), label="prior (no information)"),
]
ax.legend(
    handles=leg,
    frameon=False,
    loc="upper left",
    ncol=1,
    handlelength=1.3,
    handleheight=1.0,
    labelspacing=0.28,
    borderpad=0.2,
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig1_contraction_spectrum.png")
plt.close(fig)
print("fig1 rebuilt v2")
