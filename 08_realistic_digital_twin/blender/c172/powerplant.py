"""Cowling, nose bowl with inlets and landing light, spinner, propeller, exhaust."""
import math
from mathutils import Vector

from . import units as U
from .units import fs
from .shapes import (parent_keep, new_bm, loft, revolve, tube, box, bezier, obj_from_bm, add_subsurf, add_boolean, add_solidify,
                     add_edge_split, superellipse, ellipse, rounded_rect, naca4, resample_loop, interp_table, extrude_profile)
from .profiles import interp_pchip
from .airframe import K_RING

# FS -> half width, z bottom, z top, ring centre z, n_top, n_bottom   (build frame). Status: estimated.
# Top and bottom lines follow the photo-profile side elevation: an almost straight top falling 6 in
# from the firewall to the nose, and an underside that sweeps up from the firewall to the spinner.
# The section is widest at crank height with square shoulders, to clear the cylinder heads.
COWL_TABLE = [
    (-33.6, 0.335, 1.468, 1.726, 1.612, 2.6, 2.0),
    (-32,   0.385, 1.405, 1.734, 1.610, 3.0, 2.0),
    (-30,   0.428, 1.330, 1.742, 1.608, 3.6, 2.0),
    (-27,   0.455, 1.205, 1.760, 1.605, 4.4, 2.05),
    (-23,   0.466, 1.075, 1.783, 1.600, 4.6, 2.2),
    (-19,   0.472, 0.988, 1.795, 1.590, 4.6, 2.4),
    (-10,   0.482, 0.913, 1.823, 1.540, 3.8, 2.7),
    (-4,    0.487, 0.890, 1.836, 1.470, 3.0, 2.9),
    (0,     0.490, 0.878, 1.843, 1.420, 2.6, 3.0),
]
COWL_STATIONS = [-33.6, -33, -32, -30.5, -28.5, -26, -23, -19.5, -15, -10, -5, 0]
NOSE_Y = fs(-34.3)
SPINNER_R = 0.115                       # 9 in spinner (estimated)
SPINNER_BASE_FS = -34.6
# Openings in the chin of the nose cap, both on the centreline (ramp photograph of a 1970s 172):
INLET = dict(x=0.222, z=U.PROP_Z + 0.012, w=0.205, h=0.112)      # cooling-air inlets either side of the spinner
LIGHT = dict(z=U.PROP_Z - 0.275, r=0.057)                        # single landing light below the spinner (POH p.7-27)
AIR_INLET = dict(z=U.PROP_Z - 0.45, w=0.15, h=0.085)             # carburettor air inlet; the filter sits right behind it (POH p.7-24)
MUFFLER_Y, MUFFLER_Z = fs(-9.5), U.PROP_Z - 0.43                 # muffler axis (across the aircraft, under the rear of the engine)

def cowl_ring(s, k=K_RING):
    w, zb, zt, zc, nt, nb = interp_pchip(COWL_TABLE, s)
    return [Vector((x, fs(s), z)) for x, z in superellipse(w, zc - zb, zt - zc, zc, nt, nb, k)]

def cowl_lower_z(s, x):
    """Height of the underside of the cowl skin at station s (in) and lateral position x (m)."""
    w, zb, zt, zc, nt, nb = interp_pchip(COWL_TABLE, s)
    t = min(1.0, abs(x) / w)
    return zc - (zc - zb) * (1 - t ** nb) ** (1 / nb)

def chin_station(x, z):
    """Station (in) at which the underside of the cowl is at height z; the chin sweeps down and aft."""
    a, b = COWL_TABLE[0][0], -12.0
    for _ in range(40):
        m = (a + b) / 2
        if cowl_lower_z(m, x) > z:
            a = m
        else:
            b = m
    return (a + b) / 2

def air_filter_y():
    """Front face of the induction air filter: just behind the lower edge of the inlet in the chin."""
    return fs(chin_station(0.0, AIR_INLET["z"] - AIR_INLET["h"] / 2) + 0.9)

def _link(ob, grp):
    parent_keep(ob, grp)

def _recess(ctx, name, outline, z0, y_back, cap=True):
    """Dark wall of an opening in the chin: from just inside the skin straight back to y_back, with an optional back plate."""
    pts = [(x * 1.03, z * 1.03) for x, z in outline]                     # a little larger than the cut, so nothing is coplanar
    front = [Vector((x, fs(chin_station(x, z0 + z)) + 0.005, z0 + z)) for x, z in pts]
    back = [Vector((x, y_back, z0 + z)) for x, z in pts]
    bm = new_bm()
    loft(bm, [front, back], close=True, cap_start=False, cap_end=cap)
    return obj_from_bm(name, bm, ctx.col, pivot=(0, y_back, z0), mat=ctx.mats["interior_dark"], smooth=False)

def build_cowl(ctx):
    M = ctx.mats
    grp = ctx.groups["POWERPLANT"]
    k = K_RING
    rings = [cowl_ring(s) for s in COWL_STATIONS]
    # nose-bowl face: from the front ring in toward the crank axis; the hole it leaves is behind the spinner
    front = rings[0]
    centre = Vector((0, 0, U.PROP_Z))
    def toward_axis(p, f, y):
        return Vector((centre.x + (p.x - centre.x) * f, y, centre.z + (p.z - centre.z) * f))
    inner = [toward_axis(p, 0.40, NOSE_Y) for p in front]
    mid = [toward_axis(p, 0.74, fs(-34.15)) for p in front]
    all_rings = [inner, mid] + rings
    nvs = len(all_rings)
    uv_v = [0.0, 0.03] + [0.06 + 0.94 * (s - COWL_STATIONS[0]) / (0 - COWL_STATIONS[0]) for s in COWL_STATIONS]
    q = k // 4
    def half(name, idx, label_en, label_ar, y_pivot):
        rr = [[r[i % k] for i in idx] for r in all_rings]
        bm = new_bm()
        # texture u is the position round the whole section, as on the fuselage (0 bottom, 0.25 right,
        # 0.5 top, 0.75 left), so the stripes carry on from the fuselage across the firewall
        loft(bm, rr, close=False, uv_v=uv_v, uv_u_scale=len(idx) / k, uv_u_offset=idx[0] / k)
        ob = obj_from_bm(name, bm, ctx.col, pivot=(0, fs(0), y_pivot), mat=M["cowl"])
        # keep the four corners of each half where they are, or the halves part at both ends of the side seam
        add_subsurf(ob, ctx.subsurf).boundary_smooth = "PRESERVE_CORNERS"
        return ob
    upper = half("POWERPLANT.cowl_upper", list(range(q, 3 * q + 1)), "Upper cowl (removable)", "غطاء المحرك العلوي", COWL_TABLE[-1][3])
    lower = half("POWERPLANT.cowl_lower", list(range(3 * q, 5 * q + 1)), "Lower cowl", "غطاء المحرك السفلي", COWL_TABLE[-1][2])
    # openings cut through the nose cap: cooling-air inlets (both halves), landing light and carburettor air inlet (chin)
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
    y_cut = fs(-42)
    inlet_cutters = []
    for sx in (-1, 1):
        bm = new_bm()
        extrude_profile(bm, rounded_rect(INLET["w"], INLET["h"], 0.04, 5), X, Z, (sx * INLET["x"], y_cut, INLET["z"]), Y, 0.0, 0.27, smooth_sides=False)
        inlet_cutters.append(obj_from_bm(f"_cut_inlet_{'L' if sx > 0 else 'R'}", bm, ctx.cutters, smooth=False))
    light_outline = ellipse(LIGHT["r"], LIGHT["r"], 28)
    air_outline = rounded_rect(AIR_INLET["w"], AIR_INLET["h"], 0.018, 4)
    chin_cutters = []
    for name, outline, z0 in (("landing_light", light_outline, LIGHT["z"]), ("air_inlet", air_outline, AIR_INLET["z"])):
        deepest = max(chin_station(x, z0 + z) for x, z in outline)
        bm = new_bm()
        extrude_profile(bm, outline, X, Z, (0, y_cut, z0), Y, 0.0, fs(deepest + 0.8) - y_cut, smooth_sides=False)
        chin_cutters.append(obj_from_bm("_cut_" + name, bm, ctx.cutters, smooth=False))
    for ob, cutters in ((upper, inlet_cutters), (lower, inlet_cutters + chin_cutters)):
        add_solidify(ob, 0.008)          # closed manifold first, so the exact boolean is reliable
        for c in cutters:
            add_boolean(ob, c, "DIFFERENCE", c.name)
        add_edge_split(ob, 50)           # crisp shading round the openings and along the cowl edges
        _link(ob, grp)
    ctx.tag(upper, "POWERPLANT", "Upper engine cowl (quick-release fasteners, oil door)", "غطاء المحرك العلوي (مشابك سريعة، باب الزيت)", status="estimated", removable=True)
    ctx.tag(lower, "POWERPLANT", "Lower engine cowl (cooling inlets, landing light, carburetor air inlet)", "غطاء المحرك السفلي (فتحات التبريد وضوء الهبوط ومدخل هواء المكربن)", status="estimated")
    # inlet ducts (dark interior behind the inlets)
    for sx in (-1, 1):
        bm = new_bm()
        pts = rounded_rect(INLET["w"] + 0.012, INLET["h"] + 0.012, 0.045, 5)
        rings_ = [[Vector((sx * INLET["x"] + x, fs(-33.9) + d, INLET["z"] + z)) for x, z in pts] for d in (0.0, 0.20)]
        loft(bm, rings_, close=True, cap_start=False, cap_end=True, flip=True)
        duct = obj_from_bm(f"POWERPLANT.inlet_duct_{'L' if sx > 0 else 'R'}", bm, ctx.col, pivot=(sx * INLET["x"], fs(-33.9), U.PROP_Z), mat=M["interior_dark"])
        _link(duct, grp)
        ctx.tag(duct, "POWERPLANT", "Cooling air inlet (to the cylinder baffles)", "فتحة هواء التبريد", status="estimated")
    # landing light: a sealed-beam lamp set back in a recess of the chin, facing forward
    lens_y = fs(chin_station(0.0, LIGHT["z"] - LIGHT["r"])) + 0.012
    recess = _recess(ctx, "POWERPLANT.landing_light_recess", light_outline, LIGHT["z"], lens_y + 0.07)
    _link(recess, lower)
    ctx.tag(recess, "POWERPLANT", "Landing light recess", "تجويف ضوء الهبوط", status="estimated")
    light_at = (0.0, lens_y + 0.004, LIGHT["z"])
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.048, 0.0), (0.054, 0.012), (0.054, 0.03), (0.0, 0.055)], axis="Y", origin=light_at, segs=24)
    refl = obj_from_bm("ELECTRICAL.landing_light", bm, ctx.col, pivot=light_at, mat=M["chrome"])
    _link(refl, grp)
    ctx.tag(refl, "ELECTRICAL", "Landing light (cowl nose cap)", "ضوء الهبوط (مقدمة غطاء المحرك)", status="poh", ref="p.7-27",
            note="A single landing light is standard; dual landing/taxi lights were an option")
    lens_at = (0.0, lens_y, LIGHT["z"])
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.054, 0.0), (0.054, 0.004), (0.0, 0.004)], axis="Y", origin=lens_at, segs=24)
    lens = obj_from_bm("ELECTRICAL.landing_light_lens", bm, ctx.col, pivot=lens_at, mat=M["glass"])
    _link(lens, grp)
    ctx.tag(lens, "ELECTRICAL", "Landing light lens", "عدسة ضوء الهبوط", status="estimated")
    # carburettor air inlet: a short duct back to the face of the air filter (engine.build_accessories)
    duct = _recess(ctx, "INDUCTION.air_inlet_duct", air_outline, AIR_INLET["z"], air_filter_y() + 0.004, cap=False)
    _link(duct, lower)
    ctx.tag(duct, "INDUCTION", "Carburetor air inlet (lower cowl)", "مدخل هواء المكربن (غطاء المحرك السفلي)", status="poh", ref="p.7-24")
    # firewall
    bm = new_bm()
    ring = cowl_ring(0)
    loft(bm, [[Vector((p.x * 0.985, fs(0.6), p.z)) for p in ring], [Vector((p.x * 0.985, fs(1.6), p.z)) for p in ring]], close=True, cap_start=True, cap_end=True)
    fw = obj_from_bm("AIRFRAME.firewall", bm, ctx.col, pivot=(0, fs(1), COWL_TABLE[-1][4]), mat=M["bare_alu"])
    _link(fw, ctx.groups["AIRFRAME"])
    ctx.tag(fw, "AIRFRAME", "Firewall (stainless steel), FS 0 datum", "الجدار الناري (نقطة المرجع FS 0)", status="poh", ref="p.6-x datum")

def build_spinner_prop(ctx):
    M = ctx.mats
    grp = ctx.groups["POWERPLANT"]
    hub = Vector((0, fs(-36.4), U.PROP_Z))
    # spinner (pointed ogive) with backplate
    prof = []
    n = 16
    base_y = fs(SPINNER_BASE_FS)
    for i in range(n + 1):
        t = i / n
        prof.append((SPINNER_R * math.sin(t * math.pi / 2) ** 0.9, U.SPINNER_TIP_Y + (base_y - 0.012 - U.SPINNER_TIP_Y) * t))
    prof.append((SPINNER_R, base_y))
    bm = new_bm()
    revolve(bm, prof, axis="Y", origin=(0, 0, U.PROP_Z), segs=40, cap_start=False, cap_end=False)
    sp = obj_from_bm("POWERPLANT.spinner", bm, ctx.col, pivot=hub, mat=M["paint_white"])
    add_subsurf(sp, 1)
    _link(sp, grp)
    ctx.tag(sp, "POWERPLANT", "Spinner", "القمع الأمامي (السبينر)", status="estimated", spin_axis="y", spin_sign=-1, animate="prop")
    bm = new_bm()
    revolve(bm, [(0.0, base_y - 0.004), (SPINNER_R + 0.006, base_y - 0.004), (SPINNER_R + 0.006, base_y + 0.006), (0.0, base_y + 0.006)], axis="Y", origin=(0, 0, U.PROP_Z), segs=40)
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
    revolve(bm, [(0.0, fs(-38.2)), (0.07, fs(-38.2)), (0.07, fs(-34.8)), (0.0, fs(-34.8))], axis="Y", origin=(0, 0, U.PROP_Z), segs=24)
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
    # exhaust tailpipe: from the right end of the muffler, out through the lower cowl just ahead of the firewall,
    # pointing down, aft and slightly outboard
    ex_x = -0.16
    low = cowl_lower_z(-7.0, ex_x)
    pts = bezier(Vector((ex_x, MUFFLER_Y, MUFFLER_Z)), Vector((ex_x, MUFFLER_Y + 0.01, MUFFLER_Z - 0.13)),
                 Vector((ex_x - 0.01, fs(-7.5), low + 0.03)), Vector((ex_x - 0.03, fs(-4.0), low - 0.15)), 12)
    bm = new_bm()
    tube(bm, pts, 0.03, segs=14, cap=True)
    ex = obj_from_bm("ENGINE.exhaust_tailpipe", bm, ctx.col, pivot=pts[0], mat=M["exhaust"])
    _link(ex, grp)
    ctx.tag(ex, "ENGINE", "Exhaust tailpipe (from the muffler)", "ماسورة العادم", status="estimated")
