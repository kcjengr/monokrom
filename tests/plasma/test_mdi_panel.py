"""Tests for mdi_panel.py — verify the MdiPanelService."""

from monokrom.plasma.mdi_panel import MdiPanelService


class MockMdiEntry:
    def __init__(self, text=''):
        self._text = text

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text


class MockParamButton:
    def __init__(self):
        self._text = ''

    def setText(self, text):
        self._text = text


class MockMainWindow:
    def __init__(self):
        self.mdiEntry = MockMdiEntry()
        self.btnGcodeP1 = MockParamButton()
        self.btnGcodeP2 = MockParamButton()
        self.btnGcodeP3 = MockParamButton()
        self.btnGcodeP4 = MockParamButton()
        self.btnGcodeP5 = MockParamButton()
        self.btnGcodeP6 = MockParamButton()
        self.btnGcodeP7 = MockParamButton()
        self.btnGcodeP8 = MockParamButton()
        self.btnGcodeP9 = MockParamButton()
        self.btnGcodeP10 = MockParamButton()


class TestMdiPanelServiceInit:
    def test_init_stores_main_window(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        assert service.main_window is mw


class TestMdiPanelAppendChar:
    def test_append_char_to_empty(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        service.append_char('G')
        assert mw.mdiEntry.text() == 'G'

    def test_append_char_to_existing_text(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('G1')
        service = MdiPanelService(mw)
        service.append_char(' ')
        assert mw.mdiEntry.text() == 'G1 '

    def test_append_multiple_chars(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        for ch in 'G0X100':
            service.append_char(ch)
        assert mw.mdiEntry.text() == 'G0X100'


class TestMdiPanelClearParams:
    def test_clear_params_clears_all_buttons(self):
        mw = MockMainWindow()
        # Set some param buttons to non-empty values
        for i in range(1, 11):
            getattr(mw, 'btnGcodeP' + str(i)).setText('X')
        service = MdiPanelService(mw)
        service.clear_params()
        for i in range(1, 11):
            assert getattr(mw, 'btnGcodeP' + str(i))._text == ''


class TestMdiPanelLookupParams:
    def test_lookup_g1_finds_params(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        result = service.lookup_params('G1')
        assert result is True
        # G1 params are X, Y, Z
        assert mw.btnGcodeP1._text == 'X'
        assert mw.btnGcodeP2._text == 'Y'
        assert mw.btnGcodeP3._text == 'Z'

    def test_lookup_g2_finds_params(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        result = service.lookup_params('G2')
        assert result is True
        # G2 params are X, Y, Z, I, J, K, R, P
        assert mw.btnGcodeP1._text == 'X'
        assert mw.btnGcodeP8._text == 'P'

    def test_lookup_m3_finds_params(self):
        mw = MockMainWindow()
        service = MdiPanelService(mw)
        result = service.lookup_params('M3')
        assert result is True
        # M3 params are S, $
        assert mw.btnGcodeP1._text == 'S'
        assert mw.btnGcodeP2._text == '$'

    def test_lookup_unknown_gcode_clears_params(self):
        mw = MockMainWindow()
        mw.btnGcodeP1.setText('X')
        service = MdiPanelService(mw)
        result = service.lookup_params('G999')
        assert result is False
        assert mw.btnGcodeP1._text == ''

    def test_lookup_null_text_clears_params(self):
        mw = MockMainWindow()
        mw.btnGcodeP1.setText('X')
        service = MdiPanelService(mw)
        result = service.lookup_params('null')
        assert result is False
        assert mw.btnGcodeP1._text == ''

    def test_lookup_empty_text_clears_params(self):
        mw = MockMainWindow()
        mw.btnGcodeP1.setText('X')
        service = MdiPanelService(mw)
        result = service.lookup_params('')
        assert result is False
        assert mw.btnGcodeP1._text == ''


class TestMdiPanelBackspace:
    def test_backspace_removes_last_char(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('G1')
        service = MdiPanelService(mw)
        service.backspace()
        assert mw.mdiEntry.text() == 'G'

    def test_backspace_empty_stays_empty(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('')
        service = MdiPanelService(mw)
        service.backspace()
        assert mw.mdiEntry.text() == ''

    def test_backspace_single_char(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('A')
        service = MdiPanelService(mw)
        service.backspace()
        assert mw.mdiEntry.text() == ''


class TestMdiPanelAddSpace:
    def test_add_space_to_text(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('G1')
        service = MdiPanelService(mw)
        service.add_space()
        assert mw.mdiEntry.text() == 'G1 '

    def test_add_space_empty_does_nothing(self):
        mw = MockMainWindow()
        mw.mdiEntry.setText('')
        service = MdiPanelService(mw)
        service.add_space()
        assert mw.mdiEntry.text() == ''
