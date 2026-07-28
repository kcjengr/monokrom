# Plasma UI Code Review

## Overall Impression

**"A functional monolith with surprisingly clean service layers buried under a 781-line god object."**

The architecture actually isn't terrible — the service classes (`HALBridge`, `CutRecoveryService`, `SheetAlignmentService`, `ConsumableChangeService`) are well-structured, dependency-injected, and testable. That's the good news. The bad news is that `mainwindow.py` is doing the job of three classes, and `quickshapes.py` is a 1,159-line file that reads like a math textbook written by someone who really, really wants you to understand every intermediate calculation.

---

## Bugs & Edge Cases

### 1. `quickshapes.py` — Mutable default argument in 8+ functions

```python
def circle(diameter, kerf, leadin=4, conv=1, lines=[]):
```

This is the classic "I thought `lines=[]` was safe" mistake. In Python, default arguments are evaluated *once* at function definition time. Every call that omits `lines` shares the *same list*. If you call `circle()` twice, the second call appends to the leftover from the first.

`lifting_lug` does it right (`if lines is None: lines = []`). The other 13 shape functions don't.

**Fix:** Change all `lines=[]` defaults to `lines=None` with `if lines is None: lines = []`.

> ✅ **FIXED (2026-07-27)** — All 14 shape functions now use `lines=None` with the proper guard. No remaining `lines=[]` defaults.

### 2. `quickshapes.py` — `theta = cos((r1 - r2) / d)` is mathematically wrong (3 locations)

In `exhaust_flange()`: `build_corner()` nested function (line 501), and duplicated inline in the `nb==2` branch (line 710) and `nb==3` branch (line 760):

```python
theta = cos((r1 - r2) / d)
```

`cos()` returns a value in [-1, 1]. You're treating it as an angle in radians.

**The correct fix is `cos()` → `acos()`.** For external tangent geometry between two circles, the perpendicularity condition (tangent line dot radius = 0) yields `cos(θ) = (r₁ - r₂) / d`, so `θ = acos((r₁ - r₂) / d)`.

> ❌ **The review's suggestion of `asin()` was WRONG.** Testing with `asin()` produced non-tangent lines that cut incorrect geometry. The correct function is `acos()`, with a guard for the geometrically impossible case where `|(r1-r2)/d| >= 1`:
> 
> ```python
> ratio = (rr1 - rr2) / d
> if abs(ratio) >= 1.0:
>     theta = pi / corners
>     theta2 = 0
> else:
>     theta = acos(ratio)
> theta2 = (pi / corners) - theta
> ```

**Why this bug is hidden (and why the code "works"):**

1. **Test parameters are physically unrealistic.** The tests use `id=100, wt=20, pcd=80` — bolt holes at PCD radius 40mm, but the inner hole edge is at 50mm. The bolt holes are *inside* the inner hole. This gives `ratio > 1`, which triggers the `theta < 0` fallback (`theta = pi/3`), producing "close enough" geometry.

2. **Tests only check "output exists", not geometry correctness.** Every assertion is `assert "G1" in gcode` or `assert len(lines_list) > 0` — no coordinate validation.

3. **The fallback masks the bug for extreme cases.** When bolt holes are far from the flange edge, `ratio > 1` and the code falls back to a simple 60° angle.

**Physical impact for realistic parameters** (`id=100, wt=10, pcd=160, bd=10, nb=3`):

| Metric             | Buggy (`cos`)  | Correct (`acos`) | Error     |
| ------------------ | -------------- | ---------------- | --------- |
| θ (theta)          | 46.5°          | 51.3°            | **5.2°**  |
| Arc start position | (-59.3, -14.3) | (-55.1, -23.8)   | **9.5mm** |

**9mm off on a CNC plasma cut is not a rounding error — it's a scrap part.** The sloped transition between the inner hole and bolt holes would be cut at the wrong angle, and the bolt holes wouldn't align.

```python
# Typical case: ratio = 0.625
cos(0.625)   # 0.811 rad  (46.5°)  ← WRONG (treated as angle, not cosine value)
acos(0.625)  # 0.896 rad  (51.3°)  ← CORRECT
asin(0.625)  # 0.675 rad  (38.7°)  ← WRONG (produces non-tangent lines)
```

This is the kind of bug that produces valid G-code that a machine would execute without error — but cuts the wrong geometry. Good luck debugging that at 2 AM when someone orders an exhaust flange.

> ✅ **FIXED (2026-07-28)** — All 3 locations use `acos(ratio)` with `abs(ratio) >= 1.0` guard. `acos` added to math imports. Tangent lines verified correct.

### 3. `mainwindow.py` — Lambda capture bug in signal connections (lines 282–285)

```python
for btn_name in ("btn_feed_hold", "btn_cycle_start", "btn_stop_abort"):
    getattr(self, btn_name).clicked.connect(
        lambda x, b=btn_name: self.on_cut_recovery_button(b)
    )
```

You *did* capture `b=btn_name` correctly here — good. But then on lines 288–295, you do the exact same thing with `a=action`, also correct. However, the pattern is duplicated across two nearly-identical loops. This is a code smell — if one loop gets fixed and the other doesn't, you'll have an asymmetrical bug. Consider refactoring to a single helper method.

### 4. `sheet_alignment.py` — `G10 L2 P0 R0` sent before reading coordinates ❌ FALSE POSITIVE — assessment was incorrect

```python
def set_point_1(self, pos_absolute):
    self.hal.send_mdi('G10 L2 P0 R0')  # reset work coords
    x_current_pos = float(pos_absolute.Absolute(0))  # read AFTER reset
    ...
```

**Assessment: WRONG.** The `G10 L2 P0 R0` command resets work coordinate system offsets to zero — it does not read or depend on machine position in any way. The `pos_absolute` parameter is passed in from the caller (a `pos` object from qtpyvcp's position API) and is not being "read from the machine" inside this function. The reset and the use of `pos_absolute` are independent operations — the order doesn't matter because `G10 L2 P0 R0` does not affect the values returned by `pos_absolute.Absolute()`. The assessment assumed a dependency that doesn't exist.

### 5. `sheet_alignment.py` — Multiple `G10 L2 P0 R0` without `wait_complete()`

```python
self.hal.send_mdi('G10 L2 P0 R0')
self.hal.send_mdi('G10 L2 P0 X0 Y0')
self.hal.wait_complete()
self.hal.wait_complete()  # <-- why two?
```

Three MDI commands, two `wait_complete()` calls. The third command may execute before the first two complete. And why double `wait_complete()`?

**Fix:** One `wait_complete()` after each `send_mdi()`, or batch them with a single wait at the end.

> ✅ **FIXED (2026-07-27)** — The `align()` method now pairs every `send_mdi()` with its own `wait_complete()`, serialising the MDI sequence correctly. Original pattern of "3 sends, 2 waits" is gone.

### 6. `process_filter.py` — `get_current_cut()` returns a list, not a cut

```python
def get_current_cut(self):
    ...
    cutlist = parent._plasma_plugin.tool_id(tool_id)
    if len(cutlist) > 0:
        return cutlist  # returns a LIST
    return None
```

But `update_cut()` iterates over it as if it's a single object:

```python
q = self.get_current_cut()
...
parent._plasma_plugin.updateCut(q, **arglst)  # q is a list, not a cut object
```

Meanwhile `get_filter_query()` does it right — returns `cutlist` (a list), and callers index into it. But `get_current_cut()` should return `cutlist[0]` to be consistent with how `cutchart_pin_update` uses `tool_id()`.

### 7. `plasma_hal_double_spinbox.py` — `resetToOriginal` assigns a Setting object, not a value

```python
def resetToOriginal(self):
    self._setting = self._original_value  # Both are Setting objects
    self.setDisplayValue(self._setting)   # setValue expects a number, not a Setting
```

This method is broken. `self._setting` and `self._original_value` are both `Setting` objects. You'd need `self._setting.getValue()`.

### 8. `mdi_panel.py` — `'null'` as a string sentinel

```python
text = self.main_window.mdiEntry.text() or 'null'
if text != 'null':
    text += char
```

Why is `'null'` a string? Use `None`. Or better yet, just use `QLineEdit.text()` naturally — it returns `""` for empty, which is falsy.

```python
def append_char(self, char):
    text = self.main_window.mdiEntry.text()
    self.main_window.mdiEntry.setText(text + char)
```

---

## Performance

### 9. `quickshapes.py` — Debug logging on *every single G-code line*

Look at the `n_square` function. For a grid of 20x20 holes, that's **1,200+ log statements** — every hole position, every intermediate calculation, every arc center. And this runs every time a shape is generated.

```python
LOG.debug(f"---- x/y={(x,y)}, kh={kh}, hd/2={hd/2}")
LOG.debug(f"---- G1 X{x - (fix(hd/2) - ikh)}")
LOG.debug(f"---- G3 I{fix(hd/2) - ikh}")
LOG.debug(f"---- effective center = {...}")
```

The `exhaust_flange` function has even worse — `build_corner` logs the center of every arc with a heading like `>>> Big Arc <<<` and `>>> Line 1 <<<`. This is not logging, this is writing a diary.

**Fix:** Either remove most debug logging or make it conditional behind a `DEBUG_SHAPE_GEN` flag. The logs are useful during development but will slow down runtime and bloat log files in production.

> ✅ **FIXED (2026-07-28)** — All per-hole and per-step debug logging in `quickshapes.py` removed. The file went from ~1,200+ `LOG.debug` calls (in tight loops) to 10 single-line summary logs — one per shape function. Remaining calls are outside loops and only fire once per shape generation:
>
> | Function | Before | After |
> |----------|--------|-------|
> | `lifting_lug` | 1 | 1 (unchanged) |
> | `pipe_saddle` | 2 | 2 (unchanged) |
> | `build_corner` | ~20 | 1 (header only) |
> | `build_slot` | ~10 | 0 (all commented out) |
> | `exhaust_flange` | ~7 | 0 (all commented out) |
> | `n_square` (20×20) | ~1,200 | 5 (one per row + summary) |
>
> The per-hole debug lines inside `n_square`'s loops (every x/y, every G1, every G3, every arc center) were the primary culprit. These are gone. The remaining logs are lightweight and appropriate for tracing which shapes were generated.

### 10. `shape_generator.py` — Repeated `import` in every method

```python
def _circle(self):
    ...
    from . import quickshapes as qs
    ...

def _rectangle(self):
    ...
    from . import quickshapes as qs
    ...
```

This repeats 14 times. Python caches imports, so it's not *wrong*, but it's noise. Import once at the top of the class or module.

> ✅ **NO TEST IMPACT** — The module already has `from . import quickshapes as qs` at the top (line 2). Every local import shadows it but resolves to the exact same module. Moving to the module-level import is safe — both `test_shape_generator.py` and `test_quickshapes_shapes.py` will continue to pass unchanged. The 14 local `from . import quickshapes as qs` statements inside methods are redundant no-ops.

---

## Security

### 11. `mainwindow.py` — MDI command injection via `frame_work()`

```python
move_cmd = (
    f"F{feed_rate};"
    f"G53 G0 Z{min_max_z[1]};"
    ...
)
self.hal.send_mdi(move_cmd)
```

The `feed_rate` comes from a UI slider, so it's bounded. But `min_max_z[1]` comes from `INFO.getAxisMinMax("Z")` which reads the INI file. If someone edits the INI to include malicious content in a limit field... well, it's formatted into an MDI command. Probably not a concern in practice (INI values are numeric), but worth noting.

### 12. `mainwindow.py` — `seed_database()` file path validation

```python
src = os.path.expanduser(self.lne_seed_source.text())
if not os.path.isfile(src):
    ...
self._plasma_plugin.seed_data_base(src)
```

The file path comes from a UI text field. There's no validation that the file is in an expected directory or that it's a legitimate database seed file. A user could point this at `/etc/shadow` and... well, the plasma VCP probably won't have permission, but it's still a code smell.

---

## Quality & Style

### 13. `mainwindow.py` — 781-line god object

This class:

- Instantiates 7 services
- Reads INI config
- Sets up 50+ UI signal/slot connections
- Implements framing, sheet alignment, consumable change, cut recovery, MDI panel, VTK display management, database seeding
- Has 30+ methods

It's the architectural equivalent of a Tupperware container that holds everything in the kitchen. **Extract the UI setup logic** into a dedicated `MainWindowUI` class, and **extract the business logic** (framing, alignment, etc.) into their own modules. The service classes are already clean — the main window should be a thin coordinator.

### 14. `quickshapes.py` — 1,159 lines, 14 shapes, zero structure

> ❌ **DISPUTED — No refactoring needed.**

The reviewer's suggestion to split shapes into classes or modules is architecturally wrong for this codebase. Here's why:

- **Single consumer:** `quickshapes.py` is imported by exactly one file — `shape_generator.py` — which calls flat functions like `qs.circle(...)`, `qs.rectangle(...)`, etc.
- **Pure functions:** Each shape function takes parameters and returns `(lines, error_msg)`. No shared state, no side effects, no inheritance relationship between shapes.
- **Zero polymorphism:** There's no interface to implement, no subclassing to do, no runtime dispatch that would benefit from classes.

Refactoring into a `ShapeRegistry` with classes would:
1. Add ~15 new class definitions for what are already self-contained functions
2. Require changing every call site in `shape_generator.py`
3. Provide zero benefit — introducing classes where simple functions are the correct abstraction

**The flat function API is the right design.** The only actionable improvement would be adding section header comments before each shape function for readability, which is already partially done.

### 15. Typos everywhere

| File                           | Line       | What               | Should be           | Status |
| ------------------------------ | ---------- | ------------------ | ------------------- | ------ |
| `mainwindow.py`                | 103        | `param_kirfwidth`  | `param_kerfwidth`   | ✅ FIXED |
| `mainwindow.py`                | 624        | `tranformUI_reset` | `transformUI_reset` | ✅ FIXED |
| `quickshapes.py`               | 856, 857   | `Horiztonal`       | `Horizontal`        | ✅ FIXED |
| `quickshapes.py`               | 876, 877   | `Horiztonal`       | `Horizontal`        | ✅ FIXED |
| `plasma_hal_checkbox.py`       | 62, 64, 79, 94 | `Initalizing`  | `Initializing`      | ✅ FIXED |
| `plasma_hal_double_spinbox.py` | 70, 72, 89, 103 | `Initalizing` | `Initializing`      | ✅ FIXED |
| `plasma_hal_spinbox.py`        | 54, 56, 71, 86 | `Initalizing`  | `Initializing`      | ✅ FIXED |

> ❌ **FALSE POSITIVE:** `quickshapes.py:271` `lifrtring lug` does not exist in the codebase. Line 271 is `def mirror_x(x0):`. The function `lifting_lug` at line 205 is correctly spelled.

> ⚠️ **Undercounted:** The review cited 2 `Horiztonal` occurrences (lines 835, 855) but there are 4 (lines 856, 857, 876, 877). It cited 11 `Initalizing` occurrences but there are 12 (each widget file has 3 in `initialize()` + 1 in the final "DONE" log).

> ✅ **FIXED (2026-07-28)** — All real typos corrected across 11 files. `param_kirfwidth` → `param_kerfwidth` required renaming in `mainwindow.py`, `mainwindow.ui`, `mainwindow_ui.py` (regenerated), `shape_generator.py`, and 14 test occurrences. `tranformUI_reset` renamed (method was defined but never called). `Initalizing` → `Initializing` in all 12 log statements across the 3 widget files.

### 16. `plasma_hal_spinbox.py` — Docstring says `s32` for enable pin, it's actually `bit`

> ✅ **FIXED (2026-07-28)** — The docstring at line 24 now correctly reads `bit` for the enable pin, matching the code at line 75 which creates it as `"bit"`.

### 17. `cyclestart_action_button.py` — `flashButton()` is never properly integrated

```python
self.pulse_timer.timeout.connect(self.flashButton)
```

But `flashButton` just toggles `pulse_state` and alternates style classes. Meanwhile, `setIsPaused` calls `self.pulse_timer.start(500)` and `setIsPaused(False)` calls `self.pulse_timer.stop()`. So the timer *does* run, but `flashButton` and `setIsPaused`/`setIsIdle` are fighting over the button text — `flashButton` never sets text, only style class, while `setIsPaused` sets text to "CYCLE PAUSED". The pulse animation will flash the style but the text stays. Confusing UX.

### 18. `process_filter.py` — Duplicate imports scattered across methods

```python
def param_update_from_filters(self, index=0):
    from qtpy.QtCore import Qt        # imported again
    from qtpy.QtWidgets import QListWidgetItem  # imported again

def filter_sub_list_select(self, item):
    from qtpy.QtCore import Qt        # imported again
```

Module-level imports already exist on lines 3-4. These are no-op at runtime (Python caches imports), but they're noise and suggest the author wasn't sure where to put imports.

### 19. `consumable_change.py` — `handle_button` returns a dict that's rarely used

```python
def handle_button(self, action, ...):
    if action in ('cycle_start', 'stop_abort'):
        return {
            'btn_consumable_change': {'enabled': False, 'checked': False},
            ...
        }
```

But in `mainwindow.py`, the return value is discarded in some paths. The pattern of returning mutation instructions from the service and applying them in the view is repeated across 3 services. It's a workable pattern, but consider whether the services should directly manipulate UI state via callbacks or events instead.

### 20. `file_ops.py` — `_parsed` suffix handling is fragile

```python
name_parts = real_file.rsplit(".", 1)
if name_parts[0].endswith("_parsed"):
    ppart = "."
else:
    ppart = "_parsed."
new_name = name_parts[0] + ppart + name_parts[1]
```

This assumes filenames have exactly one dot. A file like `program.ngc_v2.ngc` would produce `program.ngc_parsed_v2.ngc`. Use `pathlib.Path` for robust path manipulation.

---

## What's Actually Good

- **`HALBridge`** — Clean dependency injection with lazy loading. This is the kind of code I wish more people wrote. Importing this module doesn't crash if LinuxCNC isn't running. Respect.
- **Service classes** — `CutRecoveryService`, `SheetAlignmentService`, `ConsumableChangeService` are all well-encapsulated, state-machine-driven, and have clear public APIs.
- **Signal/slot separation** — The main window delegates to services rather than implementing business logic inline. The delegation pattern is clean even if the main window is bloated.
- **`ShapeGeneratorService` routing** — The `generators = {0: self._circle, ...}` dict is a clean dispatch mechanism.

---

## Verdict

### Fix these and I'll sign off

The core architecture is sound, but there are real bugs (mutable defaults, wrong trig function) that could produce incorrect G-code or crash under edge cases. The `quickshapes.py` math bugs are the most dangerous — they'll cut metal wrong and waste material.

**Priority fixes:**

1. `quickshapes.py` mutable default arguments (bug #1)
2. `quickshapes.py` `cos()` → `asin()` (bug #2)
3. `process_filter.py` `get_current_cut()` returning list vs single object (bug #6)
4. `mainwindow.py` split the god object (quality #13)

The rest is cleanup. But in a CNC context, clean code isn't cosmetic — it's the difference between a clean cut and a $400 sheet of steel that's now decorative art.

---

## Issue 21: `filter_distance_system` shows "inch" instead of "mm" despite being set to "mm"

### Symptom

`_setup_ui_defaults()` (mainwindow.py:221) calls `filter_distance_system.setCurrentText("mm")` and debug logs confirm this. Yet the UI displays "inch".

### Root Cause

The initialization sequence in `MainWindow.__init__()` creates a race between setting the value and then immediately destroying it:

1. **`_setup_ui_defaults()`** (line 220-222) — Sets locked fields:
   
   ```python
   self.filter_machine.setCurrentText(self._machine)
   self.filter_distance_system.setCurrentText(self._linear_setting)  # "mm"
   self.filter_pressure_system.setCurrentText(self._pressure_setting)
   ```

2. **`_create_hal_pins()`** (line 367) — Calls `load_plasma_ui_filter_data()`

3. **`load_ui_filter_data()`** (process_filter.py:25-38) — Iterates ALL keys in `filter_fld_map`, calling `ui_fld.clear()` then re-adding items from the database:
   
   ```python
   ui_fld.clear()                          # <-- clears "mm" selection
   for data in getattr(parent, '_' + k):   # <-- repopulates from DB
       ui_fld.addItem(data.name, data.id)  # <-- widget resets to index 0
   ```

After `clear()`, the combo box resets to index 0. When items are re-added from the database, if `"inch"` happens to be the first record in the `linearsystems` table, the widget displays `"inch"` instead of the `"mm"` that was set.

### Dead Code: `locked_fld_map` is never consulted

`locked_fld_map` is defined at mainwindow.py:61-65 but **never referenced anywhere** in the codebase:

```python
locked_fld_map = {
    "machines": "filter_machine",
    "linearsystems": "filter_distance_system",
    "pressuresystems": "filter_pressure_system",
}
```

The three "locked" fields exist in both `locked_fld_map` and `filter_fld_map`, but nothing ever checks `locked_fld_map` to protect them from being reset.

### The Fix

Three changes:

| Change                                         | File                   | Location                          |
| ---------------------------------------------- | ---------------------- | --------------------------------- |
| Accept `locked_fld_map` in service constructor | `process_filter.py:17` | `__init__`                        |
| Restore locked fields after repopulation       | `process_filter.py:38` | End of `load_ui_filter_data` loop |
| Pass `locked_fld_map` when creating service    | `mainwindow.py:127`    | Service instantiation             |

**`process_filter.py:17`** — Accept the locked map:

```python
def __init__(self, parent, locked_fld_map=None):
    self.parent = parent
    self.filter_fld_map = type(parent).filter_fld_map
    self.param_fld_map = type(parent).param_fld_map
    self.locked_fld_map = locked_fld_map or {}
```

**`process_filter.py:38`** — Restore locked fields after repopulation:

```python
# After the for loop that adds items, restore locked filter fields
for db_key, ui_name in self.locked_fld_map.items():
    ui_fld = getattr(parent, ui_name)
    if db_key == "machines":
        ui_fld.setCurrentText(parent._machine)
    elif db_key == "linearsystems":
        ui_fld.setCurrentText(parent._linear_setting)
    elif db_key == "pressuresystems":
        ui_fld.setCurrentText(parent._pressure_setting)
```

**`mainwindow.py:127`** — Pass the map when creating the service:

```python
self.process_filter_service = ProcessFilterService(self, self.locked_fld_map)
```

### Note on `cutchart_pin_update()`

There's a separate path: `cutchart_pin_update()` (mainwindow.py:531-537) which sets ALL filter fields (including locked ones) based on a cut chart record loaded via HAL pin. This is likely intentional — when a cut chart is loaded, its machine/linear system/pressure values should match the chart. This path is **not** affected by the fix above.
