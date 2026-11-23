# Day 1: The anatomy of a TOPAS simulation

**Goal:** understand the pieces every Monte Carlo dose simulation needs (geometry, source,
physics, scoring, run settings), see protons moving through water in 3D, and run a first
low-statistics simulation.

**Format:** groups of 3–4, one laptop drives the simulation and the others read the files and
answer questions. Swap the driver at every part. Time: about 2.5 hours.

**Before you start:** TOPAS and Python are installed and tested ([00_INSTALL.md](00_INSTALL.md)).
Open a terminal and go to the parameter folder. **Always run TOPAS from this folder**:

```bash
cd topas_tutorials/params
```

---

## Part 1: Read a simulation before running it (25 min)

Our simulation is a **150 MeV proton pencil beam** hitting a **20 × 20 × 30 cm water phantom**.
It is split into small files, each about one idea. Every file **includes** the previous one and
can **override** its parameters:

```
physics_and_run.txt   HOW particles interact; random seed; threads
      ▲ included by
geometry.txt          WHAT they travel through (world, water phantom, optional slab)
      ▲
beam.txt              WHERE they come from (the proton source)
      ▲
scoring.txt           WHAT we measure (dose map, point detector)
      ▲                          ▲
main.txt              visualization.txt  ← day1_step1/2/3 files
(batch run, Day 2)    (3D viewer on)
```

Every parameter line looks like `type:Category/Name/Property = value unit`, for example
`d:Ge/Phantom/HLZ = 15. cm`. The comments at the top of [geometry.txt](params/geometry.txt)
explain the types (`d`, `s`, `i`, `b`, `u`).

Open the four files in a text editor and answer:

1. What material is the world made of? The phantom?
2. `HLX` stands for "half-length in X". What are the **full** dimensions of the phantom?
3. Where is the beam's starting point (x, y, z)? Which direction does it travel? At what depth
   in water does the phantom start? (Hint: read the coordinate note in `geometry.txt`.)
4. What is the beam energy, and the energy spread? How wide is the beam spot (sigma)?
5. How many protons ("histories") will be simulated by `main.txt`?
6. In `scoring.txt`, what is the size of one bin of the dose map in x and in z?
   What is the size of the point detector?
7. The dose-map slab has `IsParallel = "True"`. In your own words, why can it overlap the
   point detector without breaking the simulation?
8. Which physics list is used? (No need to understand every module yet.)

---

## Part 2: See the geometry (15 min)

```bash
topas day1_step1_geometry.txt
```

The Qt window opens and **pauses**. In the left panel, click the **Parameter Control** tab
and press its **Run** button (▶, or the word "Run"). Zero protons are fired, so you only see
the volumes.

* Rotate the view by dragging with the mouse; zoom with the scroll wheel.
* The coloured axes are 5 cm long: **red = X, green = Y, blue = Z**.
* You can also type Geant4 viewer commands in the command box at the bottom, e.g.
  `/vis/viewer/set/viewpointThetaPhi 90 0` (side view) or `/vis/viewer/set/viewpointThetaPhi 0 0`
  (view along the beam).

Questions:

1. Which side of the phantom faces the beam (+Z or −Z)?
2. Check the phantom's size against your answer to Part 1 Q2 using the 5 cm axes.

Close the window when you are done.

---

## Part 3: Fire some protons (30 min)

```bash
topas day1_step2_beam.txt
```

Press **Run**. 20 protons are simulated. Colours: **red = protons, yellow = electrons,
green = gammas, grey = neutrons**.

Questions:

1. Roughly at what depth do the protons stop? (Use the axes. You will measure it precisely
   in Part 6.)
2. Do all protons stop at exactly the same depth? Why not? (Two physical reasons.)
3. Do you see any secondary particles? Which kinds? Where do they come from?
4. Do the proton tracks stay perfectly straight? What is the name of this effect?

Now **edit `day1_step2_beam.txt`** (not `beam.txt`) by adding a line at the bottom, rerun, and
observe. Try one change at a time:

| Add this line | What do you expect? What do you see? |
|---|---|
| `i:So/Beam/NumberOfHistoriesInRun = 100` | |
| `d:So/Beam/BeamEnergy = 100. MeV` | |
| `d:So/Beam/BeamEnergy = 200. MeV` | |
| `d:So/Beam/BeamPositionSpreadX = 15. mm` | |
| `s:So/Beam/BeamParticle = "e-"`  (and energy 20 MeV) | |
| `s:So/Beam/BeamParticle = "gamma"`  (and energy 6 MeV) | |

5. Why does adding a line in `day1_step2_beam.txt` change the value set in `beam.txt`?
6. Compare protons with electrons and photons: how is the shape of their tracks different?
   Why are protons attractive for radiotherapy?

Remove your extra lines before moving on.

---

## Part 4: Where do we measure dose? (15 min)

```bash
topas day1_step3_scoring.txt
```

Now the scoring volumes are drawn: a **green wire-frame slab** (the dose map) and a **red 1 cm
cube** (the point detector).

1. Where is the point detector (depth and off-axis distance)? Check this against `scoring.txt`.
2. The dose map is 1 cm thick in y. Why might a thin slab through the beam axis be enough to
   describe the dose from this beam? (Hint: symmetry.)
3. Is the point detector inside the high-dose region? Is it at the Bragg peak?

---

## Part 5: The GUI playground (20 min)

```bash
topas day1_step4_gui_playground.txt
```

This file is a complete simulation in one file. Parameters defined with a `c` in their type
(`dc:`, `sc:`, `bc:`, ...) are **changeable**: they appear in the **Parameter Control** tab
of the Qt window. Change one there, then press **Run** again to fire 10 more protons with the new value.

Each group member chooses one thing to try and shows the group:

* Switch on the slab (`Ge/Slab/Include` = True) and change its material:
  `G4_BONE_COMPACT_ICRU`, `G4_AIR`, `G4_LEAD`. What happens to where the protons stop?
* Change the phantom material to `G4_PLEXIGLASS` or `G4_LUNG_ICRP`.
* Change the beam particle to `alpha` or `neutron`.
* Make the phantom thinner (`Ge/Phantom/HLZ = 5 cm`) so that the protons exit.

Write down one surprising observation per person.

---

## Part 6: Your first real simulation, no graphics (30 min)

Graphics are slow. Real dose calculations run in **batch mode** using all CPU cores:

```bash
topas main.txt
```

10,000 protons take roughly 5–30 seconds on a laptop. Then:

1. How long did it take? How many CPU threads did TOPAS use? (Look at the output.)
2. Open `DoseMap.csv` in a text editor. What do the header lines tell you? What are the
   columns? Why are most values 0?

Now plot it. From the `topas_tutorials` folder:

```bash
cd ..
```

```bash
python3 scripts/plot_run.py params
```

This shows (a) the 2D dose map, (b) depth-dose curves on-axis and off-axis, (c) lateral
profiles at three depths, and prints key numbers. The figure is saved as
`params/dose_summary.png`.

3. At what depth is the **Bragg peak**? What is the distal **R80** (depth beyond the peak where
   the dose falls to 80 %)?
4. Compare R80 with the CSDA range of 150 MeV protons in water from NIST PSTAR:
   **15.77 g/cm²**. Should they agree? Why is R80 used as the "range" clinically?
5. What is the peak-to-entrance dose ratio?
6. Compare the on-axis and off-axis (x = 1 cm) depth-dose curves. Why does the off-axis curve
   rise much more with depth than the on-axis curve does?
7. How does the lateral beam width (FWHM) change with depth? Why?
8. Why do the curves look noisy? How could you make them smoother?

---

## Wrap-up (10 min)

Each group answers in two or three sentences, to share with the class:

* Name the five building blocks of a TOPAS simulation and the file where each one lives.
* One thing from the 3D view that surprised you.
* What would you change in order to simulate a 100 MeV beam in a bone phantom?

**Next time (Day 2):** we will run many simulations, changing one thing at a time, and compare
the results quantitatively.
