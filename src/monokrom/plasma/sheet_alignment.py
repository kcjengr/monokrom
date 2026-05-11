"""Sheet alignment state machine for coordinate system rotation."""

import math


class SheetAlignmentService:
    """Manages sheet alignment with two-point reference and angle calculation.

    When laser or point buttons are toggled, enters alignment mode — saves current
    positions as references, enables subsequent controls, and switches to manual mode.
    On alignment completion, resets all state and performs coordinate transforms.
    """

    def __init__(self, hal):
        self.hal = hal
        self.sheet_align_p1 = None
        self.sheet_align_p2 = None

    # -- Public API -----------------------------------------------------------

    def handle_toggle(self, button_name, checked):
        """Handle toggle/click events from alignment buttons.

        Args:
            button_name: One of 'btn_laser', 'btn_sheet_align_pt1',
                         'btn_sheet_align_pt2', 'btn_sheet_doalign'.
            checked: Current checked state for toggles (ignored for clicked).

        Returns:
            dict with UI state changes needed.
        """
        if button_name == 'btn_laser':
            return self._handle_laser(checked)

        if button_name == 'btn_sheet_align_pt1':
            return self._handle_pt1(checked)

        if button_name == 'btn_sheet_align_pt2':
            return self._handle_pt2(checked)

        if button_name == 'btn_sheet_doalign':
            return self._handle_doalign()

    def get_status_text(self):
        """Generate status text for the alignment display widget.

        Returns:
            str with REF1 and/or REF2 coordinates formatted for display.
        """
        ref1 = "REF1:..."
        ref2 = "REF2:..."

        if self.sheet_align_p1 is not None:
            ref1 = f"REF1:\n{self.sheet_align_p1[0]:.4f},\n{self.sheet_align_p1[1]:.4f}"

        if self.sheet_align_p2 is not None:
            ref2 = f"REF2:\n{self.sheet_align_p2[0]:.4f},\n{self.sheet_align_p2[1]:.4f}"

        return f'{ref1}\n{ref2}'

    def get_current_points(self):
        """Return current alignment points for external use.

        Returns:
            tuple of (p1, p2) where each is [x, y] or None.
        """
        return self.sheet_align_p1, self.sheet_align_p2

    # -- Internal -------------------------------------------------------------

    def _handle_laser(self, checked):
        """Handle laser button toggle — master control for alignment mode."""
        if checked:
            return {
                'btn_sheet_align_pt1': {'enabled': True},
            }

        # Reset all state when laser is unchecked
        return {
            'btn_sheet_align_pt1': {'enabled': False, 'checked': False},
            'btn_sheet_align_pt2': {'enabled': False, 'checked': False},
            'btn_sheet_doalign': {'enabled': False},
        }

    def _handle_pt1(self, checked):
        """Handle point 1 button toggle."""
        if checked:
            return {
                'btn_sheet_align_pt2': {'enabled': True},
            }

        # Reset downstream state when pt1 is unchecked
        return {
            'btn_sheet_align_pt2': {'enabled': False, 'checked': False},
            'btn_sheet_doalign': {'enabled': False},
        }

    def _handle_pt2(self, checked):
        """Handle point 2 button toggle."""
        if checked:
            return {
                'btn_sheet_doalign': {'enabled': True},
            }

        # Reset downstream state when pt2 is unchecked
        return {
            'btn_sheet_doalign': {'enabled': False},
        }

    def _handle_doalign(self):
        """Handle do-align button click — triggers alignment sequence."""
        # Return UI reset state for the caller to apply after alignment completes
        return {
            'btn_sheet_align_pt1': {'checked': False, 'enabled': False},
            'btn_sheet_align_pt2': {'checked': False, 'enabled': False},
            'btn_laser': {'checked': False},
            'btn_sheet_doalign': {'enabled': False},
        }

    def set_point_1(self, pos_absolute):
        """Record point 1 from current machine position.

        Args:
            pos_absolute: Plugin providing absolute axis positions [x, y].
        """
        self.hal.send_mdi('G10 L2 P0 R0')
        x_current_pos = float(pos_absolute.Absolute(0))
        y_current_pos = float(pos_absolute.Absolute(1))
        self.sheet_align_p1 = [x_current_pos, y_current_pos]

    def set_point_2(self, pos_absolute):
        """Record point 2 from current machine position.

        Args:
            pos_absolute: Plugin providing absolute axis positions [x, y].
        """
        self.hal.send_mdi('G10 L2 P0 R0')
        x_current_pos = float(pos_absolute.Absolute(0))
        y_current_pos = float(pos_absolute.Absolute(1))
        self.sheet_align_p2 = [x_current_pos, y_current_pos]

    def align(self, laser_offset_x_value, laser_offset_y_value):
        """Execute the full alignment sequence.

        Sends MDI commands to reset coordinate system, apply rotation angle,
        and move to origin. Resets internal state on completion.

        Args:
            laser_offset_x_value: Current laser X offset from UI widget.
            laser_offset_y_value: Current laser Y offset from UI widget.

        Returns:
            bool: True if alignment succeeded, False if points not set.
        """
        if self.sheet_align_p1 is None or self.sheet_align_p2 is None:
            return False

        # Reset coordinate system
        self.hal.send_mdi('G10 L2 P0 R0')
        self.hal.wait_complete()
        self.hal.send_mdi('G10 L2 P0 X0 Y0')
        self.hal.wait_complete()
        self.hal.wait_complete()

        # Calculate rotation angle from two points
        x_diff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
        y_diff = self.sheet_align_p2[1] - self.sheet_align_p1[1]
        z_angle = self._calculate_angle(x_diff, y_diff)

        # Apply laser offset compensation and rotation
        self.hal.send_mdi(f'G10 L20 P0 X{laser_offset_x_value} Y{laser_offset_y_value}')
        self.hal.wait_complete()
        self.hal.send_mdi(f'G10 L2 P0 R{z_angle}')
        self.hal.wait_complete()
        self.hal.send_mdi('G0 X0 Y0')
        self.hal.wait_complete()

        # Reset state
        self.sheet_align_p1 = None
        self.sheet_align_p2 = None

        return True

    @staticmethod
    def _calculate_angle(x_diff, y_diff):
        """Calculate rotation angle from two point differences.

        Implements quadrant-aware atan2 logic matching the original sheet_align method.

        Args:
            x_diff: Difference in X coordinates (p2.x - p1.x).
            y_diff: Difference in Y coordinates (p2.y - p1.y).

        Returns:
            float: Rotation angle in degrees.
        """
        if x_diff and y_diff:
            z_angle = math.degrees(math.atan(y_diff / x_diff))
            if x_diff > 0:
                z_angle += 180
            elif y_diff > 0:
                z_angle += 360
            if abs(x_diff) < abs(y_diff):
                z_angle -= 90
        elif x_diff:
            if x_diff > 0:
                z_angle = 180
            else:
                z_angle = 0
        elif y_diff:
            if y_diff > 0:
                z_angle = 180
            else:
                z_angle = 0
        else:
            z_angle = 0

        return z_angle

    def reset(self):
        """Clear alignment points without sending any HAL commands."""
        self.sheet_align_p1 = None
        self.sheet_align_p2 = None
