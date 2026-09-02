# Config YAML

MonoKrom Plasma uses a YAML configuration file (`config.yml`) for QtPyVCP settings. This
file defines data plugins, windows, dialogs, and persistent settings.

## Config File Location

The config file is specified in the INI file:

```ini
[DISPLAY]
CONFIG_FILE = custom_config.yml
```

The simulation config uses:
```ini
CONFIG_FILE = custom_config.yml
```

Which resolves to:
```
~/linuxcnc/configs/sim.monokrom/plasmac/custom_config.yml
```

## Custom Config

The `custom_config.yml` file overrides specific settings from the main `config.yml`:

```yaml
# Override file locations
file_locations:
  kwargs:
    local_locations:
      NC Files: ~/linuxcnc/nc_files
```

## Main Config Structure

The main `config.yml` is located at:
```
src/monokrom/src/monokrom/plasma/config.yml
```

### VCP Information

```yaml
vcp:
  name: MonoKrom Plasma
  version: v0.0.5
  author: Kurt Jacobson, James Walker
  description: >
    Plasma UI leveraging the qtpyvcp plasma processes plugin.
```

### Data Plugins

#### Status Plugin

```yaml
data_plugins:
  status:
    kwargs:
      cycle_time: 50  # 50ms update cycle
```

#### Persistent Data Manager

```yaml
persistent_data_manager:
  provider: qtpyvcp.plugins.persistent_data_manager:PersistentDataManager
  kwargs:
    serialization_method: pickle
```

Settings are serialized as pickle files and stored in the machine configuration directory.

#### Plasma Processes Plugin

```yaml
plasmaprocesses:
  provider: qtpyvcp.plugins.plasma_processes:PlasmaProcesses
  kwargs:
    db_type: "sqlite"
```

This plugin provides the SQLite-backed plasma process database. It requires the forked
qtpyvcp branch (`plasma_db`).

#### File Locations Plugin

```yaml
file_locations:
  provider: qtpyvcp.plugins.file_locations:FileLocations
  kwargs:
    default_location: NC Files
    local_locations:
      Home: ~/
      Desktop: ~/Desktop
      NC Files: ~/linuxcnc/nc_files
```

### Windows

#### Main Window

```yaml
windows:
  mainwindow:
    provider: monokrom.plasma.mainwindow:MainWindow
    kwargs:
      menu: null
      ui_file: {{ file.dir }}/mainwindow.ui
      stylesheet: {{ file.dir }}/../common/monokrom.qss
      title: ( vcp.name ) ( vcp.version)
```

| Parameter | Description |
|-----------|-------------|
| `provider` | Python class for the main window |
| `ui_file` | Qt Designer UI file path |
| `stylesheet` | QSS stylesheet path |
| `title` | Window title (uses Jinja2 template) |

### Dialogs

#### Open File Dialog

```yaml
dialogs:
  open_file:
    provider: monokrom.common.widgets.input_overlay:MkInputOverlay
    kwargs:
      ui_file: {{ file.dir}}/../common/widgets/file_chooser.ui
```

#### Recent Files Dialog

```yaml
recent_files:
  provider: monokrom.common.widgets.input_overlay:MkInputOverlay
  kwargs:
    ui_file: {{ file.dir}}/../common/widgets/recent_file_chooser.ui
```

#### New Process Dialog

```yaml
new_process:
  provider: monokrom.common.widgets.input_overlay:MkInputOverlay
  kwargs:
    ui_file: {{ file.dir }}/new_process.ui
```

### G-code Editor Styling

```yaml
gcode_editor:
  kwargs:
    background: "#16160e"
    text_color: "#ffee06"
    current_line_color: "#ffee06"
    current_line_background: "#16160e"
    font_family: "Noto Sans Mono"
    font_size: 11
    line_number_color: "#ffee06"
    line_number_background: "#505050"
```

### G-code Syntax Profile

```yaml
gcode_syntax:
  version: 1
  flat-token-groups: true
  styles:
    - name: gcode
      color: "#ffee06"
    - name: mcode
      color: "#ffee06"
    - name: axis
      color: "#ffee06"
    - name: number
      color: "#ffee06"
    - name: operator
      color: "#ffee06"
    - name: comment
      color: "#ffee06"
    - name: string
      color: "#ffee06"
```

## Persistent Settings

MonoKrom Plasma defines over 110 persistent settings that are saved to the `.prefs` file.
These are organized into categories:

### THC Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `thc_delay` | 0.5 | THC enable delay (seconds) |
| `thc_threshold` | 1.0 | THC voltage threshold (V) |
| `thc_pid_p_gain` | 10.0 | THC proportional gain |
| `thc_pid_i_gain` | 0.0 | THC integral gain |
| `thc_pid_d_gain` | 0.0 | THC derivative gain |
| `thc_enabled` | true | THC enabled flag |
| `thc_feed_rate` | 3000.0 | THC feed rate (mm/min) |
| `thc_vad_threshold` | 60.0 | VAD detection threshold (V) |
| `thc_void_override` | 99 | VAD void retraction override |
| `thc_safe_height` | 40.0 | Minimum Z height during cutting |
| `height_per_volt` | 0.100 | Z movement per volt calibration |
| `plasma_vad` | true | VAD enabled |
| `plasma_void_sense` | true | Void sensing enabled |
| `plasma_mesh_sense` | false | Mesh mode enabled |
| `corner_lock` | false | Corner lock enabled |
| `plasma_auto_volts` | true | Auto volts mode |

### Probe Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `probe_float_travel` | 3.2 | Float switch travel distance (mm) |
| `probe_speed` | 300 | Probe feed rate (mm/min) |
| `probe_height` | 14.0 | Target height after probing (mm) |
| `probe_offset` | -0.5 | Additional probe offset (mm) |
| `ohmic_sensing_enabled` | false | Ohmic probe enabled |
| `probe_ohmic_retries` | 3 | Number of ohmic probe retries |
| `probe_skip_ihs` | 0.0 | Skip initial height search distance |
| `probe_setup_speed` | 3000 | Probe setup approach speed (mm/min) |

### Arc Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `arc_fail_timeout` | 3.0 | Arc fail timeout (seconds) |
| `arc_max_starts` | 3 | Max arc start attempts |
| `arc_retry_delay` | 5.0 | Delay between arc retries (seconds) |
| `arc_ok_high_volts` | 250.0 | Arc OK high voltage threshold (V) |
| `arc_ok_low_volts` | 60.0 | Arc OK low voltage threshold (V) |
| `puddle_jump_height` | 0.0 | Puddle jump retraction height |
| `puddle_jump_delay` | 0.0 | Puddle jump delay (seconds) |
| `plasma_torch_pulse_sec` | 1.0 | Torch pulse duration (seconds) |
| `pause_at_end` | false | Pause at end of cut |
| `arc_voltage_scale` | 0.006744 | Arc voltage scale calibration |
| `arc_voltage_offset` | 3687.5 | Arc voltage offset calibration |
| `arc_height_per_volt` | 0.100 | Arc height per volt calibration |

### Scribe Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `scribe_arm_delay` | 0.0 | Scribe arming delay (seconds) |
| `scribe_on_delay` | 0.3 | Scribe on delay (seconds) |

### Spot Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `spot_threshold` | 5.0 | Spot detection threshold |
| `spot_delay` | 100.0 | Spot delay (seconds) |

### Plasma Cut Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `plasma_hole_thickness_ratio` | 5 | Hole detection thickness ratio |
| `plasma_max_hole_size` | 50.0 | Maximum hole size for through-cut (mm) |
| `plasma_hole_detect_enable` | true | Hole detection enabled |
| `plasma_arc1_percent` | 60.0 | Arc 1 power percentage |
| `plasma_arc1_distance` | 80.0 | Arc 1 distance |
| `plasma_arc2_percent` | 40.0 | Arc 2 power percentage |
| `plasma_arc2_distance` | 20.0 | Arc 2 distance |
| `plasma_arc3_percent` | 100.0 | Arc 3 power percentage |
| `plasma_arc3_distance` | 20.0 | Arc 3 distance |
| `plasma_overburn_percent` | 100.0 | Overburn percentage |
| `plasma_leadin_percent` | 60.0 | Lead-in percentage |
| `plasma_leadin_radius` | 3.0 | Lead-in radius |
| `plasma_small_hole_detect` | false | Small hole detection enabled |
| `plasma_force_straight_leadin` | false | Straight lead-in for small holes |
| `plasma_small_hole_threshold` | 3.5 | Small hole threshold |
| `plasma_hole_kerf` | 0.0 | Small hole kerf compensation |
| `plasma_use_hidef` | false | High definition mode enabled |

### Offset Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `laser_offset_x` | 0.0 | Laser pointer X offset |
| `laser_offset_y` | 0.0 | Laser pointer Y offset |
| `camera_offset_x` | 0.0 | Camera X offset |
| `camera_offset_y` | 0.0 | Camera Y offset |
| `scribe_offset_x` | 0.0 | Scribe X offset |
| `scribe_offset_y` | 0.0 | Scribe Y offset |
| `ohmic_offset_x` | 0.0 | Ohmic probe X offset |
| `ohmic_offset_y` | 0.0 | Ohmic probe Y offset |

### Consumable Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `consumable_offset_x` | 10.0 | Consumable change X offset |
| `consumable_offset_y` | 0.0 | Consumable change Y offset |
| `consumable_xy_feed_rate` | 0.0 | Consumable change XY feed rate (mm/min) |

### UI Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `backplot_multitool-colors` | true | Backplot multi-tool colors |

### Confirmation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `run_save_confirm` | false | Confirm before saving program |
| `run_delete_confirm` | true | Confirm before deleting program |

### Rate Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `thc_feed_rate` | 0.0 | THC feed rate (mm/min) |
| `framing_feed_rate` | 2000.0 | Framing feed rate (mm/min) |

## Jinja2 Templating

The config.yml supports Jinja2 templating for dynamic values:

```yaml
# File path relative to config directory
ui_file: {{ file.dir }}/mainwindow.ui

# Value from another config section
title: ( vcp.name ) ( vcp.version)

# Include shared fragments
#{% include "default_menubar.yml" %}
```

## Customizing the Config

### Changing File Locations

Edit `custom_config.yml` to override file locations:

```yaml
file_locations:
  kwargs:
    local_locations:
      NC Files: /path/to/your/nc_files
      Home: /path/to/your/home
```

### Switching to MySQL

For networked installations, you can switch the plasma processes database from SQLite to MySQL:

```yaml
plasmaprocesses:
  provider: qtpyvcp.plugins.plasma_processes:PlasmaProcesses
  kwargs:
    db_type: "mysql"
    db_host: "localhost"
    db_port: 3306
    db_name: "monokrom_plasma"
    db_user: "monokrom"
    db_password: "secret"
```

### Adding Custom Settings

Add new persistent settings to the config.yml:

```yaml
persistent_settings:
  my_custom_setting:
    default: 0
    type: int
    widget: hal_spinbox
```

The setting will be automatically saved to the `.prefs` file and restored on VCP restart.
