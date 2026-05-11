"""Tests for cut_recovery.py — verify the CutRecoveryService."""

from monokrom.plasma.cut_recovery import CutRecoveryService


class MockHal:
    def __init__(self):
        self.pins = {}
        self.set_p_calls = []

    def get_value(self, pin_name):
        return self.pins.get(pin_name)

    def set_p(self, pin_name, value):
        self.pins[pin_name] = value
        self.set_p_calls.append((pin_name, value))


class MockWidget:
    def __init__(self):
        self._enabled = False
        self._current_index = 0

    @property
    def enabled(self):
        return self._enabled

    def setEnabled(self, enabled):
        self._enabled = enabled

    def setCurrentIndex(self, index):
        self._current_index = index


class TestCutRecoveryInit:
    def test_init_stores_hal(self):
        hal = MockHal()
        service = CutRecoveryService(hal)
        assert service.hal is hal

    def test_init_default_state(self):
        hal = MockHal()
        service = CutRecoveryService(hal)
        assert service.cut_recovery_status is False
        assert service.x_orig is None
        assert service.y_orig is None
        assert service.z_orig is None
        assert service.o_scale is None


class TestCutRecoveryHandleButtonFeedHold:
    def test_feed_hold_enters_recovery_mode(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset-counts'] = 100
        hal.pins['axis.y.eoffset-counts'] = 200
        hal.pins['axis.z.eoffset-counts'] = 50
        hal.pins['plasmac.offset-scale'] = 1.0
        service = CutRecoveryService(hal)

        widget = MockWidget()
        jog_stack = MockWidget()

        changes = service.handle_button(
            'btn_feed_hold', widget, jog_stack, cut_recovery_speed_value=50
        )

        assert service.cut_recovery_status is True
        assert widget._enabled is True
        assert jog_stack._current_index == 1
        assert hal.pins['plasmac.x-offset'] == '0'
        assert hal.pins['plasmac.y-offset'] == '0'
        assert service.x_orig == 100
        assert service.y_orig == 200
        assert service.z_orig == 50
        assert service.o_scale == 1.0

    def test_feed_hold_does_not_set_direction(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset-counts'] = 0
        hal.pins['axis.y.eoffset-counts'] = 0
        hal.pins['axis.z.eoffset-counts'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        service = CutRecoveryService(hal)

        widget = MockWidget()
        jog_stack = MockWidget()

        service.handle_button(
            'btn_feed_hold', widget, jog_stack, cut_recovery_speed_value=50
        )

        # Enter recovery does not set direction — that's handled by separate buttons
        assert ('plasmac.paused-motion-speed', '0.5') not in hal.set_p_calls


class TestCutRecoveryHandleButtonCycleStart:
    def test_cycle_start_exits_recovery_mode(self):
        hal = MockHal()
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True

        widget = MockWidget()
        widget._enabled = True
        jog_stack = MockWidget()
        jog_stack._current_index = 1

        changes = service.handle_button(
            'btn_cycle_start', widget, jog_stack, cut_recovery_speed_value=0
        )

        assert service.cut_recovery_status is False
        assert widget._enabled is False
        assert jog_stack._current_index == 0
        assert hal.pins['plasmac.x-offset'] == '0'
        assert hal.pins['plasmac.y-offset'] == '0'


class TestCutRecoveryHandleButtonStopAbort:
    def test_stop_abort_exits_recovery_mode(self):
        hal = MockHal()
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True

        widget = MockWidget()
        widget._enabled = True
        jog_stack = MockWidget()
        jog_stack._current_index = 1

        changes = service.handle_button(
            'btn_stop_abort', widget, jog_stack, cut_recovery_speed_value=0
        )

        assert service.cut_recovery_status is False
        assert widget._enabled is False
        assert jog_stack._current_index == 0

    def test_stop_abort_clears_cut_recovery_pin(self):
        hal = MockHal()
        hal.pins['plasmac.cut-recovery'] = '1'
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True

        widget = MockWidget()
        widget._enabled = True
        jog_stack = MockWidget()
        jog_stack._current_index = 1

        service.handle_button(
            'btn_stop_abort', widget, jog_stack, cut_recovery_speed_value=0
        )

        assert hal.pins['plasmac.cut-recovery'] == '0'

    def test_cycle_start_clears_cut_recovery_pin(self):
        hal = MockHal()
        hal.pins['plasmac.cut-recovery'] = '1'
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True

        widget = MockWidget()
        widget._enabled = True
        jog_stack = MockWidget()
        jog_stack._current_index = 1

        service.handle_button(
            'btn_cycle_start', widget, jog_stack, cut_recovery_speed_value=0
        )

        assert hal.pins['plasmac.cut-recovery'] == '0'


class TestCutRecoverySetDirection:
    def test_direction_forward(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        service.set_direction(1, cut_recovery_speed_value=50)

        assert ('plasmac.paused-motion-speed', '0.5') in hal.set_p_calls

    def test_direction_reverse(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        service.set_direction(-1, cut_recovery_speed_value=75)

        assert ('plasmac.paused-motion-speed', '-0.75') in hal.set_p_calls

    def test_direction_stop(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        service.set_direction(0, cut_recovery_speed_value=50)

        assert ('plasmac.paused-motion-speed', '0') in hal.set_p_calls


class TestCutRecoveryMove:
    def test_move_rejected_when_not_in_recovery(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is False

    def test_move_applied_in_mm_mode(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = 0
        hal.pins['plasmac.y-offset'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 10
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        assert float(hal.pins['plasmac.x-offset']) == 10.0
        assert hal.pins['plasmac.cut-recovery'] == '1'

    def test_move_applied_in_inches(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = 0
        hal.pins['plasmac.y-offset'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 0.3
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='inch',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        # int(0.3 / 1.0) = 0, so offset stays at 0.0
        assert float(hal.pins['plasmac.x-offset']) == 0.0

    def test_move_rejected_exceeds_max_in_inches(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0.35
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = 0
        hal.pins['plasmac.y-offset'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 10
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='inch',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is False

    def test_move_with_laser_offset(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = 0
        hal.pins['plasmac.y-offset'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 100
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 5
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=2, laser_offset_y=3,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        # distX = 5 * 1 = 5, xTotal = 0 - (2 * 1) + 5 = 3
        assert float(hal.pins['plasmac.x-offset']) == 5.0

    def test_move_diagonal(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = 0
        hal.pins['plasmac.y-offset'] = 0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 10
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=1, laser_offset_x=0, laser_offset_y=0,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        assert float(hal.pins['plasmac.x-offset']) == 10.0
        assert float(hal.pins['plasmac.y-offset']) == 10.0


class TestCutRecoveryCancelPressed:
    def test_cancel_sets_cut_recovery_to_zero(self):
        hal = MockHal()
        hal.pins['plasmac.cut-recovery'] = '1'
        service = CutRecoveryService(hal)

        service.cancel_pressed()

        assert hal.pins['plasmac.cut-recovery'] == '0'

    def test_cancel_does_nothing_when_already_zero(self):
        hal = MockHal()
        hal.pins['plasmac.cut-recovery'] = '0'
        service = CutRecoveryService(hal)

        service.cancel_pressed()

        assert hal.pins['plasmac.cut-recovery'] == '0'

    def test_cancel_does_nothing_when_pin_missing(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        service.cancel_pressed()

        assert len(hal.set_p_calls) == 0


class TestCutRecoveryGetStatus:
    def test_get_status_returns_current_state(self):
        hal = MockHal()
        service = CutRecoveryService(hal)

        assert service.get_cut_recovery_status() is False

        service.cut_recovery_status = True
        assert service.get_cut_recovery_status() is True


class TestCutRecoveryMoveWithStringPins:
    """Verify move logic handles string-typed HAL values correctly via float() casts."""

    def test_move_with_string_pin_values(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = '0'
        hal.pins['axis.y.eoffset'] = '0'
        hal.pins['plasmac.x-offset'] = '0'
        hal.pins['plasmac.y-offset'] = '0'
        hal.pins['plasmac.offset-scale'] = '1.0'
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = '10'
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        assert float(hal.pins['plasmac.x-offset']) == 10.0

    def test_move_with_float_pin_values(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0.0
        hal.pins['axis.y.eoffset'] = 0.0
        hal.pins['plasmac.x-offset'] = 0.0
        hal.pins['plasmac.y-offset'] = 0.0
        hal.pins['plasmac.offset-scale'] = 1.0
        hal.pins['qtpyvcp.laser.out'] = 0
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 5.25
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=0, laser_offset_y=0,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True
        # int(5.25 / 1.0) = 5 — move amount is truncated to int before applying
        assert float(hal.pins['plasmac.x-offset']) == 5.0

    def test_move_with_laser_bit_as_int(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset'] = 0
        hal.pins['axis.y.eoffset'] = 0
        hal.pins['plasmac.x-offset'] = '0'
        hal.pins['plasmac.y-offset'] = '0'
        hal.pins['plasmac.offset-scale'] = '1.0'
        hal.pins['qtpyvcp.laser.out'] = 1
        hal.pins['qtpyvcp.param-kirfwidth.out'] = 5
        service = CutRecoveryService(hal)
        service.cut_recovery_status = True
        service.o_scale = 1.0

        result = service.move(
            x_dir=1, y_dir=0, laser_offset_x=2, laser_offset_y=3,
            linear_setting='mm',
            btn_cut_recover_fwd=MockWidget(),
            btn_cut_recover_rev=MockWidget()
        )

        assert result is True

    def test_enter_recovery_with_string_pin_values(self):
        hal = MockHal()
        hal.pins['axis.x.eoffset-counts'] = '100'
        hal.pins['axis.y.eoffset-counts'] = '200'
        hal.pins['axis.z.eoffset-counts'] = '50'
        hal.pins['plasmac.offset-scale'] = '2.5'
        service = CutRecoveryService(hal)

        widget = MockWidget()
        jog_stack = MockWidget()

        service.handle_button(
            'btn_feed_hold', widget, jog_stack, cut_recovery_speed_value=50
        )

        assert service.x_orig == 100.0
        assert service.y_orig == 200.0
        assert service.z_orig == 50.0
        assert service.o_scale == 2.5

    def test_cancel_with_string_pin_value(self):
        hal = MockHal()
        hal.pins['plasmac.cut-recovery'] = '1'
        service = CutRecoveryService(hal)

        service.cancel_pressed()

        assert hal.pins['plasmac.cut-recovery'] == '0'
