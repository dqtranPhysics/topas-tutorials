"""
topas_tools.py -- small helpers to read the TOPAS CSV files from these tutorials.

You normally do not run this file directly; plot_run.py and compare_runs.py use it.

Each TOPAS csv file starts with '#' header lines, e.g.
    # X in 77 bins of 0.2 cm
    # Z in 150 bins of 0.2 cm
    # DoseToMedium ( Gy ) : Sum   Mean   Standard_Deviation
followed by one line per bin:   x_index, y_index, z_index, Sum, Mean, Standard_Deviation
"""
import re
from pathlib import Path

import numpy as np


def _read_topas_csv(path):
    """Return (header_lines, data_array, report_names)."""
    path = Path(path)
    header = [ln for ln in path.read_text().splitlines() if ln.startswith("#")]
    data = np.atleast_2d(np.loadtxt(path, delimiter=",", comments="#"))
    # The last header line lists what each value column means.
    reports = header[-1].split(":")[-1].split()          # e.g. ['Sum', 'Mean', 'Standard_Deviation']
    return header, data, reports


def _bins(header, axis):
    """Read '# X in 77 bins of 0.2 cm' -> (77, 0.2). Returns (1, None) if absent."""
    for ln in header:
        m = re.match(rf"#\s*{axis} in (\d+) bins? +of ([\d.eE+-]+) cm", ln)
        if m:
            return int(m.group(1)), float(m.group(2))
    return 1, None


def _stats(sum_, mean, sd):
    """Number of histories N = Sum/Mean, and uncertainty of the mean = SD/sqrt(N)."""
    ok = mean > 0
    n_hist = float(np.median(sum_[ok] / mean[ok])) if ok.any() else np.nan
    sem = sd / np.sqrt(n_hist)
    return n_hist, sem


def load_dose_map(run):
    """
    Read DoseMap.csv from a run folder (or give the csv path directly).

    Returns a dict with
      x      : lateral bin centres (cm), 0 = beam axis
      depth  : depth bin centres (cm), 0 = phantom entrance
      dose   : 2D array [x, depth], dose per proton (Gy)
      err    : 2D array [x, depth], 1-sigma statistical uncertainty of dose (Gy)
      n      : number of protons (histories) in the run
    """
    path = Path(run)
    if path.is_dir():
        path = path / "DoseMap.csv"
    header, data, reports = _read_topas_csv(path)
    nx, dx = _bins(header, "X")
    nz, dz = _bins(header, "Z")

    col = {name: 3 + i for i, name in enumerate(reports)}   # value columns start after 3 index columns
    ix, iz = data[:, 0].astype(int), data[:, 2].astype(int)
    shape = (nx, nz)
    sum_, mean, sd = (np.zeros(shape) for _ in range(3))
    sum_[ix, iz] = data[:, col["Sum"]]
    mean[ix, iz] = data[:, col["Mean"]]
    sd[ix, iz] = data[:, col["Standard_Deviation"]]
    n_hist, sem = _stats(sum_, mean, sd)

    x = (np.arange(nx) + 0.5) * dx - nx * dx / 2           # centred on the beam axis
    depth = (np.arange(nz) + 0.5) * dz                     # bin 0 = entrance (slab was flipped)
    return dict(x=x, depth=depth, dose=mean, err=sem, n=n_hist, file=str(path))


def load_detector(run):
    """Read DetectorDose.csv -> (dose per proton, 1-sigma uncertainty, N).
    If no proton reached the detector, the dose is 0 and N (hence the uncertainty) is unknown (nan)."""
    path = Path(run)
    if path.is_dir():
        path = path / "DetectorDose.csv"
    header, data, reports = _read_topas_csv(path)
    row = data[0]
    vals = {name: row[i] for i, name in enumerate(reports)}   # no index columns for a 1-bin scorer
    n_hist, sem = _stats(np.array([vals["Sum"]]), np.array([vals["Mean"]]),
                         np.array([vals["Standard_Deviation"]]))
    return vals["Mean"], float(sem[0]), n_hist


def depth_dose(m, x_cm=0.0):
    """Depth-dose curve (dose, err) in the column of bins closest to lateral position x_cm."""
    i = int(np.argmin(abs(m["x"] - x_cm)))
    return m["dose"][i], m["err"][i], m["x"][i]


def lateral_profile(m, depth_cm):
    """Lateral profile (dose, err) in the row of bins closest to depth_cm."""
    k = int(np.argmin(abs(m["depth"] - depth_cm)))
    return m["dose"][:, k], m["err"][:, k], m["depth"][k]


def range_metrics(depth, dose):
    """Bragg-peak depth, and distal R90 / R80 (depth where dose falls to 90% / 80% of max)."""
    k = int(np.argmax(dose))
    out = {"peak_depth": depth[k], "entrance_dose": dose[:3].mean(), "peak_dose": dose[k]}
    for level in (90, 80):
        target = dose[k] * level / 100
        beyond = np.where(dose[k:] < target)[0]
        if len(beyond) == 0:
            out[f"R{level}"] = np.nan
            continue
        j = k + beyond[0]                                   # first bin below the level
        # linear interpolation between bins j-1 and j
        f = (dose[j - 1] - target) / (dose[j - 1] - dose[j])
        out[f"R{level}"] = depth[j - 1] + f * (depth[j] - depth[j - 1])
    return out


def fwhm(x, profile):
    """Full width at half maximum of a lateral profile (cm), by linear interpolation."""
    if profile.max() <= 0:
        return np.nan                                       # no dose at this depth
    half = profile.max() / 2
    above = np.where(profile >= half)[0]
    if len(above) < 3:
        return np.nan                                       # a few stray hits, not a beam
    i0, i1 = above[0], above[-1]
    if i0 == 0 or i1 == len(profile) - 1:
        return np.nan                                       # profile wider than the scoring grid
    left = np.interp(half, [profile[i0 - 1], profile[i0]], [x[i0 - 1], x[i0]])
    right = np.interp(half, [profile[i1 + 1], profile[i1]], [x[i1 + 1], x[i1]])
    return right - left
