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

---

## Structural problems (unchanged)

**`__init__` is ~280 lines** — Signal wiring, HAL pin creation, UI setup, config loading, and state initialization are all in one block.

**God class — 1224 lines, ~50 methods, 6+ responsibilities** — Every method couples Qt widget access, business logic, and hardware communication.

---

## Responsibilities to extract

Each service takes a `HALBridge` in its constructor and owns its own state. MainWindow wires signals to thin delegate methods that forward to the service.

1. **Sheet alignment** (`:1082-1224`) — ~140 lines, self-contained state machine with `sheet_align_toggle`, `sheet_align_set_p1/p2`, `sheet_align`, `build_status_text`. Depends on `HALBridge.send_mdi()` + `wait_complete()`. Extract to `sheet_alignment.py`.

2. **Cut recovery** (`:516-578`) — ~60 lines of jog+offset logic for post-stop recovery. Depends on `HALBridge.get_value()`, `set_p()`, `set_offsets()`. Extract to `cut_recovery.py`.

3. **Consumable change** (`:581-614`) — ~35 lines, currently tangled with cut recovery's sender-check pattern. Depends on `HALBridge.get_value()`, `set_p()`, `set_offsets()`. Extract to `consumable_change.py`.

4. **Filter/process data management** (`:681-804`) — `load_plasma_ui_filter_data`, `param_update_from_filters`, `filter_sub_list_select`, `get_filter_query`, `get_current_cut`. ~125 lines of database/filter plumbing. No HAL dependency. Extract to `process_filter.py`.

5. **MDI panel** (`:912-970`) — ~60 lines, self-contained button/entry logic. No HAL dependency. Extract to `mdi_panel.py`.

6. **Quickshapes G-code generation** (`:369-501`) — The massive `match/case` block (~140 lines) dispatching 14 shapes. Replace with a lookup table mapping shape IDs to generator functions. Extract to `shape_generator.py`.

7. **File operations** (`:855-1007`) — `openLatest`, `save_file`, `reload_file`. ~50 lines, could be `file_ops.py`. No HAL dependency.

8. ~~**HAL pin management** (`:290-343`)~~ — **DONE.** Replaced by `HALBridge`. The external-trigger pin boilerplate can also be extracted into a helper method once the services are wired up.

---

## Target file layout

```
src/monokrom/plasma/
├── mainwindow.py          (~500 lines, thin coordinator)
├── hal_bridge.py          (7 public methods + lazy defaults — DONE)
├── sheet_alignment.py     (~150 lines)
├── cut_recovery.py        (~70 lines)
├── consumable_change.py   (~40 lines)
├── process_filter.py      (~130 lines)
├── mdi_panel.py           (~60 lines)
├── shape_generator.py     (~150 lines — maps UI → quickshapes calls)
└── file_ops.py            (~50 lines)
```

Each service owns its signals, state, and logic. `MainWindow.__init__` shrinks to creating instances and connecting Qt signals to delegate methods.

---

## Specific code issues to fix regardless of structure

- **`:581`** — `def consumable_change(self):` has inconsistent indentation (4 spaces instead of 8), will cause `IndentationError`.
- **`:207-209, :248-255`** — `btn_feed_hold`, `btn_cycle_start`, `btn_stop_abort` are connected to both `cut_recovery` and `consumable_change`. This dual-dispatch via `sender().objectName()` is fragile. Extracting the two services will eliminate this pattern entirely.
- **`:390-490`** — The `match/case` block reads 10+ UI values per shape. Each case becomes its own method in `shape_generator.py`.
- **`:555-574`** — `cutrec_move` does coordinate math, bounds checking, and HAL writes all in one function. After extracting `CutRecoveryService`, the HAL calls go through `HALBridge` and the math can be unit-tested.

---

## Before/after comparison

| Area | Before refactoring | After HALBridge wiring | Target after full refactor |
|------|-------------------|------------------------|--------------------------|
| Largest single method | `__init__` at ~260 lines | ~280 (import + hal init added) | ~80 lines |
| Longest method body | `clicked_qs_refresh` at ~130 lines | Still ~130 | Each shape generator at ~10 lines |
| Testable without Qt | 0 methods | HALBridge: 14 tests pass | Filter, file ops, recovery math, alignment math |
| Cohesion | Low — sender dispatch scattered across class | HALBridge is cohesive; mainwindow calls `self.hal` | High — each module owns its feature |
| Hardware coupling | 53 direct calls to `cnchal`/`issue_mdi`/`CMD` | **0 direct calls** — all through `HALBridge` | 0 direct calls — all go through services |

---

## Next step

**Extract services one by one.** Wiring is complete — all hardware calls flow through `self.hal`. Now extract the first responsibility into its own service class.

**Recommended order** (easiest to hardest):

1. Consumable change — ~35 lines, 2 public methods, small state surface
2. Cut recovery — ~70 lines, self-contained state machine
3. Sheet alignment — ~150 lines, angle math is testable as pure functions
4. Process filter — ~125 lines, no HAL dependency, pure data plumbing
5. Shape generator — ~140 line match/case → lookup table + per-shape methods
6. MDI panel — ~60 lines, trivial state machine
7. File ops — ~50 lines, straightforward

Each extraction follows the same pattern: create the service class, inject `HALBridge`, wire MainWindow signals to thin delegates, verify existing tests still pass (they should — mainwindow.py behavior is unchanged).
