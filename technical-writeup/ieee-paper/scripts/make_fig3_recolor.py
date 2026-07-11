import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "font.family": "DejaVu Serif",
        "font.size": 9,
        "axes.labelsize": 9,
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
f3 = json.load(open("outputs/f3_contraction_vs_n.json"))
curve = f3["curve"]
Ns = [c["n_train"] for c in curve]
disp = {k: k for k in post["contraction"]}
C_ID = "#1f6f43"
C_DIFF = "#b23a48"
fig, ax = plt.subplots(figsize=(3.5, 2.7))
for k in post["contraction"]:
    meds = [np.median([s["post_conformal"][k] for s in c["per_seed"]]) for c in curve]
    resp = f3["verdict"][k]["label"] == "data-limited"
    col = C_ID if resp else C_DIFF
    ax.plot(Ns, meds, marker="o", ms=3, lw=1.3, ls="-" if resp else (0, (2, 2)), color=col)
    ax.annotate(
        disp[k],
        (Ns[-1], meds[-1]),
        xytext=(4, 0),
        textcoords="offset points",
        fontsize=6.5,
        va="center",
        color=col,
    )
ax.axhline(1.0, color="0.4", lw=0.8, ls=(0, (4, 3)))
ax.set_xlabel("training budget N")
ax.set_ylabel("post-conformal contraction")
ax.set_xticks(Ns)
ax.set_xlim(Ns[0] - 300, Ns[-1] + 1200)
ax.set_ylim(0, 1.3)
ax.text(
    0.02,
    0.04,
    "green = tightens with N (budget-limited)\nred = flat or widening",
    transform=ax.transAxes,
    fontsize=6.3,
    color="0.3",
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_contraction_vs_N.png")
plt.close(fig)
print("fig3 recolored")
