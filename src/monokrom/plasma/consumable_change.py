"""Consumable change state machine for offset management."""


class ConsumableChangeService:
    """Manages consumable change mode with X/Y offset handling.

    When toggled on, sets machine offsets based on user input and enables
    the consumable-change HAL pin. When toggled off, resets offsets.

    Button flow: feed_hold enables the consumable_change button,
    cycle_start/stop_abort disables it.
    """

    def __init__(self, hal):
        self.hal = hal

    # -- Public API -----------------------------------------------------------

    def handle_button(self, action, btn_enabled, btn_checked, cycle_enabled):
        """Handle feed_hold / cycle_start / stop_abort button clicks.

        Args:
            action: One of 'feed_hold', 'cycle_start', 'stop_abort'.
            btn_enabled: Current enabled state of the consumable change toggle.
            btn_checked: Current checked state of the consumable change toggle.
            cycle_enabled: Current enabled state of the cycle start button.
        """
        if action in ('cycle_start', 'stop_abort'):
            return {
                'btn_consumable_change': {'enabled': False, 'checked': False},
                'btn_cycle_start': {'enabled': cycle_enabled}
            }

        if action == 'feed_hold':
            return {
                'btn_consumable_change': {'enabled': True},
                'btn_cycle_start': {'enabled': cycle_enabled}
            }

    def toggle_on(self, consumable_offset_x_value, consumable_offset_y_value,
                  pos_absolute):
        """Enable consumable change mode.

        Args:
            consumable_offset_x_value: Current X offset from UI widget.
            consumable_offset_y_value: Current Y offset from UI widget.
            pos_absolute: Plugin providing absolute axis positions [x, y].

        Returns:
            dict with UI state changes needed.
        """
        x_current_pos = float(pos_absolute.Absolute(0))
        y_current_pos = float(pos_absolute.Absolute(1))
        scale = self.hal.get_value('plasmac.offset-scale')
        self.hal.set_p('plasmac.x-offset',
                       f'{(consumable_offset_x_value - x_current_pos)/scale:.0f}')
        self.hal.set_p('plasmac.y-offset',
                       f'{(consumable_offset_y_value - y_current_pos)/scale:.0f}')
        self.hal.set_p('plasmac.consumable-change', '1')

        return {
            'btn_cycle_start': {'enabled': False}
        }

    def toggle_off(self):
        """Disable consumable change mode and reset offsets.

        Returns:
            dict with UI state changes needed.
        """
        self.hal.set_p('plasmac.x-offset', f'{0:.0f}')
        self.hal.set_p('plasmac.y-offset', f'{0:.0f}')
        self.hal.set_p('plasmac.consumable-change', '0')

        return {
            'btn_cycle_start': {'enabled': True}
        }
