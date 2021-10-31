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
