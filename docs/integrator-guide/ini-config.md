# INI Configuration

The INI file defines the LinuxCNC machine configuration. MonoKrom Plasma uses a modified
INI format with additional sections for plasma-specific settings.

## Example INI File

The simulation config `plasmac_sim.ini` serves as a reference. Key sections are documented
below.

## Required Sections

### [EMC]

```ini
[EMC]
VERSION = 1.1
MACHINE = Monokrom Plasma - Metric XYZ
DEBUG = 0
```

| Parameter | Description |
|-----------|-------------|
| `VERSION` | INI file version (always 1.1) |
| `MACHINE` | Machine name (displayed in VCP title) |
| `DEBUG` | Debug level (0 = normal, higher = more verbose) |

### [DISPLAY]

```ini
[DISPLAY]
DISPLAY = monokrom_plasma
KEYBOARD_JOG = True
JET = True
CONFIRM_EXIT = False
FULLSCREEN = False
GCODE_SYNTAX = gcode_syntax.yml
LOG_FILE = sim.log
LOG_LEVEL = DEBUG
PREFERENCE_FILE = sim.pref
CONFIG_FILE = custom_config.yml
POSITION_OFFSET = RELATIVE
POSITION_FEEDBACK = ACTUAL
DEFAULT_LINEAR_VELOCITY = 50.0000
MAX_LINEAR_VELOCITY = 125.0000
MIN_LINEAR_VELOCITY = 0.5000
MAX_FEED_OVERRIDE = 2.000000
PROGRAM_PREFIX = ~/linuxcnc/nc_files
INCREMENTS = JOG 10mm 5mm 1mm 0.1mm
GEOMETRY = xyz
```

| Parameter | Description |
|-----------|-------------|
| `DISPLAY` | VCP to launch — `monokrom_plasma` (16:9, 1080p) |
| `KEYBOARD_JOG` | Enable keyboard jogging |
| `JET` | Enable VTK jet/spindle display |
| `CONFIRM_EXIT` | Require confirmation on exit |
| `FULLSCREEN` | Start in fullscreen mode |
| `GCODE_SYNTAX` | Syntax highlighting profile file |
| `LOG_FILE` | Log file name |
| `LOG_LEVEL` | Log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `PREFERENCE_FILE` | QtPyVCP preferences file name |
| `CONFIG_FILE` | QtPyVCP config.yml file |
| `POSITION_OFFSET` | Position display mode (RELATIVE or ABSOLUTE) |
| `POSITION_FEEDBACK` | Position feedback source (ACTUAL or COMMAND) |
| `DEFAULT_LINEAR_VELOCITY` | Default jog velocity |
| `MAX_LINEAR_VELOCITY` | Maximum jog velocity |
| `MIN_LINEAR_VELOCITY` | Minimum jog velocity |
| `MAX_FEED_OVERRIDE` | Maximum feed override multiplier |
| `PROGRAM_PREFIX` | Default directory for G-code files |
| `INCREMENTS` | Jog increment sizes |
| `GEOMETRY` | Axis geometry (xyz, xyza, etc.) |

### [VTK]

```ini
[VTK]
SPINDLE = jet_tracking_crosshair.stl
```

| Parameter | Description |
|-----------|-------------|
| `SPINDLE` | 3D model file for the spindle/jet display |

### [QTPLASMAC]

```ini
[QTPLASMAC]
MODE = 0
ESTOP_TYPE = 0
```

| Parameter | Description |
|-----------|-------------|
| `MODE` | Operating mode (0, 1, or 2) — see [Hardware Setup](hardware-setup.md) |
| `ESTOP_TYPE` | E-Stop behavior: 0 = indicator only, 1 = software controllable |

### [PLASMAC]

```ini
[PLASMAC]
DBOUNCE = TRUE
MACHINE = A120
PRESSURE = bar
DEFAULT_CUTCHART = 2
SLAT_TOP = -65.0
```

| Parameter | Description |
|-----------|-------------|
| `DBOUNCE` | Enable built-in debounce (TRUE/FALSE) |
| `MACHINE` | Plasma power source model name (for cut chart lookup) |
| `PRESSURE` | Pressure units (psi, bar, or MPa) |
| `DEFAULT_CUTCHART` | Default cut chart number |
| `SLAT_TOP` | Z position of slat top (for height calculations) |

### [FILTER]

```ini
[FILTER]
PROGRAM_EXTENSION = .ngc,.nc,.tap GCode File (*.ngc, *.nc, *.tap)
ngc = plasma_gcode_preprocessor
nc = plasma_gcode_preprocessor
tap = plasma_gcode_preprocessor
```

| Parameter | Description |
|-----------|-------------|
| `PROGRAM_EXTENSION` | File extensions accepted by the VCP |
| `ngc` / `nc` / `tap` | Preprocessor command for each extension |

### [RS274NGC]

```ini
[RS274NGC]
PARAMETER_FILE = sim.var
RS274NGC_STARTUP_CODE = o<metric_startup> call
SUBROUTINE_PATH = ./:./user_buttons:../../nc_files/subroutines
USER_M_PATH = ./:./plasmac
```

| Parameter | Description |
|-----------|-------------|
| `PARAMETER_FILE` | RS274/NGC parameter file (.var) |
| `RS274NGC_STARTUP_CODE` | Startup G-code (G21 for metric, G20 for imperial) |
| `SUBROUTINE_PATH` | Colon-separated paths for NGC subroutines |
| `USER_M_PATH` | Paths for user M-code handlers |

**Note:** For imperial configs, replace `G21` with `G20` in `RS274NGC_STARTUP_CODE`.

### [TASK]

```ini
[TASK]
TASK = milltask
CYCLE_TIME = 0.010
```

| Parameter | Description |
|-----------|-------------|
| `TASK` | Task module (always `milltask` for plasma) |
| `CYCLE_TIME` | Task cycle time in seconds |

### [EMCMOT]

```ini
[EMCMOT]
EMCMOT = motmod
COMM_TIMEOUT = 1.0
COMM_WAIT = 0.010
BASE_PERIOD = 100000
SERVO_PERIOD = 1000000
```

| Parameter | Description |
|-----------|-------------|
| `EMCMOT` | Motion module |
| `COMM_TIMEOUT` | Communication timeout (seconds) |
| `COMM_WAIT` | Communication wait time (seconds) |
| `BASE_PERIOD` | Base thread period (nanoseconds) |
| `SERVO_PERIOD` | Servo thread period (nanoseconds) |

### [HAL]

```ini
[HAL]
TWOPASS = ON
HALFILE = plasmac_sim_overlay.hal
HALFILE = qtplasmac_connections_sim.hal
HALUI = halui
HALFILE = ../common/hallib/core_sim_3.hal
HALFILE = ../common/hallib/spindle_sim.hal
HALFILE = ../common/hallib/simulated_home.hal
POSTGUI_HALFILE = postgui_call_list_plasmac_sim.hal
```

| Parameter | Description |
|-----------|-------------|
| `TWOPASS` | Enable two-pass HAL processing |
| `HALFILE` | HAL files to load (multiple entries allowed) |
| `HALUI` | HAL UI module (always `halui`) |
| `POSTGUI_HALFILE` | HAL file loaded after GUI initializes |

### [HALUI]

```ini
[HALUI]
MDI_COMMAND=(debug,macro0)
MDI_COMMAND=(debug,macro1)
MDI_COMMAND=G0X0Y0
...
```

| Parameter | Description |
|-----------|-------------|
| `MDI_COMMAND` | MDI commands accessible via HAL pins (for pendants, user buttons) |

### [KINS]

```ini
[KINS]
KINEMATICS = trivkins coordinates=XYZ
JOINTS = 3
```

| Parameter | Description |
|-----------|-------------|
| `KINEMATICS` | Kinematics module |
| `JOINTS` | Number of joints |

### [TRAJ]

```ini
[TRAJ]
AXES = 3
SPINDLES = 3
COORDINATES = XYZ
LINEAR_UNITS = mm
ANGULAR_UNITS = degree
DEFAULT_LINEAR_VELOCITY = 100
MAX_LINEAR_VELOCITY = 350
DEFAULT_LINEAR_ACCELERATION = 2500
MAX_LINEAR_ACCELERATION = 2500
NO_FORCE_HOMING = 1
```

| Parameter | Description |
|-----------|-------------|
| `AXES` | Number of axes |
| `SPINDLES` | Number of spindles (3 for plasma: main, THC, offset) |
| `COORDINATES` | Axis names |
| `LINEAR_UNITS` | Units (mm or inches) |
| `ANGULAR_UNITS` | Angular units (degree) |
| `DEFAULT_LINEAR_VELOCITY` | Default linear velocity |
| `MAX_LINEAR_VELOCITY` | Maximum linear velocity |
| `DEFAULT_LINEAR_ACCELERATION` | Default acceleration |
| `MAX_LINEAR_ACCELERATION` | Maximum acceleration |
| `NO_FORCE_HOMING` | Skip forced homing (1 = yes) |

### Axis Sections ([AXIS_X], [AXIS_Y], [AXIS_Z])

```ini
[AXIS_X]
MIN_LIMIT = -2.001
MAX_LIMIT = 1200.001
MAX_VELOCITY = 500.0
MAX_ACCELERATION = 5000.0
OFFSET_AV_RATIO = 0.5
```

| Parameter | Description |
|-----------|-------------|
| `MIN_LIMIT` | Minimum axis limit |
| `MAX_LIMIT` | Maximum axis limit |
| `MAX_VELOCITY` | Maximum velocity (should be double the joint value) |
| `MAX_ACCELERATION` | Maximum acceleration (should be double the joint value) |
| `OFFSET_AV_RATIO` | Offset/velocity ratio for external offsets (always 0.5) |

### Joint Sections ([JOINT_0], [JOINT_1], [JOINT_2])

```ini
[JOINT_0]
MIN_LIMIT = -2.001
MAX_LIMIT = 1200.001
MAX_VELOCITY = 250
MAX_ACCELERATION = 2500
TYPE = LINEAR
HOME = 0.000
HOME_OFFSET = 0.0
HOME_SEQUENCE = 1
HOME_USE_INDEX = NO
HOME_SEARCH_VEL = 1.0
HOME_LATCH_VEL = 0.1
HOME_IGNORE_LIMITS = NO
HOME_IS_SHARED = 1
```

| Parameter | Description |
|-----------|-------------|
| `MIN_LIMIT` / `MAX_LIMIT` | Joint limits |
| `MAX_VELOCITY` / `MAX_ACCELERATION` | Joint max velocity/acceleration |
| `TYPE` | Joint type (LINEAR or ANGULAR) |
| `HOME` | Home position |
| `HOME_OFFSET` | Offset from home switch to reference |
| `HOME_SEQUENCE` | Homing order (0 = Z first, then X/Y) |
| `HOME_USE_INDEX` | Use index mark for homing |
| `HOME_SEARCH_VEL` | Search velocity during homing |
| `HOME_LATCH_VEL` | Latch velocity during homing |
| `HOME_IGNORE_LIMITS` | Ignore limits during homing |
| `HOME_IS_SHARED` | Shared home (true for XYZ on same axis) |

### [EMCIO]

```ini
[EMCIO]
EMCIO = io
CYCLE_TIME = 0.100
DB_PROGRAM = /path/to/plasma_tooldbpipe
```

| Parameter | Description |
|-----------|-------------|
| `EMCIO` | IO control module |
| `CYCLE_TIME` | IO cycle time |
| `DB_PROGRAM` | Plasma tool database pipe program |

## User Button Configuration

User buttons are configured in the `[DISPLAY]` section:

```ini
USER1_NAME=EXAMPLE USER 1
USER1_ACTION=testfn1.ngc
USER2_NAME=EXAMPLE USER 2
USER2_ACTION=testfn2.ngc
USER3_NAME=LASER OFF
USER3_ACTION=laser_off.ngc
```

| Parameter | Description |
|-----------|-------------|
| `USER<n>_NAME` | Display name for the button |
| `USER<n>_ACTION` | NGC subroutine to execute |

Up to 10 user buttons (USER1-USER10) are supported. See [User Buttons](user-buttons.md) for details.

## Customizing the INI File

### Creating a New Configuration

1. Copy the simulation config as a starting point:
   ```bash
   cp ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini \
      ~/linuxcnc/configs/my_machine/my_machine.ini
   ```

2. Edit the INI file:
   - Update `MACHINE` name
   - Adjust axis limits and velocities for your machine
   - Configure operating mode
   - Set up HAL files

3. Create corresponding HAL files (see [HAL Connections](hal-connections.md)).

4. Test with the simulator before connecting to real hardware.
