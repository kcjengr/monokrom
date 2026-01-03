from math import cos, sin, tan, atan, atan2, asin, degrees, radians, sqrt, hypot, pi
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)


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

    
    