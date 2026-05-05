"""Unit tests for quickshapes.py helper and utility functions."""

from math import cos, sin, atan, pi

import pytest

from monokrom.plasma.quickshapes import (
    fix,
    start_cut,
    stop_cut,
    preamble,
    postamble,
    magic_material,
    refl,
    midpoint,
    calculate_slope,
)


class TestFix:
    """Tests for the fix() rounding function."""

    def test_fix_rounds_to_5_decimal_places(self):
        assert fix(1.23456789) == 1.23457

    def test_fix_preserves_exact_values(self):
        assert fix(1.5) == 1.5

    def test_fix_handles_zero(self):
        assert fix(0.0) == 0.0

    def test_fix_handles_negative(self):
        assert fix(-3.14159265) == -3.14159

    def test_fix_handles_integer(self):
        assert fix(5) == 5


class TestStartCut:
    """Tests for start_cut() function."""

    def test_start_cut_appends_m3_command(self, lines_list):
        start_cut(lines_list)
        assert any("M3" in line and "plasma start" in line for line in lines_list)

    def test_start_cut_single_line(self, lines_list):
        start_cut(lines_list)
        assert len(lines_list) == 1


class TestStopCut:
    """Tests for stop_cut() function."""

    def test_stop_cut_appends_m5_command(self, lines_list):
        stop_cut(lines_list)
        assert any("M5" in line and "plasma end" in line for line in lines_list)

    def test_stop_cut_single_line(self, lines_list):
        stop_cut(lines_list)
        assert len(lines_list) == 1


class TestPreamble:
    """Tests for preamble() function."""

    def test_preamble_metric_default(self, lines_list):
        preamble(lines_list)
        assert any("G21" in line for line in lines_list)
        assert any("units: metric" in line for line in lines_list)

    def test_preamble_inch_mode(self, lines_list):
        preamble(lines_list, metric=False)
        assert any("G20" in line for line in lines_list)
        assert any("units: inch" in line for line in lines_list)

    def test_preamble_contains_g40(self, lines_list):
        preamble(lines_list)
        assert any("G40" in line for line in lines_list)

    def test_preamble_contains_g90(self, lines_list):
        preamble(lines_list)
        assert any("G90" in line for line in lines_list)

    def test_preamble_contains_thc_enable(self, lines_list):
        preamble(lines_list)
        assert any("M65 P2" in line for line in lines_list)

    def test_preamble_contains_torch_enable(self, lines_list):
        preamble(lines_list)
        assert any("M65 P3" in line for line in lines_list)

    def test_preamble_has_expected_line_count(self, lines_list):
        preamble(lines_list)
        # 2 comment lines + 8 G-code lines = 10 total
        assert len(lines_list) == 10


class TestPostamble:
    """Tests for postamble() function."""

    def test_postamble_contains_g40(self, lines_list):
        postamble(lines_list)
        assert any("G40" in line for line in lines_list)

    def test_postamble_contains_m30(self, lines_list):
        postamble(lines_list)
        assert any("M30" in line for line in lines_list)

    def test_postamble_contains_m159_reset(self, lines_list):
        postamble(lines_list)
        assert any("M159" in line for line in lines_list)

    def test_postamble_has_expected_line_count(self, lines_list):
        postamble(lines_list)
        # 2 comment + 8 G-code = 10 total
        assert len(lines_list) == 10


class TestMagicMaterial:
    """Tests for magic_material() function."""

    def test_magic_material_appends_comment(self, lines_list):
        magic_material(kw=0.1, ph=1.0, pd=2.0, ch=0.5, fr=100, mt=1, lines=lines_list)
        assert any("begin material setup" in line for line in lines_list)

    def test_magic_material_appends_f_command(self, lines_list):
        magic_material(kw=0.1, ph=1.0, pd=2.0, ch=0.5, fr=100, mt=1, lines=lines_list)
        assert any("F#" in line for line in lines_list)

    def test_magic_material_returns_lines(self, lines_list):
        result = magic_material(kw=0.1, ph=1.0, pd=2.0, ch=0.5, fr=100, mt=1, lines=lines_list)
        assert result is lines_list

    def test_magic_material_line_count(self, lines_list):
        magic_material(kw=0.1, ph=1.0, pd=2.0, ch=0.5, fr=100, mt=1, lines=lines_list)
        assert len(lines_list) == 4


class TestRef:
    """Tests for refl() reflection function."""

    def test_reflection_across_x_axis(self):
        # Reflect (0, 5) across line from (0,0) to (1,0) [the x-axis]
        x, y = refl(0, 0, 1, 0, 0, 5)
        assert x == 0
        assert y == -5

    def test_reflection_across_y_axis(self):
        # Reflect (5, 0) across line from (0,0) to (0,1) [the y-axis]
        x, y = refl(0, 0, 0, 1, 5, 0)
        assert x == -5
        assert y == 0

    def test_reflection_on_diagonal(self):
        # Reflect (2, 0) across line y=x from (0,0) to (1,1)
        x, y = refl(0, 0, 1, 1, 2, 0)
        assert x == 0
        assert y == 2

    def test_reflection_preserves_point_on_line(self):
        # Point on the reflection line should stay unchanged
        x, y = refl(0, 0, 4, 0, 2, 0)
        assert x == 2
        assert y == 0

    def test_reflection_negative_coordinates(self):
        x, y = refl(0, 0, 1, 1, -3, -3)
        assert x == -3
        assert y == -3


class TestMidpoint:
    """Tests for midpoint() function."""

    def test_midpoint_simple(self):
        result = midpoint((0, 0), (10, 0))
        assert result == (5.0, 0.0)

    def test_midpoint_diagonal(self):
        result = midpoint((0, 0), (6, 8))
        assert result == (3.0, 4.0)

    def test_midpoint_negative(self):
        result = midpoint((-4, -2), (2, 6))
        assert result == (-1.0, 2.0)

    def test_midpoint_same_points(self):
        result = midpoint((5, 5), (5, 5))
        assert result == (5.0, 5.0)


class TestCalculateSlope:
    """Tests for calculate_slope() function."""

    def test_slope_horizontal(self):
        assert calculate_slope(0, 0, 10, 0) == 0.0

    def test_slope_vertical_returns_none(self):
        result = calculate_slope(5, 0, 5, 10)
        assert result is None

    def test_slope_positive(self):
        result = calculate_slope(0, 0, 2, 4)
        assert result == 2.0

    def test_slope_negative(self):
        result = calculate_slope(0, 4, 2, 0)
        assert result == -2.0

    def test_slope_diagonal_45_degrees(self):
        result = calculate_slope(0, 0, 3, 3)
        assert result == 1.0
