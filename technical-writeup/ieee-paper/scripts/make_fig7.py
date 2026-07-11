import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import corner
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Serif", "figure.dpi": 200})
OUT = "technical-writeup/ieee-paper/figures"
hl = json.load(open("outputs/hl_tarp_results.json"))
names = hl["theta_names"]
S = np.array(hl["posterior"]["samples"])
truth = [hl["true_theta"][k] for k in names]
labels = [n.replace("_", "\n") for n in names]
fig = corner.corner(
    S,
    labels=labels,
    truths=truth,
    truth_color="#b1163a",
    color="#12507a",
    show_titles=False,
    plot_datapoints=False,
    fill_contours=True,
    levels=(0.5, 0.9),
    hist_kwargs={"color": "#12507a"},
    label_kwargs={"fontsize": 7},
    max_n_ticks=3,
)
for ax in fig.axes:
    ax.tick_params(labelsize=5.5)
fig.set_size_inches(7.0, 7.0)
fig.savefig(f"{OUT}/fig7_posterior_corner.png", bbox_inches="tight")
plt.close(fig)
print("fig7 done", S.shape)
