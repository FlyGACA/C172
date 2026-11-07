"""Exterior airframe: fuselage (with window/door cut-outs), wings, control surfaces,
empennage, struts and exterior details. All dimensions see units.py for status."""
import math
import bpy
import bmesh
from mathutils import Vector

from . import units as U
from .units import fs, bl, IN
from .shapes import (parent_keep, new_bm, loft, extrude_profile, revolve, tube, cylinder, box, bezier, obj_from_bm, empty,
                     add_subsurf, add_boolean, add_solidify, add_edge_split, add_bevel, naca4, airfoil_interp,
                     split_airfoil, superellipse, rounded_rect, ellipse, resample_loop, interp_table, smoothstep)

K_RING = 40          # points around fuselage sections
K_WING = 72          # points around wing box sections
K_CTRL = 48          # points around control-surface sections

# FS(in) -> half width, z bottom, z top, ring centre z, n_top, n_bottom   (status: estimated)
FUS_TABLE = [
    (0,   0.490, 0.900, 1.740, 1.38, 2.4, 2.2),
    (6,   0.515, 0.860, 1.860, 1.38, 2.5, 2.3),
    (14,  0.535, 0.830, 1.980, 1.36, 2.6, 2.4),
    (25,  0.540, 0.810, 2.000, 1.34, 4.5, 2.4),
    (60,  0.540, 0.800, 2.000, 1.32, 5.0, 2.4),
    (100, 0.535, 0.800, 1.990, 1.32, 4.5, 2.4),
    (108, 0.520, 0.805, 1.965, 1.32, 3.2, 2.3),
    (120, 0.470, 0.830, 1.860, 1.31, 2.3, 2.2),
    (135, 0.385, 0.880, 1.720, 1.29, 2.2, 2.1),
    (160, 0.290, 0.975, 1.560, 1.26, 2.1, 2.1),
    (200, 0.200, 1.060, 1.430, 1.235, 2.0, 2.0),
    (240, 0.125, 1.130, 1.360, 1.235, 2.0, 2.0),
    (268, 0.065, 1.170, 1.320, 1.235, 2.0, 2.0),
    (283, 0.028, 1.190, 1.300, 1.235, 2.0, 2.0),
]
FUS_STATIONS = [0, 3, 6, 10, 14, 18, 22, 25, 30, 36, 42, 48, 54, 60, 68, 76, 84, 92, 100, 104, 108, 112, 116, 120,
                126, 135, 145, 160, 180, 200, 220, 240, 255, 268, 278, 283]

def fus_ring(s, k=K_RING):
    w, zb, zt, zc, nt, nb = interp_table(FUS_TABLE, s)
    return [Vector((x, fs(s), z)) for x, z in superellipse(w, zc - zb, zt - zc, zc, nt, nb, k)]

def fus_top_z(s):
    return interp_table(FUS_TABLE, s)[2]

def fus_half_width(s):
    return interp_table(FUS_TABLE, s)[0]

def fus_surface_z(s, x, top=False):
    """Skin height at station s (in) and lateral x (m): bottom of the section, or top."""
    w, zb, zt, zc, nt, nb = interp_table(FUS_TABLE, s)
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

WINDOW_FRAME = 0.035   # visible frame width around glass cut-outs (m)

def window_cutters(ctx):
    """Return dict of cutter objects for every glazed opening and the doors."""
    C = {}
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
    # ---- door outline (left/right), hinge at the A-pillar (FS 14)
    door = _round_corners(_side_polygon([(14.5, 1.03), (50, 1.03), (50, 1.90), (27, 1.925), (14.5, 1.55)]), r=0.04)
    door_win = _round_corners(_side_polygon([(19.5, 1.31), (47, 1.31), (47, 1.86), (29, 1.885), (19.5, 1.58)]), r=0.035)
    rear_win = _round_corners(_side_polygon([(53.5, 1.31), (92, 1.31), (100, 1.86), (53.5, 1.86)]), r=0.04)
    for side, sgn in (("L", 1), ("R", -1)):
        C["door_" + side] = _cutter(ctx, "door_" + side, door, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["door_win_" + side] = _cutter(ctx, "door_win_" + side, door_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["rear_win_" + side] = _cutter(ctx, "rear_win_" + side, rear_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
    # ---- windshield: sloped plane from the cowl deck (FS 0, z 1.74) to the roof (FS 15, z 1.985)
    base = Vector((0, fs(0.5), 1.745)); top = Vector((0, fs(15.5), 1.995))
    slope = (top - base); L = slope.length; sdir = slope / L
    nrm = Vector((0, -sdir.z, sdir.y))
    ws = _round_corners([(-0.47, -0.06), (0.47, -0.06), (0.41, L + 0.05), (-0.41, L + 0.05)], r=0.05)
    C["windshield"] = _cutter(ctx, "windshield", ws, X, sdir, base, nrm, -0.35, 0.45)
    # ---- rear window on the sloping aft roof (FS 106 → 122)
    rb = Vector((0, fs(106), fus_top_z(106) + 0.004)); rt = Vector((0, fs(123), fus_top_z(123) + 0.004))
    rs = (rt - rb); Lr = rs.length; rdir = rs / Lr
    rnrm = Vector((0, -rdir.z, rdir.y))
    rw = _round_corners([(-0.43, 0.0), (0.43, 0.0), (0.36, Lr), (-0.36, Lr)], r=0.05)
    C["rear_window"] = _cutter(ctx, "rear_window", rw, X, rdir, rb, rnrm, -0.35, 0.45)
    return C

# ----------------------------------------------------------------------------- fuselage

def build_fuselage(ctx):
    M = ctx.mats
    parent = ctx.groups["AIRFRAME"]
    y0, y1 = fs(0), fs(283)
    rings = [fus_ring(s) for s in FUS_STATIONS]
    uv_v = [(fs(s) - y0) / (y1 - y0) for s in FUS_STATIONS]
    cut = window_cutters(ctx)
    ctx.cutter_objects = cut

    def shell(name, thickness=0.014):
        """Closed loft -> subdivision -> thin skin. Booleans see a closed mesh as a solid, so
        the skin must be solidified BEFORE any cut, otherwise the cabin volume is solid."""
        bm = new_bm()
        loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v)
        ob = obj_from_bm(name, bm, ctx.col, mat=M["fuselage"])
        add_subsurf(ob, ctx.subsurf)
        add_solidify(ob, thickness)
        return ob

    # main shell with every opening removed
    fus = shell("AIRFRAME.fuselage")
    parent_keep(fus, parent)
    for key in ("door_R", "door_L", "rear_win_R", "rear_win_L", "windshield", "rear_window"):
        add_boolean(fus, cut[key], "DIFFERENCE", "cut_" + key)
    ctx.tag(fus, "AIRFRAME", "Fuselage", "جسم الطائرة", status="estimated",
            note="Envelope from POH Fig 1-1; cross-sections estimated from photographs")

    # glazing: intersection of the same shell with the cutters
    def glass(name, key, parent_ob, label_en, label_ar):
        g = shell(name, thickness=0.005)
        add_boolean(g, cut[key], "INTERSECT", "glass")
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
        hinge = Vector((sgn * (fus_half_width(14.5) - 0.01), fs(14.5), 1.45))
        d = shell(f"AIRFRAME.door_{side}")
        add_boolean(d, cut["door_" + side], "INTERSECT", "door")
        add_boolean(d, cut["door_win_" + side], "DIFFERENCE", "win")
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
        hx = sgn * fus_half_width(40)
        box(bm, (0.012, 0.11, 0.02), center=(hx + sgn * 0.012, fs(42), 1.22))
        box(bm, (0.03, 0.03, 0.03), center=(hx + sgn * 0.01, fs(46), 1.22))
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
    p0 = Vector((side * 0.42, fs(46), fus_surface_z(46, 0.42) + 0.02))
    p1 = Vector((side * 2.44, U.WING_LE_Y + 0.33 * wing_chord(2.44), zlow + 0.015))
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
        zr = fus_surface_z(s_in, 0.36, top=True) if 0 <= s_in <= 283 else 1.9
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
        pts = [Vector((px, U.WING_LE_Y + 0.18, pz)), Vector((px, U.WING_LE_Y + 0.18, pz - 0.16)), Vector((px, U.WING_LE_Y - 0.08, pz - 0.19)), Vector((px, U.WING_LE_Y - 0.26, pz - 0.19))]
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

AF_TAIL = naca4("0009", 32)
STAB_TE_Y = fs(282)
STAB_ROOT_CHORD = 1.36
STAB_TIP_CHORD = 0.78
STAB_SEMISPAN = U.H_TAIL_SPAN / 2
STAB_Z = 1.285
ELEV_CHORD = 0.50
STAB_END = STAB_SEMISPAN - 0.17        # the elevator horn wraps around beyond this
FIN_TABLE = [  # z -> LE FS, hinge FS, thickness factor
    (1.26, 150, 262, 0.35),
    (1.40, 170, 262.5, 0.6),
    (1.55, 186, 263, 0.9),
    (1.70, 199, 263.5, 1.0),
    (2.00, 215, 264.5, 1.0),
    (2.30, 231, 265.5, 0.95),
    (2.55, 244, 266.5, 0.85),
    (2.68, 252, 267, 0.7),
]
RUD_TE_FS = 283

def stab_chord(xabs):
    t = min(1.0, xabs / STAB_SEMISPAN)
    return STAB_ROOT_CHORD + (STAB_TIP_CHORD - STAB_ROOT_CHORD) * t

def stab_section(xabs, side, kind, k):
    c = stab_chord(xabs)
    y_le = STAB_TE_Y - c
    if kind == "full":
        prof = resample_loop(AF_TAIL, k)
        scale_c = c; y0 = y_le
    else:
        xc = 1 - ELEV_CHORD / c
        boxp, surfp = split_airfoil(AF_TAIL, xc)
        prof = resample_loop(boxp if kind == "box" else surfp, k)
        scale_c = c; y0 = y_le
    return [Vector((side * xabs, y0 + x * scale_c, STAB_Z + y * scale_c)) for x, y in prof]

def build_empennage(ctx):
    M = ctx.mats
    grp = ctx.groups["EMPENNAGE"]
    # ---- horizontal stabiliser (one piece through the tailcone)
    rings = []; xs = []
    for side in (-1, 1):
        pass
    stations = _stations(0.0, STAB_END, 0.15)
    right = [stab_section(x, 1, "box", K_WING) for x in stations]
    left = [stab_section(x, -1, "box", K_WING) for x in stations]
    rings = list(reversed(left)) + right[1:]
    # tip rounding
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
    stab = obj_from_bm("EMPENNAGE.stabilizer", bm, ctx.col, pivot=(0, STAB_TE_Y - STAB_ROOT_CHORD, STAB_Z), mat=M["stab"])
    parent_keep(stab, grp)
    ctx.tag(stab, "EMPENNAGE", "Horizontal stabilizer", "المثبت الأفقي", status="type_data", note="span 11 ft 4 in (type data); chord/sweep estimated")
    # ---- elevator: one piece, horns wrap round the stabiliser tips
    stations = _stations(0.05, STAB_END - 0.01, 0.15)
    def elev_half(side):
        rr = [stab_section(x, side, "surf", K_CTRL) for x in stations]
        horn = [stab_section(x, side, "full", K_CTRL) for x in _stations(STAB_END + 0.012, STAB_SEMISPAN - 0.03, 0.05)]
        # horn sections only cover the aft part: keep them but they are full airfoils (step at the stab tip)
        return rr + horn
    r = elev_half(1); l = elev_half(-1)
    rings = list(reversed(l)) + r
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[i / (len(rings) - 1) for i in range(len(rings))])
    hinge_y = STAB_TE_Y - ELEV_CHORD
    elev = obj_from_bm("EMPENNAGE.elevator", bm, ctx.col, pivot=(0, hinge_y, STAB_Z), mat=M["control"])
    parent_keep(elev, grp)
    ctx.tag(elev, "EMPENNAGE", "Elevator (with balance horns)", "الرافع (مع أذرع الموازنة)", status="estimated", hinge_axis="x", hinge_sign=-1, range_deg=[-28, 23], animate="elevator", ref="p.2-x travel")
    # ---- trim tab on the right elevator, inboard
    tab_c = 0.17
    rr = []
    xs = _stations(-0.78, -0.16, 0.1)
    for x in xs:
        c = stab_chord(abs(x)); y_le = STAB_TE_Y - c
        xc = 1 - tab_c / c
        boxp, surfp = split_airfoil(AF_TAIL, xc)
        prof = resample_loop(surfp, 32)
        rr.append([Vector((x, y_le + px * c, STAB_Z + py * c)) for px, py in prof])
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True)
    tab = obj_from_bm("EMPENNAGE.trim_tab", bm, ctx.col, pivot=(-0.16, STAB_TE_Y - tab_c, STAB_Z), mat=M["control"])
    parent_keep(tab, elev)
    ctx.tag(tab, "EMPENNAGE", "Elevator trim tab (right side)", "لسان موازنة الرافع", status="poh", ref="p.7-6 (manual trim wheel)", hinge_axis="x", hinge_sign=-1, range_deg=[-25, 25], animate="trim_tab")
    # ---- vertical fin with dorsal fillet
    rings = []
    zs = [row[0] for row in FIN_TABLE]
    zz = []
    for z in _stations(zs[0], zs[-1], 0.08):
        le, hinge, tf = interp_table(FIN_TABLE, z)
        c = (hinge - le) * IN
        thick = min(0.09, 0.13 / max(c, 1e-3)) * tf
        prof = resample_loop(naca4("00%02d" % max(2, int(round(thick * 100))), 32), K_WING)
        rings.append([Vector((y * c, fs(le) + x * c, z)) for x, y in prof]); zz.append(z)
    # fin tip rounding
    top = rings[-1]
    cy = sum(v.y for v in top) / len(top)
    for i in range(1, 4):
        t = i / 3; sc = math.sqrt(max(1e-4, 1 - t * t))
        rings.append([Vector((v.x * sc, cy + (v.y - cy) * (0.4 + 0.6 * sc), top[0].z + 0.05 * t)) for v in top]); zz.append(top[0].z + 0.05 * t)
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[(z - zz[0]) / (zz[-1] - zz[0]) for z in zz])
    fin = obj_from_bm("EMPENNAGE.fin", bm, ctx.col, pivot=(0, fs(200), 1.4), mat=M["fin"])
    parent_keep(fin, grp)
    ctx.tag(fin, "EMPENNAGE", "Vertical fin with dorsal fillet", "المثبت الرأسي مع الزعنفة الظهرية", status="estimated")
    # ---- rudder (hinge swept slightly aft, balance horn above the fin tip)
    rr = []; zz = []
    for z in _stations(1.25, 2.66, 0.08):
        le, hinge, tf = interp_table(FIN_TABLE, z)
        c_total = (RUD_TE_FS - le) * IN
        xc = (hinge - le) / (RUD_TE_FS - le)
        thick = min(0.09, 0.13 / max((hinge - le) * IN, 1e-3)) * tf
        boxp, surfp = split_airfoil(naca4("00%02d" % max(2, int(round(thick * 100))), 32), xc)
        prof = resample_loop(surfp, K_CTRL)
        rr.append([Vector((y * c_total, fs(le) + x * c_total, z)) for x, y in prof]); zz.append(z)
    for z in (2.70, 2.76, 2.80):
        le = 254 + (z - 2.70) * 60; c_total = (RUD_TE_FS + 1 - le) * IN
        prof = resample_loop(naca4("0006", 32), K_CTRL)
        sc = 1.0 if z < 2.79 else 0.5
        rr.append([Vector((y * c_total * sc, fs(le) + x * c_total, z)) for x, y in prof]); zz.append(z)
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True, uv_v=[(z - zz[0]) / (zz[-1] - zz[0]) for z in zz])
    h0 = Vector((0, fs(262), 1.25)); h1 = Vector((0, fs(267), 2.68))
    rud = obj_from_bm("EMPENNAGE.rudder", bm, ctx.col, pivot=h0, z_axis=(h1 - h0), mat=M["control"])
    parent_keep(rud, grp)
    ctx.tag(rud, "EMPENNAGE", "Rudder (with balance horn)", "الدفة (مع ذراع الموازنة)", status="estimated", hinge_axis="z", hinge_sign=1, range_deg=[-16, 16], animate="rudder")
    # tail navigation light on the rudder top, beacon on the fin tip
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.022, 0.0), (0.02, 0.02), (0.0, 0.03)], axis="Y", origin=(0, fs(281), 2.74), segs=12)
    tl = obj_from_bm("ELECTRICAL.tail_nav_light", bm, ctx.col, pivot=(0, fs(281), 2.74), mat=M["nav_white"])
    parent_keep(tl, rud)
    ctx.tag(tl, "ELECTRICAL", "Tail navigation light (white)", "ضوء الملاحة الخلفي", status="poh", ref="p.7-27")
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.035, 0.0), (0.035, 0.015), (0.03, 0.04), (0.012, 0.06), (0.0, 0.065)], axis="Z", origin=(0, fs(259), 2.725), segs=16)
    bc = obj_from_bm("ELECTRICAL.beacon", bm, ctx.col, pivot=(0, fs(259), 2.725), mat=M["nav_red"])
    parent_keep(bc, grp)
    ctx.tag(bc, "ELECTRICAL", "Flashing beacon (fin tip)", "منارة الوميض (قمة المثبت)", status="poh", ref="p.7-27")
    # tail tie-down ring
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, -0.025), (0.0, -0.025)], axis="Z", origin=(0, fs(262), 1.165), segs=12)
    td = obj_from_bm("AIRFRAME.tail_tiedown", bm, ctx.col, pivot=(0, fs(262), 1.165), mat=M["steel"])
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
    tube(bm, [Vector((0.12, fs(150), fus_top_z(150))), Vector((0.12, fs(152), fus_top_z(150) + 0.32))], 0.005, segs=8)
    elt = obj_from_bm("ELECTRICAL.elt_antenna", bm, ctx.col, pivot=(0.12, fs(150), fus_top_z(150)), mat=M["paint_white"])
    parent_keep(elt, grp)
    ctx.tag(elt, "ELECTRICAL", "ELT antenna", "هوائي جهاز تحديد موقع الطوارئ", status="estimated")
    # ADF sense wire from the roof to the fin
    bm = new_bm()
    tube(bm, [Vector((0, fs(60), 2.015)), Vector((0, fs(243), 2.42))], 0.0025, segs=6)
    wire = obj_from_bm("ELECTRICAL.adf_sense_wire", bm, ctx.col, pivot=(0, fs(60), 2.015), mat=M["steel"], smooth=True)
    parent_keep(wire, grp)
    ctx.tag(wire, "ELECTRICAL", "ADF sense antenna wire", "سلك هوائي ADF", status="estimated")
    # static port (left side)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.004), (0.0, 0.004)], axis="X", origin=(fus_half_width(62) - 0.002, fs(62), 1.12), segs=16)
    sp = obj_from_bm("PITOT_STATIC.static_port", bm, ctx.col, pivot=(fus_half_width(62), fs(62), 1.12), mat=M["bare_alu"])
    parent_keep(sp, grp)
    ctx.tag(sp, "PITOT_STATIC", "Static port (left fuselage)", "منفذ الضغط الساكن", status="poh", ref="p.7-31")
    # step and handhold on the left for refuelling
    bm = new_bm()
    zs = fus_surface_z(64, 0.42)
    tube(bm, [Vector((0.42, fs(60), zs + 0.02)), Vector((0.62, fs(60), zs - 0.22)), Vector((0.62, fs(60), zs - 0.26)), Vector((0.78, fs(60), zs - 0.26)), Vector((0.78, fs(68), zs - 0.26)), Vector((0.62, fs(68), zs - 0.26)), Vector((0.62, fs(68), zs - 0.22)), Vector((0.42, fs(68), zs + 0.02))], 0.012, segs=10)
    step = obj_from_bm("AIRFRAME.step_L", bm, ctx.col, pivot=(0.42, fs(64), zs), mat=M["steel"])
    parent_keep(step, grp)
    ctx.tag(step, "AIRFRAME", "Refuelling step (left)", "درجة التزود بالوقود", status="estimated")
    bm = new_bm()
    tube(bm, [Vector((0.52, fs(60), 1.62)), Vector((0.57, fs(60), 1.62)), Vector((0.57, fs(70), 1.62)), Vector((0.52, fs(70), 1.62))], 0.009, segs=10)
    hh = obj_from_bm("AIRFRAME.handhold_L", bm, ctx.col, pivot=(0.52, fs(65), 1.62), mat=M["steel"])
    parent_keep(hh, grp)
    ctx.tag(hh, "AIRFRAME", "Handhold (left)", "مقبض اليد", status="estimated")
    # cabin air vent inlets at the wing roots (small scoops) and the wing root fairing
    for side in (-1, 1):
        bm = new_bm()
        zroof = fus_surface_z(22, 0.30, top=True)
        box(bm, (0.06, 0.10, 0.03), center=(side * 0.30, fs(22), zroof + 0.012))
        v = obj_from_bm(f"AIRFRAME.cabin_vent_{'L' if side > 0 else 'R'}", bm, ctx.col, pivot=(side * 0.3, fs(22), zroof), mat=M["paint_white"])
        parent_keep(v, grp)
        ctx.tag(v, "AIRFRAME", "Cabin ventilation air inlet", "فتحة تهوية المقصورة", status="estimated")
    # ---- cabin interior liner (dark) so windows show a cabin, not the outside through the shell
    y0, y1 = fs(2), fs(116)
    rings = []
    for s in [2, 10, 20, 30, 45, 60, 75, 90, 100, 108, 116]:
        w, zb, zt, zc, nt, nb = interp_table(FUS_TABLE, s)
        rings.append([Vector((x, fs(s), z)) for x, z in superellipse(w - 0.03, zc - zb - 0.03, zt - zc - 0.03, zc, nt, nb, K_RING)])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, flip=True)
    liner = obj_from_bm("INTERIOR.cabin_liner", bm, ctx.col, mat=M["interior_tan"])
    add_subsurf(liner, max(1, ctx.subsurf - 1))
    add_solidify(liner, 0.008)
    # the liner needs the same openings as the shell, otherwise it blocks the windows
    for key, c in ctx.cutter_objects.items():
        add_boolean(liner, c, "DIFFERENCE", "cut_" + key)
    parent_keep(liner, ctx.groups["INTERIOR"])
    ctx.tag(liner, "INTERIOR", "Cabin interior liner", "بطانة المقصورة الداخلية", status="estimated")
    # cabin floor
    bm = new_bm()
    box(bm, (0.78, fs(112) - fs(4), 0.03), center=(0, (fs(4) + fs(112)) / 2, 0.93))   # inside the rounded belly
    floor = obj_from_bm("INTERIOR.floor", bm, ctx.col, mat=M["carpet"])
    parent_keep(floor, ctx.groups["INTERIOR"])
    ctx.tag(floor, "INTERIOR", "Cabin floor", "أرضية المقصورة", status="estimated")
