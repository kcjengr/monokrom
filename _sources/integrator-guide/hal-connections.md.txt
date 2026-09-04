# HAL Connections

HAL (Hardware Abstraction Layer) files define the signal connections between LinuxCNC
components and your hardware. MonoKrom Plasma uses a multi-file HAL structure.

## HAL File Structure

The HAL files are loaded in order as specified in the INI file:

```ini
[HAL]
HALFILE = plasmac_sim_overlay.hal       # Axis/sim overlay
HALFILE = qtplasmac_connections_sim.hal # PlasmaC connections
HALFILE = ../common/hallib/core_sim_3.hal  # Core HAL library
HALFILE = ../common/hallib/spindle_sim.hal   # Spindle simulation
HALFILE = ../common/hallib/simulated_home.hal # Home simulation
POSTGUI_HALFILE = postgui_call_list_plasmac_sim.hal # Post-GUI
```

## Core HAL Files

### `core_sim_3.hal`

Provides the core LinuxCNC HAL infrastructure for a 3-axis (XYZ) machine:
- Axis joints and encoders
- Trajectory planner
- Motion control
- Homing modules

This file is shared across all MonoKrom configurations and should not be modified.

### `spindle_sim.hal`

Provides simulated spindle control. For real plasma machines, replace with actual
spindle/plasma power supply connections.

### `simulated_home.hal`

Provides simulated home switch signals for the simulator. Not needed for real hardware.

## PlasmaC Connection Files

### `qtplasmac_connections.hal` (Real Hardware)

This is the primary file for plasma-specific HAL connections. The simulation version
(`qtplasmac_connections_sim.hal`) uses the same structure but with commented-out
hardware connections.

#### Debounce Components

```hal
loadrt dbounce names=db_breakaway,db_float,db_ohmic,db_arc-ok
addf db_float     servo-thread
addf db_ohmic     servo-thread
addf db_breakaway servo-thread
addf db_arc-ok    servo-thread

setp db_float.delay     5
setp db_ohmic.delay     5
setp db_breakaway.delay 5
setp db_arc-ok.delay    5
```

#### Arc Voltage Low-Pass Filter

```hal
# Set to 0 (disabled) unless Halscope shows noise issues
setp plasmac.lowpass-frequency 0
```

#### Mode-Specific Connections

**Mode 0 (Arc voltage for both THC and soft Arc OK):**
```hal
#net plasmac:arc-voltage-in  ***YOUR_PLASMA_ARC_VOLTAGE***  =>  plasmac.arc-voltage-in
```

**Mode 1 (Arc voltage for THC, external Arc OK):**
```hal
#net plasmac:arc-voltage-in  ***YOUR_PLASMA_ARC_VOLTAGE***  =>  plasmac.arc-voltage-in
#net plasmac:arc-ok-in       ***YOUR_PLASMA_ARC_OK***       =>  db_arc-ok.in
```

**Mode 2 (External Arc OK, external THC up/down):**
```hal
#net plasmac:arc-ok-in       ***YOUR_PLASMA_ARC_OK***       =>  db_arc-ok.in
#net plasmac:move-down       ***YOUR_MOVE_DOWN_SIGNAL***    =>  plasmac.move-down
#net plasmac:move-up         ***YOUR_MOVE_UP_SIGNAL***      =>  plasmac.move-up
```

#### Common Connections (All Modes)

```hal
#net plasmac:float-switch    ***YOUR_FLOAT_SWITCH***        =>  db_float.in
#net plasmac:breakaway       ***YOUR_BREAKAWAY_SWITCH***    =>  db_breakaway.in
#net plasmac:ohmic-probe     ***YOUR_OHMIC_PROBE***        =>  db_ohmic.in
#net plasmac:torch-on                                        =>  ***YOUR_TORCH_ON***
#net plasmac:ohmic-enable    plasmac.ohmic-enable           =>  ***YOUR_OHMIC_PROBE_ENABLING_CIRCUIT***
```

#### Scribe Connections (Optional)

```hal
#net plasmac:scribe-arm plasmac.scribe-arm => ***YOUR_SCRIBE_ARMING_OUTPUT***
#net plasmac:scribe-on  plasmac.scribe-on  => ***YOUR_SCRIBE_ON_OUTPUT***
```

#### Laser Connection (Optional)

```hal
#net qtplasmac:laser_on => ***YOUR_LASER_OUTPUT***
```

## Post-GUI HAL File

### `postgui_call_list.hal`

This file sources additional HAL files that are loaded after the GUI initializes.
MonoKrom uses:

```hal
source postgui_plasmac_sim.hal
source postgui_sim_plasmac_sim.hal
```

### `postgui_plasmac_sim.hal`

Contains extensive HAL pin mappings for plasmaC parameters. Key connections:

#### Axis Limit Connections

```hal
# Connect axis limits to plasmac
setp plasmac.x-min-limit -2.0
setp plasmac.x-max-limit 1200.0
setp plasmac.y-min-limit -2.0
setp plasmac.y-max-limit 1200.0
setp plasmac.z-min-limit -70.0
```

#### PlasmaC Parameter Mappings

```hal
# Cut parameters
net plasmac.cut-feed-rate => halui.feed-override
net plasmac.cut-height => ...
net plasmac.cut-volts => ...
net plasmac.cut-chart => ...
```

#### Probe Settings

```hal
# Float switch travel
net plasmac.float-switch-travel => ...

# Probe feed rate
net plasmac.probe-feed-rate => ...

# Ohmic probe enable
net plasmac.ohmic-probe-enable => ...
```

#### THC Settings

```hal
# THC enable
net plasmac.thc-enable => ...

# THC delay
net plasmac.thc-delay => ...

# THC PID gains
net plasmac.thc-p => ...
net plasmac.thc-i => ...
net plasmac.thc-d => ...

# Safe height
net plasmac.safe-height => ...
```

#### Arc Settings

```hal
# Arc OK thresholds
net plasmac.arc-ok-high => ...
net plasmac.arc-ok-low => ...

# Arc fail settings
net plasmac.arc-fail-delay => ...
net plasmac.arc-max-starts => ...
```

#### LED Output Connections

```hal
# Status LEDs
net plasmac.consumable-changing => ...
net plasmac.cornerlock => ...
net plasmac.thc-up => ...
net plasmac.thc-down => ...
net plasmac.arc-ok => ...
net plasmac.torch-on => ...
net plasmac.cut-length => ...
net plasmac.cut-time => ...
```

#### Cycle Start Connections

```hal
# Program state indicators
net program-is-paused => ...
net program-is-running => ...
net program-is-idle => ...
net machine-is-homed => ...
```

## Custom HAL File

### `custom.hal`

This file is NOT overwritten by MonoKrom updates. Use it for:

- Additional debounce components
- Low-pass filter settings
- Custom signal routing
- User-specific HAL logic

```hal
# Example: Custom debounce for a specific input
loadrt dbounce names=db_custom
addf db_custom servo-thread
setp db_custom.delay 10
net custom-signal => db_custom.in

# Example: Low-pass filter
setp plasmac.lowpass-frequency 100
```

## HAL Pin Reference

For a complete list of HAL pins used by MonoKrom Plasma, see the
[HAL Pin Map](../reference/hal-pin-map.md) reference.

## Debugging HAL Connections

### Using HalScope

1. Start HalScope from the LinuxCNC display:
   ```bash
   halscope
   ```

2. Add signals to plot:
   - `plasmac.arc-voltage-in` — Arc voltage signal
   - `plasmac.arc-ok` — Arc OK status
   - `plasmac.float-switch` — Float switch state
   - `plasmac.ohmic-probe` — Ohmic probe state
   - `plasmac.torch-on` — Torch on state
   - `plasmac.thc-enable` — THC enable state

3. Observe signal timing and levels to verify correct operation.

### Using HalComp

Create custom HAL components for debugging:

```hal
loadrt and2 count=1
addf and2 servo-thread
net debug-and => and2.in1 plasmac.arc-ok
net debug-and => and2.in2 plasmac.thc-enable
# Probe the output to verify logic
```

### Common HAL Issues

| Symptom | Check | Solution |
|---------|-------|----------|
| Torch doesn't turn on | `plasmac.torch-on` pin | Verify HAL connection to breakout board output |
| Arc OK not detected | `plasmac.arc-ok-in` pin | Verify input wiring, check debounce |
| THC not responding | `plasmac.arc-voltage-in` pin | Verify analog input, check low-pass filter |
| Probe doesn't trigger | `plasmac.ohmic-probe` or `plasmac.float-switch` | Verify wiring, check debounce, clean workpiece |
| Float switch false triggers | `plasmac.float-switch` signal in HalScope | Increase debounce delay |
