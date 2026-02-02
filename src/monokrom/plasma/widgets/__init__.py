from qtpyvcp.widgets.qtdesigner import _DesignerPlugin
from .plasma_line_edit import PlasmaLineEdit
from .plasma_push_button import PlasmaPushButton
from .plasma_hal_double_spinbox import PlasmaHalDoubleSpinBox
from .plasma_hal_spinbox import PlasmaHalSpinBox
from .plasma_add_process import PlasmaAddProcess
from .plasma_hal_checkbox import PlasmaHalCheckBox
from .cyclestart_action_button import CycleStartActionButton

class PlasmaLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaLineEdit

class PlasmaPushButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaPushButton

class PlasmaHalDoubleSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalDoubleSpinBox

class PlasmaHalSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalSpinBox


class PlasmaAddProcess_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaAddProcess


class PlasmaHalCheckBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalCheckBox

class CycleStartActionButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return CycleStartActionButton
