"""
compare_runs.py -- overlay several TOPAS runs and print a comparison table.

Usage (from the topas_tutorials folder):
    python scripts/compare_runs.py runs/seed1 runs/seed2 runs/seed3
    python scripts/compare_runs.py runs/E100 runs/E150 runs/E200 --normalize
    python scripts/compare_runs.py runs/seed* --offaxis 1.0 --depth 10

Options:
    --offaxis X   also compare depth-dose curves at lateral position X cm
    --depth Z     depth (cm) for the lateral-profile comparison (default 10)
    --normalize   scale every on-axis curve to its own maximum (to compare SHAPES)
    --out FILE    figure file name (default: comparison.png in the current folder)
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import topas_tools as tt

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("runs", nargs="+", help="run folders to compare (first one is the reference)")
ap.add_argument("--offaxis", type=float, default=None)
ap.add_argument("--depth", type=float, default=10.0)
ap.add_argument("--normalize", action="store_true")
ap.add_argument("--out", default="comparison.png")
ap.add_argument("--no-show", action="store_true")
args = ap.parse_args()

maps = [tt.load_dose_map(r) for r in args.runs]
names = [Path(r).name for r in args.runs]

n_panels = 4 if args.offaxis is not None else 3
fig, ax = plt.subplots(1, n_panels, figsize=(5 * n_panels, 4.6))
ref_d, ref_e, _ = tt.depth_dose(maps[0], 0.0)

print(f"{'run':<16}{'N':>8}{'peak(cm)':>10}{'R80(cm)':>9}{'entrance':>11}{'peak':>11}"
      f"{'FWHM@'+str(args.depth):>11}{'detector (nGy)':>24}")
for name, m in zip(names, maps):
    d, e, _ = tt.depth_dose(m, 0.0)
    scale = 1 / d.max() if args.normalize else 1e9
    ax[0].errorbar(m["depth"], d * scale, yerr=e * scale, lw=1.1, elinewidth=0.5, label=name)

    # ratio to the reference run, only where the reference has meaningful dose
    ok = ref_d > 0.05 * ref_d.max()
    ax[1].plot(m["depth"][ok], d[ok] / ref_d[ok], lw=1.1, label=name)

    p, pe, z_used = tt.lateral_profile(m, args.depth)
    ax[2].errorbar(m["x"], p * 1e9, yerr=pe * 1e9, lw=1.1, elinewidth=0.5, label=name)

    if args.offaxis is not None:
        od, oe, x_used = tt.depth_dose(m, args.offaxis)
        ax[3].errorbar(m["depth"], od * 1e9, yerr=oe * 1e9, lw=1.1, elinewidth=0.5, label=name)

    r = tt.range_metrics(m["depth"], d)
    det_txt = ""
    det = Path(m["file"]).parent / "DetectorDose.csv"
    if det.exists():
        dd, de, _ = tt.load_detector(det)
        det_txt = f"{dd * 1e9:.4f} +/- {de * 1e9:.4f}" if dd > 0 else "0 (no dose)"
    print(f"{name:<16}{m['n']:>8.0f}{r['peak_depth']:>10.1f}{r['R80']:>9.2f}"
          f"{r['entrance_dose'] * 1e9:>11.4f}{r['peak_dose'] * 1e9:>11.4f}"
          f"{tt.fwhm(m['x'], p):>11.2f}{det_txt:>24}")

ax[0].set(xlabel="depth (cm)", ylabel="relative dose" if args.normalize else "dose per proton (nGy)",
          title="on-axis depth dose")
ax[1].axhline(1, color="k", lw=0.8)
ax[1].set(xlabel="depth (cm)", ylabel=f"dose / dose({names[0]})", title="ratio to first run (on axis)")
ax[2].set(xlabel="lateral position x (cm)", ylabel="dose per proton (nGy)",
          title=f"lateral profile at depth {z_used:.1f} cm")
if args.offaxis is not None:
    ax[3].set(xlabel="depth (cm)", ylabel="dose per proton (nGy)", title=f"depth dose at x = {x_used:+.1f} cm")
for a in ax:
    a.legend(fontsize=8)
fig.tight_layout()
fig.savefig(args.out, dpi=120)
print(f"\nSaved figure: {args.out}")
if not args.no_show:
    plt.show()
