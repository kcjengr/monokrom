from qtpy.QtCore import Property, QTimer
from qtpyvcp.widgets import VCPButton
from qtpyvcp.actions import bindWidget, InvalidAction
from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget
from qtpyvcp.actions.machine_actions import estop

from qtpyvcp.utilities.logger import getLogger

#import pydevd;pydevd.settrace()

LOG = getLogger(__name__)


class EstopButton(VCPButton, HALWidget):
    """eStop button for triggering QtPyVCP eStop action.

    Button for setting `bit` HAL pin values.

    .. table:: Generated HAL Pins

        =========================             ===== =========
        HAL Pin Name                          Type  Direction
        =========================             ===== =========
        qtpyvcp.button.enable                 bit   in
        qtpyvcp.button.estop-reset            bit   in
        qtpyvcp.button.out                    bit   out
        qtpyvcp.button.checked                bit   out
        qtpyvcp.button.not-checked            bit   out
        =========================             ===== =========


    Args:
        parent (QWidget, optional) : The parent widget of the button, or None.

    """

    def __init__(self, parent=None):
        super(EstopButton, self).__init__(parent)

        self._enable_pin = None
        self._estop_reset_pin = None
        self._pressed_pin = None
        self._checked_pin = None
        self._not_checked_pin = None

        self.pressed.connect(self.onPress)
        self.released.connect(self.onRelease)
        self.toggled.connect(self.onCheckedStateChanged)

    def onPress(self):
        if self._pressed_pin is not None:
            self._pressed_pin.value = True

    def onRelease(self):
        if self._pressed_pin is not None:
            self._pressed_pin.value = False

    def onCheckedStateChanged(self, checked):
        if self._checked_pin is not None:
            self._checked_pin.value = checked
            self._not_checked_pin.value = not checked
            # set style based on state
            if checked:
                self.setStyleClass('estop_triggered')
            else:
                self.setStyleClass('estop_armed')

    def setIsActive(self, state):
        LOG.debug(f'Active = {state}')
        # update visual state based on estop pin state
        if state:
            self.setStyleClass('estop_triggered')
        else:
            self.setStyleClass('estop_armed')

    def reset_in(self, is_reset):
        if is_reset:
            self.setChecked(False)


    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()

        # add button.enable HAL pin
        self._enable_pin = comp.addPin(obj_name + ".enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        self._estop_reset_pin = comp.addPin(obj_name + ".estop-reset", "bit", "in")
        self._estop_reset_pin.value = False
        self._estop_reset_pin.valueChanged.connect(self.reset_in)


        # add button.out HAL pin
        self._pressed_pin = comp.addPin(obj_name + ".out", "bit", "out")
        
        if self.isCheckable():
            # add button.checked HAL pin
            self._checked_pin = comp.addPin(obj_name + ".checked", "bit", "out")
            self._not_checked_pin = comp.addPin(obj_name + ".not-checked", "bit", "out")
            self._checked_pin.value = self.isChecked()
            self._not_checked_pin.value = not self.isChecked()
            if self.isChecked():
                self.setStyleClass('estop_triggered')
            else:
                self.setStyleClass('estop_armed')

