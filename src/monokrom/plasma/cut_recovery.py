"""Cut recovery state machine for post-stop jog+offset positioning."""

from qtpyvcp.utilities.logger import getLogger
LOG = getLogger(__name__)


class CutRecoveryService:
    """Manages cut recovery mode with jog offsets and coordinate math.

    When feed_hold is pressed, enters recovery mode — saves current positions,
    enables the recovery widget, and switches to jog stack index 1.
    Cycle start / stop abort exit recovery mode and reset offsets.

    Direction buttons set paused-motion-speed based on the recovery speed slider.
    N/S/E/W directional buttons apply incremental offset moves through HAL.
    """

    def __init__(self, hal):
        self.hal = hal
        self.cut_recovery_status = False
        self.x_orig = None
        self.y_orig = None
        self.z_orig = None
        self.o_scale = None
        self._linear_setting = 'mm'

    # -- Public API -----------------------------------------------------------

    def handle_button(self, button_name, widget_recovery, jog_stack,
                      cut_recovery_speed_value):
        """Handle feed_hold / cycle_start / stop_abort clicks.

        Args:
            button_name: One of 'btn_stop_abort', 'btn_cycle_start', 'btn_feed_hold'.
            widget_recovery: Reference to the recovery widget group.
            jog_stack: Reference to the jog stack widget (setCurrentIndex).
            cut_recovery_speed_value: Current value of the recovery speed slider.

        Returns:
            dict with UI state changes needed.
        """
        if button_name in ('btn_stop_abort', 'btn_cycle_start'):
            self._exit_recovery(widget_recovery, jog_stack)
            return {
                'widget_recovery': {'enabled': False},
            }

        if button_name == 'btn_feed_hold':
            self._enter_recovery(widget_recovery, jog_stack,
                                cut_recovery_speed_value)
            return {
                'widget_recovery': {'enabled': True},
            }

    def set_direction(self, direction, cut_recovery_speed_value):
        """Set the recovery motion speed/direction.

        Args:
            direction: -1 (reverse), 0 (stop), or 1 (forward).
            cut_recovery_speed_value: Current value of the recovery speed slider.
        """
        LOG.debug(f"set_direction: direction = {direction}")
        if direction == 0:
            self.hal.set_p('plasmac.paused-motion-speed', '0')
        else:
            speed = cut_recovery_speed_value * 0.01 * direction
            self.hal.set_p('plasmac.paused-motion-speed', str(speed))
            LOG.debug(f"set_direction: speed = {speed}")

    def move(self, x_dir, y_dir, laser_offset_x, laser_offset_y,
             linear_setting, btn_cut_recover_fwd, btn_cut_recover_rev):
        """Perform a single recovery move in the given direction.

        Args:
            x_dir: -1, 0, or 1 for X axis direction.
            y_dir: -1, 0, or 1 for Y axis direction.
            laser_offset_x: Current laser X offset value from UI widget.
            laser_offset_y: Current laser Y offset value from UI widget.
            linear_setting: 'mm' or 'inch' — determines max move distance.
            btn_cut_recover_fwd: Reference to the forward recovery button (for isEnabled).
            btn_cut_recover_rev: Reference to the reverse recovery button (for isEnabled).

        Returns:
            bool: True if the move was applied, False if rejected (bounds check).
        """
        if not self.cut_recovery_status:
            LOG.debug("Cut Recovery status = FALSE, exit move.")
            return False

        LOG.debug(f"Cut Recovery button push (x,y) {x_dir}, {y_dir}")

        max_move = 0.4 if linear_setting == 'inch' else 10

        laser_on = bool(self.hal.get_value('qtpyvcp.laser.out'))
        kerf_width = float(self.hal.get_value('qtpyvcp.param-kerfwidth.out'))
        LOG.debug(f"kerf_width = {kerf_width}")

        dist_x = kerf_width * x_dir
        dist_y = kerf_width * y_dir
        
        LOG.debug(f"Distance x={dist_x}, y={dist_y}")

        axis_x_eoffset = float(self.hal.get_value('axis.x.eoffset'))
        axis_y_eoffset = float(self.hal.get_value('axis.y.eoffset'))
        LOG.debug(f"axis_x_eoffset = {axis_x_eoffset}, axis_y_eoffset = {axis_y_eoffset}")

        x_total = axis_x_eoffset - (laser_offset_x * laser_on) + dist_x
        y_total = axis_y_eoffset - (laser_offset_y * laser_on) + dist_y
        LOG.debug(f"x_total = {x_total}, y_total = {y_total}")

        if x_total > max_move or x_total < -max_move:
            LOG.debug("x_total is outside max_move")
            return False
        if y_total > max_move or y_total < -max_move:
            LOG.debug("y_total is outside max_move")
            return False

        move_x = int(dist_x / self.o_scale)
        move_y = int(dist_y / self.o_scale)
        LOG.debug(f"o_scale = {self.o_scale}")
        LOG.debug(f"move_x = {move_x}, move_y = {move_y}")

        current_x = float(self.hal.get_value('plasmac.x-offset'))
        current_y = float(self.hal.get_value('plasmac.y-offset'))
        LOG.debug(f"current_x offset = {current_x}")
        LOG.debug(f"current_y offset = {current_y}")

        self.hal.set_p('plasmac.x-offset', f'{current_x + move_x:.0f}')
        self.hal.set_p('plasmac.y-offset', f'{current_y + move_y:.0f}')
        self.hal.set_p('plasmac.cut-recovery', '1')

        return True

    def cancel_pressed(self):
        """Cancel cut recovery mode by setting the HAL pin to 0."""
        if bool(self.hal.get_value('plasmac.cut-recovery')):
            self.hal.set_p('plasmac.cut-recovery', '0')

    def get_cut_recovery_status(self):
        """Return current cut recovery status."""
        return self.cut_recovery_status

    # -- Internal -------------------------------------------------------------

    def _enter_recovery(self, widget_recovery, jog_stack, speed_value):
        """Enter cut recovery mode."""
        self.hal.set_p('plasmac.cut-recovery', '0')
        self.cut_recovery_status = True
        widget_recovery.setEnabled(True)
        jog_stack.setCurrentIndex(1)
        self.x_orig = float(self.hal.get_value('axis.x.eoffset-counts'))
        self.y_orig = float(self.hal.get_value('axis.y.eoffset-counts'))
        self.z_orig = float(self.hal.get_value('axis.z.eoffset-counts'))
        self.o_scale = float(self.hal.get_value('plasmac.offset-scale'))
        self.hal.set_p('plasmac.x-offset', f'{0:.0f}')
        self.hal.set_p('plasmac.y-offset', f'{0:.0f}')
        LOG.debug("Recovery mode Entered.")

    def _exit_recovery(self, widget_recovery, jog_stack):
        """Exit cut recovery mode and reset offsets."""
        self.hal.set_p('plasmac.cut-recovery', '0')
        self.cut_recovery_status = False
        widget_recovery.setEnabled(False)
        jog_stack.setCurrentIndex(0)
        self.hal.set_p('plasmac.x-offset', f'{0:.0f}')
        self.hal.set_p('plasmac.y-offset', f'{0:.0f}')
        LOG.debug("Recovery mode Exit.")
