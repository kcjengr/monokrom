# Overview

MonoKrom Plasma is a custom PySide6-based Virtual Control Panel (VCP) for LinuxCNC plasma
cutting machines. It is built on the [QtPyVCP](https://www.qtpyvcp.com/) framework
([source](https://github.com/kcjengr/qtpyvcp)).

## Acknowledgements

MonoKrom Plasma draws functional inspiration from [QTPlasmaC](https://linuxcnc.org/docs/html/customizing/qtplasmac.html),
the stock LinuxCNC plasma cutting screen. QTPlasmaC served as the reference point for core
plasma cutting functionality including THC, probing, arc start, and cut management. MonoKrom
extends these concepts with additional capabilities for process management, cut recovery, and
sheet alignment.

## Architecture

MonoKrom Plasma consists of two main layers:

1. **QtPyVCP** — The GUI framework providing the window management, data plugins,
   persistent settings, and widget infrastructure. MonoKrom uses a forked qtpyvcp branch
   that adds a SQLite-backed plasma processes plugin.

2. **MonoKrom Services** — A set of application-level services instantiated by the main
   window, each handling a specific workflow:
   
   - `HALBridge` — Abstraction layer for HAL/LinuxCNC communication
   - `ProcessFilterService` — Cut parameter database management and filtering
   - `ShapeGeneratorService` — Quickshape G-code generation
   - `ConsumableChangeService` — Consumable change offset state machine
   - `CutRecoveryService` — Post-interruption recovery jog state machine
   - `SheetAlignmentService` — Two-point coordinate system rotation
   - `FileOpsService` — G-code file load/save/reload operations
   - `MdiPanelService` — MDI entry assistance

All services use dependency injection, making them testable and swappable.

## MonoKrom vs QTPlasmaC

MonoKrom Plasma retains the core plasma cutting functionality of QTPlasmaC (THC, probing,
arc start, cut types, hole cutting) while adding:

| Feature           | QTPlasmaC                    | MonoKrom Plasma                                                                            |
| ----------------- | ---------------------------- | ------------------------------------------------------------------------------------------ |
| Process database  | Built-in cut chart selection | SQLite database with multi-field filtering (gas, machine, material, thickness, consumable) |
| Quickshapes       | Basic shapes                 | 14 primitives with kerf compensation and smart hole detection                              |
| Cut recovery      | Basic feed hold              | 8-directional jog pad with kerf-width incremental moves                                    |
| Consumable change | Manual offset                | Automated X/Y offset state machine via HAL pin                                             |
| Sheet alignment   | Manual coordinate rotation   | Two-point alignment service with laser offset compensation                                 |
| VTK backplot      | Basic 3D view                | Enhanced with breadcrumbs, WCS support, program/machine bounds                             |
| Process logging   | Limited                      | Cut length, cut time, arc OK indicator on stats tab                                        |
| MDI assistance    | Basic entry                  | G-code word parameter lookup with suggestion buttons                                       |
| Config system     | INI-based                    | YAML with Jinja2 templating, persistent settings via pickle                                |
| HAL abstraction   | Direct pin wiring            | `HALBridge` service with lazy factories and dependency injection                           |

## Operating Modes

MonoKrom Plasma supports three operating modes. The mode is set in
the `[PLASMAC]` section of the INI file:

```ini
[PLASMAC]
MODE = 0
```

| Mode | Arc Voltage                                           | Arc OK                 | THC Method               |
| ---- | ----------------------------------------------------- | ---------------------- | ------------------------ |
| 0    | Used for both arc voltage calculation and soft arc OK | Soft (calculated)      | Arc voltage-based        |
| 1    | Used for arc voltage calculation                      | External digital input | Arc voltage-based        |
| 2    | Not used                                              | External digital input | External up/down signals |

**Recommendation:** If your plasma power source provides an Arc OK (Transfer) output, use
Mode 1 or 2 with the external Arc OK signal rather than the soft calculated Arc OK from Mode 0.

## Display

MonoKrom Plasma is designed for 16:9 displays at 1080p (1920 x 1080).

The display is set in the INI file:

```ini
[DISPLAY]
DISPLAY = monokrom_plasma
```

## Key Concepts

### Thermal Height Control (THC)

THC maintains the correct torch-to-workpiece distance during cutting by monitoring arc voltage
and adjusting the Z axis. MonoKrom Plasma provides full PID tuning controls, voltage arc
detection (VAD), void sensing, and mesh mode on the Settings tab.

### Probing

MonoKrom supports two probing methods for finding the workpiece surface:

- **Ohmic probe** — Electronic touch-off using the workpiece and torch consumables to complete
  a circuit. This is the primary probing method.
- **Float switch** — Mechanical switch on the floating head. Used as a fallback if ohmic probe
  fails, or as the sole probing method if no ohmic probe is installed.

### Process Filter Database

The process filter database stores cut parameters (pierce height, cut height, feed rate,
volts, amps, kerf) indexed by gas type, machine type, material, thickness, and consumable.
Users select filters from dropdowns on the Parameters tab, and the matching cut parameters
are displayed and applied automatically.

### Quickshapes

MonoKrom includes 14 built-in shape primitives that generate complete G-code programs with
plasma start/stop sequences, kerf compensation, lead-ins, and smart hole detection:

Circle, Rectangle, Donut, Convex Rectangle, Lifting Lug, U-Lug, Pipe Flange, Pipe Saddle,
Exhaust Flange, N-Square Grid, L-Gusset, Angle Gusset, Truss Support, Web Stiffener.

### Cut Recovery

When a cut is interrupted (feed hold), the Cut Recovery tab provides an 8-directional jog
pad and speed slider to manually reposition the torch back to the cut path. Moves are
incremented by kerf width for precision.

### Consumable Change

The consumable change feature manages X/Y offsets for tip and wheel wear. When enabled via
HAL pin (`plasmac.consumable-change`), the machine applies the configured offset and returns
to the home position for consumable replacement.

### Sheet Alignment

The sheet alignment service performs two-point coordinate system rotation. The operator marks
two reference points on the workpiece using the laser pointer, and MonoKrom computes the
rotation angle (via `atan2`) and applies it using a `G10 L2 P0 R` command.
