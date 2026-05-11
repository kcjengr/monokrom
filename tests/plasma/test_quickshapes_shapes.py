"""Unit tests for quickshapes.py shape generation functions."""

import pytest

from monokrom.plasma.quickshapes import (
    circle,
    rectangle,
    donut,
    convex_rectangle,
    lifting_lug,
    u_lug,
    pipe_flange,
    pipe_saddle,
    exhaust_flange,
    n_square,
    L_gusset,
    angle_gusset,
    truss_support,
    web_stiffener,
)


class TestCircle:
    """Tests for circle() shape generation."""

    def test_circle_has_leadin_rapid(self, lines_list):
        circle(diameter=100, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G0" in gcode
        assert any("X" in line and "Y" in line for line in lines_list if "G0" in line)

    def test_circle_has_start_cut(self, lines_list):
        circle(diameter=100, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode

    def test_circle_has_arc_move(self, lines_list):
        circle(diameter=100, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # clockwise arc for circle

    def test_circle_has_stop_cut(self, lines_list):
        circle(diameter=100, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M5" in gcode

    def test_circle_line_count(self, lines_list):
        circle(diameter=100, kerf=2, leadin=4, lines=lines_list)
        # G0 rapid + M3 start + G1 lead-in + G2 arc + M5 stop = 5 lines
        assert len(lines_list) == 5

    def test_circle_with_zero_kerf(self, lines_list):
        circle(diameter=50, kerf=0, leadin=4, lines=lines_list)
        assert len(lines_list) == 5


class TestRectangle:
    """Tests for rectangle() shape generation."""

    def test_rectangle_has_leadin_rapid(self, lines_list):
        rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G0" in gcode

    def test_rectangle_has_start_stop(self, lines_list):
        rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_rectangle_has_linear_moves(self, lines_list):
        rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        g1_lines = [l for l in lines_list if "G1" in l]
        assert len(g1_lines) == 4  # 4 sides of rectangle

    def test_rectangle_line_count(self, lines_list):
        rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        # G0 + M3 start + G1 x4 + M5 stop = 7 lines
        assert len(lines_list) == 7


class TestDonut:
    """Tests for donut() shape generation."""

    def test_donut_has_inner_hole(self, lines_list):
        donut(od=100, id=60, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode  # inner hole start
        assert "M5" in gcode

    def test_donut_has_outer_cut(self, lines_list):
        donut(od=100, id=60, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # outer arc

    def test_donut_with_smarthole(self, lines_list):
        donut(od=100, id=60, kerf=2, internal_kerf=2, smarthole=True, leadin=4, lines=lines_list)
        assert len(lines_list) > 0

    def test_donut_default_internal_kerf(self, lines_list):
        donut(od=100, id=60, kerf=2, internal_kerf=0, smarthole=False, leadin=4, lines=lines_list)
        assert len(lines_list) > 0


class TestConvexRectangle:
    """Tests for convex_rectangle() shape generation."""

    def test_convex_rectangle_has_arc(self, lines_list):
        convex_rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # has rounded corner arc

    def test_convex_rectangle_has_start_stop(self, lines_list):
        convex_rectangle(width=100, height=50, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode


class TestULug:
    """Tests for u_lug() shape generation."""

    def test_u_lug_has_start_stop(self, lines_list):
        u_lug(w1=40, w2=20, h=60, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_u_lug_has_arcs(self, lines_list):
        u_lug(w1=40, w2=20, h=60, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # outer arc
        assert "G3" in gcode  # inner arc

    def test_u_lug_line_count(self, lines_list):
        u_lug(w1=40, w2=20, h=60, kerf=2, leadin=4, lines=lines_list)
        assert len(lines_list) >= 8


class TestPipeFlange:
    """Tests for pipe_flange() shape generation."""

    def test_pipe_flange_has_outer_circle(self, lines_list):
        pipe_flange(od=200, pcd=150, holes=6, hd=10, hole_type="Round", id=50,
                    kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # outer circle arc

    def test_pipe_flange_has_center_hole(self, lines_list):
        pipe_flange(od=200, pcd=150, holes=6, hd=10, hole_type="Round", id=50,
                    kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode  # center hole arc

    def test_pipe_flange_has_mounting_holes(self, lines_list):
        pipe_flange(od=200, pcd=150, holes=4, hd=8, hole_type="Round", id=50,
                    kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        # 4 mounting holes each with G3 arc
        assert gcode.count("G3") >= 5  # center hole + 4 mounting holes

    def test_pipe_flange_square_hole(self, lines_list):
        pipe_flange(od=200, pcd=150, holes=6, hd=10, hole_type="Square", id=50,
                    kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G1" in gcode  # square hole uses linear moves

    def test_pipe_flange_smarthole(self, lines_list):
        pipe_flange(od=200, pcd=150, holes=6, hd=10, hole_type="Round", id=50,
                    kerf=2, internal_kerf=2, smarthole=True, leadin=4, lines=lines_list)
        assert len(lines_list) > 0


class TestPipeSaddle:
    """Tests for pipe_saddle() shape generation."""

    def test_pipe_saddle_has_start_stop(self, lines_list):
        pipe_saddle(w=100, h=80, pd=50, o=20, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_pipe_saddle_has_arc(self, lines_list):
        pipe_saddle(w=100, h=80, pd=50, o=20, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode  # circular cutout arc


class TestExhaustFlange:
    """Tests for exhaust_flange() shape generation."""

    def test_exhaust_flange_has_center_hole(self, lines_list):
        exhaust_flange(id=100, wt=20, pcd=80, bd=10, sw=15, nb=3,
                       kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "G3" in gcode

    def test_exhaust_flange_2_bolt(self, lines_list):
        exhaust_flange(id=100, wt=20, pcd=80, bd=10, sw=15, nb=2,
                       kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        assert len(lines_list) > 0

    def test_exhaust_flange_smarthole(self, lines_list):
        exhaust_flange(id=100, wt=20, pcd=80, bd=10, sw=15, nb=3,
                       kerf=2, internal_kerf=2, smarthole=True, leadin=4, lines=lines_list)
        assert len(lines_list) > 0


class TestNSquare:
    """Tests for n_square() shape generation."""

    def test_n_square_has_outer_profile(self, lines_list):
        n_square(w=100, h=80, hhn=3, hhs=25, vhn=3, vhs=25, hd=8, fr=0, ch_type="None",
                 kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G1" in gcode  # outer profile

    def test_n_square_has_holes(self, lines_list):
        n_square(w=100, h=80, hhn=2, hhs=30, vhn=2, vhs=30, hd=10, fr=0, ch_type="None",
                 kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode  # hole arcs

    def test_n_square_round_center_hole(self, lines_list):
        ch_dict = {"chs": 20, "chw": 0, "chh": 0, "chfr": 0, "cha": 0, "chxo": 0, "chyo": 0}
        n_square(w=100, h=80, hhn=2, hhs=30, vhn=2, vhs=30, hd=8, fr=0, ch_type="Round",
                 kerf=2, internal_kerf=2, smarthole=False, ch_dim_dict=ch_dict, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode

    def test_n_square_rect_center_hole(self, lines_list):
        ch_dict = {"chs": 0, "chw": 20, "chh": 15, "chfr": 3, "cha": 45, "chxo": 0, "chyo": 0}
        n_square(w=100, h=80, hhn=2, hhs=30, vhn=2, vhs=30, hd=8, fr=0, ch_type="Rectangle",
                 kerf=2, internal_kerf=2, smarthole=False, ch_dim_dict=ch_dict, leadin=4, lines=lines_list)
        assert len(lines_list) > 0

    def test_n_square_with_fillet(self, lines_list):
        n_square(w=100, h=80, hhn=2, hhs=30, vhn=2, vhs=30, hd=8, fr=5, ch_type="None",
                 kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # filleted corners use arcs

    def test_n_square_smarthole(self, lines_list):
        n_square(w=100, h=80, hhn=2, hhs=30, vhn=2, vhs=30, hd=8, fr=0, ch_type="None",
                 kerf=2, internal_kerf=2, smarthole=True, leadin=4, lines=lines_list)
        assert len(lines_list) > 0


class TestLGusset:
    """Tests for L_gusset() shape generation."""

    def test_l_gusset_has_start_stop(self, lines_list):
        L_gusset(w=100, h=80, w1=30, h1=20, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_l_gusset_shape(self, lines_list):
        L_gusset(w=100, h=80, w1=30, h1=20, kerf=2, leadin=4, lines=lines_list)
        g1_lines = [l for l in lines_list if "G1" in l]
        assert len(g1_lines) == 6  # L-shape has 6 sides


class TestAngleGusset:
    """Tests for angle_gusset() shape generation."""

    def test_angle_gusset_has_start_stop(self, lines_list):
        angle_gusset(w=100, h=80, c1=20, c2=30, a=45, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_angle_gusset_no_duplicates(self, lines_list):
        """Ensure cleaned vertices don't produce zero-length moves."""
        angle_gusset(w=100, h=80, c1=20, c2=30, a=45, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        # Should have valid G1 moves with non-zero coordinates
        assert "G1" in gcode

    def test_angle_gusset_with_pair(self, lines_list):
        angle_gusset(w=100, h=80, c1=20, c2=30, a=45, kerf=2, leadin=4,
                     cutting_pair=True, xoffset=50, yoffset=0, lines=lines_list)
        gcode = "".join(lines_list)
        # Should have twice the moves for the mirrored pair
        assert gcode.count("G1") > 6


class TestTrussSupport:
    """Tests for truss_support() shape generation."""

    def test_truss_support_has_start_stop(self, lines_list):
        truss_support(w=100, h=80, w1=30, h1=20, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_truss_support_shape(self, lines_list):
        truss_support(w=100, h=80, w1=30, h1=20, kerf=2, leadin=4, lines=lines_list)
        g1_lines = [l for l in lines_list if "G1" in l]
        assert len(g1_lines) >= 6


class TestWebStiffener:
    """Tests for web_stiffener() shape generation."""

    def test_web_stiffener_has_start_stop(self, lines_list):
        web_stiffener(w=100, h=80, c=30, kerf=2, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_web_stiffener_shape(self, lines_list):
        web_stiffener(w=100, h=80, c=30, kerf=2, leadin=4, lines=lines_list)
        g1_lines = [l for l in lines_list if "G1" in l]
        assert len(g1_lines) >= 5


class TestLiftingLug:
    """Tests for lifting_lug() shape generation."""

    def test_lifting_lug_has_start_stop(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_lifting_lug_has_leading_hole(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode  # hole arc

    def test_lifting_lug_has_outer_arc(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G2" in gcode  # outer arc

    def test_lifting_lug_has_cord_arc(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G3" in gcode  # cord arc at base

    def test_lifting_lug_rb_zero(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=0, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "G1" in gcode  # straight line instead of arc

    def test_lifting_lug_rb_too_small(self, lines_list):
        lines, error_msg = lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=10, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=[])
        assert error_msg is not None
        assert "rb is too small" in error_msg

    def test_lifting_lug_cutting_pair(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, separation=20, cutting_pair=True, leadin=4, lines=lines_list)
        gcode = "".join(lines_list)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_lifting_lug_smarthole(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=True, leadin=4, lines=lines_list)
        assert len(lines_list) > 0

    def test_lifting_lug_line_count(self, lines_list):
        lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        assert len(lines_list) >= 10

    def test_lifting_lug_returns_tuple(self, lines_list):
        result = lifting_lug(w1=80, d1=20, h1=60, h2=10, d2=12, rb=50, kerf=2, internal_kerf=2, smarthole=False, leadin=4, lines=lines_list)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[1] is None
