import pytest
from unittest.mock import MagicMock
from math import cos, sin, radians, degrees, pi


@pytest.fixture
def quickshapes():
    from plasma import quickshapes
    return quickshapes


class TestFix:
    def test_rounds_to_five_decimals(self, quickshapes):
        assert quickshapes.fix(1.23456789) == 1.23457

    def test_returns_same_for_short_floats(self, quickshapes):
        assert quickshapes.fix(1.23) == 1.23

    def test_handles_zero(self, quickshapes):
        assert quickshapes.fix(0) == 0

    def test_handles_negative(self, quickshapes):
        assert quickshapes.fix(-1.23456789) == -1.23457


class TestStartCut:
    def test_appends_plasma_start(self, quickshapes):
        lines = []
        quickshapes.start_cut(lines)
        assert len(lines) == 1
        assert "M3" in lines[0]
        assert "plasma start" in lines[0]


class TestStopCut:
    def test_appends_plasma_end(self, quickshapes):
        lines = []
        quickshapes.stop_cut(lines)
        assert len(lines) == 1
        assert "M5" in lines[0]
        assert "plasma end" in lines[0]


class TestPreamble:
    def test_metric_preamble(self, quickshapes):
        lines = []
        quickshapes.preamble(lines, metric=True)
        assert any("G21" in line for line in lines)
        assert not any("G20" in line for line in lines)

    def test_inch_preamble(self, quickshapes):
        lines = []
        quickshapes.preamble(lines, metric=False)
        assert any("G20" in line for line in lines)
        assert not any("G21" in line for line in lines)

    def test_common_gcodes(self, quickshapes):
        lines = []
        quickshapes.preamble(lines)
        assert any("G40" in line for line in lines)
        assert any("G90" in line for line in lines)
        assert any("M52" in line for line in lines)
        assert any("M65 P2" in line for line in lines)
        assert any("M65 P3" in line for line in lines)
        assert any("M68" in line for line in lines)

    def test_has_begin_end_markers(self, quickshapes):
        lines = []
        quickshapes.preamble(lines)
        assert any("begin pre-amble" in line for line in lines)
        assert any("end pre-amble" in line for line in lines)


class TestPostamble:
    def test_has_gcodes(self, quickshapes):
        lines = []
        quickshapes.postamble(lines)
        assert any("G40" in line for line in lines)
        assert any("G90" in line for line in lines)
        assert any("M5" in line for line in lines)
        assert any("M30" in line for line in lines)

    def test_has_begin_end_markers(self, quickshapes):
        lines = []
        quickshapes.postamble(lines)
        assert any("begin post-amble" in line for line in lines)
        assert any("end post-amble" in line for line in lines)


class TestMagicMaterial:
    def test_returns_lines_list(self, quickshapes):
        lines = []
        result = quickshapes.magic_material(
            kw="steel", ph=120, pd=3, ch=10, fr=1.0, mt="mild", lines=lines
        )
        assert result is lines

    def test_has_material_comment(self, quickshapes):
        lines = []
        quickshapes.magic_material(
            kw="steel", ph=120, pd=3, ch=10, fr=1.0, mt="mild", lines=lines
        )
        assert any("begin material setup" in line for line in lines)

    def test_includes_params(self, quickshapes):
        lines = []
        quickshapes.magic_material(
            kw="steel", ph=120, pd=3, ch=10, fr=1.0, mt="mild", th=76, ca=6, cv=45, lines=lines
        )
        assert any("kw=steel" in line for line in lines)
        assert any("ph=120" in line for line in lines)
        assert any("th=76" in line for line in lines)
        assert any("ph=120" in line for line in lines)
        assert any("th=76" in line for line in lines)


class TestRefl:
    def test_reflect_point_across_line(self, quickshapes):
        # Reflect (0, 0) across line from (0, 0) to (10, 0) should give (0, 0) reflected to (0, 0) since it's on the line
        result = quickshapes.refl(0, 0, 10, 0, 0, 5)
        assert result == (0, -5)

    def test_reflect_point_on_perpendicular_bisector(self, quickshapes):
        # Reflect (5, 5) across line from (0, 0) to (10, 0) should give (5, -5)
        result = quickshapes.refl(0, 0, 10, 0, 5, 5)
        assert result == (5, -5)

    def test_reflect_across_diagonal_line(self, quickshapes):
        # Reflect (0, 10) across line from (0, 0) to (10, 10) should give (10, 0)
        result = quickshapes.refl(0, 0, 10, 10, 0, 10)
        assert result == (10, 0)

    def test_reflect_point_on_line(self, quickshapes):
        # Point on the line should reflect to itself
        result = quickshapes.refl(0, 0, 10, 10, 5, 5)
        assert result == (5, 5)


class TestMidpoint:
    def test_midpoint_basic(self, quickshapes):
        result = quickshapes.midpoint((0, 0), (10, 10))
        assert result == (5.0, 5.0)

    def test_midpoint_negative(self, quickshapes):
        result = quickshapes.midpoint((-10, -10), (10, 10))
        assert result == (0.0, 0.0)

    def test_midpoint_floats(self, quickshapes):
        result = quickshapes.midpoint((1.5, 2.5), (3.5, 4.5))
        assert result == (2.5, 3.5)


class TestCalculateSlope:
    def test_basic_slope(self, quickshapes):
        result = quickshapes.calculate_slope(0, 0, 10, 10)
        assert result == 1.0

    def test_horizontal_line(self, quickshapes):
        result = quickshapes.calculate_slope(0, 5, 10, 5)
        assert result == 0.0

    def test_negative_slope(self, quickshapes):
        result = quickshapes.calculate_slope(0, 10, 10, 0)
        assert result == -1.0

    def test_vertical_line_returns_none(self, quickshapes):
        result = quickshapes.calculate_slope(5, 0, 5, 10)
        assert result is None


class TestCircle:
    def test_circle_generates_lines(self, quickshapes):
        lines = []
        quickshapes.circle(100, 0.5, leadin=4, conv=1, lines=lines)
        assert len(lines) > 0

    def test_circle_has_start_stop_cut(self, quickshapes):
        lines = []
        quickshapes.circle(100, 0.5, lines=lines)
        gcode = "".join(lines)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_circle_has_arc_g2(self, quickshapes):
        lines = []
        quickshapes.circle(100, 0.5, lines=lines)
        gcode = "".join(lines)
        assert "G2" in gcode

    def test_circle_default_params(self, quickshapes):
        lines = []
        result = quickshapes.circle(100, 0.5, lines=lines)
        assert result is lines


class TestRectangle:
    def test_rectangle_generates_lines(self, quickshapes):
        lines = []
        quickshapes.rectangle(100, 50, 0.5, lines=lines)
        assert len(lines) > 0

    def test_rectangle_has_start_stop_cut(self, quickshapes):
        lines = []
        quickshapes.rectangle(100, 50, 0.5, lines=lines)
        gcode = "".join(lines)
        assert "M3" in gcode
        assert "M5" in gcode

    def test_rectangle_default_params(self, quickshapes):
        lines = []
        result = quickshapes.rectangle(100, 50, 0.5, lines=lines)
        assert result is lines


class TestDonut:
    def test_donut_has_preamble(self, quickshapes):
        lines = []
        quickshapes.donut(od=100, id=60, kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines)
        gcode = "".join(lines)
        assert "begin pre-amble" in gcode

    def test_donut_has_two_cuts(self, quickshapes):
        lines = []
        quickshapes.donut(od=100, id=60, kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines)
        gcode = "".join(lines)
        assert gcode.count("M3") == 2
        # Use \nM5 to avoid matching M52 in preamble
        assert gcode.count("\nM5 ") == 2


class TestConvexRectangle:
    def test_convex_rectangle_has_arc(self, quickshapes):
        lines = []
        quickshapes.convex_rectangle(100, 50, 0.5, lines=lines)
        gcode = "".join(lines)
        assert "G2" in gcode

    def test_convex_rectangle_default_params(self, quickshapes):
        lines = []
        result = quickshapes.convex_rectangle(100, 50, 0.5, lines=lines)
        assert result is lines


class TestLiftingLug:
    def test_lifting_lug_generates_lines(self, quickshapes):
        lines = []
        quickshapes.lifting_lug(
            w1=40, d1=20, h1=60, h2=30, d2=12, rb=0,
            kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0

    def test_lifting_lug_with_cutting_pair(self, quickshapes):
        lines = []
        quickshapes.lifting_lug(
            w1=40, d1=20, h1=60, h2=30, d2=12, rb=0,
            kerf=0.5, internal_kerf=0.5, smarthole=False,
            cutting_pair=True, separation=5, lines=lines
        )
        gcode = "".join(lines)
        assert gcode.count("M3") == 4  # two shapes * (start + pair start)

    def test_lifting_lug_with_rounded_back(self, quickshapes):
        lines = []
        quickshapes.lifting_lug(
            w1=40, d1=20, h1=60, h2=30, d2=12, rb=25,
            kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        gcode = "".join(lines)
        assert "G3" in gcode

    def test_lifting_lug_rb_too_small(self, quickshapes):
        # rb too small for w1 should fall back to straight line
        class MockParent:
            id4_error_text = MagicMock()
        lines = []
        quickshapes.lifting_lug(
            w1=40, d1=20, h1=60, h2=30, d2=12, rb=10,  # rb < w1/2
            kerf=0.5, internal_kerf=0.5, smarthole=False,
            parent=MockParent(), lines=lines
        )
        gcode = "".join(lines)
        assert "G1 X0" in gcode  # fallback straight line

    def test_lifting_lug_smarthole(self, quickshapes):
        lines = []
        quickshapes.lifting_lug(
            w1=40, d1=20, h1=60, h2=30, d2=12, rb=0,
            kerf=0.5, internal_kerf=0.5, smarthole=True, lines=lines
        )
        assert len(lines) > 0


class TestULug:
    def test_u_lug_generates_lines(self, quickshapes):
        lines = []
        quickshapes.u_lug(w1=40, w2=20, h=60, kerf=0.5, lines=lines)
        assert len(lines) > 0

    def test_u_lug_has_start_stop_cut(self, quickshapes):
        lines = []
        quickshapes.u_lug(w1=40, w2=20, h=60, kerf=0.5, lines=lines)
        gcode = "".join(lines)
        assert "M3" in gcode
        assert "M5" in gcode


class TestPipeFlange:
    def test_pipe_flange_round_hole(self, quickshapes):
        lines = []
        quickshapes.pipe_flange(
            od=100, pcd=80, holes=4, hd=10, hole_type="Round",
            id=30, kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0

    def test_pipe_flange_square_hole(self, quickshapes):
        lines = []
        quickshapes.pipe_flange(
            od=100, pcd=80, holes=4, hd=10, hole_type="Square",
            id=30, kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0

    def test_pipe_flange_multiple_holes(self, quickshapes):
        lines = []
        quickshapes.pipe_flange(
            od=100, pcd=80, holes=6, hd=10, hole_type="Round",
            id=30, kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        gcode = "".join(lines)
        # Should have 6 mounting holes + 1 center hole + 1 outer cut
        assert gcode.count("M3") == 8


class TestPipeSaddle:
    def test_pipe_saddle_generates_lines(self, quickshapes):
        lines = []
        quickshapes.pipe_saddle(w=100, h=50, pd=40, o=10, kerf=0.5, lines=lines)
        assert len(lines) > 0

    def test_pipe_saddle_has_arc(self, quickshapes):
        lines = []
        quickshapes.pipe_saddle(w=100, h=50, pd=40, o=10, kerf=0.5, lines=lines)
        gcode = "".join(lines)
        assert "G3" in gcode


class TestExhaustFlange:
    def test_exhaust_flange_2_corners(self, quickshapes):
        lines = []
        quickshapes.exhaust_flange(
            id=60, wt=10, pcd=80, bd=10, sw=15, nb=2,
            kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0

    def test_exhaust_flange_3_corners(self, quickshapes):
        lines = []
        quickshapes.exhaust_flange(
            id=60, wt=10, pcd=80, bd=10, sw=15, nb=3,
            kerf=0.5, internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0


class TestNSquare:
    def test_n_square_round_center(self, quickshapes):
        lines = []
        ch_dim_dict = {"chxo": 0, "chyo": 0, "chs": 20}
        quickshapes.n_square(
            w=100, h=80, hhn=3, hhs=30, vhn=2, vhs=40,
            hd=10, fr=5, ch_type="Round", kerf=0.5,
            internal_kerf=0.5, smarthole=False,
            ch_dim_dict=ch_dim_dict, lines=lines
        )
        assert len(lines) > 0

    def test_n_square_no_center_hole(self, quickshapes):
        lines = []
        quickshapes.n_square(
            w=100, h=80, hhn=2, hhs=40, vhn=2, vhs=40,
            hd=10, fr=0, ch_type=None, kerf=0.5,
            internal_kerf=0.5, smarthole=False, lines=lines
        )
        assert len(lines) > 0

    def test_n_square_rectangle_center(self, quickshapes):
        lines = []
        ch_dim_dict = {"chw": 30, "chh": 20, "chfr": 0, "cha": 0, "chxo": 0, "chyo": 0}
        quickshapes.n_square(
            w=100, h=80, hhn=2, hhs=40, vhn=2, vhs=40,
            hd=10, fr=0, ch_type="Rectangle", kerf=0.5,
            internal_kerf=0.5, smarthole=False,
            ch_dim_dict=ch_dim_dict, lines=lines
        )
        assert len(lines) > 0


class TestLGusset:
    def test_l_gusset_generates_lines(self, quickshapes):
        lines = []
        quickshapes.L_gusset(w=100, h=80, w1=20, h1=30, kerf=0.5, lines=lines)
        assert len(lines) > 0

    def test_l_gusset_has_start_stop_cut(self, quickshapes):
        lines = []
        quickshapes.L_gusset(w=100, h=80, w1=20, h1=30, kerf=0.5, lines=lines)
        gcode = "".join(lines)
        assert "M3" in gcode
        assert "M5" in gcode


class TestAngleGusset:
    def test_angle_gusset_generates_lines(self, quickshapes):
        lines = []
        quickshapes.angle_gusset(w=100, h=80, c1=20, c2=30, a=45, kerf=0.5, lines=lines)
        assert len(lines) > 0

    def test_angle_gusset_with_cutting_pair(self, quickshapes):
        lines = []
        quickshapes.angle_gusset(
            w=100, h=80, c1=20, c2=30, a=45, kerf=0.5,
            cutting_pair=True, xoffset=50, yoffset=0, lines=lines
        )
        gcode = "".join(lines)
        assert gcode.count("M3") == 2


class TestTrussSupport:
    def test_truss_support_generates_lines(self, quickshapes):
        lines = []
        quickshapes.truss_support(w=100, h=80, w1=30, h1=40, kerf=0.5, lines=lines)
        assert len(lines) > 0


class TestWebStiffener:
    def test_web_stiffener_generates_lines(self, quickshapes):
        lines = []
        quickshapes.web_stiffener(w=80, h=60, c=20, kerf=0.5, lines=lines)
        assert len(lines) > 0
