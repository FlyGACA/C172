"""Cowling, nose bowl with inlets and landing light, spinner, propeller, exhaust."""
import math
from mathutils import Vector

from . import units as U
from .units import fs
from .shapes import (parent_keep, new_bm, loft, revolve, tube, box, bezier, obj_from_bm, add_subsurf, add_boolean, add_solidify,
                     add_edge_split, superellipse, ellipse, rounded_rect, naca4, resample_loop, interp_table, extrude_profile)
from .profiles import interp_pchip
from .airframe import K_RING, FUS_TABLE

from .sections import COWL_TABLE, COWL_STATIONS, NOSE_FS, NOSE_MID_FS, NOSE_INNER, NOSE_MID, cowl_uv_v
NOSE_Y = fs(NOSE_FS)
SPINNER_R = 0.115                       # 9 in spinner (estimated)
SPINNER_BASE_FS = -34.6
# The propeller disc stands in the forward two thirds of the spinner, clear of the nose bowl: the blades leave the
# spinner through its side, and their trailing edges pass 5 cm ahead of the cowl (estimated from ramp photographs).
PROP_PLANE_FS = -38.6
TIP_BAND = 0.916           # the warning band at each tip begins at this part of the radius
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
    inner = [toward_axis(p, NOSE_INNER, NOSE_Y) for p in front]
    mid = [toward_axis(p, NOSE_MID, fs(NOSE_MID_FS)) for p in front]
    all_rings = [inner, mid] + rings
    nvs = len(all_rings)
    uv_v = cowl_uv_v()
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
        ob["keep_faces"] = True          # painted skin: see airframe.build_fuselage
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
    hub = Vector((0, fs(PROP_PLANE_FS), U.PROP_Z))
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
    sp = obj_from_bm("POWERPLANT.spinner", bm, ctx.col, pivot=hub, mat=M["paint_navy"])
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
    def blade(sign):
        rings = []
        R = U.PROP_R
        stations = [0.07, 0.10, 0.14, 0.20, 0.28, 0.37, 0.47, 0.57, 0.67, 0.77, 0.85, TIP_BAND, 0.965, 1.0]      # a ring where the tip band begins
        for rt in stations:
            r = R * rt
            if rt < 0.13:
                # the shank: nearly round where it leaves the hub
                c = 0.080; prof = resample_loop(ellipse(0.5, 0.40, 24), 24); beta = math.radians(60)
                prof = [(x + 0.5, y) for x, y in prof]
            else:
                # widest a little beyond half the radius, then a long taper to a rounded tip
                c = interp_table([(0.13, 0.082), (0.28, 0.112), (0.45, 0.128), (0.62, 0.130), (0.78, 0.116), (0.90, 0.094), (0.96, 0.072), (1.0, 0.034)], rt)[0]
                beta = math.radians(interp_table([(0.13, 54), (0.3, 37), (0.5, 26), (0.75, 18), (1.0, 13)], rt)[0])
                thick = interp_table([(0.13, 0.22), (0.3, 0.11), (0.6, 0.07), (1.0, 0.045)], rt)[0]
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
    # hub barrel: back to the crankshaft flange, which stands where it did (the barrel is the spacer between them)
    revolve(bm, [(0.0, fs(PROP_PLANE_FS - 1.8)), (0.07, fs(PROP_PLANE_FS - 1.8)), (0.07, fs(-34.8)), (0.0, fs(-34.8))], axis="Y", origin=(0, 0, U.PROP_Z), segs=24)
    prop = obj_from_bm("POWERPLANT.propeller", bm, ctx.col, pivot=hub, mat=M["prop_black"])
    # The face the pilot sees is flat black against glare, the forward face black with a sheen, each tip
    # carries a warning band 8 cm wide, and the hub is bare metal.
    prop.data.materials.append(M["prop_tip"]); prop.data.materials.append(M["bare_alu"]); prop.data.materials.append(M["prop_face"])
    R = U.PROP_R
    for poly in prop.data.polygons:
        xs = [abs(prop.data.vertices[v].co.x) for v in poly.vertices]
        if min(xs) > (TIP_BAND - 0.002) * R:
            poly.material_index = 1
        elif max(xs) < 0.075:
            poly.material_index = 2
        elif poly.normal.y < -0.15:
            poly.material_index = 3
    add_subsurf(prop, 1)
    prop["keep_faces"] = True            # the low quality level keeps every face: thinned out, the edge of the tip band wavers
    parent_keep(prop, sp)
    ctx.tag(prop, "POWERPLANT", "McCauley two-blade fixed-pitch propeller, 75 in", "مروحة ماكولي ثابتة الخطوة ذات شفرتين", status="poh", ref="p.1-3", spin_axis="y", spin_sign=-1, animate="prop",
            note="Blade planform, twist and airfoil are illustrative; the disc stands in the spinner, ahead of the nose bowl")
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
