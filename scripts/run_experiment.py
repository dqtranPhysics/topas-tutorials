"""
run_experiment.py -- run ONE TOPAS simulation with a few parameters changed,
keeping each run's input and output together in its own folder.

Usage (from the topas_tutorials folder):
    python scripts/run_experiment.py seed2 --seed 2
    python scripts/run_experiment.py E100 --energy 100
    python scripts/run_experiment.py det_d5 --det-depth 5 --det-x 0
    python scripts/run_experiment.py bone --slab G4_BONE_COMPACT_ICRU
    python scripts/run_experiment.py big --histories 50000
    python scripts/run_experiment.py custom --set 'd:So/Beam/BeamPositionSpreadX = 8 mm' \
                                            --set 'd:So/Beam/BeamPositionSpreadY = 8 mm'

What it does:
  1. creates runs/<name>/run.txt  =  "includeFile = main.txt"  +  your changes
  2. runs  topas  on it (from the params folder, so the includes are found)
  3. writes DoseMap.csv, DetectorDose.csv and topas.log into runs/<name>/
Open runs/<name>/run.txt to see exactly which TOPAS lines were changed.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent      # the topas_tutorials folder
PARAMS = HERE / "params"
RUNS = HERE / "runs"

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("name", help="name of this run (becomes the folder runs/<name>)")
ap.add_argument("--seed", type=int, help="random seed  (i:Ts/Seed)")
ap.add_argument("--histories", type=int, help="number of protons  (default 10000)")
ap.add_argument("--energy", type=float, help="beam energy in MeV")
ap.add_argument("--spot", type=float, help="beam spot sigma in mm (x and y)")
ap.add_argument("--det-depth", type=float, help="point-detector depth in cm")
ap.add_argument("--det-x", type=float, help="point-detector off-axis position in cm")
ap.add_argument("--phantom", help="phantom material, e.g. G4_WATER, G4_PLEXIGLASS")
ap.add_argument("--slab", help="switch on the 2 cm slab (depth 3-5 cm) with this material, "
                               "e.g. G4_BONE_COMPACT_ICRU, G4_AIR, G4_LUNG_ICRP")
ap.add_argument("--set", action="append", default=[], metavar="'TOPAS LINE'",
                help="any extra TOPAS parameter line (repeatable)")
ap.add_argument("--topas", default="topas", help="topas command (default: topas)")
args = ap.parse_args()

# ---- translate the friendly options into TOPAS parameter lines
lines = []
if args.seed is not None:
    lines.append(f"i:Ts/Seed = {args.seed}")
if args.histories is not None:
    lines.append(f"i:So/Beam/NumberOfHistoriesInRun = {args.histories}")
if args.energy is not None:
    lines.append(f"d:So/Beam/BeamEnergy = {args.energy} MeV")
if args.spot is not None:
    lines += [f"d:So/Beam/BeamPositionSpreadX = {args.spot} mm",
              f"d:So/Beam/BeamPositionSpreadY = {args.spot} mm"]
if args.det_depth is not None:
    lines.append(f"d:Ge/Detector/Depth = {args.det_depth} cm")
if args.det_x is not None:
    lines.append(f"d:Ge/Detector/TransX = {args.det_x} cm")
if args.phantom:
    lines.append(f's:Ge/Phantom/Material = "{args.phantom}"')
if args.slab:
    lines += ['b:Ge/Slab/Include = "True"', f's:Ge/Slab/Material = "{args.slab}"']
lines += args.set

if shutil.which(args.topas) is None:
    sys.exit(f"Cannot find the '{args.topas}' command. Did you finish the install guide (Step 8)?")

run_dir = RUNS / args.name
run_dir.mkdir(parents=True, exist_ok=True)
run_file = run_dir / "run.txt"
run_file.write_text(
    f"# Run '{args.name}' created by run_experiment.py\n"
    "includeFile = main.txt\n\n"
    "# --- send the output into this run's folder\n"
    f's:Sc/DoseMap/OutputFile      = "{run_dir}/DoseMap"\n'
    f's:Sc/DetectorDose/OutputFile = "{run_dir}/DetectorDose"\n\n'
    "# --- what is different in this run\n" + "\n".join(lines) + "\n"
)
print(f"Wrote {run_file.relative_to(HERE)}:")
for ln in lines:
    print("    " + ln)

print("Running TOPAS ... ", end="", flush=True)
t0 = time.time()
with open(run_dir / "topas.log", "w") as log:
    rc = subprocess.run([args.topas, str(run_file)], cwd=PARAMS, stdout=log, stderr=subprocess.STDOUT).returncode
dt = time.time() - t0

if not (run_dir / "DoseMap.csv").exists() or "serious error" in (run_dir / "topas.log").read_text():
    print(f"FAILED (exit code {rc}). Look at the end of {run_dir.relative_to(HERE)}/topas.log")
    sys.exit(1)
print(f"done in {dt:.0f} s.  Results in {run_dir.relative_to(HERE)}/")
