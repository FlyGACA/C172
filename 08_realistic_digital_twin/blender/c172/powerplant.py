"""Cowling, nose bowl with inlets and landing light, spinner, propeller, exhaust."""
import math
from mathutils import Vector

from . import units as U
from .units import fs
from .shapes import (parent_keep, new_bm, loft, revolve, tube, box, bezier, obj_from_bm, add_subsurf, add_boolean, add_solidify,
                     superellipse, ellipse, rounded_rect, naca4, resample_loop, interp_table, extrude_profile)
from .airframe import K_RING

COWL_TABLE = [  # FS -> w, zb, zt, zc, n_top, n_bot   (172N cowl: flat-topped, squarish section, chin below the spinner)
    (-36.5, 0.320, 1.120, 1.655, 1.400, 2.8, 2.4),
    (-32,   0.395, 1.030, 1.700, 1.395, 2.9, 2.5),
    (-24,   0.450, 0.960, 1.730, 1.390, 2.9, 2.5),
    (-12,   0.478, 0.915, 1.742, 1.385, 2.7, 2.4),
    (0,     0.490, 0.900, 1.740, 1.380, 2.4, 2.2),
]
COWL_STATIONS = [-36.5, -35, -32, -28, -23, -17, -11, -5, 0]
NOSE_Y = fs(-37.5)

def cowl_ring(s, k=K_RING):
    w, zb, zt, zc, nt, nb = interp_table(COWL_TABLE, s)
    return [Vector((x, fs(s), z)) for x, z in superellipse(w, zc - zb, zt - zc, zc, nt, nb, k)]

def _link(ob, grp):
    parent_keep(ob, grp)

def build_cowl(ctx):
    M = ctx.mats
    grp = ctx.groups["POWERPLANT"]
    k = K_RING
    rings = [cowl_ring(s) for s in COWL_STATIONS]
    # domed nose-bowl face: from the front ring inward to the spinner opening
    front = rings[0]
    inner = [Vector((0.19 * math.cos(-math.pi / 2 + 2 * math.pi * i / k), NOSE_Y, U.PROP_Z + 0.19 * math.sin(-math.pi / 2 + 2 * math.pi * i / k))) for i in range(k)]
    mid = [Vector(((f.x + 1.2 * i_.x) / 2.2, fs(-37.2), (f.z + 1.2 * i_.z) / 2.2)) for f, i_ in zip(front, inner)]
    all_rings = [inner, mid] + rings
    nvs = len(all_rings)
    uv_v = [0.0, 0.03] + [0.06 + 0.94 * (s - COWL_STATIONS[0]) / (0 - COWL_STATIONS[0]) for s in COWL_STATIONS]
    q = k // 4
    def half(name, idx, label_en, label_ar, y_pivot):
        rr = [[r[i % k] for i in idx] for r in all_rings]
        bm = new_bm()
        loft(bm, rr, close=False, uv_v=uv_v, uv_u_scale=0.5)
        ob = obj_from_bm(name, bm, ctx.col, pivot=(0, fs(0), y_pivot), mat=M["cowl"])
        add_subsurf(ob, ctx.subsurf)
        return ob
    upper = half("POWERPLANT.cowl_upper", list(range(q, 3 * q + 1)), "Upper cowl (removable)", "غطاء المحرك العلوي", 1.74)
    lower = half("POWERPLANT.cowl_lower", list(range(3 * q, 5 * q + 1)), "Lower cowl", "غطاء المحرك السفلي", 0.90)
    # inlets and landing light cut through the nose bowl
    cutters = []
    for sx in (-1, 1):
        bm = new_bm()
        pts = ellipse(0.10, 0.062, 28)
        extrude_profile(bm, pts, Vector((1, 0, 0)), Vector((0, 0, 1)), (sx * 0.185, fs(-42), U.PROP_Z + 0.035), Vector((0, 1, 0)), 0.0, 0.16, smooth_sides=False)
        cutters.append(obj_from_bm(f"_cut_inlet_{'L' if sx > 0 else 'R'}", bm, ctx.cutters, smooth=False))
    bm = new_bm()
    extrude_profile(bm, rounded_rect(0.14, 0.085, 0.02), Vector((1, 0, 0)), Vector((0, 0, 1)), (0.21, fs(-42), U.PROP_Z - 0.15), Vector((0, 1, 0)), 0.0, 0.17, smooth_sides=False)
    cutters.append(obj_from_bm("_cut_landing_light", bm, ctx.cutters, smooth=False))
    for ob in (upper, lower):
        add_solidify(ob, 0.008)          # closed manifold first, so the exact boolean is reliable
        for c in cutters:
            add_boolean(ob, c, "DIFFERENCE", c.name)
        _link(ob, grp)
    ctx.tag(upper, "POWERPLANT", "Upper engine cowl (quick-release fasteners, oil door)", "غطاء المحرك العلوي (مشابك سريعة، باب الزيت)", status="estimated", removable=True)
    ctx.tag(lower, "POWERPLANT", "Lower engine cowl (inlets, landing/taxi light)", "غطاء المحرك السفلي (فتحات الهواء وضوء الهبوط)", status="estimated")
    # inlet ducts (dark interior behind the inlets) and landing-light lens/reflector
    for sx in (-1, 1):
        bm = new_bm()
        pts = ellipse(0.105, 0.066, 24)
        rings_ = [[Vector((sx * 0.185 + x, fs(-36.5) + d, U.PROP_Z + 0.035 + z)) for x, z in pts] for d in (0.0, 0.25)]
        loft(bm, rings_, close=True, cap_start=False, cap_end=True, flip=True)
        duct = obj_from_bm(f"POWERPLANT.inlet_duct_{'L' if sx > 0 else 'R'}", bm, ctx.col, pivot=(sx * 0.185, fs(-36.5), U.PROP_Z), mat=M["interior_dark"])
        _link(duct, grp)
        ctx.tag(duct, "POWERPLANT", "Cooling air inlet (to the cylinder baffles)", "فتحة هواء التبريد", status="estimated")
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.06, 0.0), (0.064, 0.03), (0.0, 0.05)], axis="Y", origin=(0.21, fs(-36.4), U.PROP_Z - 0.15), segs=20)
    refl = obj_from_bm("ELECTRICAL.landing_light", bm, ctx.col, pivot=(0.21, fs(-36.4), U.PROP_Z - 0.15), mat=M["chrome"])
    _link(refl, grp)
    ctx.tag(refl, "ELECTRICAL", "Landing / taxi light (nose cowl)", "ضوء الهبوط والتدرج", status="poh", ref="p.7-27")
    bm = new_bm()
    extrude_profile(bm, rounded_rect(0.138, 0.083, 0.02), Vector((1, 0, 0)), Vector((0, 0, 1)), (0.21, fs(-36.9), U.PROP_Z - 0.15), Vector((0, 1, 0)), 0.0, 0.004, smooth_sides=False)
    lens = obj_from_bm("ELECTRICAL.landing_light_lens", bm, ctx.col, pivot=(0.21, fs(-36.9), U.PROP_Z - 0.15), mat=M["glass"])
    _link(lens, grp)
    ctx.tag(lens, "ELECTRICAL", "Landing light lens", "عدسة ضوء الهبوط", status="estimated")
    # firewall
    bm = new_bm()
    ring = cowl_ring(0)
    loft(bm, [[Vector((p.x * 0.985, fs(0.6), p.z)) for p in ring], [Vector((p.x * 0.985, fs(1.6), p.z)) for p in ring]], close=True, cap_start=True, cap_end=True)
    fw = obj_from_bm("AIRFRAME.firewall", bm, ctx.col, pivot=(0, fs(1), 1.3), mat=M["bare_alu"])
    _link(fw, ctx.groups["AIRFRAME"])
    ctx.tag(fw, "AIRFRAME", "Firewall (stainless steel), FS 0 datum", "الجدار الناري (نقطة المرجع FS 0)", status="poh", ref="p.6-x datum")

def build_spinner_prop(ctx):
    M = ctx.mats
    grp = ctx.groups["POWERPLANT"]
    hub = Vector((0, fs(-37.0), U.PROP_Z))
    # spinner (ogive) with backplate
    prof = []
    n = 14
    for i in range(n + 1):
        t = i / n
        prof.append((0.165 * math.sin(t * math.pi / 2) ** 0.85, U.SPINNER_TIP_Y + (fs(-35.3) - U.SPINNER_TIP_Y) * t - 0.0))
    prof.append((0.165, fs(-35.0)))
    bm = new_bm()
    revolve(bm, prof, axis="Y", origin=(0, 0, U.PROP_Z), segs=40, cap_start=False, cap_end=False)
    sp = obj_from_bm("POWERPLANT.spinner", bm, ctx.col, pivot=hub, mat=M["paint_white"])
    add_subsurf(sp, 1)
    _link(sp, grp)
    ctx.tag(sp, "POWERPLANT", "Spinner", "القمع الأمامي (السبينر)", status="estimated", spin_axis="y", spin_sign=-1, animate="prop")
    bm = new_bm()
    revolve(bm, [(0.0, fs(-35.3)), (0.172, fs(-35.3)), (0.172, fs(-34.9)), (0.0, fs(-34.9))], axis="Y", origin=(0, 0, U.PROP_Z), segs=40)
    bp = obj_from_bm("POWERPLANT.spinner_backplate", bm, ctx.col, pivot=hub, mat=M["bare_alu"])
    parent_keep(bp, sp)
    ctx.tag(bp, "POWERPLANT", "Spinner backplate", "صفيحة القمع الخلفية", status="estimated")
    # propeller: two blades, pivot on the crank axis
    bm = new_bm()
    af = naca4("4412", 24)
    def blade(sign):
        rings = []
        R = U.PROP_R
        stations = [0.06, 0.09, 0.13, 0.19, 0.27, 0.36, 0.46, 0.56, 0.66, 0.76, 0.85, 0.92, 0.97, 1.0]
        for rt in stations:
            r = R * rt
            if rt < 0.12:
                c = 0.085; prof = resample_loop(ellipse(0.5, 0.42, 24), 24); beta = math.radians(58)
                prof = [(x + 0.5, y) for x, y in prof]
            else:
                c = interp_table([(0.12, 0.085), (0.3, 0.135), (0.5, 0.14), (0.75, 0.125), (0.92, 0.095), (1.0, 0.028)], rt)[0]
                beta = math.radians(interp_table([(0.12, 52), (0.3, 36), (0.5, 26), (0.75, 18), (1.0, 13)], rt)[0])
                thick = interp_table([(0.12, 0.20), (0.3, 0.10), (0.6, 0.07), (1.0, 0.05)], rt)[0]
                base = naca4("44%02d" % int(round(thick * 100)), 24)
                prof = resample_loop(base, 24)
            ec = Vector((0, math.sin(beta), math.cos(beta)))       # chord LE->TE (TE aft & up for the +x blade)
            et = Vector((0, -math.cos(beta), math.sin(beta)))      # thickness toward the cambered (forward) face
            ring = []
            for xc, yc in prof:
                p = Vector((r, 0, 0)) + ec * ((xc - 0.33) * c) + et * (yc * c)
                ring.append(Vector((sign * p.x, p.y, sign * p.z)))
            rings.append([hub + p for p in ring])
        loft(bm, rings, close=True, cap_start=True, cap_end=True, flip=(sign < 0))
    blade(1); blade(-1)
    # hub barrel
    revolve(bm, [(0.0, fs(-38.5)), (0.075, fs(-38.5)), (0.075, fs(-33.5)), (0.0, fs(-33.5))], axis="Y", origin=(0, 0, U.PROP_Z), segs=24)
    prop = obj_from_bm("POWERPLANT.propeller", bm, ctx.col, pivot=hub, mat=M["prop_black"])
    # painted tips (yellow) on the outer 12 % of each blade, polished hub
    prop.data.materials.append(M["prop_tip"]); prop.data.materials.append(M["bare_alu"])
    R = U.PROP_R
    for poly in prop.data.polygons:
        xs = [abs(prop.data.vertices[v].co.x) for v in poly.vertices]
        if max(xs) > 0.88 * R:
            poly.material_index = 1
        elif max(xs) < 0.08:
            poly.material_index = 2
    add_subsurf(prop, 1)
    parent_keep(prop, sp)
    ctx.tag(prop, "POWERPLANT", "McCauley two-blade fixed-pitch propeller, 75 in", "مروحة ماكولي ثابتة الخطوة ذات شفرتين", status="poh", ref="p.1-3", spin_axis="y", spin_sign=-1, animate="prop",
            note="Blade planform, twist and airfoil are illustrative")
    # exhaust tailpipe under the lower cowl (right of centre)
    bm = new_bm()
    pts = bezier(Vector((-0.14, fs(-14), 0.98)), Vector((-0.14, fs(-8), 0.84)), Vector((-0.15, fs(-5), 0.80)), Vector((-0.17, fs(5), 0.79)), 12)
    tube(bm, pts, 0.03, segs=14, cap=True)
    ex = obj_from_bm("ENGINE.exhaust_tailpipe", bm, ctx.col, pivot=pts[0], mat=M["exhaust"])
    _link(ex, grp)
    ctx.tag(ex, "ENGINE", "Exhaust tailpipe (from the muffler)", "ماسورة العادم", status="estimated")
