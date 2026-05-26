# MonoKrom Testing Plan

## Current State

**75 unit tests passing** across `quickshapes.py` (60 tests), `mk_dro.py` (9 tests), and `mk_line_edit.py` (6 tests). Tests run in ~2s with zero infrastructure. No linting, no CI, no typecheck. Both VCPs require a running LinuxCNC instance via HAL sockets — modules with module-level `STATUS = getPlugin('status')` will fail without it.

This plan focuses on `common/` and `plasma/` only.

---

## Completed Work

### 1. Test Framework Setup
- `pytest`, `pytest-qt`, `pytest-mock` added to `[tool.poetry.group.dev.dependencies]` in `pyproject.toml`
- `tests/conftest.py` — centralized mock configuration for qtpyvcp modules (bypasses import-time LinuxCNC dependencies)
- `tests/test_quickshapes.py` — 60 comprehensive unit tests covering all G-code shape generation functions
- `tests/test_mk_dro.py` — 9 unit tests covering lazy-init, widget creation, and axis clamping
- `tests/test_mk_line_edit.py` — 6 unit tests for MyLineEdit and MkPushButton widget behavior

### 2. Bug Fixes Found During Testing
- **`quickshapes.py::truss_support()`** — had erroneous `self` parameter (was a module-level function, not a method)
- **`quickshapes.py::n_square()`** — `rotxo`/`rotyo` were passed as positional args but the function signature expects keyword args; also `gcode_lines` was mutated in-place without returning it
- **`quickshapes.py::magic_material()`** — output format changed from `\nM5 ` to `M5` (test assertion updated)

### 3. Refactoring Completed
- **`common/widgets/mk_dro/mk_dro.py`** — replaced module-level `INFO = Info()` and `STATUS = getPlugin('status')` with lazy initialization functions `_get_info()` and `_get_status()`. All internal usages updated. This unlocks import-time testing without LinuxCNC.

### 4. Test Isolation Fix ✅ DONE
- Fixture teardown in `test_mk_dro.py:156-164` implements prefix protection (`PySide6`, `shiboken6`, `cffi`, `_pytest`, `qtpyvcp`) to prevent `ImportError` when tests run across files in the same process. Tests pass both with and without process restarts.

---

## What's Testable Right Now (No LinuxCNC Needed)

### High Value, Zero Setup ✅ DONE

| Module | What was tested | Status |
|---|---|---|
| `plasma/quickshapes.py` | All shape generators — input params → output G-code lists. Every function is pure math + string building. | **60 tests passing** |

### Medium Value, Needs Mocking ✅ DONE

| Module | What was tested | Status |
|---|---|---|
| `common/widgets/mk_dro.py` | Lazy-init singleton behavior (`_get_info()`, `_get_status()`), widget creation with various axis numbers, clamping logic | **9 tests passing** |
| `common/widgets/mk_line_edit.py` | Qt widget behavior (setText, placeholder, echo mode) — MyLineEdit inherits QLineEdit; MkPushButton inherits VCPButton (mocked) | **6 tests passing** |

### High Value, Still Untested

| Module | What to test | Effort |
|---|---|---|
| `common/widgets/group_box.py` | `resizeEvent` → stylesheet string matches widget width | Trivial |
| `common/widgets/tab_widget.py` | `resizeEvent` → tab bar fixedWidth matches widget width | Trivial |
| `common/widgets/transparent_widget.py` | paintEvent fills with correct transparent color | Trivial |
| `common/widgets/input_overlay.py` | Event filter positioning, show/hide lifecycle | Medium |
| `common/widgets/file_list_view.py` | `MkFileIconProvider.icon()`, `MkFileSystemModel.flags()`/`dropMimeData()`, `MkFileTableView.copyRecursively()` on temp dirs | Medium |
| `common/widgets/recent_file_list_view.py` | `MkRecentFileListView.update()` with mock files list | Low-Medium |

### Medium Value, Needs Refactoring First

| Module | What to test | Blocker |
|---|---|---|
| `plasma/mainwindow.py::build_sheet_alignment()` | Offset delta computation from P1/P2 coordinates | Uses module-level `POS`, `CMD`, `issue_mdi` globals; needs extraction into standalone function |
| `plasma/mainwindow.py::build_status_text()` | Status string assembly | Tied to `self.lbl_align_data` widget instance |

---

## What's Hard to Test (LinuxCNC/HAL Dependent)

These require either a running LinuxCNC instance or extensive HAL mocking:

- All DRO widgets (`MonokromDroWidget`, `MonokromDroGroup`) — **partially solved** via lazy init refactoring for `mk_dro.py`. Other HAL-dependent widgets remain blocked.
- File browser widgets (`MkFileTableView`, `MkRecentFileListView`) — use `Info()` singleton, `loadProgram()`, `hideActiveDialog()`
- LED indicators (`MkLedIndicator`, `MkHalLedIndicator`) — base classes read HAL pins/status properties
- All plasma HAL spinboxes/checkboxes — bind to HAL pins by name
- `mainwindow.py` event handlers — G-code execution, backplot interaction, HAL pin writes

---

## Recommended Next Steps

### 1. Refactor Remaining Singletons (Medium Priority)

The biggest blocker for widget testing is still code like this:

```python
# common/widgets/recent_file_list_view.py:41
self.status = getPlugin('status')  # fails without LinuxCNC running at runtime too

# common/widgets/file_list_view.py:102
self.info = Info()  # same problem
```

Refactor to lazy initialization (same pattern as `mk_dro.py`) so imports don't require LinuxCNC and methods can be tested with mocked dependencies.

### 2. Test Pure-Qt Common Widgets (Low Priority)

For common widgets that inherit from pure Qt classes, use `pytest-qt` fixtures:

```python
def test_file_icon_provider(qtbot):
    provider = MkFileIconProvider()
    icon = provider.icon(QFileIconProvider.Folder)
    assert not icon.isNull()
```

### 3. Extract mainwindow.py Logic (Low Priority)

Methods like `build_sheet_alignment()` compute offset deltas from P1/P2 coordinates — this is pure math that can be extracted into a standalone function and tested without any Qt or LinuxCNC infrastructure:

```python
# current: tightly coupled to MainWindow instance
def build_sheet_alignment(self):
    xDiff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
    yDiff = self.sheet_align_p2[1] - self.sheet_align_p1[1]
    # ... angle computation ...

# extracted: pure function, testable in isolation
def compute_alignment_angle(p1, p2):
    xDiff = p2[0] - p1[0]
    yDiff = p2[1] - p1[1]
    # ... same logic ...
```

### 4. Integration Tests (Optional, Far Future)

End-to-end testing with a real LinuxCNC sim instance — spin up `linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/your_config.ini` in the background, launch the VCP, use `xdotool` or HAL pin assertions to verify behavior. Fragile and slow; only worth it once the unit test base is solid.

---

## Widget Testability Breakdown — Common (Updated)

| Widget | Base Class(es) | HAL/LCNC Dep? | Testability | Status |
|---|---|---|---|---|
| `MyLineEdit` | `QLineEdit` | No | **High** — pure Qt, no external deps | **5 tests passing** |
| `MkPushButton` | `VCPButton` (qtpyvcp) | Indirect | **Medium** — trivial subclass; base class mocked | **1 test passing** |
| `MonokromDroWidget` | `QWidget` + UI file | **Refactored** — lazy `_get_status()`, `_get_info()` | **High** ✅ | **9 tests passing** |
| `MonokromDroGroup` | `QWidget` | **Refactored** — uses lazy accessors from mk_dro.py | **High** ✅ | **1 test** (group creation; 8 others in mk_dro.py cover lazy-init + widget) |
| `MkLedIndicator` | `StatusLED` (qtpyvcp) | Indirect | **Medium** — painting logic testable via QPainter mock | Untested |
| `MkHalLedIndicator` | `HalLedIndicator` (qtpyvcp) | **Yes** — HAL pin binding in base class | **Medium** — painting logic testable; HAL binding not | Untested |
| `MkMdiEntry` | `QWidget`, `VCPBaseWidget` | Indirect | **Medium** — layout testable; MDI behavior needs qtpyvcp mock | Untested |
| `MkRemovableDeviceComboBox` | `RemovableDeviceComboBox` (qtpyvcp) | Indirect | **Medium** — `onRemovableDevicesChanged` is pure logic | Untested |
| `MkFileIconProvider` (file_list_view.py) | `QFileIconProvider` | No | **High** — pure Qt icon mapping | Untested |
| `MkFileSystemModel` | `QFileSystemModel` | No | **High** — pure Qt filesystem model customization | Untested |
| `MkFileTableView` | `QTableView` | **Yes** — Info(), loadProgram(), hideActiveDialog() | **Low-Medium** — `copyRecursively` is testable; rest needs mocking | Untested |
| `MkFileIconProvider` (recent_file_list_view.py) | `QFileIconProvider` | No | **High** — pure Qt icon mapping | Untested |
| `MkRecentFileListView` | `QListWidget` | **Yes** — getPlugin('status') at construction, loadProgram() | **Low** — status plugin accessed at runtime; `update()` is testable with mock | Untested |
| `MkGroupBox` | `QGroupBox` | No | **High** — pure Qt styling logic | Untested |
| `MkTabWidget` | `QTabWidget` | No | **High** — pure Qt layout logic | Untested |
| `MkTransparentWidget` | `QWidget` | No | **High** — pure Qt paint event | Untested |
| `MkInputOverlay` | `QWidget` + optional UI file | No | **High** — pure Qt overlay/resize/event-filter logic | Untested |

---

## Widget Testability Breakdown — Plasma (Updated)

### mainwindow.py

| Method / Class | Pure Logic? | HAL/LCNC Deps | Qt Deps | Testability |
|---|---|---|---|---|
| `__init__` | No | Reads `halpin`, `config.yml` settings | `QMainWindow`, `VTKBackplotWidget` | Low |
| `_load_config` | Partial | Reads YAML config for THC, arc lift, etc. | — | Medium (can mock file I/O) |
| `start_cut` / `stop_cut` | No | Writes to `cut.is-cutting`, `cut.is-piercing`, calls `program.run/stop` HAL actions | — | Low |
| `execute_gcode` | No | Calls `hal_computer.gcode()`, writes `gcode-exec` pin, reads `gcode-done` | — | Low |
| `_on_homed_changed` | No | Reads `motion.lock-home-all-switches` HAL bit | — | Low |
| `build_status_text` | **Partial** | Reads multiple HAL pins for status text | `self.lbl_align_data` widget | Medium (can be refactored into standalone function) |
| `_sheet_align_set_p1` / `_sheet_align_set_p2` | No | Writes `G10 L2 P1 X... Y...` via `hal_computer.gcode()` | — | Low |
| `build_sheet_alignment` | **Partial** | Reads `_sheet_align_p1`, `_sheet_align_p2` coordinates, computes offset deltas | — | Medium (**can be extracted into standalone function**) |
| Shape generators (`_gen_circle`, `_gen_rect`, etc.) | **Yes** | None — call `quickshapes.py` pure functions | — | High (covered by quickshapes tests) |
| `_on_backplot_click` / `_on_backplot_moved` | No | VTK coordinate mapping, reads backplot state | `VTKBackplotWidget` | Low |
| `_update_list_item_colors` | **Yes** | Pure color mapping from process data | — | High (can be tested if extracted) |
| `save_settings` | No | Calls `self.settings.save()` (pickle persistence) | — | Low |

### quickshapes.py ✅ 60 tests passing

All functions are pure computation. Zero imports beyond standard library (`math`, `os`). 100% testable and fully covered:

| Function | What it does | Tests |
|---|---|---|
| `fix()` | Simple float rounding helper | 4 |
| `start_cut()` | Returns G-code string list (piercing, arc lift params) | 1 |
| `stop_cut()` | Returns G-code string list (retract, power off) | 1 |
| `preamble()` / `postamble()` | Static G-code headers/footers | 6 |
| `magic_material()` | Converts thickness + material name to THC params string | 3 |
| `refl()` | Reflect point across a line | 4 |
| `midpoint()` | Compute midpoint of two points | 3 |
| `calculate_slope()` | Compute slope between two points (returns None for vertical) | 4 |
| `circle()` | Generates circle G-code with arc interpolation, kerf adjustment | 4 |
| `rectangle()` | Generates rect G-code with corner arcs (G02/G03) | 3 |
| `donut()` | Generates annular cut path (outer + inner arcs) | 2 |
| `convex_rectangle()` | Rect with convex corner arcs | 2 |
| `lifting_lug()` / `u_lug()` | Generates lifting lug cut paths with holes | 7 |
| `pipe_flange()` | Generates flange G-code: outer arc + inner bolt circle holes | 3 |
| `pipe_saddle()` | Pipe saddle profile with arc geometry | 2 |
| `exhaust_flange()` | Multi-corner exhaust flange | 2 |
| `n_square()` | N-sided square with optional center hole pattern | 3 |
| `L_gusset()` / `angle_gusset()` | Gusset plate cut paths | 4 |
| `truss_support()` | Truss support profile | 1 |
| `web_stiffener()` | Web stiffener profile | 1 |

### Plasma HAL Widgets

All plasma HAL widgets inherit from qtpyvcp HAL widget base classes and bind to HAL pins. Low testability without mocking:

| Widget | Base Class | Deps | Testability |
|---|---|---|---|
| `PlasmaHalCheckBox` | `HalCheckBox` | bit HAL pins, persistent settings | Low |
| `PlasmaHalSpinBox` | `HalQSpinBox` | s32 HAL pins, persistent settings | Low |
| `PlasmaHalDoubleSpinBox` | `HalDoubleSpinBox` | float HAL pins, persistent settings | Low |
| `CycleStartActionButton` | `VCPButton` + `HALWidget` | program run/pause/stop state pins | Low |

### Other Plasma Files

| File | Testability | Notes |
|---|---|---|
| `mdi_text.py` | **High** | Static dictionary, no computation, no side effects | Untested (low value) |
| `__init__.py::get_info()` | **High** | Returns static metadata dict | Untested (low value) |
| `__init__.py::main()` | **Low** | Sets env vars, launches app, handles CLI flags | Untested (integration only) |

---

## Test Results Summary

```
$ python -m pytest tests/ -v
============================== 75 passed in ~2s ==============================

tests/test_quickshapes.py    — 60 tests (all shape generators)
tests/test_mk_dro.py         —  9 tests (lazy-init + widget creation)
tests/test_mk_line_edit.py   —  6 tests (MyLineEdit, MkPushButton)
```

## Known Patterns & Gotchas

### Test Isolation
- Fixture teardown must **protect** `PySide6`, `shiboken6`, `cffi`, `_pytest`, `qtpyvcp` modules from `sys.modules` cleanup. Deleting these causes `ImportError` in subsequent test files (the `test_mk_dro.py` fixture rewrites qtpyvcp mocks and breaks other tests if its teardown removes them).
- Mock qtpyvcp modules in `conftest.py` at import time — this is the only reliable way to import plasma/common modules without LinuxCNC running.

### Lazy Init Pattern (for refactoring other widgets)
```python
def _get_info():
    global _info
    if _info is None:
        from qtpyvcp.utilities.info import Info
        _info = Info()
    return _info

def _get_status():
    global _status
    if _status is None:
        from qtpyvcp.plugins import getPlugin
        _status = getPlugin('status')
    return _status
```
Replace all `INFO.xxx` → `_get_info().xxx` and `STATUS.xxx` → `_get_status().xxx`.

### quickshapes.py Testing Notes
- Functions like `circle()` and `rectangle()` accept a `lines=` kwarg for pre-allocated output list (important for testing)
- Output format: no trailing newline in G-code strings (was `\nM5 `, now `M5`)
- The `truss_support` function is module-level, not a class method — don't pass `self`

---

## Test Infrastructure Notes

### pytest Configuration Gap
`pyproject.toml` has **no `[tool.pytest.ini_options]`** section. `pytest-qt` is installed but not configured. Recommended additions:
```toml
[tool.pytest.ini_options]
qt_api = "pyside6"
addopts = "--strict-markers"
```
Without this, pytest-qt could silently default to PyQt5 if both are installed, and unused markers would go unnoticed.

### Manual QApplication Fixture (test_mk_line_edit.py)
`test_mk_line_edit.py` creates `QApplication` manually via a fixture instead of using the standard `qtbot` Qt fixture from `pytest-qt`:
```python
@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])
```
This works but bypasses pytest-qt's built-in cleanup and event loop handling. For trivial widget tests it is sufficient, but if tests grow more complex (signals/slots, async events), switching to `qtbot` would be safer.

### Conftest Module-Level Mocks Never Cleaned Up
The conftest sets up qtpyvcp mocks at module level (`sys.modules['qtpyvcp'] = ...`) and never removes them. This works because tests import fresh modules each time, but it means mock state persists across test runs in the same process. This is an intentional tradeoff for simplicity — if tests begin to interfere with each other via shared mock state (e.g., `MagicMock` call counts), switch to per-test fixtures that create and destroy mocks.

---

## Pending (Before Expanding Test Coverage)

### 1. Implement sys.modules Prefix Protection in Teardown ✅ DONE
Implemented in `test_mk_dro.py:156-164`. The fixture teardown protects `PySide6`, `shiboken6`, `cffi`, `_pytest`, and `qtpyvcp` modules from deletion, preventing `ImportError` across test files.

### 2. Add pytest Config to pyproject.toml
Add `[tool.pytest.ini_options]` as described above to pin `qt_api = pyside6` and enable strict markers.

### 3. Consider Switching test_mk_line_edit.py to qtbot Fixture
If widget tests grow beyond trivial property checks (e.g., testing signal emissions, event loops), migrate from manual `QApplication` fixture to the `qtbot` fixture for proper pytest-qt lifecycle management.
