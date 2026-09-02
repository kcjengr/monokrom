# Quick Start

This guide walks you through installing MonoKrom Plasma and running it with the LinuxCNC
simulator. For real hardware setup, see the [Integrator Guide](integrator-guide/index.md).

## Prerequisites

- Linux (Debian 12/Bookworm recommended)
- Python 3.7+
- PySide6
- LinuxCNC (master branch, v2.10+)

## Step 1: Install QtPyVCP

MonoKrom Plasma requires a forked branch of qtpyvcp that adds the SQLite-backed plasma
processes plugin. Choose the branch that matches your Debian version:

| Debian Version | Branch |
|----------------|--------|
| Debian 12 (Bookworm) | `main` |
| Debian 13 (Trixie) | `pyside6` |

```bash
git clone https://github.com/kcjengr/qtpyvcp
cd qtpyvcp
git checkout main    # Debian 12
# git checkout pyside6  # Debian 13
python3 -m pip install -e .
```

If you already have a developer install of qtpyvcp, switch to the appropriate branch and
install SQLAlchemy:

```bash
cd <your-qtpyvcp-directory>
git checkout main    # Debian 12
# git checkout pyside6  # Debian 13
python3 -m pip install sqlalchemy
```

## Step 2: Install MonoKrom

```bash
cd <directory-where-you-want-the-repo>
git clone https://github.com/joco-nz/monokrom-vcp
cd monokrom-vcp
python3 -m pip install -e .
```

This creates an editable install. To update to the latest development version:

```bash
cd monokrom-vcp
git pull
python3 -m pip install -e .
```

## Step 3: Install Simulation Config

```bash
monokrom --install-sim
```

This copies the simulation configuration files to `~/linuxcnc/configs/sim.monokrom/`.

## Step 4: Start LinuxCNC Simulator

```bash
linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
```

You should see the LinuxCNC status window and the MonoKrom Plasma VCP loading. The simulator
provides simulated HAL signals for all axes, plasma functions, and probing.

## Step 5: Verify Basic Operation

Once the VCP has loaded:

1. **Home the machine** — Click the **HOME** button for each axis (X, Y, Z) on the Main Tab.
2. **Zero the axes** — Click the `0` button next to each DRO (digital readout) to set zero
   offsets. For Z, jog down to the minimum limit first, then touch off.
3. **Jog the axes** — Use the jog controls on the Main Tab to move the axes. Verify all
   axes respond correctly.
4. **Load a program** — Click the file browser icon or press `Ctrl+O` to load a G-code file
   from `~/linuxcnc/nc_files/`. The VTK backplot should display the toolpath.
5. **Select a material** — Click the material dropdown in the preview window to select a
   material from the process database.
6. **Probe test** — On the Probe tab, click **PROBE TEST**. The Z axis should probe down,
   find the material surface, and move up to the pierce height.

## Next Steps

- Read the [User Guide](user-guide/index.md) for detailed operation of each tab and panel.
- Read the [Integrator Guide](integrator-guide/index.md) for hardware wiring and configuration.
- Read the [Troubleshooting](troubleshooting.md) section if you encounter issues.
