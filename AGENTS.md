# MonoKrom — Agent Notes

## Project structure

- `src/monokrom/` — Python package. Three sub-packages:
  - `plasma/` — Plasma VCP (main active work)
  - `mill/` — Mill VCP (less active)
  - `common/` — shared widgets, stylesheets, fonts, SASS partials
- `linuxcnc/configs/sim.monokrom/` — LinuxCNC sim configs. Three subdirs: `common/`, `mill/`, `plasmac/`. Installed to `~/linuxcnc` via `--install-sim`.

## Run / install

```
python3 -m pip install -e .
```

Two CLI entry points after install:

- `monokrom_plasma --ini <config>` — launches Plasma VCP
- `monokrom_mill --ini <config>` — launches Mill VCP

Install sim configs to `~/linuxcnc`:

```
monokrom_plasma --install-sim    # same as monokrom_mill --install-sim
```

Copies repo root's `linuxcnc/` → `~/linuxcnc` (update mode, newer files only).

## LinuxCNC runtime dependency

Both Plasma and Mill VCPs require a running LinuxCNC instance to connect to.
Before launching the VCP, start LinuxCNC with the appropriate config:

```
linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/your_config.ini
```

The VCP connects to LinuxCNC via HAL sockets — if LinuxCNC is not running,
the VCP will fail to initialize. Use `--install-sim` to install the simulated
config files first.

## Qt / runtime quirks

- **PySide6 is required.** The codebase forces `QT_API=pyside6` in `src/monokrom/__init__.py:4`. If PyQt5 is also installed, Qt will default to it unless this env var is set.
- **OpenGL RHI backend is forced** via `QSG_RHI_BACKEND=opengl` at module load (`__init__.py:8`) and again in `main()` at runtime. Without this, Qt6 defaults to Vulkan/Metal which produces a black screen on systems without those backends.
- Dev mode flag `--develop` enables live QSS reload.

## UI workflow

- `.ui` files (Qt Designer) → compiled to `*_ui.py` by `pyside6-uic`. **NOT committed** — listed in `.gitignore`. Regenerate with: `pyside6-uic input.ui -o output_ui.py`
- `.qrc` resources → compiled to `*_rc.py` by `pyside6-rcc`. **NOT committed** — listed in `.gitignore`. Regenerate with: `pyside6-rcc input.qrc -o output_rc.py`
- `.qrc` and `.ui` files ARE committed.
- Stylesheets: `common/monokrom.qss` (generated from SASS), plus machine-specific `.qss` files (`plasma/plasma.qss`, `mill/plasma.qss`).

### SASS → QSS compilation

SASS lives in `common/sass/` (shared partials) and `plasma/sass/` (machine-specific). Compiled manually:

```bash
cd src/monokrom/common/sass && qtsass ./yellow.scss -o ../monokrom.qss
```

`qtsass` is not a declared dependency — it's a dev-only tool.

## Config system

- VCP config is YAML with Jinja2 templating (`config.yml` per machine).
- Uses `{{ file.dir }}` variable for paths relative to the config file.
- `{% include "default_menubar.yml" %}` for shared fragments from qtpyvcp.
- Settings in `config.yml` under `settings:` are persistent (stored as pickle by default).
- Plasma config (`plasma/config.yml`) has extensive THC/probe/plasma settings; Mill config is minimal.

## Dependencies — plasma VCP

The plasma VCP requires a **forked branch of qtpyvcp** (not the public PyPI package):

```
git clone https://github.com/kcjengr/qtpyvcp
cd qtpyvcp
git checkout plasma_db
python3 -m pip install -e .
```

This branch adds `PlasmaProcesses` plugin backed by SQLite (registered in `plasma/config.yml:data_plugins.plasmaprocesses`).

## Packaging

- Build system: Poetry (`pyproject.toml`). No `poetry.lock` committed.
- Debian packaging via `debian/`. Script `build_deb.sh` installs apt deps then runs `debuild -ePATH -b -uc -us`.
- `versioneer[toml]` is in build requirements but fully commented out — version stays `"0.0"`.

## What's missing (no tooling)

- No test framework, no linting, no formatting config, no typecheck, no CI workflows.
- No pre-commit hooks.
- Eclipse project files present (`.project`, `.pydevproject`, `.settings/`) but not maintained for other IDEs.
