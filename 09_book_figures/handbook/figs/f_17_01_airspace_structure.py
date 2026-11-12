"""Figure 17-1. Airspace blocks in a flight information region, seen from the side. A diorama of glass: the front face of each block is its cross-section (the same blocks as the old
figure: the FIR, the control area above its floor, the terminal control area with its floors stepping up away from the aerodrome, the control zone from the surface, the airway with
its floor above the ground, and the uncontrolled air between them, in grey), the blocks run back a little so that they read as slabs of translucent glass (a lit top, a darker
side, a gloss and a white edge, as in Figure 14-9), and they stand on a slab of the desert (figs/terrain.py) with the two aerodromes, the tower and a few trees on its top face.
The aeroplanes of the model are inside: the IFR one in the airway and the VFR one under its floor. The ten numbered callouts of the old figure are kept, in the same order and meaning
(figs/scene.py makes the pieces, figs/h_a2.py the tower)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 372
SX, SY = 0.96, 0.90                  # the old figure's x and y are squeezed a little to leave room for the depth
X0, Y0 = 10.0, 46.0                  # where the old (14, 26) goes
DX, DY = 30.0, -24.0                 # the depth of a block: it runs up and to the right
SOIL = 30.0                          # the thickness of the slab of ground at the foot of the front
U = "a171"

GROUND_Y_OLD = 330.0


def X(x):
    return X0 + (x - 14.0) * SX


def Y(y):
    return Y0 + (y - 26.0) * SY


def P(x, y):
    return (X(x), Y(y))


def B(p):
    """The same point at the back of the block."""
    return (p[0] + DX, p[1] + DY)


# the ground, as a picture of the desert laid on the top face of the slab: its plan is WT x HP units, mapped to the parallelogram in front of the blocks' feet
WT = (626 - 14) * SX
HP = 36.0
terrain.ensure("terrain-17-01", size=(int(WT * 4) + 4, int(HP * 4)), seed=171, kind="plain", features=("wadis", "tracks"), veil=0.08, soft=2.2)


def poly_pts(points_old):
    return [P(x, y) for x, y in points_old]


def glass(uid, points_old, c1, c2, opacity):
    """The cross-section of a block: a tinted pane (shaded from c1 above to c2 below)."""
    return S.air(uid, poly_pts(points_old), c1, c2, opacity)


def side_face(a_old, b_old, colour, opacity=0.6, uid=None):
    """A face of a block seen at its side (a right-hand face or a top face): the edge a-b and the same edge at the back."""
    a, b = P(*a_old), P(*b_old)
    pts_ = [a, b, B(b), B(a)]
    return S.face(pts_, colour, opacity, "#FFFFFF", 0.65, 0.8)


def gloss(uid, points_old):
    """The sheen of glass over a front face: a diagonal gradient from the upper left, and the white edge."""
    pts_ = poly_pts(points_old)
    xs, ys = [p[0] for p in pts_], [p[1] for p in pts_]
    return (f'<defs>{S.gradient(uid, [(0, "#FFFFFF", 0.46), (0.45, "#FFFFFF", 0.04), (1, "#FFFFFF", 0.0)], 0, 0, 0.35, 1)}</defs><polygon points="{S.pts(pts_)}" fill="url(#{uid})"/>'
            f'<polygon points="{S.pts(pts_)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="1.5" stroke-linejoin="round"/>')


# ------------------------------------------------------------------------------------------------------------------ the blocks, in old coordinates
FIR = [(14, 26), (626, 26), (626, 330), (14, 330)]
CTRL_AREA = [(14, 26), (626, 26), (626, 112), (14, 112)]
TMA = [(70, 112), (330, 112), (330, 190), (300, 190), (300, 222), (250, 222), (250, 262), (150, 262), (150, 222), (100, 222), (100, 190), (70, 190)]
CTR = [(150, 262), (250, 262), (250, 330), (150, 330)]
AIRWAY = [(330, 152), (626, 152), (626, 190), (330, 190)]


def grey_path():
    """The uncontrolled air: everything below the control area's floor that is not a block (a path with the blocks cut out)."""
    def d(points):
        return "M " + " L ".join(f"{S.n(x)},{S.n(y)}" for x, y in poly_pts(points)) + " Z"
    return d([(14, 112), (626, 112), (626, 330), (14, 330)]) + " " + d(TMA) + " " + d(CTR) + " " + d(AIRWAY)


def ground():
    """The slab of desert the blocks stand on: the desert from above on its top face (with the two aerodromes), the soil in section along its front and its right side."""
    xl, yb = P(14, GROUND_Y_OLD)
    xr = X(626)
    Wt = xr - xl
    # the matrix that lays the plan (0..Wt across, 0..HP deep, the front at HP) on the parallelogram that rises to the back
    m = f"matrix(1 0 {S.n(-DX / HP)} {S.n(-DY / HP)} {S.n(xl + DX)} {S.n(yb + DY)})"
    out = [f'<defs><clipPath id="{U}gc"><rect x="0" y="0" width="{S.n(Wt)}" height="{S.n(HP)}"/></clipPath></defs>',
           f'<polygon points="{S.pts([(xl, yb), (xr, yb), (xr + DX, yb + DY), (xl + DX, yb + DY)])}" fill="#E4D3A8"/>',
           f'<g transform="{m}"><g clip-path="url(#{U}gc)">']
    return out, Wt, yb, xl


def runway_plan(x_old0, x_old1, depth, xl, Wt):
    """A runway on the top face, in plan coordinates (the front of the top face is at HP)."""
    x0, x1 = X(x_old0) - xl, X(x_old1) - xl
    y = HP * (1 - depth)
    return (f'<rect x="{S.n(x0 - 1.2)}" y="{S.n(y - 4.4)}" width="{S.n(x1 - x0 + 2.4)}" height="8.8" fill="#D3C093" opacity="0.7"/>'
            f'<rect x="{S.n(x0)}" y="{S.n(y - 3.2)}" width="{S.n(x1 - x0)}" height="6.4" fill="#3E4553"/>'
            f'<line x1="{S.n(x0 + 3)}" y1="{S.n(y)}" x2="{S.n(x1 - 3)}" y2="{S.n(y)}" stroke="#F4F1E8" stroke-width="0.8" stroke-dasharray="3 2.4"/>')


def ground_layers():
    parts, Wt, yb, xl = ground()
    out = list(parts)
    out.append({"name": "terrain-17-01", "at": [Wt / 2, HP / 2], "width": Wt})
    out.append(runway_plan(176, 236, 0.45, xl, Wt) + runway_plan(470, 520, 0.45, xl, Wt))
    out.append("</g></g>")
    # the soil along the front and the right side of the slab
    xr = X(626)
    soil = [(xl, yb), (xr, yb), (xr, yb + SOIL), (xl, yb + SOIL)]
    side = [(xr, yb), (xr + DX, yb + DY), (xr + DX, yb + DY + SOIL), (xr, yb + SOIL)]
    strata = "".join(f'<path d="M {S.n(xl)},{S.n(yb + SOIL * f)} Q {S.n(xl + Wt * 0.3)},{S.n(yb + SOIL * f + 2.4)} {S.n(xl + Wt * 0.6)},{S.n(yb + SOIL * f - 1.4)} T {S.n(xr)},{S.n(yb + SOIL * f + 1.0)}" fill="none" stroke="#6E5532" stroke-opacity="0.28" stroke-width="{S.n(0.8 + 0.5 * i)}"/>'
                     for i, f in enumerate((0.34, 0.58, 0.8)))
    grit = "".join(f'<ellipse cx="{S.n(xl + 10 + i * 24.5 + (i % 3) * 4)}" cy="{S.n(yb + SOIL * (0.28 + 0.22 * (i % 3)))}" rx="{2 + i % 3}" ry="1.1" fill="#7B6238" opacity="0.38"/>' for i in range(24))
    out.append(f'<defs>{S.gradient(U + "so", [(0, "#DAC38E"), (0.5, "#C4A870"), (1, "#8E7447")])}{S.gradient(U + "ss", [(0, "#B99C63"), (1, "#6C5533")])}</defs>'
               f'<polygon points="{S.pts(side)}" fill="url(#{U}ss)"/><polygon points="{S.pts(soil)}" fill="url(#{U}so)"/>{strata}{grit}'
               f'<line x1="{S.n(xl)}" y1="{S.n(yb)}" x2="{S.n(xr)}" y2="{S.n(yb)}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="1.2"/>'
               f'<polygon points="{S.pts(soil)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.2" stroke-linejoin="round"/>')
    return out


def trees():
    """A few palms and acacias standing on the top face of the ground, behind the aerodromes."""
    out = []
    xl, yb = P(14, GROUND_Y_OLD)
    for i, (xo, depth, kind, size) in enumerate([(40, 0.62, "p", 10), (98, 0.72, "a", 8), (296, 0.7, "p", 9.5), (338, 0.55, "a", 7.5), (410, 0.74, "p", 9.5), (440, 0.62, "a", 8), (562, 0.7, "p", 10), (592, 0.55, "a", 7.5)]):
        x = X(xo)
        y = yb + DY * depth
        x += DX * depth
        out.append(S.palm(x, y, size * 1.9, 0.1, 30 + i) if kind == "p" else S.acacia(x, y, size * 1.4, 30 + i))
    return "".join(out)


def tower():
    xl, yb = P(14, GROUND_Y_OLD)
    x, y = X(163), yb + DY * 0.42
    return H.tower(U + "tw", x + DX * 0.42, y, 0.62)


# ------------------------------------------------------------------------------------------------------------------ the figure
def backdrop():
    top_back = [B(P(14, 26)), B(P(626, 26)), B(P(626, GROUND_Y_OLD)), B(P(14, GROUND_Y_OLD))]
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#DCE8F5")])}{S.gradient(U + "bk", [(0, "#EAF2FC"), (1, "#C9DBEF")])}'
            f'<filter id="{U}sh" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="7"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<ellipse cx="{S.n(X(320) + DX / 2)}" cy="{S.n(Y(330) + SOIL + 8)}" rx="{S.n(300 * SX)}" ry="9" fill="#16335F" opacity="0.22" filter="url(#{U}sh)"/>'
            f'<polygon points="{S.pts(top_back)}" fill="url(#{U}bk)"/>'
            f'<polygon points="{S.pts([P(14, 26), B(P(14, 26)), B(P(14, GROUND_Y_OLD)), P(14, GROUND_Y_OLD)])}" fill="#D3E0F1" opacity="0.85"/>')


def volumes():
    out = []
    # the uncontrolled air, in grey: the cross-section and its right-hand side
    out.append(f'<defs>{S.gradient(U + "gy", [(0, "#DADEE4"), (1, "#C3C9D2")])}</defs>'
               f'<path d="{grey_path()}" fill="url(#{U}gy)" fill-opacity="0.5" fill-rule="evenodd"/>')
    out.append(side_face((626, 112), (626, 330), "#9AA3B0", 0.55))
    # the control area above its floor
    out.append(side_face((14, 26), (626, 26), "#D5E5FB", 0.8))
    out.append(side_face((626, 26), (626, 112), "#7FA2DE", 0.6))
    out.append(glass(U + "ca", CTRL_AREA, "#C9DCF8", "#A8C4F0", 0.64))
    return "".join(out)


def blocks():
    out = []
    # the sides of the blocks: the right-hand faces and the top of the airway
    for a, b in (((330, 112), (330, 152)), ((300, 190), (300, 222)), ((250, 222), (250, 262))):
        out.append(side_face(a, b, "#4E78CC", 0.62))
    out.append(side_face((250, 262), (250, 330), "#2E58B2", 0.66))
    out.append(side_face((330, 152), (626, 152), "#B7CEF6", 0.8))
    out.append(side_face((626, 152), (626, 190), "#3F69C0", 0.66))
    # the cross-sections
    out.append(glass(U + "tm", TMA, "#9DBBF1", "#6B93E4", 0.66))
    out.append(glass(U + "ct", CTR, "#6A93E8", "#3C6BD4", 0.72))
    out.append(glass(U + "aw", AIRWAY, "#8EAFF0", "#5C8CE8", 0.68))
    return "".join(out)


def lines():
    """The floor of the control area (dotted), FL150 (dashed, red), the dashed outline of the FIR, and the words that the old figure had."""
    p = P
    out = []
    # the floor of the control area
    out.append(f'<line x1="{S.n(p(14, 112)[0])}" y1="{S.n(p(14, 112)[1])}" x2="{S.n(p(626, 112)[0])}" y2="{S.n(p(626, 112)[1])}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2"/>'
               f'<line x1="{S.n(p(14, 112)[0])}" y1="{S.n(p(14, 112)[1])}" x2="{S.n(p(626, 112)[0])}" y2="{S.n(p(626, 112)[1])}" stroke="#1D4ED8" stroke-width="1.4" stroke-dasharray="3 3"/>')
    # FL150
    out.append(f'<line x1="{S.n(p(14, 70)[0])}" y1="{S.n(p(14, 70)[1])}" x2="{S.n(p(626, 70)[0])}" y2="{S.n(p(626, 70)[1])}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.6"/>'
               f'<line x1="{S.n(p(14, 70)[0])}" y1="{S.n(p(14, 70)[1])}" x2="{S.n(p(626, 70)[0])}" y2="{S.n(p(626, 70)[1])}" stroke="#B91C1C" stroke-width="1.8" stroke-dasharray="8 5"/>')
    # the FIR: a dashed outline round the whole front, and the edges that run back
    x0, y0 = p(14, 26)
    x1, y1 = p(626, GROUND_Y_OLD)
    out.append(f'<rect x="{S.n(x0)}" y="{S.n(y0)}" width="{S.n(x1 - x0)}" height="{S.n(y1 - y0)}" rx="4" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.4"/>'
               f'<rect x="{S.n(x0)}" y="{S.n(y0)}" width="{S.n(x1 - x0)}" height="{S.n(y1 - y0)}" rx="4" fill="none" stroke="#1D4ED8" stroke-width="1.9" stroke-dasharray="10 6"/>')
    out.append(f'<polyline points="{S.pts([(x1, y0), (x1 + DX, y0 + DY), (x1 + DX, y1 + DY)])}" fill="none" stroke="#1D4ED8" stroke-opacity="0.7" stroke-width="1.3" stroke-dasharray="6 4"/>'
               f'<polyline points="{S.pts([(x0, y0), (x0 + DX, y0 + DY), (x1 + DX, y0 + DY)])}" fill="none" stroke="#1D4ED8" stroke-opacity="0.7" stroke-width="1.3" stroke-dasharray="6 4"/>')
    return "".join(out)


def words():
    def word(s_, x_old, y_old, colour, height=11.5):
        x, y = P(x_old, y_old)
        return H.glyph_text(s_, x, y, height, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0, spacing=0.8) + H.glyph_text(s_, x, y, height, colour, stroke=colour, stroke_width=0.35, spacing=0.8)
    return "".join([word("FIR", 70, 46, "#1D4ED8", 12), word("FL150", 586, 56, "#B91C1C", 11), word("TMA", 210, 142, "#1D4ED8", 12), word("CTR", 224, 284, "#1D4ED8", 12)])


def finish():
    """What stands in front of the objects inside the blocks: the sheen of the glass and its white edges."""
    out = []
    for i, shape in enumerate((CTRL_AREA, TMA, CTR, AIRWAY)):
        out.append(gloss(U + f"g{i}", shape))
    return "".join(out)


def aeroplanes():
    ifr = {"name": "sprite-side", "at": [X(599) + 1, Y(170)], "width": 42, "tint": "#2F66D6", "tint_strength": 0.66, "outline": {"width": 0.5, "colour": "#13296B", "opacity": 0.8}}
    vfr = {"name": "sprite-side", "at": [X(389), Y(258)], "width": 44, "tint": "#202B3C", "tint_strength": 0.78, "outline": {"width": 0.5, "colour": "#0B1220", "opacity": 0.85},
           "shadow": {"dx": 0.8, "dy": 1.6, "blur": 1.4, "opacity": 0.22}}
    arrow = S.ribbon(U + "ar", [(X(392), Y(238)), (X(392), Y(222)), (X(392), Y(200))], width=6, c1="#047857", c2="#34C08A", head=2.0)
    return ifr, vfr, arrow


def callouts():
    c = S.callout
    out = []
    for k, (x, y) in {1: P(36, 47), 2: P(540, 53), 4: P(166, 150), 5: P(450, 171), 6: P(60, 252), 7: P(392, 296), 8: P(495, 350), 9: P(206, 350), 10: P(110, 94)}.items():
        out.append(c(k, x, y))
    x, y = P(560, 232)
    out.append(c(6, x, y))
    (x, y), (tx, ty) = P(118, 296), P(152, 292)        # the control zone is small: its number stands outside, with a leader
    out.append(c(3, x, y, tx, ty))
    return "".join(out)


def layers():
    ifr, vfr, arrow = aeroplanes()
    return [backdrop(), *ground_layers(), trees(), volumes(), blocks(), tower(), vfr, arrow, ifr, finish(), lines(), words(), callouts()]


def plate():
    return {
        "id": "fig-17-01-airspace-structure",
        "replaces": "fig-17-01-airspace-structure.svg",
        "book_file": "plate-17-01-airspace-structure.jpg",
        "caption": "Figure 17-1. Airspace blocks in a flight information region, seen from the side",
        "desc": "Figure 17-1. Airspace blocks in a flight information region, seen from the side",
        "legend": [
            "The FIR: flight information and alerting service throughout.",
            "FL 150: at and above it, every flight is IFR [[§91.77]].",
            "A control zone, from the surface, around the controlled aerodrome (9).",
            "A terminal control area, its floors stepping up away from the aerodrome.",
            "An airway, with an IFR aircraft in it; its floor is above the ground.",
            "Uncontrolled airspace (grey).",
            "A VFR aeroplane under the airway's floor, outside every controlled block.",
            "An aerodrome without a control zone.",
            "A controlled aerodrome with a tower.",
            "A control area over the higher levels; its floor is the dashed line.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-01-airspace-structure.svg", "blank": True, "layers": layers()},
    }
