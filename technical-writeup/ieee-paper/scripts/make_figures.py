import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams.update(
    {
        "font.family": "DejaVu Serif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
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
cal = hl["calibration"]
f3 = json.load(open("outputs/f3_contraction_vs_n.json"))
cr = json.load(open("outputs/crlb_comparison.json"))

disp = {
    "delta_iv": "delta_iv",
    "cv_myo": "cv_myo",
    "init_length_rv": "init_length_rv",
    "cv": "cv",
    "init_length_lv": "init_length_lv",
    "w": "w",
    "branch_angle": "branch_angle",
}
C_ID = "#1f6f43"
C_DIFF = "#b23a48"
C_PRE = "#9bb7d4"
C_POST = "#23507a"

# ---- Fig 1: contraction spectrum (pre vs post), sorted by post ----
order = sorted(post["contraction"], key=lambda k: post["contraction"][k])
pre = [post["contraction_pre_conformal"][k] for k in order]
pst = [post["contraction"][k] for k in order]
x = np.arange(len(order))
w = 0.38
fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.bar(x - w / 2, pre, w, label="pre-conformal", color=C_PRE)
ax.bar(x + w / 2, pst, w, label="post-conformal", color=[C_ID if v < 0.85 else C_DIFF for v in pst])
ax.axhline(1.0, color="0.4", lw=0.8, ls=(0, (4, 3)))
ax.text(len(order) - 0.5, 1.02, "prior (no info)", ha="right", va="bottom", fontsize=7, color="0.4")
ax.set_xticks(x)
ax.set_xticklabels([disp[k] for k in order], rotation=35, ha="right")
ax.set_ylabel("contraction  (post std / prior std)")
ax.set_ylim(0, 1.35)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(f"{OUT}/fig1_contraction_spectrum.png")
plt.close(fig)

# ---- Fig 2: calibration (reliability + per-param KS) ----
cc = cal["coverage_curve"]
nom = np.array(cc["nominal"])
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
a = axes[0]
a.plot(
    [nom.min(), nom.max()],
    [nom.min(), nom.max()],
    color="0.5",
    lw=0.9,
    ls=(0, (4, 3)),
    label="ideal",
)
a.plot(nom, cc["before"], "o-", color=C_PRE, ms=3, label="before conformal")
a.plot(nom, cc["after"], "s-", color=C_POST, ms=3, label="after conformal")
a.set_xlabel("nominal credible level")
a.set_ylabel("empirical coverage")
a.set_title("(a) expected coverage")
a.legend(frameon=False, loc="upper left")
b = axes[1]
ks = cal["sbc"]
order2 = list(post["contraction"].keys())
kb = [ks[k]["before"] for k in order2]
ka = [ks[k]["after"] for k in order2]
xx = np.arange(len(order2))
b.bar(xx - 0.2, kb, 0.4, label="before", color=C_PRE)
b.bar(xx + 0.2, ka, 0.4, label="after", color=C_POST)
b.axhline(0.05, color=C_DIFF, lw=0.9, ls=(0, (4, 3)))
b.text(len(order2) - 0.5, 0.056, "p=0.05", ha="right", fontsize=7, color=C_DIFF)
b.set_xticks(xx)
b.set_xticklabels([disp[k] for k in order2], rotation=35, ha="right")
b.set_ylabel("SBC KS p-value")
b.set_title("(b) SBC uniformity")
b.legend(frameon=False, loc="upper right")
atc_pre = cal["tarp_atc"]
atc_post = cal["tarp_atc_post"]
fig.suptitle(
    f"joint TARP ATC: {atc_pre:+.3f} (overconfident) -> {atc_post:+.3f} (calibrated)",
    fontsize=8,
    y=1.02,
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig2_calibration.png", bbox_inches="tight")
plt.close(fig)

# ---- Fig 3: contraction vs N (two-point, per seed) ----
curve = f3["curve"]
Ns = [c["n_train"] for c in curve]
fig, ax = plt.subplots(figsize=(3.5, 2.7))
resp = {
    "cv": C_ID,
    "delta_iv": C_ID,
    "init_length_rv": C_ID,
    "cv_myo": C_ID,
    "init_length_lv": C_ID,
    "w": C_DIFF,
    "branch_angle": C_DIFF,
}
for k in post["contraction"]:
    meds = [np.median([s["post_conformal"][k] for s in c["per_seed"]]) for c in curve]
    lab_resp = f3["verdict"][k]["label"]
    ls = "-" if lab_resp == "data-limited" else (0, (2, 2))
    ax.plot(Ns, meds, marker="o", ms=3, lw=1.2, ls=ls, color=resp[k])
    ax.annotate(
        disp[k],
        (Ns[-1], meds[-1]),
        xytext=(4, 0),
        textcoords="offset points",
        fontsize=6.5,
        va="center",
        color=resp[k],
    )
ax.axhline(1.0, color="0.4", lw=0.8, ls=(0, (4, 3)))
ax.set_xlabel("training budget N")
ax.set_ylabel("post-conformal contraction")
ax.set_xticks(Ns)
ax.set_xlim(Ns[0] - 300, Ns[-1] + 1100)
ax.set_ylim(0, 1.3)
ax.text(
    0.02,
    0.03,
    "solid = budget-responsive   dashed = flat",
    transform=ax.transAxes,
    fontsize=6.5,
    color="0.35",
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_contraction_vs_N.png")
plt.close(fig)

# ---- Fig 4: CRLB features vs waveform ratio ----
rat = cr["ratio_features_over_waveform8"]
order4 = sorted(rat, key=lambda k: rat[k])
vals = [rat[k] for k in order4]
fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.barh(np.arange(len(order4)), vals, color=C_POST)
for i, v in enumerate(vals):
    ax.text(v + 1, i, f"{v:.0f}x", va="center", fontsize=7)
ax.set_yticks(np.arange(len(order4)))
ax.set_yticklabels([disp[k] for k in order4])
ax.set_xlabel("CRLB(features) / CRLB(waveform, 8-lead)")
ax.set_xlim(0, 80)
ax.set_title("Fisher information lost to feature compression")
fig.tight_layout()
fig.savefig(f"{OUT}/fig4_crlb_features_vs_waveform.png")
plt.close(fig)

# ---- Fig 5: pipeline architecture diagram ----
fig, ax = plt.subplots(figsize=(7.0, 2.2))
ax.axis("off")
ax.set_xlim(0, 100)
ax.set_ylim(0, 30)


def box(x, y, w, h, text, fc="#eef2f6", ec="#23507a"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=ec, lw=1.1
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.2)


def arrow(x1, x2, y=15):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y), (x2, y), arrowstyle="-|>", mutation_scale=10, color="#23507a", lw=1.1
        )
    )


box(1, 10, 15, 10, "theta (7D)\nconduction\nparams", fc="#fdf0e6", ec="#b23a48")
arrow(16, 19)
box(19, 10, 16, 10, "fractal Purkinje\ntree + eikonal\n(purkinje-uv,\nmyocardial-mesh)")
arrow(35, 38)
box(38, 10, 15, 10, "12-lead\npseudo-ECG\n(Gima-Rudy)")
arrow(53, 56)
box(56, 10, 15, 10, "features +\nwaveform\n+ noise floor\n0.025 mV")
arrow(71, 74)
box(74, 10, 15, 10, "amortized NPE\n(sbi flow)\n+ conformal")
box(
    37,
    0.5,
    52,
    7.5,
    "posterior -> contraction spectrum + SBC / coverage / TARP calibration",
    fc="#eaf3ee",
    ec="#1f6f43",
)
ax.add_patch(
    FancyArrowPatch((81, 10), (70, 8), arrowstyle="-|>", mutation_scale=10, color="#1f6f43", lw=1.1)
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_pipeline.png", bbox_inches="tight")
plt.close(fig)

print("figures written:")
import os

for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(f"{OUT}/{f}"), "B")
