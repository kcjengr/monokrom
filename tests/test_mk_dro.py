import sys
import pytest
from unittest.mock import MagicMock
from types import ModuleType


@pytest.fixture
def mk_dro_module(monkeypatch):
    """Provide mk_dro module with mocked qtpyvcp dependencies."""
    original_modules = dict(sys.modules)

    mock_status = MagicMock()
    mock_info = MagicMock()
    mock_info.AXIS_LETTER_LIST = ['x', 'y', 'z', 'a', 'b', 'c', 'u', 'v', 'w']
    mock_info.ALETTER_JNUM_DICT = {
        'X': 0, 'Y': 1, 'Z': 2, 'A': 3, 'B': 4, 'C': 5, 'U': 6, 'V': 7, 'W': 8,
        'x': 0, 'y': 1, 'z': 2, 'a': 3, 'b': 4, 'c': 5, 'u': 6, 'v': 7, 'w': 8,
    }
    mock_status.axis_mask.getValue.return_value = [0, 1, 3]

    monkeypatch.setenv('QT_QPA_PLATFORM', 'offscreen')

    mock_qtpyvcp = ModuleType('qtpyvcp')
    mock_plugins = ModuleType('qtpyvcp.plugins')
    mock_utilities = ModuleType('qtpyvcp.utilities')
    mock_info_mod = ModuleType('qtpyvcp.utilities.info')
    mock_pyside_loader = ModuleType('qtpyvcp.utilities.pyside_ui_loader')
    mock_actions = ModuleType('qtpyvcp.actions')
    mock_machine_actions = ModuleType('qtpyvcp.actions.machine_actions')

    def mock_get_plugin(name):
        if name == 'status':
            return mock_status
        return MagicMock()

    mock_plugins.getPlugin = mock_get_plugin
    mock_info_mod.Info = MagicMock(return_value=mock_info)

    class MockPySide6Ui:
        def __init__(self, *args):
            pass
        def load(self):
            mock_form = MagicMock()
            mock_base = MagicMock()
            return mock_form, mock_base

    mock_pyside_loader.PySide6Ui = MockPySide6Ui
    mock_machine_actions.issue_mdi = MagicMock()

    mock_qtpyvcp.plugins = mock_plugins
    mock_qtpyvcp.utilities = mock_utilities
    mock_utilities.info = mock_info_mod
    mock_utilities.pyside_ui_loader = mock_pyside_loader
    mock_qtpyvcp.actions = mock_actions
    mock_actions.machine_actions = mock_machine_actions

    for key in list(sys.modules.keys()):
        if key.startswith('qtpyvcp'):
            del sys.modules[key]

    mock_widgets = ModuleType('qtpyvcp.widgets')
    mock_qtdesigner = ModuleType('qtpyvcp.widgets.qtdesigner')
    mock_qtdesigner._DesignerPlugin = MagicMock()
    mock_widgets.qtdesigner = mock_qtdesigner
    mock_qtpyvcp.widgets = mock_widgets

    sys.modules['qtpyvcp'] = mock_qtpyvcp
    sys.modules['qtpyvcp.plugins'] = mock_plugins
    sys.modules['qtpyvcp.utilities'] = mock_utilities
    sys.modules['qtpyvcp.utilities.info'] = mock_info_mod
    sys.modules['qtpyvcp.utilities.pyside_ui_loader'] = mock_pyside_loader
    sys.modules['qtpyvcp.actions'] = mock_actions
    sys.modules['qtpyvcp.actions.machine_actions'] = mock_machine_actions
    sys.modules['qtpyvcp.widgets'] = mock_widgets
    sys.modules['qtpyvcp.widgets.qtdesigner'] = mock_qtdesigner

    # Symbols needed by monokrom.common.widgets.__init__ (imported transitively)
    class _VCPBaseWidget:
        pass

    class _MDIEntry:
        pass

    _vcp_text_store = {}


    class _VCPButton:
        def __init__(self, parent=None):
            self._text = ""

        def setText(self, text):
            self._text = text

        def text(self):
            return self._text

        def deleteLater(self):
            pass


    mock_widgets.VCPButton = _VCPButton
    mock_widgets.base_widgets = ModuleType('qtpyvcp.widgets.base_widgets')
    mock_widgets.base_widgets.base_widget = ModuleType(
        'qtpyvcp.widgets.base_widgets.base_widget'
    )
    mock_widgets.base_widgets.base_widget.VCPBaseWidget = _VCPBaseWidget
    sys.modules['qtpyvcp.widgets.base_widgets'] = mock_widgets.base_widgets
    sys.modules['qtpyvcp.widgets.base_widgets.base_widget'] = (
        mock_widgets.base_widgets.base_widget
    )

    mock_widgets.input_widgets = ModuleType('qtpyvcp.widgets.input_widgets')
    mock_widgets.input_widgets.mdientry_widget = ModuleType(
        'qtpyvcp.widgets.input_widgets.mdientry_widget'
    )
    mock_widgets.input_widgets.mdientry_widget.MDIEntry = _MDIEntry
    sys.modules['qtpyvcp.widgets.input_widgets'] = mock_widgets.input_widgets
    sys.modules['qtpyvcp.widgets.input_widgets.mdientry_widget'] = (
        mock_widgets.input_widgets.mdientry_widget
    )

    class _MockPySide6Ui:
        def __init__(self, *args):
            pass

        def load(self):
            return MagicMock(), MagicMock()


    sys.modules['qtpyvcp.utilities.pyside_ui_loader'].PySide6Ui = _MockPySide6Ui

    for key in list(sys.modules.keys()):
        if key.startswith('monokrom'):
            del sys.modules[key]

    import importlib.util
    import os

    file_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'monokrom',
        'common',
        'widgets',
        'mk_dro',
        'mk_dro.py'
    )
    spec = importlib.util.spec_from_file_location('mk_dro_test_mod', file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['mk_dro_test_mod'] = mod
    spec.loader.exec_module(mod)

    yield mod, mock_status, mock_info

    protected_prefixes = ('PySide6', 'shiboken6', 'cffi', '_pytest', 'qtpyvcp')
    for key in list(sys.modules.keys()):
        if key not in original_modules:
            if any(key.startswith(p) for p in protected_prefixes):
                continue
            del sys.modules[key]
    for key, val in original_modules.items():
        if key not in sys.modules:
            sys.modules[key] = val


class TestMkDroLazyInit:
    def test_get_info_returns_singleton(self, mk_dro_module):
        mod, mock_status, mock_info = mk_dro_module
        info1 = mod._get_info()
        info2 = mod._get_info()
        assert info1 is info2

    def test_get_status_returns_singleton(self, mk_dro_module):
        mod, mock_status, mock_info = mk_dro_module
        status1 = mod._get_status()
        status2 = mod._get_status()
        assert status1 is status2

    def test_axis_letter_list_accessible(self, mk_dro_module):
        mod, mock_status, mock_info = mk_dro_module
        info = mod._get_info()
        assert info.AXIS_LETTER_LIST[0] == 'x'
        assert info.AXIS_LETTER_LIST[2] == 'z'

    def test_aleletter_jnum_dict_accessible(self, mk_dro_module):
        mod, mock_status, mock_info = mk_dro_module
        info = mod._get_info()
        assert info.ALETTER_JNUM_DICT['X'] == 0
        assert info.ALETTER_JNUM_DICT['Z'] == 2


class TestMkDroWidget:
    def test_widget_creation(self, mk_dro_module):
        from PySide6.QtWidgets import QApplication
        mod, mock_status, mock_info = mk_dro_module

        app = QApplication.instance() or QApplication([])
        widget = mod.MonokromDroWidget(axis_number=0)
        assert widget is not None
        assert widget.axisNumber == 0
        widget.deleteLater()

    def test_widget_axis_number_range(self, mk_dro_module):
        from PySide6.QtWidgets import QApplication
        mod, mock_status, mock_info = mk_dro_module

        app = QApplication.instance() or QApplication([])
        widget = mod.MonokromDroWidget(axis_number=5)
        assert widget.axisNumber == 5
        widget.deleteLater()

    def test_widget_negative_axis_clamped(self, mk_dro_module):
        from PySide6.QtWidgets import QApplication
        mod, mock_status, mock_info = mk_dro_module

        app = QApplication.instance() or QApplication([])
        widget = mod.MonokromDroWidget(axis_number=-1)
        assert widget.axisNumber == 0
        widget.deleteLater()

    def test_widget_large_axis_clamped(self, mk_dro_module):
        from PySide6.QtWidgets import QApplication
        mod, mock_status, mock_info = mk_dro_module

        app = QApplication.instance() or QApplication([])
        widget = mod.MonokromDroWidget(axis_number=99)
        assert widget.axisNumber == 8
        widget.deleteLater()


class TestMkDroGroup:
    def test_group_creation(self, mk_dro_module):
        from PySide6.QtWidgets import QApplication
        mod, mock_status, mock_info = mk_dro_module

        app = QApplication.instance() or QApplication([])
        group = mod.MonokromDroGroup()
        assert group is not None
        assert group.layout.count() == 3
        group.deleteLater()
