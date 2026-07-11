import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams.update({"font.family": "DejaVu Serif", "figure.dpi": 200})
OUT = "technical-writeup/ieee-paper/figures"
fig, ax = plt.subplots(figsize=(7.0, 1.85))
ax.axis("off")
ax.set_xlim(0, 100)
ax.set_ylim(0, 26)


def box(x, y, w, h, text, fc="#eef2f6", ec="#23507a", fs=7.4):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=ec, lw=1.1
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(x1, x2, y):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y), (x2, y), arrowstyle="-|>", mutation_scale=10, color="#23507a", lw=1.1
        )
    )


TY = 14.5
TH = 10
box(1, TY, 15, TH, "theta (7D)\nconduction\nparams", fc="#fdf0e6", ec="#b23a48")
arrow(16, 19, TY + TH / 2)
box(19, TY, 16, TH, "fractal Purkinje\ntree + eikonal\n(purkinje-uv,\nmyocardial-mesh)")
arrow(35, 38, TY + TH / 2)
box(38, TY, 15, TH, "12-lead\npseudo-ECG\n(Gima-Rudy)")
arrow(53, 56, TY + TH / 2)
box(56, TY, 15, TH, "features +\nwaveform\n+ noise floor\n0.025 mV")
arrow(71, 74, TY + TH / 2)
box(74, TY, 15, TH, "amortized NPE\n(sbi flow)\n+ conformal")
# bottom box, two lines, comfortable padding
box(
    24,
    1.0,
    72,
    9.0,
    "posterior  ->  contraction spectrum\n+ SBC / coverage / TARP calibration",
    fc="#eaf3ee",
    ec="#1f6f43",
    fs=8.2,
)
ax.add_patch(
    FancyArrowPatch(
        (81, TY), (74, 10.2), arrowstyle="-|>", mutation_scale=10, color="#1f6f43", lw=1.1
    )
)
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_pipeline.png", bbox_inches="tight")
plt.close(fig)
print("fig5 rebuilt")
