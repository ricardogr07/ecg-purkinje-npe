import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "font.family": "DejaVu Serif",
        "font.size": 8.5,
        "axes.labelsize": 8.5,
        "axes.titlesize": 9,
        "legend.fontsize": 7,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
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
C_PRE = "#c7ccd1"
C_ID = "#1f6f43"
C_DIFF = "#b23a48"
C_POST = "#23507a"
names = list(post["contraction"].keys())

# ---- Calibration stacked (coverage over SBC) ----
fig, ax = plt.subplots(2, 1, figsize=(3.35, 4.2))
cc = cal["coverage_curve"]
nom = np.array(cc["nominal"])
a = ax[0]
a.plot(
    [nom.min(), nom.max()],
    [nom.min(), nom.max()],
    color="0.5",
    lw=0.9,
    ls=(0, (4, 3)),
    label="ideal",
)
a.plot(nom, cc["before"], "o-", color=C_PRE, ms=3, label="before")
a.plot(nom, cc["after"], "s-", color=C_POST, ms=3, label="after")
a.set_xlabel("nominal credible level")
a.set_ylabel("empirical coverage")
a.set_title("(a) expected coverage")
a.legend(frameon=False, loc="upper left")
b = ax[1]
kb = [cal["sbc"][k]["before"] for k in names]
ka = [cal["sbc"][k]["after"] for k in names]
xx = np.arange(len(names))
b.bar(xx - 0.2, kb, 0.4, label="before", color=C_PRE)
b.bar(xx + 0.2, ka, 0.4, label="after", color=C_POST)
b.axhline(0.05, color=C_DIFF, lw=0.9, ls=(0, (4, 3)))
b.text(len(names) - 0.5, 0.065, "p=0.05", ha="right", fontsize=6.5, color=C_DIFF)
b.set_xticks(xx)
b.set_xticklabels(names, rotation=38, ha="right")
b.set_ylabel("SBC KS p-value")
b.set_title("(b) SBC uniformity")
b.legend(frameon=False, loc="upper right")
fig.tight_layout(h_pad=1.4)
fig.savefig(f"{OUT}/fig_calibration_stacked.png")
plt.close(fig)

# ---- Budget + CRLB stacked ----
fig, ax = plt.subplots(2, 1, figsize=(3.35, 4.2))
curve = f3["curve"]
Ns = [c["n_train"] for c in curve]
a = ax[0]
for k in names:
    meds = [np.median([s["post_conformal"][k] for s in c["per_seed"]]) for c in curve]
    resp = f3["verdict"][k]["label"] == "data-limited"
    col = C_ID if resp else C_DIFF
    a.plot(Ns, meds, marker="o", ms=3, lw=1.2, ls="-" if resp else (0, (2, 2)), color=col)
    a.annotate(
        k,
        (Ns[-1], meds[-1]),
        xytext=(3, 0),
        textcoords="offset points",
        fontsize=6,
        va="center",
        color=col,
    )
a.axhline(1.0, color="0.45", lw=0.8, ls=(0, (4, 3)))
a.set_xlabel("training budget N")
a.set_ylabel("contraction")
a.set_xticks(Ns)
a.set_xlim(Ns[0] - 300, Ns[-1] + 1500)
a.set_ylim(0, 1.3)
a.set_title("(a) contraction vs budget")
a.text(
    0.02, 0.05, "green tightens, red flat/widens", transform=a.transAxes, fontsize=6, color="0.35"
)
b = ax[1]
rat = cr["ratio_features_over_waveform8"]
o = sorted(rat, key=lambda k: rat[k])
v = [rat[k] for k in o]
b.barh(np.arange(len(o)), v, color=C_POST)
for i, val in enumerate(v):
    b.text(val + 1, i, f"{val:.0f}x", va="center", fontsize=6.5)
b.set_yticks(np.arange(len(o)))
b.set_yticklabels(o)
b.set_xlim(0, 80)
b.set_xlabel("CRLB(features) / CRLB(waveform, 8-lead)")
b.set_title("(b) information lost to features")
fig.tight_layout(h_pad=1.4)
fig.savefig(f"{OUT}/fig_budget_crlb.png")
plt.close(fig)
print("stacked figures done")
