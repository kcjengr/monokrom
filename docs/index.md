# MonoKrom Plasma Documentation

Welcome to the MonoKrom Plasma documentation. This is a custom PySide6-based Virtual Control Panel
(VCP) for LinuxCNC plasma cutting machines, built on the [QtPyVCP](https://www.qtpyvcp.com/)
framework ([source](https://github.com/kcjengr/qtpyvcp)).

## What is MonoKrom Plasma?

MonoKrom Plasma is a feature-rich plasma cutting interface that leverages the concepts introduced
by [QTPlasmaC](https://linuxcnc.org/docs/html/customizing/qtplasmac.html) with additional
capabilities including:

- **Process Filter Database** — SQLite-backed cut parameter management with multi-field filtering
- **14 Quickshape Primitives** — Circle, rectangle, donut, flanges, gussets, and more
- **Cut Recovery** — 8-directional jog pad for recovering from interrupted cuts
- **Consumable Change** — Automated X/Y offset management for tip/wheel changes
- **Sheet Alignment** — Two-point coordinate system rotation with laser offset compensation
- **VTK Backplot** — 3D visualization of G-code programs
- **Process Logging** — Cut length, time, and arc OK statistics

## Documentation Sections

```{toctree}
:maxdepth: 2
:caption: Getting Started

overview
quick-start
```

```{toctree}
:maxdepth: 2
:caption: User Guide

user-guide/index
user-guide/main-tab
user-guide/conversational
user-guide/parameters
user-guide/settings
user-guide/statistics
user-guide/probe
user-guide/thc
user-guide/arc-start
user-guide/recovery
user-guide/sheet-alignment
user-guide/mdi
```

```{toctree}
:maxdepth: 2
:caption: Integrator Guide

integrator-guide/index
integrator-guide/hardware-setup
integrator-guide/ini-config
integrator-guide/hal-connections
integrator-guide/config-yml
integrator-guide/postgui-hal
integrator-guide/user-buttons
integrator-guide/process-db
integrator-guide/customization
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/hal-pin-map
reference/persistent-settings
reference/gcode-syntax
reference/state-machine
reference/quickshape-reference
```

```{toctree}
:maxdepth: 2
:caption: Other

troubleshooting
developer-guide
changelog
```

```{toctree}
:maxdepth: 1
:caption: Links

GitHub <https://github.com/kcjengr/monokrom>
LinuxCNC <https://linuxcnc.org>
QtPyVCP <https://www.qtpyvcp.com>
QTPlasmaC <https://linuxcnc.org/docs/html/customizing/qtplasmac.html>
```
