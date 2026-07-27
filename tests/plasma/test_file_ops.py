"""Tests for file_ops.py — verify the FileOpsService."""

from unittest.mock import MagicMock, patch

import pytest

from monokrom.plasma.file_ops import FileOpsService


class MockGcodeEditor:
    """Mock GcodeTextEdit with saveFile method."""

    def __init__(self):
        self.save_calls = []

    def saveFile(self, path):
        self.save_calls.append(path)


class MockParent:
    """Minimal mock of MainWindow for FileOpsService tests."""

    def __init__(self):
        self.latest_real_file = None
        self.gcode_editor = MockGcodeEditor()
        self.reset_vtk_btns_calls = []

    def reset_vtk_btns(self):
        self.reset_vtk_btns_calls.append(True)


def _make_mock_load_program():
    """Create a mock loadProgram function that tracks calls."""
    mock = MagicMock()
    return mock


class TestOpenLatest:
    def test_open_latest_sets_parent_file_and_loads_it(self):
        parent = MockParent()
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program, ngc_loc="/ngc")

        with patch("os.scandir") as mock_scandir:
            entry = MagicMock()
            entry.name = "test.ngc"
            entry.is_file.return_value = True
            entry.stat().st_mtime = 1000.0
            entry.path = "/ngc/test.ngc"
            mock_scandir.return_value.__enter__.return_value = [entry]

            service.open_latest()

        assert parent.latest_real_file == "/ngc/test.ngc"
        load_program.assert_called_once_with("/ngc/test.ngc")
        assert parent.reset_vtk_btns_calls == [True]

    def test_open_latest_picks_newest_by_mtime(self):
        parent = MockParent()
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program, ngc_loc="/ngc")

        with patch("os.scandir") as mock_scandir:
            entry1 = MagicMock()
            entry1.name = "old.ngc"
            entry1.is_file.return_value = True
            entry1.stat().st_mtime = 1000.0
            entry1.path = "/ngc/old.ngc"

            entry2 = MagicMock()
            entry2.name = "new.ngc"
            entry2.is_file.return_value = True
            entry2.stat().st_mtime = 2000.0
            entry2.path = "/ngc/new.ngc"

            mock_scandir.return_value.__enter__.return_value = [entry1, entry2]

            service.open_latest()

        assert parent.latest_real_file == "/ngc/new.ngc"
        load_program.assert_called_once_with("/ngc/new.ngc")

    def test_open_latest_ignores_hidden_files(self):
        parent = MockParent()
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program, ngc_loc="/ngc")

        with patch("os.scandir") as mock_scandir:
            hidden_entry = MagicMock()
            hidden_entry.name = ".hidden.ngc"
            hidden_entry.is_file.return_value = True
            hidden_entry.stat().st_mtime = 9999.0
            hidden_entry.path = "/ngc/.hidden.ngc"

            visible_entry = MagicMock()
            visible_entry.name = "visible.ngc"
            visible_entry.is_file.return_value = True
            visible_entry.stat().st_mtime = 1000.0
            visible_entry.path = "/ngc/visible.ngc"

            mock_scandir.return_value.__enter__.return_value = [hidden_entry, visible_entry]

            service.open_latest()

        assert parent.latest_real_file == "/ngc/visible.ngc"
        load_program.assert_called_once_with("/ngc/visible.ngc")

    def test_open_latest_does_nothing_when_dir_empty(self):
        parent = MockParent()
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program, ngc_loc="/ngc")

        with patch("os.scandir") as mock_scandir:
            mock_scandir.return_value.__enter__.return_value = []

            service.open_latest()

        assert parent.latest_real_file is None
        load_program.assert_not_called()
        assert parent.reset_vtk_btns_calls == []

    def test_open_latest_skips_directories(self):
        parent = MockParent()
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program, ngc_loc="/ngc")

        with patch("os.scandir") as mock_scandir:
            dir_entry = MagicMock()
            dir_entry.name = "subdir"
            dir_entry.is_file.return_value = False

            file_entry = MagicMock()
            file_entry.name = "file.ngc"
            file_entry.is_file.return_value = True
            file_entry.stat().st_mtime = 1000.0
            file_entry.path = "/ngc/file.ngc"

            mock_scandir.return_value.__enter__.return_value = [dir_entry, file_entry]

            service.open_latest()

        assert parent.latest_real_file == "/ngc/file.ngc"
        load_program.assert_called_once_with("/ngc/file.ngc")


class TestSaveFile:
    def test_save_file_returns_early_when_no_real_file(self):
        parent = MockParent()
        parent.latest_real_file = None
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.save_file()

        load_program.assert_not_called()
        assert parent.gcode_editor.save_calls == []
        assert parent.reset_vtk_btns_calls == []

    def test_save_file_inserts_parsed_suffix_before_extension(self):
        parent = MockParent()
        parent.latest_real_file = "/path/to/foo.ngc"
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.save_file()

        assert parent.gcode_editor.save_calls == ["/path/to/foo_parsed.ngc"]
        load_program.assert_called_once_with("/path/to/foo_parsed.ngc")
        assert parent.reset_vtk_btns_calls == [True]

    def test_save_file_replaces_trailing_parsed_suffix(self):
        parent = MockParent()
        parent.latest_real_file = "/path/to/foo_parsed.ngc"
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.save_file()

        # When name_parts[0] ends with "_parsed", ppart="." so:
        # "/path/to/foo_parsed" + "." + "ngc" -> "/path/to/foo_parsed.ngc" (no-op)
        assert parent.gcode_editor.save_calls == ["/path/to/foo_parsed.ngc"]
        load_program.assert_called_once_with("/path/to/foo_parsed.ngc")

    def test_save_file_calls_all_side_effects(self):
        parent = MockParent()
        parent.latest_real_file = "/path/to/test.ngc"
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.save_file()

        assert len(parent.reset_vtk_btns_calls) == 1
        load_program.assert_called_once_with("/path/to/test_parsed.ngc")


class TestReloadFile:
    def test_reload_file_returns_early_when_no_real_file(self):
        parent = MockParent()
        parent.latest_real_file = None
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.reload_file()

        load_program.assert_not_called()
        assert parent.reset_vtk_btns_calls == []

    def test_reload_file_returns_early_when_empty_string(self):
        parent = MockParent()
        parent.latest_real_file = ""
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.reload_file()

        load_program.assert_not_called()
        assert parent.reset_vtk_btns_calls == []

    def test_reload_file_calls_load_program_with_current_file(self):
        parent = MockParent()
        parent.latest_real_file = "/path/to/file.ngc"
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.reload_file()

        load_program.assert_called_once_with("/path/to/file.ngc")

    def test_reload_file_calls_reset_vtk_btns(self):
        parent = MockParent()
        parent.latest_real_file = "/path/to/file.ngc"
        load_program = _make_mock_load_program()
        service = FileOpsService(parent, load_program_fn=load_program)
        service.reload_file()

        assert parent.reset_vtk_btns_calls == [True]
