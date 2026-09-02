# HAL Pin Map

This reference documents the key HAL pins used by MonoKrom Plasma. The full pin map
(from the simulation) contains 2000+ lines — this document covers the plasma-specific
pins relevant to MonoKrom operation.

## PlasmaC Component Pins

### Arc Voltage

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.arc-voltage-in` | IN | float | Arc voltage input for THC (Modes 0, 1) |
| `plasmac.arc-voltage` | OUT | float | Calculated arc voltage |

### Arc OK

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.arc-ok-in` | IN | bit | External Arc OK input (Modes 1, 2) |
| `plasmac.arc-ok` | OUT | bit | Arc OK status (soft or external) |

### Torch Control

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.torch-on` | OUT | bit | Torch on/off control |

### Probe Inputs

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.float-switch` | IN | bit | Float switch input |
| `plasmac.ohmic-probe` | IN | bit | Ohmic probe input |
| `plasmac.ohmic-enable` | OUT | bit | Ohmic probe enable output |
| `plasmac.breakaway` | IN | bit | Breakaway switch input |

### THC Control

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.thc-enable` | IN/OUT | bit | THC enable flag |
| `plasmac.thc-delay` | IN/OUT | float | THC delay (seconds) |
| `plasmac.thc-p` | IN/OUT | float | THC proportional gain |
| `plasmac.thc-i` | IN/OUT | float | THC integral gain |
| `plasmac.thc-d` | IN/OUT | float | THC derivative gain |
| `plasmac.thc-up` | OUT | bit | THC commanding Z up |
| `plasmac.thc-down` | OUT | bit | THC commanding Z down |
| `plasmac.safe-height` | IN/OUT | float | Minimum Z height during cutting |
| `plasmac.height-override` | IN/OUT | float | THC height correction multiplier |
| `plasmac.height-per-volt` | IN/OUT | float | Z movement per volt calibration |
| `plasmac.vad-threshold` | IN/OUT | float | VAD detection threshold |
| `plasmac.vad-override` | IN/OUT | float | VAD void retraction override |
| `plasmac.void-sense` | IN/OUT | bit | Void sensing enabled |
| `plasmac.mesh-sense` | IN/OUT | bit | Mesh mode enabled |
| `plasmac.corner-lock` | IN/OUT | bit | Corner lock enabled |
| `plasmac.auto-volts` | IN/OUT | bit | Auto volts mode |
| `plasmac.lowpass-frequency` | IN | float | Low-pass filter cutoff (Hz) |

### Probe Settings

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.float-switch-travel` | IN/OUT | float | Float switch travel distance |
| `plasmac.probe-feed-rate` | IN/OUT | float | Probe feed rate |
| `plasmac.probe-height` | IN/OUT | float | Target height after probing |
| `plasmac.probe-offset` | IN/OUT | float | Additional probe offset |
| `plasmac.ohmic-retries` | IN/OUT | int | Number of ohmic probe retries |
| `plasmac.skip-ihs` | IN/OUT | float | Skip initial height search distance |
| `plasmac.probe-setup-speed` | IN/OUT | float | Probe setup approach speed |
| `plasmac.probe-test` | IN | bit | Probe test trigger (HAL controlled) |
| `plasmac.probe-test-error` | OUT | s32 | Probe test error code |

### Arc Start Settings

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.pierce-height` | IN/OUT | float | Pierce height |
| `plasmac.pierce-delay` | IN/OUT | float | Pierce delay (seconds) |
| `plasmac.cut-height` | IN/OUT | float | Cut height |
| `plasmac.cut-feed-rate` | IN/OUT | float | Cut feed rate |
| `plasmac.cut-volts` | IN/OUT | float | Cut voltage |
| `plasmac.cut-amperage` | IN/OUT | float | Cut amperage |
| `plasmac.puddle-jump-height` | IN/OUT | float | Puddle jump retraction height |
| `plasmac.puddle-jump-delay` | IN/OUT | float | Puddle jump delay (seconds) |
| `plasmac.torch-pulse` | IN/OUT | float | Torch pulse duration (seconds) |
| `plasmac.pause-at-end` | IN/OUT | bit | Pause at end of cut |
| `plasmac.arc-fail-delay` | IN/OUT | float | Arc fail timeout (seconds) |
| `plasmac.arc-max-starts` | IN/OUT | int | Max arc start attempts |
| `plasmac.arc-retry-delay` | IN/OUT | float | Delay between arc retries |
| `plasmac.arc-ok-high` | IN/OUT | float | Arc OK high voltage threshold |
| `plasmac.arc-ok-low` | IN/OUT | float | Arc OK low voltage threshold |
| `plasmac.voltage-scale` | IN/OUT | float | Arc voltage scale calibration |
| `plasmac.voltage-offset` | IN/OUT | float | Arc voltage offset calibration |

### Cut Parameters

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.cut-chart` | IN/OUT | int | Cut chart number |
| `plasmac.kerf` | IN/OUT | float | Kerf width |
| `plasmac.hole-thickness-ratio` | IN/OUT | float | Hole detection thickness ratio |
| `plasmac.max-hole-size` | IN/OUT | float | Maximum hole size for through-cut |
| `plasmac.hole-detect` | IN/OUT | bit | Hole detection enabled |
| `plasmac.overburn` | IN/OUT | bit | Overburn mode enabled |
| `plasmac.leadin` | IN/OUT | float | Lead-in length |
| `plasmac.small-hole-detect` | IN/OUT | bit | Small hole detection enabled |
| `plasmac.small-hole-straight-lead-in` | IN/OUT | bit | Straight lead-in for small holes |
| `plasmac.small-hole-threshold` | IN/OUT | float | Small hole threshold |
| `plasmac.small-hole-kerf` | IN/OUT | float | Small hole kerf compensation |
| `plasmac.hidef-mode` | IN/OUT | bit | High definition mode enabled |

### Arc Power Levels

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.arc1-percent` | IN/OUT | float | Arc 1 power percentage |
| `plasmac.arc1-distance` | IN/OUT | float | Arc 1 distance |
| `plasmac.arc1-radius` | IN/OUT | float | Arc 1 radius |
| `plasmac.arc2-percent` | IN/OUT | float | Arc 2 power percentage |
| `plasmac.arc2-distance` | IN/OUT | float | Arc 2 distance |
| `plasmac.arc2-radius` | IN/OUT | float | Arc 2 radius |
| `plasmac.arc3-percent` | IN/OUT | float | Arc 3 power percentage |
| `plasmac.arc3-distance` | IN/OUT | float | Arc 3 distance |
| `plasmac.arc3-radius` | IN/OUT | float | Arc 3 radius |

### Scribe

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.scribe-arm` | OUT | bit | Scribe arming output |
| `plasmac.scribe-on` | OUT | bit | Scribe on output |
| `plasmac.scribe-arm-delay` | IN/OUT | float | Scribe arming delay |
| `plasmac.scribe-on-delay` | IN/OUT | float | Scribe on delay |

### Spot Detection

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.spot-threshold` | IN/OUT | float | Spot detection threshold |
| `plasmac.spot-delay` | IN/OUT | float | Spot delay |

### Consumable Change

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.consumable-change` | IN | bit | Consumable change HAL trigger |
| `plasmac.consumable-x` | IN/OUT | float | Consumable change X offset |
| `plasmac.consumable-y` | IN/OUT | float | Consumable change Y offset |
| `plasmac.consumable-xy-feed` | IN/OUT | float | Consumable change XY feed rate |

### Offsets

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.laser-offset-x` | IN/OUT | float | Laser pointer X offset |
| `plasmac.laser-offset-y` | IN/OUT | float | Laser pointer Y offset |
| `plasmac.camera-offset-x` | IN/OUT | float | Camera X offset |
| `plasmac.camera-offset-y` | IN/OUT | float | Camera Y offset |
| `plasmac.scribe-offset-x` | IN/OUT | float | Scribe X offset |
| `plasmac.scribe-offset-y` | IN/OUT | float | Scribe Y offset |
| `plasmac.ohmic-offset-x` | IN/OUT | float | Ohmic probe X offset |
| `plasmac.ohmic-offset-y` | IN/OUT | float | Ohmic probe Y offset |

### Laser

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `qtplasmac.laser-on` | OUT | bit | Laser pointer control |

### State Indicators (Outputs)

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.consumable-changing` | OUT | bit | Consumable change active |
| `plasmac.cornerlock` | OUT | bit | Corner lock active |
| `plasmac.cut-length` | OUT | float | Total cut length |
| `plasmac.cut-time` | OUT | float | Total cut time |

### Mode 2 THC (External)

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `plasmac.move-up` | IN | bit | External THC up command |
| `plasmac.move-down` | IN | bit | External THC down command |

## Axis External Offset Pins

MonoKrom uses LinuxCNC external offsets for Z axis motion (and X/Y for consumable change/recovery):

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `axis.z.eoffset-request` | OUT | float | Z offset request from plasmac |
| `axis.z.eoffset-enable` | IN | bit | Z offset enable |
| `axis.z.eoffset-clear` | IN | bit | Z offset clear |
| `axis.z.eoffset-counts` | IN | s32 | Z offset counts |
| `axis.z.eoffset-scale` | IN | float | Z offset scale |
| `axis.x.eoffset-request` | OUT | float | X offset request (consumable/recovery) |
| `axis.x.eoffset-enable` | IN | bit | X offset enable |
| `axis.x.eoffset-clear` | IN | bit | X offset clear |
| `axis.y.eoffset-request` | OUT | float | Y offset request (consumable/recovery) |
| `axis.y.eoffset-enable` | IN | bit | Y offset enable |
| `axis.y.eoffset-clear` | IN | bit | Y offset clear |

## Debounce Component Pins

| Component | Pin | Direction | Type | Description |
|-----------|-----|-----------|------|-------------|
| `db_float` | `in` | IN | bit | Float switch input |
| `db_float` | `out` | OUT | bit | Debounced float switch |
| `db_float` | `delay` | IN | float | Debounce delay (servo periods) |
| `db_ohmic` | `in` | IN | bit | Ohmic probe input |
| `db_ohmic` | `out` | OUT | bit | Debounced ohmic probe |
| `db_ohmic` | `delay` | IN | float | Debounce delay (servo periods) |
| `db_breakaway` | `in` | IN | bit | Breakaway switch input |
| `db_breakaway` | `out` | OUT | bit | Debounced breakaway |
| `db_breakaway` | `delay` | IN | float | Debounce delay (servo periods) |
| `db_arc-ok` | `in` | IN | bit | Arc OK input |
| `db_arc-ok` | `out` | OUT | bit | Debounced arc OK |
| `db_arc-ok` | `delay` | IN | float | Debounce delay (servo periods) |

## Cycle Start State Pins

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `program-is-paused` | OUT | bit | Program is paused (feed hold) |
| `program-is-running` | OUT | bit | Program is running |
| `program-is-idle` | OUT | bit | Program is idle |
| `machine-is-homed` | OUT | bit | Machine is homed |

## Pendant / External Control Pins

| Pin | Direction | Type | Description |
|-----|-----------|------|-------------|
| `halui.mdi-command.0` through `halui.mdi-command.15` | IN | bit | MDI command triggers (pendant macros) |

## Full HAL Pin Map

The complete HAL pin map (2000+ lines) is available in the source repository at:
`docs/qtplasmac_hal_map.txt`

To regenerate:
```bash
# Run LinuxCNC with the config, then:
halcmd show > docs/qtplasmac_hal_map.txt
```
