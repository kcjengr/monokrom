# Persistent Settings

This reference documents all persistent settings in MonoKrom Plasma. Settings are saved
to the `.prefs` file (pickle format) and restored automatically on VCP restart.

## THC Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `thc_delay` | 0.5 | float | Settings | THC enable delay (seconds) |
| `thc_threshold` | 1.0 | float | Settings | THC voltage threshold (V) |
| `thc_pid_p_gain` | 10.0 | float | Settings | THC proportional gain |
| `thc_pid_i_gain` | 0.0 | float | Settings | THC integral gain |
| `thc_pid_d_gain` | 0.0 | float | Settings | THC derivative gain |
| `thc_enabled` | true | bool | Settings | THC enabled flag |
| `thc_feed_rate` | 3000.0 | float | Settings | THC feed rate (mm/min) |
| `thc_vad_threshold` | 60.0 | float | Settings | VAD detection threshold (V) |
| `thc_void_override` | 99 | int | Settings | VAD void retraction override |
| `thc_safe_height` | 40.0 | float | Settings | Minimum Z height during cutting |
| `height_per_volt` | 0.100 | float | Settings | Z movement per volt calibration |
| `plasma_vad` | true | bool | Settings | VAD enabled |
| `plasma_void_sense` | true | bool | Settings | Void sensing enabled |
| `plasma_mesh_sense` | false | bool | Settings | Mesh mode enabled |
| `corner_lock` | false | bool | Settings | Corner lock enabled |
| `plasma_auto_volts` | true | bool | Settings | Auto volts mode |

## Probe Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `probe_float_travel` | 3.2 | float | Settings | Float switch travel distance (mm) |
| `probe_speed` | 300 | int | Settings | Probe feed rate (mm/min) |
| `probe_height` | 14.0 | float | Settings | Target height after probing (mm) |
| `probe_offset` | -0.5 | float | Settings | Additional probe offset (mm) |
| `ohmic_sensing_enabled` | false | bool | Settings | Ohmic probe enabled |
| `probe_ohmic_retries` | 3 | int | Settings | Number of ohmic probe retries |
| `probe_skip_ihs` | 0.0 | float | Settings | Skip initial height search distance |
| `probe_setup_speed` | 3000 | int | Settings | Probe setup approach speed (mm/min) |

## Arc Start Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `arc_fail_timeout` | 3.0 | float | Settings | Arc fail timeout (seconds) |
| `arc_max_starts` | 3 | int | Settings | Max arc start attempts |
| `arc_retry_delay` | 5.0 | float | Settings | Delay between arc retries (seconds) |
| `arc_ok_high_volts` | 250.0 | float | Settings | Arc OK high voltage threshold (V) |
| `arc_ok_low_volts` | 60.0 | float | Settings | Arc OK low voltage threshold (V) |
| `puddle_jump_height` | 0.0 | float | Settings | Puddle jump retraction height |
| `puddle_jump_delay` | 0.0 | float | Settings | Puddle jump delay (seconds) |
| `plasma_torch_pulse_sec` | 1.0 | float | Settings | Torch pulse duration (seconds) |
| `pause_at_end` | false | bool | Settings | Pause at end of cut |
| `arc_voltage_scale` | 0.006744 | float | Settings | Arc voltage scale calibration |
| `arc_voltage_offset` | 3687.5 | float | Settings | Arc voltage offset calibration |
| `arc_height_per_volt` | 0.100 | float | Settings | Arc height per volt calibration |

## Scribe Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `scribe_arm_delay` | 0.0 | float | Settings | Scribe arming delay (seconds) |
| `scribe_on_delay` | 0.3 | float | Settings | Scribe on delay (seconds) |

## Spot Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `spot_threshold` | 5.0 | float | Settings | Spot detection threshold |
| `spot_delay` | 100.0 | float | Settings | Spot delay (seconds) |

## Plasma Cut Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `plasma_hole_thickness_ratio` | 5 | int | Settings | Hole detection thickness ratio |
| `plasma_max_hole_size` | 50.0 | float | Settings | Max hole size for through-cut (mm) |
| `plasma_hole_detect_enable` | true | bool | Settings | Hole detection enabled |
| `plasma_arc1_percent` | 60.0 | float | Settings | Arc 1 power percentage |
| `plasma_arc1_distance` | 80.0 | float | Settings | Arc 1 distance |
| `plasma_arc2_percent` | 40.0 | float | Settings | Arc 2 power percentage |
| `plasma_arc2_distance` | 20.0 | float | Settings | Arc 2 distance |
| `plasma_arc3_percent` | 100.0 | float | Settings | Arc 3 power percentage |
| `plasma_arc3_distance` | 20.0 | float | Settings | Arc 3 distance |
| `plasma_overburn_percent` | 100.0 | float | Settings | Overburn percentage |
| `plasma_leadin_percent` | 60.0 | float | Settings | Lead-in percentage |
| `plasma_leadin_radius` | 3.0 | float | Settings | Lead-in radius |
| `plasma_small_hole_detect` | false | bool | Settings | Small hole detection enabled |
| `plasma_force_straight_leadin` | false | bool | Settings | Straight lead-in for small holes |
| `plasma_small_hole_threshold` | 3.5 | float | Settings | Small hole threshold |
| `plasma_hole_kerf` | 0.0 | float | Settings | Small hole kerf compensation |
| `plasma_use_hidef` | false | bool | Settings | High definition mode enabled |

## Offset Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `laser_offset_x` | 0.0 | float | Settings | Laser pointer X offset |
| `laser_offset_y` | 0.0 | float | Settings | Laser pointer Y offset |
| `camera_offset_x` | 0.0 | float | Settings | Camera X offset |
| `camera_offset_y` | 0.0 | float | Settings | Camera Y offset |
| `scribe_offset_x` | 0.0 | float | Settings | Scribe X offset |
| `scribe_offset_y` | 0.0 | float | Settings | Scribe Y offset |
| `ohmic_offset_x` | 0.0 | float | Settings | Ohmic probe X offset |
| `ohmic_offset_y` | 0.0 | float | Settings | Ohmic probe Y offset |

## Consumable Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `consumable_offset_x` | 10.0 | float | Settings | Consumable change X offset |
| `consumable_offset_y` | 0.0 | float | Settings | Consumable change Y offset |
| `consumable_xy_feed_rate` | 0.0 | float | Settings | Consumable change XY feed rate (mm/min) |

## UI Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `backplot_multitool-colors` | true | bool | Settings | Backplot multi-tool colors |

## Confirmation Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `run_save_confirm` | false | bool | Settings | Confirm before saving program |
| `run_delete_confirm` | true | bool | Settings | Confirm before deleting program |

## Rate Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `thc_feed_rate` | 0.0 | float | Settings | THC feed rate (mm/min) |
| `framing_feed_rate` | 2000.0 | float | Settings | Framing feed rate (mm/min) |

## Locked Filter Settings

| Setting | Default | Type | Tab | Description |
|---------|---------|------|-----|-------------|
| `filter_gas_locked` | false | bool | Parameters | Gas filter locked |
| `filter_machine_locked` | false | bool | Parameters | Machine filter locked |
| `filter_material_locked` | false | bool | Parameters | Material filter locked |
| `filter_thickness_locked` | false | bool | Parameters | Thickness filter locked |
| `filter_consumable_locked` | false | bool | Parameters | Consumable filter locked |

## File Locations

| Setting | Default | Type | Description |
|---------|---------|------|-------------|
| `nc_files_dir` | ~/linuxcnc/nc_files | string | NC files directory |
| `home_dir` | ~/ | string | Home directory |
| `desktop_dir` | ~/Desktop | string | Desktop directory |

## Persistent Settings File

Settings are stored in:

```
<machine_name>.prefs
```

Located in the machine configuration directory (e.g., `~/linuxcnc/configs/sim.monokrom/plasmac/sim.pref`).

The file is in pickle format and should not be edited manually. To reset all settings:

```bash
# Stop LinuxCNC
rm ~/linuxcnc/configs/sim.monokrom/plasmac/sim.pref
# Restart LinuxCNC - settings will restore to defaults
```
