import matplotlib
import meshio
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

plt.rcParams.update({"font.family": "DejaVu Serif", "figure.dpi": 210})
OUT = "technical-writeup/ieee-paper/figures"
rng = np.random.default_rng(0)


def load(endo, tree, keep=4500):
    m = meshio.read(endo)
    tr = meshio.read(tree)
    tris = [c.data for c in m.cells if c.type == "triangle"][0]
    if len(tris) > keep:
        tris = tris[rng.choice(len(tris), keep, replace=False)]
    seg = [c.data for c in tr.cells if c.type == "line"][0]
    return m.points, tris, tr.points[seg]


lvP, lvT, lvS = load("outputs/f5_lv_endo_cut.obj", "outputs/f5_lv_tree.vtu")
rvP, rvT, rvS = load("outputs/f5_rv_endo_cut.obj", "outputs/f5_rv_tree.vtu")
allP = np.vstack([lvP, rvP])
ctr = allP.mean(0)


def draw(ax, elev, azim):
    for P, T, fc in [(lvP, lvT, "#d9dde2"), (rvP, rvT, "#d3dbe2")]:
        pc = Poly3DCollection(P[T], alpha=0.10, facecolor=fc, edgecolor="none")
        pc.set_rasterized(True)
        ax.add_collection3d(pc)
    ax.add_collection3d(Line3DCollection(lvS, colors="#c0143c", linewidths=0.6))
    ax.add_collection3d(Line3DCollection(rvS, colors="#0f5a86", linewidths=0.6))
    r = (allP.max(0) - allP.min(0)).max() / 2
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.dist = 7


fig = plt.figure(figsize=(7.0, 3.4))
for i, (el, az, ttl) in enumerate([(18, -115, "(a) anterior"), (14, 55, "(b) posterior-septal")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    draw(ax, el, az)
    ax.text2D(0.5, 0.02, ttl, transform=ax.transAxes, ha="center", fontsize=8.5)
fig.legend(
    handles=[
        Line2D([0], [0], color="#c0143c", lw=1.6, label="LV Purkinje network"),
        Line2D([0], [0], color="#0f5a86", lw=1.6, label="RV Purkinje network"),
        Line2D([0], [0], color="#d3dbe2", lw=7, alpha=0.7, label="endocardial surface"),
    ],
    loc="lower center",
    ncol=3,
    frameon=False,
    fontsize=8.5,
    bbox_to_anchor=(0.5, -0.01),
)
fig.subplots_adjust(left=0, right=1, top=1.02, bottom=0.11, wspace=-0.05)
fig.savefig(f"{OUT}/fig6_crtdemo_purkinje.png", bbox_inches="tight")
plt.close(fig)
print("fig6 done")
