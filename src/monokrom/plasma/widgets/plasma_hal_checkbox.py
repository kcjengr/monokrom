from PySide6.QtCore import Property

from qtpyvcp import hal
from qtpyvcp.widgets.hal_widgets.hal_checkbox import HalCheckBox

from qtpyvcp import SETTINGS
from qtpyvcp.utilities.logger import getLogger

LOG = getLogger(__name__)


class PlasmaHalCheckBox(HalCheckBox):
    """HAL CheckBox

    CheckBox for displaying and setting `bit` HAL pin values AND
    to have the value saved to persistent storage on exit.

    .. table:: Generated HAL Pins

        ========================= ===== =========
        HAL Pin Name              Type  Direction
        ========================= ===== =========
        qtpyvcp.checkbox.enable   bit   in
        qtpyvcp.checkbox.check    bit   in
        qtpyvcp.checkbox.checked  bit   out
        ========================= ===== =========
    """
    def __init__(self, parent=None):
        super(PlasmaHalCheckBox, self).__init__(parent)
        self._setting = None
        self._setting_name = None

        # self._enable_pin = None
        # self._check_pin = None
        # self._checked_pin = None

        self.toggled.connect(self.onCheckedStateChanged)

    # def changeEvent(self, event):
    #     super(HalCheckBox, self).changeEvent(event)
    #     if event == QEvent.EnabledChange and self._enable_pin is not None:
    #         self._enable_pin.value = self.isEnabled()
    #
    # def onCheckedStateChanged(self, checked):
    #     if self._checked_pin is not None:
    #         self._checked_pin.value = checked

    def setDisplayChecked(self, checked):
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)

    @Property(str)
    def settingName(self):
        return self._setting_name

    @settingName.setter
    def settingName(self, name):
        self._setting_name = name

    def initialize(self):
        LOG.debug("Initalizing PlasmaHalCheckBox: '{}'".format(self._setting_name))
        self._setting = SETTINGS.get(self._setting_name)
        if self._setting is not None:

            value = self._setting.getValue()

            self.setDisplayChecked(value)
            self.toggled.emit(value)

            self._setting.notify(self.setDisplayChecked)
            self.toggled.connect(self._setting.setValue)

        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        # add checkbox.enable HAL pin
        self._enable_pin = comp.addPin(obj_name + ".enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        # add checkbox.check HAL pin
        self._check_pin = comp.addPin(obj_name + ".check", "bit", "in")
        self._check_pin.value = self.isChecked()
        self._check_pin.valueChanged.connect(self.setChecked)

        # add checkbox.checked HAL pin
        self._checked_pin = comp.addPin(obj_name + ".checked", "bit", "out")
        self._checked_pin.value = self.isChecked()
