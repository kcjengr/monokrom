# Installation

## Prerequisites

- Debian 13 (Trixie) with xfce4 desktop (recommended)
- 1920×1080 screen resolution
- Graphics hardware supporting OpenGL 3.2 / GLSL 1.50+
- LinuxCNC 2.9.8+ (must be installed **before** MonoKrom)
- **Do not set a root password** during Debian installation — leave it blank

## APT Install (Recommended)

The shared [qtpyvcp repository](https://repository.qtpyvcp.com/) provides pre-built
packages for MonoKrom Plasma on Debian 13. This is the simplest install path.

> **TODO:** Verify `repository.qtpyvcp.com/install.sh` and `uninstall.sh` still include
> `python3-monokrom` in their package lists after each repository update. The scripts
> reference MonoKrom but this should be confirmed before publishing.

### 1. Add the APT Repository

Run the following command to auto-detect your Debian release, architecture, and configure
the repository with the correct signing key:

```bash
curl -fsSL https://repository.qtpyvcp.com/install.sh | sudo sh
```

> **Note:** If you previously added the repository manually (e.g. via a `.list` file),
> this script will retire the old config and replace it with the correct one.

### 2. Install MonoKrom Plasma

```bash
sudo apt install python3-monokrom
```

### 3. Install Simulation Config

```bash
monokrom_plasma --install-sim
```

This copies the simulation configuration files to `~/linuxcnc/configs/sim.monokrom/`.

### 4. Start LinuxCNC Simulator

```bash
linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
```

You should see the LinuxCNC status window and the MonoKrom Plasma VCP loading. The simulator
provides simulated HAL signals for all axes, plasma functions, and probing.

### Updating

MonoKrom Plasma and its dependencies update through normal APT upgrades:

```bash
sudo apt update
sudo apt upgrade
```

During updates, the simulation configuration files shipped with MonoKrom may be overwritten.
It is strongly recommended to keep your machine configuration files with unique names
(avoid naming them `config.yml` — use something like `my_machine.yml`) to prevent
overwrites.

### Uninstall

To completely remove MonoKrom Plasma, QtPyVCP, and the APT repository:

```bash
curl -fsSL https://repository.qtpyvcp.com/uninstall.sh | sudo sh
```

This removes only the qtpyvcp repository's packages, sources, and keys. Your LinuxCNC
configs in `~/linuxcnc/configs/` are left untouched.

### Troubleshooting: Missing Key Error

If `sudo apt update` shows a warning like:

```
Missing key 50F874571F20C5B0BA225E2F0CDFCCE0388CFA48, which is needed to verify signature
```

Run the following one-liner to fix the repository configuration:

```bash
curl -fsSL https://repository.qtpyvcp.com/uninstall.sh | sudo sh && \
curl -fsSL https://repository.qtpyvcp.com/install.sh | sudo sh && \
sudo apt install -y python3-monokrom
```

This completely removes and reinstalls the repository configuration cleanly.

## Developer Install

This method installs from source into an editable (`-e`) pip install. Use this if you
plan to modify MonoKrom or QtPyVCP code.

### 1. Install LinuxCNC

Debian 13 (Trixie) installs via the LinuxCNC-prebuilt ISO which includes the PREEMPT-RT
kernel and LinuxCNC uspace package:

```bash
sudo apt update
sudo apt upgrade
sudo apt install linuxcnc-uspace
```

Download the ISO from:
https://www.linuxcnc.org/iso/linuxcnc_2.9.8-amd64.hybrid.iso

### 2. Install Dependencies

```bash
sudo apt install git python3-pip python3-venv
```

### 3. Install QtPyVCP

MonoKrom Plasma requires a forked branch of qtpyvcp that adds the SQLite-backed plasma
processes plugin. Debian 13 uses the `pyside6` branch.

```bash
cd ~/dev
git clone https://github.com/kcjengr/qtpyvcp
cd qtpyvcp
git checkout pyside6
python3 -m pip install -e .
```

If you already have a developer install of qtpyvcp, switch to the appropriate branch and
install SQLAlchemy:

```bash
cd <your-qtpyvcp-directory>
git checkout pyside6
python3 -m pip install sqlalchemy
```

### 4. Install MonoKrom

```bash
cd ~/dev
git clone https://github.com/kcjengr/monokrom
cd monokrom
python3 -m pip install -e .
```

### 5. Install Simulation Config

```bash
monokrom_plasma --install-sim
```

### 6. Start LinuxCNC Simulator

```bash
linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
```

### Updating a Developer Install

```bash
cd ~/dev/qtpyvcp
git pull && python3 -m pip install -e .
cd ~/dev/monokrom
git pull && python3 -m pip install -e .
```

### Uninstalling a Developer Install

```bash
rm -rf ~/dev/qtpyvcp ~/dev/monokrom
```
