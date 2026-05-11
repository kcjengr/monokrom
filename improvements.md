# MainWindow Refactoring — Status & Plan

## Completed

### HALBridge (`src/monokrom/plasma/hal_bridge.py`)
A thin, injectable wrapper around all LinuxCNC/HAL/MDI communication.

- **Public API**: `get_value()`, `set_p()`, `send_mdi()`, `wait_complete()`, `set_offset()`, `get_eoffset()`, `set_offsets()`
- **Lazy defaults**: `_DefaultCnchal` (linuxcnc hal), `_DefaultMdi`, `_DefaultCmd` defer imports until first use, so importing this module never requires a running Qt/LinuxCNC instance.
- **Constructor injection**: Pass mocks for testing (`HALBridge(cnchal=mock, issue_mdi_fn=fn, cmd=mock_cmd)`).
- **14 passing tests** in `tests/plasma/test_hal_bridge.py` using `MockCnchal` and `MockCmd`.

### HALBridge wired into MainWindow (DONE)
All 53 direct hardware calls in `mainwindow.py` have been replaced with `self.hal` method calls.

| Old pattern | New pattern |
|-------------|-------------|
| `cnchal.set_p(pin, val)` | `self.hal.set_p(pin, val)` |
| `cnchal.get_value(pin)` | `self.hal.get_value(pin)` |
| `issue_mdi(gcode)` | `self.hal.send_mdi(gcode)` |
| `CMD.wait_complete()` | `self.hal.wait_complete()` |

`mainwindow.py` now has zero direct calls to `cnchal`, `issue_mdi`, or `CMD`. All hardware communication flows through the injectable `HALBridge` instance created in `__init__` via `self.hal = HALBridge()`.

### Consumable Change Service (`src/monokrom/plasma/consumable_change.py`)
Extracted from mainwindow (~35 lines → 77 line service with tests).

- **Public API**: `handle_button(action)`, `toggle_on(x, y, pos)`, `toggle_off()` — returns UI state change dicts instead of directly manipulating widgets.
- **Constructor injection**: Takes `HALBridge` in constructor.
- **7 passing tests** in `tests/plasma/test_consumable_change.py`.
- MainWindow delegates (`on_consumable_button`, `on_consumable_toggle`) forward to the service.
- Eliminated the fragile `sender().objectName()` dual-dispatch pattern — buttons now connect to typed delegate methods.

### Cut Recovery Service (`src/monokrom/plasma/cut_recovery.py`)
Extracted from mainwindow (~65 lines → 167 line service with tests).

- **Public API**: `handle_button()`, `set_direction()`, `move()`, `cancel_pressed()`, `get_cut_recovery_status()` — owns state machine for jog+offset recovery mode.
- **Constructor injection**: Takes `HALBridge` in constructor.
- **26 passing tests** in `tests/plasma/test_cut_recovery.py`.
- MainWindow delegates (`on_cut_recovery_button`, `on_cut_recovery_direction`, `on_cut_recovery_move`, `on_cut_recovery_cancel`) forward to the service.
- Coordinate math (bounds checking, offset calculations) is now unit-testable as pure logic within the service.

### Sheet Alignment Service (`src/monokrom/plasma/sheet_alignment.py`)
Extracted from mainwindow (~140 lines → 205 line service with tests).

- **Public API**: `handle_toggle()`, `set_point_1()`, `set_point_2()`, `align()`, `get_status_text()` — owns state machine for two-point coordinate rotation.
- **Constructor injection**: Takes `HALBridge` in constructor.
- **33 passing tests** in `tests/plasma/test_sheet_alignment.py`.
- MainWindow delegates (`on_sheet_align_laser`, `on_sheet_align_pt1`, `on_sheet_align_pt2`, `on_sheet_align_doalign`) forward to the service.
- Angle calculation (`_calculate_angle`) is now unit-testable as a static pure function — quadrant-aware atan logic with no Qt or HAL coupling.

### MDI Panel Service (`src/monokrom/plasma/mdi_panel.py`)
Extracted from mainwindow (~59 lines → 85 line service with tests).

- **Public API**: `append_char(char)`, `lookup_params(gcode_text)`, `clear_params()`, `backspace()`, `add_space()` — manages MDI text entry and G-code parameter lookups.
- **Constructor injection**: Takes main window reference for widget access.
- **16 passing tests** in `tests/plasma/test_mdi_panel.py`.
- MainWindow delegates (`on_btngrpMdi_buttonClicked`, `btnParams_clicked`, `mdiBackSpace_clicked`, `mdiSpace_clicked`) forward to the service.
- Eliminated inline text manipulation and param button updates — all logic now in a testable service class.

---

## Structural problems (unchanged)

**`__init__` is ~240 lines** — Signal wiring, HAL pin creation, UI setup, config loading, and state initialization are all in one block. External-trigger pin boilerplate (lines 324-346) has not yet been extracted into a helper method.

**God class — 1054 lines, ~50 methods, 6+ responsibilities** — Every method couples Qt widget access, business logic, and hardware communication.

---

## Responsibilities to extract

Each service takes a `HALBridge` in its constructor and owns its own state. MainWindow wires signals to thin delegate methods that forward to the service.

1. ~~**Sheet alignment** (`:1077-1219`)~~ — **DONE.** Extracted to `sheet_alignment.py` with 33 tests.

2. ~~**Cut recovery** (`:518-582`)~~ — **DONE.** Extracted to `cut_recovery.py` with 26 tests.

3. ~~**Consumable change** (`:583-610`)~~ — **DONE.** Extracted to `consumable_change.py` with 7 tests. Sender dispatch pattern eliminated.

4. ~~**MDI panel** (`:863-921`)~~ — **DONE.** Extracted to `mdi_panel.py` with 16 tests. Uses `mdiText.gcode_words()` from `mdi_text.py` (987 lines). MainWindow delegates forward to the service.

5. **File operations** (`:810-827`, `:931-962`) — `openLatest`, `save_file`, `reload_file`. ~50 lines, could be `file_ops.py`. No HAL dependency.

6. **Quickshapes G-code generation** (`:371-504`) — The massive `match/case` block (~134 lines) dispatching 14 shapes. Replace with a lookup table mapping shape IDs to generator functions. Extract to `shape_generator.py`.

7. **Filter/process data management** (`:636-809`) — `load_plasma_ui_filter_data`, `param_update_from_filters`, `filter_sub_list_select`, `get_filter_query`, `get_current_cut`, `add_new_cut_process`, `update_cut`. ~175 lines of database/filter plumbing. Depends on `_plasma_plugin` for DB access (not HAL). Extract to `process_filter.py`.

8. ~~**HAL pin management** (`:290-343`)~~ — **DONE.** Replaced by `HALBridge`. External-trigger pin boilerplate (lines 324-346) still in `__init__` — extract into a helper method once remaining services are wired up.

---

## Target file layout

```
src/monokrom/plasma/
├── mainwindow.py          (~1054 lines, thin coordinator in progress)
├── hal_bridge.py          (7 public methods + lazy defaults — DONE)
├── consumable_change.py   (77 lines — DONE, 7 tests)
├── cut_recovery.py        (167 lines — DONE, 26 tests)
├── sheet_alignment.py     (205 lines — DONE, 33 tests)
├── mdi_panel.py           (85 lines — DONE, 16 tests)
├── file_ops.py            (~50 lines)
├── shape_generator.py     (~134 lines — maps UI → quickshapes calls)
└── process_filter.py      (~175 lines)
```

Each service owns its signals, state, and logic. `MainWindow.__init__` shrinks to creating instances and connecting Qt signals to delegate methods.

---

## Specific code issues to fix regardless of structure

- ~~**`:581`** — `def consumable_change(self):` has inconsistent indentation (4 spaces instead of 8), will cause `IndentationError`.~~ **DONE.** Extracted to `consumable_change.py` with correct formatting.
- **`:250-257`** — `btn_feed_hold`, `btn_cycle_start`, `btn_stop_abort` are connected to both `cut_recovery` and `consumable_change` services. Both now use typed delegates (`on_cut_recovery_button`, `on_consumable_button`) — wiring is correct but this dual-connect pattern should be noted.
- **`:371-504`** — The `match/case` block in `clicked_qs_refresh` reads 6-12 UI values per shape (14 shapes total). Each case becomes its own method in `shape_generator.py`.
- ~~**`:555-574`** — `cutrec_move` does coordinate math, bounds checking, and HAL writes all in one function.~~ **DONE.** Extracted to `CutRecoveryService`; HAL calls go through `HALBridge`, math is unit-testable.
- ~~**`:1038-1180`** — `sheet_align_toggle` uses `sender().objectName()` dispatch pattern.~~ **DONE.** Extracted to `SheetAlignmentService` with typed delegates (`on_sheet_align_laser`, `on_sheet_align_pt1`, `on_sheet_align_pt2`, `on_sheet_align_doalign`). Angle calculation is now a static pure function in the service.

---

## Before/after comparison

| Area | Before refactoring | After HALBridge wiring | After consumable service | After cut recovery | After sheet alignment | After MDI panel (current) | Target after full refactor |
|------|-------------------|------------------------|--------------------------|---------------------|-----------------------|---------------------------|---------------------------|
| mainwindow.py | 1219 lines | ~1220 | ~1220 | ~1220 | 1094 lines | 1054 lines | ~600 lines |
| Largest single method | `__init__` at ~260 lines | ~280 (import + hal init added) | ~280 (service init added) | ~275 (cut_recovery_service added) | ~240 (external-trigger boilerplate still in __init__) | ~240 (external-trigger boilerplate still in __init__) | ~80 lines |
| Longest method body | `clicked_qs_refresh` at ~130 lines | Still ~130 | Still ~130 | Still ~130 | Still ~134 | Still ~134 | Each shape generator at ~10 lines |
| Testable without Qt | 0 methods | HALBridge: 14 tests pass | HALBridge: 14 + Consumable: 7 = 21 | HALBridge: 14 + Consumable: 7 + CutRecovery: 26 + SheetAlign: 33 = 80 | 162 tests (HALBridge 14 + Consumable 7 + CutRecovery 26 + SheetAlign 33 + Quickshapes 82) | 178 tests (+ MDI panel 16) | Filter, file ops, shape gen |
| Cohesion | Low — sender dispatch scattered across class | HALBridge is cohesive; mainwindow calls `self.hal` | Consumable service owns its logic with typed delegates | Cut recovery owns its state machine with typed delegates | Sheet alignment owns coordinate rotation with typed delegates | MDI panel owns text entry + param lookup logic | High — each module owns its feature |
| Hardware coupling | 53 direct calls to `cnchal`/`issue_mdi`/`CMD` | **0 direct calls** — all through `HALBridge` | **0 direct calls** — all through `HALBridge` → services | **0 direct calls** — all through `HALBridge` → services | **0 direct calls** — all through `HALBridge` → services | **0 direct calls** — all through `HALBridge` → services | 0 direct calls — all go through services |

---

## Next step

**Extract services one by one.** Wiring, consumable change, cut recovery, sheet alignment, and MDI panel are complete — all hardware calls flow through `self.hal`. Now extract the next responsibility into its own service class.

**Recommended order** (easiest to hardest):

1. ~~Consumable change~~ — **DONE.** 77 lines, 3 public methods, 7 tests.
2. ~~Cut recovery~~ — **DONE.** 167 lines, state machine with jog+offset logic and coordinate math, 26 tests.
3. ~~Sheet alignment~~ — **DONE.** 205 lines, state machine with quadrant-aware angle math, 33 tests.
4. ~~MDI panel~~ — **DONE.** 85 lines, self-contained button/entry logic, 16 tests.
5. **File ops** — ~50 lines, straightforward `openLatest`/`save_file`/`reload_file`. No HAL dependency.
6. **Shape generator** — ~134 line match/case → lookup table + per-shape methods. Each case reads 6-12 UI values.
7. **Process filter** — ~175 lines, depends on `_plasma_plugin` for DB access (not HAL). Biggest remaining block with most state to track.

Each extraction follows the same pattern: create the service class, inject `HALBridge`, wire MainWindow signals to thin delegates, verify existing tests still pass (they should — mainwindow.py behavior is unchanged).
