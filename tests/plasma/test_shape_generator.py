"""Unit tests for ShapeGeneratorService."""

import pytest
from unittest.mock import MagicMock, patch


class MockValueWidget:
    """Mock a Qt widget that has a .value() method returning an int/float."""

    def __init__(self, val):
        self._val = val

    def value(self):
        return self._val


class MockCheckWidget:
    """Mock a Qt checkbox widget with .isChecked()."""

    def __init__(self, checked=False):
        self.checked = checked

    def isChecked(self):
        return self.checked


class MockComboWidget:
    """Mock a Qt combo box with .currentText()."""

    def __init__(self, text="Round"):
        self._text = text

    def currentText(self):
        return self._text


def _make_mock_mainwindow(overrides=None):
    """Build a mock MainWindow-like object with all required widgets."""
    mw = MagicMock()
    defaults = {
        "param_kirfwidth": MockValueWidget(2),
        "quickshape_internal_kerf": MockValueWidget(0),
        "chkb_hole_detect_enable": MockCheckWidget(False),
        "param_pierceheight": MockValueWidget(5),
        "param_piercedelay": MockValueWidget(10),
        "param_cutheight": MockValueWidget(20),
        "param_cutfeedrate": MockValueWidget(100),
        "param_cutamps": MockValueWidget(80),
        "param_cutvolts": MockValueWidget(40),
        "param_pauseatend": MockValueWidget(0),
        # Shape 0 - circle
        "id0_dbl_diam": MockValueWidget(100),
        # Shape 1 - rectangle
        "id1_dbl_width": MockValueWidget(100),
        "id1_dbl_height": MockValueWidget(50),
        # Shape 2 - donut
        "id2_dbl_inner_diam": MockValueWidget(60),
        "id2_dbl_outer_diam": MockValueWidget(100),
        # Shape 3 - convex_rectangle
        "id3_dbl_width": MockValueWidget(100),
        "id3_dbl_height": MockValueWidget(50),
        # Shape 4 - lifting_lug
        "id4_dbl_w1": MockValueWidget(80),
        "id4_dbl_d1": MockValueWidget(20),
        "id4_dbl_h1": MockValueWidget(60),
        "id4_dbl_h2": MockValueWidget(10),
        "id4_dbl_d2": MockValueWidget(12),
        "id4_dbl_rb": MockValueWidget(50),
        "id4_chk_pair": MockCheckWidget(False),
        "id4_dbl_separation": MockValueWidget(20),
        # Shape 5 - u_lug
        "id5_dbl_w1": MockValueWidget(40),
        "id5_dbl_w2": MockValueWidget(20),
        "id5_dbl_h": MockValueWidget(60),
        # Shape 6 - pipe_flange
        "id6_dbl_od": MockValueWidget(200),
        "id6_dbl_pcd": MockValueWidget(150),
        "id6_int_holes": MockValueWidget(6),
        "id6_dbl_hd": MockValueWidget(10),
        "id6_combo_hole": MockComboWidget("Round"),
        "id6_dbl_id": MockValueWidget(50),
        # Shape 7 - pipe_saddle
        "id7_dbl_w": MockValueWidget(100),
        "id7_dbl_h": MockValueWidget(80),
        "id7_dbl_pd": MockValueWidget(50),
        "id7_dbl_o": MockValueWidget(20),
        # Shape 8 - exhaust_flange
        "id8_dbl_id": MockValueWidget(100),
        "id8_dbl_wt": MockValueWidget(20),
        "id8_dbl_pcd": MockValueWidget(80),
        "id8_dbl_bd": MockValueWidget(10),
        "id8_dbl_sw": MockValueWidget(15),
        "id8_int_nb": MockValueWidget(3),
        # Shape 9 - n_square
        "id9_dbl_w": MockValueWidget(100),
        "id9_dbl_h": MockValueWidget(80),
        "id9_int_hhn": MockValueWidget(2),
        "id9_dbl_hs": MockValueWidget(30),
        "id9_int_vhn": MockValueWidget(2),
        "id9_dbl_vs": MockValueWidget(30),
        "id9_dbl_hd": MockValueWidget(8),
        "id9_dbl_fr": MockValueWidget(0),
        "id9_combo_ch": MockComboWidget("None"),
        # Shape 10 - l_gusset
        "id10_dbl_w": MockValueWidget(100),
        "id10_dbl_h": MockValueWidget(80),
        "id10_dbl_w1": MockValueWidget(30),
        "id10_dbl_h1": MockValueWidget(20),
        # Shape 11 - angle_gusset
        "id11_dbl_w": MockValueWidget(100),
        "id11_dbl_h": MockValueWidget(80),
        "id11_dbl_c1": MockValueWidget(20),
        "id11_dbl_c2": MockValueWidget(30),
        "id11_dbl_a": MockValueWidget(45),
        "id11_chk_pair": MockCheckWidget(False),
        "id11_dbl_xoffset": MockValueWidget(0),
        "id11_dbl_yoffset": MockValueWidget(0),
        # Shape 12 - truss_support
        "id12_dbl_w": MockValueWidget(100),
        "id12_dbl_h": MockValueWidget(80),
        "id12_dbl_w1": MockValueWidget(30),
        "id12_dbl_h1": MockValueWidget(20),
        # Shape 13 - web_stiffener
        "id13_dbl_w": MockValueWidget(100),
        "id13_dbl_h": MockValueWidget(80),
        "id13_dbl_c": MockValueWidget(30),
    }

    for name, widget in defaults.items():
        setattr(mw, name, widget)

    if overrides:
        for name, widget in overrides.items():
            setattr(mw, name, widget)

    return mw


class TestShapeGeneratorServiceDispatch:
    """Tests for ShapeGeneratorService.generate() dispatch."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_0(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(0)
        assert error is None
        assert len(lines) > 0

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_1(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(1)
        assert error is None
        assert len(lines) > 0

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_2(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(2)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_3(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(3)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_4(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(4)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_5(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(5)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_6(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(6)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_7(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(7)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_8(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(8)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_9(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(9)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_10(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(10)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_11(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(11)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_12(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(12)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_shape_index_13(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(13)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_invalid_shape_index(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(99)
        assert error is not None
        assert "Unknown shape index" in error
        assert lines == []

    @patch("qtpyvcp.utilities.info.Info")
    def test_negative_shape_index(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(-1)
        assert error is not None


class TestShapeGeneratorServiceLiftingLug:
    """Tests for lifting_lug via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_rb_too_small_returns_error(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id4_dbl_rb": MockValueWidget(10)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(4)
        assert error is not None
        assert "rb is too small" in error

    @patch("qtpyvcp.utilities.info.Info")
    def test_valid_rb_returns_no_error(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(4)
        assert error is None


class TestShapeGeneratorServiceCommon:
    """Tests for shared behavior across all shapes."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_all_shapes_return_tuple(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        for i in range(14):
            result = service.generate(i)
            assert isinstance(result, tuple), f"Shape {i} did not return a tuple"
            assert len(result) == 2, f"Shape {i} tuple has wrong length"

    @patch("qtpyvcp.utilities.info.Info")
    def test_success_shapes_have_lines(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        for i in range(14):
            lines, error = service.generate(i)
            if error is None:
                assert len(lines) > 0, f"Shape {i} returned empty lines list"

    def test_service_stores_main_window(self):
        mw = _make_mock_mainwindow()
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        service = ShapeGeneratorService(mw)
        assert service.main_window is mw


class TestShapeGeneratorServiceCircle:
    """Tests for circle via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_circle_uses_diameter(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id0_dbl_diam": MockValueWidget(200)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(0)
        assert error is None
        assert len(lines) > 0

    @patch("qtpyvcp.utilities.info.Info")
    def test_circle_with_small_diameter(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id0_dbl_diam": MockValueWidget(10)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(0)
        assert error is None


class TestShapeGeneratorServiceRectangle:
    """Tests for rectangle via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_rectangle_dimensions(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id1_dbl_width": MockValueWidget(150), "id1_dbl_height": MockValueWidget(75)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(1)
        assert error is None


class TestShapeGeneratorServiceDonut:
    """Tests for donut via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_donut_outer_larger_than_inner(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(2)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_donut_with_smart_hole(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"chkb_hole_detect_enable": MockCheckWidget(True)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(2)
        assert error is None


class TestShapeGeneratorServicePipeFlange:
    """Tests for pipe_flange via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_pipe_flange_round_holes(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        mw = _make_mock_mainwindow()
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(6)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_pipe_flange_square_holes(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id6_combo_hole": MockComboWidget("Square")}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(6)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_pipe_flange_different_hole_count(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id6_int_holes": MockValueWidget(8)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(6)
        assert error is None


class TestShapeGeneratorServiceN_Square:
    """Tests for n_square via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_n_square_round_center_hole(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id9_combo_ch": MockComboWidget("Round")}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(9)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_n_square_rect_center_hole(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id9_combo_ch": MockComboWidget("Rectangle")}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(9)
        assert error is None

    @patch("qtpyvcp.utilities.info.Info")
    def test_n_square_with_fillet(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id9_dbl_fr": MockValueWidget(5)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(9)
        assert error is None


class TestShapeGeneratorServiceAngleGusset:
    """Tests for angle_gusset via ShapeGeneratorService."""

    @patch("qtpyvcp.utilities.info.Info")
    def test_angle_gusset_pair(self, mock_info):
        mock_info.return_value.getIsMachineMetric.return_value = True
        from monokrom.plasma.shape_generator import ShapeGeneratorService
        overrides = {"id11_chk_pair": MockCheckWidget(True), "id11_dbl_xoffset": MockValueWidget(50)}
        mw = _make_mock_mainwindow(overrides)
        service = ShapeGeneratorService(mw)
        lines, error = service.generate(11)
        assert error is None
