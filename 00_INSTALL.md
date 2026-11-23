# 0. Installing TOPAS and the visual interface

**Do this before Day 1.** Building TOPAS from source takes **1–2 hours** (most of it is
compiling, so you can do other things while you wait) and needs about **10 GB** of free disk
space. In each group, at least one laptop must have a working install before class starts.

TOPAS is now open source as **OpenTOPAS**. These steps summarize the official quick-start guides
for **OpenTOPAS v4.3.1 + Geant4 11.4.3**. If anything here disagrees with the official guide,
follow the official guide:

| Your computer | Official guide |
|---|---|
| macOS (Sonoma 14 or newer) | <https://github.com/OpenTOPAS/OpenTOPAS/blob/master/OpenTOPAS_quickStart_MacOS.md> |
| Linux (Ubuntu / Debian) | <https://github.com/OpenTOPAS/OpenTOPAS/blob/master/OpenTOPAS_quickStart_Debian.md> |
| Windows 10/11 | <https://github.com/OpenTOPAS/OpenTOPAS/blob/master/OpenTOPAS_quickStart_WSL.md> (runs TOPAS inside Linux, using WSL) |

Documentation: <https://opentopas.readthedocs.io>. Help forum: the *Discussions* tab of the
OpenTOPAS GitHub page.

---

## What you are installing, and why

```
 TOPAS  (reads our simple text parameter files)
   └── built on  Geant4   (the Monte Carlo particle-transport toolkit)
         ├── Geant4 data files  (cross sections, about 4 GB)
         └── Qt + OpenGL        (the interactive 3D "visual interface")
   └── GDCM (reads DICOM images; TOPAS needs it to build, we will not use it)
```

The **visual interface** is the Qt window that shows the geometry and particle tracks. You get
it by building Geant4 **with Qt and OpenGL turned on** (`-DGEANT4_USE_QT=ON ...`) and building
TOPAS with `-DTOPAS_USE_QT=ON`. If you skip these flags, TOPAS still runs, but it cannot open
the 3D window, and you won't be able to do Day 1.

---

## Step-by-step overview (all platforms)

| Step | What | Notes |
|---|---|---|
| 1 | Install compilers and tools | macOS: Xcode command-line tools + Homebrew + XQuartz. Linux/WSL: `build-essential`, OpenGL/X11 dev packages |
| 2 | Install **Qt** and **CMake** | macOS: `brew install qt cmake git wget`. Ubuntu: `qt6-base-dev ...` packages from the guide |
| 3 | Download Geant4 **11.4.3** source | `wget https://gitlab.cern.ch/geant4/geant4/-/archive/v11.4.3/geant4-v11.4.3.tar.gz` |
| 4 | Download the Geant4 **data sets** into a `G4DATA` folder | The exact `wget` list is in the guide (16 files) |
| 5 | Build Geant4 **with Qt + OpenGL** | `cmake ... -DGEANT4_USE_QT=ON -DGEANT4_USE_QT_QT6=ON -DGEANT4_USE_OPENGL=ON` (macOS) |
| 6 | Build GDCM 2.6.8 | Bundled in the OpenTOPAS source folder |
| 7 | Clone OpenTOPAS, `git checkout v4.3.1`, build it **with Qt** | `cmake ../OpenTOPAS ... -DTOPAS_USE_QT=ON -DTOPAS_USE_QT6=ON` |
| 8 | Create a `topas` launcher script and put it on your `PATH` | Sets the library and data paths for you |
| 9 | Test (see below) | |

### Known issues in the official guides

1. **macOS, step 6.2 `cmake` command:** the line `-DGEANT4_USE_SYSTEM_ZLIB=ON` is missing a
   trailing backslash `\`. Without it the `-DCMAKE_OSX_ARCHITECTURES=arm64` line is not part
   of the command. Add the `\`. Leave out the `arm64` line on Intel Macs.
2. **Qt path on macOS:** replace `/opt/homebrew/Cellar/qt/6.9.3` with the output of
   `readlink -f $(brew --prefix qt)` on *your* machine.
3. **CMake 4.x and GDCM:** GDCM 2.6.8 does not configure with CMake 4.0 or newer. Use CMake
   3.28.x for GDCM only (the Debian guide explains how).
4. **Launcher script:** the guide's script ends with `.../bin/topas $1`. Change `$1` to `"$@"`
   so that file names containing spaces, and extra arguments, are passed through correctly:

   ```bash
   #!/bin/bash
   export QT_QPA_PLATFORM_PLUGIN_PATH=/Applications/TOPAS/OpenTOPAS-install/Frameworks
   export TOPAS_G4_DATA_DIR=/Applications/GEANT4/G4DATA
   export DYLD_LIBRARY_PATH=/Applications/TOPAS/OpenTOPAS-install/lib:/Applications/GEANT4/geant4-install/lib:$DYLD_LIBRARY_PATH
   /Applications/TOPAS/OpenTOPAS-install/bin/topas "$@"
   ```
   (On Linux/WSL use `LD_LIBRARY_PATH` and your `$HOME/Applications/...` paths instead.)

### Platform notes for the visual interface

* **macOS:** install **XQuartz** (<https://www.xquartz.org>), then log out and back in once.
  The TOPAS window itself is a normal Qt window.
* **Windows:** use **Windows 11**, where WSL includes graphics support ("WSLg"), so Linux GUI
  windows open on your Windows desktop. On Windows 10 you would need an X server, which we do
  not support in this class. Keep all tutorial files inside the Linux home folder (`~/...`),
  not under `/mnt/c/...`: it is much faster.
* **Linux:** works out of the box once the OpenGL/X11 dev packages from the guide are installed.

---

## Test your installation (do all three)

**Test 1: the `topas` command is found.** Open a **new** terminal window, then:

```bash
which topas
```

It should print the path to your launcher script. If it prints nothing, the launcher is not on
your `PATH` (step 8.2 of the guide).

**Test 2: a batch simulation.** It should start with `Welcome to TOPAS, Tool for Particle Simulation`.

```bash
cd /Applications/TOPAS/OpenTOPAS-install/examples/Scoring
```

```bash
topas Dose.txt
```

It should finish in under a minute and print a dose value. (On Linux/WSL the examples folder
is under `$HOME/Applications/TOPAS/OpenTOPAS-install/examples`.)

**Test 3: the visual interface.** Download or clone this tutorial folder, then:

```bash
cd topas_tutorials/params
```

```bash
topas day1_step2_beam.txt
```

A window opens showing a light-blue wire-frame box. TOPAS **pauses before running**. In the
left panel, click the **Parameter Control** tab. Its small toolbar has a **Run** button (a ▶
play icon, or the word "Run" if the icons were not found). Click it to start. You should see red proton
tracks entering one face of the box and stopping about halfway through it. Close the window
to quit.

> The terminal may print messages such as `mutex lock failure in ~G4Cache` or
> `QObject::connect: No such signal` when TOPAS exits or opens Qt. These are harmless.

---

## Python for the analysis (all platforms)

The analysis scripts need Python 3.9+ with `numpy` and `matplotlib`:

```bash
python3 -m pip install --user numpy matplotlib
```

Check:

```bash
python3 -c "import numpy, matplotlib; print('analysis tools OK')"
```

---

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `topas: command not found` | Open a new terminal; check `echo $PATH` contains `~/shellScripts` |
| `G4Exception ... G4ENSDFSTATEDATA` or "data directory" error | `TOPAS_G4_DATA_DIR` in the launcher does not point to the folder containing the unpacked data sets |
| `Library not loaded` / `cannot open shared object file` | `DYLD_LIBRARY_PATH` (mac) / `LD_LIBRARY_PATH` (Linux) in the launcher is wrong |
| Qt error `could not find the Qt platform plugin "cocoa"` / `"xcb"` | `QT_QPA_PLATFORM_PLUGIN_PATH` is wrong; on Linux try `sudo apt install libxcb-cursor0` |
| Nothing happens when you click **Run**, and the terminal showed `No such signal QSignalMapper::mapped(int)` | TOPAS was configured with `-DTOPAS_USE_QT6=OFF` but built against Qt 6, so the Parameter Control buttons are not connected. In the OpenTOPAS build folder: re-run `cmake` with `-DTOPAS_USE_QT=ON -DTOPAS_USE_QT6=ON`, delete the stale Qt cache with `rm -rf sequence/sequence_autogen`, then `make install`. (Without the `rm`, linking fails with `Undefined symbols ... TsQt6::staticMetaObject`.) |
| Window opens but is black or empty | Press **Run** (Parameter Control tab) first; then try rotating with the mouse. In WSL, run `wsl --update` from Windows |
| `Topas quitting, unable to open parameter file: scoring.txt` | You ran TOPAS from the wrong folder. Always `cd topas_tutorials/params` first |
| No 3D window at all, just text output | TOPAS or Geant4 was built without Qt; rebuild with the Qt flags |
