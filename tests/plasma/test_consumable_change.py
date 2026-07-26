"""Tests for consumable_change.py — verify the ConsumableChangeService."""

from monokrom.plasma.consumable_change import ConsumableChangeService


class MockHal:
    def __init__(self):
        self.pins = {}
        self.set_p_calls = []

    def get_value(self, pin_name):
        return self.pins.get(pin_name)

    def set_p(self, pin_name, value):
        self.pins[pin_name] = value
        self.set_p_calls.append((pin_name, value))


class MockPos:
    @staticmethod
    def Absolute(axis):
        return [100.0, 200.0][axis]


class TestConsumableChangeServiceInit:
    def test_init_stores_hal(self):
        hal = MockHal()
        service = ConsumableChangeService(hal)
        assert service.hal is hal


class TestConsumableChangeHandleButton:
    def test_feed_hold_enables_consumable_button(self):
        hal = MockHal()
        service = ConsumableChangeService(hal)
        changes = service.handle_button('feed_hold', False, False, True)
        assert changes['btn_consumable_change'] == {'enabled': True}

    def test_cycle_start_disables_consumable_button(self):
        hal = MockHal()
        service = ConsumableChangeService(hal)
        changes = service.handle_button('cycle_start', True, False, True)
        assert changes['btn_consumable_change'] == {'enabled': False, 'checked': False}

    def test_stop_abort_disables_consumable_button(self):
        hal = MockHal()
        service = ConsumableChangeService(hal)
        changes = service.handle_button('stop_abort', True, True, True)
        assert changes['btn_consumable_change'] == {'enabled': False, 'checked': False}


class TestConsumableChangeToggleOn:
    def test_toggle_on_sets_offsets(self):
        hal = MockHal()
        hal.pins['plasmac.offset-scale'] = 1.0
        service = ConsumableChangeService(hal)

        changes = service.toggle_on(50.0, 100.0, MockPos)

        assert 'plasmac.x-offset' in hal.pins
        assert 'plasmac.y-offset' in hal.pins
        assert hal.pins['plasmac.consumable-change'] == '1'
        # x_offset=50, x_current=100, scale=1 => (50-100)/1 = -50
        assert hal.pins['plasmac.x-offset'] == '-50'
        # y_offset=100, y_current=200, scale=1 => (100-200)/1 = -100
        assert hal.pins['plasmac.y-offset'] == '-100'
        assert changes['btn_cycle_start'] == {'enabled': False}

    def test_toggle_on_with_scale_factor(self):
        hal = MockHal()
        hal.pins['plasmac.offset-scale'] = 2.0
        service = ConsumableChangeService(hal)

        service.toggle_on(10.0, 20.0, MockPos)

        # (10-100)/2 = -45, (20-200)/2 = -90
        assert hal.pins['plasmac.x-offset'] == '-45'
        assert hal.pins['plasmac.y-offset'] == '-90'


class TestConsumableChangeToggleOff:
    def test_toggle_off_resets_offsets(self):
        hal = MockHal()
        service = ConsumableChangeService(hal)

        changes = service.toggle_off()

        assert hal.pins['plasmac.x-offset'] == '0'
        assert hal.pins['plasmac.y-offset'] == '0'
        assert hal.pins['plasmac.consumable-change'] == '0'
        assert changes['btn_cycle_start'] == {'enabled': True}
