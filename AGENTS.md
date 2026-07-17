# Monokrom — Agent Instructions

## Critical Formating Rule
- You are operating inside an OpenCode agent harness.

- You must output tool-calling schemas in absolute, flawless JSON.

- Never truncate code blocks or slip out of the requested JSON structure.

## Project layout
- `src/monokrom/` — three sub-packages: `common` (shared widgets/styles), `mill`, `plasma`
- `tests/` — pytest only; covers quickshapes, cut_recovery, consumable_change, hal_bridge, sheet_alignment, mdi_panel
- Entry points: `monokrom_plasma` → `monokrom.plasma:main`, `monokrom_mill` → `monokrom.mill:main`
- Both launch via `qtpyvcp.run_vcp()` after loading `{VCP_DIR}/{machine}/config.yml`

## Commands
```
pip install -e .           # editable install (Poetry backend, no lockfile)
pytest                     # run tests (conftest.py prepends src/ to sys.path)
pytest -k quickshapes      # focused verification of G-code generator
monokrom --install-sim     # copy LinuxCNC sim configs to ~/.linuxcnc/sims
```

## QtPyVCP plugin system
Plugins register via `pyproject.toml` under `[tool.poetry.plugins]`:
- `qtpyvcp.vcp` — VCP names (`monokrom_plasma`, `monokrom_mill`)
- `qtpyvcp.widgets` — widget groups loaded by QtPyVCP at runtime

New widgets must be exported in their package's `__init__.py` and registered under the matching plugin key.

## Generated files (don't edit these)
- `*_ui.py` — auto-generated from `.ui` Qt Designer files via `pyuic5`
- `monokrom_rc.py` — auto-generated from `.qrc` via `pyrcc5`

When editing a `.ui` file, regenerate with:
```
pyuic5 input.ui -o output_ui.py
```

## Stylesheets
- Common SCSS in `src/monokrom/common/sass/` compiles to `monokrom.qss`; themes: blue, red, yellow, dark, light. Build script: `common/sass/build-yellow-plasma.sh`.
- Plasma has its own `sass/plasma.scss` → `plasma.qss`.
- Mill has no SCSS of its own.

## Testing notes
- Tests use class-based pytest organization (`class TestXxx`).
- The `lines_list` fixture is a shared mutable list for G-code line accumulation — each test gets a fresh copy.
- Tests verify G-code output by checking that generated lines contain expected commands (M3, M5, G0, G1, G2, G3, etc.).
- No linting or typechecking config exists; only pytest is configured.

## Plasma package
The largest and most actively developed package. Key files:
- `mainwindow.py` (747 lines) — full plasma UI logic, cut recovery, consumable change, sheet alignment, VTK backplot
- `quickshapes.py` (1159 lines) — G-code shape generator for circles, rectangles, donuts, pipe flanges, gussets, etc.
- Three `.ui` variants: default, `mainwindow-1024-768.ui`, `mainwindow-less-greedy.ui`
