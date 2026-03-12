# PySide6 Conversion — Per-file Report (monokrom, excluding mill)

Generated: 2026-02-26

Scope: files under `src/monokrom` excluding the `mill/` folder. This report lists files that require attention for a PySide6 conversion, grouped by type and with recommended edits.

Summary
- Many modules already import Qt via `qtpy` (good — keep using `qtpy` and provide `PySide6` backend).
- No compiled `*_ui.py` files found under `src/monokrom` (UIs are shipped as `.ui` files or loaded at runtime).
- Key conversion actions: ensure `qcompile` is available in the venv and regenerate compiled UI modules if you want generated Python UI files; verify `qtpy.uic.loadUi` calls and custom widget import paths.

Files needing attention

- `src/monokrom/__init__.py`
  - Uses `qtpyvcp` CLI and supports `--qt-api`.
  - Action: update docs / README to recommend `QT_API=pyside6` and the venv activation command; no code changes required.

- `src/monokrom/plasma/mainwindow.py`
  - Imports Qt via `qtpy` and extensively uses `qtpyvcp` APIs and custom widgets.
  - Action: verify at runtime under `QT_API=pyside6` — watch for enum/name changes, ensure `qtpyvcp` plugin imports resolve, and run the smoke test.

- `src/monokrom/plasma/widgets/` (multiple files)
  - Files: `plasma_hal_spinbox.py`, `plasma_hal_double_spinbox.py`, `plasma_push_button.py`, `plasma_hal_checkbox.py`, `plasma_line_edit.py`, `plasma_add_process.py`, `cyclestart_action_button.py`, `__init__.py`, plus others.
  - Pattern: imports use `qtpy` and `qtpyvcp` widget classes and HAL integrations.
  - Action: generally safe — ensure Signal/Slot declarations use `qtpy.QtCore.Signal/Slot` (they do via `qtpy`), check any legacy `.exec_()` usage and replace with `.exec()`, and add unit tests that instantiate each custom widget.

- `src/monokrom/common/widgets/` (multiple files)
  - Files: `mdi_entry.py`, `transparent_widget.py`, `group_box.py`, `recent_file_list_view.py`, `mk_led.py`, `input_overlay.py`, `file_list_view.py`, `mk_dro/mk_dro.py`, `mk_led_hal.py`, `mk_line_edit.py`, `tab_widget.py`, `mk_push_button.py`, `__init__.py`.
  - Specific notes:
    - `input_overlay.py` and `mk_dro/mk_dro.py` call `uic.loadUi(...)` — ensure `qtpy.uic.loadUi` is used and that widget import paths referenced by the `.ui` files are importable when running under the project root.
    - `mk_dro.py` defines `UI_FILE = os.path.join(os.path.dirname(__file__), "mk_dro.ui")` and calls `uic.loadUi(UI_FILE, self)` — validate paths at runtime.
  - Action: verify `uic.loadUi` behavior under PySide6; if issues occur, regenerate compiled UI modules with `qcompile` and update imports accordingly.

- `.ui` files (inventory)
  - `src/monokrom/plasma/mainwindow.ui`
  - `src/monokrom/plasma/mainwindow-1024-768.ui`
  - `src/monokrom/plasma/mainwindow-less-greedy.ui`
  - `src/monokrom/plasma/widgets/new_process.ui`
  - `src/monokrom/common/widgets/file_chooser.ui`
  - `src/monokrom/common/widgets/recent_file_chooser.ui`
  - `src/monokrom/common/widgets/int_entry.ui`
  - `src/monokrom/common/widgets/mk_dro/mk_dro.ui`

  - Action: these `.ui` files reference custom widgets (headers show `qtpyvcp.*` classes). Before running the UI under PySide6, either:
    - Ensure `qtpy.uic.loadUi` is able to locate the custom widget classes at runtime; OR
    - Regenerate Python UI modules using the `qcompile` command (run in the venv):
      ```
      source ~/dev/venv/bin/activate
      qcompile src/monokrom/plasma/mainwindow.ui -o src/monokrom/plasma/mainwindow_ui.py
      qcompile src/monokrom/common/widgets/mk_dro/mk_dro.ui -o src/monokrom/common/widgets/mk_dro_ui.py
      ```

Other patterns to scan/fix (global)
- Search-replace candidates:
  - `.exec(` -> `.exec(` (replace legacy `.exec_(` occurrences with `.exec(`)
  - `pyqtSignal` / `pyqtSlot` -> `Signal` / `Slot` via `qtpy.QtCore`
  - Any direct `from PySide2` / `from PyQt5` imports (none found in `src/monokrom` except `mill/` area); if found, convert to `qtpy` or to `PySide6` as desired.
- Verify any uses of `QVariant` or `QString` and replace with native Python types.

Suggested next actions (automatable)
1. Run this command from the repo root to activate the venv and run a fast static grep for leftover direct PyQt/PySide imports:
```bash
source ~/dev/venv/bin/activate
grep -R --line-number "from PySide\|from PyQt" src/monokrom | grep -v "/mill/" || true
```
2. Run the application under the venv with `QT_API=pyside6` and capture startup errors:
```bash
source ~/dev/venv/bin/activate
export QT_API=pyside6
python -m src.monokrom plasma
```
3. If `uic.loadUi` fails for specific `.ui` files, regenerate them with `qcompile` while the venv is active.

Report notes
- This report was generated from a static search of `src/monokrom` for Qt-related usage. It is conservative: files that import via `qtpy` are listed as 'ok but verify' because runtime issues mostly arise from Designer custom-widget references in `.ui` files.
