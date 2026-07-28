"""Quickshape G-code generation service."""
from . import quickshapes as qs


class ShapeGeneratorService:
    """Generates G-code for quickshape primitives from UI parameter values.

    Each shape has its own method that reads widget values, calls the
    corresponding quickshapes function, and returns (lines, error_msg).
    The generate() method routes by shape index.
    """

    def __init__(self, main_window):
        self.main_window = main_window

    # -- Public API -----------------------------------------------------------

    def generate(self, shape_index):
        """Generate G-code lines for the given shape index.

        Args:
            shape_index: Integer 0-13 matching the quickshape type.

        Returns:
            Tuple of (lines_list, error_msg). error_msg is None on success.
        """
        generators = {
            0: self._circle,
            1: self._rectangle,
            2: self._donut,
            3: self._convex_rectangle,
            4: self._lifting_lug,
            5: self._u_lug,
            6: self._pipe_flange,
            7: self._pipe_saddle,
            8: self._exhaust_flange,
            9: self._n_square,
            10: self._l_gusset,
            11: self._angle_gusset,
            12: self._truss_support,
            13: self._web_stiffener,
        }

        gen = generators.get(shape_index)
        if gen is None:
            return [], f"Unknown shape index: {shape_index}"

        lines, error_msg = gen()
        return lines, error_msg

    # -- Shared helpers -------------------------------------------------------

    def _common_params(self):
        """Return shared parameters used by all shapes."""
        mw = self.main_window
        from qtpyvcp.utilities.info import Info

        lines = []
        kerf = mw.param_kerfwidth.value()
        internal_kerf = mw.quickshape_internal_kerf.value()
        smart_hole = mw.chkb_hole_detect_enable.isChecked()
        INFO = Info()
        qs.preamble(lines, metric=INFO.getIsMachineMetric())
        qs.magic_material(
            kw=kerf,
            ph=mw.param_pierceheight.value(),
            pd=mw.param_piercedelay.value(),
            ch=mw.param_cutheight.value(),
            fr=mw.param_cutfeedrate.value(),
            mt=1, th=0,
            ca=mw.param_cutamps.value(),
            cv=mw.param_cutvolts.value(),
            pe=mw.param_pauseatend.value(),
            gp=0, cm=0, jh=0, jd=0,
            lines=lines,
        )
        return lines, kerf, internal_kerf, smart_hole

    def _postamble(self, lines):
        """Append postamble and return the completed lines list."""
        qs.postamble(lines)
        return lines

    # -- Per-shape methods ----------------------------------------------------

    def _circle(self):
        lines, kerf, _, _ = self._common_params()
        diameter = self.main_window.id0_dbl_diam.value()
        qs.circle(diameter=diameter, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _rectangle(self):
        lines, kerf, _, _ = self._common_params()
        width = self.main_window.id1_dbl_width.value()
        height = self.main_window.id1_dbl_height.value()
        qs.rectangle(width, height, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _donut(self):
        lines, kerf, internal_kerf, smart_hole = self._common_params()
        inner_diam = self.main_window.id2_dbl_inner_diam.value()
        outer_diam = self.main_window.id2_dbl_outer_diam.value()
        qs.donut(od=outer_diam, id=inner_diam, kerf=kerf,
                 internal_kerf=internal_kerf, smarthole=smart_hole,
                 leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _convex_rectangle(self):
        lines, kerf, _, _ = self._common_params()
        width = self.main_window.id3_dbl_width.value()
        height = self.main_window.id3_dbl_height.value()
        qs.convex_rectangle(width, height, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _lifting_lug(self):
        lines, kerf, internal_kerf, smart_hole = self._common_params()
        w1 = self.main_window.id4_dbl_w1.value()
        d1 = self.main_window.id4_dbl_d1.value()
        h1 = self.main_window.id4_dbl_h1.value()
        h2 = self.main_window.id4_dbl_h2.value()
        d2 = self.main_window.id4_dbl_d2.value()
        rb = self.main_window.id4_dbl_rb.value()
        pair = self.main_window.id4_chk_pair.isChecked()
        separation = self.main_window.id4_dbl_separation.value()
        lines, error_msg = qs.lifting_lug(w1, d1, h1, h2, d2, rb, kerf=kerf,
                       internal_kerf=internal_kerf, smarthole=smart_hole,
                       separation=separation, cutting_pair=pair,
                       leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, error_msg

    def _u_lug(self):
        lines, kerf, _, _ = self._common_params()
        w1 = self.main_window.id5_dbl_w1.value()
        w2 = self.main_window.id5_dbl_w2.value()
        h = self.main_window.id5_dbl_h.value()
        qs.u_lug(w1, w2, h, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _pipe_flange(self):
        lines, kerf, internal_kerf, smart_hole = self._common_params()
        od = self.main_window.id6_dbl_od.value()
        pcd = self.main_window.id6_dbl_pcd.value()
        holes = self.main_window.id6_int_holes.value()
        hd = self.main_window.id6_dbl_hd.value()
        hole_type = self.main_window.id6_combo_hole.currentText()
        id_ = self.main_window.id6_dbl_id.value()
        qs.pipe_flange(od, pcd, holes, hd, hole_type, id_,
                       kerf=kerf, internal_kerf=internal_kerf,
                       smarthole=smart_hole, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _pipe_saddle(self):
        lines, kerf, _, _ = self._common_params()
        w = self.main_window.id7_dbl_w.value()
        h = self.main_window.id7_dbl_h.value()
        pd = self.main_window.id7_dbl_pd.value()
        o = self.main_window.id7_dbl_o.value()
        qs.pipe_saddle(w, h, pd, o, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _exhaust_flange(self):
        lines, kerf, internal_kerf, smart_hole = self._common_params()
        id_ = self.main_window.id8_dbl_id.value()
        wt = self.main_window.id8_dbl_wt.value()
        pcd = self.main_window.id8_dbl_pcd.value()
        bd = self.main_window.id8_dbl_bd.value()
        sw = self.main_window.id8_dbl_sw.value()
        nb = self.main_window.id8_int_nb.value()
        qs.exhaust_flange(id_, wt, pcd, bd, sw, nb,
                          kerf=kerf, internal_kerf=internal_kerf,
                          smarthole=smart_hole, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _n_square(self):
        lines, kerf, internal_kerf, smart_hole = self._common_params()
        w = self.main_window.id9_dbl_w.value()
        h = self.main_window.id9_dbl_h.value()
        hhn = self.main_window.id9_int_hhn.value()
        hhs = self.main_window.id9_dbl_hs.value()
        vhn = self.main_window.id9_int_vhn.value()
        vhs = self.main_window.id9_dbl_vs.value()
        hd = self.main_window.id9_dbl_hd.value()
        fr = self.main_window.id9_dbl_fr.value()
        ch_type = self.main_window.id9_combo_ch.currentText()
        ch_dim_dict = None
        if ch_type != "None":
            mw = self.main_window
            ch_dim_dict = {
                "chs": mw.id9_dbl_chs.value(),
                "chw": mw.id9_dbl_chw.value(),
                "chh": mw.id9_dbl_chh.value(),
                "chfr": mw.id9_dbl_chfr.value(),
                "cha": mw.id9_dbl_cha.value(),
                "chxo": mw.id9_dbl_chxo.value(),
                "chyo": mw.id9_dbl_chyo.value(),
            }
        qs.n_square(w, h, hhn, hhs, vhn, vhs, hd, fr, ch_type,
                    kerf=kerf, internal_kerf=internal_kerf,
                    smarthole=smart_hole, ch_dim_dict=ch_dim_dict,
                    leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _l_gusset(self):
        lines, kerf, _, _ = self._common_params()
        w = self.main_window.id10_dbl_w.value()
        h = self.main_window.id10_dbl_h.value()
        w1 = self.main_window.id10_dbl_w1.value()
        h1 = self.main_window.id10_dbl_h1.value()
        qs.L_gusset(w, h, w1, h1, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _angle_gusset(self):
        lines, kerf, _, _ = self._common_params()
        w = self.main_window.id11_dbl_w.value()
        h = self.main_window.id11_dbl_h.value()
        c1 = self.main_window.id11_dbl_c1.value()
        c2 = self.main_window.id11_dbl_c2.value()
        a = self.main_window.id11_dbl_a.value()
        pair = self.main_window.id11_chk_pair.isChecked()
        xoffset = self.main_window.id11_dbl_xoffset.value()
        yoffset = self.main_window.id11_dbl_yoffset.value()
        qs.angle_gusset(w, h, c1, c2, a, kerf=kerf, cutting_pair=pair,
                        xoffset=xoffset, yoffset=yoffset,
                        leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _truss_support(self):
        lines, kerf, _, _ = self._common_params()
        w = self.main_window.id12_dbl_w.value()
        h = self.main_window.id12_dbl_h.value()
        w1 = self.main_window.id12_dbl_w1.value()
        h1 = self.main_window.id12_dbl_h1.value()
        qs.truss_support(w, h, w1, h1, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None

    def _web_stiffener(self):
        lines, kerf, _, _ = self._common_params()
        w = self.main_window.id13_dbl_w.value()
        h = self.main_window.id13_dbl_h.value()
        c = self.main_window.id13_dbl_c.value()
        qs.web_stiffener(w, h, c, kerf=kerf, leadin=4, conv=1, lines=lines)
        self._postamble(lines)
        return lines, None
