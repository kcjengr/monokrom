"""Tests for hal_bridge.py — verify the bridge delegates correctly."""

from monokrom.plasma.hal_bridge import HALBridge


class TestHALBridgeInit:
    def test_init_with_explicit_deps(self):
        mock_cnchal = MockCnchal()
        mock_mdi_fn = lambda x: None
        mock_cmd = MockCmd()
        bridge = HALBridge(cnchal=mock_cnchal, issue_mdi_fn=mock_mdi_fn, cmd=mock_cmd)
        assert bridge._cnchal is mock_cnchal
        assert bridge._issue_mdi is mock_mdi_fn
        assert bridge._cmd is mock_cmd

    def test_init_without_deps_uses_lazy_defaults(self):
        # Should not raise — lazy defaults defer imports until first use
        bridge = HALBridge()
        assert bridge._cnchal is not None
        assert bridge._issue_mdi is not None
        assert bridge._cmd is not None


class MockCnchal:
    """A minimal mock that records set_p calls and returns stored values."""

    def __init__(self):
        self.pins = {}
        self.set_p_calls = []

    def get_value(self, pin_name):
        return self.pins.get(pin_name)

    def set_p(self, pin_name, value):
        self.pins[pin_name] = value
        self.set_p_calls.append((pin_name, value))


class MockCmd:
    def __init__(self):
        self.wait_complete_calls = 0

    def wait_complete(self):
        self.wait_complete_calls += 1


class TestHALBridgeGetValue:
    def test_get_value_delegates_to_cnchal(self):
        cnchal = MockCnchal()
        cnchal.pins['axis.x.eoffset'] = 42
        bridge = HALBridge(cnchal=cnchal)
        assert bridge.get_value('axis.x.eoffset') == 42

    def test_get_value_returns_none_for_unknown_pin(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        result = bridge.get_value('nonexistent.pin')
        assert result is None


class TestHALBridgeSetP:
    def test_set_p_delegates_to_cnchal(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_p('plasmac.x-offset', '100')
        assert cnchal.pins['plasmac.x-offset'] == '100'
        assert cnchal.set_p_calls == [('plasmac.x-offset', '100')]


class TestHALBridgeSendMdi:
    def test_send_mdi_delegates_to_issue_mdi(self):
        received = []

        def capture(gcode):
            received.append(gcode)

        bridge = HALBridge(issue_mdi_fn=capture)
        bridge.send_mdi('G0 X10 Y20')
        assert received == ['G0 X10 Y20']


class TestHALBridgeWaitComplete:
    def test_wait_complete_calls_cmd(self):
        cmd = MockCmd()
        bridge = HALBridge(cmd=cmd)
        bridge.wait_complete()
        assert cmd.wait_complete_calls == 1

    def test_wait_complete_called_multiple_times(self):
        cmd = MockCmd()
        bridge = HALBridge(cmd=cmd)
        bridge.wait_complete()
        bridge.wait_complete()
        bridge.wait_complete()
        assert cmd.wait_complete_calls == 3


class TestHALBridgeSetOffset:
    def test_set_offset_calls_set_p_with_correct_pin(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_offset('x', 123)
        assert cnchal.pins['axis.x.eoffset'] == '123'

    def test_set_offset_formats_as_string(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_offset('y', 45.678)
        assert cnchal.pins['axis.y.eoffset'] == '45.678'


class TestHALBridgeGetEoffset:
    def test_get_eoffset_calls_get_value_with_correct_pin(self):
        cnchal = MockCnchal()
        cnchal.pins['axis.z.eoffset'] = 99
        bridge = HALBridge(cnchal=cnchal)
        result = bridge.get_eoffset('z')
        assert result == 99


class TestHALBridgeSetOffsets:
    def test_set_offsets_resets_both(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_offsets(0, 0)
        assert cnchal.pins['plasmac.x-offset'] == '0'
        assert cnchal.pins['plasmac.y-offset'] == '0'

    def test_set_offsets_custom_values(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_offsets(50, -30)
        assert cnchal.pins['plasmac.x-offset'] == '50'
        assert cnchal.pins['plasmac.y-offset'] == '-30'

    def test_set_offsets_formats_integers(self):
        cnchal = MockCnchal()
        bridge = HALBridge(cnchal=cnchal)
        bridge.set_offsets(100, 200)
        assert cnchal.pins['plasmac.x-offset'] == '100'
        assert cnchal.pins['plasmac.y-offset'] == '200'
