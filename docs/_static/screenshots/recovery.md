# Plasma UI Cut Recovery Panel Description

## Scope

This description focuses on the **right quarter of the screenshot**, where the **Run & Monitor / Jog** area and the **Cut Recovery** controls are displayed. General machine controls visible elsewhere in the screenshot are outside the main scope.

## Overall layout

The right-side area is a tall, narrow panel with a dark olive-black background, bright yellow borders, and yellow text. The panel is divided into:

1. A two-tab header at the top.
2. A bordered **Cut Recovery** control group near the top.
3. A large unused dark area beneath the recovery group.

## 1. Header tabs

Two large tabs span the top of the right-side panel:

- **RUN & MONITOR**: dark background with yellow text.
- **JOG**: filled yellow with dark text.

The filled styling makes **JOG** appear to be the selected tab in the screenshot.

## 2. Cut Recovery panel

A bordered control group immediately below the tabs is headed **CUT RECOVERY**. The group contains controls for moving through or repositioning within a paused cut.

### 2.1 Reverse and Forward controls

Two rectangular buttons sit across the top of the group:

- **REVERSE** on the left.
- **FORWARD** on the right.

Both buttons have dark interiors, rounded yellow borders, and yellow labels.

Between the buttons is a vertical slider:

- The slider track is dark.
- A bright yellow handle is positioned around the middle of the track.
- No numeric value or scale is displayed.

The exact quantity controlled by the slider is not labelled in the screenshot.

### 2.2 Kerf movement controls

Below the slider is an eight-direction movement control arranged around the word **kerf**.

The available outlined arrow buttons point:

- Up.
- Down.
- Left.
- Right.
- Up-left.
- Up-right.
- Down-left.
- Down-right.

The arrows form a directional pad around the central **kerf** label. The arrangement provides movement choices along both machine axes and diagonals. The screenshot does not display a movement distance, step size, or coordinate value beside the arrows.

### 2.3 Cancel Movement

A wide button spans the bottom of the Cut Recovery group:

- **Cancel Movement**

The button has a dark interior, yellow rounded border, and centred yellow text. The label indicates cancellation of an active or requested recovery movement.

## 3. Panel state and visual presentation

- The **Cut Recovery** group is fully outlined in yellow and visually separated from the rest of the right-hand column.
- The bright yellow slider handle provides the strongest state indication inside the group.
- The directional arrows are outline-only graphics rather than filled buttons.
- No recovery coordinates, distance values, warning message, confirmation prompt, or path preview are shown within this section.
- The area below the recovery group is empty and retains the dark panel background.

## Functional summary

| Control                  | Visible role                                                                        |
| ------------------------ | ----------------------------------------------------------------------------------- |
| **RUN & MONITOR** tab    | Provides access to the monitoring view                                              |
| **JOG** tab              | Selected view containing the recovery controls                                      |
| **REVERSE**              | Requests movement backward through the cut-recovery sequence                        |
| **FORWARD**              | Requests movement forward through the cut-recovery sequence                         |
| Vertical slider          | Unlabelled adjustable recovery control                                              |
| Eight directional arrows | Reposition the recovery location in cardinal or diagonal directions around the kerf |
| **Cancel Movement**      | Cancels recovery movement                                                           |

## Relationship to the surrounding UI

The Cut Recovery panel appears while the main control area shows **CYCLE PAUSED**, connecting the recovery tools visually with a paused cutting operation. The right-side controls are isolated from the general cycle, power, emergency-stop, and override controls shown to the left.

This description records visible labels and layout. Functional wording beyond the labels is based only on the placement and conventional meaning of the displayed controls.
