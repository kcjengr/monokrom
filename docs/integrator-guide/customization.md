# Customization

This guide covers customizing the MonoKrom Plasma appearance, behavior, and functionality.

## Stylesheets

MonoKrom Plasma uses Qt Stylesheets (QSS) for theming. Stylesheets are compiled from SASS
source files.

### Stylesheet Sources

| File | Purpose |
|------|---------|
| `src/monokrom/common/monokrom.qss` | Master stylesheet (compiled from SASS) |
| `src/monokrom/plasma/plasma.qss` | Plasma-specific overrides (minimal) |
| `linuxcnc/configs/sim.monokrom/plasmac/qtplasmac_sim.qss` | Sim-specific overrides |

### Applying a Stylesheet

The stylesheet is applied in `config.yml`:

```yaml
windows:
  mainwindow:
    kwargs:
      stylesheet: {{ file.dir }}/../common/monokrom.qss
```

### Compiling SASS to QSS

SASS sources are in `src/monokrom/common/sass/` and `src/monokrom/plasma/sass/`.

Compile manually:

```bash
cd src/monokrom/common/sass
qtsass ./yellow.scss -o ../monokrom.qss
```

**Note:** `qtsass` is a dev-only tool, not a runtime dependency.

### SASS Structure

```
src/monokrom/common/sass/
├── yellow.scss          # Yellow theme (default)
└── _variables.scss      # Shared variables

src/monokrom/plasma/sass/
└── plasma.scss          # Plasma-specific partial (imports common yellow.scss)
```

### Creating a Custom Style

1. **Create a new SASS file:**
   ```scss
   // src/monokrom/common/sass/custom.scss
   @import 'variables';

   // Override colors
   $primary-color: #3498db;
   $background-color: #1a1a2e;
   $text-color: #eee;

   // Your custom styles
   QPushButton {
       background: $primary-color;
       color: $text-color;
       border: 1px solid darken($primary-color, 10%);
   }
   ```

2. **Compile to QSS:**
   ```bash
   qtsass ./custom.scss -o ../custom.qss
   ```

3. **Apply in config.yml:**
   ```yaml
   windows:
     mainwindow:
       kwargs:
         stylesheet: /path/to/custom.qss
   ```

### Runtime Stylesheet Loading

In development mode, the VCP supports live QSS reload:

```bash
monokrom_plasma --ini <config> --develop
```

This enables automatic stylesheet reloading when the QSS file changes.

## Custom Widgets

MonoKrom provides custom Qt widgets in the `monokrom.common.widgets` and
`monokrom.plasma.widgets` packages.

### Common Widgets

| Widget | Class | File | Purpose |
|--------|-------|------|---------|
| LED | `MkLed` | `mk_led.py` | LED indicator |
| HAL LED | `MkLedHal` | `mk_led_hal.py` | HAL-connected LED |
| Push Button | `MkPushButton` | `mk_push_button.py` | Styled push button |
| Line Edit | `MkLineEdit` | `mk_line_edit.py` | Styled line edit |
| MDI Entry | `MkMdiEntry` | `mdi_entry.py` | MDI text entry |
| File List | `MkFileListView` | `file_list_view.py` | File browser |
| Recent Files | `MkRecentFileListView` | `recent_file_list_view.py` | Recent files |
| Group Box | `MkGroupBox` | `group_box.py` | Styled group box |
| Input Overlay | `MkInputOverlay` | `input_overlay.py` | Dialog overlay |
| Tab Widget | `MkTabWidget` | `tab_widget.py` | Custom tab widget |
| DRO | `MkDro` | `mk_dro/` | Digital readout |
| Transparent Widget | `MkTransparentWidget` | `transparent_widget.py` | Transparent base |

### Plasma Widgets

| Widget | Class | File | Purpose |
|--------|-------|------|---------|
| HAL SpinBox | `PlasmaHalSpinBox` | `plasma_hal_spinbox.py` | HAL-connected integer spinbox |
| HAL Double SpinBox | `PlasmaHalDoubleSpinBox` | `plasma_hal_double_spinbox.py` | HAL-connected float spinbox |
| HAL CheckBox | `PlasmaHalCheckBox` | `plasma_hal_checkbox.py` | HAL-connected checkbox |
| Cycle Start Button | `CycleStartActionButton` | `cyclestart_action_button.py` | State-aware cycle start |
| Add Process | `PlasmaAddProcess` | `plasma_add_process.py` | New cut process entry |

### Registering Custom Widgets

Custom widgets are registered in `pyproject.toml`:

```toml
[tool.poetry.plugins."qtpyvcp.widgets"]
monokrom_common_widgets = "monokrom.common.widgets"
monokrom_plasma_widgets = "monokrom.plasma.widgets"
monokrom_mill_widgets = "monokrom.mill.widgets"
```

Widgets can then be used in Qt Designer by promoting standard Qt widgets to the custom class.

## Adding a Custom Service

Services are instantiated in `mainwindow.py` and use dependency injection.

### Creating a New Service

```python
# src/monokrom/plasma/my_service.py
class MyService:
    def __init__(self, hal_bridge):
        self.hal = hal_bridge
        self._pin = None

    def initialize(self):
        self._pin = self.hal.create_pin("bit", "in", "plasmac.my-signal")

    def do_something(self):
        value = self.hal.get_value(self._pin)
        # ...
```

### Registering the Service

In `mainwindow.py`:

```python
from .my_service import MyService

class MainWindow(VCPMainWindow):
    def _init_services(self):
        # ... existing services ...
        self.my_service = MyService(self.hal)
        self.my_service.initialize()
```

## Adding Custom User Buttons

See [User Buttons](user-buttons.md) for configuration details.

## Custom G-code Filter

MonoKrom uses the `plasma_gcode_preprocessor` as the G-code filter. To create a custom
filter:

1. Create a Python module that implements the filter interface.
2. Register it in the INI file:
   ```ini
   [FILTER]
   PROGRAM_EXTENSION = .ngc GCode File (*.ngc)
   ngc = my_custom_filter
   ```
3. The filter module must be importable by Python.

## Customizing the Preview View

The VTK backplot can be customized through the INI file:

```ini
[VTK]
SPINDLE = jet_tracking_crosshair.stl
```

### View Controls

The preview window provides these view controls:

| Button | Function |
|--------|----------|
| **T** | Top-down full table view |
| **P** | Isometric (perspective) view |
| **Z** | Top-down centered on program |
| **Pan** | ← → ↑ ↓ buttons |
| **Zoom** | + / - buttons |
| **Clear** | C button clears the live plot |

## Customizing Jog Settings

Jog increments are configured in the INI file:

```ini
[DISPLAY]
INCREMENTS = JOG 10mm 5mm 1mm 0.1mm
```

Override limits:

```ini
[DISPLAY]
MAX_FEED_OVERRIDE = 2.000000
DEFAULT_LINEAR_VELOCITY = 50.0000
MAX_LINEAR_VELOCITY = 125.0000
MIN_LINEAR_VELOCITY = 0.5000
```

## Customizing File Locations

File locations are configured in `custom_config.yml`:

```yaml
file_locations:
  kwargs:
    default_location: NC Files
    local_locations:
      Home: ~/
      Desktop: ~/Desktop
      NC Files: ~/linuxcnc/nc_files
    # network_locations:
    #   DropBox: ~/DropBox/gcode
```

## Customizing Persistent Settings

Persistent settings are defined in `config.yml` and saved to the `.prefs` file. To add
new persistent settings:

```yaml
persistent_settings:
  my_setting:
    default: 0
    type: int
    widget: hal_spinbox
    label: "My Setting"
```

The setting will be automatically loaded, displayed in the UI, and saved to the prefs file.

## Customizing the G-code Editor

G-code editor styling is configured in `config.yml`:

```yaml
gcode_editor:
  kwargs:
    background: "#16160e"
    text_color: "#ffee06"
    current_line_color: "#ffee06"
    current_line_background: "#16160e"
    font_family: "Noto Sans Mono"
    font_size: 11
```

## Customizing the G-code Syntax Profile

Syntax highlighting is defined in `gcode_syntax.yml` (located in the config directory):

```yaml
version: 1
flat-token-groups: true
styles:
  - name: gcode
    color: "#ffee06"
  - name: mcode
    color: "#ffee06"
  - name: axis
    color: "#ffee06"
  # ... more styles
```

The INI file references this profile:

```ini
[DISPLAY]
GCODE_SYNTAX = gcode_syntax.yml
```

## Customizing the Window Title

The window title is set from the VCP info in `config.yml`:

```yaml
windows:
  mainwindow:
    kwargs:
      title: ( vcp.name ) ( vcp.version)
```

This produces a title like: `MonoKrom Plasma v0.0.5`

## Customizing the Menubar

The menubar is included from `default_menubar.yml` (commented out by default):

```yaml
#{% include "default_menubar.yml" %}
```

To use the default menubar, uncomment this line. To create a custom menubar, define
your own menu structure in the config.yml.
