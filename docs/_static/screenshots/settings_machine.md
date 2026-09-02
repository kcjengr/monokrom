# Plasma Machine Settings and Parameters Screen Description

## Overview

The screenshot shows the **Machine** page within the **Settings** section of a plasma cutting machine interface. The screen uses a near-black background with dark olive panels and bright yellow headers, borders, labels, values, and controls.

The workspace is divided into these main areas:

1. **User input and display formatting** on the upper left.
2. **Process confirmation preferences** below the display settings.
3. **Laser, camera, scribe, and ohmic offsets** in the upper centre-left.
4. **Machine and table settings** below the offset controls.
5. **Database seeding controls** in the lower left.
6. **Job Favorites** in a large panel on the right.
7. A persistent **application navigation bar** along the bottom.

---

## 1. Top-level headings

The top of the settings workspace contains two main headings:

- **THC / ARC / PROBE & MARKING**, centred over the left-side configuration area.
- **MACHINE**, shown as a wide filled yellow tab over the main right-side area.

The highlighted **MACHINE** heading indicates that the visible settings belong to the machine configuration page.

---

## 2. User Input panel

The upper-left **USER INPUT** panel contains one checkbox option:

- **On-Screen Keyboard**: not selected.

The checkbox is displayed as an empty rounded square. The option controls whether an on-screen keyboard is used for text or numeric entry, based on the visible label.

---

## 3. DRO Format panel

The **DRO FORMAT** panel defines the formatting used for displayed numeric values. DRO is the abbreviation shown in the panel title.

### Visible fields

| Setting | Displayed value |
|---|---|
| **Inch Format** | `%9.4f` |
| **Millimeter Format** | `%9.3f` |
| **Degree Format** | `%9.2f` |
| **Display Units** | `Auto` |

The first three values appear in bordered text-entry fields. **Display Units** is a yellow dropdown field with a downward arrow.

The format strings visually indicate different decimal precision for inches, millimetres, and degrees. The screenshot does not include an explanation of the format-string syntax.

---

## 4. Process Run Save/Delete Confirms panel

The **PROCESS RUN SAVE/DELETE CONFIRMS** panel contains two confirmation preferences:

- **Ask before Process Run save**: not selected.
- **Ask before Process Run delete**: selected.

The selected delete-confirmation option is shown as a filled yellow rounded square containing a dark check mark. The save-confirmation option is shown as an empty outlined square.

---

## 5. Laser, Camera & Scribe Offsets panel

The **LASER, CAMERA & SCRIBE OFFSETS** panel contains X and Y offset values for four devices or sensing modes.

Two column headings identify the coordinate directions:

- **X**
- **Y**

Each numeric control includes a circular minus button, a central value, and a circular plus button.

| Device or mode | X offset | Y offset |
|---|---:|---:|
| **LASER** | `0.00000` | `0.00000` |
| **CAMERA** | `0.00000` | `0.00000` |
| **SCRIBE** | `0.00000` | `0.00000` |
| **OHMIC** | `0.00000` | `0.00000` |

A thin vertical text cursor is visible at the beginning of the Laser X value, suggesting that this field has input focus in the captured screen.

---

## 6. Machine & Table Settings panel

The **MACHINE & TABLE SETTINGS** panel contains unit, machine-selection, timing, feed, and offset parameters.

### 6.1 Dropdown settings

Three dark dropdown fields appear at the top of the panel:

| Setting | Selected value |
|---|---|
| **DISTANCE SYSTEM** | `mm` |
| **PRESSURE SYSTEM** | `bar` |
| **MACHINE** | `A120` |

Each field includes a subtle downward arrow on the right. The dark appearance contrasts with the bright yellow editable controls below and may indicate a different state or control style. The screenshot alone does not specify whether these dropdowns are disabled.

### 6.2 Adjustable machine values

| Parameter | Displayed value |
|---|---:|
| **TORCH PULSE DURATION** | `0.300 S` |
| **CONSUMABLE XY FEEDRATE** | `0.00` |
| **CONSUMABLE X OFFSET** | `7.99900` |
| **CONSUMABLE Y OFFSET** | `7.99900` |
| **FRAMING FEED** | `0.00` |

Each value is displayed in a yellow minus/value/plus control. The screenshot explicitly shows seconds for torch pulse duration, but no units are displayed beside the remaining values.

---

## 7. DB Seeding panel

The lower-left **DB SEEDING** panel contains controls associated with loading seed data from a file.

### Visible controls

- **Seed DB from file** button.
- A long bordered path field displaying:

```text
~/linuxcnc/configs/sim.monokrom/plasmac/master-seed-source.csv
```

The remainder of the panel is empty. The visible labels and file path indicate that the panel references a CSV seed-source file.

---

## 8. Job Favorites panel

A large bordered **JOB FAVORITES** panel occupies much of the right side of the screen.

### Visible structure

- A bright yellow panel header labelled **JOB FAVORITES**.
- A large empty dark content area, with no favorite jobs or entries visible.
- Two bordered buttons positioned around the middle of the panel:
  - **ADD**
  - **NEW**

The screenshot does not show any selected item, list heading, explanatory text, or additional fields inside this panel.

---

## 9. Bottom navigation bar

A persistent navigation bar spans the bottom of the application:

- **CONTROL & RUN**
- **CUT & MATERIAL**
- **QUICKSHAPES**
- **SETTINGS**
- **DIAGNOSTICS**

**SETTINGS** is the active section and is highlighted as a wide filled yellow tab. The other navigation options appear as yellow text on the dark background.

---

## 10. Machine status message

A small status message appears at the bottom-left edge:

> Can't turn machine ON until out of E-Stop

The message indicates that machine activation is blocked while the emergency-stop condition remains active.

---

## 11. Visual and interaction design

- **High contrast:** Bright yellow labels and controls stand out against the dark interface.
- **Panel grouping:** Yellow headers and borders divide preferences, offsets, machine parameters, database controls, and favorites.
- **Consistent numeric editing:** Adjustable numeric values use a repeated minus/value/plus arrangement.
- **Mixed input types:** The screen includes checkboxes, text fields, dropdowns, numeric controls, and action buttons.
- **Touch-oriented layout:** Large controls and wide spacing make the interface suitable for touchscreen operation.
- **State indication:** Filled yellow checkboxes indicate selected options, while empty outlines indicate unselected options.
- **Unused space:** Large empty areas remain in the Machine workspace and Job Favorites panel, creating a sparse layout on this settings page.

---

## Functional layout summary

| Screen area | Main purpose | Visible controls and information |
|---|---|---|
| Upper-left | Configure data entry | On-Screen Keyboard checkbox |
| Left-middle | Define numeric display formats | Inch, millimetre, degree, and automatic display-unit settings |
| Left-lower-middle | Configure save/delete confirmations | Confirmation checkboxes for Process Run save and delete actions |
| Upper centre-left | Enter accessory offsets | X and Y offsets for laser, camera, scribe, and ohmic functions |
| Centre-left | Configure machine and table values | Unit systems, machine selection, torch pulse, consumable offsets/feed, and framing feed |
| Lower-left | Load database seed data | Seed button and CSV source path |
| Right | Manage job favorites | Empty favorites area with Add and New buttons |
| Bottom | Navigate between application modules | Control & Run, Cut & Material, Quickshapes, Settings, and Diagnostics |
| Bottom-left edge | Display interlock status | Emergency-stop warning |
