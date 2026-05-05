# MainWindow Improvements

## Structural problems

**Module-level side effects** (`:43-48`) — Code runs at import time with broken indentation. This is fragile; INI file resolution, `linuxcnc.ini()` call, and variable assignments should be deferred to class init or a lazy initializer.

**`__init__` is ~240 lines** — It handles signal wiring, HAL pin creation, UI setup, config loading, and state initialization all in one block. This is the hardest part to read and test.

## Responsibilities that can be extracted

The class does too many distinct things. Each of these could be a separate module or inner class:

1. **Sheet alignment** (`:1073-1221`) — ~150 lines, self-contained state machine with `sheet_align_toggle`, `sheet_align_set_p1/p2`, `sheet_align`, `build_status_text`. Easy to extract as `sheet_alignment.py`.

2. **Cut recovery** (`:514-578`) — ~65 lines of jog+offset logic for post-stop recovery. Could be `cut_recovery.py`.

3. **Consumable change** (`:579-613`) — ~35 lines, currently tangled with cut recovery's sender-check pattern. Could be `consumable_change.py`.

4. **Filter/process data management** (`:679-803`) — `load_plasma_ui_filter_data`, `param_update_from_filters`, `filter_sub_list_select`, `get_filter_query`, `get_current_cut`. ~125 lines of database/filter plumbing. Could be `process_filter.py`.

5. **MDI panel** (`:906-964`) — ~60 lines, self-contained button/entry logic. Could be `mdi_panel.py`.

6. **Quickshapes G-code generation** (`:361-500`) — The massive `match/case` block (~140 lines) dispatching 14 shapes. Could be a dedicated `shape_generator.py` or `quickshapes_ui.py` that maps UI fields to `qs.*` calls.

7. **File operations** (`:853-1005`) — `openLatest`, `save_file`, `reload_file`. ~50 lines, could be `file_ops.py`.

8. **HAL pin management** (`:290-343`) — The entire external-trigger pin setup block (~50 lines) is boilerplate that could be a helper method or factory.

## Specific code issues to fix regardless of structure

- **`:579`** — `def consumable_change(self):` has inconsistent indentation (4 spaces instead of 8), will cause `IndentationError`.
- **`:206-208, :246-253`** — `btn_feed_hold`, `btn_cycle_start`, `btn_stop_abort` are connected to both `cut_recovery` and `consumable_change`. This dual-dispatch via `sender().objectName()` is fragile and hard to follow.
- **`:388-488`** — The `match/case` block reads 10+ UI values per shape. Each case could be its own method (e.g., `_gen_circle()`, `_gen_rectangle()`).
- **`:552-571`** — `cutrec_move` does coordinate math, bounds checking, and HAL writes all in one function.

## Recommended restructuring plan

```
src/monokrom/plasma/
├── mainwindow.py          (~600 lines, thin coordinator)
├── sheet_alignment.py     (~150 lines)
├── cut_recovery.py        (~70 lines)
├── consumable_change.py   (~40 lines)
├── process_filter.py      (~130 lines)
├── mdi_panel.py           (~60 lines)
├── shape_generator.py     (~150 lines — maps UI → quickshapes calls)
└── file_ops.py            (~50 lines)
```

The `MainWindow.__init__` would shrink to wiring these components together, and each extracted module would own its signals, state, and logic. This makes each piece testable in isolation (no Qt required for filter/query logic, for example).

## Before/after complexity comparison

| Area | Current | After extraction |
|------|---------|-----------------|
| Largest single method | `__init__` at ~240 lines | `__init__` at ~80 lines |
| Longest method body | `clicked_qs_refresh` at ~130 lines | Each shape generator at ~10 lines |
| Testable without Qt | ~0 methods | Filter, file ops, recovery math |
| Cohesion | Low — sender dispatch scattered across class | High — each module owns its feature |

The biggest win is extracting the filter/process data block and the quickshapes dispatcher. Those two alone would cut the file by ~45%. Sheet alignment and cut recovery are next because they're self-contained state machines that currently share a confusing sender-check pattern.
