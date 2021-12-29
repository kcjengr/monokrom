from qtpy.QtCore import Property, QTimer
from qtpyvcp.widgets import VCPButton
from qtpyvcp.actions import bindWidget, InvalidAction
from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget
from qtpyvcp.actions.machine_actions import estop

from qtpyvcp.utilities.logger import getLogger

#import pydevd;pydevd.settrace()

LOG = getLogger(__name__)


class EstopActionButton(VCPButton, HALWidget):
    """eStop button for triggering QtPyVCP eStop action.

    Button for setting `bit` HAL pin values.

    .. table:: Generated HAL Pins

        =========================             ===== =========
        HAL Pin Name                          Type  Direction
        =========================             ===== =========
        qtpyvcp.button.enable                 bit   in
        qtpyvcp.button.estop-reset            bit   in
        qtpyvcp.button.estop-active           bit   in
        qtpyvcp.button.out                    bit   out
        qtpyvcp.button.checked                bit   out
        =========================             ===== =========


    Args:
        parent (QWidget, optional) : The parent widget of the button, or None.

    """

    def __init__(self, parent=None):
        super(EstopActionButton, self).__init__(parent)

        self._action_name = ''
        self.actionName = ''
        self._enable_pin = None
        self._estop_reset_pin = None
        self._estop_active_pin = None
        self._pressed_pin = None
        self._checked_pin = None

        self.pulse_timer = None
        self.pulse_state = -1

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


    @Property(str)
    def actionName(self):
        """Property for the name of the action the button triggers (str).

        When this property is set it calls :meth:`QtPyVCP.actions.bindWidget`
        to bind the widget to the action.
        """
        return self._action_name

    @actionName.setter
    def actionName(self, action_name):
        self._action_name = action_name
        try:
            bindWidget(self, action_name)
        except InvalidAction:
            pass

    def setReset(self, state):
        LOG.debug(f'Reset = {state}')
        if state:
            LOG.debug('reset estop signal recieved')
            estop.reset()
    
    def triggerEstop(self):
            estop.activate()

    def setIsActive(self, state):
        LOG.debug(f'Active = {state}')
        # update visual state based on estop pin state
        if state:
            self.setStyleClass('estop_triggered')
        else:
            self.setStyleClass('estop_armed')


    def flashButton(self):
        if self.pulse_state > 0:
            self.setStyleClass('cycle_running')
        else:
            self.setStyleClass('cycle_stopped')
        self.pulse_state *= -1


    def initialize(self):
        comp = hal.getComponent()
        obj_name = self.getPinBaseName()


        # add button.enable HAL pin
        self._enable_pin = comp.addPin(obj_name + ".enable", "bit", "in")
        self._enable_pin.value = self.isEnabled()
        self._enable_pin.valueChanged.connect(self.setEnabled)

        self._estop_reset_pin = comp.addPin(obj_name + ".estop-reset", "bit", "in")
        self._estop_reset_pin.valueChanged.connect(self.setReset)

        self._estop_active_pin = comp.addPin(obj_name + ".estop-active", "bit", "in")
        self._estop_active_pin.valueChanged.connect(self.setIsActive)


        # add button.out HAL pin
        self._pressed_pin = comp.addPin(obj_name + ".out", "bit", "out")
        
        if self.isCheckable():
            # add button.checked HAL pin
            self._checked_pin = comp.addPin(obj_name + ".checked", "bit", "out")
            self._checked_pin.value = self.isChecked()

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.flashButton)
