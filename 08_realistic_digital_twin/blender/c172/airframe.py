"""Exterior airframe: fuselage (with window/door cut-outs), wings, control surfaces,
empennage, struts and exterior details. All dimensions see units.py for status."""
import math
import bpy
import bmesh
from mathutils import Vector

from . import units as U
from .units import fs, bl, wl, IN
from .shapes import (parent_keep, new_bm, loft, extrude_profile, revolve, tube, cylinder, box, bezier, obj_from_bm, empty,
                     add_subsurf, add_boolean, add_solidify, add_edge_split, add_bevel, naca4, airfoil_interp,
                     split_airfoil, superellipse, rounded_rect, ellipse, resample_loop, interp_table, smoothstep)
from .profiles import interp_pchip, interp_linear

K_RING = 40          # points around fuselage sections
K_WING = 72          # points around wing box sections
K_CTRL = 48          # points around control-surface sections

# FS(in) -> half width, z bottom, z top, ring centre z, n_top, n_bottom   (build frame, see units.wl)
# Status: estimated. Top and bottom lines follow the photo-profile side elevation (cowl deck 57.8 in,
# belly 16.7 in at FS 45, rear-window roof line down to 52.2 in at FS 128, tailcone to the rudder post);
# widths are from under-wing photographs: parallel under the wing, then a straight taper to the tail.
# The cabin is slab-sided with a flat belly and tight lower corners (n_bottom 4, from a photograph taken
# from below), so the door sill is close to full width; the tailcone is oval.
FUS_TABLE = [
    (0,   0.490, 0.878, 1.843, 1.42, 2.6, 3.0),
    (4,   0.505, 0.868, 1.862, 1.42, 2.6, 3.2),
    (10,  0.522, 0.852, 1.935, 1.40, 2.5, 3.5),
    (16,  0.535, 0.840, 2.000, 1.38, 3.0, 3.8),
    (22,  0.540, 0.828, 2.045, 1.36, 3.6, 4.0),
    (25,  0.540, 0.822, 2.060, 1.36, 4.0, 4.0),
    (30,  0.540, 0.812, 2.030, 1.35, 4.2, 4.0),
    (36,  0.540, 0.804, 2.005, 1.34, 4.8, 4.0),
    (60,  0.537, 0.805, 2.000, 1.34, 5.0, 4.0),
    (76,  0.520, 0.830, 2.000, 1.34, 4.8, 4.0),
    (88,  0.495, 0.848, 2.000, 1.34, 4.4, 3.8),
    (96,  0.472, 0.858, 1.950, 1.35, 3.5, 3.4),
    (108, 0.435, 0.874, 1.860, 1.35, 2.9, 2.9),
    (120, 0.395, 0.895, 1.765, 1.33, 2.5, 2.5),
    (128, 0.368, 0.910, 1.713, 1.31, 2.35, 2.3),
    (150, 0.300, 0.939, 1.681, 1.30, 2.25, 2.2),
    (180, 0.215, 0.995, 1.636, 1.31, 2.2, 2.2),
    (200, 0.165, 1.035, 1.606, 1.315, 2.2, 2.2),
    (220, 0.115, 1.066, 1.573, 1.315, 2.2, 2.2),
    (240, 0.050, 1.124, 1.543, 1.33, 2.0, 2.0),
    (247, 0.022, 1.168, 1.552, 1.36, 2.0, 2.0),
]
FUS_STATIONS = [0, 2, 4, 7, 10, 13, 16, 19, 22, 25, 28, 32, 36, 42, 48, 54, 60, 68, 76, 84, 88, 92, 96, 100, 104, 108, 112,
                116, 120, 124, 128, 136, 145, 160, 180, 200, 215, 228, 236, 240, 244, 247]
FUS_END_FS = FUS_STATIONS[-1]          # rudder post; the rudder carries the outline aft of here
FUS_UV_END_FS = 283                    # texture v = 1 (kept from the first layout so the livery atlas stays valid)

def fus_ring(s, k=K_RING):
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    return [Vector((x, fs(s), z)) for x, z in superellipse(w, zc - zb, zt - zc, zc, nt, nb, k)]

def fus_top_z(s):
    return interp_pchip(FUS_TABLE, s)[2]

def fus_half_width(s):
    return interp_pchip(FUS_TABLE, s)[0]

def fus_half_width_at(s, z):
    """Half width of the skin at station s (in) and height z (m); 0 above or below the section."""
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    if not zb < z < zt:
        return 0.0
    t, n = ((z - zc) / (zt - zc), nt) if z >= zc else ((zc - z) / (zc - zb), nb)
    return w * (1 - t ** n) ** (1 / n)

def fus_surface_z(s, x, top=False):
    """Skin height at station s (in) and lateral x (m): bottom of the section, or top."""
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    t = min(1.0, abs(x) / w)
    if top:
        return zc + (zt - zc) * (1 - t ** nt) ** (1 / nt)
    return zc - (zc - zb) * (1 - t ** nb) ** (1 / nb)

# ----------------------------------------------------------------------------- cutters

def _cutter(ctx, name, pts2d, axis_u, axis_v, origin, depth_axis, d0, d1):
    bm = new_bm()
    extrude_profile(bm, pts2d, Vector(axis_u), Vector(axis_v), origin, Vector(depth_axis), d0, d1, smooth_sides=False)
    ob = obj_from_bm("_cut_" + name, bm, ctx.cutters, smooth=False)
    ob.hide_render = True
    ob.display_type = "WIRE"
    return ob

def _side_polygon(pts_fs_z):
    """(FS in, z m) -> (y, z) tuples."""
    return [(fs(s), z) for s, z in pts_fs_z]

def _round_corners(poly, r=0.03, n=4):
    """Round every corner of a closed polygon with radius r (simple arc insertion)."""
    out = []
    m = len(poly)
    for i in range(m):
        p0 = Vector(poly[i - 1]); p1 = Vector(poly[i]); p2 = Vector(poly[(i + 1) % m])
        d0 = (p0 - p1).normalized(); d2 = (p2 - p1).normalized()
        rr = min(r, (p0 - p1).length * 0.45, (p2 - p1).length * 0.45)
        a = p1 + d0 * rr; b = p1 + d2 * rr
        for j in range(n + 1):
            t = j / n
            q = a * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + b * t * t
            out.append((q.x, q.y))
    return out

def _inset(poly, d):
    """Move every edge of a convex polygon inward by d."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sign = 1.0 if area > 0 else -1.0                     # counter-clockwise: the interior is left of each edge
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        length = math.hypot(ex, ey)
        nx, ny = -ey / length * sign, ex / length * sign
        lines.append(((x0 + nx * d, y0 + ny * d), (ex, ey)))
    out = []
    for i in range(n):
        (p, e), (q, f) = lines[i - 1], lines[i]
        t = ((q[0] - p[0]) * f[1] - (q[1] - p[1]) * f[0]) / (e[0] * f[1] - e[1] * f[0])
        out.append((p[0] + e[0] * t, p[1] + e[1] * t))
    return out

# Glazing and door outlines, side elevation in (FS in, WL in). Status: estimated (photo-profile and
# ramp photographs): the side windows are only about 13 in tall, with their sills at the height of the
# propeller axis; the front door post leans back at about 47 degrees; the windshield wraps round the
# sides to that post, its lower edge dropping from the cowl deck toward the post; the rear window wraps
# over the sloping back of the cabin and its lower edge is level with the start of the dorsal fin.
SILL_WL, WINDOW_TOP_WL = 48.5, 61.6
DOOR = [(17.5, 20.9), (55.0, 20.9), (55.0, 62.6), (31.5, 63.4), (18.0, 48.6), (17.5, 44.3)]
DOOR_WINDOW = [(21.5, SILL_WL), (52.3, SILL_WL), (52.3, 61.6), (34.4, 62.2)]
REAR_SIDE_WINDOW = [(58.5, SILL_WL), (91.0, SILL_WL), (85.5, WINDOW_TOP_WL), (58.5, WINDOW_TOP_WL)]
REAR_WINDOW = [(94.5, 52.8), (128.5, 52.8), (128.5, 55.0), (94.5, 68.0)]      # everything above its lower edge
# Windshield: everything ahead of the door post (2 in ahead of the door's sloping edge), above a lower
# edge that leaves the cowl deck at FS 3.2 and meets the post at WL 52, and below a top edge that
# reaches the roof at the wing leading edge (FS 24.8). The other two corners lie outside the hull.
WINDSHIELD = [(-3.0, 60.76), (19.1, 52.0), (30.2, 64.2), (8.0, 72.97), (-3.0, 76.0)]
DOOR_GAP = 0.004            # the doors are this much smaller than their openings all round (m)

def window_cutters(ctx):
    """Return dict of cutter objects for every glazed opening and the doors."""
    C = {}
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
    def side(points):
        return [(fs(s), wl(w)) for s, w in points]
    door = _round_corners(side(DOOR), r=0.04)
    door_fit = _round_corners(_inset(side(DOOR), DOOR_GAP), r=0.04 - DOOR_GAP)
    door_win = _round_corners(side(DOOR_WINDOW), r=0.035)
    rear_win = _round_corners(side(REAR_SIDE_WINDOW), r=0.045)
    for name, sgn in (("L", 1), ("R", -1)):
        C["door_" + name] = _cutter(ctx, "door_" + name, door, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["door_fit_" + name] = _cutter(ctx, "door_fit_" + name, door_fit, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["door_win_" + name] = _cutter(ctx, "door_win_" + name, door_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["rear_win_" + name] = _cutter(ctx, "rear_win_" + name, rear_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
    # windshield and rear window: side-profile prisms cut right across the fuselage
    C["windshield"] = _cutter(ctx, "windshield", _round_corners(side(WINDSHIELD), r=0.03), Y, Z, (0, 0, 0), X, -1.0, 1.0)
    C["rear_window"] = _cutter(ctx, "rear_window", _round_corners(side(REAR_WINDOW), r=0.012), Y, Z, (0, 0, 0), X, -1.0, 1.0)
    return C

# ----------------------------------------------------------------------------- fuselage

def build_fuselage(ctx):
    M = ctx.mats
    parent = ctx.groups["AIRFRAME"]
    y0, y1 = fs(0), fs(FUS_UV_END_FS)
    rings = [fus_ring(s) for s in FUS_STATIONS]
    uv_v = [(fs(s) - y0) / (y1 - y0) for s in FUS_STATIONS]
    cut = window_cutters(ctx)
    ctx.cutter_objects = cut

    def shell(name, thickness=0.014):
        """Closed loft -> subdivision -> thin skin. Booleans see a closed mesh as a solid, so
        the skin must be solidified BEFORE any cut, otherwise the cabin volume is solid."""
        bm = new_bm()
        loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v)
        # crease both end rings: without it the subdivision rounds the firewall end and opens a gap behind the cowl
        crease = bm.edges.layers.float.new("crease_edge")
        ends = (rings[0][0].y, rings[-1][0].y)
        for e in bm.edges:
            if any(all(abs(v.co.y - y) < 1e-6 for v in e.verts) for y in ends):
                e[crease] = 1.0
        ob = obj_from_bm(name, bm, ctx.col, mat=M["fuselage"])
        add_subsurf(ob, ctx.subsurf)
        add_solidify(ob, thickness)
        return ob

    def crisp(ob):
        """Hard shading along the cut edges of an opening (added after the booleans)."""
        add_edge_split(ob, 50)

    # main shell with every opening removed
    fus = shell("AIRFRAME.fuselage")
    parent_keep(fus, parent)
    for key in ("door_R", "door_L", "rear_win_R", "rear_win_L", "windshield", "rear_window"):
        add_boolean(fus, cut[key], "DIFFERENCE", "cut_" + key)
    crisp(fus)
    ctx.tag(fus, "AIRFRAME", "Fuselage", "جسم الطائرة", status="estimated",
            note="Envelope from POH Fig 1-1; cross-sections estimated from photographs")

    # glazing: intersection of the same shell with the cutters
    def glass(name, key, parent_ob, label_en, label_ar):
        g = shell(name, thickness=0.005)
        add_boolean(g, cut[key], "INTERSECT", "glass")
        crisp(g)
        g.data.materials.clear(); g.data.materials.append(M["glass"])
        parent_keep(g, parent_ob)
        ctx.tag(g, "AIRFRAME", label_en, label_ar, status="estimated", kind="glass")
        return g

    glass("AIRFRAME.windshield", "windshield", fus, "Windshield (acrylic)", "الزجاج الأمامي")
    glass("AIRFRAME.rear_window", "rear_window", fus, "Rear window", "النافذة الخلفية")
    glass("AIRFRAME.window_rear_R", "rear_win_R", fus, "Right rear side window", "النافذة الجانبية الخلفية اليمنى")
    glass("AIRFRAME.window_rear_L", "rear_win_L", fus, "Left rear side window", "النافذة الجانبية الخلفية اليسرى")
    # (cutter names already follow +x = left)

    # doors: shell ∩ door cutter, minus the window; hinge at the A-pillar
    for side, sgn in (("L", 1), ("R", -1)):
        hinge = Vector((sgn * (fus_half_width(DOOR[0][0]) - 0.01), fs(DOOR[0][0]), wl(34.0)))
        d = shell(f"AIRFRAME.door_{side}")
        add_boolean(d, cut["door_fit_" + side], "INTERSECT", "door")
        add_boolean(d, cut["door_win_" + side], "DIFFERENCE", "win")
        crisp(d)
        # move the mesh so the pivot is the hinge line
        for v in d.data.vertices:
            v.co -= hinge
        d.location = hinge
        parent_keep(d, parent)
        ctx.tag(d, "AIRFRAME", f"{'Left' if sgn > 0 else 'Right'} cabin door", "باب المقصورة " + ("الأيسر" if sgn > 0 else "الأيمن"),
                status="estimated", hinge_axis="z", hinge_sign=sgn, range_deg=[0, 65], animate="door")
        glass(f"AIRFRAME.door_window_{side}", "door_win_" + side, d, f"{'Left' if sgn > 0 else 'Right'} door window", "نافذة الباب " + ("الأيسر" if sgn > 0 else "الأيمن"))
        # door handle
        bm = new_bm()
        hx = sgn * fus_half_width(48); hz = wl(40.5)
        box(bm, (0.012, 0.11, 0.02), center=(hx + sgn * 0.012, fs(47), hz))
        box(bm, (0.03, 0.03, 0.03), center=(hx + sgn * 0.01, fs(51), hz))
        h = obj_from_bm(f"AIRFRAME.door_handle_{side}", bm, ctx.col, pivot=hinge, mat=M["chrome"])
        parent_keep(h, d)
        ctx.tag(h, "AIRFRAME", "Door handle", "مقبض الباب", status="estimated")
    return fus

# ----------------------------------------------------------------------------- wings

DIH = math.radians(U.ref("dihedral_deg"))
WASHOUT = math.radians(U.ref("washout_deg"))
AF_ROOT = naca4("2412", 36)
AF_TIP = naca4("0012", 36)
FLAP_XC = 0.75
AIL_XC = 0.76
ROOT_X = 0.0
# Wing strut, estimated. Both ends were placed by rendering the model from the direction of the
# photo-profile until its strut covered the strut in the photograph (the viewing angle displaces parts
# that are far from the centreline, so stations cannot be read off the photograph directly). The foot
# is on the fuselage frame under the lower front corner of the door, not on the door.
STRUT_FS = (20.5, 44.0)     # fuselage end, wing end (about 30 % chord)
STRUT_FOOT_WL = 19.2
FLAP_SPAN = (0.56, 2.52)
AIL_SPAN = (2.60, 5.24)
TIP_START = 5.30

def wing_chord(x):
    x = abs(x)
    if x <= U.TAPER_START:
        return U.ROOT_CHORD
    t = (x - U.TAPER_START) / (U.SEMISPAN - U.TAPER_START)
    return U.ROOT_CHORD + (U.TIP_CHORD - U.ROOT_CHORD) * min(1.0, t)

def wing_section(xabs, side, cut=None, k=K_WING):
    """World-space ring for the wing at |x| = xabs. cut: None (full airfoil), ('box', xc) or ('surf', xc)."""
    t = min(1.0, max(0.0, (xabs - 0.5) / (U.SEMISPAN - 0.5)))
    af = airfoil_interp(AF_ROOT, AF_TIP, t)
    if cut is None:
        prof = resample_loop(af, k)
    else:
        boxp, surfp = split_airfoil(af, cut[1])
        prof = resample_loop(boxp if cut[0] == "box" else surfp, k)
    c = wing_chord(xabs)
    inc = math.radians(1.5) - WASHOUT * t
    y_le = U.WING_LE_Y
    z_le = U.WING_Z + max(0.0, xabs - 0.5) * math.tan(DIH)
    ring = []
    for xc, yc in prof:
        # chord along +y (aft), thickness along +z, incidence rotates nose-up about the LE
        yy = xc * c; zz = yc * c
        y = y_le + yy * math.cos(inc) + zz * math.sin(inc)
        z = z_le - yy * math.sin(inc) + zz * math.cos(inc)
        ring.append(Vector((side * xabs, y, z)))
    return ring

def wing_hinge_point(xabs, side, xc):
    c = wing_chord(xabs)
    t = min(1.0, max(0.0, (xabs - 0.5) / (U.SEMISPAN - 0.5)))
    inc = math.radians(1.5) - WASHOUT * t
    af = airfoil_interp(AF_ROOT, AF_TIP, t)
    n = len(af); upper = af[: n // 2 + 1]; lower = [af[0]] + list(reversed(af[n // 2:]))
    def y_at(pts, x):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return 0.0
    zc = 0.5 * (y_at(upper, xc) + y_at(lower, xc)) * c
    yy = xc * c
    y = U.WING_LE_Y + yy * math.cos(inc) + zc * math.sin(inc)
    z = U.WING_Z + max(0.0, xabs - 0.5) * math.tan(DIH) - yy * math.sin(inc) + zc * math.cos(inc)
    return Vector((side * xabs, y, z))

def _stations(a, b, step):
    n = max(2, int(round((b - a) / step)) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def build_wing(ctx, side):
    M = ctx.mats
    name = "L" if side > 0 else "R"          # +x is the left wing
    grp = ctx.groups["WING_" + name]
    # ---- main wing box: sections through root → flap span → gap → aileron span → tip
    rings = []
    xs = []
    def add(x, cut):
        rings.append(wing_section(x, side, cut)); xs.append(x)
    for x in _stations(ROOT_X, FLAP_SPAN[0] - 0.01, 0.14): add(x, None)
    for x in _stations(FLAP_SPAN[0], FLAP_SPAN[1], 0.2): add(x, ("box", FLAP_XC))
    for x in _stations(AIL_SPAN[0], AIL_SPAN[1], 0.2): add(x, ("box", AIL_XC))
    for x in _stations(AIL_SPAN[1] + 0.04, TIP_START, 0.03): add(x, None)
    # drooped tip cap: shrink the section toward a rounded tip
    tipc = wing_chord(TIP_START)
    for i in range(1, 7):
        t = i / 6
        x = TIP_START + (U.SEMISPAN - TIP_START) * t
        ring = wing_section(TIP_START, side, None)
        cy = sum(v.y for v in ring) / len(ring); cz = sum(v.z for v in ring) / len(ring)
        sc = math.sqrt(max(1e-4, 1 - t * t))
        rr = []
        for v in ring:
            rr.append(Vector((side * x, cy + (v.y - cy) * (0.25 + 0.75 * sc), cz + (v.z - cz) * sc - 0.035 * t)))
        rings.append(rr); xs.append(x)
    uv_v = [(x - ROOT_X) / (U.SEMISPAN - ROOT_X) for x in xs]
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=False, cap_end=True, uv_v=uv_v, flip=(side < 0))
    wing = obj_from_bm(f"WING_{name}.wing", bm, ctx.col, pivot=(side * 0.5, U.WING_LE_Y, U.WING_Z), mat=M["wing"])
    parent_keep(wing, grp)
    ctx.tag(wing, "WING_" + name, f"{'Left' if side > 0 else 'Right'} wing", "الجناح " + ("الأيسر" if side > 0 else "الأيمن"),
            status="type_data", note="NACA 2412 root / 0012 tip, 1°44′ dihedral, 3° washout (type data); planform estimated")
    # ---- flap
    def surface(nm, span, xc, label_en, label_ar, mat, rng):
        rr = []; xx = []
        for x in _stations(span[0] + 0.015, span[1] - 0.015, 0.2):
            rr.append(wing_section(x, side, ("surf", xc), k=K_CTRL)); xx.append(x)
        h0 = wing_hinge_point(span[0] + 0.015, side, xc)
        h1 = wing_hinge_point(span[1] - 0.015, side, xc)
        bm = new_bm()
        loft(bm, rr, close=True, cap_start=True, cap_end=True, uv_v=[(x - span[0]) / (span[1] - span[0]) for x in xx], flip=(side < 0))
        axis = (h1 - h0); axis = axis if axis.x > 0 else -axis
        ob = obj_from_bm(nm, bm, ctx.col, pivot=h0 if side > 0 else h1, x_axis=axis, mat=mat)
        parent_keep(ob, grp)
        ctx.tag(ob, "WING_" + name, label_en, label_ar, status="estimated", hinge_axis="x", hinge_sign=-1, range_deg=rng, animate=nm.split(".")[1])
        return ob
    surface(f"WING_{name}.flap", FLAP_SPAN, FLAP_XC, f"{'Left' if side > 0 else 'Right'} flap (0°/10°/20°/30°)", "القلاب " + ("الأيسر" if side > 0 else "الأيمن"), M["control"], [0, 30])
    surface(f"WING_{name}.aileron", AIL_SPAN, AIL_XC, f"{'Left' if side > 0 else 'Right'} aileron", "الجنيح " + ("الأيسر" if side > 0 else "الأيمن"), M["control"], [-20, 15])
    # ---- strut (streamlined section) from the lower fuselage longeron to the wing underside
    lower = wing_section(2.44, side, None)
    zlow = min(v.z for v in lower)
    foot_z = wl(STRUT_FOOT_WL)
    p0 = Vector((side * (fus_half_width_at(STRUT_FS[0], foot_z) - 0.015), fs(STRUT_FS[0]), foot_z))
    p1 = Vector((side * 2.44, fs(STRUT_FS[1]), zlow + 0.015))
    d = (p1 - p0).normalized()
    # section: ellipse 0.11 × 0.040, long axis along the flight direction
    sec = ellipse(0.020, 0.055, 20)
    ax_u = Vector((0, 0, 1)).cross(d).normalized()  # lateral-ish
    ax_v = Vector((0, 1, 0))
    ax_v = (ax_v - d * ax_v.dot(d)).normalized()
    ax_u = ax_v.cross(d).normalized()
    bm = new_bm()
    ring0 = [p0 + ax_u * a + ax_v * b for a, b in sec]
    ring1 = [p1 + ax_u * a + ax_v * b for a, b in sec]
    # end fairings: slightly larger sections near the ends
    ring0b = [p0 + d * 0.12 + ax_u * a * 1.6 + ax_v * b * 1.25 for a, b in sec]
    ring1b = [p1 - d * 0.12 + ax_u * a * 1.6 + ax_v * b * 1.25 for a, b in sec]
    loft(bm, [ring0, ring0b, ring1b, ring1], close=True, cap_start=True, cap_end=True)
    strut = obj_from_bm(f"WING_{name}.strut", bm, ctx.col, pivot=p0, mat=M["paint_white"])
    add_subsurf(strut, 1)
    parent_keep(strut, grp)
    ctx.tag(strut, "WING_" + name, "Wing strut", "دعامة الجناح", status="estimated")
    # ---- wing root fairing (fillet between the wing lower surface and the cabin roof)
    rings = []
    c_root = wing_chord(0.5)
    for i in range(0, 15):
        t = i / 14
        y = U.WING_LE_Y - 0.08 + t * (c_root + 0.18)
        s_in = (y / IN) + U.FS_ORIGIN
        xr = 0.60 if 0.03 < t < 0.97 else 0.50
        lower = wing_section(xr, side, None)
        zw = min(v.z for v in lower if abs(v.y - y) < 0.12) if any(abs(v.y - y) < 0.12 for v in lower) else min(v.z for v in lower)
        zr = fus_surface_z(s_in, 0.36, top=True) if 0 <= s_in <= FUS_END_FS else 1.9
        pts = []
        for j in range(7):
            a = math.pi / 2 * j / 6
            pts.append(Vector((side * (0.36 + (xr - 0.36) * math.sin(a)), y, zr + (zw + 0.01 - zr) * (1 - math.cos(a)))))
        rings.append(pts)
    bm = new_bm()
    loft(bm, rings, close=False, cap_start=False, cap_end=False, flip=(side < 0))   # exterior faces up/outward
    fair = obj_from_bm(f"WING_{name}.root_fairing", bm, ctx.col, pivot=(side * 0.5, U.WING_LE_Y, U.WING_Z), mat=M["paint_white"])
    # recalc_face_normals picks an arbitrary side for an open strip: force the exterior (up/outward) side,
    # otherwise the single-sided paint material is back-face culled in the web viewer
    if sum(p.normal.z for p in fair.data.polygons) < 0:
        fair.data.flip_normals()
    add_subsurf(fair, 1)
    parent_keep(fair, grp)
    ctx.tag(fair, "WING_" + name, "Wing root fairing", "غطاء جذر الجناح الانسيابي", status="estimated")
    # ---- details: fuel cap, nav light, strobe, tie-down, pitot (left), stall vane (left), fuel vent (left)
    xcap = 1.17
    topz = max(v.z for v in wing_section(xcap, side, None) if abs(v.y - (U.WING_LE_Y + 0.33 * U.ROOT_CHORD)) < 0.08)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.055, 0.0), (0.055, 0.006), (0.02, 0.008), (0.0, 0.009)], axis="Z", origin=(side * xcap, U.WING_LE_Y + 0.33 * U.ROOT_CHORD, topz - 0.002), segs=24)
    cap = obj_from_bm(f"WING_{name}.fuel_cap", bm, ctx.col, pivot=(side * xcap, U.WING_LE_Y + 0.33 * U.ROOT_CHORD, topz), mat=M["bare_alu"])
    parent_keep(cap, grp)
    ctx.tag(cap, "FUEL", f"{'Left' if side > 0 else 'Right'} fuel filler cap (21.5 gal tank)", "غطاء خزان الوقود " + ("الأيسر" if side > 0 else "الأيمن"), status="poh", ref="p.1-4, 7-28")
    tip = wing_section(U.SEMISPAN - 0.02, side, None)
    tz = sum(v.z for v in tip) / len(tip); ty = U.WING_LE_Y + 0.5 * wing_chord(U.SEMISPAN)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.03, 0.0), (0.028, 0.02), (0.012, 0.035), (0.0, 0.04)], axis="X", origin=(side * (U.SEMISPAN - 0.025), ty - 0.22, tz + 0.01), segs=16)
    nav = obj_from_bm(f"WING_{name}.nav_light", bm, ctx.col, pivot=(side * U.SEMISPAN, ty, tz), mat=M["nav_red" if side > 0 else "nav_green"])
    if side < 0:
        for v in nav.data.vertices: v.co.x = -v.co.x
        nav.data.flip_normals()
        nav.matrix_world.translation = Vector((side * U.SEMISPAN, ty, tz))
    parent_keep(nav, grp)
    ctx.tag(nav, "ELECTRICAL", f"{'Red (left)' if side > 0 else 'Green (right)'} navigation light", "ضوء الملاحة " + ("الأحمر" if side > 0 else "الأخضر"), status="poh", ref="p.7-27")
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.012, 0.0), (0.012, 0.01), (0.0, 0.014)], axis="Z", origin=(side * (U.SEMISPAN - 0.13), ty + 0.05, max(v.z for v in tip) - 0.004), segs=12)
    st = obj_from_bm(f"WING_{name}.strobe", bm, ctx.col, pivot=(side * (U.SEMISPAN - 0.13), ty + 0.05, tz), mat=M["nav_white"])
    parent_keep(st, grp)
    ctx.tag(st, "ELECTRICAL", "Wingtip strobe light", "ضوء الوميض في طرف الجناح", status="poh", ref="p.7-27")
    bm = new_bm()
    tiez = min(v.z for v in wing_section(2.9, side, None))
    revolve(bm, [(0.0, 0.0), (0.018, 0.0), (0.018, -0.02), (0.0, -0.02)], axis="Z", origin=(side * 2.9, U.WING_LE_Y + 0.45 * wing_chord(2.9), tiez + 0.003), segs=12)
    tiedown = obj_from_bm(f"WING_{name}.tiedown", bm, ctx.col, pivot=(side * 2.9, U.WING_LE_Y + 0.45 * wing_chord(2.9), tiez), mat=M["steel"])
    parent_keep(tiedown, grp)
    ctx.tag(tiedown, "AIRFRAME", "Wing tie-down ring", "حلقة ربط الجناح", status="estimated")
    if side > 0:
        # pitot tube: L-shaped mast under the left wing ahead of the leading edge (POH p.7-31)
        px = 1.75
        pz = min(v.z for v in wing_section(abs(px), side, None)) - 0.01
        # a short mast about 5 in below the wing with the tube pointing forward about 6 in (estimated)
        pts = [Vector((px, U.WING_LE_Y + 0.16, pz)), Vector((px, U.WING_LE_Y + 0.16, pz - 0.115)), Vector((px, U.WING_LE_Y + 0.10, pz - 0.13)), Vector((px, U.WING_LE_Y + 0.0, pz - 0.13))]
        bm = new_bm()
        tube(bm, bezier(pts[0], pts[1], pts[2], pts[3], 14), 0.011, segs=14)
        pit = obj_from_bm("PITOT_STATIC.pitot_tube", bm, ctx.col, pivot=pts[0], mat=M["bare_alu"])
        add_subsurf(pit, 1)
        parent_keep(pit, grp)
        ctx.tag(pit, "PITOT_STATIC", "Pitot tube (heated)", "أنبوب البيتو (مسخّن)", status="poh", ref="p.7-31")
        # stall warning vane in the leading edge
        bm = new_bm()
        box(bm, (0.012, 0.03, 0.045), center=(1.05, U.WING_LE_Y + 0.004, U.WING_Z + (1.05 - ROOT_X) * math.tan(DIH) + 0.012))
        sw = obj_from_bm("AIRFRAME.stall_warning", bm, ctx.col, pivot=(1.05, U.WING_LE_Y, U.WING_Z), mat=M["black_plastic"])
        parent_keep(sw, grp)
        ctx.tag(sw, "AIRFRAME", "Stall warning horn inlet (reed type)", "فتحة إنذار الانهيار", status="poh", ref="p.7-11")
        # fuel vent below the left wing near the strut
        bm = new_bm()
        vz = min(v.z for v in wing_section(2.2, side, None))
        tube(bm, [Vector((2.2, U.WING_LE_Y + 0.05, vz)), Vector((2.2, U.WING_LE_Y + 0.05, vz - 0.12)), Vector((2.2, U.WING_LE_Y - 0.02, vz - 0.13))], 0.006, segs=10)
        vent = obj_from_bm("FUEL.vent_line", bm, ctx.col, pivot=(2.2, U.WING_LE_Y + 0.05, vz), mat=M["bare_alu"])
        parent_keep(vent, grp)
        ctx.tag(vent, "FUEL", "Fuel tank vent (left wing, interconnected)", "فتحة تهوية خزان الوقود", status="poh", ref="p.7-28")
    return wing

# ----------------------------------------------------------------------------- empennage
# Status: estimated (photo-profile). Outlines are tabulated as (FS in, WL in); wl() gives the build-frame z.

AF_TAIL = naca4("0009", 32)
STAB_SEMISPAN = U.H_TAIL_SPAN / 2
STAB_Z = wl(37.0)
STAB_TE_FS = (253.0, 247.5)             # elevator trailing edge: root, tip
STAB_CHORD = (50.0 * IN, 29.5 * IN)     # stabiliser + elevator chord: root, tip
ELEV_CHORD = (18.5 * IN, 14.0 * IN)     # elevator chord: root, tip
STAB_END = STAB_SEMISPAN - 0.17         # the elevator horn wraps round the stabiliser tip beyond this

def _span_t(xabs):
    return min(1.0, xabs / STAB_SEMISPAN)

def stab_te_y(xabs):
    return fs(STAB_TE_FS[0] + (STAB_TE_FS[1] - STAB_TE_FS[0]) * _span_t(xabs))

def stab_chord(xabs):
    return STAB_CHORD[0] + (STAB_CHORD[1] - STAB_CHORD[0]) * _span_t(xabs)

def elev_chord(xabs):
    """Elevator chord, with the V cut-out at the centre that lets the rudder swing."""
    full = ELEV_CHORD[0] + (ELEV_CHORD[1] - ELEV_CHORD[0]) * _span_t(xabs)
    return min(full, 0.15 + max(0.0, xabs - 0.02) * 3.2)

ELEV_HINGE_Y = fs(STAB_TE_FS[0]) - ELEV_CHORD[0]

def stab_section(xabs, side, kind, k):
    c = stab_chord(xabs)
    y_le = stab_te_y(xabs) - c
    if kind == "full":
        prof = resample_loop(AF_TAIL, k)
    else:
        boxp, surfp = split_airfoil(AF_TAIL, 1 - elev_chord(xabs) / c)
        prof = resample_loop(boxp if kind == "box" else surfp, k)
    return [Vector((side * xabs, y_le + x * c, STAB_Z + y * c)) for x, y in prof]

# Vertical tail, side elevation. Leading edge as WL -> FS: the dorsal fin starts as a point at the foot
# of the rear window (FS 129) and ramps gently aft into the 45-degree fin leading edge. Rows below
# WL 52.2 lie inside the tailcone and only keep the loft closed.
FIN_LE = [(46.3, 232.0), (47.2, 225.0), (48.4, 205.0), (49.6, 185.0), (51.3, 155.0), (52.7, 129.0), (53.7, 150.0), (55.3, 165.0),
          (56.2, 180.0), (56.9, 190.0), (57.6, 200.0), (59.2, 210.0), (61.1, 215.0), (64.3, 220.0), (73.8, 230.0), (83.5, 240.0),
          (95.0, 251.2), (96.5, 253.6)]
TAIL_END_FS = U.ref("tail_end_fs_in")            # rear top corner of the rudder: the overall length of POH Fig 1-1
FIN_TOP = ((253.6, 96.5), (TAIL_END_FS, 92.3))  # top edge: front corner, rear corner (highest at the front)
RUD_TE = ((258.6, 43.5), (TAIL_END_FS, 92.3))   # raked rudder trailing edge above WL 43.5; vertical below it
RUD_FOOT = ((240.0, 29.5), (258.6, 35.0))       # lower edge of the rudder, continuing the tailcone underside
RUD_HINGE = ((237.5, 29.5), (264.0, 92.0))      # rudder hinge line
FIN_VLE = ((220.0, 64.3), (251.2, 95.0))        # straight part of the fin leading edge (chord reference)
FIN_BASE_WL = FIN_LE[0][0]
FIN_TIP_WL = FIN_TOP[0][1]
DORSAL_HALF_T = 0.011                            # the dorsal fin is a thin sheet-metal blade ...
DORSAL_ROOT = [(129.0, 0.0), (140.0, 0.016), (215.0, 0.052), (247.0, 0.034)]   # FS -> half width of its faired root (m)
DORSAL_ROOT_H = 4.5                              # ... flaring out over this height (in) above the tailcone

def _line(a, b, at, index):
    """Value of the other coordinate on the line a-b; index 0 = given FS, 1 = given WL."""
    other = 1 - index
    return a[other] + (b[other] - a[other]) * (at - a[index]) / (b[index] - a[index])

def fin_le_fs(w):
    return interp_pchip(FIN_LE, w)[0]

def fin_top_fs(w):
    """Station of the sloping top edge at water line w (only meaningful above the rear corner)."""
    return _line(FIN_TOP[0], FIN_TOP[1], w, 1)

def rudder_hinge_fs(w):
    return _line(RUD_HINGE[0], RUD_HINGE[1], w, 1)

def rudder_te_fs(w):
    if w >= FIN_TOP[1][1]:
        return fin_top_fs(w)
    if w >= RUD_TE[0][1]:
        return _line(RUD_TE[0], RUD_TE[1], w, 1)
    if w >= RUD_FOOT[1][1]:
        return RUD_TE[0][0]
    return _line(RUD_FOOT[0], RUD_FOOT[1], max(w, RUD_FOOT[0][1]), 1)

def tailcone_top_wl(station):
    return (fus_top_z(min(max(station, 0.0), FUS_END_FS)) - U.GROUND_Z) / IN

def fin_half_thickness(station, w):
    """Half thickness (m) of the vertical tail at (FS, WL): a symmetric section between the extended
    fin leading edge and the rudder trailing edge, the dorsal blade ahead of it, and a root fairing
    that flares out into the top of the tailcone."""
    le = fin_le_fs(w)
    nose = min(1.0, max(0.0, (station - le) / 4.0)) ** 0.5
    blade = DORSAL_HALF_T * nose
    height = w - tailcone_top_wl(station)
    root = interp_linear(DORSAL_ROOT, min(max(station, DORSAL_ROOT[0][0]), DORSAL_ROOT[-1][0]))[0]
    flare = root * nose * (1.0 if height <= 0 else max(0.0, 1 - height / DORSAL_ROOT_H) ** 2)
    v_le = _line(FIN_VLE[0], FIN_VLE[1], w, 1)
    te = max(rudder_te_fs(min(w, FIN_TOP[1][1])), v_le + 12.0)
    chord_m = (te - v_le) * IN
    u = (station - v_le) / (te - v_le)
    if u <= 0.0:
        return max(blade, flare)
    u = min(u, 1.0)
    thickness = min(0.09, 0.07 * chord_m)
    section = 5 * thickness * (0.2969 * math.sqrt(u) - 0.1260 * u - 0.3516 * u ** 2 + 0.2843 * u ** 3 - 0.1036 * u ** 4)
    return max(blade, section, flare)

def _fin_ring(w, n):
    """Fixed fin at water line w: from the hinge line forward along the left side to the leading
    edge and back along the right side (same order as naca4(), so the livery atlas still fits)."""
    le = fin_le_fs(w)
    aft = min(rudder_hinge_fs(w), fin_top_fs(w)) if w > FIN_TOP[1][1] else rudder_hinge_fs(w)
    aft = max(aft, le + 0.5)
    stations = [le + (aft - le) * (1 - j / n) ** 1.6 for j in range(n + 1)]        # hinge ... leading edge
    left = [Vector((fin_half_thickness(st, w), fs(st), wl(w))) for st in stations]
    right = [Vector((-fin_half_thickness(st, w), fs(st), wl(w))) for st in reversed(stations[:-1])]
    return left + right[:-1]

def _rudder_ring(w, n):
    """Rudder at water line w: trailing edge, left side forward to the rounded nose at the hinge, back."""
    hinge = rudder_hinge_fs(w)
    te = max(rudder_te_fs(w), hinge + 0.6)
    nose_h = max(0.004, fin_half_thickness(hinge, w) * 0.92)
    def half(st):
        t = (st - hinge) / (te - hinge)
        return nose_h * (1 - t) + 0.0015 * t
    stations = [te - (te - hinge) * j / n for j in range(n + 1)]                   # trailing edge ... hinge
    left = [Vector((half(st), fs(st), wl(w))) for st in stations]
    nose = [Vector((nose_h * math.cos(a), fs(hinge) - nose_h * 0.9 * math.sin(a), wl(w))) for a in (math.radians(d) for d in (30, 60, 90, 120, 150))]
    right = [Vector((-half(st), fs(st), wl(w))) for st in reversed(stations)]
    return left + nose + right[:-1]

def build_empennage(ctx):
    M = ctx.mats
    grp = ctx.groups["EMPENNAGE"]
    # ---- horizontal stabiliser (one piece through the tailcone)
    stations = _stations(0.0, STAB_END, 0.15)
    right = [stab_section(x, 1, "box", K_WING) for x in stations]
    left = [stab_section(x, -1, "box", K_WING) for x in stations]
    rings = list(reversed(left)) + right[1:]
    def cap_rings(base_ring, side):
        out = []
        cy = sum(v.y for v in base_ring) / len(base_ring); cz = sum(v.z for v in base_ring) / len(base_ring)
        for i in range(1, 4):
            t = i / 3
            sc = math.sqrt(max(1e-4, 1 - t * t))
            out.append([Vector((v.x + side * 0.05 * t, cy + (v.y - cy) * (0.3 + 0.7 * sc), cz + (v.z - cz) * sc)) for v in base_ring])
        return out
    rings = list(reversed(cap_rings(left[-1], -1))) + rings + cap_rings(right[-1], 1)
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[i / (len(rings) - 1) for i in range(len(rings))])
    stab = obj_from_bm("EMPENNAGE.stabilizer", bm, ctx.col, pivot=(0, stab_te_y(0) - STAB_CHORD[0], STAB_Z), mat=M["stab"])
    parent_keep(stab, grp)
    ctx.tag(stab, "EMPENNAGE", "Horizontal stabilizer", "المثبت الأفقي", status="type_data", note="span 11 ft 4 in (type data); chord, sweep and position estimated (photo-profile)")
    # ---- elevator: one piece, horns wrap round the stabiliser tips, V cut-out at the centre for the rudder
    stations = [0.03, 0.07, 0.12, 0.20] + _stations(0.30, STAB_END - 0.01, 0.15)
    def elev_half(side):
        rr = [stab_section(x, side, "surf", K_CTRL) for x in stations]
        horn = [stab_section(x, side, "full", K_CTRL) for x in _stations(STAB_END + 0.012, STAB_SEMISPAN - 0.03, 0.05)]
        # rounded tip out to the full span (11 ft 4 in over the elevator horns)
        last = horn[-1]
        cy = sum(v.y for v in last) / len(last)
        for dx, scale in ((0.018, 0.82), (0.027, 0.55), (0.03, 0.25)):
            horn.append([Vector((v.x + side * dx, cy + (v.y - cy) * (0.5 + 0.5 * scale), STAB_Z + (v.z - STAB_Z) * scale)) for v in last])
        return rr + horn
    r = elev_half(1); l = elev_half(-1)
    rings = list(reversed(l)) + r
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[i / (len(rings) - 1) for i in range(len(rings))])
    elev = obj_from_bm("EMPENNAGE.elevator", bm, ctx.col, pivot=(0, ELEV_HINGE_Y, STAB_Z), mat=M["control"])
    parent_keep(elev, grp)
    ctx.tag(elev, "EMPENNAGE", "Elevator (with balance horns)", "الرافع (مع أذرع الموازنة)", status="estimated", hinge_axis="x", hinge_sign=-1, range_deg=[-28, 23], animate="elevator", ref="p.2-x travel")
    # ---- trim tab on the right elevator, inboard
    tab_c = 0.15
    rr = []
    xs = _stations(-0.80, -0.26, 0.1)
    for x in xs:
        c = stab_chord(abs(x)); y_le = stab_te_y(abs(x)) - c
        boxp, surfp = split_airfoil(AF_TAIL, 1 - tab_c / c)
        prof = resample_loop(surfp, 32)
        # a hair proud of the elevator skin it is let into, so the two surfaces never coincide
        proud = lambda py: py * c * 1.12 + (0.0012 if py > 1e-6 else -0.0012 if py < -1e-6 else 0.0)
        rr.append([Vector((x, y_le + px * c, STAB_Z + proud(py))) for px, py in prof])
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True)
    tab = obj_from_bm("EMPENNAGE.trim_tab", bm, ctx.col, pivot=(-0.26, stab_te_y(0.26) - tab_c, STAB_Z), mat=M["control"])
    parent_keep(tab, elev)
    ctx.tag(tab, "EMPENNAGE", "Elevator trim tab (right side)", "لسان موازنة الرافع", status="poh", ref="p.7-6 (manual trim wheel)", hinge_axis="x", hinge_sign=-1, range_deg=[-25, 25], animate="trim_tab")
    # ---- vertical fin with dorsal fin: horizontal slices, closely spaced where the dorsal ramp is shallow
    levels = [FIN_BASE_WL, 47.6, 48.9, 50.2, 51.4, 52.2, 52.7, 53.1, 53.7, 54.5, 55.3, 55.8, 56.2, 56.6, 56.9, 57.2, 57.6, 58.4,
              59.2, 60.1, 61.1, 62.5, 64.3, 67.0, 70.0, 73.8, 77.0, 80.0, 83.5, 86.5, 89.5, 92.3, 93.3, 94.3, 95.0, 95.6, 96.1, 96.4]
    rings = [_fin_ring(w, 26) for w in levels]
    visible0 = 52.7
    uv_v = [max(0.0, (w - visible0) / (FIN_TIP_WL - visible0)) for w in levels]
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v)
    fin = obj_from_bm("EMPENNAGE.fin", bm, ctx.col, pivot=(0, fs(215), wl(55)), mat=M["fin"])
    parent_keep(fin, grp)
    ctx.tag(fin, "EMPENNAGE", "Vertical fin with dorsal fin", "المثبت الرأسي مع الزعنفة الظهرية", status="estimated",
            note="Outline from the photo-profile side elevation; section thickness estimated")
    # ---- rudder: raked trailing edge, foot continuing the tailcone underside
    levels = [29.5, 30.5, 31.8, 33.2, 35.0, 37.5, 40.5, 43.5, 47.0, 51.0, 55.0, 59.0, 63.0, 67.0, 71.0, 75.0, 79.0, 83.0, 86.5,
              89.5, 92.3, 93.0, 93.7, 94.3]
    rr = [_rudder_ring(w, 10) for w in levels]
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True, uv_v=[(w - levels[0]) / (levels[-1] - levels[0]) for w in levels])
    h0 = Vector((0, fs(RUD_HINGE[0][0]), wl(RUD_HINGE[0][1]))); h1 = Vector((0, fs(RUD_HINGE[1][0]), wl(RUD_HINGE[1][1])))
    rud = obj_from_bm("EMPENNAGE.rudder", bm, ctx.col, pivot=h0, z_axis=(h1 - h0), mat=M["control"])
    parent_keep(rud, grp)
    ctx.tag(rud, "EMPENNAGE", "Rudder", "الدفة", status="estimated", hinge_axis="z", hinge_sign=1, range_deg=[-16, 16], animate="rudder",
            note="Outline from the photo-profile side elevation; hinge line estimated")
    # white tail light at the top rear corner of the rudder, beacon on the fin tip
    tl_pos = (0, fs(FIN_TOP[1][0] - 0.8), wl(FIN_TOP[1][1] - 0.4))
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.018, 0.02), (0.0, 0.03)], axis="Y", origin=tl_pos, segs=12)
    tl = obj_from_bm("ELECTRICAL.tail_nav_light", bm, ctx.col, pivot=tl_pos, mat=M["nav_white"])
    parent_keep(tl, rud)
    ctx.tag(tl, "ELECTRICAL", "Tail navigation light (white)", "ضوء الملاحة الخلفي", status="poh", ref="p.7-27")
    bc_fs = 257.8
    bc_pos = (0, fs(bc_fs), wl(_line(FIN_TOP[0], FIN_TOP[1], bc_fs, 0)) - 0.012)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.035, 0.0), (0.035, 0.015), (0.03, 0.04), (0.012, 0.06), (0.0, 0.065)], axis="Z", origin=bc_pos, segs=16)
    bc = obj_from_bm("ELECTRICAL.beacon", bm, ctx.col, pivot=bc_pos, mat=M["nav_red"])
    parent_keep(bc, grp)
    ctx.tag(bc, "ELECTRICAL", "Flashing beacon (fin tip)", "منارة الوميض (قمة المثبت)", status="poh", ref="p.7-27")
    # tail tie-down ring under the tailcone
    td_pos = (0, fs(226), fus_surface_z(226, 0.0) + 0.004)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, -0.025), (0.0, -0.025)], axis="Z", origin=td_pos, segs=12)
    td = obj_from_bm("AIRFRAME.tail_tiedown", bm, ctx.col, pivot=td_pos, mat=M["steel"])
    parent_keep(td, grp)
    ctx.tag(td, "AIRFRAME", "Tail tie-down ring", "حلقة ربط الذيل", status="estimated")
    return fin

# ----------------------------------------------------------------------------- fuselage-mounted details

def build_details(ctx):
    M = ctx.mats
    grp = ctx.groups["AIRFRAME"]
    # comm antenna: bent whip on the roof
    bm = new_bm()
    pts = bezier(Vector((0, fs(78), 2.0)), Vector((0, fs(80), 2.3)), Vector((0, fs(88), 2.45)), Vector((0, fs(98), 2.55)), 10)
    tube(bm, pts, 0.009, segs=10, radius_end=0.003)
    ant = obj_from_bm("ELECTRICAL.comm_antenna", bm, ctx.col, pivot=(0, fs(78), 2.0), mat=M["paint_white"])
    parent_keep(ant, grp)
    ctx.tag(ant, "ELECTRICAL", "COM antenna (bent whip)", "هوائي الاتصال", status="estimated")
    # ELT antenna aft
    bm = new_bm()
    elt_z = fus_surface_z(150, 0.12, top=True)
    tube(bm, [Vector((0.12, fs(150), elt_z)), Vector((0.12, fs(152), elt_z + 0.32))], 0.005, segs=8)
    elt = obj_from_bm("ELECTRICAL.elt_antenna", bm, ctx.col, pivot=(0.12, fs(150), elt_z), mat=M["paint_white"])
    parent_keep(elt, grp)
    ctx.tag(elt, "ELECTRICAL", "ELT antenna", "هوائي جهاز تحديد موقع الطوارئ", status="estimated")
    # ADF sense wire from the roof to the fin
    bm = new_bm()
    tube(bm, [Vector((0, fs(60), 2.015)), Vector((0, fs(fin_le_fs(76.0) + 0.3), wl(76.0)))], 0.0025, segs=6)
    wire = obj_from_bm("ELECTRICAL.adf_sense_wire", bm, ctx.col, pivot=(0, fs(60), 2.015), mat=M["steel"], smooth=True)
    parent_keep(wire, grp)
    ctx.tag(wire, "ELECTRICAL", "ADF sense antenna wire", "سلك هوائي ADF", status="estimated")
    # static port (left side)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.004), (0.0, 0.004)], axis="X", origin=(fus_half_width(62) - 0.002, fs(62), 1.12), segs=16)
    sp = obj_from_bm("PITOT_STATIC.static_port", bm, ctx.col, pivot=(fus_half_width(62), fs(62), 1.12), mat=M["bare_alu"])
    parent_keep(sp, grp)
    ctx.tag(sp, "PITOT_STATIC", "Static port (left fuselage)", "منفذ الضغط الساكن", status="poh", ref="p.7-31")
    # cabin air inlets: round openings in the leading edge of each wing root (ramp photograph)
    for side in (-1, 1):
        name = "L" if side > 0 else "R"
        vx = side * 0.70
        le = Vector((vx, U.WING_LE_Y, U.WING_Z + (abs(vx) - 0.5) * math.tan(DIH)))
        bm = new_bm()
        revolve(bm, [(0.0, -0.001), (0.018, -0.001), (0.018, 0.02), (0.0, 0.02)], axis="Y", origin=le, segs=20)
        v = obj_from_bm(f"AIRFRAME.cabin_vent_{name}", bm, ctx.col, pivot=le, mat=M["interior_dark"])
        parent_keep(v, ctx.groups["WING_" + name])
        ctx.tag(v, "AIRFRAME", "Cabin ventilation air inlet (wing root leading edge)", "فتحة تهوية المقصورة (مقدمة جذر الجناح)", status="estimated")
    # ---- cabin interior liner (dark) so windows show a cabin, not the outside through the shell
    y0, y1 = fs(2), fs(116)
    rings = []
    for s in [2, 10, 20, 30, 45, 60, 75, 90, 100, 108, 116]:
        w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
        rings.append([Vector((x, fs(s), z)) for x, z in superellipse(w - 0.03, zc - zb - 0.03, zt - zc - 0.03, zc, nt, nb, K_RING)])
    def liner_shell(name):
        bm = new_bm()
        loft(bm, rings, close=True, cap_start=True, cap_end=True, flip=True)
        ob = obj_from_bm(name, bm, ctx.col, mat=M["interior_tan"])
        add_subsurf(ob, max(1, ctx.subsurf - 1))
        add_solidify(ob, 0.008)
        return ob
    liner = liner_shell("INTERIOR.cabin_liner")
    # the liner needs the same openings as the shell, otherwise it blocks the windows
    for key, c in ctx.cutter_objects.items():
        if not key.startswith("door_fit"):
            add_boolean(liner, c, "DIFFERENCE", "cut_" + key)
    parent_keep(liner, ctx.groups["INTERIOR"])
    ctx.tag(liner, "INTERIOR", "Cabin interior liner", "بطانة المقصورة الداخلية", status="estimated")
    # door trim panels: the part of the liner inside each door opening, carried by the door, so the
    # inside of a door shows trim rather than the back of the painted skin
    for side in ("L", "R"):
        door = bpy.data.objects.get(f"AIRFRAME.door_{side}")
        panel = liner_shell(f"INTERIOR.door_panel_{side}")
        add_boolean(panel, ctx.cutter_objects["door_fit_" + side], "INTERSECT", "door")
        add_boolean(panel, ctx.cutter_objects["door_win_" + side], "DIFFERENCE", "win")
        parent_keep(panel, door)
        ctx.tag(panel, "INTERIOR", f"{'Left' if side == 'L' else 'Right'} door trim panel", "بطانة الباب " + ("الأيسر" if side == "L" else "الأيمن"), status="estimated")
    # cabin floor: a flat panel that narrows with the hull so its edges stay inside the skin
    FLOOR_Z = 0.93
    floor_stations = [4, 12, 20, 30, 45, 60, 75, 88, 100, 108, 112]
    bm = new_bm()
    rings = []
    for st in floor_stations:
        half = max(0.12, fus_half_width_at(st, FLOOR_Z - 0.015) - 0.03)
        rings.append([Vector((half, fs(st), FLOOR_Z + 0.015)), Vector((-half, fs(st), FLOOR_Z + 0.015)),
                      Vector((-half, fs(st), FLOOR_Z - 0.015)), Vector((half, fs(st), FLOOR_Z - 0.015))])
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    floor = obj_from_bm("INTERIOR.floor", bm, ctx.col, mat=M["carpet"], smooth=False)
    parent_keep(floor, ctx.groups["INTERIOR"])
    ctx.tag(floor, "INTERIOR", "Cabin floor", "أرضية المقصورة", status="estimated")
