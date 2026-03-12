# PySide6 Conversion Plan for Monokrom (exclude Mill)

Date: 2026-02-26

Purpose
- Create a reproducible, low-risk plan to convert the `monokrom` VCP to run on PySide6, using `probe_basic` as a working reference.
- Mill UI/code is intentionally excluded from this plan; focus areas are `common/` and `plasma/`.

Repository layout (relevant parts)
- `src/monokrom/__init__.py` — CLI / entrypoint (supports `--qt-api` override)
- `src/monokrom/common/` — shared widgets, many `.ui` files and designer plugins
- `src/monokrom/plasma/` — plasma-specific UI and logic: `.ui` files, `mainwindow.py`, `config.yml`
- `src/monokrom/mill/` — MILL (ignored for this work)

High-level findings
- Project already uses `qtpy` and `qtpyvcp` widely — most modules import via `qtpy.QtWidgets`, `qtpy.QtCore`, and `qtpy.uic`.
- UI assets: many `.ui` files live in `common/` and `plasma/` and are loaded at runtime via `uic.loadUi` or compiled UI modules.
- Custom widgets are exposed to Designer via `qtpyvcp.widgets.qtdesigner` hooks and used in `.ui` headers.
- `qtpyvcp` and linuxcnc/hal integrations are central and must remain functional.
- `probe_basic` is a useful reference: it already includes PySide6-generated UI modules and examples of `qtpy` + `PySide6` usage.

Conversion approach (recommended)
- Preferred path: Continue using `qtpy` as the abstraction layer and target PySide6 as the backend (set `QT_API=pyside6` or install `PySide6` and use `qtpy`'s detection). This keeps code changes minimal because existing imports use `qtpy`.
- Alternative (more invasive): Replace `qtpy` calls with direct `PySide6` imports across the codebase and regenerate UI modules. Only choose this if you want to drop `qtpy` entirely.

Goals
- Run Monokrom with PySide6 producing the same behavior as current setup.
- Regenerate or ensure `.ui` / compiled UI modules are PySide6-compatible.
- Keep `qtpyvcp` and HAL behavior intact.

Checklist / quick inventory tasks
1. Inventory all `.ui` files and where they're loaded (runtime `uic.loadUi` vs compiled modules).
2. Inventory any direct `PySide2`/`PyQt5` imports — convert or route via `qtpy`.
3. Note any hand-written bindings that rely on old Qt API names (enums moved, `exec_`, QVariant usage, etc.).
4. Collect list of custom widgets used in Designer headers (they must remain importable by PySide6 at runtime).

Concrete commands (env & UI compilation)
- Set runtime backend (for tests):
```
export QT_API=pyside6
```
- Regenerate .ui → python (if you choose to keep compiled UI files):
```
# Ensure the qtpyvcp command is available by activating the project's Python venv
# (qtpyvcp provides the `qcompile` helper). Activate your venv first:
```
source ~/dev/venv/bin/activate
```
Then run `qcompile`:
```
qcompile src/monokrom/plasma/mainwindow.ui -o src/monokrom/plasma/mainwindow_ui.py
qcompile src/monokrom/common/widgets/some_widget.ui -o src/monokrom/common/widgets/some_widget_ui.py
```
- Compile resources (if any .qrc are present):
```
source ~/dev/venv/bin/activate
qcompile resources.qrc -o resources_rc.py
```

Detailed Work Breakdown Structure (WBS)
Phase 0 — Prep
  0.1 Create an isolated Python environment (pyenv/venv) with Python >= 3.8. If you already have the project's venv at `~/dev/venv`, activate it before running `qcompile` or other tooling:
```
source ~/dev/venv/bin/activate
```
  0.2 Install `PySide6`, `qtpy`, and `qtpyvcp` into the venv and test the `probe_basic` example to confirm a working PySide6 environment. Ensure `qtpyvcp` is installed so the `qcompile` helper is available (install via `pip install qtpyvcp` or your project editable install).
  0.3 Add `requirements-dev.txt` entries for `pyside6` and tooling (the Qt6 compiler/helpers are provided via `qtpyvcp` when installed in the venv).

Phase 1 — Inventory & Baseline tests
  1.1 Run static search for `from PySide|from PyQt|qtpy.uic|uic.loadUi|\.ui` and collect file list.
  1.2 Record UI files that are compiled vs loaded at runtime.
  1.3 Run the app under current default backend to capture baseline runtime errors and behavior (smoke run).
  1.4 Create a small automated smoke test that imports `src/monokrom` main entry and instantiates the main window (headless CI may require Xvfb).

Phase 2 — Decide & prepare UI artifacts
  2.1 If `.py` UI files exist but were generated for PyQt5/PySide2, regenerate them with `qcompile` (this helper wraps the appropriate compiler for the chosen Qt backend).
  2.2 Ensure `.ui` files referencing custom widgets list the same Python import path those widgets are available from at runtime (e.g., `qtpyvcp.widgets...`).
  2.3 (Optional) Add a `tools/regen_ui.sh` script to simplify regeneration and include examples.

Phase 3 — Code compatibility edits
  3.1 Global import policy: prefer `from qtpy.QtWidgets import ...` etc. — keep `qtpy` and ensure `PySide6` is available to `qtpy`.
  3.2 Replace legacy API calls:
    - `.exec()` (replace older `.exec_()` usages)
    - `Signal`, `Slot` names should be used via `qtpy` or imported from `qtpy.QtCore`.
    - Enum and flag changes (e.g., `Qt.AlignLeft` still OK; watch for cases where Qt5 used top-level enums).
    - Remove any `QString`/`QVariant` assumptions — Qt6 uses native Python types.
  3.3 Fix `uic.loadUi` usage if it relies on `PyQt5.uic` specifics; prefer `qtpy.uic.loadUi`.
  3.4 Update any `pyqtSignal/pyqtSlot` to `Signal/Slot` via `qtpy.QtCore` or use `from PySide6.QtCore import Signal` if moving to direct PySide6.

Phase 4 — Custom widgets & Designer plugins
  4.1 Ensure custom widgets under `src/monokrom/common/widgets` and `src/monokrom/plasma/widgets` are importable when Python path uses project root.
  4.2 If compiled UI modules import custom widgets by different names, update import paths.
  4.3 Add minimal unit tests that instantiate each custom widget to surface constructor issues.

Phase 5 — Integration & HAL / linuxcnc specifics
  5.1 Verify `qtpyvcp.hal` usage remains compatible (this is pure Python integration with LinuxCNC HAL; PySide6 should not affect it directly).
  5.2 Validate any code that manipulates HAL objects from GUI threads — ensure thread rules still followed.

Phase 6 — Smoke test and iterative fixes
  6.1 Run monokrom with `QT_API=pyside6` and fix runtime exceptions.
  6.2 Focus areas: missing widget imports, wrong enum names, missing plugin registrations, resource loading failures.
  6.3 Keep a running changelog of each fix and the file(s) changed.

Phase 7 — Packaging, CI, docs
  7.1 Update `pyproject.toml` / `requirements.txt` to include `PySide6` as an optional or required dependency as appropriate.
  7.2 Update any packaging steps that compile UI or resources.
  7.3 Add CI job that runs the smoke test under Xvfb.
  7.4 Update `docs/` with commands to rebuild UI resources and how to run with `QT_API=pyside6`.

Files & patterns you will frequently edit
- `src/monokrom/__init__.py` — CLI and start up (it already supports `--qt-api` override).
- `src/monokrom/plasma/mainwindow.py` and its `.ui` files.
- `src/monokrom/common/widgets/*` — custom widget constructors and any `uic.loadUi` usage.
- `src/monokrom/*/*.ui` — review headers referring to qtpyvcp widgets.

Quick migration checklist (developer actions)
1. Create venv (or use existing `~/dev/venv`) and install `PySide6`, `qtpy`, and `qtpyvcp` into it. Activate it with:
```
source ~/dev/venv/bin/activate
```
2. Run `export QT_API=pyside6` and run `python -m src.monokrom` (or proper entry) to identify runtime failures.
3. Regenerate compiled UI files with `qcompile` where necessary while the venv is active.
4. Apply minimal edits (search/replace) for `exec_` and signal names.
5. Run smoke test and iterate until clean startup.

Risk notes
- Because `qtpyvcp` (and the application) uses custom widgets registered with Designer, ensure those imports resolve in the runtime environment; mismatch here is the common cause of runtime failures.
- LinuxCNC/HAL interactions are environment-dependent — you may need to stub or run in a dev mode for CI.
- `probe_basic` shows a successful setup pattern: keep `qtpy` usage and prefer regenerating UIs targeted at PySide6.

Next actions (I can do for you)
- Produce a per-file report listing files needing edits (imports, `.ui` usage, compiled UI modules).
- Create a `tools/regen_ui.sh` script that regenerates the project's UIs with `qcompile` (run while `~/dev/venv` is activated).
- Run an automated search-and-replace for trivial API changes (like `exec_` -> `exec`).

Contact / reference
- Reference project used: `probe_basic` (in your workspace) — it contains PySide6-generated UI and examples of `qtpy` + `PySide6` usage.

End of plan
