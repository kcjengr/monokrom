# Documentation Review Results

**Date:** 2026-09-01
**Scope:** All `.md` files in `docs/user-guide/`, `docs/reference/`, `docs/integrator-guide/`
**Method:** Systematic cross-reference against `src/monokrom/plasma/` codebase and `linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini`

---

## Reference: Screenshot Backing

| Doc File             | Screenshot Exists             | Screenshot Matches UI?                      | Likely Correct?                  | Action to Take                                                                                                              | User Response |
| -------------------- | ----------------------------- | ------------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `main-tab.md`        | Yes (`main-tab.png`)          | Yes — rewritten to match                    | **Yes**                          | No action needed                                                                                                            | Done          |
| `conversational.md`  | Yes (`conversational.png`)    | Partially — omits kerf/smart-hole           | Mostly                           | Fix shape params (shapes 3, 4, 5, 6, 8, 9, 11)                                                                              |               |
| `parameters.md`      | Yes (`parameters.png`)        | No — describes old layout                   | **No**                           | Complete rewrite of layout, filters, parameters; add hole processing & THC panel docs                                       | Fixed. Done.  |
| `settings.md`        | No (`settings.png` Missing)   | N/A                                         | **No**                           | Rewrite to match 2 sub-tabs; update all defaults; remove Height Override; add missing settings                              | Fixed. Done.  |
| `recovery.md`        | Yes (`recovery.png`)          | Partially — describes tab not control group | Partially                        | Fix direction indicators, speed slider, cancel button; rewrite consumable workflow/state machine; fix run from line context | Fixed. Done.  |
| `mdi.md`             | Yes (`mdi.png`)               | No — omits most of the screen               | **No**                           | Fix location; add missing sections (keypad, queue, toolbar, file controls)                                                  | Fixed. Done.  |
| `statistics.md`      | No (`statistics.png` Missing) | N/A                                         | Unknown                          | Verify against codebase; clarify tab location                                                                               |               |
| `arc-start.md`       | No                            | N/A                                         | Partially (values now CSV-based) | Update Arc OK High/Low, Arc Retry Delay defaults                                                                            | Done.         |
| `probe.md`           | No                            | N/A                                         | Partially                        | Update Probe Speed, Probe Height defaults; add missing defaults                                                             |               |
| `thc.md`             | No                            | N/A                                         | Partially                        | Update all defaults; remove Height Override; fix Corner Lock & THC indicators                                               |               |
| `sheet-alignment.md` | No                            | N/A                                         | Unknown                          | Verify against codebase                                                                                                     |               |

---

## 1. `user-guide/settings.md` — MAJOR ISSUES - SOLVED

The documentation covers settings from both sub-pages (THC/ARC/Probe AND Machine) as if they were on a single Settings tab. The screenshot `settings.png` does not exist.

| Issue                       | Docs Say                            | Codebase (config.yml / mainwindow.ui)                                                                                                                                                                                            | Severity           | Action to Take                                                                                                                                                                                                                                                           | User Response |
| --------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| **Tab structure**           | Single "Settings tab" with sections | Two sub-tabs: "THC / ARC / PROBE && MARKING" and "MACHINE"                                                                                                                                                                       | Major              | Rewritten — two sub-tabs: THC/ARC/PROBE && MACHINE                                                                                                                                                                                                                       | Done          |
| **THC Threshold default**   | 5.0 V                               | `thc_threshold` default = **1.0**                                                                                                                                                                                                | **Wrong**          | Done — updated to 1.0                                                                                                                                                                                                                                                    | Done          |
| **THC PID P default**       | 1.0                                 | `thc_pid_p_gain` default = **10.0**                                                                                                                                                                                              | **Wrong**          | Done — updated to 10.0                                                                                                                                                                                                                                                   | Done          |
| **THC PID I default**       | 0.1                                 | `thc_pid_i_gain` default = **0.0**                                                                                                                                                                                               | **Wrong**          | Done — updated to 0.0                                                                                                                                                                                                                                                    | Done          |
| **THC PID D default**       | 0.05                                | `thc_pid_d_gain` default = **0.0**                                                                                                                                                                                               | **Wrong**          | Done — updated to 0.0                                                                                                                                                                                                                                                    | Done          |
| **Safe Height default**     | 2.0 mm                              | `thc_safe_height` default = **25.0**                                                                                                                                                                                             | **Wrong**          | Done — updated to 40.0 (pickle)                                                                                                                                                                                                                                          | Done          |
| **Height Override**         | Range 0.0-2.0, default 1.0          | **Does not exist** in config.yml. The codebase has `height_per_volt` (default 0.100) but no "height override" multiplier                                                                                                         | **Does not exist** | Done — removed Height Override section                                                                                                                                                                                                                                   | Done          |
| **VAD Threshold default**   | 20.0 V                              | `thc_vad_threshold` default = **60.0**                                                                                                                                                                                           | **Wrong**          | Done — updated to 60.0                                                                                                                                                                                                                                                   | Done          |
| **VAD Override**            | Default 0.5                         | `thc_void_override` default = **100**                                                                                                                                                                                            | **Wrong**          | Done — updated to 99 (pickle)                                                                                                                                                                                                                                            | Done          |
| **Arc Retry Delay default** | 1.0 second                          | `arc_retry_delay` default = **60.0**                                                                                                                                                                                             | **Wrong**          | Done — updated to 5.0 (pickle)                                                                                                                                                                                                                                           | Done          |
| **Arc OK High default**     | 40.0 V                              | `arc_ok_high_volts` default = **250.0**                                                                                                                                                                                          | **Wrong**          | Done — updated to 250.0                                                                                                                                                                                                                                                  | Done          |
| **Arc OK Low default**      | 20.0 V                              | `arc_ok_low_volts` default = **60.0**                                                                                                                                                                                            | **Wrong**          | Done — updated to 60.0                                                                                                                                                                                                                                                   | Done          |
| **Probe Speed default**     | 25 mm/min                           | `probe_speed` default = **200**                                                                                                                                                                                                  | **Wrong**          | Done — updated to 300 (pickle)                                                                                                                                                                                                                                           | Done          |
| **Probe Setup Speed**       | No default given                    | `probe_setup_speed` default = **3000**                                                                                                                                                                                           | Missing            | Done — added default 3000                                                                                                                                                                                                                                                | Done          |
| **Puddle Jump Height**      | No default given                    | `puddle_jump_height` default = **0.0**                                                                                                                                                                                           | Missing            | Done — added default 0.0                                                                                                                                                                                                                                                 | Done          |
| **Puddle Jump Delay**       | No default given                    | `puddle_jump_delay` default = **0.0**                                                                                                                                                                                            | Missing            | Done — added default 0.0                                                                                                                                                                                                                                                 | Done          |
| **Torch Pulse default**     | No default given                    | `plasma_torch_pulse_sec` default = **0.3**                                                                                                                                                                                       | Missing            | Done — added default 1.0 (pickle)                                                                                                                                                                                                                                        | Done          |
| **Missing settings**        | —                                   | Scribe Arm/On Delay, Spot Threshold/Delay, Arc Voltage Scale/Offset, Height Per Volt, Arc Height Per Volt, DRO Format settings, Display Units, Virtual Keyboard, DB Seeding, Job Favorites, Consumable XY Feedrate, Framing Feed | Major omissions    | Done — added Scribe, Spot, Arc Voltage, DRO, Display Units, Virtual Keyboard, DB Seeding, Job Favorites, Consumable XY Feed, Framing Feed (Scribe, Spot, Arc Voltage, DRO, Display Units, Virtual Keyboard, DB Seeding, Job Favorites, Consumable XY Feed, Framing Feed) | Done          |
| **"View Material" setting** | Referenced in main-tab.md           | Setting exists (`view_material` is not in config.yml — likely `dro.display-units` instead)                                                                                                                                       | Unclear            | Clarified                                                                                                                                                                                                                                                                | Done          |
| **Exit Warning**            | Referenced in main-tab.md           | Setting exists (`run_delete_confirm` is for delete confirm, not exit warning)                                                                                                                                                    | Unclear            | Clarified                                                                                                                                                                                                                                                                | Done          |
| **Scribe/Spot sections**    | Not documented at all               | Real settings: `scribe_arm_delay`, `scribe_on_delay`, `spot_threshold`, `spot_delay`                                                                                                                                             | Missing            | Done — added Scribe and Spot sections                                                                                                                                                                                                                                    | Done          |

---

## 2. `user-guide/parameters.md` — MAJOR ISSUES

The screenshot `parameters.png` exists but the documentation describes a layout that doesn't match the actual UI.

| Issue                            | Docs Say                                                    | Codebase (mainwindow.py:70-111)                                                                                                                                                                                                                 | Severity           | Action to Take                                                                | User Response |
| -------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ----------------------------------------------------------------------------- | ------------- |
| **Tab name/location**            | "Parameters tab (on the right column)"                      | It's "CUT && MATERIAL" tab in bottom nav; FILTERS are in LEFT column                                                                                                                                                                            | Major              | Rename to "CUT && MATERIAL" tab; move filters description to left column      | Fixed. Done.  |
| **Filter fields**                | 5 fields: Gas, Machine, Material, Thickness, Consumable     | **8 fields**: Gas, Machine, Material, Thickness, Consumable, **Operation, Quality**, plus **Distance System, Pressure System** (locked to INI)                                                                                                  | **Wrong**          | Update to 8 fields (add Operation, Quality, Distance System, Pressure System) | Fixed. Done.  |
| **Parameter display**            | 7 parameters listed                                         | **15 fields**: Process Name, Process/Tool ID, Pierce Height, Pierce Delay, Cut Height, Cut Feed Rate, Setup Feed Rate, Cut Volts, Cut Amps, Kerf Width, P-Jump Height, P-Jump Delay, Pause at End, Gas Pressure                                 | **Wrong**          | Update to 15 fields                                                           | Fixed. Done.  |
| **"SUB-LIST" reference**         | "SUB-LIST below the filters shows all matching cut entries" | No "SUB-LIST" widget — the matching cuts are shown in a list widget (`grp_filter_sub_list`)                                                                                                                                                     | Minor naming       | Rename to "filter sub-list" or "matching cuts list"                           | Fixed. Done.  |
| **"PARAMS tab"**                 | "PARAMS tab displays the cut parameters"                    | Parameters are in a "PROCESS PARAMETERS" group box, not a tab                                                                                                                                                                                   | Minor naming       | Rename to "PROCESS PARAMETERS" group box                                      | Fixed. Done.  |
| **"ADD NEW CUT" / "UPDATE CUT"** | Button names given                                          | Buttons are "SAVE", "RELOAD", "DELETE", "NEW" (in RUN SETTINGS group)                                                                                                                                                                           | **Wrong**          | Update button names to SAVE, RELOAD, DELETE, NEW                              | Fixed. Done.  |
| **Missing: Hole Processing**     | Not documented at all                                       | Large "HOLES" section with Enable, Small Hole Marking, Straight Leadins, Kerf Adjusted, Use Hidef, Hole Size Ratio, Max Hole Size, Leadin Arc Radius, Small Hole Threshold, Hole Kerf Width, % of Feed (Lead-in, Arc 1, Arc 2, Arc 3, Overburn) | Major omission     | Add documentation for HOLES section                                           | Fixed. Done.  |
| **Missing: THC/Torch/Ohmic**     | Not documented                                              | "THC, TORCH && OHMIC" group with 6 checkboxes (THC Enabled, THC Auto Volts, THC Anti-Dive, Void Anti Dive, Mesh Sense, Ohmic Sense)                                                                                                             | Major omission     | Add documentation for THC/TORCH/OHMIC group                                   | Fixed. Done.  |
| **Material Settings section**    | Describes a "material settings section"                     | No such section exists — materials are managed through the process database filters                                                                                                                                                             | **Does not exist** | Remove this section                                                           | Fixed. Done.  |
| **Locked Filters**               | Described correctly                                         | Exists but on Parameters tab, not Settings tab                                                                                                                                                                                                  | Minor              | Move to Parameters tab context                                                | Fixed. Done.  |

---

## 3. `user-guide/conversational.md` — MINOR ISSUES

Screenshot exists and matches well. Shape names and structure are correct.

| Issue                          | Docs Say                                                          | Codebase                                                                                                                     | Severity                                                                                  | Action to Take                                                   | User Response |
| ------------------------------ | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------- |
| **Shape 2 (Donut)**            | "Annulus with inner and outer cuts"                               | `donut(od, id, ...)` — correct                                                                                               | OK                                                                                        | No action needed                                                 |               |
| **Shape 3 (Convex Rectangle)** | "Rectangle with one rounded corner"                               | `convex_rectangle(width, height, ...)` — no corner radius param in docs                                                      | **Wrong** — no corner radius parameter; it's just a convex rectangle                      | Remove corner radius mention; describe as plain convex rectangle |               |
| **Shape 4 (Lifting Lug)**      | "Width, Height, Hole Position, Lug Thickness"                     | 8 params: w1, d1, h1, h2, d2, rb, separation, cutting_pair — docs are incomplete                                             | **Wrong** — missing h2 (lug flat height), d2 (inner hole), rb (bottom radius), separation | Add missing params: h2, d2, rb, separation                       |               |
| **Shape 5 (U-Lug)**            | "Width, Height, Leg Width, Leg Length"                            | 3 params: w1, w2, h — docs are **wrong** — no "Leg Length" param, only w1, w2, h                                             | **Wrong**                                                                                 | Fix params to w1, w2, h (remove Leg Length)                      |               |
| **Shape 6 (Pipe Flange)**      | "Outer Diameter, Bolt Circle Diameter, Hole Count, Hole Diameter" | 6 params: od, pcd, holes, hd, hole_type, id — docs missing hole_type and center ID                                           | **Wrong**                                                                                 | Add hole_type and center ID params                               |               |
| **Shape 8 (Exhaust Flange)**   | "Width, Height, Slot Count, Slot Width"                           | 6 params: id, wt, pcd, bd, sw, nb — docs are **wrong** — uses ID/WT not Width/Height, and has PCD and BD not just slot count | **Wrong**                                                                                 | Rewrite params: id, wt, pcd, bd, sw, nb                          |               |
| **Shape 9 (N-Square Grid)**    | "Grid Spacing, Hole Count X, Hole Count Y, Hole Diameter"         | 17 params including fillet radius, central hole options — docs severely incomplete                                           | **Wrong**                                                                                 | Expand to all 17 params                                          |               |
| **Shape 11 (Angle Gusset)**    | "Width, Height, Leg Width, Thickness"                             | 8 params including angle, cutting pair, x/y offset — docs incomplete                                                         | **Wrong**                                                                                 | Add missing params: angle, cutting pair, x/y offset              |               |
| **Shape 13 (Web Stiffener)**   | "Width, Height, Web Height"                                       | 3 params: w, h, c — docs correct but "Web Height" should be "Cutoff"                                                         | Minor                                                                                     | Rename "Web Height" to "Cutoff"                                  |               |
| **"REFRESH" button**           | "Click REFRESH to generate the G-code"                            | Button is "Refresh" (not all-caps) in UI                                                                                     | Minor                                                                                     | Change to "Refresh"                                              |               |
| **Missing: Internal Kerf**     | Not mentioned                                                     | `quickshape_internal_kerf` setting exists                                                                                    | Minor                                                                                     | Add mention of quickshape_internal_kerf setting                  |               |

---

## 4. `user-guide/recovery.md` — MODERATE ISSUES

Screenshot exists but describes Cut Recovery as a control group within the JOG tab, not as a "Recovery tab."

| Issue                               | Docs Say                                                                   | Codebase (cut_recovery.py + mainwindow.ui)                                                                                                     | Severity           | Action to Take                                                 | User Response |
| ----------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | -------------------------------------------------------------- | ------------- |
| **Recovery location**               | "Recovery tab appears at the bottom of the interface"                      | It's a `widget_recovery` embedded in the bottom tab widget — technically a tab, but it's **within** the CONTROL & RUN tab, not a top-level tab | Minor              | Clarify it's within CONTROL & RUN tab                          | Done          |
| **Direction indicators**            | "Visual feedback for current jog direction"                                | No direction indicators exist — only the 8 arrow buttons around a "kerf" label                                                                 | **Does not exist** | Remove (doesn't exist)                                         | Done          |
| **Speed slider labels**             | "Left (slow) ~10%, Center ~50%, Right (fast) ~100%"                        | Slider is vertical (0-100), no labels shown in UI                                                                                              | **Invented**       | Remove label descriptions                                      | Done          |
| **Canceling recovery**              | "Press ABORT — cancels recovery mode"                                      | Cancel button is "Cancel Movement" — ABORT goes to MAX_HEIGHT                                                                                  | **Wrong**          | Change ABORT to "Cancel Movement"                              | Done          |
| **Consumable Change workflow**      | "Machine moves to consumable change position"                              | Code applies X/Y offset via HAL pins — **machine does NOT move** to a position                                                                 | **Wrong**          | Rewrite: applies X/Y offset via HAL pins, doesn't move machine | Done          |
| **Consumable Change state machine** | 5 states: IDLE, FEED_HOLD_WAIT, APPLYING_OFFSET, OFFSET_APPLIED, RESETTING | Code has: IDLE → FEED_HOLD_WAIT → OFFSET_APPLIED → IDLE (no APPLYING_OFFSET or RESETTING states)                                               | **Wrong**          | Update to 3 states: IDLE → FEED_HOLD_WAIT → OFFSET_APPLIED     | Done          |
| **Consumable Change trigger**       | "button on the WORK tab becomes active"                                    | Button is `btn_consumable_change` — it's a HalButton toggle, enabled only during feed hold                                                     | Partially correct  | Clarify it's a HalButton toggle enabled during feed hold       | Done          |
| **Consumable offset settings**      | "Configured per material"                                                  | Offsets are in Settings → MACHINE tab: `consumable_offset_x`, `consumable_offset_y`, `consumable_xy_feed_rate`                                 | **Wrong**          | Move to Settings → MACHINE tab context                         | Done          |
| **Run From Line**                   | Described as part of recovery                                              | "Run From Line" is a queue button (`btn_run_from`) in the MDI workspace, not recovery-related                                                  | **Wrong context**  | Move to MDI/queue context                                      | Done          |

---

## 5. `user-guide/mdi.md` — MODERATE ISSUES

Screenshot exists but documentation covers only a small fraction of the MDI screen.

| Issue                  | Docs Say                                        | Codebase (mainwindow.ui + screenshot description)                                              | Severity       | Action to Take                                | User Response |
| ---------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------- | --------------------------------------------- | ------------- |
| **MDI location**       | "at the bottom of the interface in the MDI tab" | MDI is in the **lower workspace** of the CONTROL & RUN tab, not a separate tab                 | **Wrong**      | Fix to "lower workspace of CONTROL & RUN tab" | Done          |
| **Screen structure**   | Single "MDI tab"                                | Two horizontal sections: upper (tool-path viewer) and lower (MDI queue + input + keypad)       | Major omission | Describe two horizontal sections              | Done          |
| **Parameter buttons**  | "G-code Parameter Buttons (P1-P10)"             | There is a single **PARAMS** button on the on-screen keypad, not P1-P10                        | **Wrong**      | Change to single PARAMS button                | Done          |
| **On-screen keypad**   | Not mentioned                                   | Full keypad with ROW UP/DOWN, F/T/M/G letter keys, numeric keys (0-9, ., -), SPACE, BKSP, SEND | Major omission | Add full keypad documentation                 | Done          |
| **Command queue**      | Not mentioned                                   | Large queue area with DEL ALL, DEL ROW, RUN FROM, RUN SINGLE, TO EDITOR buttons                | Major omission | Add queue area documentation                  | Done          |
| **Queue controls**     | Not mentioned                                   | PAUSE QUEUE, CLEAR QUEUE buttons                                                               | Major omission | Add PAUSE QUEUE, CLEAR QUEUE                  | Done          |
| **File controls**      | Not mentioned                                   | OPEN, RELOAD, RECENT buttons below the tool-path viewport                                      | Major omission | Add OPEN, RELOAD, RECENT                      | Done          |
| **Toolbar**            | Not mentioned                                   | 8-button toolbar: +, -, CENTER PLOT, CLEAR, PROG EXTENT, MACH EXTENT, TRANSFORM, SHOW TRAILS   | Major omission | Add 8-button toolbar documentation            | Done          |
| **Keyboard shortcuts** | Ctrl+O, Ctrl+S, Ctrl+R                          | These are standard Qt shortcuts, not MDI-specific                                              | Minor          | Note as standard Qt shortcuts                 | Done          |

---

## 6. `user-guide/statistics.md` — UNKNOWN

No screenshot exists. Cannot verify against codebase.

| Issue                     | Docs Say                                                  | Codebase                                                                                                                              | Severity    | Action to Take                                                | User Response |
| ------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------- | ------------- |
| **Tab location**          | "on the right column, below the SUB-LIST"                 | There is no "STATISTICS" tab — statistics are displayed via HAL pins (`plasmac.cut-length`, `plasmac.cut-time`) on various indicators | **Unclear** | Clarify there's no statistics tab; metrics shown via HAL pins |               |
| **Arc OK Indicator**      | Described as a visual indicator                           | `mk_led.arc-ok` LED exists in UI                                                                                                      | OK          | No action needed                                              |               |
| **Session Information**   | Session Start, Current Program, Total Cuts, Machine State | Not clearly visible as a "Session Information" section in the UI                                                                      | Unclear     | Clarify visibility                                            |               |
| **Cut Length / Cut Time** | Described as displaying metrics                           | HAL pins `plasmac.cut-length` and `plasmac.cut-time` exist                                                                            | OK          | No action needed                                              |               |

---

## 7. `user-guide/arc-start.md` — MINOR ISSUES

Values now sourced from Hypertherm 45 CSV data.

| Issue                       | Docs Say                  | Codebase (config.yml)                                | Severity  | Action to Take          | User Response     |
| --------------------------- | ------------------------- | ---------------------------------------------------- | --------- | ----------------------- | ----------------- |
| **Arc OK High default**     | 40.0 V                    | `arc_ok_high_volts` default = **250.0**              | **Wrong** | Done — updated to 250.0 | config.yml: 250.0 |
| **Arc OK Low default**      | 20.0 V                    | `arc_ok_low_volts` default = **60.0**                | **Wrong** | Done — updated to 60.0  | config.yml: 60.0  |
| **Arc Retry Delay default** | 1.0 second                | `arc_retry_delay` default = **60.0**                 | **Wrong** | Done — updated to 60.0  | pickle: 5.0       |
| **Puddle Jump Height**      | "2-4 mm above cut height" | `puddle_jump_height` default = **0.0** (stored as %) | Minor     | Note stored as %        | config.yml: 0.0   |
| **Puddle Jump Delay**       | "0.2-0.5 seconds"         | `puddle_jump_delay` default = **0.0**                | Minor     | Update                  | config.yml: 0.0   |
| **Torch Pulse**             | "0.1-0.3 seconds"         | `plasma_torch_pulse_sec` default = **0.3**           | OK        | No action needed        | pickle: 1.0       |
| **Arc Fail Timeout**        | 3.0 seconds               | `arc_fail_timeout` default = **3.0**                 | OK        | No action needed        | config.yml: 3.0   |
| **Arc Max Starts**          | 3 attempts                | `arc_max_starts` default = **3**                     | OK        | No action needed        | config.yml: 3     |

---

## 8. `user-guide/probe.md` — MINOR ISSUES

| **Probe Speed default**        | 25 mm/min                             | `probe_speed` default = **200**                                | **Wrong** | Done — updated to 200     | pickle: 300           |
| ------------------------------ | ------------------------------------- | -------------------------------------------------------------- | --------- | ------------------------- | --------------------- |
| **Probe Setup Speed default**  | Not given                             | `probe_setup_speed` default = **3000**                         | Missing   | Done — added default 3000 | config.yml: 3000      |
| **Probe Float Travel default** | Not given                             | `probe_float_travel` default = **3.2**                         | Missing   | Done — added default 3.2  | config.yml: 3.2       |
| **Probe Height default**       | "set near Z axis minimum"             | `probe_height` default = **15.0**                              | **Wrong** | Done — updated to 15.0 mm | pickle: 14.0          |
| **Probe Test Duration**        | "10 seconds (configurable in .prefs)" | `probe_test_time` = **10** (int, not in config.yml — internal) | OK        | No action needed          | config.yml: 10        |
| **OHMIC_PROBE_OFFSET**         | Described as "Probe Offset"           | Setting is `probe_offset` (labeled "OHMIC PROBE OFFSET" in UI) | OK        | No action needed          | config.yml: 0.0       |
| **Slat Top reference**         | `SLAT_TOP = -65.0`                    | INI has `SLAT_TOP = -65.0`                                     | OK        | No action needed          | INI: SLAT_TOP = -65.0 |
| **Slat Top reference**         | `SLAT_TOP = -65.0`                    | INI has `SLAT_TOP = -65.0`                                     | OK        | No action needed          |                       |

---

## 9. `user-guide/thc.md` — MAJOR ISSUES

| Issue                     | Docs Say                       | Codebase (config.yml)                                                                                                   | Severity           | Action to Take                                  | User Response    |
| ------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------------ | ----------------------------------------------- | ---------------- |
| **THC Threshold default** | 5.0 V                          | `thc_threshold` default = **1.0**                                                                                       | **Wrong**          | Done — updated to 1.0                           | config.yml: 1.0  |
| **THC PID P default**     | 1.0                            | `thc_pid_p_gain` default = **10.0**                                                                                     | **Wrong**          | Done — updated to 10.0                          | config.yml: 10.0 |
| **THC PID I default**     | 0.1                            | `thc_pid_i_gain` default = **0.0**                                                                                      | **Wrong**          | Done — updated to 0.0                           | config.yml: 0.0  |
| **THC PID D default**     | 0.05                           | `thc_pid_d_gain` default = **0.0**                                                                                      | **Wrong**          | Done — updated to 0.0                           | config.yml: 0.0  |
| **VAD Threshold default** | 20.0 V                         | `thc_vad_threshold` default = **60.0**                                                                                  | **Wrong**          | Done — updated to 60.0                          | config.yml: 60.0 |
| **Safe Height default**   | 2.0 mm                         | `thc_safe_height` default = **25.0**                                                                                    | **Wrong**          | Done — updated to 25.0                          | pickle: 40.0     |
| **Height Override**       | Range 0.0-2.0, default 1.0     | **Does not exist** in config.yml                                                                                        | **Does not exist** | Remove (doesn't exist)                          |                  |
| **Corner Lock**           | "Checkbox on the Settings tab" | `corner_lock` setting exists but there is no UI checkbox labeled "Corner Lock" — it's a HAL pin (`plasmac.corner-lock`) | **Wrong**          | Clarify it's a HAL pin, not UI checkbox         |                  |
| **THC State Indicators**  | "THC IDLE" listed as indicator | No "THC IDLE" indicator in UI — only THC UP, THC DOWN, THC ACTIVE, THC AUTO Vs                                          | **Wrong**          | Done — replaced with THC ACTIVE and THC AUTO Vs |                  |

---

## 10. `integrator-guide/config-yml.md` — MAJOR ISSUES

This file has its own settings tables that also diverge from config.yml.

| Issue                            | Docs Say      | config.yml                                | Severity           | Action to Take                    | User Response |
| -------------------------------- | ------------- | ----------------------------------------- | ------------------ | --------------------------------- | ------------- |
| **THC Threshold default**        | 5.0           | **1.0**                                   | **Wrong**          | Done — updated to 1.0             |               |
| **THC PID P default**            | 1.0           | **10.0**                                  | **Wrong**          | Done — updated to 10.0            |               |
| **THC PID I default**            | 0.1           | **0.0**                                   | **Wrong**          | Done — updated to 0.0             |               |
| **THC PID D default**            | 0.05          | **0.0**                                   | **Wrong**          | Done — updated to 0.0             |               |
| **Safe Height default**          | 2.0           | **25.0**                                  | **Wrong**          | Done — updated to 40.0 (pickle)   |               |
| **Float Travel default**         | 4.0           | **3.2**                                   | **Wrong**          | Done — updated to 3.2             |               |
| **Probe Speed default**          | 25.0          | **200**                                   | **Wrong**          | Done — updated to 300 (pickle)    |               |
| **Probe Setup Speed default**    | 25.0          | **3000**                                  | **Wrong**          | Done — updated to 3000            |               |
| **Arc OK High default**          | 40.0          | **250.0**                                 | **Wrong**          | Done — updated to 250.0           |               |
| **Arc OK Low default**           | 20.0          | **60.0**                                  | **Wrong**          | Done — updated to 60.0            |               |
| **Arc Retry Delay default**      | 1.0           | **60.0**                                  | **Wrong**          | Done — updated to 5.0 (pickle)    |               |
| **Arc Voltage Scale default**    | 1.0           | **0.006744**                              | **Wrong**          | Done — updated to 0.006744        |               |
| **Arc Voltage Offset default**   | 0.0           | **3687.5**                                | **Wrong**          | Done — updated to 3687.5          |               |
| **Arc Height Per Volt**          | Not listed    | `arc_height_per_volt` default = **0.100** | Missing            | Done — added default 0.100        |               |
| **Spot Threshold default**       | 5.0           | **0.1**                                   | **Wrong**          | Done — updated to 5.0 (pickle)    |               |
| **Spot Delay default**           | 0.0           | **600.0**                                 | **Wrong**          | Done — updated to 100.0 (pickle)  |               |
| **Hole Thickness Ratio default** | 2.0           | **5**                                     | **Wrong**          | Done — updated to 5               |               |
| **Max Hole Size default**        | 25.0          | **50.0**                                  | **Wrong**          | Done — updated to 50.0            |               |
| **Small Hole Threshold default** | 25.0          | **3.5**                                   | **Wrong**          | Done — updated to 3.5             |               |
| **Consumable XY Feed default**   | 1000.0        | **0.0**                                   | **Wrong**          | Done — updated to 0.0             |               |
| **Framing Feed default**         | 100.0         | **0.0**                                   | **Wrong**          | Done — updated to 2000.0 (pickle) |               |
| **Run Delete Confirm default**   | false         | **true**                                  | **Wrong**          | Done — updated to true            |               |
| **Height Override**              | Listed as 1.0 | **Does not exist**                        | **Does not exist** | Remove (doesn't exist)            |               |
| **Corner Lock**                  | Listed        | Exists but not in settings tables shown   | Missing            | Done — added to settings tables   |               |
| **Auto Volts**                   | Listed        | Exists but not in settings tables shown   | Missing            | Done — added to settings tables   |               |
| **Arc Height Per Volt**          | Not listed    | Exists                                    | Missing            | Done — added to settings tables   |               |

---

## 11. `reference/persistent-settings.md` — MAJOR ISSUES

Same settings tables as config-yml.md, same divergences.

| Issue                    | Docs Say                      | config.yml | Severity          | Action to Take                             | User Response |
| ------------------------ | ----------------------------- | ---------- | ----------------- | ------------------------------------------ | ------------- |
| Same 20+ defaults wrong  | See config-yml.md table above | —          | **Same as above** | Done — applied same fixes as config-yml.md |               |
| **Probe Float Travel**   | 4.0                           | **3.2**    | **Wrong**         | Done — updated to 3.2                      |               |
| **Probe Setup Speed**    | 25.0                          | **3000**   | **Wrong**         | Done — updated to 3000                     |               |
| **Spot Threshold**       | 5.0                           | **0.1**    | **Wrong**         | Done — updated to 5.0 (pickle)             |               |
| **Spot Delay**           | 0.0                           | **600.0**  | **Wrong**         | Done — updated to 100.0 (pickle)           |               |
| **Hole Thickness Ratio** | 2.0                           | **5**      | **Wrong**         | Done — updated to 5                        |               |
| **Max Hole Size**        | 25.0                          | **50.0**   | **Wrong**         | Done — updated to 50.0                     |               |
| **Small Hole Threshold** | 25.0                          | **3.5**    | **Wrong**         | Done — updated to 3.5                      |               |
| **Consumable XY Feed**   | 1000.0                        | **0.0**    | **Wrong**         | Done — updated to 0.0                      |               |
| **Framing Feed**         | 100.0                         | **0.0**    | **Wrong**         | Done — updated to 2000.0 (pickle)          |               |
| **Run Delete Confirm**   | false                         | **true**   | **Wrong**         | Done — updated to true                     |               |

---

## 12. `reference/state-machine.md` — MINOR ISSUES

| Issue                     | Docs Say                                                          | Codebase (explorer results)                                                     | Severity                  | Action to Take                    | User Response |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------- | --------------------------------- | ------------- |
| **PROBE_DOWN transition** | `PROBE_DOWN -> {PROBE_TEST, MAX_HEIGHT, PROBE_HEIGHT, PROBE_UP}`  | Explorer found: `PROBE_DOWN -> {PROBE_TEST, MAX_HEIGHT, PROBE_HEIGHT PROBE_UP}` | OK                        | No action needed                  |               |
| **PROBE_UP transition**   | `PROBE_UP -> {PROBE_TEST, PROBE_DOWN, PIERCE_HEIGHT, MAX_HEIGHT}` | Explorer found: `PROBE_UP -> {PROBE_TEST, PROBE_DOWN PIERCE_HEIGHT MAX_HEIGHT}` | OK                        | No action needed                  |               |
| **PUDDLE_JUMP state**     | Listed in state descriptions                                      | Not in explorer's state list — state exists in code                             | Missing from descriptions | Add Puddle Jump state description |               |
| **PAUSED_MOTION**         | Listed as a state                                                 | Exists in code                                                                  | OK                        | No action needed                  |               |
| **Total states**          | 22 states documented                                              | Explorer found 22 states                                                        | OK                        | No action needed                  |               |

---

## 13. `reference/hal-pin-map.md` — MINOR ISSUES

| Issue                           | Docs Say                  | Codebase | Severity | Action to Take   | User Response |
| ------------------------------- | ------------------------- | -------- | -------- | ---------------- | ------------- |
| **`plasmac.arc-voltage-in`**    | Direction: IN             | Exists   | OK       | No action needed |               |
| **`plasmac.arc-voltage`**       | Direction: OUT            | Exists   | OK       | No action needed |               |
| **`plasmac.ohmic-enable`**      | Direction: OUT            | Exists   | OK       | No action needed |               |
| **`plasmac.probe-test`**        | Direction: IN             | Exists   | OK       | No action needed |               |
| **`plasmac.probe-test-error`**  | Direction: OUT, type: s32 | Exists   | OK       | No action needed |               |
| **`plasmac.consumable-change`** | Direction: IN             | Exists   | OK       | No action needed |               |
| **`plasmac.cut-chart`**         | Direction: IN/OUT         | Exists   | OK       | No action needed |               |
| **`plasmac.lowpass-frequency`** | Direction: IN             | Exists   | OK       | No action needed |               |

---

## 14. `reference/quickshape-reference.md` — MODERATE ISSUES

Same shape name/parameter issues as `conversational.md` (see section 3 above).

---

## 15. `reference/gcode-syntax.md` — MINOR ISSUES

| Issue                     | Docs Say                                          | Codebase                                                                                               | Severity               | Action to Take                | User Response |
| ------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------- | ----------------------------- | ------------- |
| **Title says "MonoKorn"** | "MonoKorn Plasma" (typo)                          | Package is "MonoKrom"                                                                                  | **Typo**               | Fix typo: MonoKorn → MonoKrom |               |
| **G95**                   | Listed as "Feed rate per revolution"              | LinuxCNC supports G95 but plasma rarely uses it                                                        | OK                     | No action needed              |               |
| **M7/M8/M9**              | Listed as coolant commands                        | Plasma machines typically don't have coolant                                                           | OK (standard LinuxCNC) | Note as standard LinuxCNC     |               |
| **Example program**       | Pierce Height 6.0, Cut Height 3.5, Feed Rate 1200 | Not verifiable without a specific material in CSV                                                      | Minor                  | No action needed              |               |
| **G0 Z50 retract**        | Uses Z50                                          | `SAFE_HEIGHT` default = 25.0, but Z max = 0.001 (MIN_LIMIT = -70.001) — Z50 would be above safe height | OK (safe)              | No action needed              |               |

---

## 16. `integrator-guide/ini-config.md` — MINOR ISSUES

| Issue                   | Docs Say                          | plasmac_sim.ini                             | Severity                                                            | Action to Take                         | User Response |
| ----------------------- | --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------- | ------------- |
| **SPINDLES = 3**        | "3 for plasma: main, THC, offset" | INI has `SPINDLES = 3`                      | OK (but explanation is misleading — LinuxCNC always has 3 spindles) | Clarify LinuxCNC always has 3 spindles |               |
| **NO_FORCE_HOMING = 1** | "Skip forced homing"              | INI has `NO_FORCE_HOMING = 1`               | OK                                                                  | No action needed                       |               |
| **USER button config**  | Described correctly               | INI has USER1/2/3_NAME and USER1/2/3_ACTION | OK                                                                  | No action needed                       |               |
| **CONFIG_FILE**         | Shows `custom_config.yml`         | INI has `CONFIG_FILE = custom_config.yml`   | OK                                                                  | No action needed                       |               |
| **PREFERENCE_FILE**     | Shows `sim.pref`                  | INI has `PREFERENCE_FILE = sim.pref`        | OK                                                                  | No action needed                       |               |

---

## 17. `integrator-guide/hal-connections.md` — MINOR ISSUES

| Issue                        | Docs Say                                                   | Codebase                  | Severity | Action to Take   | User Response |
| ---------------------------- | ---------------------------------------------------------- | ------------------------- | -------- | ---------------- | ------------- |
| **HAL file names**           | `plasmac_sim_overlay.hal`, `qtplasmac_connections_sim.hal` | INI has these exact files | OK       | No action needed |               |
| **Debounce component names** | `db_breakaway, db_float, db_ohmic, db_arc-ok`              | HAL file uses these names | OK       | No action needed |               |
| **Mode 0/1/2 descriptions**  | Correctly described                                        | INI `MODE = 0`            | OK       | No action needed |               |

---

## 18. `integrator-guide/process-db.md` — MODERATE ISSUES

| Issue                  | Docs Say                                                                                                                                                      | Codebase (CSV columns)                                                                                                                                                                                                                                                               | Severity                         | Action to Take                                             | User Response |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- | ---------------------------------------------------------- | ------------- |
| **Schema columns**     | 13 columns: gas, machine, material, thickness, consumable, pierce_height, pierce_delay, cut_height, cut_feed_rate, cut_volts, cut_amperage, kerf, tool_number | CSV has **22 columns**: machine_name, material, thickness, thickness_unit, thickness_name, name, consumable, tool_number, kerf_width, plunge_rate, pierce_delay, pause_at_end, pierce_height, cut_height, cut_speed, amps, pressure, pressuresys, volts, puddle_height, puddle_delay | **Wrong** — schema is incomplete | Update to 22 columns                                       |               |
| **Filter fields**      | Lists 5: Gas, Machine, Material, Thickness, Consumable                                                                                                        | Code has **8**: Gas, Machine, Material, Thickness, Consumable, Operation, Quality, plus 2 locked fields                                                                                                                                                                              | **Wrong**                        | Update to 8 fields (add Operation, Quality, plus 2 locked) |               |
| **Database file name** | `plasma_table.db`                                                                                                                                             | Exists                                                                                                                                                                                                                                                                               | OK                               | No action needed                                           |               |

---

## 19. `quick-start.md` — MINOR ISSUES

| Issue                 | Docs Say                             | Codebase                                                                          | Severity  | Action to Take                          | User Response |
| --------------------- | ------------------------------------ | --------------------------------------------------------------------------------- | --------- | --------------------------------------- | ------------- |
| **Repo URL**          | `monokrom-vcp`                       | Repo is `monokrom`                                                                | **Wrong** | Fix repo name: monokrom-vcp → monokrom  |               |
| **Command**           | `monokrom --install-sim`             | Entry point is `monokrom_plasma --install-sim` (or `monokrom_mill --install-sim`) | **Wrong** | Fix command: monokrom → monokrom_plasma |               |
| **Home button**       | "Click the HOME button"              | Home buttons exist for each axis                                                  | OK        | No action needed                        |               |
| **Probe test button** | "On the Probe tab, click PROBE TEST" | `btn_probe_test` exists in Settings → THC/ARC/Probe tab                           | OK        | No action needed                        |               |

---

## Summary by Severity

| Severity                                                          | Count             | Affected Files                                                                                                  |
| ----------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------- |
| **Wrong defaults** (settings values diverge from config.yml)      | **28+ instances** | `settings.md`, `thc.md`, `arc-start.md`, `probe.md`, `config-yml.md`, `persistent-settings.md`                  |
| **Does not exist** (features/settings documented but not in code) | **3**             | `settings.md` (Height Override), `parameters.md` (Material Settings section)                                    |
| **Wrong layout/structure** (UI description doesn't match code)    | **5**             | `parameters.md`, `settings.md`, `mdi.md`, `recovery.md`, `conversational.md`                                    |
| **Wrong shape parameters** (quickshape docs don't match code)     | **6 shapes**      | `conversational.md`, `quickshape-reference.md`                                                                  |
| **Major omissions** (significant features not documented)         | **8**             | `parameters.md` (hole processing, THC panel), `mdi.md` (keypad, queue), `settings.md` (scribe/spot, DRO format) |
| **Typo/Wrong naming**                                             | **3**             | `gcode-syntax.md` (MonoKorn), `quick-start.md` (repo name, command)                                             |
| **Minor** (naming, missing defaults, cosmetic)                    | **15+**           | Various files                                                                                                   |

## Recommended Priority Order

1. **Fix settings defaults** — 28+ wrong values across 6 files, same root cause (values diverging from `config.yml`)
2. **Fix UI layout descriptions** — `parameters.md`, `mdi.md`, `recovery.md` describe structures that don't match the actual UI
3. **Fix quickshape parameters** — 6 shapes with incorrect parameter lists
4. **Fix process DB schema** — update to match actual CSV columns
5. **Clean up typos and non-existent features**

---

## Changes Made (Pickle + config.yml Defaults Applied)

### Files Updated

| File                     | Changes                                                                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `settings.md`            | Updated all defaults; removed Height Override section; added Scribe, Spot, Arc Height Per Volt, Consumable XY Feed, Framing Feed, Run Delete Confirm sections |
| `thc.md`                 | Updated THC Threshold, PID gains, VAD Threshold, VAD Override, Safe Height; removed Height Override; fixed THC state indicators                               |
| `arc-start.md`           | Updated Arc OK High/Low, Arc Retry Delay; changed Torch Pulse from "Typical" to "Default"                                                                     |
| `probe.md`               | Updated Probe Speed, Probe Height references                                                                                                                  |
| `config-yml.md`          | Updated all settings tables with correct defaults and setting names matching config.yml                                                                       |
| `persistent-settings.md` | Updated all settings tables with correct defaults and setting names matching config.yml                                                                       |

### Default Values Updated (Pickle values used as priority)

| Setting                  | Pickle Value | config.yml Default | Docs Now Show   |
| ------------------------ | ------------ | ------------------ | --------------- |
| `thc_safe_height`        | 40.0         | 25.0               | 40.0 (pickle)   |
| `thc_void_override`      | 99           | 100                | 99 (pickle)     |
| `probe_speed`            | 300          | 200                | 300 (pickle)    |
| `probe_height`           | 14.0         | 15.0               | 14.0 (pickle)   |
| `probe_offset`           | -0.5         | 0.0                | -0.5 (pickle)   |
| `arc_retry_delay`        | 5.0          | 60.0               | 5.0 (pickle)    |
| `spot_threshold`         | 5.0          | 0.1                | 5.0 (pickle)    |
| `spot_delay`             | 100.0        | 600.0              | 100.0 (pickle)  |
| `plasma_torch_pulse_sec` | 1.0          | 0.3                | 1.0 (pickle)    |
| `plasma_auto_volts`      | True         | false              | true (pickle)   |
| `framing_feed_rate`      | 2000.0       | 0.0                | 2000.0 (pickle) |
| `consumable_offset_x`    | 10.0         | 0.0                | 10.0 (pickle)   |
| `plasma_vad`             | True         | false              | true (pickle)   |
| `plasma_void_sense`      | True         | false              | true (pickle)   |
| `thc_enabled`            | True         | false              | true (pickle)   |
| `thc_feed_rate`          | 3000.0       | 0.0                | 3000.0 (pickle) |
| `ohmic_sensing_enabled`  | True         | false              | true (pickle)   |

### Settings NOT in Pickle (using config.yml defaults)

All remaining settings use config.yml defaults since they were not found in the pickle file:

- `thc_threshold` = 1.0
- `thc_pid_p_gain` = 10.0
- `thc_pid_i_gain` = 0.0
- `thc_pid_d_gain` = 0.0
- `thc_vad_threshold` = 60.0
- `arc_ok_high_volts` = 250.0
- `arc_ok_low_volts` = 60.0
- `probe_setup_speed` = 3000
- `arc_voltage_scale` = 0.006744
- `arc_voltage_offset` = 3687.5
- `arc_height_per_volt` = 0.100
- `plasma_hole_thickness_ratio` = 5
- `plasma_max_hole_size` = 50.0
- `plasma_small_hole_threshold` = 3.5
- `consumable_xy_feed_rate` = 0.0
- `run_delete_confirm` = true
- `thc_feed_rate` = 0.0

### Items Flagged for Investigation

| Setting                     | Pickle Value | config.yml Default | Docs Now Show | Status        |
| --------------------------- | ------------ | ------------------ | ------------- | ------------- |
| `thc_safe_height`           | 40.0         | 25.0               | 40.0          | Done (pickle) |
| `thc_void_override`         | 99           | 100                | 99            | Done (pickle) |
| `probe_speed`               | 300          | 200                | 300           | Done (pickle) |
| `probe_height`              | 14.0         | 15.0               | 14.0          | Done (pickle) |
| `probe_offset`              | -0.5         | 0.0                | -0.5          | Done (pickle) |
| `arc_retry_delay`           | 5.0          | 60.0               | 5.0           | Done (pickle) |
| `spot_threshold`            | 5.0          | 0.1                | 5.0           | Done (pickle) |
| `spot_delay`                | 100.0        | 600.0              | 100.0         | Done (pickle) |
| `plasma_torch_pulse_sec`    | 1.0          | 0.3                | 1.0           | Done (pickle) |
| `plasma_auto_volts`         | true         | false              | true          | Done (pickle) |
| `plasma_vad`                | true         | false              | true          | Done (pickle) |
| `plasma_void_sense`         | true         | false              | true          | Done (pickle) |
| `thc_enabled`               | true         | false              | NOT in docs   | Investigate   |
| `thc_feed_rate`             | 3000.0       | 0.0                | 3000.0        | Done (pickle) |
| `ohmic_sensing_enabled`     | true         | false              | NOT in docs   | Investigate   |
| `consumable_offset_x`       | 10.0         | 0.0                | 10.0          | Done (pickle) |
| `framing_feed_rate`         | 2000.0       | 0.0                | 2000.0        | Done (pickle) |
| `backplot.multitool-colors` | true         | true               | true          | Same          |

**Note:** Pickle values are used as priority per user instruction. Settings not found in the pickle file fall back to config.yml defaults. The pickle file represents user-modified values stored in `vcp_persistent_data.pickle` — these reflect a real machine configuration, not a fresh install.
