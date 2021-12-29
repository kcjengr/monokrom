from qtpy.QtCore import Property, QTimer
from qtpyvcp.widgets import VCPButton
from qtpyvcp.actions import bindWidget, InvalidAction
from qtpyvcp import hal
from qtpyvcp.widgets import HALWidget

from qtpyvcp.utilities.logger import getLogger

#import pydevd;pydevd.settrace()

LOG = getLogger(__name__)


class CycleStartActionButton(VCPButton, HALWidget):
    """Cycle Start button for triggering QtPyVCP prog run action.

    Button for setting `bit` HAL pin values.

    .. table:: Generated HAL Pins

        =========================             ===== =========
        HAL Pin Name                          Type  Direction
        =========================             ===== =========
        qtpyvcp.button.enable                 bit   in
        qtpyvcp.button.program-is-running     bit   in
        qtpyvcp.button.program-is-paused      bit   in
        qtpyvcp.button.program-is-idle        bit   in
        qtpyvcp.button.out                    bit   out
        qtpyvcp.button.checked                bit   out
        =========================             ===== =========


    Args:
        parent (QWidget, optional) : The parent widget of the button, or None.

    """

    def __init__(self, parent=None):
        super(CycleStartActionButton, self).__init__(parent)

        self._action_name = ''
        self.actionName = 'program.run'
        self._enable_pin = None
        self._program_is_running_pin = None
        self._program_is_paused_pin = None
        self._program_is_idle_pin = None
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

    def setIsRunning(self, running):
        LOG.debug(f'Running state = {running}')
        if running:
            self.setText('CYCLE RUNNING')
            self.setStyleClass('cycle_running')

    def setIsPaused(self, paused):
        LOG.debug(f'Paused state = {paused}')
        if paused:
            self.setText('CYCLE PAUSED')
            self.setStyleClass('cycle_running')
            self.pulse_timer.start(500)
        else:
            self.pulse_timer.stop()


    def setIsIdle(self, idle):
        LOG.debug(f'Idle state = {idle}')
        if idle:
            self.setText('CYCLE START')
            self.setStyleClass('cycle_stopped')

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

        self._program_is_running_pin = comp.addPin(obj_name + ".program-is-running", "bit", "in")
        self._program_is_running_pin.valueChanged.connect(self.setIsRunning)

        self._program_is_paused_pin = comp.addPin(obj_name + ".program-is-paused", "bit", "in")
        self._program_is_paused_pin.valueChanged.connect(self.setIsPaused)

        self._program_is_idle_pin = comp.addPin(obj_name + ".program-is-idle", "bit", "in")
        self._program_is_idle_pin.valueChanged.connect(self.setIsIdle)


        # add button.out HAL pin
        self._pressed_pin = comp.addPin(obj_name + ".out", "bit", "out")
        
        if self.isCheckable():
            # add button.checked HAL pin
            self._checked_pin = comp.addPin(obj_name + ".checked", "bit", "out")
            self._checked_pin.value = self.isChecked()

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.flashButton)
