import sys
from types import ModuleType
from unittest.mock import MagicMock, Mock

# ── helpers ────────────────────────────────────────────────────────────────
def _make_mod(name):
    m = ModuleType(name)
    sys.modules[name] = m
    return m


# ── mock package tree (ModuleType so Python's import system works) ─────────
qtpyvcp = _make_mod('qtpyvcp')
qtpyvcp.plugins = _make_mod('qtpyvcp.plugins')
qtpyvcp.vcp = _make_mod('qtpyvcp.vcp')
qtpyvcp.vcp_widgets = _make_mod('qtpyvcp.vcp_widgets')
qtpyvcp.widgets = _make_mod('qtpyvcp.widgets')
qtpyvcp.actions = _make_mod('qtpyvcp.actions')

# utilities submodules
qtpyvcp.utilities = _make_mod('qtpyvcp.utilities')
qtpyvcp.utilities.info = _make_mod('qtpyvcp.utilities.info')
qtpyvcp.utilities.logger = _make_mod('qtpyvcp.utilities.logger')
qtpyvcp.utilities.pyside_ui_loader = _make_mod('qtpyvcp.utilities.pyside_ui_loader')

# widgets submodules
qtpyvcp.widgets.qtdesigner = _make_mod('qtpyvcp.widgets.qtdesigner')
qtpyvcp.widgets.base_widgets = _make_mod('qtpyvcp.widgets.base_widgets')
qtpyvcp.widgets.base_widgets.base_widget = _make_mod(
    'qtpyvcp.widgets.base_widgets.base_widget'
)
qtpyvcp.widgets.input_widgets = _make_mod('qtpyvcp.widgets.input_widgets')
qtpyvcp.widgets.input_widgets.mdientry_widget = _make_mod(
    'qtpyvcp.widgets.input_widgets.mdientry_widget'
)
qtpyvcp.widgets.input_widgets.file_system = _make_mod(
    'qtpyvcp.widgets.input_widgets.file_system'
)
qtpyvcp.widgets.dialogs = _make_mod('qtpyvcp.widgets.dialogs')
qtpyvcp.widgets.display_widgets = _make_mod(
    'qtpyvcp.widgets.display_widgets'
)
qtpyvcp.widgets.display_widgets.status_led = _make_mod(
    'qtpyvcp.widgets.display_widgets.status_led'
)
qtpyvcp.widgets.hal_widgets = _make_mod('qtpyvcp.widgets.hal_widgets')
qtpyvcp.widgets.hal_widgets.hal_led = _make_mod(
    'qtpyvcp.widgets.hal_widgets.hal_led'
)

# actions submodules
qtpyvcp.actions.machine_actions = _make_mod('qtpyvcp.actions.machine_actions')
qtpyvcp.actions.program_actions = _make_mod(
    'qtpyvcp.actions.program_actions'
)

# ── symbols that code imports directly ─────────────────────────────────────

mock_logger = MagicMock()
mock_logger.getLogger.return_value = MagicMock()
sys.modules['qtpyvcp.utilities.logger'] = mock_logger

qtpyvcp.plugins.getPlugin = MagicMock()
qtpyvcp.widgets.qtdesigner._DesignerPlugin = MagicMock()
qtpyvcp.widgets.dialogs.hideActiveDialog = MagicMock()
qtpyvcp.widgets.input_widgets.file_system.RemovableDeviceComboBox = MagicMock()
qtpyvcp.widgets.display_widgets.status_led.StatusLED = MagicMock()
qtpyvcp.widgets.hal_widgets.hal_led.HalLedIndicator = MagicMock()

qtpyvcp.utilities.info.Info = MagicMock()
qtpyvcp.actions.machine_actions.issue_mdi = MagicMock()
qtpyvcp.actions.program_actions.load = MagicMock()


# PySide6Ui – used by mk_dro / input_overlay
class _MockPySide6Ui:
    def __init__(self, *args):
        pass

    def load(self):
        return MagicMock(), MagicMock()


sys.modules['qtpyvcp.utilities.pyside_ui_loader'].PySide6Ui = _MockPySide6Ui


# VCPBaseWidget – must be a real class (not MagicMock) because code does:
#   class MkMdiEntry(QWidget, VCPBaseWidget):
# A MagicMock raises "metaclass conflict" as a base class.
class _VCPBaseWidget:
    pass


qtpyvcp.widgets.base_widgets.base_widget.VCPBaseWidget = _VCPBaseWidget


# MDIEntry – imported by mdi_entry.py; needs to be a class so the import works.
class _MDIEntry:
    pass


qtpyvcp.widgets.input_widgets.mdientry_widget.MDIEntry = _MDIEntry


# VCPButton – MkPushButton inherits from it and calls setText/text().
# Using MagicMock as base would break inheritance; use a minimal class with
# working text/setText backed by a dict.
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


qtpyvcp.widgets.VCPButton = _VCPButton
