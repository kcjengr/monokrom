# User Buttons

User Buttons provide quick access to custom NGC subroutines from the Main Tab. Up to 10
user buttons (USER1-USER10) can be configured.

## Configuration

User buttons are configured in the INI file's `[DISPLAY]` section:

```ini
[DISPLAY]
USER1_NAME=EXAMPLE USER 1
USER1_ACTION=testfn1.ngc
USER2_NAME=EXAMPLE USER 2
USER2_ACTION=testfn2.ngc
USER3_NAME=LASER OFF
USER3_ACTION=laser_off.ngc
# USER4 through USER10 can be added similarly
```

| Parameter | Description |
|-----------|-------------|
| `USER<n>_NAME` | Display name shown on the button |
| `USER<n>_ACTION` | NGC subroutine filename to execute |

## Example User Buttons (from sim config)

```ini
USER1_NAME=EXAMPLE USER 1
USER1_ACTION=testfn1.ngc
USER2_NAME=EXAMPLE USER 2
USER2_ACTION=testfn2.ngc
USER3_NAME=LASER OFF
USER3_ACTION=laser_off.ngc
```

## User Button Subroutines

User button subroutines are NGC files located in the subroutine path:

```ini
[RS274NGC]
SUBROUTINE_PATH = ./:./user_buttons:../../nc_files/subroutines
```

### Example: `user_buttons/park.ngc`

Parks the gantry to a safe position:

```ngc
; Park gantry to X-min+1, Y-max-1
G90
G0 X[#<_x_min> + 1] Y[#<_y_max> - 1]
```

### Example: `user_buttons/single_cut.ngc`

Performs a single cut at a fixed distance from the current point:

```ngc
; Single cut subroutine
; Requires: #1 = distance, #2 = feed rate
G91
G1 X[#1] F[#2]
G90
```

### Example: `user_buttons/laser_off.ngc`

Turns off the laser pointer:

```ngc
; Laser off subroutine
o<laser_off> sub
#100 = 0  ; Laser off
#<_laser_on> = #100
o<laser_off> endsub
```

## Creating Custom User Buttons

### Step 1: Create the NGC Subroutine

Create a new file in the `user_buttons/` directory:

```ngc
; user_buttons/my_custom_action.ngc
; Description: My custom action
; Author: Your Name

o<my_custom_action> sub

; Your G-code here
G0 Z50
G0 X100 Y100
o<my_custom_action> endsub
```

### Step 2: Configure the INI File

Add the user button configuration:

```ini
[DISPLAY]
USER4_NAME=MY CUSTOM ACTION
USER4_ACTION=my_custom_action.ngc
```

### Step 3: Test

1. Restart LinuxCNC.
2. Verify the button appears on the Main Tab.
3. Click the button to execute the subroutine.

## User Button Limitations

- User buttons execute NGC subroutines, not arbitrary G-code.
- Subroutines must use the `o<name> sub ... o<name> endsub` format.
- User buttons cannot accept parameters directly (use global variables or MDI).
- Long-running subroutines may block the VCP UI.

## Advanced: User Buttons with Parameters

For parameterized user buttons, use global variables:

```ini
; Set a variable before pressing the user button
[HALUI]
MDI_COMMAND=G10 L20 P0 X100  ; Set X position
```

```ngc
; user_buttons/position_to_x.ngc
o<position_to_x> sub
G90
G0 X[#<_x_pos>]
o<position_to_x> endsub
```

## User Buttons and HAL

User buttons can also trigger HAL MDI commands:

```ini
[DISPLAY]
USER5_NAME=HOME ALL
USER5_ACTION=halui.home-all.ngc
```

```ngc
; user_buttons/halui.home-all.ngc
; This file contains HAL MDI commands
o<halui_home_all> sub
; The halui module handles the actual homing
o<halui_home_all> endsub
```

## Troubleshooting User Buttons

| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| Button doesn't appear | Not configured in INI | Add USER<n>_NAME and USER<n>_ACTION |
| Subroutine not found | Wrong path or filename | Check SUBROUTINE_PATH in INI |
| Subroutine errors | NGC syntax error | Verify `o<name> sub` / `o<name> endsub` format |
| Button does nothing | Subroutine is empty | Add G-code commands to subroutine |
