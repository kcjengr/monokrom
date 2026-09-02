# Plasma Cut Parameters Screen Description

## Overview

The screenshot shows the **Cut & Material** section of a plasma cutting machine interface. The screen is a process-editing workspace used to select a cutting process, inspect or adjust its parameters, configure hole-processing behaviour, and view torch-height-control and sensing options.

The interface uses a near-black background with dark olive panels, bright yellow headers, borders, labels, input fields, and selection indicators. The layout is divided into four main columns:

1. **Process filters and file controls** on the left.
2. **General process parameters** in the centre-left.
3. **Hole-processing parameters and diagram** in the centre-right.
4. **THC, torch, and ohmic options** on the far right.

A persistent application-navigation bar runs along the bottom.

---

## 1. Top-level headers

The top of the screen contains three major headings:

- **CUT & PROCESS**: highlighted in yellow over the left section.
- **PROCESS EDITOR**: centred over the parameter-editing workspace.
- **STATISTICS**: displayed over the right side.

No statistical values or charts are visible beneath the **STATISTICS** heading in this screenshot. The visible far-right content is the **THC, TORCH & OHMIC** options panel.

---

## 2. Process Filters panel

The upper-left **PROCESS FILTERS** panel contains six dropdown selectors. Each field has a downward arrow at the right edge.

| Filter         | Selected value |
| -------------- | -------------- |
| **MATERIAL**   | `Generic`      |
| **THICKNESS**  | `8mm`          |
| **CONSUMABLE** | `Shielded`     |
| **OPERATION**  | `Cut`          |
| **GAS**        | `Air - Air`    |
| **QUALITY**    | `Production`   |

These selections define the displayed cutting-process configuration. The screenshot shows a generic 8 mm shielded air-plasma cutting process intended for production cutting.

---

## 3. Run Settings panel

The lower-left **RUN SETTINGS** panel contains four bordered action buttons:

- **SAVE**
- **RELOAD**
- **DELETE**
- **NEW**

The remainder of the panel is empty. The button labels indicate controls for managing process configurations, but the screenshot does not display additional instructions or saved-item listings.

---

## 4. Process Parameters panel

The centre-left **PROCESS PARAMETERS** panel displays the selected process identity and its main cutting values.

### 4.1 Process identification

- **PROCESS NAME:** `Auto Material 8mm`
- **PROCESS / CUTCHART / TOOL ID:** `99999`

### 4.2 Editable process values

Each numeric field is a yellow rectangular control with a circular minus button on the left and a circular plus button on the right.

| Parameter           | Displayed value |
| ------------------- | ---------------:|
| **KERF WIDTH**      | `1.500`         |
| **PIERCE HEIGHT**   | `10.00`         |
| **PIERCE DELAY**    | `0.30 S`        |
| **CUT HEIGHT**      | `10.00`         |
| **CUT FEED RATE**   | `900`           |
| **SETUP FEED RATE** | `100.00`        |
| **CUT AMPS**        | `40 A`          |
| **CUT VOLTS**       | `99 V`          |
| **P-JUMP HEIGHT**   | `0.00 %`        |
| **P-JUMP DELAY**    | `0.00 S`        |
| **PAUSE AT END**    | `0.00 S`        |
| **GAS PRESSURE**    | `90.00`         |

The screen does not display units beside kerf width, heights, feed rates, or gas pressure. Only values with visibly stated units are recorded with units above.

---

## 5. Holes and Hole Processing Instructions

The largest panel occupies the centre-right portion of the screen. A yellow header labelled **HOLES** covers the left portion of its top edge, while **Hole Processing Instructions** appears on the dark header area to the right.

### 5.1 Hole-processing checkboxes

Five square-option controls are visible across the upper portion:

- **ENABLE**
- **SMALL HOLE MARKING**
- **STRAIGHT LEADINS**
- **KERF ADJUSTED**
- **USE HIDEF IF AVAILABLE**

All five boxes appear empty in the screenshot.

### 5.2 Hole-size and lead-in values

Four adjustable fields appear beneath the checkboxes:

| Displayed value | Associated label or instruction                             |
| ---------------:| ----------------------------------------------------------- |
| `5`             | **Hole Size ratio relative to Material Thickness (x:1) \*** |
| `50.0000`       | **Maximum hole size to process \***                         |
| `3.0000`        | **Leadin Arc Radius**; `0 = Auto calculate leadin.`         |
| `3.5000`        | **Small hole threshold**                                    |

Each value uses the same minus/value/plus interaction pattern as the general process parameters.

### 5.3 Hole kerf width

A separate field on the right is labelled:

- **Hole Kerf Width**
- `0 = Use process kerf`

The displayed value is:

- `1.0000`

### 5.4 Feed-percentage controls

A heading of **% OF FEED** appears above a vertical group of five adjustable values. An **Adjustment** heading appears over a second column, which contains a value only for the overburn row.

| Path segment | % of feed | Adjustment     |
| ------------ | ---------:| --------------:|
| **LEAD-IN**  | `60.0 %`  | No value shown |
| **ARC 1**    | `60.0 %`  | No value shown |
| **ARC 2**    | `40.0 %`  | No value shown |
| **ARC 3**    | `100.0%`  | No value shown |
| **OVERBURN** | `100.0 %` | `0.0000`       |

All displayed values include minus and plus buttons.

### 5.5 Processing-comparison note

An asterisked note beside the feed controls states:

> The value used is the larger of the two supplied, once calculated and processing commences.

This note visually corresponds to the two earlier hole-size settings marked with asterisks.

---

## 6. Hole-processing diagram

A yellow circular diagram appears at the bottom of the hole-processing panel. The diagram illustrates the sequence and positions used when cutting a circular hole.

Visible diagram elements include:

- A large yellow circular cutting path.
- A smaller concentric circular guide or boundary.
- A radial **Lead-in** line extending upward from the centre to the top of the circle.
- A marked **Torch Off** position at approximately the 12 o'clock location.
- Direction arrows around the outer path.
- Labelled path regions: **Arc 1**, **Arc 2**, **Arc 3**, and **Overburn**.
- The overburn segment continues around the top area near the torch-off position.

The diagram visually links the feed-percentage rows to portions of the circular cutting path.

### Overburn explanatory text

The explanatory text beside the diagram reads:

> Overburn can push torch-off past 12 oclock position.

> Torch-off is at kerf size BEFORE 12 oclock. Overburn Adjustment shifts that position left for a positive value and right for a negative value.

The words **oclock** and **torch-off** are reproduced as displayed in the interface.

---

## 7. THC, Torch & Ohmic panel

The far-right **THC, TORCH & OHMIC** panel presents six checkbox-style settings. Selected items show a yellow square containing a dark check mark. The unselected item shows an empty outlined square.

| Setting                      | Visible state |
| ---------------------------- | ------------- |
| **THC ENABLED**              | Selected      |
| **THC AUTO VOLTS**           | Selected      |
| **THC (VELOCITY) ANTI-DIVE** | Selected      |
| **VOID ANTI DIVE**           | Selected      |
| **MESH SENSE**               | Not selected  |
| **OHMIC SENSE**              | Selected      |

THC is an abbreviation visible in the interface. The panel groups torch-height-control, anti-dive, mesh-sensing, and ohmic-sensing options.

---

## 8. Bottom navigation bar

A wide navigation bar spans the bottom of the screen:

- **CONTROL & RUN**
- **CUT & MATERIAL**
- **QUICKSHAPES**
- **SETTINGS**
- **DIAGNOSTICS**

**CUT & MATERIAL** is the active section and is displayed as a wide, filled yellow tab. The other sections appear as yellow text on the dark background.

---

## 9. Machine status message

A small message at the bottom-left edge reads:

> Can't turn machine ON until out of E-Stop

The message indicates that machine activation is blocked while the emergency-stop condition remains active.

---

## 10. Visual and interaction design

- **High-contrast presentation:** Yellow fields and labels are highly visible against the dark background.
- **Touch-oriented controls:** Large dropdowns, checkboxes, action buttons, and plus/minus controls support touchscreen interaction.
- **Consistent numeric editing:** Nearly every adjustable value uses the same minus/value/plus arrangement.
- **Logical grouping:** Filters, process values, hole-processing behaviour, and sensing options are separated by bordered panels.
- **State visibility:** Filled checkboxes clearly distinguish selected options from unselected options.
- **Contextual explanation:** Notes and the circular hole diagram explain how specialised hole settings relate to the cutting path.

---

## Functional layout summary

| Screen area         | Main purpose                         | Visible controls and information                                                                |
| ------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------- |
| Upper left          | Filter the active process            | Material, thickness, consumable, operation, gas, and quality dropdowns                          |
| Lower left          | Manage process records               | Save, reload, delete, and new                                                                   |
| Centre-left         | Edit general cut parameters          | Process identity, kerf, heights, delays, feed rates, amperage, voltage, pause, and gas pressure |
| Centre-right upper  | Configure hole processing            | Enable options, hole limits, arc radius, threshold, and hole kerf width                         |
| Centre-right middle | Adjust path-segment speeds           | Lead-in, Arc 1, Arc 2, Arc 3, and overburn feed percentages                                     |
| Centre-right lower  | Explain circular-hole processing     | Lead-in, torch-off, arcs, overburn, and adjustment diagram                                      |
| Far right           | Configure THC and sensing            | THC, auto volts, anti-dive, mesh sense, and ohmic sense                                         |
| Bottom              | Navigate between application modules | Control & Run, Cut & Material, Quickshapes, Settings, and Diagnostics                           |
| Bottom-left edge    | Display machine interlock status     | Emergency-stop warning                                                                          |
