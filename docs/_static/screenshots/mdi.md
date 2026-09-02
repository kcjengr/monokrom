# Plasma UI MDI Screen Description

## Overview

The screenshot shows the **MDI (Manual Data Input)** area of a plasma machine user interface. The screen combines a tool-path viewer with controls for loading programs, managing an MDI command queue, entering commands through an on-screen keypad, and sending commands to the machine controller.

The interface uses a high-contrast industrial color scheme:

- Near-black background.
- Dark olive control surfaces.
- Bright yellow headers, borders, labels, and selected controls.
- A large black plotting area.

The screen is divided into two principal horizontal sections:

1. A large **Tool Path / G-code viewer** across the upper portion.
2. An **MDI command and queue workspace** across the lower portion.

---

## 1. Tool Path and G-code header

Two large tabs span the top of the screen:

- **TOOL PATH**: filled yellow, indicating the selected view.
- **GCODE**: dark background with yellow text, indicating an alternate view.

The selected Tool Path view occupies most of the upper screen.

---

## 2. Tool-path toolbar

A row of eight controls appears immediately below the header:

| Control | Visible purpose |
|---|---|
| **+** | Increase the plot scale or zoom in |
| **-** | Decrease the plot scale or zoom out |
| **CENTER PLOT** | Centre the plotted geometry in the viewport |
| **CLEAR** | Clear the visible plot or displayed trail information |
| **PROG EXTENT** | Fit or display the program extents |
| **MACH EXTENT** | Fit or display the machine extents |
| **TRANSFORM** | Access a plot or coordinate transformation function |
| **SHOW TRAILS** | Display tool or movement trails |

**PROG EXTENT**, **MACH EXTENT**, and **SHOW TRAILS** are filled yellow. The remaining buttons have dark interiors with yellow outlines.

The exact active-state meaning of the filled controls is not explained within the screenshot.

---

## 3. Tool-path viewport

A large black rectangular viewport fills most of the upper screen beneath the toolbar.

In the captured state:

- No tool path or part geometry is visible.
- No coordinate axes, grid, dimensions, or position marker are shown.
- No warning or empty-state message appears inside the viewport.

The viewport is bordered by the surrounding dark panel rather than by a separate bright outline.

---

## 4. Program file controls

Three wide buttons appear directly below the tool-path viewport:

- **OPEN**: dark button with a bright yellow border.
- **RELOAD**: visibly dimmed, suggesting an unavailable or inactive state.
- **RECENT**: dark button with a bright yellow border.

These controls visually provide access to program-file selection and reuse. The screenshot does not show a current filename.

---

## 5. Lower MDI workspace

The lower section is enclosed by a bright yellow border and divided into two major areas:

1. A large queue or command-list area on the left.
2. The MDI input field and on-screen keypad on the right.

---

## 6. Queue or command-list area

A large dark rectangular area occupies the lower-left side of the MDI workspace.

Visible characteristics:

- The area has a slightly lighter dark background than the outer screen.
- No commands, rows, cursor, headings, or status messages are visible.
- The empty area likely serves as the visible command queue or command history, based on the adjacent queue controls.

### Queue action buttons

Five buttons run along the bottom of this area:

- **DEL ALL**
- **DEL ROW**
- **RUN FROM**
- **RUN SINGLE**
- **TO EDITOR**

The button labels indicate operations for deleting queue contents, running selected commands, and transferring content to an editor. No row is visibly selected in the screenshot.

---

## 7. MDI command input field

At the top of the lower-right workspace is a long bordered input field labelled:

- **MDI:**

The field is empty. The label appears at the left inside the control rather than above it.

This field is positioned directly above the on-screen command keypad.

---

## 8. Queue controls

Two labelled buttons appear at the left side of the keypad's upper rows:

- **PAUSE QUEUE**
- **CLEAR QUEUE**

Additional blank bordered buttons occupy the same rows to the right. These blank controls contain no visible text or symbols.

Two more blank buttons appear on a shorter row beneath the queue controls.

The blank controls may be reserved or configurable, but the screenshot provides no labels or explanation.

---

## 9. MDI on-screen keypad

The lower-right area contains a structured keypad for entering common MDI letters, numbers, punctuation, spacing, and parameters.

### 9.1 Navigation buttons

The leftmost keypad column begins with:

- **ROW UP**
- **ROW DOWN**

These buttons are aligned with the first two main keypad rows.

### 9.2 Letter keys

Visible command-letter keys include:

- **F**
- **T**
- **M**
- **G**

These letters are placed in a vertical column beside the numeric keys.

### 9.3 Numeric keys

The numeric keypad follows a calculator-style arrangement:

| Row | Keys |
|---|---|
| Upper numeric row | `7`, `8`, `9` |
| Middle numeric row | `4`, `5`, `6` |
| Lower numeric row | `1`, `2`, `3` |
| Bottom numeric row | `0`, `.`, `-` |

### 9.4 Command-entry controls

The bottom row contains:

- **SPACE**
- **PARAMS**
- **BKSP**
- **SEND**

These controls provide space entry, parameter access, backspace, and command submission.

---

## 10. Visual states and interaction design

- **Selected tab:** Tool Path is clearly selected through a filled yellow header.
- **Inactive or alternate tab:** G-code remains dark with yellow text.
- **Unavailable control:** Reload is visibly dimmer than Open and Recent.
- **Empty state:** Both the tool-path viewport and queue area contain no visible content.
- **Touch-oriented layout:** Large buttons, generous spacing, and a full on-screen keypad support touchscreen operation.
- **Consistent styling:** Most actionable controls use rounded yellow borders with yellow text on dark interiors.
- **Active toolbar controls:** Several toolbar buttons are filled yellow, distinguishing them from outline-only controls.

---

## Functional layout summary

| Screen area | Main purpose | Visible elements |
|---|---|---|
| Top header | Select the main program view | Tool Path and G-code tabs |
| Upper toolbar | Control plot presentation | Zoom, centre, clear, program extent, machine extent, transform, and trails |
| Main upper viewport | Display program geometry | Empty black tool-path plotting area |
| File-control row | Manage program files | Open, Reload, and Recent |
| Lower-left area | Display queued or entered commands | Empty command-list area |
| Lower-left button row | Manage and execute queue rows | Delete all, delete row, run from, run single, and transfer to editor |
| Lower-right input | Enter an MDI command | Empty MDI field |
| Lower-right upper controls | Manage command queue | Pause Queue, Clear Queue, and unlabelled buttons |
| Lower-right keypad | Construct and submit commands | Row navigation, F/T/M/G keys, numbers, decimal point, minus, Space, Params, Backspace, and Send |

---

## Visible screen state

The screenshot captures an empty MDI workspace:

- The Tool Path view is selected.
- No program geometry is plotted.
- No G-code or MDI commands are listed.
- The MDI input field is empty.
- Reload appears unavailable.
- Program and machine extent controls, plus Show Trails, are visually highlighted.

This description records the visible layout, labels, values, and control states. Functional interpretations are limited to what is directly indicated by the control labels and their placement.
