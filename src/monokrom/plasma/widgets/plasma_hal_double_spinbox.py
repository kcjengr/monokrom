from qtpy.QtCore import Property, Signal

from qtpyvcp import hal
from qtpyvcp.widgets.hal_widgets.hal_double_spinbox import HalDoubleSpinBox
from qtpyvcp import SETTINGS

from qtpyvcp.utilities.logger import getLogger

#import pydevd;pydevd.settrace()

LOG = getLogger(__name__)

class PlasmaHalDoubleSpinBox(HalDoubleSpinBox):
    """Plasma HAL DoubleSpinBox for use with plasmac

    DoubleSpinBox for displaying and setting `float` HAL pin values AND
    to have the value saved to persistent storage on exit.

    .. table:: Generated HAL Pins

        ========================= ========= =========
        HAL Pin Name              Type      Direction
        ========================= ========= =========
        qtpyvcp.spinbox.enable    bit       in
        qtpyvcp.spinbox.in        float     in
        qtpyvcp.spinbox.out       float     out
        ========================= ========= =========
    """
    
    focusReceived = Signal(object)
    
    def __init__(self, parent=None):
        super(PlasmaHalDoubleSpinBox, self).__init__(parent)
        self._setting = None
        self._original_value = None
        self._setting_name = None
        self._value_pin = None

    @Property(str)
    def settingName(self):
        return self._setting_name

    @settingName.setter
    def settingName(self, name):
        self._setting_name = name

    
    def setDisplayValue(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def forceUpdatePinValue(self):
        if self._value_pin is not None:
            self._value_pin.value = self.value()

    def editingEnded(self):
        self._setting.setValue(self.value())

    def focusInEvent(self, event):
        # fire the focusReceived signal
        self.focusReceived.emit(self)
        super(PlasmaHalDoubleSpinBox, self).focusInEvent(event)
    
    def resetToOriginal(self):
        self._setting = self._original_value
        self.setDisplayValue(self._setting)

    def initialize(self):
        LOG.debug("Initalizing PlasmaHalDoubleSpinBox: '{}'".format(self._setting_name))
        self._setting = SETTINGS.get(self._setting_name)
        self._original_value = self._setting
        if self._setting is not None:
            if self._setting.max_value is not None:
                self.setMaximum(self._setting.max_value)
            if self._setting.min_value is not None:
                self.setMinimum(self._setting.min_value)

            self.setDisplayValue(self._setting.getValue())
            self._setting.notify(self.setDisplayValue)
            #self.valueChanged.connect(self._setting.setValue)
            self.editingFinished.connect(self.editingEnded)

        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        # add spinbox.enabled HAL pin
        self._enabled_pin = comp.addPin(obj_name + ".enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)

        # add spinbox.checked HAL pin
        self._value_pin = comp.addPin(obj_name + ".out", "float", "out")
        self._value_pin.value = self.value()

        # add spinbox.checked HAL pin
        self._set_value_pin = comp.addPin(obj_name + ".in", "float", "in")
        self._set_value_pin.valueChanged.connect(self.setValue)

