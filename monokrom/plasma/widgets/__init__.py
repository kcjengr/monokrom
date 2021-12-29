from qtpyvcp.widgets.qtdesigner import _DesignerPlugin

from .plasma_line_edit import PlasmaLineEdit
class PlasmaLineEdit_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaLineEdit

from .plasma_push_button import PlasmaPushButton
class PlasmaPushButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaPushButton

from .plasma_hal_double_spinbox import PlasmaHalDoubleSpinBox
class PlasmaHalDoubleSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalDoubleSpinBox

from .plasma_hal_spinbox import PlasmaHalSpinBox
class PlasmaHalSpinBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalSpinBox


from .plasma_add_process import PlasmaAddProcess
class PlasmaAddProcess_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaAddProcess


from .plasma_hal_checkbox import PlasmaHalCheckBox
class PlasmaHalCheckBox_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return PlasmaHalCheckBox

from .cyclestart_action_button import CycleStartActionButton
class CycleStartActionButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return CycleStartActionButton

from .estop_action_button import EstopActionButton
class EstopActionButton_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return EstopActionButton
