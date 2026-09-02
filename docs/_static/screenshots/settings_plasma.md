# Plasma CNC Settings Screen Description

## Overview

The screenshot shows the **Settings** section of a plasma CNC user interface, specifically the **THC / ARC / PROBE & MARKING** page. The page presents configuration values for torch height control, arc behaviour, probing and motion, and scribe or spot operations.

The interface uses a near-black background with dark olive panels and bright yellow headers, borders, labels, buttons, and value fields. Most editable values use a consistent control made up of a minus button, a central value, and a plus button.

The screen is divided into four principal parameter panels:

1. **THC** in the upper-left.
2. **ARC** in the upper-right.
3. **PROBING & MOTION** in the lower-left.
4. **SCRIBE & SPOT** in the lower-right.

A large unused dark area fills the lower portion of the page, while the application navigation bar runs along the bottom.

---

## 1. Page tabs

Two large tabs span the top of the settings workspace:

- **THC / ARC / PROBE & MARKING**: filled yellow and visually selected.
- **MACHINE**: dark background with yellow text and border.

The selected tab corresponds to the parameter groups displayed below it.

---

## 2. THC panel

The upper-left panel is headed **THC**. The panel contains torch height control values arranged in two columns.

### Left column

| Parameter | Displayed value |
|---|---:|
| **DELAY** | `0.50 S` |
| **THRESHOLD** | `1.00 V` |
| **PID P GAIN (SPEED)** | `10` |
| **PID I GAIN** | `0` |
| **PID D GAIN** | `0` |

### Right column

| Parameter | Displayed value |
|---|---:|
| **VAD THRESHOLD** | `60 %` |
| **VOID OVERRIDE** | `100 %` |
| **SAFE HEIGHT** | `25` |
| **MAX THC FEED RATE** | `7200.0` |

The **MAX THC FEED RATE** value is shown as yellow text without the surrounding minus/value/plus control used by the other values.

Several minus buttons appear muted compared with the other controls, particularly beside the zero-valued PID gain fields. This is a visible styling difference; the screenshot does not state whether the controls are disabled or at a minimum value.

---

## 3. ARC panel

The upper-right panel is headed **ARC**. Arc-related parameters are split into a main left column and a smaller right column.

### Left column

| Parameter | Displayed value |
|---|---:|
| **FAIL TIMEOUT** | `3.00 S` |
| **MAX. STARTS** | `3` |
| **RETRY DELAY** | `60 S` |
| **VOLTAGE SCALE** | `0.006744 V` |
| **VOLTAGE OFFSET** | `3687.500 V` |

### Right column

| Parameter | Displayed value |
|---|---:|
| **HEIGHT PER VOLT** | `0.100` |
| **OK HIGH VOLTS** | `250.00 V` |
| **OK LOW VOLTS** | `60.00 V` |

Each displayed arc value uses a yellow minus/value/plus control. The minus button beside **Height per Volt** is visibly muted, as is the plus button beside **OK Low Volts**.

---

## 4. Probing & Motion panel

The lower-left panel is headed **PROBING & MOTION**. Values are arranged in two columns, with a **PROBE TEST** button at the lower-right of the panel.

### Left column

| Parameter | Displayed value |
|---|---:|
| **FLOAT TRAVEL** | `3.20` |
| **PROBE SPEED** | `200` |
| **PROBE HEIGHT** | `15.00` |
| **OHMIC PROBE OFFSET** | `0.000` |

### Right column

| Parameter | Displayed value |
|---|---:|
| **OHMIC RETRIES** | `3` |
| **SKIP IHS** | `0` |
| **SETUP SPEED (units per min)** | `3000` |

### Probe Test control

A wide, dark button with a yellow border is labelled **PROBE TEST**. The screenshot does not show test results, instructions, or a status indicator beside the button.

The minus button for **SKIP IHS** appears muted. Units are not displayed beside most values, except for the wording included in the **Setup Speed (units per min)** label.

---

## 5. Scribe & Spot panel

The lower-right panel is headed **SCRIBE & SPOT**. The panel contains two scribe timing values on the left and two spot-operation values on the right.

### Scribe values

| Parameter | Displayed value |
|---|---:|
| **SCRIBE ARM DELAY** | `0.0 S` |
| **SCRIBE ON DELAY** | `0.3 S` |

### Spot values

| Parameter | Displayed value |
|---|---:|
| **SPOT THRESHOLD** | `0 V` |
| **SPOT DELAY** | `600 ms` |

The minus buttons beside **Scribe Arm Delay** and **Spot Threshold** appear muted. All four values retain visible plus controls.

---

## 6. Numeric control pattern

Most editable parameters use the same visual arrangement:

- A circular **minus** button on the left.
- A bold numeric value in the centre.
- A circular **plus** button on the right.
- A bright yellow rounded rectangle surrounding the complete control.

The repeated pattern makes numeric settings visually consistent across THC, arc, probing, motion, scribe, and spot sections.

---

## 7. Empty workspace

A large dark area extends beneath the four parameter panels. No additional controls, diagrams, messages, tables, or values are visible in this area.

---

## 8. Bottom navigation bar

A persistent navigation bar spans the bottom of the application:

- **CONTROL & RUN**
- **CUT & MATERIAL**
- **QUICKSHAPES**
- **SETTINGS**
- **DIAGNOSTICS**

**SETTINGS** is the active module and appears as a wide, filled yellow tab. The other module names are shown as yellow text on the dark background.

---

## 9. Machine status message

A small status message is visible at the bottom-left edge:

> Can't turn machine ON until out of E-Stop

The message states that machine activation is blocked while the emergency-stop condition remains active.

---

## 10. Visual design and visible states

- **High contrast:** Yellow controls and labels stand out against the near-black background.
- **Panel hierarchy:** Bright yellow headers and borders clearly separate the four parameter groups.
- **Touch-oriented controls:** Large plus and minus buttons support direct touchscreen adjustment.
- **Consistent alignment:** Labels are left-aligned and values are arranged in vertical columns.
- **Selected navigation:** Filled yellow tabs identify the open settings page and application module.
- **Muted controls:** Some minus or plus buttons use a duller yellow tone than surrounding controls. The screenshot does not explicitly define the meaning of this state.
- **Sparse lower area:** The lower half of the settings workspace is mostly empty.

---

## Functional layout summary

| Screen area | Main purpose | Visible settings and controls |
|---|---|---|
| Top tabs | Select the settings category | THC / Arc / Probe & Marking; Machine |
| Upper-left | Configure THC values | Delay, threshold, PID gains, VAD threshold, void override, safe height, and maximum THC feed rate |
| Upper-right | Configure arc parameters | Timeouts, starts, retry delay, voltage scale and offset, height per volt, and acceptable voltage limits |
| Lower-left | Configure probing and motion | Float travel, probe speed and height, ohmic offset and retries, Skip IHS, setup speed, and Probe Test |
| Lower-right | Configure scribe and spot timing | Scribe arm delay, scribe-on delay, spot threshold, and spot delay |
| Bottom navigation | Move between application modules | Control & Run, Cut & Material, Quickshapes, Settings, and Diagnostics |
| Bottom-left edge | Display the machine interlock state | Emergency-stop warning |

---

## Captured screen state

The screenshot records the following visible state:

- **THC / ARC / PROBE & MARKING** is the selected settings page.
- **SETTINGS** is the selected application module.
- All four parameter panels contain populated values.
- No dialog, keyboard, validation warning, or test result is open.
- The machine cannot be turned on because the interface reports an E-Stop condition.

This document describes the visible layout, labels, values, and control states. It does not prescribe safe operating values or machine-adjustment procedures.
