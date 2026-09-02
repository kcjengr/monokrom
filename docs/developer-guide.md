# Developer Guide

This guide covers the MonoKorn Plasma architecture, development workflow, and conventions
for developers who want to extend or modify the VCP.

## Architecture Overview

MonoKorn Plasma follows a service-oriented architecture built on [QtPyVCP](https://www.qtpyvcp.com/):

```
+--------------------------------------------------+
|                   Main Window                     |
+--------------------------------------------------+
|  Tab Widget (Main | Preview | Parameters | ...)   |
+--------------------------------------------------+
|              Service Layer (DI)                   |
|  +----------+ +-----------+ +----------------+   |
|  | HALBridge | | Process   | | ShapeGenerator |   |
|  |           | | Filter    | | Service        |   |
|  +----------+ +-----------+ +----------------+   |
|  +----------+ +-----------+ +----------------+   |
|  | Consumable| | Cut       | | SheetAlign     |   |
|  | Change    | | Recovery  | | Service        |   |
|  +----------+ +-----------+ +----------------+   |
|  +----------+ +-----------+                      |
|  | FileOps  | | MdiPanel  |                      |
|  | Service  | | Service   |                      |
|  +----------+ +-----------+                      |
+--------------------------------------------------+
|              QtPyVCP Framework                    |
+--------------------------------------------------+
|              LinuxCNC / HAL                       |
+--------------------------------------------------+
```

## Service Layer

All application logic is encapsulated in services. Each service is a Python class that
handles a specific workflow. Services are instantiated by the main window using dependency
injection.

### HALBridge

The HALBridge service abstracts HAL/LinuxCNC communication. It provides:

- Lazy factory pattern for HAL pin connections
- Type-safe pin access (bit, float, s32)
- Signal/slot connections for pin value changes
- Configuration from YAML files

```python
# Example: Getting a HAL pin through HALBridge
from monokrom.plasma.services.hal_bridge import HALBridge

bridge = HALBridge()
arc_ok = bridge.get_pin("plasmac.arc-ok", "bit")
arc_ok.value_changed.connect(self.on_arc_ok_changed)
```

### ProcessFilterService

Manages the SQLite-backed process filter database. Provides:

- CRUD operations for cut processes
- Multi-field filtering (gas, machine, material, thickness, consumable)
- Signal/slot for filter changes and selections

```python
from monokrom.plasma.services.process_filter import ProcessFilterService

service = ProcessFilterService()
# Get all cuts matching filters
cuts = service.get_cuts(gas="Air", material="Mild Steel", thickness="3mm")
# Add a new cut
service.add_cut(gas="Air", material="Mild Steel", thickness="3mm",
                pierce_height=6.0, cut_height=3.5, cut_feed_rate=1200)
```

### ShapeGeneratorService

Generates G-code for Quickshape primitives. Provides:

- 14 built-in shape generators
- Kerf compensation
- Smart hole detection
- Lead-in generation
- Plasma start/stop sequences

```python
from monokrom.plasma.services.shape_generator import ShapeGeneratorService

service = ShapeGeneratorService()
# Generate a circle
gcode = service.generate_circle(diameter=100.0, material="Mild Steel 3mm")
# Save to file
service.save_gcode(gcode, "/home/user/linuxcnc/nc_files/circle.ngc")
```

### ConsumableChangeService

Manages X/Y offsets for consumable change. Provides:

- State machine for consumable change workflow
- Offset application and removal
- HAL pin integration

### CutRecoveryService

Manages cut recovery after interruptions. Provides:

- 8-directional jog pad control
- Kerf-width incremental moves
- Speed slider integration

### SheetAlignmentService

Manages sheet alignment via two-point rotation. Provides:

- Two-point coordinate system rotation
- Laser offset compensation
- G10 L2 P0 R command generation

### FileOpsService

Manages G-code file operations. Provides:

- Load, save, reload G-code files
- File browser integration
- Program validation

### MdiPanelService

Provides MDI entry assistance. Provides:

- G-code word parameter lookup
- Suggestion buttons for common parameters

## Development Workflow

### Setting Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/joco-nz/monokrom-vcp
cd monokrom-vcp

# Install in editable mode
python3 -m pip install -e .

# Install dev dependencies (if any)
python3 -m pip install -r requirements-dev.txt  # if exists
```

### Running the VCP in Development Mode

```bash
# Run with live QSS reload
monokrom_plasma --ini <config> --develop

# Run with specific config
monokrom_plasma --ini ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
```

### Code Style

MonoKorn Plasma does not currently have a linter or formatter configured. However, the
existing code follows these conventions:

- **Indentation:** 4 spaces (no tabs)
- **Line length:** 100 characters maximum
- **Naming:**
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_leading_underscore`
- **Imports:** Standard library first, then third-party, then local
- **Docstrings:** Google-style docstrings for public APIs

### Adding a New Service

1. Create a new service class in `src/monokrom/plasma/services/`:

```python
# src/monokrom/plasma/services/my_service.py
from PyQt6.QtCore import QObject, pyqtSignal

class MyService(QObject):
    """Description of the service."""

    value_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = None

    def get_value(self):
        """Get the current value."""
        return self._value

    def set_value(self, value):
        """Set the value and emit change signal."""
        self._value = value
        self.value_changed.emit(value)
```

2. Instantiate the service in the main window:

```python
# src/monokrom/plasma/main_window.py
from monokrom.plasma.services.my_service import MyService

class MainWindow(...):
    def __init__(self, ...):
        # ...
        self.my_service = MyService(parent=self)
```

3. Connect the service to UI widgets as needed.

### Adding a New Quickshape

1. Add the shape generator function in `src/monokrom/plasma/services/shape_generator.py`:

```python
def generate_my_shape(self, param1, param2, material=None):
    """Generate G-code for my shape."""
    # Get material parameters
    params = self.get_material_params(material)

    # Generate G-code
    gcode = f"""; MonoKrom Quickshape - My Shape
G0 Z{params['pierce_height']}
...
"""
    return gcode
```

2. Add a button for the shape in the Quickshapes UI:

```python
# In the Quickshapes widget
button = QPushButton("My Shape")
button.clicked.connect(lambda: self.generate_shape('my_shape', ...))
```

3. Update the shape reference table in `docs/reference/quickshape-reference.md`.

### Adding a New HAL Pin Connection

1. Define the pin in the HAL file (`postgui.hal` or custom HAL file):

```hal
# Connect a custom HAL pin
net my-custom-pin => plasmac.my-pin
```

2. Access the pin through HALBridge:

```python
my_pin = self.hal_bridge.get_pin("plasmac.my-pin", "bit")
```

3. Connect to the pin's value change signal:

```python
my_pin.value_changed.connect(self.on_my_pin_changed)
```

### Testing

MonoKorn Plasma does not currently have a test framework configured. To test changes:

1. Run the VCP with the simulation config:
   ```bash
   monokrom_plasma --ini ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
   ```

2. Verify the changes in the VCP interface.

3. Test with real hardware if available.

## Debugging

### Enabling Debug Output

Set the environment variable `MONOKROM_DEBUG=1` to enable debug logging:

```bash
MONOKROM_DEBUG=1 monokrom_plasma --ini <config>
```

### HAL Debugging

Use `halcmd` to inspect HAL pins during runtime:

```bash
# List all pins
halcmd show

# Show a specific pin
halcmd show pin plasmac.arc-ok

# Watch a pin for changes
halcmd watch plasmac.arc-ok
```

### Qt Debugging

Use Qt's built-in debugging tools:

```bash
# Enable Qt debug output
QT_DEBUG_PLUGINS=1 monokrom_plasma --ini <config>
```

## Extending the UI

### Adding a New Tab

1. Create a new widget class:

```python
# src/monokrom/plasma/widgets/my_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class MyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        # Add widgets to layout
```

2. Add the tab to the main window:

```python
# In main_window.py
from monokrom.plasma.widgets.my_tab import MyTab

self.my_tab = MyTab(parent=self)
self.tab_widget.addTab(self.my_tab, "My Tab")
```

### Adding a New Widget

Create a new widget class in `src/monokrom/plasma/widgets/` or `src/monokrom/common/widgets/`:

```python
# src/monokrom/plasma/widgets/my_widget.py
from PyQt6.QtWidgets import QWidget, QLabel

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("My Widget", self)
```

## Configuration

### YAML Configuration

MonoKorn Plasma uses YAML with Jinja2 templating for configuration. See the
[Integrator Guide - config.yml](integrator-guide/config-yml.md) for details.

### Persistent Settings

Settings are stored in a pickle file and managed by QtPyVCP's persistent settings system.
See the [Persistent Settings](reference/persistent-settings.md) reference for the full
list of settings.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository on GitHub.
2. Create a feature branch from `main`.
3. Make your changes.
4. Submit a pull request.

### Pull Request Checklist

- [ ] Code follows the existing style conventions.
- [ ] Changes are documented (docstrings, comments).
- [ ] Documentation is updated (if applicable).
- [ ] Changes are tested with the simulation config.
- [ ] Changelog is updated (if applicable).

## See Also

- [Overview](overview.md) — Architecture and feature overview
- [Integrator Guide](integrator-guide/index.md) — Hardware setup and configuration
- [Quickshape Reference](reference/quickshape-reference) — Quickshape primitives
- [G-Code Syntax](reference/gcode-syntax) — G-code reference
