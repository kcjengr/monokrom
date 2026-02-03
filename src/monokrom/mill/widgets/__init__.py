from qtpyvcp.widgets.qtdesigner import _DesignerPlugin
from .mill_line_edit import MkMillLineEdit
from .mill_push_button import MkMillPushButton

class MkMillLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkMillLineEdit

class MkMillPushButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return MkMillPushButton
