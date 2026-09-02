# Quickshapes Plasma Conversational Screen Description

## Overview

The screenshot shows the **Quickshapes** conversational programming screen for a plasma cutting interface. The screen uses a high-contrast industrial theme with a near-black background, dark olive panels, bright yellow controls and labels, pale blue geometry, and red tool-movement lines.

The interface is arranged into four principal areas:

1. A **shape-selection palette** on the far left.
2. A **parameter-entry and shape-reference area** in the centre-left.
3. A large **generated tool-path preview** on the right.
4. A persistent **application navigation bar** along the bottom.

The selected example is a circular flange or ring with four circular holes distributed around a pitch circle.

---

## 1. Shape-selection palette

A tall bordered panel on the far left contains a two-column grid of large icon buttons. Each icon represents a predefined shape or profile that can be selected for conversational part creation.

The visible icons, read from top to bottom and left to right, depict:

1. Circle or circular plate.
2. Rectangle.
3. Ring or annulus.
4. Rounded-top rectangular profile.
5. Tapered lug with a circular hole.
6. U-shaped or elongated slot profile.
7. Circular flange with four holes.
8. Rectangular profile with a concave curved top edge.
9. Oval or two-bolt flange profile.
10. Rectangular plate with four corner holes.
11. L-shaped profile.
12. Right-triangle profile.
13. Trapezoidal profile.
14. Tapered or chamfered rectangular profile.

The **four-hole circular flange** icon appears to correspond to the parameters and previews currently displayed.

---

## 2. Parameter-entry area

The upper centre-left area contains the editable dimensions and options for the selected shape. Labels appear in yellow on the left, with bright yellow value fields to the right.

Each numeric field includes:

- A circular **minus** button on the left.
- A displayed numeric value in the centre.
- A circular **plus** button on the right.

These controls indicate incremental adjustment of each parameter.

### Visible parameters

| Parameter | Displayed value | Visual meaning in the reference diagram |
|---|---:|---|
| **OD** | `100.0000` | Outer diameter of the circular part |
| **PCD** | `76.0000` | Pitch-circle diameter on which the holes are positioned |
| **Num Holes** | `4` | Number of repeated holes around the pitch circle |
| **hd** | `12.0000` | Hole diameter |
| **Hole style** | `Round` | Shape style selected for the holes |
| **ID** | `45.0000` | Inner diameter of the central opening |

### Hole-style selector

The **Hole style** control is a dropdown field. The displayed selection is **Round**, with a downward arrow at the right edge of the field.

---

## 3. Dimension reference diagram

A large instructional diagram occupies the lower centre-left area. The diagram explains how the entered parameters relate to the selected flange geometry.

### Diagram contents

- A thick yellow outer ring represents the circular part and its outer boundary.
- A thick yellow inner ring represents the central circular opening.
- Four small yellow circular holes are placed at the top, right, bottom, and left positions.
- A red dashed circle passes through the centres of the four holes and represents the pitch circle.
- Red centre marks are visible inside the holes.
- A cyan diagonal dimension line is associated with **OD**.
- A red diagonal dimension line is associated with **ID**.
- The **PCD** label is positioned beside the dashed pitch circle.
- The **hd** label appears beneath the bottom hole, with red dashed extension lines indicating the hole width.

Large yellow labels identify **OD**, **PCD**, **ID**, and **hd** directly on the graphic. The diagram acts as a visual guide for the parameter fields rather than as the final cutting preview.

### Refresh control

A wide bordered **Refresh** button appears below the reference diagram. The button likely requests regeneration or updating of the displayed geometry after parameter changes. This function is inferred from the button label and placement.

---

## 4. Generated tool-path preview

The right half of the screen contains a large black plotting viewport enclosed by the main panel border. The viewport displays the geometry generated from the current Quickshapes parameters.

### Geometry displayed

The pale blue or violet outlines show:

- One large circular outer boundary.
- One concentric circular inner opening.
- Four smaller circular holes arranged evenly around the centre.

The four holes are positioned approximately at the top, right, bottom, and left locations, matching the four-hole reference diagram.

### Tool movement and lead geometry

Red line segments connect points near the circular features. The red lines form a sequence between the holes and include a long diagonal segment extending toward the lower-left area. Short pale line segments are visible near several circular profiles.

The red lines appear to represent non-cutting travel or linking movement, while the short pale segments may represent entry or exit geometry. The screenshot does not provide an on-screen legend, so these interpretations are based on the visual conventions used in the plot.

### Plot axes

The plot includes visible horizontal and vertical axes:

- The vertical axis is labelled **Y**.
- The bottom axis has numeric markings from approximately `0.000` to `101.491`.
- The left axis also shows values from approximately `0.000` to `101.491`.
- A midpoint value of approximately `50.746` is visible on both axes.

The plotted circular part nearly fills the available coordinate range.

---

## 5. Processing and kerf controls

Below the plot is a compact settings area.

### Smart Hole Processing Active

The label **Smart Hole Processing Active** appears beside a circular status indicator. The indicator is shown as an outlined yellow circle rather than a filled circle.

### Internal Kerf

The **Internal Kerf** setting provides:

- A minus button.
- A numeric value of `0.0000`.
- A plus button.

A note below the field reads:

> Internal Kerf = 0 will default to using material kerf from Cur Process.

This indicates that a zero internal-kerf override uses the kerf value associated with the current cutting process.

---

## 6. Bottom navigation bar

A persistent navigation strip spans the bottom of the screen. The available sections are:

- **CONTROL & RUN**
- **CUT & MATERIAL**
- **QUICKSHAPES**
- **SETTINGS**
- **DIAGNOSTICS**

**QUICKSHAPES** is the active section and is highlighted with a wide bright yellow tab. The other navigation items appear as yellow text on the dark background.

---

## 7. Machine status message

A small status message appears at the bottom-left edge of the screen:

> Can't turn machine ON until out of E-Stop

The message shows that machine activation is currently blocked by an emergency-stop condition.

---

## 8. Visual and interaction design

- **High contrast:** Bright yellow controls stand out strongly against the dark background.
- **Touch-oriented controls:** Large shape icons and wide parameter controls are suitable for touchscreen use.
- **Conversational workflow:** The operator selects a standard shape, adjusts named dimensions, reviews a dimension guide, and inspects the generated cutting path.
- **Immediate visual feedback:** The reference diagram explains each dimension while the plot shows the resulting geometry and path.
- **Consistent selection state:** The active Quickshapes navigation tab is filled yellow, while inactive navigation items remain unfilled.
- **Grouped layout:** Borders clearly separate shape selection, parameter configuration, reference graphics, and tool-path output.

---

## Functional layout summary

| Screen area | Main purpose | Visible functions |
|---|---|---|
| Far-left palette | Select a standard conversational shape | Fourteen profile icons including circles, rectangles, flanges, slots, triangles, and custom profiles |
| Upper centre-left | Enter shape dimensions | Adjust OD, PCD, hole count, hole diameter, hole style, and ID |
| Lower centre-left | Explain parameter meanings | Labelled flange diagram and Refresh button |
| Right plot | Preview generated geometry and path | Displays outer profile, inner opening, four holes, axes, and movement lines |
| Below plot | Configure hole and kerf processing | Smart-hole status and internal-kerf adjustment |
| Bottom navigation | Move between application modules | Control & Run, Cut & Material, Quickshapes, Settings, and Diagnostics |
| Bottom-left status | Show machine interlock information | Emergency-stop warning message |

---

## Typical screen workflow suggested by the layout

1. Select a predefined shape from the left palette.
2. Adjust the dimensional values using the minus and plus controls.
3. Select the required hole style from the dropdown.
4. Use the dimension reference graphic to verify the meaning of each field.
5. Select **Refresh** to update the generated shape.
6. Review the resulting geometry and movement lines in the plot.
7. Adjust internal kerf or smart-hole processing settings where required.

The sequence above is an interpretation of the visual arrangement and labels; the screenshot does not display explicit operating instructions.
