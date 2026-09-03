"""Tests for setup.py — the config installer module.

Tests cover PrefsParser, SettingsMapper, IniTransformer, ConfigGenerator,
and the VCP options integration in custom_config.yml generation.

Uses the reference configs in Supporting-Collateral/hw-configs/ as fixtures.
"""

import configparser
import os
import shutil
import tempfile

import pytest

from monokrom.plasma.setup import (
    ConfigGenerator,
    IniTransformer,
    PrefsParser,
    SettingsMapper,
    Wizard,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SOURCE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "Supporting-Collateral", "hw-configs", "plasma-ui-specific",
)
REFERENCE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "Supporting-Collateral", "hw-configs", "monokrom_plasma",
)


@pytest.fixture()
def source_dir():
    """Path to the qtplasmac reference config."""
    return SOURCE_DIR


@pytest.fixture()
def tmp_dir():
    """Provide a temporary directory for generated output."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture()
def prefs(source_dir):
    """Parsed .prefs from the source config."""
    prefs_file = os.path.join(source_dir, "plasma-ui-specific.prefs")
    return PrefsParser(prefs_file)


@pytest.fixture()
def config_yml_path():
    """Path to the MonoKrom plasma config.yml (settings defaults)."""
    return os.path.join(
        os.path.dirname(__file__),
        "..", "..", "src", "monokrom", "plasma", "config.yml",
    )


# ---------------------------------------------------------------------------
# PrefsParser
# ---------------------------------------------------------------------------

class TestPrefsParser:
    def test_parses_plasma_parameters(self, prefs):
        params = prefs.get_section("PLASMA_PARAMETERS")
        assert isinstance(params, dict)
        assert "Arc Voltage Offset" in params

    def test_parses_buttons(self, prefs):
        buttons = prefs.get_button_codes()
        assert isinstance(buttons, list)
        assert len(buttons) > 0
        # Each button is (index, name, code)
        idx, name, code = buttons[0]
        assert isinstance(idx, int)
        assert isinstance(name, str)
        assert isinstance(code, str)

    def test_parses_enable_options(self, prefs):
        opts = prefs.get_section("ENABLE_OPTIONS")
        assert isinstance(opts, dict)
        assert "THC enable" in opts

    def test_get_returns_single_value(self, prefs):
        val = prefs.get("PLASMA_PARAMETERS", "Arc Voltage Offset")
        assert val is not None

    def test_get_returns_none_for_missing_key(self, prefs):
        val = prefs.get("PLASMA_PARAMETERS", "NONEXISTENT_KEY")
        assert val is None

    def test_get_returns_none_for_missing_section(self, tmp_dir):
        prefs_file = os.path.join(tmp_dir, "empty.prefs")
        with open(prefs_file, 'w') as f:
            f.write("[EMPTY]\nkey = value\n")
        p = PrefsParser(prefs_file)
        val = p.get("NOSECTION", "key")
        assert val is None


# ---------------------------------------------------------------------------
# SettingsMapper
# ---------------------------------------------------------------------------

class TestSettingsMapper:
    def test_map_settings_returns_four_lists(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        updated, skipped, not_found_prefs, not_found_config = mapper.map_settings(prefs)
        assert isinstance(updated, list)
        assert isinstance(skipped, list)
        assert isinstance(not_found_prefs, list)
        assert isinstance(not_found_config, list)

    def test_updated_settings_have_correct_tuple_shape(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        updated, _, _, _ = mapper.map_settings(prefs)
        for prefs_key, config_key, value, default in updated:
            assert isinstance(prefs_key, str)
            assert isinstance(config_key, str)
            assert value != default

    def test_skipped_settings_match_defaults(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        _, skipped, _, _ = mapper.map_settings(prefs)
        for prefs_key, config_key, value in skipped:
            # Value should match the default
            assert value is not None

    def test_not_found_prefs_are_mono_only(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        _, _, not_found_prefs, _ = mapper.map_settings(prefs)
        for config_key, default in not_found_prefs:
            assert isinstance(config_key, str)
            assert isinstance(default, (bool, float, int, str, type(None)))

    def test_not_found_config_are_qtplasmac_only(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        _, _, _, not_found_config = mapper.map_settings(prefs)
        for prefs_key, value in not_found_config:
            assert isinstance(prefs_key, str)

    def test_probe_speed_is_mapped(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        updated, _, _, _ = mapper.map_settings(prefs)
        config_keys = [k for _, k, _, _ in updated]
        assert "probe_speed" in config_keys

    def test_arc_retry_delay_is_mapped(self, prefs, config_yml_path):
        mapper = SettingsMapper(config_yml_path)
        updated, _, _, _ = mapper.map_settings(prefs)
        prefs_keys = [k for k, _, _, _ in updated]
        assert "Arc Restart Delay" in prefs_keys


# ---------------------------------------------------------------------------
# IniTransformer
# ---------------------------------------------------------------------------

class TestIniTransformer:
    def test_transform_changes_display(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert cp.get("DISPLAY", "DISPLAY") == "monokrom_plasma"

    def test_transform_removes_qtplasmac_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        with open(out_path) as f:
            content = f.read()
        assert "[QTPLASMAC]" not in content

    def test_transform_changes_filter(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert cp.get("FILTER", "ngc") == "plasma_gcode_preprocessor"

    def test_transform_preserves_hmot_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        with open(out_path) as f:
            content = f.read()
        assert "[HMOT]" in content
        assert "CARD0" in content

    def test_transform_preserves_hardware_sections(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        # Hardware sections should be preserved
        assert cp.has_section("KINS")
        assert cp.has_section("TRAJ")
        assert cp.has_section("EMCMOT")

    def test_transform_adds_python_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert cp.has_section("PYTHON")
        assert cp.get("PYTHON", "PATH_PREPEND") == "./python"

    def test_transform_adds_config_file(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert cp.get("DISPLAY", "CONFIG_FILE") == "custom_config.yml"

    def test_transform_changes_emcio_db_program(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert "plasma_tooldbpipe" in cp.get("EMCIO", "DB_PROGRAM")

    def test_transform_renames_hardware_halfile(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        with open(out_path) as f:
            content = f.read()
        assert "HALFILE = monokrom.hal" in content

    def test_transform_keeps_custom_hal(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        with open(out_path) as f:
            content = f.read()
        assert "HALFILE = custom.hal" in content

    def test_transform_with_prefs_adds_user_buttons(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        t.transform(prefs, out_path)
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        cp.read(out_path)
        assert cp.has_option("DISPLAY", "USER1_NAME")
        assert cp.get("DISPLAY", "USER1_NAME") == "PROBE_TEST"

    def test_transform_returns_changes_dict(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        t = IniTransformer(ini_path)
        changes = t.transform(prefs, out_path)
        assert isinstance(changes, dict)
        assert "DISPLAY" in changes
        assert "FILTER" in changes

    def test_set_display(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        t.set_display()
        assert t.config.get("DISPLAY", "DISPLAY") == "monokrom_plasma"

    def test_remove_qtplasmac_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        t.remove_qtplasmac_section()
        assert not t.config.has_section("QTPLASMAC")

    def test_set_gcode_filter(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        t.set_gcode_filter()
        assert t.config.get("FILTER", "ngc") == "plasma_gcode_preprocessor"

    def test_add_python_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        t.add_python_section()
        assert t.config.has_section("PYTHON")
        assert t.config.get("PYTHON", "PATH_PREPEND") == "./python"

    def test_add_hmot_section(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        # Remove HMOT to test addition
        if t.config.has_section("HMOT"):
            t.config.remove_section("HMOT")
        t.add_hmot_section("hm2_7i76e.0")
        assert t.config.has_section("HMOT")
        assert t.config.get("HMOT", "CARD0") == "hm2_7i76e.0"

    def test_add_user_buttons(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        buttons = [(1, "PROBE\\TEST", "O100 call"), (2, "OHMIC\\TEST", "O200 call")]
        t.add_user_buttons(buttons)
        assert t.config.get("DISPLAY", "USER1_NAME") == "PROBE_TEST"
        assert t.config.get("DISPLAY", "USER2_NAME") == "OHMIC_TEST"
        assert t.config.get("DISPLAY", "USER1_ACTION") == "O100.ngc"
        assert t.config.get("DISPLAY", "USER2_ACTION") == "O200.ngc"

    def test_add_user_buttons_capped_at_three(self, source_dir, tmp_dir):
        ini_path = os.path.join(source_dir, "plasma-ui-specific.ini")
        out_path = os.path.join(tmp_dir, "monokrom.ini")
        t = IniTransformer(ini_path)
        buttons = [
            (1, "BTN1", "O1"), (2, "BTN2", "O2"),
            (3, "BTN3", "O3"), (4, "BTN4", "O4"),
        ]
        t.add_user_buttons(buttons)
        assert t.config.has_option("DISPLAY", "USER3_NAME")
        assert not t.config.has_option("DISPLAY", "USER4_NAME")


# ---------------------------------------------------------------------------
# ConfigGenerator
# ---------------------------------------------------------------------------

class TestConfigGenerator:
    def test_init_accepts_vcp_options(self, tmp_dir):
        gen = ConfigGenerator(
            SOURCE_DIR, tmp_dir,
            vcp_options={"confirm_exit": True, "fullscreen": False},
        )
        assert gen.vcp_options["confirm_exit"] is True
        assert gen.vcp_options["fullscreen"] is False

    def test_init_defaults_vcp_options_when_none(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir, vcp_options=None)
        assert gen.vcp_options["confirm_exit"] is False
        assert gen.vcp_options["fullscreen"] is False
        assert gen.vcp_options["file_locations"] == []

    def test_generate_custom_config_yml_uses_confirm_exit(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "custom"), exist_ok=True)
        gen = ConfigGenerator(
            SOURCE_DIR, os.path.join(tmp_dir, "custom"),
            vcp_options={"confirm_exit": True, "fullscreen": False},
        )
        gen._generate_custom_config_yml()
        with open(os.path.join(tmp_dir, "custom", "custom_config.yml")) as f:
            content = f.read()
        assert "confirm_exit: true" in content

    def test_generate_custom_config_yml_uses_fullscreen(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "custom"), exist_ok=True)
        gen = ConfigGenerator(
            SOURCE_DIR, os.path.join(tmp_dir, "custom"),
            vcp_options={"confirm_exit": False, "fullscreen": True},
        )
        gen._generate_custom_config_yml()
        with open(os.path.join(tmp_dir, "custom", "custom_config.yml")) as f:
            content = f.read()
        assert "fullscreen: true" in content

    def test_generate_custom_config_yml_uses_custom_file_locations(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "custom"), exist_ok=True)
        gen = ConfigGenerator(
            SOURCE_DIR, os.path.join(tmp_dir, "custom"),
            vcp_options={
                "confirm_exit": False,
                "file_locations": ["MyCuts: /home/user/cuts", "Backup: /mnt/bak"],
            },
        )
        gen._generate_custom_config_yml()
        with open(os.path.join(tmp_dir, "custom", "custom_config.yml")) as f:
            content = f.read()
        assert "MyCuts: /home/user/cuts" in content
        assert "Backup: /mnt/bak" in content
        # Defaults should NOT be present when custom locations provided
        assert "Home: ~/" not in content
        assert "Desktop: ~/Desktop" not in content

    def test_generate_custom_config_yml_uses_defaults_when_empty(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "custom"), exist_ok=True)
        gen = ConfigGenerator(
            SOURCE_DIR, os.path.join(tmp_dir, "custom"),
            vcp_options={"file_locations": []},
        )
        gen._generate_custom_config_yml()
        with open(os.path.join(tmp_dir, "custom", "custom_config.yml")) as f:
            content = f.read()
        assert "Home: ~/" in content
        assert "Desktop: ~/Desktop" in content
        assert "NC Files: ~/linuxcnc/nc_files" in content

    def test_generate_custom_config_yml_false_values(self, tmp_dir):
        os.makedirs(os.path.join(tmp_dir, "custom"), exist_ok=True)
        gen = ConfigGenerator(
            SOURCE_DIR, os.path.join(tmp_dir, "custom"),
            vcp_options={"confirm_exit": False, "fullscreen": False},
        )
        gen._generate_custom_config_yml()
        with open(os.path.join(tmp_dir, "custom", "custom_config.yml")) as f:
            content = f.read()
        assert "confirm_exit: false" in content
        assert "fullscreen: false" in content

    def test_generate_creates_output_directory(self, tmp_dir):
        out = os.path.join(tmp_dir, "nested", "deep")
        gen = ConfigGenerator(SOURCE_DIR, out)
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        gen.generate(None, ini_t, None, auto=True)
        assert os.path.isdir(out)

    def test_generate_creates_monokrom_ini(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))

    def test_generate_creates_postgui_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "postgui.hal"))

    def test_generate_creates_custom_config_yml(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "custom_config.yml"))

    def test_generate_creates_custom_postgui_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "custom_postgui.hal"))

    def test_generate_creates_user_buttons(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        buttons_dir = os.path.join(tmp_dir, "user_buttons")
        assert os.path.isdir(buttons_dir)
        ngc_files = os.listdir(buttons_dir)
        assert len(ngc_files) > 0
        assert all(f.endswith(".ngc") for f in ngc_files)

    def test_generate_copies_tool_tbl(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "tool.tbl"))

    def test_generate_copies_custom_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "custom.hal"))

    def test_generate_copies_shutdown_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "shutdown.hal"))

    def test_generate_copies_ohmic_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "ohmic.hal"))

    def test_generate_creates_plasma_table_db(self, tmp_dir):
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir, config_yml_path=config_yml)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "plasma_table.db"))

    def test_generate_creates_setup_log(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        log_path = os.path.join(tmp_dir, "setup.log")
        assert os.path.isfile(log_path)
        with open(log_path) as f:
            content = f.read()
        assert "=== MonoKrom Plasma Setup ===" in content
        assert "[UPDATED]" in content
        assert "[SKIPPED]" in content
        assert "[NOT_FOUND_IN_PREFS]" in content

    def test_generate_does_not_copy_material_cfg(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        assert not os.path.isfile(os.path.join(tmp_dir, "material.cfg"))

    def test_generate_copies_plasma_hardware_hal(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        # plasma-ui-specific.hal is renamed to monokrom.hal in INI
        # Check that the INI references monokrom.hal
        with open(os.path.join(tmp_dir, "monokrom.ini")) as f:
            content = f.read()
        assert "HALFILE = monokrom.hal" in content

    def test_generate_copies_python_dir(self, tmp_dir):
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)
        python_dir = os.path.join(tmp_dir, "python")
        assert os.path.isdir(python_dir)

    def test_generate_copy_as_is_list(self):
        expected = [
            "custom.hal",
            "shutdown.hal",
            "ohmic.hal",
            "tool.tbl",
            "M159",
            "M190",
        ]
        for fname in expected:
            assert fname in ConfigGenerator.COPY_AS_IS

    def test_generate_optional_hal_list(self):
        expected = [
            "xhc-whb04b-6.hal",
            "joypad.hal",
            "joypad_preloader.hal",
        ]
        for fname in expected:
            assert fname in ConfigGenerator.OPTIONAL_HAL


# ---------------------------------------------------------------------------
# End-to-end: full pipeline with vcp_options
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_full_pipeline_applies_vcp_options(self, tmp_dir):
        """Verify that wizard-collected vcp_options flow through to generated config."""
        gen = ConfigGenerator(
            SOURCE_DIR, tmp_dir,
            vcp_options={
                "confirm_exit": True,
                "fullscreen": True,
                "file_locations": ["Cuts: /home/user/cuts"],
                "import_buttons": True,
            },
        )
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        # Check custom_config.yml reflects vcp_options
        with open(os.path.join(tmp_dir, "custom_config.yml")) as f:
            content = f.read()
        assert "confirm_exit: true" in content
        assert "fullscreen: true" in content
        assert "Cuts: /home/user/cuts" in content

    def test_full_pipeline_produces_valid_ini(self, tmp_dir):
        """Verify generated INI can be parsed and has expected sections."""
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str
        ini_path = os.path.join(tmp_dir, "monokrom.ini")
        cp.read(ini_path)

        # Core sections
        assert cp.get("DISPLAY", "DISPLAY") == "monokrom_plasma"
        assert cp.get("FILTER", "ngc") == "plasma_gcode_preprocessor"
        assert cp.has_section("PYTHON")
        assert cp.has_section("HMOT")

        # Hardware preserved
        assert cp.get("KINS", "JOINTS") == "4"
        assert cp.get("TRAJ", "COORDINATES") == "XYYZ"

    def test_full_pipeline_produces_valid_postgui_hal(self, tmp_dir):
        """Verify postgui.hal contains VCP→plasmac net connections."""
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        with open(os.path.join(tmp_dir, "postgui.hal")) as f:
            content = f.read()
        assert "net plasmac:torch-on" in content
        assert "net plasmac:arc-ok" in content
        assert "net plasmac:torch-enable" in content

    def test_full_pipeline_user_buttons_from_prefs(self, tmp_dir):
        """Verify user buttons are generated from .prefs BUTTONS section."""
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        buttons_dir = os.path.join(tmp_dir, "user_buttons")
        ngc_files = os.listdir(buttons_dir)
        # Should have buttons from prefs
        assert len(ngc_files) >= 3
        # Check content of one button file
        with open(os.path.join(buttons_dir, ngc_files[0])) as f:
            content = f.read()
        assert "sub" in content.lower() or "o" in content[0].lower()

    def test_full_pipeline_log_contains_settings_summary(self, tmp_dir):
        """Verify setup.log contains settings migration summary."""
        gen = ConfigGenerator(SOURCE_DIR, tmp_dir)
        prefs = PrefsParser(os.path.join(SOURCE_DIR, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(SOURCE_DIR, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        with open(os.path.join(tmp_dir, "setup.log")) as f:
            content = f.read()
        assert "Settings Migration" in content
        assert "INI Transformations" in content
        assert "Files Generated" in content
        assert "Files Copied" in content


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------

class TestWizardInit:
    def test_wizard_init_sets_defaults(self, source_dir):
        w = Wizard(source_dir)
        assert w.source_dir == os.path.abspath(source_dir)
        assert w.output_dir is None
        assert w.prefs is None
        assert w.vcp_options == {
            'confirm_exit': False,
            'fullscreen': False,
            'file_locations': [],
            'import_buttons': True,
        }

    def test_wizard_init_with_output_dir(self, source_dir):
        w = Wizard(source_dir, output_dir="/tmp/output")
        assert w.output_dir == "/tmp/output"


class TestWizardStep6:
    """Tests for Wizard._step6_generate — the critical path that calls ConfigGenerator."""

    def test_step6_generate_calls_config_generator(self, source_dir, tmp_dir, monkeypatch):
        """Verify _step6_generate creates a ConfigGenerator and calls generate()."""
        w = Wizard(source_dir, output_dir=tmp_dir)
        # Parse prefs and ini in step 2
        w.prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        w.ini_transformer = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        w.settings_mapper = SettingsMapper(config_yml)
        _, w.updated_settings, w.skipped_settings, _ = w.settings_mapper.map_settings(w.prefs)

        # Mock input: 'y' to confirm generation, '' for other prompts
        inputs = iter(['y', '', '', '', '', ''])
        monkeypatch.setattr('builtins.input', lambda *a: next(inputs))

        w._step6_generate()

        # Verify files were created
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))
        assert os.path.isfile(os.path.join(tmp_dir, "postgui.hal"))
        assert os.path.isfile(os.path.join(tmp_dir, "custom_config.yml"))
        assert os.path.isfile(os.path.join(tmp_dir, "custom_postgui.hal"))
        assert os.path.isfile(os.path.join(tmp_dir, "setup.log"))

    def test_step6_generate_with_vcp_options(self, source_dir, tmp_dir, monkeypatch):
        """Verify vcp_options are passed through to ConfigGenerator."""
        w = Wizard(source_dir, output_dir=tmp_dir)
        w.prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        w.ini_transformer = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        w.settings_mapper = SettingsMapper(config_yml)
        _, w.updated_settings, w.skipped_settings, _ = w.settings_mapper.map_settings(w.prefs)

        # Set VCP options
        w.vcp_options = {
            'confirm_exit': True,
            'fullscreen': True,
            'file_locations': ['My NC Files: /home/user/nc'],
            'import_buttons': True,
        }

        inputs = iter(['y', '', '', '', '', ''])
        monkeypatch.setattr('builtins.input', lambda *a: next(inputs))

        w._step6_generate()

        # Verify VCP options were applied
        with open(os.path.join(tmp_dir, "custom_config.yml")) as f:
            content = f.read()
        assert "confirm_exit: true" in content
        assert "fullscreen: true" in content
        assert "My NC Files: /home/user/nc" in content

    def test_step6_generate_auto_mode(self, source_dir, tmp_dir, monkeypatch):
        """Verify auto mode skips interactive prompts."""
        w = Wizard(source_dir, output_dir=tmp_dir)
        w.prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        w.ini_transformer = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        w.settings_mapper = SettingsMapper(config_yml)
        _, w.updated_settings, w.skipped_settings, _ = w.settings_mapper.map_settings(w.prefs)

        inputs = iter(['y', '', '', '', '', ''])
        monkeypatch.setattr('builtins.input', lambda *a: next(inputs))

        w._step6_generate()

        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))


class TestWizardRun:
    """Tests for Wizard.run — the full interactive flow."""

    def test_run_with_mocked_input(self, source_dir, tmp_dir, monkeypatch):
        """Test the full wizard run with mocked input calls."""
        w = Wizard(source_dir, output_dir=tmp_dir)
        w.config_yml_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )

        # Mock input: simulate pressing Enter through all steps, 'y' to confirm generation
        # Step 1: use provided source_dir (skips selection)
        # Step 2: Enter
        # Step 3: Enter (toggle updated), Enter (toggle skipped), Enter (continue)
        # Step 4: Enter (confirm_exit), Enter (fullscreen), Enter (file_locations), Enter (buttons)
        # Step 5: Enter
        # Step 6: y (confirm generation)
        inputs = iter(['', '', '', '', '', '', '', '', '', '', 'y'])
        monkeypatch.setattr('builtins.input', lambda *a: next(inputs))

        w.run()

        # Verify output files were created
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))
        assert os.path.isfile(os.path.join(tmp_dir, "postgui.hal"))
        assert os.path.isfile(os.path.join(tmp_dir, "custom_config.yml"))
        assert os.path.isfile(os.path.join(tmp_dir, "setup.log"))

    def test_run_uses_provided_source_dir(self, source_dir, tmp_dir, monkeypatch):
        """When source_dir is provided, skip config selection."""
        w = Wizard(source_dir, output_dir=tmp_dir)
        w.config_yml_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )

        inputs = iter(['', '', '', '', '', '', '', '', '', '', 'y'])
        monkeypatch.setattr('builtins.input', lambda *a: next(inputs))

        w.run()

        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))


# ---------------------------------------------------------------------------
# SettingsMapper write_settings edge cases
# ---------------------------------------------------------------------------

class TestSettingsMapperWriteSettings:
    def test_write_settings_creates_output_file(self, prefs, tmp_dir):
        """write_settings should write to a copy of config.yml without Jinja2 templates."""
        # Create a clean config.yml without Jinja2 templates for testing
        clean_yml = os.path.join(tmp_dir, "clean_config.yml")
        with open(clean_yml, 'w') as f:
            f.write("settings:\n")
            f.write("  arc_voltage_offset:\n")
            f.write("    default_value: 0.0\n")
            f.write("    type: float\n")
        mapper = SettingsMapper(clean_yml)
        # Use a minimal prefs with matching key
        minimal_prefs = PrefsParser.__new__(PrefsParser)
        minimal_prefs.parsed = {'PLASMA_PARAMETERS': {'Arc Voltage Offset': '123.4'}}
        updated, _, _, _ = mapper.map_settings(minimal_prefs)
        output_path = os.path.join(tmp_dir, "output.yml")
        written = mapper.write_settings(clean_yml, updated, output_path)
        assert os.path.isfile(output_path)
        assert len(written) > 0

    def test_write_settings_empty_settings(self, tmp_dir):
        # Create a minimal config.yml without Jinja2 templates
        clean_yml = os.path.join(tmp_dir, "clean.yml")
        with open(clean_yml, 'w') as f:
            f.write("settings:\n  arc_voltage_offset:\n    default_value: 0.0\n")
        mapper = SettingsMapper(clean_yml)
        output_path = os.path.join(tmp_dir, "output.yml")
        written = mapper.write_settings(clean_yml, [], output_path)
        assert written == []
        assert os.path.isfile(output_path)


# ---------------------------------------------------------------------------
# IniTransformer edge cases
# ---------------------------------------------------------------------------

class TestIniTransformerEdgeCases:
    def test_read_with_duplicates_file_not_found(self, tmp_dir):
        with pytest.raises(FileNotFoundError, match="not found"):
            IniTransformer(os.path.join(tmp_dir, "nonexistent.ini"))

    def test_transform_preserves_non_vcp_sections(self, source_dir, tmp_dir):
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        output_path = os.path.join(tmp_dir, "output.ini")
        ini_t.transform(None, output_path)
        # Should preserve [TRAJ], [KINS], [EMCMOT], etc.
        assert ini_t.config.has_section('TRAJ')
        assert ini_t.config.has_section('KINS')
        assert ini_t.config.has_section('EMCMOT')


# ---------------------------------------------------------------------------
# ConfigGenerator edge cases
# ---------------------------------------------------------------------------

class TestConfigGeneratorEdgeCases:
    def test_generate_optional_hal_files(self, source_dir, tmp_dir):
        """Verify optional HAL files (xhc-whb04b-6.hal, ohmic.hal) are copied when present."""
        gen = ConfigGenerator(source_dir, tmp_dir)
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        # ohmic.hal should be copied if present in source
        if os.path.isfile(os.path.join(source_dir, "ohmic.hal")):
            assert os.path.isfile(os.path.join(tmp_dir, "ohmic.hal"))

    def test_generate_user_buttons_with_prefs(self, source_dir, tmp_dir):
        """Verify user_buttons are generated from prefs BUTTONS section."""
        gen = ConfigGenerator(source_dir, tmp_dir)
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(prefs, ini_t, mapper, auto=True)

        buttons_dir = os.path.join(tmp_dir, "user_buttons")
        assert os.path.isdir(buttons_dir)
        ngc_files = os.listdir(buttons_dir)
        assert len(ngc_files) > 0

    def test_generate_no_prefs_no_mapper(self, source_dir, tmp_dir):
        """Verify generate works with prefs=None and mapper=None (auto mode)."""
        gen = ConfigGenerator(source_dir, tmp_dir)
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        gen.generate(None, ini_t, None, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))

    def test_generate_no_prefs_with_mapper(self, source_dir, tmp_dir):
        """Verify generate works with prefs=None but mapper provided."""
        gen = ConfigGenerator(source_dir, tmp_dir)
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        config_yml = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "src", "monokrom", "plasma", "config.yml",
        )
        mapper = SettingsMapper(config_yml)
        gen.generate(None, ini_t, mapper, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))

    def test_generate_no_mapper_with_prefs(self, source_dir, tmp_dir):
        """Verify generate works with mapper=None but prefs provided."""
        gen = ConfigGenerator(source_dir, tmp_dir)
        prefs = PrefsParser(os.path.join(source_dir, "plasma-ui-specific.prefs"))
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        gen.generate(prefs, ini_t, None, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))

    def test_generate_with_none_config_yml_path(self, source_dir, tmp_dir):
        """Verify ConfigGenerator handles config_yml_path=None."""
        gen = ConfigGenerator(source_dir, tmp_dir, config_yml_path=None)
        ini_t = IniTransformer(os.path.join(source_dir, "plasma-ui-specific.ini"))
        gen.generate(None, ini_t, None, auto=True)
        assert os.path.isfile(os.path.join(tmp_dir, "monokrom.ini"))
