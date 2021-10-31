from qtpyvcp.widgets.hal_widgets.hal_spinbox import HalQSpinBox

from qtpyvcp import SETTINGS


class PlasmaHalSpinBox(HalQSpinBox):
    def __init__(self, parent=None):
        super(PlasmaHalSpinBox, self).__init__(parent)
        self._setting = None
        self._setting_name = str(self.objectName()).replace('_', '-')
    
    def setDisplayValue(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def initialize(self):
        self._setting = SETTINGS.get(self._setting_name)
        if self._setting is not None:
            if self._setting.max_value is not None:
                self.setMaximum(self._setting.max_value)
            if self._setting.min_value is not None:
                self.setMinimum(self._setting.min_value)

            self.setDisplayValue(self._setting.getValue())
            self._setting.notify(self.setDisplayValue)
            self.valueChanged.connect(self._setting.setValue)
