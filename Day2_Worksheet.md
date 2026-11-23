# Day 2: Experiments with the simulation

**Goal:** use the simulation like a lab instrument. Change **one thing at a time**, compare
dose quantitatively, and learn to tell a real physical difference from statistical noise.

**Format:** every group does **Experiment A** (statistics) first. The instructor then assigns
each group one of **B, C, D**. Groups present their findings in the last 30 minutes.
Time: about 2.5 hours.

All commands are run from the `topas_tutorials` folder:

```bash
cd topas_tutorials
```

---

## The two tools you will use

**`run_experiment.py`** runs one simulation with a few changes. Each run gets its own folder
under `runs/`:

```bash
python3 scripts/run_experiment.py seed2 --seed 2
```

This writes `runs/seed2/run.txt`, which contains `includeFile = main.txt` plus the lines that
changed (open it and look!). It then runs TOPAS and saves `DoseMap.csv`, `DetectorDose.csv`
and `topas.log` to `runs/seed2/`. Options:

| Option | TOPAS parameter it sets |
|---|---|
| `--seed 2` | `i:Ts/Seed` |
| `--histories 50000` | `i:So/Beam/NumberOfHistoriesInRun` (default 10000) |
| `--energy 100` | `d:So/Beam/BeamEnergy` (MeV) |
| `--spot 8` | beam spot sigma in x and y (mm) |
| `--det-depth 5` | `d:Ge/Detector/Depth` (cm) |
| `--det-x 1` | `d:Ge/Detector/TransX` (cm, off-axis) |
| `--phantom G4_PLEXIGLASS` | `s:Ge/Phantom/Material` |
| `--slab G4_BONE_COMPACT_ICRU` | switch on the 2 cm slab at depth 3–5 cm, with this material |
| `--set 'any TOPAS line'` | anything else (repeatable) |

**`compare_runs.py`** overlays several runs (the first one is the reference) and prints a
table of the Bragg-peak depth, R80, entrance and peak dose, lateral FWHM, and point-detector
dose ± 1σ:

```bash
python3 scripts/compare_runs.py runs/seed1 runs/seed2 runs/seed3
```

Useful options: `--normalize` (compare curve *shapes*), `--offaxis 1.0` (add depth-dose at
x = 1 cm), `--depth 15` (where to take the lateral profile), `--out myplot.png`.
To look at a single run in detail, use `python3 scripts/plot_run.py runs/seed2`.

> **Dose units:** all doses are **per proton** (nGy/proton). That lets you compare runs with
> different numbers of protons directly.
>
> **Uncertainty:** the `±` value is the 1σ statistical uncertainty of the mean, which TOPAS
> estimates from the spread of the dose deposited by individual protons:
> σ_mean = Standard_Deviation / √N.

---

## Experiment A (everyone): random seeds and statistics (40 min)

A Monte Carlo result is a **random estimate**. How big is the randomness?

1. Run the same simulation with five different seeds (about 5–30 s each):

   ```bash
   for s in 1 2 3 4 5; do python3 scripts/run_experiment.py seed$s --seed $s; done
   ```

2. Run seed 1 **again** under a different name:

   ```bash
   python3 scripts/run_experiment.py seed1_again --seed 1
   ```

3. Compare:

   ```bash
   python3 scripts/compare_runs.py runs/seed1 runs/seed1_again runs/seed2 runs/seed3 runs/seed4 runs/seed5 --out runs/A_seeds.png
   ```

Fill in the table for the **point detector** (depth 10 cm, on axis):

| Run | Detector dose (nGy/proton) | ± 1σ |
|---|---|---|
| seed1 | | |
| seed1_again | | |
| seed2 | | |
| seed3 | | |
| seed4 | | |
| seed5 | | |
| **mean of seeds 1–5** | | |
| **standard deviation of seeds 1–5** | | |

Questions:

1. Are `seed1` and `seed1_again` identical? What does this tell you about the "random"
   numbers in a Monte Carlo code? Why is this useful for debugging?
2. Is the spread of the five seeds (their standard deviation) similar to the ± that TOPAS
   reports for a single run? (With only 5 samples, "similar" means within a factor of about 1.5.)
3. On the "ratio to first run" panel, how big are the bin-to-bin fluctuations on axis? Are
   they bigger near the entrance or near the Bragg peak? Why?
4. Now run 5× more protons:

   ```bash
   python3 scripts/run_experiment.py N50k --histories 50000
   ```

   ```bash
   python3 scripts/compare_runs.py runs/seed1 runs/N50k
   ```

   By what factor did the detector uncertainty shrink? What factor do you expect from 1/√N?
   How many protons would you need to reach 0.1 % uncertainty in the detector? How long would
   that take on your laptop?
5. The dose-map bins (2 × 10 × 2 mm³) are much noisier than the 1 cm³ detector. Why?
   What is the trade-off between voxel size and statistical noise?

> **Rule for the rest of today:** a difference between two runs is only meaningful if it is
> clearly larger than about 2–3 times the combined uncertainty, σ_combined = √(σ₁² + σ₂²).

---

## Experiment B: beam energy and range (40 min)

```bash
for E in 70 100 150 200; do python3 scripts/run_experiment.py E$E --energy $E; done
```

```bash
python3 scripts/compare_runs.py runs/E70 runs/E100 runs/E150 runs/E200 --normalize --out runs/B_energy.png
```

| Energy (MeV) | Bragg-peak depth (cm) | R80 (cm) | PSTAR CSDA range (g/cm²) | Peak / entrance | Run time (s) |
|---|---|---|---|---|---|
| 70 | | | 4.08 | | |
| 100 | | | 7.72 | | |
| 150 | | | 15.77 | | |
| 200 | | | 25.96 | | |

1. How well does R80 match the CSDA range? Plot R80 against energy. Is the relationship
   linear? Fit R = α·E^p (the Bragg–Kleeman rule). What value of p do you get? (The textbook
   value is about 1.7–1.8.)
2. Why does the peak-to-entrance ratio *decrease* at higher energy? (Think about range
   straggling and nuclear interactions.)
3. Compare the width of the Bragg peak (distal falloff) at 70 and 200 MeV. Why is it different?
4. Why does the run time increase with energy?
5. **Extension:** compare the lateral profile at 2/3 of the range for each energy (use
   `--depth`). Which energy gives the widest beam at depth, and why?

---

## Experiment C: scoring position, on-axis vs off-axis (40 min)

Two ways to "measure" dose at a point: read it from the **dose map** (small bins), or move the
1 cm³ **point detector** (like a small ion chamber).

**C1: Detector along the beam axis**

```bash
for d in 2 5 10 14 15.5 16; do python3 scripts/run_experiment.py det_d$d --det-depth $d; done
```

```bash
python3 scripts/compare_runs.py runs/det_d2 runs/det_d5 runs/det_d10 runs/det_d14 runs/det_d15.5 runs/det_d16 --out runs/C1.png
```

**C2: Detector off-axis at 10 cm depth**

```bash
for x in 0 0.5 1 1.5 2 3; do python3 scripts/run_experiment.py det_x$x --det-x $x; done
```

```bash
python3 scripts/compare_runs.py runs/det_x0 runs/det_x0.5 runs/det_x1 runs/det_x1.5 runs/det_x2 runs/det_x3 --offaxis 1.0 --out runs/C2.png
```

For each detector position, also read the dose-map value at the same point from the plot (or
use `plot_run.py` with `--offaxis` and `--depths`).

| Position | Detector (nGy/p) ± σ | Dose map at the same point | Ratio detector / map |
|---|---|---|---|
| depth 2 cm, on axis | | | |
| depth 10 cm, on axis | | | |
| depth 15.5 cm (peak), on axis | | | |
| depth 10 cm, x = 1 cm | | | |
| depth 10 cm, x = 2 cm | | | |

1. Did moving the detector change the dose-map results? (Look at the comparison plot.) Why or
   why not? (Remember: the detector is made of water, and the dose map is a parallel world.)
2. Plot detector dose against depth and against off-axis distance. Compare with the dose-map
   curves.
3. At the Bragg peak, the 1 cm detector reads much **lower** than the peak of the 2 mm dose
   map. Explain this **volume-averaging** effect. What does it mean for choosing a detector
   to measure a Bragg peak?
4. Off-axis at 2–3 cm, how large is the relative uncertainty? Why is it so much larger than
   on axis? How many protons would you need for a 2 % result at x = 3 cm?
5. Why is the off-axis dose at x = 1 cm a larger fraction of the on-axis dose near the end of
   the range than near the entrance?

---

## Experiment D: geometry and materials (40 min)

**D1: A 2 cm heterogeneity slab at depth 3–5 cm, covering the whole field**

```bash
for m in G4_BONE_COMPACT_ICRU G4_AIR G4_LUNG_ICRP G4_ADIPOSE_TISSUE_ICRP; do python3 scripts/run_experiment.py slab_$m --slab $m; done
```

```bash
python3 scripts/run_experiment.py water_ref --seed 1
```

```bash
python3 scripts/compare_runs.py runs/water_ref runs/slab_G4_BONE_COMPACT_ICRU runs/slab_G4_AIR runs/slab_G4_LUNG_ICRP runs/slab_G4_ADIPOSE_TISSUE_ICRP --out runs/D1.png
```

| Slab material | R80 (cm) | Range shift vs water (cm) | Water-equivalent thickness of the 2 cm slab (cm) |
|---|---|---|---|
| water (reference) | | 0 | 2 |
| G4_BONE_COMPACT_ICRU | | | |
| G4_AIR | | | |
| G4_LUNG_ICRP | | | |
| G4_ADIPOSE_TISSUE_ICRP | | | |

1. Water-equivalent thickness (WET) = 2 cm − (range shift). Calculate the WET and the
   **relative stopping power** (RSP = WET / 2 cm) of each material.
2. `G4_LUNG_ICRP` barely changes the range. Look up its density in the Geant4 NIST material
   database (Geant4 "Book for Application Developers", appendix on materials). Why is this not like a real, air-filled lung? How would you
   make a realistic lung material in TOPAS?
3. Clinically, a range error of a few mm matters a lot. A CT-to-RSP conversion error of 3 %
   in 10 cm of tissue gives what range error?

**D2: Phantom material**

```bash
python3 scripts/run_experiment.py pmma --phantom G4_PLEXIGLASS
```

```bash
python3 scripts/compare_runs.py runs/water_ref runs/pmma --out runs/D2.png
```

4. What is the range in PMMA? Why does the "water-equivalent" depth not equal the physical
   depth? (The analysis still labels the axis "depth in water".)

**D3 (challenge): a half-field bone edge**

Make the slab cover only x > 0, and widen the beam so that both halves are irradiated:

```bash
python3 scripts/run_experiment.py halfbone --slab G4_BONE_COMPACT_ICRU --spot 10 --set 'd:Ge/Slab/HLX = 5 cm' --set 'd:Ge/Slab/TransX = 5 cm'
```

```bash
python3 scripts/plot_run.py runs/halfbone --offaxis -1 1
```

5. Describe the dose map. What happens to the Bragg peak at x = −1 cm and at x = +1 cm?
6. Near x = 0 the depth-dose curve has **two** peaks. Why? Why is this a problem for treatment
   plans with a single pencil beam crossing a bone edge?

---

## Presentations (30 min)

Each group gets 5 minutes and **one or two plots**. Answer:

1. What did you change, and what did you keep fixed?
2. What changed in the dose, and by how much (with uncertainty)?
3. Is the change real or noise? How do you know?
4. The physics explanation.
5. One thing that would make the simulation more realistic.

---

## Going further (optional)

* Change the beam spot size (`--spot 2`, `--spot 8`) and compare lateral profiles at several
  depths. At what depth does the original spot size stop mattering?
* Add angular divergence: `--set 's:So/Beam/BeamAngularDistribution = "Gaussian"'` plus the
  spread and cutoff parameters (see `examples/Scoring/Dose.txt` in your TOPAS install).
* Swap the physics list: `--set 'sv:Ph/Default/Modules = 1 "g4em-standard_opt0"'` (no nuclear
  interactions). What changes in the peak-to-entrance ratio and the off-axis halo?
* Score something else on the same grid, e.g. dose-averaged proton LET:

  ```bash
  python3 scripts/run_experiment.py let --set 's:Sc/LET/Quantity = "ProtonLET"' --set 's:Sc/LET/Component = "DoseMap"' --set 's:Sc/LET/OutputType = "csv"' --set 's:Sc/LET/IfOutputFileAlreadyExists = "Overwrite"'
  ```

  The file `LET.csv` is written to the `params` folder (the analysis scripts do not read it;
  try writing your own plot with `numpy.loadtxt`).
