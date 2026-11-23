# Hands-on TOPAS: a proton beam in a water phantom

Two group-work sessions introducing Monte Carlo dose calculation with
[OpenTOPAS](https://github.com/OpenTOPAS/OpenTOPAS). Students shoot a proton pencil beam into a
water phantom and score dose on-axis and off-axis. Every simulation runs at low statistics
(10,000 protons, about 5–30 s) on a laptop.

| | File | What students do |
|---|---|---|
| **Before class** | [00_INSTALL.md](00_INSTALL.md) | Install TOPAS with the Qt visual interface, plus Python with numpy/matplotlib |
| **Day 1** | [Day1_Worksheet.md](Day1_Worksheet.md) | Read the parts of a TOPAS simulation, view geometry and tracks in 3D, run a first batch simulation and plot the Bragg peak |
| **Day 2** | [Day2_Worksheet.md](Day2_Worksheet.md) | Compare runs: random seeds and statistics (everyone), then beam energy, scoring position, or geometry/materials (one per group) |
| Instructor | Instructor notes with answers are kept privately (not in this repo) | |

## Folder layout

```
topas_tutorials/
├── params/                       TOPAS parameter files: ALWAYS run topas from inside this folder
│   ├── physics_and_run.txt         physics list, seed, threads
│   ├── geometry.txt                world, 20x20x30 cm water phantom, optional 2 cm slab
│   ├── beam.txt                    150 MeV proton pencil beam, sigma 4 mm
│   ├── scoring.txt                 2D dose map (2 mm bins) + movable 1 cm^3 point detector
│   ├── main.txt                    full simulation, batch mode       (Day 1 Part 6, Day 2)
│   ├── visualization.txt           turns on the Qt/OpenGL 3D viewer
│   └── day1_step1..4_*.txt         Day 1 visual steps
├── scripts/
│   ├── run_experiment.py           run one variant -> runs/<name>/   (Day 2)
│   ├── plot_run.py                 plot one run: dose map, depth-dose, lateral profiles
│   ├── compare_runs.py             overlay runs + table (peak, R80, FWHM, detector dose ± σ)
│   └── topas_tools.py              CSV reader and metric helpers
└── runs/                           created on Day 2 (git-ignored)
```

The parameter files form one include **chain**:
`physics_and_run → geometry → beam → scoring → main` (or `→ visualization → day1_step*`).
TOPAS does not allow two sibling include files to set the same parameter, which is why each
file includes exactly one other file.

## Quick start (once TOPAS is installed)

```bash
cd topas_tutorials/params
```

```bash
topas day1_step2_beam.txt
```

```bash
topas main.txt
```

```bash
cd .. && python3 scripts/plot_run.py params
```

## Tested with

OpenTOPAS 4.2.p3 / Geant4 11.4.0 on macOS (Apple silicon, 8 cores). 10,000 protons at
150 MeV take about 4 s using all cores, or about 14 s on one core. The install guide targets the
current release (OpenTOPAS 4.3.1 / Geant4 11.4.3). The parameter syntax used here is the same
in both.
