# Changelog

All notable changes to MonoKorn Plasma will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial documentation structure (Sphinx + MyST + RTD theme)
- User guide (12 pages): Main tab, conversational, parameters, settings, statistics,
  probe, THC, arc start, recovery, sheet alignment, MDI
- Integrator guide (8 pages): Hardware setup, INI config, HAL connections, config.yml,
  postgui-HAL, user buttons, process database, customization
- Reference materials (5 pages): HAL pin map, persistent settings, G-code syntax,
  state machine, Quickshape reference
- GitHub Actions workflow for automated documentation builds
- Sphinx configuration with MyST Parser and Read the Docs theme

### Changed

- Nothing yet.

### Deprecated

- Nothing yet.

### Removed

- Nothing yet.

### Fixed

- Nothing yet.

### Security

- Nothing yet.

## [0.0] - YYYY-MM-DD

### Added

- Initial release of MonoKorn Plasma VCP
- PySide6-based plasma cutting interface
- SQLite-backed process filter database
- 14 Quickshape primitives
- Cut recovery with 8-directional jog pad
- Consumable change offset management
- Sheet alignment with two-point rotation
- VTK backplot with breadcrumbs and WCS support
- Process logging (cut length, time, arc OK)
- MDI entry assistance
- YAML configuration with Jinja2 templating
- Persistent settings via pickle
- THC with PID tuning, VAD, void sensing, mesh mode
- Ohmic and float switch probing
- Arc start with puddle jump and torch pulse
- Simulation config for LinuxCNC sim

[Unreleased]: https://github.com/joco-nz/monokrom-vcp/compare/v0.0...HEAD
[0.0]: https://github.com/joco-nz/monokrom-vcp/releases/tag/v0.0
