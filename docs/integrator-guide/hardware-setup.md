# Hardware Setup

This guide covers hardware requirements, I/O configuration, and wiring for MonoKrom Plasma
installations. It assumes familiarity with LinuxCNC basic configuration (stepconf/pncconf).

## Hardware Requirements

### Minimum Hardware

- LinuxCNC-compatible computer (see [LinuxCNC System Requirements](https://linuxcnc.org/docs/devel/html/getting-system-requirements.html))
- Breakout board with sufficient I/O pins
- Plasma power supply with torch on control
- Z axis with floating head (for probe input)

### Recommended Hardware

- Mesa electronics board (e.g., 7i96, 7i76)
- Ohmic probe kit
- Laser pointer for sheet alignment
- Pendant or external controls (optional)

## Operating Modes

MonoKrom Plasma supports three operating modes, selected in the INI file:

```ini
[QTPLASMAC]
MODE = 0
```

| Mode | Arc Voltage | Arc OK | THC Method | Recommended For |
|------|-------------|--------|------------|-----------------|
| **0** | Required | Soft (calculated) | Arc voltage-based | Machines without Arc OK output |
| **1** | Required | External digital input | Arc voltage-based | Machines with Arc OK output (recommended) |
| **2** | Not used | External digital input | External up/down signals | External THC controllers |

**Recommendation:** If your plasma power source provides an Arc OK (Transfer) output, use
Mode 1 or 2 with the external Arc OK signal rather than the soft calculated Arc OK from Mode 0.

## Available I/Os

### Required I/O

| Signal | Direction | Type | HAL Pin | Description |
|--------|-----------|------|---------|-------------|
| **Torch On** | Output | Digital | `plasmac.torch-on` | Controls plasma power supply |
| **Arc Voltage** OR **Arc OK** | Input | Analog/Digital | See modes above | See mode table |

**Minimum I/O:** One of Arc Voltage input OR Arc OK input, plus Torch On output.

### Optional I/O

| Signal | Direction | Type | HAL Pin | Description |
|--------|-----------|------|---------|-------------|
| **Arc Voltage** | Input | Analog | `plasmac.arc-voltage-in` | Arc voltage for THC (Modes 0, 1) |
| **Arc OK** | Input | Digital | `plasmac.arc-ok-in` | Arc transfer signal (Modes 1, 2) |
| **Float Switch** | Input | Digital | `plasmac.float-switch` | Mechanical probe switch |
| **Ohmic Probe** | Input | Digital | `plasmac.ohmic-probe` | Electronic touch-off |
| **Ohmic Enable** | Output | Digital | `plasmac.ohmic-enable` | Ohmic probe power control |
| **Breakaway** | Input | Digital | `plasmac.breakaway` | Torch breakaway detection |
| **Scribe Arm** | Output | Digital | `plasmac.scribe-arm` | Scribe positioning |
| **Scribe On** | Output | Digital | `plasmac.scribe-on` | Scribe activation |
| **Laser On** | Output | Digital | `qtplasmac.laser_on` | Alignment laser control |
| **Move Up** | Input | Digital | `plasmac.move-up` | THC up command (Mode 2) |
| **Move Down** | Input | Digital | `plasmac.move-down` | THC down command (Mode 2) |

**Note:** Only one of Float Switch or Ohmic Probe is required. If both are installed,
Float Switch serves as a fallback if Ohmic Probe fails.

## Wiring Guide

### Mode 1 Wiring (Recommended)

```
Plasma Power Source              Breakout Board
┌─────────────┐                 ┌──────────────┐
│ Torch On    │─────────────────│ Digital In   │
│ Arc OK      │─────────────────│ Digital In   │
│ Arc Voltage │─────────────────│ Analog In    │
└─────────────┘                 └──────────────┘

Float Switch ────────────────────│ Digital In   │
Ohmic Probe  ────────────────────│ Digital In   │
Ohmic Enable ────────────────────│ Digital Out  │
Breakaway  ──────────────────────│ Digital In   │
Laser On     ────────────────────│ Digital Out  │
```

### Debounce Configuration

All digital inputs that use mechanical switches should be debounced. MonoKrom uses the
`dbounce` component (LinuxCNC's modern debounce solution):

```hal
# In qtplasmac_connections.hal or custom.hal
loadrt dbounce names=db_float,db_ohmic,db_breakaway,db_arcok
addf db_float     servo-thread
addf db_ohmic     servo-thread
addf db_breakaway servo-thread
addf db_arcok     servo-thread

# Each increment = one servo thread cycle (1ms at 1MHz period)
setp db_float.delay     5    # 5ms
setp db_ohmic.delay     5
setp db_breakaway.delay 5
setp db_arcok.delay     5

# Connect inputs
net float-switch     => db_float.in
net ohmic-probe      => db_ohmic.in
net breakaway        => db_breakaway.in
net arc-ok           => db_arcok.in
```

**Tuning:** Use Halscope to observe switch signals. Start with `delay = 5` and adjust
based on observed bounce duration. Each increment adds ~0.001 mm to probed height.

## Z Axis Settings

### Recommended Z Axis Configuration

| Parameter | Recommendation | Example (Metric) |
|-----------|---------------|------------------|
| **MIN_LIMIT** | Just below slat top, accounting for float switch travel and overrun | -70.0 mm |
| **MAX_LIMIT** | Highest desired Z position (must be >= HOME_OFFSET) | 0.0 mm |
| **HOME** | 5-10 mm below MAX_LIMIT | 0.0 mm |
| **HOME_OFFSET** | Distance from home switch to reference position | 1.0 mm |

### Overrun Calculation

Calculate Z axis overrun during probing:

```
o = 0.5 * a * (v / a)^2
```

Where:
- `o` = overrun
- `a` = Z axis acceleration
- `v` = Z axis velocity

**Metric example:** a = 600 mm/s², v = 60 mm/s → o = 3 mm

**Imperial example:** a = 24 in/s², v = 2.4 in/s → o = 0.12 in

Set MIN_LIMIT to account for overrun:
```
MIN_LIMIT = slat_top - float_switch_travel - overrun - tolerance
```

### Height Reference

```
                    ^ Z positive
   MAX_LIMIT  ------+-------------------
                    |
   HOME       ------+-------------------  (5-10mm below MAX)
                    |
   Safe Height  ----+-------------------
                    |
   Pierce Height  --+-------------------
                    |
   Cut Height  ---- +-------------------
                    |
   Workpiece  ------ +-------------------
                    |
   Slat Top  ------  +-------------------
                    |
   MIN_LIMIT  ------ +-------------------
```

## Contact Load

Mechanical relays may require minimum current for reliable operation:

### Gold Contacts

Gold contacts (e.g., Mesa 7I96 inputs at 4700 Ω) typically need only ~5 mA — sufficient
for most plasma relay outputs. No additional hardware needed.

### Other Contacts

If minimum contact current is not met, add a parallel resistor:

```
R = Us / (Im - Ii)
P = Us² / Rs
```

Where:
- `Us` = supply voltage
- `Im` = minimum contact current
- `Ii` = breakout board input current

**Example:** 24V supply, 20.8 mA minimum, 5.1 mA input → R = 1529 Ω → use 1500 Ω 1W resistor

## Low-Pass Filter

The plasmac component has a built-in low-pass filter for arc voltage noise:

```hal
# In custom.hal — set only if Halscope shows noise issues
setp plasmac.lowpass-frequency 100  # 100 Hz cutoff
```

**Default:** 0 (disabled). Only enable if Halscope analysis shows noise amplitude is large
enough to cause issues. Most plasma machines do not need this filter.

## Desktop Launcher

Create a desktop launcher for easy startup:

```ini
[Desktop Entry]
Comment=
Terminal=false
Name=MonoKrom Plasma
Exec=sh -c "linuxcnc $HOME/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini"
Type=Application
Icon=/usr/share/pixmaps/linuxcncicon.png
```

Set `Terminal=true` if you want a terminal window for error messages.
