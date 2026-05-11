"""Tests for sheet_alignment.py — verify the SheetAlignmentService."""

from monokrom.plasma.sheet_alignment import SheetAlignmentService


class MockHal:
    def __init__(self):
        self.mdi_commands = []
        self.wait_complete_calls = 0

    def send_mdi(self, gcode):
        self.mdi_commands.append(gcode)

    def wait_complete(self):
        self.wait_complete_calls += 1


class MockPos:
    """Mock position plugin providing absolute axis values."""
    def __init__(self, x=0.0, y=0.0):
        self._x = x
        self._y = y

    def Absolute(self, axis):
        if axis == 0:
            return self._x
        return self._y


class TestSheetAlignmentInit:
    def test_init_stores_hal(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        assert service.hal is hal

    def test_init_default_state(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        assert service.sheet_align_p1 is None
        assert service.sheet_align_p2 is None


class TestSheetAlignmentHandleToggle:
    def test_laser_on_enables_pt1(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_laser', checked=True)

        assert result == {'btn_sheet_align_pt1': {'enabled': True}}

    def test_laser_off_resets_all_state(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_laser', checked=False)

        assert 'btn_sheet_align_pt1' in result
        assert result['btn_sheet_align_pt1']['enabled'] is False
        assert result['btn_sheet_align_pt1']['checked'] is False
        assert 'btn_sheet_align_pt2' in result
        assert result['btn_sheet_align_pt2']['enabled'] is False
        assert result['btn_sheet_doalign']['enabled'] is False

    def test_pt1_on_enables_pt2(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_sheet_align_pt1', checked=True)

        assert result == {'btn_sheet_align_pt2': {'enabled': True}}

    def test_pt1_off_resets_downstream(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_sheet_align_pt1', checked=False)

        assert result['btn_sheet_align_pt2']['enabled'] is False
        assert result['btn_sheet_doalign']['enabled'] is False

    def test_pt2_on_enables_doalign(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_sheet_align_pt2', checked=True)

        assert result == {'btn_sheet_doalign': {'enabled': True}}

    def test_pt2_off_disables_doalign(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_sheet_align_pt2', checked=False)

        assert result['btn_sheet_doalign']['enabled'] is False

    def test_doalign_returns_reset_state(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.handle_toggle('btn_sheet_doalign', checked=False)

        assert result['btn_sheet_align_pt1']['checked'] is False
        assert result['btn_sheet_align_pt1']['enabled'] is False
        assert result['btn_sheet_align_pt2']['checked'] is False
        assert result['btn_sheet_align_pt2']['enabled'] is False
        assert result['btn_laser']['checked'] is False
        assert result['btn_sheet_doalign']['enabled'] is False


class TestSheetAlignmentStatusText:
    def test_status_text_both_none(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        text = service.get_status_text()

        assert text == "REF1:...\nREF2:..."

    def test_status_text_p1_only(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [10.5, 20.75]

        text = service.get_status_text()

        assert 'REF1:' in text
        assert '10.5000' in text
        assert '20.7500' in text
        assert 'REF2:...' in text

    def test_status_text_p2_only(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p2 = [30.1234, 40.5678]

        text = service.get_status_text()

        assert 'REF1:...' in text
        assert 'REF2:' in text
        assert '30.1234' in text
        assert '40.5678' in text

    def test_status_text_both_set(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [1.0, 2.0]
        service.sheet_align_p2 = [3.0, 4.0]

        text = service.get_status_text()

        assert 'REF1:' in text
        assert 'REF2:' in text
        assert '1.0000' in text
        assert '3.0000' in text


class TestSheetAlignmentGetCurrentPoints:
    def test_returns_none_when_no_points(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        p1, p2 = service.get_current_points()

        assert p1 is None
        assert p2 is None

    def test_returns_points_when_set(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [1.0, 2.0]
        service.sheet_align_p2 = [3.0, 4.0]

        p1, p2 = service.get_current_points()

        assert p1 == [1.0, 2.0]
        assert p2 == [3.0, 4.0]


class TestSheetAlignmentSetPoint:
    def test_set_point_1_records_position(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        pos = MockPos(x=100.5, y=200.75)

        service.set_point_1(pos)

        assert service.sheet_align_p1 == [100.5, 200.75]
        assert hal.mdi_commands == ['G10 L2 P0 R0']

    def test_set_point_2_records_position(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        pos = MockPos(x=300.25, y=400.5)

        service.set_point_2(pos)

        assert service.sheet_align_p2 == [300.25, 400.5]
        assert hal.mdi_commands == ['G10 L2 P0 R0']


class TestSheetAlignmentAlign:
    def test_align_fails_when_points_not_set(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)

        result = service.align(0, 0)

        assert result is False
        assert len(hal.mdi_commands) == 0

    def test_align_fails_when_only_p1_set(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [1.0, 2.0]

        result = service.align(0, 0)

        assert result is False

    def test_align_sends_mdi_commands(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [0.0, 0.0]
        service.sheet_align_p2 = [100.0, 0.0]

        service.align(laser_offset_x_value=5.0, laser_offset_y_value=3.0)

        assert 'G10 L2 P0 R0' in hal.mdi_commands
        assert 'G10 L2 P0 X0 Y0' in hal.mdi_commands
        assert 'G10 L20 P0 X5.0 Y3.0' in hal.mdi_commands
        # index 4 is G10 L2 P0 R<angle>, index 5 is G0 X0 Y0
        assert any('G10 L2 P0 R' in cmd for cmd in hal.mdi_commands)
        assert 'G0 X0 Y0' in hal.mdi_commands

    def test_align_resets_state_on_success(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [0.0, 0.0]
        service.sheet_align_p2 = [100.0, 0.0]

        service.align(0, 0)

        assert service.sheet_align_p1 is None
        assert service.sheet_align_p2 is None

    def test_align_returns_true_on_success(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [0.0, 0.0]
        service.sheet_align_p2 = [100.0, 0.0]

        result = service.align(0, 0)

        assert result is True


class TestSheetAlignmentCalculateAngle:
    def test_angle_both_differences_zero(self):
        angle = SheetAlignmentService._calculate_angle(0, 0)
        assert angle == 0

    def test_angle_along_x_positive(self):
        angle = SheetAlignmentService._calculate_angle(100, 0)
        assert angle == 180

    def test_angle_along_x_negative(self):
        angle = SheetAlignmentService._calculate_angle(-100, 0)
        assert angle == 0

    def test_angle_along_y_positive(self):
        angle = SheetAlignmentService._calculate_angle(0, 50)
        assert angle == 180

    def test_angle_along_y_negative(self):
        angle = SheetAlignmentService._calculate_angle(0, -50)
        assert angle == 0

    def test_angle_first_quadrant_x_positive_y_positive(self):
        # x=50, y=50 => atan(1)=45, +180=225, abs(x)<abs(y)? No (equal), no -90
        angle = SheetAlignmentService._calculate_angle(50, 50)
        assert angle == 225

    def test_angle_first_quadrant_x_positive_y_negative(self):
        # x=100, y=-10 => atan(-0.1)=-5.71, +180=174.29, abs(100)<abs(-10)? No
        angle = SheetAlignmentService._calculate_angle(100, -10)
        assert abs(angle - 174.28940686250036) < 0.001

    def test_angle_diagonal_45_degrees(self):
        # x=100, y=100 => atan(1)=45, +180=225, abs(x)<abs(y)? No (equal), no -90
        angle = SheetAlignmentService._calculate_angle(100, 100)
        assert angle == 225

    def test_angle_diagonal_x_less_than_y(self):
        # x=50, y=100 => atan(2)=63.43..., +180=243.43..., abs(50)<abs(100) so -90 = 153.43...
        angle = SheetAlignmentService._calculate_angle(50, 100)
        assert abs(angle - 153.43494882292201) < 0.001


class TestSheetAlignmentReset:
    def test_reset_clears_points(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [1.0, 2.0]
        service.sheet_align_p2 = [3.0, 4.0]

        service.reset()

        assert service.sheet_align_p1 is None
        assert service.sheet_align_p2 is None

    def test_reset_does_not_send_hal_commands(self):
        hal = MockHal()
        service = SheetAlignmentService(hal)
        service.sheet_align_p1 = [1.0, 2.0]

        service.reset()

        assert len(hal.mdi_commands) == 0
        assert hal.wait_complete_calls == 0
