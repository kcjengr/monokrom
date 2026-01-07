from math import cos, sin, tan, atan, atan2, asin, degrees, radians, sqrt, hypot, pi
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)

def fix(v):
    return round(v, 5)

def start_cut(lines):
    lines.append("M3 $0 S1 (plasma start)\n")

def stop_cut(lines):
    lines.append("M5 $0 (plasma end)\n")

def preamble(lines, metric=True):
    lines.append(';begin pre-amble\n')
    if metric:
        lines.append(' G21 (units: metric)\n')
    else:
        lines.append(' G20 (units: inch)\n')
    lines.append(' G40 (cutter compensation: off)\n')
    lines.append(' G90 (distance mode: absolute)\n')
    lines.append(' M52 P1 (adaptive feed: on)\n') 
    lines.append(' M65 P2 (enable THC)\n')
    lines.append(' M65 P3 (enable torch)\n')
    lines.append(' M68 E3 Q0 (velocity 100%)\n')
    lines.append(' G64 P0.025 Q0.025 (tracking tolerances: 0.025mm)\n') 
    lines.append(';end pre-amble\n')

def postamble(lines):
    lines.append(';begin post-amble\n')
    lines.append(' G40 (cutter compensation: off)\n')
    lines.append(' G90 (distance mode: absolute)\n')
    lines.append(' M65 P2 (enable THC)\n')
    lines.append(' M65 P3 (enable torch)\n')
    lines.append(' M68 E3 Q0 (velocity 100%)\n')
    lines.append(' M5 $-1 (backup stop)\n')
    lines.append(' M159 P601 Q0 (Reset pierce mode to normal)\n')
    lines.append(';end post-amble\n')
    lines.append(' M30 (end program)\n')

def magic_material(kw, ph, pd, ch, fr, mt, th=0, ca=0, cv=0, pe=0, gp=0, cm=0, jh=0, jd=0, lines=[]):
    lines.append(';\n;begin material setup\n')
    lines.append(f" (o=0, kw={kw}, ph={ph}, pd={pd}, ch={ch}, fr={fr}, mt={mt}, th={th:.0f}, ca={ca:.0f}, cv={cv:.0f}, pe={pe}, gp={gp}, cm={cm:.0f}, jh={jh}, jd={jd})\n")
    lines.append(' F#<_hal[plasmac.cut-feed-rate]>\n')
    lines.append(';end material setup\n')
    return lines

def circle(diameter, kerf, leadin=4, conv=1, lines=[]):
    """
    Build the gcode for a circle
    
    Param:
    diameter: the circle diameter
    kerf: width of the kerf in measurement units
    leadin: length of lead-in in measurement units
    conv: the conversation factor for measurement units.  Assumes mm as base
    """
    # build the circle around 0,0
    # use a straight lead in
    x = (diameter+kerf)/2
    y = 0
    lines.append(f"G0 X{x + leadin} Y0\n")
    start_cut(lines)
    lines.append(f"G1 X{x} Y0\n")
    lines.append(f"G2 I-{x}\n")
    stop_cut(lines)
    return lines

def rectangle(width, height, kerf, leadin=4, conv=1, lines=[]):
    """
    Build the gcode for a rectangle
    
    Param:
    width, height: sides of rectangle
    kerf: width of the kerf in measurement units
    leadin: length of lead-in in measurement units
    conv: the conversation factor for measurement units.  Assumes mm as base
    """
    # build the rectangle with 0,0 as lower left corner
    # use a straight lead in
    x=0
    y=0
    lines.append(f"G0 X0 Y0\n")
    # start cut at leadin
    start_cut(lines)
    lines.append(f"G1 Y{leadin+height+kerf}\n")
    lines.append(f"G1 X{width+kerf}\n")
    lines.append(f"G1 Y{leadin}\n")
    lines.append(f"G1 X0\n")
    stop_cut(lines)
    return lines

def donut(od, id, kerf, leadin=4, conv=1, lines=[]):
    x = (id+kerf)/2
    y = 0
    preamble(lines)
    lines.append(f"G0 X{x - leadin} Y0\n")
    start_cut(lines)
    lines.append(f"G1 X{x} Y0\n")
    lines.append(f"G3 I-{x}\n")
    stop_cut(lines)
    x = (od+kerf)/2
    lines.append(f"G0 X{x + leadin} Y0\n")
    start_cut(lines)
    lines.append(f"G1 X{x} Y0\n")
    lines.append(f"G2 I-{x}\n")
    stop_cut(lines)
    return lines

def convex_rectangle(width, height, kerf, leadin=4, conv=1, lines=[]):
    # build the rectangle with 0,0 as lower left corner
    # use a straight lead in
    x=0
    y=0
    lines.append(f"G0 X0 Y0\n")
    # start cut at leadin
    start_cut(lines)
    lines.append(f"G1 Y{leadin+height+kerf}\n")
    lines.append(f"G2 X{width+kerf} Y{leadin+height+kerf} I{(width+kerf)/2}\n")
    lines.append(f"G1 Y{leadin}\n")
    lines.append(f"G1 X0\n")
    stop_cut(lines)
    return lines

def lifting_lug(w1, d1, h1, h2, d2, rb, kerf, separation=0, cutting_pair=False, parent=None, leadin=4, conv=1, lines=[]):
    # calculate the key points
    # given two triangles to solve for
    # Triangle 1:
    #    From center of d1 circle, line down (called 'xv') to half w1 (called 'wh')
    #    forming a right angle. The hypotenuse from d1 center to
    #    either 0,0 or 0,h2. (Called 'h')
    # 
    # Triangle 2:
    #    From center of d1 circle out to edge of circle (left side, line called 'r')
    #    forming right angle with line to either 0,0 or 0,h2 (called 'd').
    #    Hypotenuse is common with triangle 1.
    #
    # Solve hypotenuse of triangle 1, 'h'.  Then solve remaining unknown side on
    # triangle 2. This will give length will be 'd'.
    # Then solve the two angles closest to 0,0 and add sum them as 'angle'.
    #
    # h = sqrt(x**2 + w**2)
    # d = sqrt(h**2 - r**2)
    # 
    # a1 = atan(x/w)
    # a2 = atan(r/d)
    #
    # a1 is angle between line wh and h
    # a2 is angle between h and d
    # Therefore a1+a2 = total angle from base of lug (w1) to flat side that is
    # at a tangent to the circle formed by d1.
    #
    # Now able to use formula to determine the x,y position of the angled
    # angled side tangent point of the lifting lug.  This can then be
    # mirrored to the other side of the lug about the middle of w1.
    #
    # x1 = x + (d * cos(angle))
    # y1 = y + (d * sin(angle))
    #
    # x and y are the start point of the vector (side of the lug) and d is
    # the distance or magnitude of the vector with the angle (direction)
    # referenced from the flat base plan.
    kh = kerf/2                 # half kerf width
    r = (d1+kerf)/2             # radius of d1
    r2 = (d2+kerf)/2            # radius of d2
    wh = (w1+kerf)/2            # middle of w1
    xv = (h1-h2)-r-kh           # vertical line from centre d1 (and d2) down to base of triangle 1
    h = sqrt(xv**2 + wh**2)     # hypotenuse of triangle 1
    d = sqrt(h**2 - r**2)       # adjacent side of triangle 2
    a1 = atan(xv/wh)            # angle between line wh and h
    a2 = atan(r/d)              # angle between h and d 
    angle = a1 + a2             # total angle from base of lug (w1) to flat side that is tangent to d1
    
    x1 = d * cos(angle)         # x position of tangent point on d1
    y1 = h2 + (d * sin(angle))  # y psotion of tangent point on d1

    # mirror for vertical and horizontal lines. k = the mirror line
    # horixontal line (x stays same):  x,y = (x, 2k-y)
    # vertical line (y stays same): x,y = (2k-x, y)
    # mirror line horizontal and should be at half h1 but after *2 becomes h1
    mirror_y = lambda y0: h1-y0
    mirror_x = lambda x0: w1-x0

    lines.append(f"(Leadin for lifting hole)\n")
    lines.append(f"G0 X{wh} Y{leadin+h1-r}\n")
    start_cut(lines)
    lines.append(f"G1 X{wh-r2}\n")
    lines.append(f"G3 I{r2}\n")
    LOG.debug(f"g3 for liftring lug: startX={wh-r2} I={r2}")
    stop_cut(lines)
    lines.append(f"(Leadin for outer shape)\n")
    lines.append(f"G0 X0 Y0\n")
    start_cut(lines)
    lines.append(f"G1 Y{leadin+h2}\n")
    lines.append(f"G1 X{x1} Y{y1}\n")
    lines.append(f"G2 X{mirror_x(x1)+kerf} Y{y1} I{(mirror_x(x1)+kerf-x1)/2} J{leadin+h1-r-y1}\n")
    lines.append(f"G1 X{w1+kerf} Y{leadin+h2}\n")
    lines.append(f"G1 Y{leadin}\n")
    if parent != None: parent.id4_error_text.setText("")
    if rb == 0:
        lines.append(f"G1 X0\n")
    else:
        # calc cord/circle data to construct arc
        # Given cord length L (w1 for our params) and radius rb
        # distance from cord to center circle is 'cd'
        # cd = sqrt(rb**2 - (L/2)**2)
        # angle of arc is 2*asin(L / (2*rb))
        try:
            cd = sqrt((rb**2) - ((w1/2)**2))
            #angle_cord_arc = degrees(2 * asin(w1 / (2*rb)))
            #angle_cord_offset = (180-angle_cord_arc)/2
            #dxf.add_arc((wh,-cd), rb, angle_cord_offset, 180-angle_cord_offset)
            lines.append(f"G3 X0 Y{leadin} I-{wh} J-{cd}\n")
        except ValueError as e:
            # math calc issue so just do plan straight line
            LOG.warn(f"Error {e} found.  Check rb is large enough.")
            if parent != None:
                parent.id4_error_text.setText("rb is to small.\nrb should be >= (w1 / 2).\nOr put another way,\n(rb * 2) >= w1")
            lines.append(f"G1 X0\n")

    # if cutting_pair is true generate a second shape that is offset
    # and 180 degrees.
    if cutting_pair:
        # remember to cut external cw.  So start far upper right
        # offset_x is the gap between parts plus half w1
        offset_x = separation + w1
        lines.append(f"(Leadin for lifting hole)\n")
        lines.append(f"G0 X{wh+offset_x} Y{mirror_y(leadin+h1-r)}\n")
        start_cut(lines)
        lines.append(f"G1 X{wh-r2+offset_x}\n")
        lines.append(f"G3 I{r2}\n")
        stop_cut(lines)
        
        lines.append(f"(Leadin for outer shape)\n")
        lines.append(f"G0 X{offset_x+w1} Y{h1+leadin}\n")
        start_cut(lines)
        lines.append(f"G1 Y{mirror_y(leadin+h2)}\n")
        lines.append(f"G1 X{mirror_x(x1)+offset_x} Y{mirror_y(y1)}\n")
        # calc the J offset for arc
        j_offset = mirror_y(leadin+h1-r) - mirror_y(y1)
        lines.append(f"G2 X{x1+offset_x} Y{mirror_y(y1)} I{(x1-mirror_x(x1))/2} J{j_offset}\n")
        lines.append(f"G1 X{mirror_x(w1+kerf)+offset_x} Y{mirror_y(leadin+h2)}\n")
        lines.append(f"G1 Y{mirror_y(leadin)}\n")
        if rb == 0:
            lines.append(f"G1 X{offset_x+w1}\n")
        else:
            # calc cord/circle data to construct arc
            # Given cord length L (w1 for our params) and radius rb
            # distance from cord to center circle is 'cd'
            # cd = sqrt(rb**2 - (L/2)**2)
            # angle of arc is 2*asin(L / (2*rb))
            try:
                cd = sqrt((rb**2) - ((w1/2)**2))
                #angle_cord_arc = degrees(2 * asin(w1 / (2*rb)))
                #angle_cord_offset = (180-angle_cord_arc)/2
                #dxf.add_arc((wh,-cd), rb, angle_cord_offset, 180-angle_cord_offset)
                lines.append(f"G3 X{offset_x+w1} I{wh} J{cd}\n")
            except ValueError as e:
                # math calc issue so just do plan straight line
                LOG.warn(f"Error {e} found.  Check rb is large enough.")
                if parent != None:
                    parent.id4_error_text.setText("rb is to small.\nrb should be >= (w1 / 2).\nOr put another way,\n(rb * 2) >= w1")
                lines.append(f"G1 X{offset_x+w1}\n")
    
    stop_cut(lines)
    return lines

def u_lug(w1, w2, h, kerf, leadin=4, conv=1, lines=[]):
    outer_radius = w1/2
    inner_radius = w2/2
    leg_size = (w1-w2)/2
    kh = kerf/2
    lines.append(f"\n")
    # build the legs
    lines.append(f"G0 X{0-kh} Y{0-leadin}\n")
    start_cut(lines)
    lines.append(f"G1 Y{h-outer_radius}\n")
    lines.append(f"G2 X{w1+kh} I{outer_radius+kh}\n")
    lines.append(f"G1 Y{0-kh}\n")
    lines.append(f"G1 X{w1-leg_size-kh}\n")
    lines.append(f"G1 Y{h-outer_radius}\n")
    lines.append(f"G3 X{leg_size+kh} I{-inner_radius+kh}\n")
    lines.append(f"G1 Y{0-kh}\n")
    lines.append(f"G1 X{0-kh}\n")
    stop_cut(lines)
    return lines
    
def pipe_flange(od, pcd, holes, hd, hole_type, id, kerf, leadin=4, conv=1, lines=[]):
    kh = kerf/2
    lines.append(f"\n")
    
    # make central hole
    # note: Shape is built around 0,0 as center
    match hole_type:
        case "Round":
            lines.append(f"G0 X0 Y{(id/2)-kh}\n")
            start_cut(lines)
            lines.append(f"G3 J-{(id/2)-kh}\n")
        case "Square":
            sq_start_x = -id/2
            sq_start_y = id/2
            lines.append(f"G0 X{sq_start_x+leadin} Y0\n")
            start_cut(lines)
            lines.append(f"G1 X{sq_start_x+kh}\n")
            lines.append(f"G1 Y{sq_start_y-kh}\n")
            lines.append(f"G1 X{sq_start_x+id-kerf}\n")
            lines.append(f"G1 Y{sq_start_y-id-kerf}\n")
            lines.append(f"G1 X{sq_start_x+kh}\n")
            lines.append(f"G1 Y0\n")
    stop_cut(lines)
    # calc pcd for holes
    # x1 = x + (d * cos(angle))
    # y1 = y + (d * sin(angle))
    angle_gap = 360/holes
    i = 0
    current_angle = 90
    d = pcd/2
    while i < holes:
        x1 = d * cos(radians(current_angle))
        y1 = d * sin(radians(current_angle))
        lines.append(f"\n")
        lines.append(f"G0 X{x1-(hd/2)+kh} Y{y1}\n")
        start_cut(lines)
        lines.append(f"G3 I{(hd/2)-kh}\n")
        stop_cut(lines)
        current_angle += angle_gap
        if current_angle > 360:
            current_angle -= 360
        i += 1 
    
    # calc where leadin starts
    x = (leadin + od/2) * cos(radians(45))
    y = (leadin + od/2) * sin(radians(45))
    lines.append(f"G0 X{x} Y{y}\n")
    start_cut(lines)
    x = (kh + od/2) * cos(radians(45))
    y = (kh + od/2) * sin(radians(45))
    lines.append(f"G1 X{x} Y{y}\n")
    lines.append(f"G2 I-{x} J-{y}\n")
    stop_cut(lines)

def pipe_saddle(w, h, pd, o, kerf, leadin=4, conv=1, lines=[]):
    kh = kerf/2
    lines.append(f"\n")
    # calc the needed values
    # circle center and radius
    cx = w/2    # circle center x
    cy = h + o  # circle center y
    cr = pd/2   # circle radius
    angle = asin(o/cr) if o > 0 else 0
    x1 = cx + (cr * cos(angle))
    y1 = cy + (cr * sin(angle))
    LOG.debug(f"Pipe Saddle: angle={degrees(angle)}, x1={x1}, y1={y1}")
    # add basic shape
    LOG.debug(f"points list for polyline:  {[((2*cx)-x1,y1), (0,h), (0,0), (w,0), (w,h), (x1,y1)]}")
    # remember to cut cw
    lines.append(f"G0 X{fix(x1-leadin)} Y{fix(h+kh)}\n") # lead in
    start_cut(lines)
    lines.append(f"G1 X{fix(w+kh)}\n")       # start center to top right corner
    lines.append(f"G1 Y{fix(0-kh)}\n")       # down to y0
    lines.append(f"G1 X{fix(0-kh)}\n")       # left to x0
    lines.append(f"G1 y{fix(h+kh)}\n")       # up to top left corner
    lines.append(f"G1 X{fix((2*cx)-x1+kh)}\n")
    lines.append(f"G3 X{fix(x1-kh)} I{fix(cx-((2*cx)-x1+kh))} J{fix(cy-(h+kh))}\n")
    stop_cut(lines)

def exhaust_flange(id, wt, pcd, bd, sw, nb, kerf, leadin=4, conv=1, lines=[]):
    def build_corner(rr1, rr2, xx2, yy2, corners, lines):
        """
        Build the mounting hole corners and slopped sides.
        
        Args:
            rr1 (float): Radius of the inner hole plus wall thickness
            rr2 (float): Diameter of the bolt hole
            xx2, yy2 (float): Position of the corners hole
            corners (int): Number of corners.  2 or 3
            lines : ref to the lines list 
        
        Approach:
            Calculate the two lines start/end positions,
            the small corner arc and the large arc.
            THEN build them in the correct order to allow
            clockwise cut path.
            Assumes that the torch is already active and
            that the rapid/leadin to the start position is
            already done.
        """
        LOG.debug("=========  build_corner =========")
        kh = kerf/2
        #d= sqrt(xx2**2 + yy2**2)
        d = hypot(xx2, yy2)
        theta = cos((rr1 - rr2) / d)
        # LOG.debug(f"Initial theta={degrees(theta)}")
        theta2 = (pi / corners) - theta
        
        if theta < 0:
            theta = pi / corners
            theta2 = 0
        
        a = a_start = atan2(xx2, yy2) - theta
        s = s_start = sin(a)
        c = c_start = cos(a)
        # LOG.debug(f"corner data: rr1={rr1}, rr2={rr2}, xx2={xx2}, yy2={yy2}, corners={corners}")
        # LOG.debug(f"corner data: d={d}, theta={(theta)}, theta2={(theta2)}, a={a}")
        # LOG.debug(f"corner data: s={s}, c={c}")
        line1_start_x = fix(s*rr1)
        line1_start_y = fix(c*rr1)
        line1_end_x = fix((s*rr2)+xx2)
        line1_end_y = fix((c*rr2)+yy2)
        
        # we have the arc centre:  xx2, yy2
        # we have start point of arc which is part of a right triangle: (s*rr2)+xx2, (c*rr2)+yy2
        # with center and end point we have a vector which has distance (r) and angle (ang)
        arc_center_x = xx2
        arc_center_y = yy2
        arc_start_x = (s*rr2)+xx2
        arc_start_y = (c*rr2)+yy2
        arc_center_offset_x = s*rr2 
        arc_center_offset_y = c*rr2 
        bigarc1_end_x = s*rr1
        bigarc1_end_y = c*rr1
        ang1 = atan2(arc_start_y - arc_center_y, arc_start_x - arc_center_x)
        r = hypot(arc_start_x - arc_center_x, arc_start_y - arc_center_y)

        # need to calc small arc start before new s & c recalc'd
        smallarc_start_x = fix((s*rr2)+xx2)
        smallarc_start_y = fix((c*rr2)+yy2)

        
        a += (theta * 2)
        s = sin(a)
        c = cos(a)
        arc_end_x = (s*rr2)+xx2
        arc_end_y = (c*rr2)+yy2
        # bigarc2_start_x = s*rr1
        # bigarc2_start_y = c*rr1
        ang2 = atan2(arc_end_y - arc_center_y, arc_end_x - arc_center_x)

        # LOG.debug(f"angle 0,0 to arc start={degrees(ang1)}, start x/y={(arc_start_x, arc_start_y)}")
        # LOG.debug(f"angle 0,0 to arc end={degrees(ang2)}, end x/y={(arc_end_x, arc_end_y)}")
        # LOG.debug(f"using center = {(fix(arc_center_x), fix(arc_center_y))}, r={r}")
        # small arc
        smallarc_end_x = fix((s*rr2)+xx2)
        smallarc_end_y = fix((c*rr2)+yy2)
        smallarc_I = -fix(arc_center_offset_x)
        smallarc_J = -fix(arc_center_offset_y)
        # line on bottom
        line2_start_x = fix((s*rr2)+xx2)
        line2_start_y = fix((c*rr2)+yy2)
        line2_end_x = fix(s*rr1)
        line2_end_y = fix(c*rr1)

        #
        # Start building the shape up for cw cutting
        #

        # Big arc processing        
        if theta2 > 0:
            #big arc 1
            ang1 = atan2(bigarc1_end_y ,bigarc1_end_x)
            bigarc1_start_x = rr1 * cos(ang1 + (theta2 *2))
            bigarc1_start_y = rr1 * sin(ang1 + (theta2 *2))
            # add arc cares about the direction of the arc.
            # i.e. drawing from smaller angle to larger angle in ccw direction
            # Also theta is a modifier.  Add it to the start angle to get end angle.
            #writer.add_arc((0,0), rr1, degrees(ang1), degrees(ang1)+degrees(theta2 *2))
            LOG.debug(">>> Big Arc <<<")
            LOG.debug(f"big arc1 data: start x1/y1={(fix(bigarc1_start_x) ,fix(bigarc1_start_y))}, radius={fix(rr1)}")
            LOG.debug(f"big arc1 data: end x1/y1={(fix(bigarc1_end_x) ,fix(bigarc1_end_y))}, I/J offsets={(-fix(bigarc1_start_x), -fix(bigarc1_start_y))}")
            LOG.debug(f"big arc1 data: effective center x/y = {(fix(bigarc1_start_x)+-fix(bigarc1_start_x), fix(bigarc1_start_y)+-fix(bigarc1_start_y))}")
            LOG.debug(f"big arc1 data: angle1 = {degrees(ang1)}, angle2 = {degrees(ang1 + (theta2 *2))}")
            LOG.debug(f"big arc1 data: data to build angles:")
            LOG.debug(f"big arc1 data: a = atan2{(xx2,yy2)} - {theta} = {a_start} : sin(a)={s_start} : cos(a)={c_start}")
            LOG.debug(f"big arc1 data: angle1 = atan2{(bigarc1_end_y, bigarc1_end_x)} = {degrees(ang1)}, angle2 = angle1 + theta2*2 = {degrees(ang1 + (theta2 *2))}")
            LOG.debug(f"big arc1 data: angle2 used to calc big arc start x/y. r1 = {rr1}")
            # lines.append(f"G2 X{fix(bigarc1_end_x)} Y{fix(bigarc1_end_y)} I{-fix(bigarc1_start_x)} J{-fix(bigarc1_start_y)}\n")
            line1_start_x = fix(bigarc1_end_x)
            line1_start_y = fix(bigarc1_end_y)
        
        LOG.debug(">>> Line 1 <<<")
        LOG.debug(f"line1 data: Start={(line1_start_x,line1_start_y)}, End={(line1_end_x, line1_end_y)}")
        # first line to corner arc
        lines.append(f"G1 X{line1_end_x} Y{line1_end_y}\n")
        LOG.debug(">>> Small Arc <<<")
        # small corner
        LOG.debug(f"Small arc: Start={(smallarc_start_x, smallarc_start_y)}, End={(smallarc_end_x, smallarc_end_y)}")
        LOG.debug(f"Small arc: I/J={(smallarc_I, smallarc_J)}, radius={fix(r)}")
        LOG.debug(f"Small arc: effective center x/y = {(smallarc_start_x+smallarc_I, smallarc_start_y+smallarc_J)}")
        lines.append(f"G2 X{smallarc_end_x} Y{smallarc_end_y} I{smallarc_I} J{smallarc_J}\n")
        # line 2
        LOG.debug(">>> Line 2 <<<")
        LOG.debug(f"line2 data: Start={(line2_start_x, line2_start_y)}, End={(line2_end_x, line2_end_y)}")
        lines.append(f"G1 X{line2_end_x} Y{line2_end_y}\n")
        LOG.debug("+---------------------------------------------------+")
    
    def build_slot(x, y, sw, bd, lines):
        LOG.debug("============= build_slot ===========")
        kh = kerf/2
        if sw - bd == 0:
            #writer.add_circle((x, y), bd/2)
            lines.append(f"G0 X{x} Y{y}\n")
            start_cut(lines)
            lines.append(f"G1 X{x+(bd/2)-kh}\n")
            lines.append(f"G3 I{-(bd/2)-kh}")
            stop_cut(lines)
            return
        
        a = atan2(y,x)
        r1 = bd/2
        r2 = (sw - bd) / 2
        s = sin(a) * r2
        c = cos(a) * r2
        # gives the two ends of the middle line. 
        x1 = x + c
        y1 = y + s
        x2 = x - c
        y2 = y - s
        LOG.debug(f"build slot: x/y={(x,y)}, sw={sw}, bd={bd}, a={degrees(a)}, r1={r1}, r2={r2}")
        LOG.debug(f"build slot: s={s}, c={c}")
        
        # we need to calculate the lines either side of the middle line.
        # Find the points that are are 90 degree to each end point.
        # so get that unit value for x and y offsets and scale it by r1.
        # Given r1 is essentially the hypotenuse then:
        # cosine gives the Adjacent == x axis
        # sine gives the Opposite == y axis
        s = sin(a + (pi / 2)) * r1
        c = cos(a + (pi / 2)) * r1
        LOG.debug(f"build slot: recalced s={s}, c={c}")
        LOG.debug(f"build slot: mirror line x1/y1={(x1,y1)}, x2/y2={(x2,y2)}")
        # writer.add_polyline_2d([(x1+c,y1+s), (x2+c, y2+s)])
        # writer.add_polyline_2d([(x1-c,y1-s), (x2-c, y2-s)])
        # work out the start/end angles for arc1
        a_start = atan2(s, c)
        a_end = atan2(-s, -c)
        LOG.debug(f"a_start={degrees(a_start)}, a_end={degrees(a_end)}")
        # writer.add_arc((x1,y1),r1, degrees(a_end), degrees(a_start))
        # writer.add_arc((x2,y2),r1, degrees(a_start), degrees(a_end))
        lines.append(f"(Got to start of slot line 1)\n")
        lines.append(f"G0 X{fix(x1+c)} Y{fix(y1+s)}\n")
        start_cut(lines)
        lines.append(f"G1 X{fix(x2+c)} Y{fix(y2+s)}\n")
        lines.append(f"G3 X{fix(x2-c)} Y{fix(y2-s)} I{fix(-c)} J{fix(-s)}\n")
        lines.append(f"G1 X{x1-c} Y{y1-s}\n")
        lines.append(f"G3 X{fix(x1+c)} Y{fix(y1+s)} I{fix(c)} J{fix(s)}\n")
        stop_cut(lines)
        LOG.debug("+---------------------------------------------------+")
        
    
    # r1 is the outside major radius.  i.e. hole + wall thickness.
    
    kh = kerf/2
    r1 = (id / 2) + wt
    # r2 is the bolt diameter
    r2 = bd
    offset = 0
    # if slot width (sw) is larger then than bolt diam then calc an offset
    if sw > bd:
        offset = (sw - bd) / 2
    # pcr = pitch circle radius
    pcr = pcd /2
    # part is built around a 0,0 centre
    lines.append(f"G0 X{(id/2)-leadin} Y{0}\n")
    start_cut(lines)
    lines.append(f"G1 X{(id/2)-kh} Y{0}\n")
    lines.append(f"G3 I-{(id/2)-kh}\n")
    stop_cut(lines)
    
    if nb == 2:
        build_slot(pcr, 0, sw, bd, lines)
        build_slot(-pcr, 0, sw, bd, lines)
        # work out the starting position for the first corner
        # and rapid to it. Note: a bunch of repeat code to what is in
        # the build_corner function


        #     r1 (float): Radius of the inner hole plus wall thickness
        #     r2 (float): Diameter of the bolt hole
        #     xx2, yy2 (float): Position of the corners hole
        #     nb (int): Number of corners.  2 or 3
        #     lines : ref to the lines list 
        xx2 = pcr + offset
        yy2 = 0
        d = hypot(xx2, yy2)
        theta = cos((r1 - r2) / d)
        theta2 = (pi / nb) - theta
        #
        if theta < 0:
            theta = pi / nb
            theta2 = 0
        #
        a = atan2(xx2, yy2) - theta
        s = sin(a)
        c = cos(a)
        bigarc1_end_x = s*r1
        bigarc1_end_y = c*r1
        if theta2 > 0:
            #big arc 1
            ang1 = atan2(bigarc1_end_y ,bigarc1_end_x)
            bigarc1_start_x = fix(r1 * cos(ang1 + (theta2 *2)))
            bigarc1_start_y = fix(r1 * sin(ang1 + (theta2 *2)))
            LOG.debug(f"Move to external start: X/y = {(bigarc1_start_x, bigarc1_start_y)} for end = {(fix(bigarc1_end_x), fix(bigarc1_end_y))}")
            LOG.debug(f"Move to external start: data to build angles:")
            LOG.debug(f"Move to external start: a = atan2{(xx2,yy2)} - {theta} = {a} : sin(a)={s} : cos(a)={c}")
            LOG.debug(f"Move to external start: angle1 = atan2{(fix(bigarc1_end_y), fix(bigarc1_end_x))} = {degrees(ang1)}, angle2 = angle1 + theta2*2 = {degrees(ang1 + (theta2 *2))}")
            LOG.debug(f"Move to external start: angle2 used to calc big arc start x/y. r1 = {r1}")
            lines.append(f"G0 X{bigarc1_start_x} Y{bigarc1_start_y}\n")
        else:
            #writer.add_polyline_2d([(s*rr1,c*rr1), ((s*rr2)+xx2, (c*rr2)+yy2)])
            lines.append(f"G0 X{fix(s*r1)} Y{fix(c*r1)}\n")
        
        start_cut(lines)
        build_corner(r1, r2, xx2, yy2, 2, lines)
        build_corner(r1, r2, -(xx2), yy2, 2, lines)
        stop_cut(lines)
    else:
        x = cos(pi/1.5) * pcr
        y = sin(pi/1.5) * pcr
        build_slot(pcr, 0, sw, bd, lines)
        build_slot(x, y, sw, bd, lines)
        build_slot(x, -y, sw, bd, lines)
        x = cos(pi/1.5) * (pcr + offset)
        y = sin(pi/1.5) * (pcr + offset)

        d = hypot(x, y)
        theta = cos((r1 - r2) / d)
        theta2 = (pi / nb) - theta
        #
        if theta < 0:
            theta = pi / nb
            theta2 = 0
        #
        a = atan2(x, y) - theta
        s = sin(a)
        c = cos(a)
        bigarc1_end_x = s*r1
        bigarc1_end_y = c*r1

        if theta2 > 0:
            #big arc 1
            ang1 = atan2(bigarc1_end_y ,bigarc1_end_x)
            bigarc1_start_x = fix(r1 * cos(ang1 + (theta2 *2)))
            bigarc1_start_y = fix(r1 * sin(ang1 + (theta2 *2)))
            LOG.debug(f"Move to external start: X/y = {(bigarc1_start_x, bigarc1_start_y)} for end = {(fix(bigarc1_end_x), fix(bigarc1_end_y))}")
            LOG.debug(f"Move to external start: data to build angles:")
            LOG.debug(f"Move to external start: a = atan2{(x,y)} - {theta} = {a} : sin(a)={s} : cos(a)={c}")
            LOG.debug(f"Move to external start: angle1 = atan2{(fix(bigarc1_end_y), fix(bigarc1_end_x))} = {degrees(ang1)}, angle2 = angle1 + theta2*2 = {degrees(ang1 + (theta2 *2))}")
            LOG.debug(f"Move to external start: angle2 used to calc big arc start x/y. r1 = {r1}")
            lines.append(f"G0 X{fix(s*r1)} Y{fix(c*r1)}\n")
            # lines.append(f"G0 X{bigarc1_start_x} Y{bigarc1_start_y}\n")
        else:
            #writer.add_polyline_2d([(s*rr1,c*rr1), ((s*rr2)+xx2, (c*rr2)+yy2)])
            lines.append(f"G0 X{fix(s*r1)} Y{fix(c*r1)}\n")

        start_cut(lines)
        build_corner(r1, r2, pcr + offset, 0, 3, lines)
        # build_corner(r1, r2, x, y, 3, lines)
        # build_corner(r1, r2, x, -y, 3, lines)
        stop_cut(lines)

