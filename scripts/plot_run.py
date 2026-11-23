"""
plot_run.py -- plot the results of ONE TOPAS run.

Usage (from the topas_tutorials folder):
    python scripts/plot_run.py params                      # Day 1: results of 'topas main.txt'
    python scripts/plot_run.py runs/seed1                  # a Day-2 run folder
    python scripts/plot_run.py runs/seed1 --offaxis 1.0 --depths 2 10 15

Makes one figure (saved as dose_summary.png in the run folder) with
  (a) the 2D dose map, (b) on-axis and off-axis depth-dose curves,
  (c) lateral profiles at a few depths,
and prints the key numbers.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import topas_tools as tt

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("run", help="run folder containing DoseMap.csv (or the csv file itself)")
ap.add_argument("--offaxis", type=float, nargs="+", default=[0.5, 1.0],
                help="off-axis distances (cm) for extra depth-dose curves")
ap.add_argument("--depths", type=float, nargs="+", default=[2.0, 10.0, 15.0],
                help="depths (cm) for lateral profiles")
ap.add_argument("--no-show", action="store_true", help="only save the png, do not open a window")
args = ap.parse_args()

m = tt.load_dose_map(args.run)
out_dir = Path(m["file"]).parent
title = out_dir.name
print(f"Run: {title}   ({m['n']:.0f} protons)")

fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))

# (a) 2D dose map: depth across, lateral position up
im = ax[0].imshow(m["dose"] * 1e9, origin="lower", aspect="auto", cmap="viridis",
                  extent=[0, m["depth"][-1] + m["depth"][0], m["x"][0] * 2 - m["x"][1], -m["x"][0] * 2 + m["x"][1]])
ax[0].set(xlabel="depth in water (cm)", ylabel="lateral position x (cm)", title="(a) dose map", ylim=(-4, 4))
fig.colorbar(im, ax=ax[0], label="dose per proton (nGy)")

# (b) depth-dose curves: on-axis plus off-axis
for x_cm in [0.0] + args.offaxis:
    d, e, x_used = tt.depth_dose(m, x_cm)
    ax[1].errorbar(m["depth"], d * 1e9, yerr=e * 1e9, lw=1.2, elinewidth=0.6,
                   label=f"x = {x_used:+.1f} cm" + (" (on axis)" if abs(x_used) < 0.15 else ""))
ax[1].set(xlabel="depth in water (cm)", ylabel="dose per proton (nGy)", title="(b) depth-dose curves")
ax[1].legend()

# (c) lateral profiles at a few depths
for z in args.depths:
    p, e, z_used = tt.lateral_profile(m, z)
    ax[2].errorbar(m["x"], p * 1e9, yerr=e * 1e9, lw=1.2, elinewidth=0.6, label=f"depth {z_used:.1f} cm")
ax[2].set(xlabel="lateral position x (cm)", ylabel="dose per proton (nGy)", title="(c) lateral profiles")
ax[2].legend()

fig.suptitle(title)
fig.tight_layout()
png = out_dir / "dose_summary.png"
fig.savefig(png, dpi=120)
print(f"Saved figure: {png}")

# ---- numbers
d0, e0, _ = tt.depth_dose(m, 0.0)
r = tt.range_metrics(m["depth"], d0)
print(f"On-axis Bragg peak depth : {r['peak_depth']:.1f} cm")
print(f"On-axis R90 / R80        : {r['R90']:.2f} / {r['R80']:.2f} cm")
print(f"Peak-to-entrance ratio   : {r['peak_dose'] / r['entrance_dose']:.2f}")
for z in args.depths:
    p, _, z_used = tt.lateral_profile(m, z)
    print(f"Lateral FWHM at {z_used:4.1f} cm  : {tt.fwhm(m['x'], p):.2f} cm")

det = out_dir / "DetectorDose.csv"
if det.exists():
    dose, err, _ = tt.load_detector(det)
    if dose > 0:
        print(f"Point detector (1 cm cube): {dose * 1e9:.4f} +/- {err * 1e9:.4f} nGy/proton "
              f"({100 * err / dose:.1f} %)")
    else:
        print("Point detector (1 cm cube): 0 -- no dose reached it")

if not args.no_show:
    plt.show()
