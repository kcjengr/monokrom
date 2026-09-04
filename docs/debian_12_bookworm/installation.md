# Installation

## Prerequisites

- Linux (Debian 12/Bookworm)
- Python 3.7+
- PyQt5
- LinuxCNC (master branch, v2.10+)

## APT Install

<!-- TODO: Add actual apt install commands -->

```bash
# TODO: Add APT repository setup and package installation
sudo apt update
sudo apt install <packages>
```

## Developer Install

### Install QtPyVCP

MonoKrom Plasma requires a forked branch of qtpyvcp that adds the SQLite-backed plasma
processes plugin.

```bash
git clone https://github.com/kcjengr/qtpyvcp
cd qtpyvcp
git checkout main
python3 -m pip install -e .
```

If you already have a developer install of qtpyvcp, switch to the appropriate branch and
install SQLAlchemy:

```bash
cd <your-qtpyvcp-directory>
git checkout main
python3 -m pip install sqlalchemy
```

### Install MonoKrom

```bash
cd <directory-where-you-want-the-repo>
git clone https://github.com/kcjengr/monokrom
cd monokrom
python3 -m pip install -e .
```

This creates an editable install. To update to the latest development version:

```bash
cd monokrom
git pull
python3 -m pip install -e .
```

### Install Simulation Config

```bash
monokrom_plasma --install-sim
```

This copies the simulation configuration files to `~/linuxcnc/configs/sim.monokrom/`.

### Start LinuxCNC Simulator

```bash
linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
```

You should see the LinuxCNC status window and the MonoKrom Plasma VCP loading. The simulator
provides simulated HAL signals for all axes, plasma functions, and probing.
