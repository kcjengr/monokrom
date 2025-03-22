from PySide6.QtCore import Property

from qtpyvcp import hal
from qtpyvcp.widgets.hal_widgets.hal_spinbox import HalQSpinBox
from qtpyvcp import SETTINGS

from qtpyvcp.utilities.logger import getLogger

#import pydevd;pydevd.settrace()

LOG = getLogger(__name__)

class PlasmaHalSpinBox(HalQSpinBox):
    """Plasma HAL SpinBox for use with plasmac

    SpinBox for displaying and setting `s32` HAL pin values AND
    to have the value saved to persistent storage on exit.

    .. table:: Generated HAL Pins

        ========================= ========= =========
        HAL Pin Name              Type      Direction
        ========================= ========= =========
        qtpyvcp.spinbox.enable    s32       in
        qtpyvcp.spinbox.in        s32       in
        qtpyvcp.spinbox.out       s32       out
        ========================= ========= =========
    """

    def __init__(self, parent=None):
        super(PlasmaHalSpinBox, self).__init__(parent)
        self._setting = None
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

    def initialize(self):
        LOG.debug("Initalizing PlasmaHalSpinBox: '{}'".format(self._setting_name))
        self._setting = SETTINGS.get(self._setting_name)
        if self._setting is not None:
            if self._setting.max_value is not None:
                self.setMaximum(self._setting.max_value)
            if self._setting.min_value is not None:
                self.setMinimum(self._setting.min_value)

            self.setDisplayValue(self._setting.getValue())
            self._setting.notify(self.setDisplayValue)
            self.valueChanged.connect(self._setting.setValue)

        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        pin_typ = 's32'
        # add spinbox.enable HAL pin
        self._enabled_pin = comp.addPin(obj_name + ".enable", "bit", "in")
        self._enabled_pin.value = self.isEnabled()
        self._enabled_pin.valueChanged.connect(self.setEnabled)

        # add spinbox.out HAL pin
        self._value_pin = comp.addPin(obj_name + ".out", pin_typ, "out")
        self._value_pin.value = self.value()

        # add spinbox.in HAL pin
        self._set_value_pin = comp.addPin(obj_name + ".in", pin_typ, "in")
        self._set_value_pin.valueChanged.connect(self.setValue)
