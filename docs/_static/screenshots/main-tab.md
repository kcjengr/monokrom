# Plasma UI Layout Analysis

## Overview

The image shows a full-screen industrial plasma cutting machine interface with a high-contrast black, dark olive, and bright yellow color scheme. The screen is divided into three main vertical work areas:

1. **Machine position and primary controls** on the left.
2. **Run monitoring and plasma-process controls** in the center.
3. **Tool-path and G-code visualization** on the right.

A persistent navigation bar runs along the bottom of the screen.

---

## 1. Left Area: Work, Machine Position, and Main Controls

### 1.1 Work / Machine header

The upper-left panel has two large tabs:

- **WORK**: selected and highlighted in yellow.
- **MACHINE**: an alternate coordinate or machine-state view.

A small crosshair-style icon appears near the Machine tab.

### 1.2 Coordinate-system selection

A row of six buttons selects the active coordinate system:

- **G54**: currently selected.
- **G55**
- **G56**
- **G57**
- **G58**
- **G59**

### 1.3 Axis position readouts

Three large digital displays show the current machine or work coordinates:

- **X: -226.900**
- **Y: -264.800**
- **Z: 0.000**

Each axis row includes a home-style icon, suggesting an axis reference, homing, or zero-related function.

### 1.4 Positioning and zeroing controls

To the right of the axis readouts are two tall buttons:

- A large button with a **home icon**.
- **ZERO XY in G5x**, used to set the X and Y work zero for the selected G5x coordinate system.

### 1.5 Motion and process status

Below the coordinate panel, a status strip displays:

- **FEED RATE: 0.00**
- **CURRENT VELOCITY: 0.00**
- **ACTIVE CUT PROCESS: Auto Material 8mm**

This area summarizes current movement and the selected cutting process or material preset.

### 1.6 Control panel

The lower-left **CONTROL** panel contains the principal machine-operation buttons:

- **CYCLE START**: starts or resumes the machining cycle.
- **FEED HOLD**: pauses commanded feed motion.
- **STOP / ABORT**: stops or aborts the current operation.
- **M1 BREAK**: enables or invokes an optional program stop.
- **CONSUMABLE CHANGE**: supports a torch consumable-change workflow.
- **FRAME JOB**: traces or checks the boundary of the loaded job.
- **PARK**: moves the machine to a predefined parked position.
- **GOTO WORK ZERO**: moves to the active work-coordinate origin.
- **GOTO HOME**: moves toward the machine home position.
- **MACHINE POWER**: controls machine-enabled power state.
- **ESTOP**: a large green emergency-stop status/control area.

Several controls are dimmed, which visually indicates that the corresponding functions are currently unavailable or inactive.

### 1.7 Override sliders

Three tall vertical sliders occupy the lower center of the left section. Each slider has a **RESET** button above it:

- **RAPID: 100%**
- **FEED: 100%**
- **JOG: 38%**

The sliders provide manual override of rapid travel speed, programmed feed speed, and jog speed.

### 1.8 Status message

A message at the bottom-left reads:

> Can't turn machine ON until out of E-Stop

The message indicates that machine power is interlocked while the emergency-stop condition is active.

---

## 2. Center Area: Run & Monitor and Jog

### 2.1 Header tabs

The narrow center panel has two tabs:

- **RUN & MONITOR**: selected.
- **JOG**: alternate manual-motion controls.

### 2.2 Input and process-state indicators

The upper portion contains paired labels and circular status lamps. The indicators appear to report digital inputs, torch states, and plasma-process conditions.

Visible labels include:

- **PROBE**
- **UP/DOWN**, with two adjacent indicators
- **FLOAT**
- **OHMIC**
- **ARC-OK**
- **TORCH**
- **KERF CROSS**
- **CRNR LOCK**
- **THC ACTIVE**
- **CHG CON**
- **THC AUTO Vs**
- **MESH**

Filled yellow circles indicate active states; outlined circles indicate inactive states. In the captured screen, **OHMIC** and **THC AUTO Vs** appear active, while most other status lamps are outlined.

### 2.3 Torch-height and anti-dive controls

A group of four large buttons provides direct plasma-process controls:

- **TORCH ENABLE**
- **THC ENABLE**: highlighted.
- **VELOCITY ANTI DIVE**: highlighted.
- **VOID ANTI DIVE**: highlighted.

These controls relate to torch activation, torch-height control, and prevention of unwanted torch movement in specific cutting conditions.

### 2.4 Arc-voltage override

The panel displays:

- **ARC Voltage: 0.00**
- **OVERRIDE: 0 V**

Minus and plus buttons flank the voltage override value, allowing the operator to decrease or increase the override.

### 2.5 Operating mode selection

Three mode buttons are provided:

- **MANUAL**: selected.
- **MDI**
- **AUTO**

These correspond to manual operation, manual data input, and automatic program execution.

### 2.6 Program and torch utility controls

The lower portion contains paired utility buttons:

- **LOAD NEWEST FILE**
- **PULSE TORCH**
- **PIERCE ONLY**
- **DRY RUN**: highlighted.
- **EXAMPLE USER 1**
- **EXAMPLE USER 2**
- **LASER OFF**

Several blank button positions are also present, likely reserved for configurable or future user functions. The highlighted **DRY RUN** control suggests a non-cutting program test mode is selected.

---

## 3. Right Area: Tool Path and G-code Viewer

### 3.1 Header tabs

The large right section has two primary tabs:

- **TOOL PATH**: selected.
- **GCODE**: alternate program-text view.

### 3.2 View toolbar

A horizontal toolbar sits above the drawing viewport:

- **+**: zoom in.
- **-**: zoom out.
- **CENTER PLOT**: centers the drawing in the viewport.
- **CLEAR**: clears the displayed plot or trails.
- **PROG EXTENT**: fits the program extents to the view.
- **MACH EXTENT**: fits the machine extents to the view.
- **TRANSFORM**: applies or opens coordinate/view transformations.
- **SHOW TRAILS**: selected, enabling visible motion or tool trails.

### 3.3 Tool-path viewport

The central black viewport visualizes a cutting program. Visible geometry includes:

- A large rounded rectangular outer profile.
- Several circular holes or features.
- Multiple long rounded slots or internal contours.
- Thin pale-blue or violet outlines representing programmed geometry.
- Red diagonal lines representing displayed travel trails, linking feature locations.
- Short pale line segments near some circles, possibly approach, lead-in, lead-out, or orientation indicators.

The drawing extends close to the viewport boundaries, and portions of some paths approach or cross the visible right edge.

### 3.4 File controls

Three large buttons appear below the viewport:

- **OPEN**: opens a program or G-code file.
- **RELOAD**: reloads the current file.
- **RECENT**: accesses recently used files.

---

## 4. Bottom Navigation Bar

A persistent navigation strip spans the screen and provides access to the major application areas:

- **CONTROL & RUN**: selected and highlighted.
- **CUT & MATERIAL**
- **QUICKSHAPES**
- **SETTINGS**
- **DIAGNOSTICS**

This navigation separates normal machine operation from process setup, shape creation, configuration, and troubleshooting.

---

## 5. Visual and Interaction Design

- **Color coding:** Bright yellow identifies selected tabs, active buttons, values, labels, and borders. Darker controls appear inactive or unavailable. Green is used for the ESTOP area.
- **Panel hierarchy:** Thick outlined containers divide coordinate controls, machine controls, process monitoring, and visualization.
- **Touch-oriented layout:** Large rectangular buttons, wide spacing, and oversized coordinate values are suitable for an industrial touchscreen.
- **Immediate machine feedback:** Position, feed, velocity, process selection, override percentages, voltage, and status lamps remain visible on the primary operating screen.
- **Safety visibility:** The emergency-stop condition and the machine-power interlock message are displayed prominently near the main controls.

---

## Functional Layout Summary

| Area | Main purpose | Key functions |
|---|---|---|
| Left upper | Position and coordinate management | Select G54-G59, read X/Y/Z, home or zero axes |
| Left lower | Machine-cycle control | Start, hold, abort, park, frame job, move to zero/home, power and ESTOP |
| Left center | Speed overrides | Adjust and reset rapid, feed, and jog percentages |
| Center upper | Machine and plasma monitoring | View probe, ohmic, torch, arc, THC, anti-dive, and related states |
| Center middle | Plasma-process adjustment | Enable torch/THC, select anti-dive options, adjust arc-voltage override |
| Center lower | Operating and test modes | Select Manual/MDI/Auto, load files, pulse torch, pierce-only, dry run |
| Right upper | Viewer controls | Zoom, center, fit extents, transform, clear, and display trails |
| Right main | Program visualization | Inspect contours, holes, slots, cutting paths, and travel trails |
| Right lower | Program file handling | Open, reload, or select a recent file |
| Bottom bar | Application navigation | Control & Run, Cut & Material, Quickshapes, Settings, Diagnostics |
