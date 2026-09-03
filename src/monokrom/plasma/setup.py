"""
MonoKrom Plasma Config Installer — Core Module

Converts a qtplasmac configuration (from StepConf/PnCconf) into a
MonoKrom-compatible configuration. The hardware layer (HAL, INI
axis/joint settings) is preserved; only the VCP-specific layer is
transformed.

Classes:
    PrefsParser     — reads and parses .prefs file
    SettingsMapper  — maps .prefs keys to config.yml settings
    IniTransformer  — transforms INI file sections
    ConfigGenerator — orchestrates file copying, generation, logging
"""

import os
import re
import shutil
import logging
from datetime import datetime
from collections import OrderedDict

import yaml
import configparser


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PrefsParser
# ---------------------------------------------------------------------------

class PrefsParser:
    """Reads and parses a qtplasmac .prefs file.

    The .prefs file is INI-style.  Each section becomes a dict of
    key-value pairs in the ``parsed`` attribute.
    """

    # Sections we actually care about for migration.
    RELEVANT_SECTIONS = frozenset([
        'PLASMA_PARAMETERS',
        'GUI_OPTIONS',
        'BUTTONS',
        'ENABLE_OPTIONS',
        'LASER_OFFSET',
        'CAMERA_OFFSET',
        'OFFSET_PROBING',
        'CONVERSATIONAL',
        'SINGLE CUT',
        'STATISTICS',
        'POWERMAX',
        'COLOR_OPTIONS',
    ])

    def __init__(self, prefs_path):
        self.prefs_path = prefs_path
        self.parsed = OrderedDict()
        self._parse()

    # -- public -------------------------------------------------------------

    def get(self, section, key, default=None):
        """Return a value from the parsed prefs, or *default*."""
        return self.parsed.get(section, {}).get(key, default)

    def get_section(self, section):
        """Return the full dict for *section*, or empty dict."""
        return self.parsed.get(section, {})

    def get_button_codes(self):
        """Return a sorted list of (number, name, code) tuples for
        buttons that have both a name and a code."""
        buttons = self.get_section('BUTTONS')
        result = []
        idx = 1
        while True:
            name = buttons.get(f'{idx} Name', '').strip()
            code = buttons.get(f'{idx} Code', '').strip()
            if not name and not code:
                break
            if name and code:
                result.append((idx, name, code))
            idx += 1
        return result

    # -- internal -----------------------------------------------------------

    def _parse(self):
        if not os.path.isfile(self.prefs_path):
            raise FileNotFoundError(f'.prefs file not found: {self.prefs_path}')

        cp = configparser.ConfigParser(interpolation=None, strict=True)
        # Preserve case of keys (default is lowercasing)
        cp.optionxform = lambda x: x  # type: ignore[assignment]
        cp.read(self.prefs_path)

        for section in cp.sections():
            if section not in self.RELEVANT_SECTIONS:
                continue
            self.parsed[section] = OrderedDict()
            for key, value in cp.items(section):
                self.parsed[section][key] = value


# ---------------------------------------------------------------------------
# SettingsMapper
# ---------------------------------------------------------------------------

class SettingsMapper:
    """Maps .prefs keys to config.yml setting names and compares
    against MonoKrom defaults."""

    # .prefs key → (config.yml key, type hint for conversion)
    MAPPING = OrderedDict([
        ('Arc Voltage Offset',      ('arc_voltage_offset',      float)),
        ('Arc Voltage Scale',       ('arc_voltage_scale',       float)),
        ('THC Threshold',           ('thc_threshold',           float)),
        ('THC Delay',               ('thc_delay',               float)),
        ('Pid P Gain',              ('thc_pid_p_gain',          float)),
        ('Pid I Gain',              ('thc_pid_i_gain',          float)),
        ('Pid D Gain',              ('thc_pid_d_gain',          float)),
        ('Velocity Anti Dive Threshold', ('thc_vad_threshold',  float)),
        ('Safe Height',             ('thc_safe_height',         float)),
        ('Float Switch Travel',     ('probe_float_travel',      float)),
        ('Probe Feed Rate',         ('probe_speed',             float)),
        ('Probe Start Height',      ('probe_height',            float)),
        ('Ohmic Probe Offset',      ('probe_offset',            float)),
        ('Ohmic Maximum Attempts',  ('probe_ohmic_retries',     int)),
        ('Setup Feed Rate',         ('probe_setup_speed',       float)),
        ('Skip IHS Distance',       ('probe_skip_ihs',          float)),
        ('Arc Fail Timeout',        ('arc_fail_timeout',        float)),
        ('Arc Maximum Starts',      ('arc_max_starts',          int)),
        ('Arc Restart Delay',       ('arc_retry_delay',         float)),
        ('Arc OK High',             ('arc_ok_high_volts',       float)),
        ('Arc OK Low',              ('arc_ok_low_volts',        float)),
        ('Height Per Volt',         ('arc_height_per_volt',     float)),
        ('Scribe Arming Delay',     ('scribe_arm_delay',        float)),
        ('Scribe On Delay',         ('scribe_on_delay',         float)),
        ('Spotting Threshold',      ('spot_threshold',          float)),
        ('Spotting Time',           ('spot_delay',              float)),
        ('Offset Feed Rate',        ('consumable_xy_feed_rate', float)),
        ('Void Sense Slope',        ('thc_void_override',       float)),
    ])

    def __init__(self, config_yml_path):
        self.config_yml_path = config_yml_path
        self.defaults = self._load_defaults()

    # -- public -------------------------------------------------------------

    def map_settings(self, prefs):
        """Compare .prefs values against MonoKrom defaults.

        Returns (updated, skipped, not_found_prefs, not_found_config) where:
            updated       — list of (prefs_key, config_key, prefs_value, default_value)
            skipped       — list of (prefs_key, config_key, value)
            not_found_prefs — list of (config_key, default_value)
            not_found_config — list of (prefs_key, prefs_value)
        """
        updated = []
        skipped = []
        not_found_prefs = []
        not_found_config = []

        for prefs_key, (config_key, type_hint) in self.MAPPING.items():
            prefs_value = prefs.get('PLASMA_PARAMETERS', prefs_key)
            if prefs_value is None:
                not_found_config.append((prefs_key, None))
                continue

            try:
                prefs_value = type_hint(prefs_value)
            except (ValueError, TypeError):
                not_found_config.append((prefs_key, prefs_value))
                continue

            default_value = self.defaults.get(config_key)
            if default_value is None:
                not_found_config.append((prefs_key, prefs_value))
                continue

            if prefs_value != default_value:
                updated.append((prefs_key, config_key, prefs_value, default_value))
            else:
                skipped.append((prefs_key, config_key, prefs_value))

        # MonoKrom-only settings (in config.yml but not in .prefs)
        for config_key, default_value in self.defaults.items():
            if not any(config_key == ck for _, ck, *_ in updated) and not any(config_key == ck for _, ck, *_ in skipped):
                not_found_prefs.append((config_key, default_value))

        return updated, skipped, not_found_prefs, not_found_config

    def write_settings(self, config_yml_path, settings, output_path):
        """Write migrated settings into a copy of config.yml.

        *settings* is the list of (prefs_key, config_key, value, default)
        tuples from ``map_settings``.  Only settings that differ from
        the default are written.

        Returns the list of written keys.
        """
        with open(config_yml_path, 'r') as f:
            config = yaml.safe_load(f)

        written = []
        for prefs_key, config_key, value, _default in settings:
            if config is None or 'settings' not in config:
                config = {'settings': {}}
            config['settings'][config_key] = value
            written.append(config_key)

        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return written

    # -- internal -----------------------------------------------------------

    def _load_defaults(self):
        """Load the 'settings:' section from config.yml as a flat dict.

        The config.yml file may contain Jinja2 templates ({{ ... }})
        in non-settings sections, which yaml.safe_load cannot parse.
        We extract only the settings section using a regex-based
        approach.
        """
        if not os.path.isfile(self.config_yml_path):
            return {}

        with open(self.config_yml_path, 'r') as f:
            content = f.read()

        # Extract the settings section using regex
        # Match from 'settings:' to the next top-level key (not indented)
        settings_match = re.search(
            r'^settings:\s*\n((?:\s+.+\n?)*)',
            content,
            re.MULTILINE
        )

        defaults = {}
        if settings_match:
            settings_block = settings_match.group(1)
            # Parse the settings block as YAML
            settings_yaml = 'settings:\n' + settings_block
            try:
                settings = yaml.safe_load(settings_yaml)
            except yaml.YAMLError:
                logger.warning('Could not parse settings section, using empty defaults')
                return defaults

            settings = settings.get('settings', {}) or {}
            for key, node in settings.items():
                if isinstance(node, dict):
                    defaults[key] = node.get('default_value')
                else:
                    defaults[key] = node

        return defaults


# ---------------------------------------------------------------------------
# IniTransformer
# ---------------------------------------------------------------------------

class IniTransformer:
    """Transforms a qtplasmac INI file into a MonoKrom INI.

    Hardware sections (axis/joint limits, velocities, PID gains,
    stepgen settings) are preserved unchanged.  Only VCP-specific
    sections are modified.
    """

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.config = configparser.ConfigParser(interpolation=None, strict=True)
        self.config.optionxform = str  # type: ignore[assignment]
        # Allow duplicate keys by reading manually
        self._read_with_duplicates(ini_path)

    def _read_with_duplicates(self, ini_path):
        """Read INI file allowing duplicate keys (qtplasmac configs may have them).

        Multi-value keys (e.g. HALFILE) are joined with spaces.
        Single-value keys (e.g. POSITION_FEEDBACK) are replaced by the last occurrence.
        """
        if not os.path.isfile(ini_path):
            raise FileNotFoundError(f'INI file not found: {ini_path}')

        # Keys that are always single-value — last occurrence wins
        _SINGLE_VALUE_KEYS = frozenset([
            # [DISPLAY] single-value keys
            'POSITION_FEEDBACK', 'POSITION_OFFSET', 'DISPLAY', 'MAX_FEED_OVERRIDE',
            'INTRO_GRAPHIC', 'INTRO_TIME', 'PROGRAM_PREFIX', 'INCREMENTS',
            'DEFAULT_LINEAR_VELOCITY', 'MAX_LINEAR_VELOCITY', 'MIN_LINEAR_VELOCITY',
            'DEFAULT_ANGULAR_VELOCITY', 'MAX_ANGULAR_VELOCITY', 'MIN_ANGULAR_VELOCITY',
            'GEOMETRY', 'CYCLE_TIME', 'CONFIG_FILE',
            # [EMC] single-value keys
            'MACHINE', 'DEBUG', 'VERSION',
            # [FILTER] single-value keys
            'ngc', 'EXECUTION_TIME',
            # [TASK] single-value keys
            'MAXIMUM_TASK_TIME', 'MAXIMUM_TOOL_CHANGE_TIME',
            # [RS274NGC] single-value keys
            'SUBROUTINE_PATH', 'PARAMETER_FILE',
            # [EMCIO] single-value keys
            'TOOL_TABLE', 'DB_PROGRAM',
            # [KINS] single-value keys
            'JOINTS', 'KINEMATICS', 'TCP_OUTPUT', 'TCP_INPUT',
            # [TRAJ] single-value keys
            'COORDINATES', 'AXES',
            # [EMCMOT] single-value keys
            'BASE_PERIOD', 'SERVO_PERIOD',
            # [HAL] single-value keys (except HALFILE which is multi-value)
            'HALUI', 'POSTGUI_HALFILE',
            # Joint/axis single-value keys
            'HOME_OFFSET', 'HOME_SEARCH_SCALE', 'HOME_VEL',
            'HOME_FINAL_VELOCITY', 'HOME_IS_HOME', 'HOME_ALL',
            # PID tuning parameters
            'P', 'I', 'D', 'FF1', 'FF2', 'BANDWIDTH',
            # Stepgen parameters
            'STEPGEN_MAX_VEL', 'STEPGEN_SCALE', 'MAX_OUTPUT', 'MAX_ERROR', 'MIN_ERROR',
        ])

        current_section = None
        current_options = OrderedDict()

        with open(ini_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith(';'):
                    continue

                # Section header
                m = re.match(r'^\[(.+)\]$', line)
                if m:
                    # Save previous section
                    if current_section is not None:
                        for key, value in current_options.items():
                            self.config.set(current_section, key, value)
                    current_section = m.group(1)
                    current_options = OrderedDict()
                    if not self.config.has_section(current_section):
                        self.config.add_section(current_section)
                    continue

                # Skip lines outside any section
                if current_section is None:
                    continue

                # Key = Value
                m = re.match(r'^(\S+)\s*=\s*(.*)', line)
                if m and current_section is not None:
                    key, value = m.group(1), m.group(2).strip()
                    if key in _SINGLE_VALUE_KEYS:
                        # Single-value key: last occurrence wins
                        current_options[key] = value
                    else:
                        # Multi-value key: join with spaces
                        existing = current_options.get(key, '')
                        if existing:
                            current_options[key] = existing + ' ' + value
                        else:
                            current_options[key] = value
                    self.config.set(current_section, key, current_options[key])

        # Save the last section's options
        if current_section is not None:
            for key, value in current_options.items():
                self.config.set(current_section, key, value)

    # -- public -------------------------------------------------------------

    def set_display(self, display_name='monokrom_plasma'):
        """Replace DISPLAY value in [DISPLAY] section."""
        self.config.set('DISPLAY', 'DISPLAY', display_name)

    def remove_qtplasmac_section(self):
        """Remove the [QTPLASMAC] section if present."""
        self.config.remove_section('QTPLASMAC')

    def set_gcode_filter(self, program='plasma_gcode_preprocessor'):
        """Replace qtplasmac_gcode with plasma_gcode_preprocessor."""
        for key in list(self.config.options('FILTER')):
            if self.config.get('FILTER', key).strip() == 'qtplasmac_gcode':
                self.config.set('FILTER', key, program)

    def set_db_program(self, path='/usr/bin/plasma_tooldbpipe'):
        """Replace TOOL_TABLE with DB_PROGRAM in [EMCIO]."""
        self.config.remove_option('EMCIO', 'TOOL_TABLE')
        self.config.set('EMCIO', 'DB_PROGRAM', path)

    def add_python_section(self, path_prepend='./python'):
        """Add [PYTHON] section if python/ dir exists in config."""
        if not self.config.has_section('PYTHON'):
            self.config.add_section('PYTHON')
        self.config.set('PYTHON', 'PATH_PREPEND', path_prepend)
        self.config.set('PYTHON', 'PATH_APPEND', '../../nc_files/remap_lib/python-stdglue')
        self.config.set('PYTHON', 'TOPLEVEL', './python/toplevel.py')
        self.config.set('PYTHON', 'LOG_LEVEL', '10')

    def add_hmot_section(self, card='hm2_7i76e.0'):
        """Add [HMOT] section if not present."""
        if not self.config.has_section('HMOT'):
            self.config.add_section('HMOT')
        self.config.set('HMOT', 'CARD0', card)

    def add_user_buttons(self, buttons, prefix='USER'):
        """Add USER1/2/3_NAME and USER1/2/3_ACTION to [DISPLAY]."""
        for idx, name, code in buttons:
            if idx > 3:
                break
            safe_name = name.replace('\\', '_').replace(' ', '_')
            self.config.set('DISPLAY', f'{prefix}{idx}_NAME', safe_name)
            # Store the gcode code as the action filename stub
            action = code.split()[0] if code else ''
            if action:
                self.config.set('DISPLAY', f'{prefix}{idx}_ACTION', f'{action}.ngc')

    def add_halfile(self, filename):
        """Append a HALFILE entry to [HAL]."""
        existing = self.config.get('HAL', 'HALFILE', fallback='').split()
        if filename not in existing:
            existing.append(filename)
            self.config.set('HAL', 'HALFILE', ' '.join(existing))

    def set_subroutine_path(self):
        """Update SUBROUTINE_PATH in [RS274NGC] to include user_buttons."""
        current = self.config.get('RS274NGC', 'SUBROUTINE_PATH', fallback='')
        if './user_buttons' not in current:
            if current:
                # Insert user_buttons after the first ./:
                parts = current.split(':', 1)
                current = parts[0] + ':./user_buttons:' + parts[1]
            else:
                current = './user_buttons'
        self.config.set('RS274NGC', 'SUBROUTINE_PATH', current)

    def add_monokrom_display_options(self):
        """Add MonoKrom-specific DISPLAY options (JET, CONFIRM_EXIT, etc.)."""
        self.config.set('DISPLAY', 'JET', 'True')
        self.config.set('DISPLAY', 'CONFIRM_EXIT', 'False')
        self.config.set('DISPLAY', 'FULLSCREEN', 'True')
        self.config.set('DISPLAY', 'KEYBOARD_JOG', 'True')
        self.config.set('DISPLAY', 'HIDE_MENU_BAR', 'True')
        self.config.set('DISPLAY', 'GCODE_SYNTAX', 'gcode_syntax.yml')

    def add_vtk_section(self):
        """Add [VTK] section with SPINDLE model path."""
        if not self.config.has_section('VTK'):
            self.config.add_section('VTK')
        self.config.set('VTK', 'SPINDLE',
                        '/usr/lib/python3/dist-packages/qtpyvcp/widgets/display_widgets/vtk_backplot/models/jet_tracking_crosshair.stl')

    def add_plasmac_section(self, pressure='MPa', machine='Cutskill 60'):
        """Add [PLASMAC] section with machine details."""
        if not self.config.has_section('PLASMAC'):
            self.config.add_section('PLASMAC')
        self.config.set('PLASMAC', 'DEBOUNCE', 'TRUE')
        self.config.set('PLASMAC', 'PRESSURE', pressure)
        self.config.set('PLASMAC', 'MACHINE', machine)
        self.config.set('PLASMAC', 'DEFAULT_CUTCHART', '1')
        self.config.set('PLASMAC', 'SLAT_TOP', '-130')

    def add_hal_entries(self, source_dir):
        """Add TWOPASS and optional pendant HAL file to [HAL]."""
        if not self.config.has_section('HAL'):
            return
        self.config.set('HAL', 'TWOPASS', 'ON')
        xhc_hal = os.path.join(source_dir, 'xhc-whb04b-6.hal')
        if os.path.isfile(xhc_hal):
            existing = self.config.get('HAL', 'HALFILE', fallback='').split()
            if 'xhc-whb04b-6.hal' not in existing:
                existing.append('xhc-whb04b-6.hal')
                self.config.set('HAL', 'HALFILE', ' '.join(existing))

    def add_halui_mdi_commands(self):
        """Add MDI_COMMAND entries for pendant macros to [HALUI]."""
        if not self.config.has_section('HALUI'):
            self.config.add_section('HALUI')
        for i in range(17):
            # Use unique keys so configparser writes each as a separate line
            self.config.set('HALUI', f'MDI_COMMAND_{i}', f'(debug,macro{i}) # macro{i} pendant macro')

    def transform(self, prefs, output_path, source_dir=None, output_ini_name='monokrom.ini'):
        """Apply all transformations and write the output INI.

        Returns a dict of changes made: {section: [(option, old, new), ...]}
        """
        changes = {}

        # Display
        old_display = self.config.get('DISPLAY', 'DISPLAY', fallback='')
        self.set_display()
        if old_display != 'monokrom_plasma':
            changes.setdefault('DISPLAY', []).append(('DISPLAY', old_display, 'monokrom_plasma'))

        # CONFIG_FILE — required for VCP to locate its YAML config
        current_config_file = self.config.get('DISPLAY', 'CONFIG_FILE', fallback='')
        if current_config_file != 'custom_config.yml':
            self.config.set('DISPLAY', 'CONFIG_FILE', 'custom_config.yml')
            if current_config_file:
                changes.setdefault('DISPLAY', []).append(('CONFIG_FILE', current_config_file, 'custom_config.yml'))
            else:
                changes.setdefault('DISPLAY', []).append(('CONFIG_FILE', '', 'custom_config.yml'))

        # Remove qtplasmac section
        if self.config.has_section('QTPLASMAC'):
            self.remove_qtplasmac_section()
            changes['QTPLASMAC'] = [('REMOVED', 'present', 'removed')]

        # Gcode filter
        old_filter = self.config.get('FILTER', 'ngc', fallback='')
        self.set_gcode_filter()
        if old_filter != 'plasma_gcode_preprocessor':
            changes.setdefault('FILTER', []).append(('ngc', old_filter, 'plasma_gcode_preprocessor'))

        # EMCIO
        if self.config.has_option('EMCIO', 'TOOL_TABLE'):
            self.set_db_program()
            changes.setdefault('EMCIO', []).append(('TOOL_TABLE', 'tool.tbl', 'DB_PROGRAM'))

        # PYTHON section (if python/ dir exists in source)
        if not self.config.has_section('PYTHON'):
            self.add_python_section()
            changes['PYTHON'] = [('PATH_PREPEND', '', './python')]

        # Rename .hal file reference (pncconf-generated hardware layer)
        halfile = self.config.get('HAL', 'HALFILE', fallback='')
        if halfile:
            halfiles = halfile.split()
            renamed = False
            for i, hf in enumerate(halfiles):
                basename = os.path.basename(hf)
                if basename.endswith('.hal') and not basename.startswith('monokrom') and not basename.startswith('qtplasmac') and not basename.startswith('custom') and not basename.startswith('shutdown'):
                    halfiles[i] = 'monokrom.hal'
                    renamed = True
            if renamed:
                self.config.set('HAL', 'HALFILE', ' '.join(halfiles))
                changes.setdefault('HAL', []).append(('HALFILE', halfile, ' '.join(halfiles)))

        # User buttons from prefs
        buttons = prefs.get_button_codes() if prefs else []
        if buttons:
            self.add_user_buttons(buttons)
            changes['DISPLAY'] = changes.get('DISPLAY', [])
            for idx, name, code in buttons[:3]:
                safe_name = name.replace('\\', '_').replace(' ', '_')
                changes['DISPLAY'].append((f'{idx}_NAME', '', safe_name))

        # Subroutine path
        old_sub = self.config.get('RS274NGC', 'SUBROUTINE_PATH', fallback='')
        self.set_subroutine_path()
        new_sub = self.config.get('RS274NGC', 'SUBROUTINE_PATH')
        if old_sub != new_sub:
            changes.setdefault('RS274NGC', []).append(('SUBROUTINE_PATH', old_sub, new_sub))

        # MonoKrom display options
        self.add_monokrom_display_options()
        changes.setdefault('DISPLAY', []).append(('JET', '', 'True'))
        changes.setdefault('DISPLAY', []).append(('CONFIRM_EXIT', '', 'False'))
        changes.setdefault('DISPLAY', []).append(('FULLSCREEN', '', 'True'))
        changes.setdefault('DISPLAY', []).append(('KEYBOARD_JOG', '', 'True'))
        changes.setdefault('DISPLAY', []).append(('HIDE_MENU_BAR', '', 'True'))
        changes.setdefault('DISPLAY', []).append(('GCODE_SYNTAX', '', 'gcode_syntax.yml'))

        # [VTK] section
        self.add_vtk_section()
        changes['VTK'] = [('SPINDLE', '', 'jet_tracking_crosshair.stl')]

        # [PLASMAC] section
        pressure = 'MPa'
        machine = 'Cutskill 60'
        if prefs:
            pressure = prefs.get('PLASMA_PARAMETERS', 'Pressure Units', default='MPa') or 'MPa'
        self.add_plasmac_section(pressure, machine)
        changes['PLASMAC'] = [('DEBOUNCE', '', 'TRUE'), ('PRESSURE', '', pressure),
                              ('MACHINE', '', machine), ('DEFAULT_CUTCHART', '', '1'),
                              ('SLAT_TOP', '', '-130')]

        # [HAL] entries (TWOPASS, pendant HAL)
        if source_dir:
            self.add_hal_entries(source_dir)
            if self.config.has_option('HAL', 'TWOPASS'):
                changes.setdefault('HAL', []).append(('TWOPASS', '', 'ON'))
            xhc_hal = os.path.join(source_dir, 'xhc-whb04b-6.hal')
            if os.path.isfile(xhc_hal) and 'xhc-whb04b-6.hal' in self.config.get('HAL', 'HALFILE', fallback=''):
                changes.setdefault('HAL', []).append(('HALFILE', '', 'xhc-whb04b-6.hal'))

        # [HALUI] MDI commands for pendant macros
        self.add_halui_mdi_commands()
        changes['HALUI'] = [('MDI_COMMAND', '', '(debug,macro0) ... (debug,macro16)')]

        # Write output, splitting multi-value entries (HALFILE, etc.) into separate lines
        import io
        buf = io.StringIO()
        self.config.write(buf)
        content = buf.getvalue()

        # Split multi-value keys into separate lines
        multi_value_keys = {'HALFILE'}
        lines = content.split('\n')
        result = []
        for line in lines:
            stripped = line.strip()
            for mk in multi_value_keys:
                if stripped.startswith(mk + ' = ') or stripped.startswith(mk + '='):
                    # Split the value and create separate lines
                    prefix = line[:len(line) - len(line.lstrip())]
                    value = stripped.split('=', 1)[1].strip()
                    values = value.split()
                    for v in values:
                        result.append(f'{prefix}{mk} = {v}')
                    break
            else:
                # Rename MDI_COMMAND_N keys back to MDI_COMMAND
                import re
                m = re.match(r'^(\s*)MDI_COMMAND_(\d+)\s*=\s*(.*)', line)
                if m:
                    prefix, idx, value = m.group(1), m.group(2), m.group(3).strip()
                    result.append(f'{prefix}MDI_COMMAND = {value}')
                else:
                    result.append(line)

        with open(output_path, 'w') as f:
            f.write('\n'.join(result))

        return changes


# ---------------------------------------------------------------------------
# ConfigGenerator
# ---------------------------------------------------------------------------

class ConfigGenerator:
    """Orchestrates file copying, generation, and logging."""

    # Files that should be copied as-is from source to output
    COPY_AS_IS = [
        'custom.hal',
        'qtplasmac_comp.hal',
        'shutdown.hal',
        'ohmic.hal',
        'tool.tbl',
        'M159',
        'M190',
    ]

    # Template-based files (copied from templates if not present in source)
    TEMPLATE_FILES = [
        'plasma_table.db',
    ]

    # Known .hal files that may be present
    OPTIONAL_HAL = [
        'xhc-whb04b-6.hal',
        'joypad.hal',
        'joypad_preloader.hal',
    ]

    def __init__(self, source_dir, output_dir, config_yml_path=None, log_path=None, vcp_options=None):
        self.source_dir = os.path.abspath(source_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.config_yml_path = config_yml_path
        self.log_path = log_path or os.path.join(self.output_dir, 'setup.log')
        self.log_lines = []
        self.vcp_options = vcp_options or {
            'confirm_exit': False,
            'fullscreen': False,
            'file_locations': [],
            'import_buttons': True,
        }
        self._config_yml_path_resolved = None

    # -- public API ---------------------------------------------------------

    def generate(self, prefs, ini_transformer, settings_mapper, auto=False):
        """Run the full generation pipeline.

        Steps:
            1. Create output directory
            2. Copy hardware files as-is
            3. Transform and write INI
            4. Generate postgui.hal template
            5. Generate custom_postgui.hal
            6. Generate custom_config.yml
            7. Generate user_buttons/
            8. Copy python/ directory if present
            9. Copy gcode_syntax.yml from sim if not present
            10. Write setup.log
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # Resolve config_yml_path if not provided
        if self.config_yml_path is None:
            self.config_yml_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(__file__)))),
                'plasma', 'config.yml'
            )

        self._log(f'=== MonoKrom Plasma Setup ===')
        self._log(f'Source config: {self.source_dir}')
        self._log(f'Output config: {self.output_dir}')
        self._log(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self._log('')

        # Settings migration
        self._log('--- Settings Migration ---')
        if settings_mapper and prefs:
            updated, skipped, not_found_prefs, not_found_config = settings_mapper.map_settings(prefs)
            for prefs_key, config_key, value, default in updated:
                self._log(f'[UPDATED] {prefs_key}: {value} -> {value} (config.yml {config_key})')
            for prefs_key, config_key, value in skipped:
                self._log(f'[SKIPPED] {prefs_key}: {value} (matches MonoKrom default)')
            for config_key, default in not_found_prefs:
                self._log(f'[NOT_FOUND_IN_PREFS] {config_key}: {default} (using MonoKrom default)')
            for prefs_key, value in not_found_config:
                display_val = value if value is not None else '(empty)'
                self._log(f'[NOT_FOUND_IN_CONFIG] {prefs_key}: {display_val} (qtplasmac-only setting)')
        else:
            self._log('  (skipped — no settings mapper or prefs provided)')
        self._log('')

        # INI transformation
        self._log('--- INI Transformations ---')
        changes = ini_transformer.transform(prefs, os.path.join(self.output_dir, 'monokrom.ini'), source_dir=self.source_dir)
        for section, items in changes.items():
            for option, old, new in items:
                self._log(f'[{section}] {option}: {old} -> {new}')
        self._log('')

        # Copy files as-is
        self._log('--- Files Copied ---')
        copied = []
        for fname in self.COPY_AS_IS:
            src = os.path.join(self.source_dir, fname)
            dst = os.path.join(self.output_dir, fname)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                copied.append(fname)
                self._log(f'  {fname}')

        # Optional HAL files
        for fname in self.OPTIONAL_HAL:
            src = os.path.join(self.source_dir, fname)
            dst = os.path.join(self.output_dir, fname)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                copied.append(fname)
                self._log(f'  {fname}')

        # Rename source HAL file to monokrom.hal (pncconf-generated hardware layer)
        src_ini = os.path.join(self.source_dir, os.path.basename(ini_transformer.ini_path))
        halfile = ''
        try:
            src_config = configparser.ConfigParser()
            src_config.read(src_ini, encoding='utf-8')
            halfile = src_config.get('HAL', 'HALFILE', fallback='')
        except configparser.DuplicateOptionError:
            # Source INI has duplicate keys (e.g. POSITION_FEEDBACK); read HALFILE manually
            in_hal = False
            with open(src_ini, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('['):
                        in_hal = line.strip('[]').lower() == 'hal'
                    elif in_hal and line.lower().startswith('halfile'):
                        halfile = line.split('=', 1)[1].strip()
                        break
        if halfile:
            halfiles = halfile.split()
            for hf in halfiles:
                basename = os.path.basename(hf)
                if basename.endswith('.hal') and not basename.startswith('monokrom') and not basename.startswith('qtplasmac') and not basename.startswith('custom') and not basename.startswith('shutdown'):
                    src = os.path.join(self.source_dir, basename)
                    dst = os.path.join(self.output_dir, 'monokrom.hal')
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                        copied.append(f'{basename} -> monokrom.hal')
                        self._log(f'  {basename} -> monokrom.hal')
                    break
        self._log('')

        # Copy template-based files
        self._log('--- Files from Templates ---')
        for fname in self.TEMPLATE_FILES:
            templates_path = os.path.join(
                os.path.dirname(self.config_yml_path),
                '..', '..', '..', 'linuxcnc', 'configs', 'templates', 'plasmac', fname
            )
            templates_path = os.path.normpath(templates_path)
            dst = os.path.join(self.output_dir, fname)
            if os.path.isfile(templates_path):
                shutil.copy2(templates_path, dst)
                self._log(f'  {fname} (from templates)')
            else:
                self._log(f'  {fname} (template not found)')
        self._log('')

        # Generate postgui.hal
        self._log('--- Files Generated ---')
        self._generate_postgui_hal()
        self._log('  postgui.hal (static template)')

        self._generate_custom_postgui_hal()
        self._log('  custom_postgui.hal (sources postgui.hal)')

        self._generate_custom_config_yml()
        self._log('  custom_config.yml (VCP config)')

        # Copy gcode_syntax.yml from sim if not in source
        self._copy_gcode_syntax()
        self._log('')

        # Generate user_buttons/
        self._log('--- Files Derived ---')
        self._generate_user_buttons(prefs)
        self._log('')

        # Copy python/ if present
        self._copy_python_dir()

        # Write log
        self._write_log()

        self._log('')
        self._log('=== Setup Complete ===')
        return self.log_lines

    # -- internal -----------------------------------------------------------

    def _generate_postgui_hal(self):
        """Generate postgui.hal from the templates directory."""
        output_path = os.path.join(self.output_dir, 'postgui.hal')

        # Build path to templates: from config.yml go up to project root, then linuxcnc/configs/templates/plasmac
        templates_dir = os.path.join(
            os.path.dirname(self.config_yml_path),
            '..', '..', '..', 'linuxcnc', 'configs', 'templates', 'plasmac', 'postgui.hal'
        )
        templates_dir = os.path.normpath(templates_dir)

        if os.path.isfile(templates_dir):
            shutil.copy2(templates_dir, output_path)
        else:
            # Fallback: try sim.monokrom relative to config.yml
            sim_postgui = os.path.join(
                os.path.dirname(self.config_yml_path),
                '..', '..', 'sim.monokrom', 'plasmac', 'postgui_plasmac_sim.hal'
            )
            sim_postgui = os.path.normpath(sim_postgui)

            if os.path.isfile(sim_postgui):
                shutil.copy2(sim_postgui, output_path)
            else:
                # Inline fallback — the base set of VCP→plasmac nets
                lines = [
                    '# MonoKrom postgui.hal — auto-generated from sim template',
                    '# Keep your post GUI customisations here.',
                    '',
                    'net plasmac:axis-z-max-limit     ini.z.max_limit             =>  plasmac.axis-z-max-limit',
                    'net plasmac:axis-z-min-limit     ini.z.min_limit             =>  plasmac.axis-z-min-limit',
                    'net plasmac:axis-x-max-limit     ini.x.max_limit             =>  plasmac.axis-x-max-limit',
                    'net plasmac:axis-x-min-limit     ini.x.min_limit             =>  plasmac.axis-x-min-limit',
                    'net plasmac:axis-y-max-limit     ini.y.max_limit             =>  plasmac.axis-y-max-limit',
                    'net plasmac:axis-y-min-limit     ini.y.min_limit             =>  plasmac.axis-y-min-limit',
                    '',
                    '# Inputs',
                    'net plasmac:cornerlock-enable                qtpyvcp.plasma-vad.checked => plasmac.cornerlock-enable',
                    'net plasmac:cornerlock-threshold          qtpyvcp.thc-vad-threshold.out => plasmac.cornerlock-threshold',
                    'net plasmac:cut-feed-rate                 qtpyvcp.param-cutfeedrate.out => plasmac.cut-feed-rate',
                    'net plasmac:cut-height                      qtpyvcp.param-cutheight.out => plasmac.cut-height',
                    'net plasmac:cut-volts                        qtpyvcp.param-cutvolts.out => plasmac.cut-volts',
                    'net plasmac:arc-voltage-scale             qtpyvcp.arc-voltage-scale.out => plasmac.arc-voltage-scale',
                    'net plasmac:arc-voltage-offset           qtpyvcp.arc-voltage-offset.out => plasmac.arc-voltage-offset',
                    'net plasmac:float-switch-travel          qtpyvcp.probe-float-travel.out => plasmac.float-switch-travel',
                    'net plasmac:height-override                qtpyvcp.voltage-override.out => plasmac.height-override',
                    'net plasmac:height-per-volt             qtpyvcp.arc-height-per-volt.out => plasmac.height-per-volt',
                    'net plasmac:mesh-enable               qtpyvcp.plasma-mesh-sense.checked => plasmac.mesh-enable',
                    'net plasmac:probe-feed-rate                     qtpyvcp.probe-speed.out => plasmac.probe-feed-rate',
                    'net plasmac:probe-start-height                 qtpyvcp.probe-height.out => plasmac.probe-start-height',
                    'net plasmac:ohmic-max-attempts          qtpyvcp.probe-ohmic-retries.out => plasmac.ohmic-max-attempts',
                    'net plasmac:ohmic-probe-enable    qtpyvcp.ohmic-sensing-enabled.checked => plasmac.ohmic-probe-enable',
                    'net plasmac:ohmic-probe-offset                 qtpyvcp.probe-offset.out => plasmac.ohmic-probe-offset',
                    'net plasmac:setup-feed-rate               qtpyvcp.probe-setup-speed.out => plasmac.setup-feed-rate',
                    'net plasmac:skip-ihs-distance                qtpyvcp.probe-skip-ihs.out => plasmac.skip-ihs-distance',
                    'net plasmac:pause-at-end                   qtpyvcp.param-pauseatend.out => plasmac.pause-at-end',
                    'net plasmac:pierce-delay                  qtpyvcp.param-piercedelay.out => plasmac.pierce-delay',
                    'net plasmac:pierce-height                qtpyvcp.param-pierceheight.out => plasmac.pierce-height',
                    'net plasmac:puddle-jump-delay         qtpyvcp.param-puddlejumpdelay.out => plasmac.puddle-jump-delay',
                    'net plasmac:puddle-jump-height       qtpyvcp.param-puddlejumpheight.out => plasmac.puddle-jump-height',
                    'net plasmac:restart-delay                   qtpyvcp.arc-retry-delay.out => plasmac.restart-delay',
                    'net plasmac:arc-fail-delay                 qtpyvcp.arc-fail-timeout.out => plasmac.arc-fail-delay',
                    'net plasmac:arc-max-starts                   qtpyvcp.arc-max-starts.out => plasmac.arc-max-starts',
                    'net plasmac:scribe-arm-delay               qtpyvcp.scribe-arm-delay.out => plasmac.scribe-arm-delay',
                    'net plasmac:scribe-on-delay                 qtpyvcp.scribe-on-delay.out => plasmac.scribe-on-delay',
                    'net plasmac:spotting-threshold               qtpyvcp.spot-threshold.out => plasmac.spotting-threshold',
                    'net plasmac:spotting-time                        qtpyvcp.spot-delay.out => plasmac.spotting-time',
                    'net plasmac:thc-enable                      qtpyvcp.thc-enabled.checked => plasmac.thc-enable',
                    'net plasmac:thc-delay                             qtpyvcp.thc-delay.out => plasmac.thc-delay',
                    'net plasmac:thc-feed-rate                                                  plasmac.thc-feed-rate',
                    'net plasmac:thc-threshold                     qtpyvcp.thc-threshold.out => plasmac.thc-threshold',
                    'net plasmac:pid-d-gain                       qtpyvcp.thc-pid-d-gain.out => plasmac.pid-d-gain',
                    'net plasmac:pid-i-gain                       qtpyvcp.thc-pid-i-gain.out => plasmac.pid-i-gain',
                    'net plasmac:pid-p-gain                       qtpyvcp.thc-pid-p-gain.out => plasmac.pid-p-gain',
                    'net plasmac:safe-height                     qtpyvcp.thc-safe-height.out => plasmac.safe-height',
                    'net plasmac:use-auto-volts            qtpyvcp.plasma-auto-volts.checked => plasmac.use-auto-volts',
                    'net plasmac:torch-enable                   qtpyvcp.torch-enable.checked => plasmac.torch-enable',
                    'net plasmac:torch-pulse                  qtpyvcp.plasma-torch-pulse.out => plasmac.torch-pulse-start',
                    'net plasmac:torch-pulse-time         qtpyvcp.plasma-torch-pulse-sec.out => plasmac.torch-pulse-time',
                    'net plasmac:arc-ok-high                   qtpyvcp.arc-ok-high-volts.out => plasmac.arc-ok-high',
                    'net plasmac:arc-ok-low                     qtpyvcp.arc-ok-low-volts.out => plasmac.arc-ok-low',
                    'net plasmac:xy-feed-rate            qtpyvcp.consumable-xy-feed-rate.out => plasmac.xy-feed-rate',
                    'net plasmac:laser-on                <= qtpyvcp.laser.checked',
                    '',
                    '# Outputs',
                    'net plasmac:consumable-changing     plasmac.consumable-changing         => qtpyvcp.led-change-consumable.on',
                    'net plasmac:cornerlock-is-locked    plasmac.cornerlock-is-locked        => qtpyvcp.led-corner-lock.on',
                    'net plasmac:led-down                plasmac.led-down                    => qtpyvcp.led-thc-down.on',
                    'net plasmac:led-up                  plasmac.led-up                      => qtpyvcp.led-thc-up.on',
                    'net plasmac:pierce-count            plasmac.pierce-count',
                    'net plasmac:probe-test-error        plasmac.probe-test-error',
                    'net plasmac:state                   plasmac.state-out',
                    'net plasmac:thc-active              plasmac.thc-active                  => qtpyvcp.led-thc-active.on',
                    'net plasmac:z-height                plasmac.z-height',
                    'net plasmac:arc-ok-out              plasmac.arc-ok-out                  => qtpyvcp.led-arc-ok.on',
                    'net plasmac:torch-on                plasmac.torch-on                    => qtpyvcp.led-torch-on.on',
                    'net plasmac:cut-length              plasmac.cut-length                  => qtpyvcp.stats-cut-length.in',
                    'net plasmac:cut-time                plasmac.cut-time                    => qtpyvcp.stats-cut-time.in',
                    '',
                    '# Cycle Start Connections',
                    'net plasmac:program-is-paused                                           => qtpyvcp.cycle-start.program-is-paused',
                    'net plasmac:program-is-running                                          => qtpyvcp.cycle-start.program-is-running',
                    'net plasmac:program-is-idle                                             => qtpyvcp.cycle-start.program-is-idle',
                    'net plasmac:machine-is-homed                                            => qtpyvcp.cycle-start.enable',
                    '',
                    '# Feed and Current Velocity display links',
                    'net plasmac:feed-upm                                                    => qtpyvcp.mk-feedrate.in',
                    'net plasmac:current-velocity                                            => qtpyvcp.mk-current-velcoity.in',
                ]
                with open(output_path, 'w') as f:
                    f.write('\n'.join(lines) + '\n')

    def _generate_custom_postgui_hal(self):
        """Generate custom_postgui.hal that sources postgui.hal."""
        output_path = os.path.join(self.output_dir, 'custom_postgui.hal')
        content = (
            '# Include your custom_postgui HAL commands here\n'
            '# This file will not be overwritten when you run PNCconf again\n'
            'source postgui.hal\n'
            '#source joypad.hal\n'
        )
        with open(output_path, 'w') as f:
            f.write(content)

    def _generate_custom_config_yml(self):
        """Generate custom_config.yml using wizard-collected VCP options."""
        output_path = os.path.join(self.output_dir, 'custom_config.yml')

        # Build local_locations from wizard input or defaults
        wizard_locs = self.vcp_options.get('file_locations', [])
        if wizard_locs:
            local_locations = {}
            for loc in wizard_locs:
                if ':' in loc:
                    name, path = loc.split(':', 1)
                    local_locations[name.strip()] = path.strip()
        else:
            local_locations = {
                'Home': '~/',
                'Desktop': '~/Desktop',
                'NC Files': '~/linuxcnc/nc_files',
            }

        lines = [
            '# MonoKrom Plasma VCP config — auto-generated',
            'windows:',
            '  mainwindow:',
            '    kwargs:',
            f'      confirm_exit: {"true" if self.vcp_options.get("confirm_exit") else "false"}',
            f'      fullscreen: {"true" if self.vcp_options.get("fullscreen") else "false"}',
            '',
            'data_plugins:',
            '  file_locations:',
            '      provider: qtpyvcp.plugins.file_locations:FileLocations',
            '      log_level: debug',
            '      kwargs:',
            '        default_location: NC Files',
            '        local_locations:',
        ]
        for name, path in local_locations.items():
            lines.append(f'          {name}: {path}')

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

    def _copy_gcode_syntax(self):
        """Copy gcode_syntax.yml from templates, source, or sim."""
        src = os.path.join(self.source_dir, 'gcode_syntax.yml')
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(self.output_dir, 'gcode_syntax.yml'))
            return

        # Try templates directory
        templates_path = os.path.join(
            os.path.dirname(self.config_yml_path),
            '..', '..', '..', 'linuxcnc', 'configs', 'templates', 'plasmac', 'gcode_syntax.yml'
        )
        templates_path = os.path.normpath(templates_path)
        if os.path.isfile(templates_path):
            shutil.copy2(templates_path, os.path.join(self.output_dir, 'gcode_syntax.yml'))
            return

        # Fallback to sim
        sim_path = os.path.join(
            os.path.dirname(self.config_yml_path),
            '..', '..', 'sim.monokrom', 'plasmac', 'gcode_syntax.yml'
        )
        sim_path = os.path.normpath(sim_path)
        if os.path.isfile(sim_path):
            shutil.copy2(sim_path, os.path.join(self.output_dir, 'gcode_syntax.yml'))
            self._log('  gcode_syntax.yml (from sim)')

    def _generate_user_buttons(self, prefs):
        """Generate user_buttons/ .ngc files from .prefs BUTTONS section."""
        buttons = prefs.get_button_codes() if prefs else []
        if not buttons:
            return

        buttons_dir = os.path.join(self.output_dir, 'user_buttons')
        os.makedirs(buttons_dir, exist_ok=True)

        for idx, name, code in buttons:
            # Create a filename from the code (first word, stripped of spaces)
            base = code.split()[0] if code else f'button_{idx}'
            filename = f'{base}.ngc'
            filepath = os.path.join(buttons_dir, filename)

            # Convert name for sub name (replace \ with _)
            sub_name = name.replace('\\', '_').replace(' ', '_').lower()

            content = (
                f'; User button: {name}\n'
                f'; Generated by MonoKrom setup\n'
                f'O<{sub_name}> sub\n'
                f'{code}\n'
                f'O<{sub_name}> endsub\n'
                f'M2\n'
            )
            with open(filepath, 'w') as f:
                f.write(content)
            self._log(f'  user_buttons/{filename} (from {name})')

    def _copy_python_dir(self):
        """Copy python/ directory if present in source."""
        src = os.path.join(self.source_dir, 'python')
        dst = os.path.join(self.output_dir, 'python')
        if os.path.isdir(src):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            self._log('  python/ (directory copied)')

    # -- logging ------------------------------------------------------------

    def _log(self, message):
        self.log_lines.append(message)
        logger.info(message)

    def _write_log(self):
        with open(self.log_path, 'w') as f:
            f.write('\n'.join(self.log_lines) + '\n')


# ---------------------------------------------------------------------------
# Interactive Wizard
# ---------------------------------------------------------------------------

class Wizard:
    """CLI-based interactive wizard for the setup command.

    Implements the 6-step wizard flow:
    1. Select qtplasmac config directory
    2. Review detected hardware
    3. Review settings migration (with toggle support)
    4. Configure VCP options
    5. Review generated files
    6. Confirm and generate
    """

    def __init__(self, source_dir, output_dir=None, config_yml_path=None):
        self.source_dir = os.path.abspath(source_dir)
        self.output_dir = output_dir
        self.config_yml_path = config_yml_path
        self.prefs = None
        self.ini_transformer = None
        self.settings_mapper = None
        self.generator = None
        self.updated_settings = []
        self.skipped_settings = []
        self.not_found_prefs = []
        self.not_found_config = []
        self.vcp_options = {
            'confirm_exit': False,
            'fullscreen': False,
            'file_locations': [],
            'import_buttons': True,
        }
        self.user_buttons_override = []
        self.selected_config = None

    # -- public -------------------------------------------------------------

    def run(self):
        """Execute the full wizard flow."""
        print('\n' + '=' * 60)
        print('  MonoKrom Plasma Config Setup Wizard')
        print('=' * 60)
        print()

        # Step 1: Select config directory
        self._step1_select_config()

        # Step 2: Review hardware
        self._step2_review_hardware()

        # Step 3: Review settings migration
        self._step3_review_settings()

        # Step 4: Configure VCP options
        self._step4_configure_vcp()

        # Step 5: Review generated files
        self._step5_review_files()

        # Step 6: Confirm and generate
        self._step6_generate()

    # -- step 1: select config ----------------------------------------------

    def _step1_select_config(self):
        """Scan ~/linuxcnc/configs/ for qtplasmac configs and let user select."""
        print('Step 1/6: Select qtplasmac config directory')
        print('-' * 60)

        linuxcnc_configs = os.path.expanduser('~/linuxcnc/configs')
        if not os.path.isdir(linuxcnc_configs):
            print(f'Error: {linuxcnc_configs} not found.')
            print('Please specify --from-config <path> instead.')
            raise SystemExit(1)

        # Scan for .ini files with qtplasmac/qt in display
        configs = []
        for fname in sorted(os.listdir(linuxcnc_configs)):
            if not fname.endswith('.ini'):
                continue
            ini_path = os.path.join(linuxcnc_configs, fname)
            try:
                with open(ini_path) as f:
                    content = f.read()
                if 'qtplasmac' in content.lower() or 'qt' in content.lower():
                    # Extract machine name from [EMC] MACHINE
                    m = re.search(r'\[EMC\]\s*\n\s*MACHINE\s*=\s*(.+)', content)
                    machine = m.group(1).strip() if m else 'Unknown'
                    configs.append((ini_path, machine))
            except (IOError, OSError):
                continue

        # If source_dir was provided, use it; otherwise let user choose
        if self.source_dir != linuxcnc_configs:
            # Use provided path directly
            if os.path.isfile(self.source_dir):
                self.selected_config = self.source_dir
                print(f'Selected: {self.source_dir}')
            elif os.path.isdir(self.source_dir):
                # Look for .ini files in the directory
                ini_files = []
                for fname in sorted(os.listdir(self.source_dir)):
                    if fname.endswith('.ini'):
                        ini_files.append(os.path.join(self.source_dir, fname))
                if ini_files:
                    self.selected_config = ini_files[0]
                    print(f'Selected: {self.selected_config}')
                else:
                    print(f'No .ini files found in {self.source_dir}')
                    raise SystemExit(1)
            else:
                print(f'Path not found: {self.source_dir}')
                raise SystemExit(1)
        else:
            if not configs:
                print('No qtplasmac configs found.')
                raise SystemExit(1)

            print(f'Found {len(configs)} qtplasmac config(s):')
            print()
            for i, (path, machine) in enumerate(configs, 1):
                print(f'  {i}. {os.path.basename(path)} ({machine})')
                print(f'     {path}')
            print()

            while True:
                choice = input('Select config number (or path): ').strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(configs):
                        self.selected_config = configs[idx][0]
                        break
                elif os.path.isfile(choice):
                    self.selected_config = choice
                    break
                print('Invalid selection.')

        # Extract source directory from ini path
        self.source_dir = os.path.dirname(self.selected_config)
        print(f'Source: {self.source_dir}')
        print()

    # -- step 2: review hardware --------------------------------------------

    def _step2_review_hardware(self):
        """Parse INI and prefs, display hardware info."""
        print('Step 2/6: Detected hardware')
        print('-' * 60)

        # Parse INI for hardware info (strict=False to handle duplicates in qtplasmac configs)
        ini_cp = configparser.ConfigParser(interpolation=None, strict=False)
        ini_cp.optionxform = str  # type: ignore[assignment]
        ini_cp.read(self.selected_config)

        # Parse prefs
        prefs_file = None
        for fname in os.listdir(self.source_dir):
            if fname.endswith('.prefs'):
                prefs_file = os.path.join(self.source_dir, fname)
                break

        if not prefs_file:
            raise FileNotFoundError(f'No .prefs file in {self.source_dir}')

        self.prefs = PrefsParser(prefs_file)

        # Extract hardware info
        machine = ini_cp.get('EMC', 'MACHINE', fallback='Unknown')
        joints = ini_cp.get('KINS', 'JOINTS', fallback='?')
        axes = ini_cp.get('TRAJ', 'COORDINATES', fallback='XYZ')

        # Detect controller from HAL files
        controller = 'Unknown'
        for fname in os.listdir(self.source_dir):
            if fname.endswith('.hal'):
                try:
                    with open(os.path.join(self.source_dir, fname)) as f:
                        if 'hm2' in f.read():
                            controller = 'HM2 (7i76E/etc)'
                            break
                        elif 'parport' in f.read():
                            controller = 'Parport'
                            break
                except IOError:
                    pass

        # Get plasma machine type and pressure from prefs
        plasma_params = self.prefs.get_section('PLASMA_PARAMETERS')
        pressure = ini_cp.get('PLASMAC', 'PRESSURE', fallback='Unknown')

        print(f'  Machine:      {machine}')
        print(f'  Axes:         {axes} ({joints} joints)')
        print(f'  Controller:   {controller}')
        print(f'  Pressure:     {pressure}')
        print()
        print('Press Enter to continue...')
        input()

    # -- step 3: review settings --------------------------------------------

    def _step3_review_settings(self):
        """Show settings migration table, allow toggling."""
        print('Step 3/6: Settings migration')
        print('-' * 60)

        self.settings_mapper = SettingsMapper(
            self.config_yml_path or os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(__file__)))),
                'plasma', 'config.yml'
            )
        )

        self.updated_settings, self.skipped_settings, self.not_found_prefs, self.not_found_config = \
            self.settings_mapper.map_settings(self.prefs)

        # Display updated settings
        if self.updated_settings:
            print(f'\n{len(self.updated_settings)} settings differ from MonoKrom defaults:')
            print()
            print(f'  {"#":<4} {"Prefs Key":<30} {"Current":>10} {"Default":>10}  {"Action"}')
            print(f'  {"-"*4} {"-"*30} {"-"*10} {"-"*10}  {"-"*12}')
            for i, (prefs_key, config_key, value, default) in enumerate(self.updated_settings, 1):
                print(f'  {i:<4} {prefs_key:<30} {str(value):>10} {str(default):>10}  KEEP')
            print()
            print('  Toggle settings to skip (enter numbers separated by commas):')
            while True:
                choice = input('  Indices to skip (or Enter to continue): ').strip()
                if not choice:
                    break
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip()]
                    for idx in indices:
                        if 1 <= idx <= len(self.updated_settings):
                            self.updated_settings[idx - 1] = None
                    self.updated_settings = [s for s in self.updated_settings if s is not None]
                    print(f'  {len(self.updated_settings)} settings remaining.')
                    break
                except ValueError:
                    print('  Please enter numbers separated by commas (e.g. 1,3).')

        # Display skipped settings
        if self.skipped_settings:
            print(f'{len(self.skipped_settings)} settings match defaults (no change needed).')
            print()
            print(f'  {"#":<4} {"Prefs Key":<30} {"Value":>10}')
            print(f'  {"-"*4} {"-"*30} {"-"*10}')
            for i, (prefs_key, config_key, value) in enumerate(self.skipped_settings, 1):
                print(f'  {i:<4} {prefs_key:<30} {str(value):>10}')
            print()
            print('  Force-update any settings to a non-default value (enter numbers separated by commas):')
            while True:
                choice = input('  Indices to force (or Enter to continue): ').strip()
                if not choice:
                    break
                try:
                    indices = [int(x.strip()) for x in choice.split(',') if x.strip()]
                    for idx in indices:
                        if 1 <= idx <= len(self.skipped_settings):
                            self.skipped_settings[idx - 1] = None
                    self.skipped_settings = [s for s in self.skipped_settings if s is not None]
                    print(f'  {len(self.skipped_settings)} settings remaining (will stay at default).')
                    break
                except ValueError:
                    print('  Please enter numbers separated by commas (e.g. 1,3).')

        # Display not-found-in-config (qtplasmac-only)
        if self.not_found_config:
            print(f'{len(self.not_found_config)} settings have no MonoKrom equivalent:')
            for prefs_key, value in self.not_found_config[:5]:
                display_val = value if value is not None else '(empty)'
                print(f'  - {prefs_key}: {display_val}')
            if len(self.not_found_config) > 5:
                print(f'  ... and {len(self.not_found_config) - 5} more')
            print()

        # Display not-found-in-prefs (MonoKrom-only)
        if self.not_found_prefs:
            print(f'{len(self.not_found_prefs)} MonoKrom-only settings (will use defaults):')
            for config_key, default in self.not_found_prefs[:5]:
                print(f'  - {config_key}: {default}')
            if len(self.not_found_prefs) > 5:
                print(f'  ... and {len(self.not_found_prefs) - 5} more')
            print()

        print('Press Enter to continue...')
        input()

    # -- step 4: configure VCP options --------------------------------------

    def _step4_configure_vcp(self):
        """Configure VCP-specific options."""
        print('Step 4/6: VCP options')
        print('-' * 60)

        # confirm_exit
        while True:
            choice = input('Confirm exit dialog? [y/N]: ').strip().lower()
            if choice in ('y', 'yes', 'n', 'no', ''):
                self.vcp_options['confirm_exit'] = choice in ('y', 'yes')
                break
            print('Please enter y or n.')

        # fullscreen
        while True:
            choice = input('Start fullscreen? [y/N]: ').strip().lower()
            if choice in ('y', 'yes', 'n', 'no', ''):
                self.vcp_options['fullscreen'] = choice in ('y', 'yes')
                break
            print('Please enter y or n.')

        # file locations
        print()
        print('NC file locations (one per line, blank line to finish):')
        print('  Format: Name: path')
        locations = []
        while True:
            line = input('  > ').strip()
            if not line:
                break
            if ':' in line:
                locations.append(line)
        self.vcp_options['file_locations'] = locations

        # user buttons
        print()
        buttons = self.prefs.get_button_codes() if self.prefs else []
        if buttons:
            print(f'Found {len(buttons)} user buttons in .prefs:')
            for idx, name, code in buttons:
                print(f'  {idx}. {name}: {code}')
            print()
            while True:
                choice = input('Import user buttons? [Y/n]: ').strip().lower()
                if choice in ('y', 'yes', 'n', 'no', ''):
                    self.vcp_options['import_buttons'] = choice not in ('n', 'no')
                    break
                print('Please enter y or n.')
        print()
        print('Press Enter to continue...')
        input()

    # -- step 5: review generated files -------------------------------------

    def _step5_review_files(self):
        """Show summary of files to be generated/copied."""
        print('Step 5/6: Generated files summary')
        print('-' * 60)

        # Determine output directory
        if self.output_dir is None:
            base = os.path.basename(self.source_dir)
            if base.startswith('monokrom_'):
                self.output_dir = self.source_dir
            else:
                self.output_dir = os.path.join(os.path.dirname(self.source_dir), f'monokrom_{base}')

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Show INI changes preview
        self.ini_transformer = IniTransformer(self.selected_config)
        changes = self.ini_transformer.transform(self.prefs, os.path.join(self.output_dir, 'monokrom.ini'), source_dir=self.selected_config)

        print('\nINI transformations:')
        if changes:
            for section, items in changes.items():
                for option, old, new in items:
                    print(f'  [{section}] {option}: {old} -> {new}')
        else:
            print('  (none)')

        print('\nFiles to be generated:')
        print('  - monokrom.ini (modified)')
        print('  - postgui.hal (VCP→plasmac nets)')
        print('  - custom_postgui.hal (sources postgui.hal)')
        print('  - custom_config.yml (VCP config)')
        print('  - gcode_syntax.yml (syntax highlighting)')

        if self.vcp_options['import_buttons'] and self.prefs:
            buttons = self.prefs.get_button_codes()
            if buttons:
                print(f'  - user_buttons/ ({len(buttons)} .ngc files)')

        print('\nFiles to be copied:')
        for fname in ConfigGenerator.COPY_AS_IS:
            src = os.path.join(self.source_dir, fname)
            if os.path.isfile(src):
                print(f'  - {fname}')

        for fname in ConfigGenerator.OPTIONAL_HAL:
            src = os.path.join(self.source_dir, fname)
            if os.path.isfile(src):
                print(f'  - {fname}')

        src = os.path.join(self.source_dir, 'python')
        if os.path.isdir(src):
            print('  - python/ (directory)')

        templates_path = os.path.join(
            os.path.dirname(self.config_yml_path or ''),
            '..', '..', '..', 'linuxcnc', 'configs', 'templates', 'plasmac', 'plasma_table.db'
        )
        if os.path.isfile(os.path.normpath(templates_path)):
            print('  - plasma_table.db (pre-seeded)')

        print()
        print(f'Output directory: {self.output_dir}')
        print()
        print('Press Enter to continue...')
        input()

    # -- step 6: confirm and generate ---------------------------------------

    def _step6_generate(self):
        """Final confirmation and file generation."""
        print('Step 6/6: Confirm and generate')
        print('-' * 60)
        print()
        print(f'Source:  {self.source_dir}')
        print(f'Output:  {self.output_dir}')
        print()

        while True:
            choice = input('Generate MonoKrom config? [y/N]: ').strip().lower()
            if choice in ('y', 'yes', 'n', 'no', ''):
                if choice in ('y', 'yes'):
                    break
                else:
                    print('Cancelled.')
                    raise SystemExit(0)
            print('Please enter y or n.')

        # Generate using ConfigGenerator
        self.generator = ConfigGenerator(
            self.source_dir, self.output_dir,
            self.config_yml_path or os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(__file__)))),
                'plasma', 'config.yml'
            ),
            vcp_options=self.vcp_options
        )

        lines = self.generator.generate(
            self.prefs, self.ini_transformer, self.settings_mapper, auto=True
        )

        # Print completion summary
        print()
        print('=' * 60)
        print('  Setup Complete!')
        print('=' * 60)
        print()
        print(f'Output: {self.output_dir}')
        print(f'Log:    {self.generator.log_path}')
        print()
        print('Next steps:')
        print('  1. Review the generated config files')
        print('  2. Test with: monokrom_plasma --ini <path-to-monokrom.ini>')
        print('  3. Adjust settings in config.yml as needed')
        print()


# ---------------------------------------------------------------------------
# Convenience entry point
# ---------------------------------------------------------------------------

def run(source_dir, output_dir=None, config_yml_path=None, auto=False):
    """Run the full migration pipeline from a qtplasmac config directory.

    Args:
        source_dir:   Path to the qtplasmac config directory.
        output_dir:   Path for the output MonoKrom config.  If None,
                      defaults to <source_dir> with the directory name
                      changed to include 'monokrom_' prefix.
        config_yml_path: Path to the MonoKrom config.yml (for defaults).
        auto:         If True, skip interactive prompts.

    Returns:
        list of log lines.
    """
    source_dir = os.path.abspath(source_dir)

    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f'Source config directory not found: {source_dir}')

    # Determine output directory
    if output_dir is None:
        base = os.path.basename(source_dir)
        if base.startswith('monokrom_'):
            output_dir = source_dir
        else:
            output_dir = os.path.join(os.path.dirname(source_dir), f'monokrom_{base}')

    # Determine config.yml path
    if config_yml_path is None:
        # Look in the plasma package
        from monokrom.plasma import VCP_CONFIG_FILE
        config_yml_path = VCP_CONFIG_FILE

    # Find .prefs file
    prefs_file = None
    for fname in os.listdir(source_dir):
        if fname.endswith('.prefs'):
            prefs_file = os.path.join(source_dir, fname)
            break

    if prefs_file is None:
        raise FileNotFoundError(f'No .prefs file found in {source_dir}')

    # Find INI file
    ini_file = None
    for fname in os.listdir(source_dir):
        if fname.endswith('.ini'):
            ini_file = os.path.join(source_dir, fname)
            break

    if ini_file is None:
        raise FileNotFoundError(f'No .ini file found in {source_dir}')

    # --- Run pipeline ---

    # Step 1: Parse .prefs
    prefs = PrefsParser(prefs_file)

    # Step 2: Parse and transform INI
    ini_transformer = IniTransformer(ini_file)
    prefs_file_basename = os.path.basename(prefs_file)
    output_ini_name = prefs_file_basename.rsplit('.prefs', 1)[0] + '.ini'
    # Remove the original name prefix and replace with monokrom
    output_ini_name = 'monokrom.ini'

    # Step 3: Map settings
    settings_mapper = SettingsMapper(config_yml_path)

    # Step 4: Generate
    generator = ConfigGenerator(source_dir, output_dir, config_yml_path)
    lines = generator.generate(prefs, ini_transformer, settings_mapper, auto=auto)

    return lines
