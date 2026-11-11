"""Figures of the handbook that are drawings, not renders: here the airfoil (Figure 5-2), drawn from the NACA 2412
section the wing of the model is built from (08_realistic_digital_twin/blender/c172/profiles.py), so that the section is
a real cambered one, not a lens, and the camber line is the one of that section.

draw(plate, glyphs, spec) -> the SVG text. The numbers are those of the book's legend; the same drawing helpers as the
renders' callouts (plate_draw.py)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "08_realistic_digital_twin", "blender"))
sys.path.insert(0, HERE)
from c172.profiles import naca4                                    # noqa: E402
from plate_draw import colour, num, arrow, marker, leader, glyph  # noqa: E402

CHORD = 372.0          # units
ALPHA = 13.0           # degrees: more than the wing flies at, so that the angle reads on the page


def to_screen(le, d, n, u, v):
    return (le[0] + u * d[0] + v * n[0], le[1] + u * d[1] + v * n[1])


def draw(plate, glyphs, spec):
    cw, ch = plate["canvas"]
    a = math.radians(ALPHA)
    d = (math.cos(a), math.sin(a))                  # along the chord, toward the trailing edge (right and a little down)
    n = (math.sin(a), -math.cos(a))                 # the way up from the chord
    le = (190.0, 172.0)
    ink = colour("ink")
    bg = spec["backgrounds"][plate["background"]]
    top, bottom = bg["top"], bg["bottom"]

    section = [to_screen(le, d, n, x * CHORD, y * CHORD) for x, y in naca4("2412", n=80)]
    outline = "M" + " L".join(f"{num(x)},{num(y)}" for x, y in section) + " Z"
    # the mean camber line of NACA 2412: m = 0.02 at p = 0.4
    camber = []
    for i in range(61):
        x = i / 60.0
        yc = 0.02 / 0.4 ** 2 * (2 * 0.4 * x - x * x) if x < 0.4 else 0.02 / 0.6 ** 2 * ((1 - 0.8) + 2 * 0.4 * x - x * x)
        camber.append(to_screen(le, d, n, x * CHORD, yc * CHORD))
    camber_path = "M" + " L".join(f"{num(x)},{num(y)}" for x, y in camber)

    te = to_screen(le, d, n, CHORD, 0.0)
    ext = to_screen(le, d, n, -150.0, 0.0)                              # the chord line, extended ahead of the wing
    cp = to_screen(le, d, n, 0.30 * CHORD, 0.0)                         # the centre of pressure, a quarter to a third of the way back
    parts = []
    add = parts.append

    # relative wind: the air meets the wing from the front and moves back; arrows at the left, and the line the angle is measured from
    add(f'<line x1="30" y1="{num(le[1])}" x2="{num(le[0] - 6)}" y2="{num(le[1])}" stroke="{colour("marker")}" stroke-width="1.6" stroke-dasharray="1.5 5" stroke-linecap="round"/>')
    wind = []
    for y in (246, 288, 330):
        wind.append(arrow((24, y), (150, y), colour("marker"), 2.4, 11))
    add("".join(wind))

    # the section, with a soft body: lighter above, darker below
    add('<defs><linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F7FC"/><stop offset="1" stop-color="#A9B7CE"/></linearGradient></defs>')
    add(f'<path d="{outline}" transform="translate(3.5 5)" fill="#6F7F9C" opacity=".22"/>')
    add(f'<path d="{outline}" fill="url(#body)" stroke="{ink}" stroke-width="2.2" stroke-linejoin="round"/>')

    # chord line: through the section and extended ahead; mean camber line inside it
    add(f'<line x1="{num(ext[0])}" y1="{num(ext[1])}" x2="{num(te[0])}" y2="{num(te[1])}" stroke="{ink}" stroke-width="1.6" stroke-dasharray="6 4.5"/>')
    add(f'<path d="{camber_path}" fill="none" stroke="#C8651B" stroke-width="2.2" stroke-linecap="round"/>')

    # angle of attack: the arc between the relative wind line and the chord line extended
    r = 128.0
    arc_a = (le[0] - r, le[1])
    arc_b = (le[0] - r * math.cos(a), le[1] - r * math.sin(a))
    add(f'<path d="M{num(arc_a[0])},{num(arc_a[1])} A{num(r)},{num(r)} 0 0 1 {num(arc_b[0])},{num(arc_b[1])}" fill="none" stroke="{ink}" stroke-width="1.8"/>')
    add(glyph("α", le[0] - r - 17, le[1] - 12, 19, fill=ink))

    # flight path: opposite the relative wind
    add(arrow((372, 52), (228, 52), ink, 2.8, 13))

    # lift perpendicular to the relative wind (straight up), drag along it (back); both from the centre of pressure
    lift_head = (cp[0], cp[1] - 116)
    drag_head = (cp[0] + 124, cp[1])
    add(arrow(cp, lift_head, colour("lift"), 3.6, 14))
    add(arrow(cp, drag_head, colour("drag"), 3.6, 14))
    add(f'<circle cx="{num(cp[0])}" cy="{num(cp[1])}" r="4.2" fill="#FFFFFF" stroke="{ink}" stroke-width="1.5"/>')

    # callouts, numbered as the book's legend: 1 leading edge, 2 trailing edge, 3 chord line (extended ahead), 4 mean camber
    # line, 5 relative wind, 6 angle of attack, 7 flight path, 8 lift, 9 drag
    def call(k, at, pos):
        parts.append(leader(pos, at))
        parts.append(marker(k, pos[0], pos[1]))
    call(1, le, (le[0] - 30, le[1] + 52))
    call(2, te, (te[0] + 36, te[1] + 40))
    call(3, ext, (ext[0] - 8, ext[1] - 38))
    camber_pt = camber[40]
    call(4, camber_pt, (camber_pt[0] + 26, camber_pt[1] + 76))
    call(5, (150, 288), (186, 288))
    call(6, (le[0] - r * math.cos(a / 2), le[1] - r * math.sin(a / 2)), (108, 208))
    add(marker(7, 204, 52))
    add(marker(8, lift_head[0] + 26, lift_head[1] + 2))
    add(marker(9, drag_head[0] + 24, drag_head[1] - 4))

    gradient = (f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgb({top[0]},{top[1]},{top[2]})"/>'
                f'<stop offset="1" stop-color="rgb({bottom[0]},{bottom[1]},{bottom[2]})"/></linearGradient></defs>')
    number = "-".join(plate["id"].split("-")[1:3])          # the book's figures name themselves by number: one file serves both editions
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}">',
        f"  <title>{number}</title>", f"  <desc>{number}</desc>", f"  {gradient}",
        f'  <rect width="{cw}" height="{ch}" fill="url(#sky)"/>',
        "  " + "".join(parts), "</svg>", ""])
