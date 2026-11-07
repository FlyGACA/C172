"""Classic 1979 172N cockpit: instrument panel (six-pack, engine cluster, radio stack),
controls, yokes, pedals, seats, belts and interior trim. Layout estimated from the
period-correct reference photographs (C-FZKL panel); every control is its own object."""
import math
import bpy
from mathutils import Vector

from . import units as U
from .units import fs
from .shapes import (parent_keep, new_bm, loft, revolve, tube, cylinder, box, bezier, obj_from_bm, add_subsurf,
                     add_bevel, extrude_profile, rounded_rect, ellipse)
from .dials import cell_uv, MISC, CELLS

PANEL_Y = fs(19)          # instrument panel face (aft side), facing the pilot (+y)
PANEL_Z0, PANEL_Z1 = 1.37, 1.64
LOWER_Z0, LOWER_Z1 = 1.22, 1.37
D3 = 0.079; D2 = 0.057   # 3⅛ in and 2¼ in instrument face diameters

# (name, cell, x, z, diameter, needles)
INSTRUMENTS = [
    ("ASI", "ASI", 0.405, 1.565, D3, ["ASI"]),
    ("AI", None, 0.305, 1.565, D3, []),
    ("ALT", "ALT", 0.205, 1.565, D3, ["ALT_100", "ALT_1000", "ALT_10000"]),
    ("TC", "TC", 0.405, 1.465, D3, ["TC"]),
    ("DG", None, 0.305, 1.465, D3, []),
    ("VSI", "VSI", 0.205, 1.465, D3, ["VSI"]),
    ("CLOCK", "CLOCK", 0.490, 1.575, D2, ["CLOCK_H", "CLOCK_M"]),
    ("FUEL_L", "FUEL_L", 0.490, 1.49, D2, ["FUEL_L"]),
    ("FUEL_R", "FUEL_R", 0.490, 1.425, D2, ["FUEL_R"]),
    ("OIL_T", "OIL_T", 0.120, 1.59, D2, ["OIL_T"]),
    ("OIL_P", "OIL_P", 0.120, 1.525, D2, ["OIL_P"]),
    ("AMMETER", "AMMETER", 0.120, 1.46, D2, ["AMMETER"]),
    ("SUCTION", "SUCTION", 0.120, 1.395, D2, ["SUCTION"]),
    ("TACH", "TACH", -0.270, 1.565, D3, ["TACH"]),
    ("OAT", "CLOCK", -0.450, 1.58, D2, ["OAT"]),
]
RADIOS = [("COMNAV1", 1.615, 0.050), ("COMNAV2", 1.563, 0.050), ("ADF", 1.511, 0.050), ("XPDR", 1.459, 0.050), ("AUDIO", 1.417, 0.034), ("MARKER", 1.385, 0.028)]

def _uv_rect(bm, faces, region, flip_v=False):
    uv = bm.loops.layers.uv.active
    u0, v0, u1, v1 = region
    for f in faces:
        xs = [l.vert.co.x for l in f.loops]; zs = [l.vert.co.z for l in f.loops]
        mnx, mxx, mnz, mxz = min(xs), max(xs), min(zs), max(zs)
        for l in f.loops:
            tu = (l.vert.co.x - mnx) / max(1e-9, mxx - mnx); tv = (l.vert.co.z - mnz) / max(1e-9, mxz - mnz)
            l[uv].uv = (u0 + (u1 - u0) * tu, v0 + (v1 - v0) * tv)

def disc_face(bm, center, r, region, segs=40, y_offset=0.0, flip=False):
    """Flat disc facing +y, UV-mapped to a square atlas cell."""
    uv = bm.loops.layers.uv.active
    c = Vector(center) + Vector((0, y_offset, 0))
    verts = [bm.verts.new(c + Vector((r * math.cos(2 * math.pi * i / segs), 0, r * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    f = bm.faces.new(verts if flip else list(reversed(verts)))
    f.smooth = False
    u0, v0, u1, v1 = region
    for l in f.loops:
        d = l.vert.co - c
        l[uv].uv = (u0 + (u1 - u0) * (0.5 - 0.5 * d.x / r), v0 + (v1 - v0) * (0.5 + 0.5 * d.z / r))
    return f

def quad_face(bm, center, w, h, region, y_offset=0.0):
    uv = bm.loops.layers.uv.active
    c = Vector(center) + Vector((0, y_offset, 0))
    pts = [c + Vector((-w / 2, 0, -h / 2)), c + Vector((w / 2, 0, -h / 2)), c + Vector((w / 2, 0, h / 2)), c + Vector((-w / 2, 0, h / 2))]
    verts = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(list(reversed(verts))); f.smooth = False
    u0, v0, u1, v1 = region
    for l in f.loops:
        d = l.vert.co - c
        l[uv].uv = (u0 + (u1 - u0) * (0.5 - 0.5 * d.x / (w / 2)), v0 + (v1 - v0) * (0.5 + 0.5 * d.z / (h / 2)))
    return f

def needle(ctx, name, center, length, width, mat, label_en, label_ar, kind, y_off=0.012, tail=0.0, thickness=0.0015):
    bm = new_bm()
    c = Vector(center) + Vector((0, y_off, 0))
    # tapered pointer from the hub upward (+z), optional tail
    pts = [(-width / 2, -tail), (width / 2, -tail), (width / 2 * 0.9, length * 0.6), (width * 0.12, length), (-width * 0.12, length), (-width / 2 * 0.9, length * 0.6)]
    extrude_profile(bm, pts, Vector((1, 0, 0)), Vector((0, 0, 1)), c, Vector((0, 1, 0)), 0, thickness, smooth_sides=False)
    ob = obj_from_bm(name, bm, ctx.col, pivot=c, mat=mat, smooth=False)
    parent_keep(ob, ctx.groups["PANEL"])
    ctx.tag(ob, "PANEL", label_en, label_ar, status="poh", needle=kind, spin_axis="y", spin_sign=-1, animate="needle")
    return ob

def build_panel(ctx):
    M = ctx.mats
    grp = ctx.groups["PANEL"]
    dials = ctx.mats["dials"]; misc = ctx.mats["panel_misc"]
    # ---- upper panel plate (grey/black crinkle) and lower wood-grain panel
    bm = new_bm()
    box(bm, (1.06, 0.012, PANEL_Z1 - PANEL_Z0), center=(0, PANEL_Y - 0.006, (PANEL_Z0 + PANEL_Z1) / 2))
    panel = obj_from_bm("PANEL.upper_panel", bm, ctx.col, pivot=(0, PANEL_Y, PANEL_Z0), mat=M["panel_grey"], smooth=False)
    add_bevel(panel, 0.004, 2)
    parent_keep(panel, grp)
    ctx.tag(panel, "PANEL", "Instrument panel (upper, flight & engine instruments)", "لوحة العدادات العلوية", status="estimated")
    bm = new_bm()
    box(bm, (1.06, 0.03, LOWER_Z1 - LOWER_Z0), center=(0, PANEL_Y - 0.0, (LOWER_Z0 + LOWER_Z1) / 2))
    quad_face(bm, (0, PANEL_Y + 0.018, (LOWER_Z0 + LOWER_Z1) / 2), 1.06, LOWER_Z1 - LOWER_Z0, MISC["WOOD"])
    lower = obj_from_bm("PANEL.lower_panel", bm, ctx.col, pivot=(0, PANEL_Y, LOWER_Z0), mat=M["woodgrain"], smooth=False)
    lower.data.materials.append(misc)
    lower.data.polygons[-1].material_index = 1
    parent_keep(lower, grp)
    ctx.tag(lower, "PANEL", "Lower panel (switches, engine controls) — wood-grain laminate", "اللوحة السفلية (المفاتيح وأدوات التحكم بالمحرك)", status="estimated")
    # ---- instruments
    for name, cell, x, z, dia, needles in INSTRUMENTS:
        c = (x, PANEL_Y, z)
        # bezel ring
        bm = new_bm()
        ro = dia / 2 + 0.006
        revolve(bm, [(dia / 2 - 0.002, 0.0), (ro, 0.0), (ro, 0.012), (ro - 0.004, 0.016), (dia / 2 - 0.002, 0.016)], axis="Y", origin=c, segs=40, cap_start=False, cap_end=False)
        bez = obj_from_bm(f"PANEL.{name}.bezel", bm, ctx.col, pivot=c, mat=M["bezel_black"])
        parent_keep(bez, grp)
        # screws
        for a in (45, 135, 225, 315):
            pass
        ctx.tag(bez, "PANEL", f"{name} bezel", f"إطار عداد {name}", status="estimated", instrument=name)
        bm = new_bm()
        if name == "AI":
            disc_face(bm, c, dia / 2 * 0.98, cell_uv("AI_BALL"), y_offset=0.004)
            ball = obj_from_bm("PANEL.AI.ball", bm, ctx.col, pivot=(x, PANEL_Y + 0.004, z), mat=dials, smooth=False)
            parent_keep(ball, grp)
            ctx.tag(ball, "PANEL", "Attitude indicator — gyro horizon (vacuum)", "مؤشر الوضع — الأفق الجيروسكوبي", status="poh", ref="p.7-34", animate="ai_ball", spin_axis="y", spin_sign=-1)
            bm = new_bm()
            disc_face(bm, c, dia / 2 * 1.0, cell_uv("AI_MASK"), y_offset=0.009)
            mask = obj_from_bm("PANEL.AI.mask", bm, ctx.col, pivot=c, mat=ctx.mats["dials_alpha"], smooth=False)
            parent_keep(mask, grp)
            ctx.tag(mask, "PANEL", "Attitude indicator (miniature aeroplane)", "مؤشر الوضع", status="poh", ref="p.7-34", instrument="AI")
        elif name == "DG":
            disc_face(bm, c, dia / 2 * 0.98, cell_uv("DG_CARD"), y_offset=0.004)
            card = obj_from_bm("PANEL.DG.card", bm, ctx.col, pivot=(x, PANEL_Y + 0.004, z), mat=dials, smooth=False)
            parent_keep(card, grp)
            ctx.tag(card, "PANEL", "Directional gyro — compass card (vacuum)", "الجيروسكوب الاتجاهي — بطاقة البوصلة", status="poh", ref="p.7-34", animate="dg_card", spin_axis="y", spin_sign=-1)
            bm = new_bm()
            disc_face(bm, c, dia / 2 * 1.0, cell_uv("DG_MASK"), y_offset=0.009)
            mask = obj_from_bm("PANEL.DG.mask", bm, ctx.col, pivot=c, mat=ctx.mats["dials_alpha"], smooth=False)
            parent_keep(mask, grp)
            ctx.tag(mask, "PANEL", "Directional gyro (heading indicator)", "مؤشر الاتجاه", status="poh", ref="p.7-34", instrument="DG")
        else:
            disc_face(bm, c, dia / 2 * 0.99, cell_uv(cell), y_offset=0.004)
            face = obj_from_bm(f"PANEL.{name}.face", bm, ctx.col, pivot=c, mat=dials, smooth=False)
            parent_keep(face, grp)
            ctx.tag(face, "PANEL", f"{name} dial", f"قرص عداد {name}", status="poh", instrument=name, ref="Fig 2-2 / 2-3 markings")
        # glass
        bm = new_bm()
        revolve(bm, [(0.0, 0.016), (dia / 2 * 0.6, 0.0155), (dia / 2 - 0.002, 0.013)], axis="Y", origin=c, segs=40, cap_start=False, cap_end=False)
        gl = obj_from_bm(f"PANEL.{name}.glass", bm, ctx.col, pivot=c, mat=M["instrument_glass"])
        parent_keep(gl, grp)
        ctx.tag(gl, "PANEL", "Instrument glass", "زجاج العداد", status="estimated", kind="glass")
        # needles
        for nd in needles:
            L = dia / 2 * 0.82; W = 0.005; mat = M["paint_white"]; tail = 0.0; yo = 0.008
            if nd == "ALT_1000": L = dia / 2 * 0.55; W = 0.009
            if nd == "ALT_10000": L = dia / 2 * 0.9; W = 0.0025
            if nd == "TC": continue
            if nd == "CLOCK_H": L = dia / 2 * 0.5; W = 0.004
            if nd == "CLOCK_M": L = dia / 2 * 0.8; W = 0.003; yo = 0.0095
            if nd in ("FUEL_L", "FUEL_R", "OIL_T", "OIL_P", "AMMETER", "SUCTION", "OAT"): L = dia / 2 * 0.8; W = 0.004
            needle(ctx, f"PANEL.{name}.needle_{nd}", c, L, W, mat, f"{name} needle ({nd})", f"إبرة {name}", nd, y_off=yo, tail=tail)
        if name == "TC":
            # miniature aeroplane needle (rotates about the hub) and the inclinometer ball
            bm = new_bm()
            cc = Vector(c) + Vector((0, 0.009, 0))
            box(bm, (dia * 0.7, 0.0015, 0.004), center=cc + Vector((0, 0, 0.002)))
            box(bm, (0.006, 0.0015, 0.018), center=cc + Vector((0, 0, 0.0)))
            box(bm, (0.016, 0.0015, 0.004), center=cc + Vector((0, 0, -0.012)))
            tcn = obj_from_bm("PANEL.TC.needle_TC", bm, ctx.col, pivot=cc, mat=M["paint_white"], smooth=False)
            parent_keep(tcn, grp)
            ctx.tag(tcn, "PANEL", "Turn coordinator miniature aeroplane (electric gyro)", "طائرة مصغرة لمنسق الانعطاف", status="poh", ref="p.7-34", needle="TC", spin_axis="y", spin_sign=-1, animate="needle")
            bm = new_bm()
            revolve(bm, [(0.0, -0.004), (0.0045, -0.004), (0.0045, 0.004), (0.0, 0.004)], axis="Y", origin=(x, PANEL_Y + 0.009, z - dia * 0.3), segs=12)
            ballo = obj_from_bm("PANEL.TC.ball", bm, ctx.col, pivot=(x, PANEL_Y + 0.009, z - dia * 0.3), mat=M["black_plastic"])
            parent_keep(ballo, grp)
            ctx.tag(ballo, "PANEL", "Inclinometer ball (slip/skid)", "كرة الانزلاق", status="poh", ref="p.7-34", animate="tc_ball")
    # ---- radio stack (ARC 300-series style), period-correct 1979 layout
    for region, z, h in RADIOS:
        bm = new_bm()
        box(bm, (0.165, 0.025, h), center=(-0.045, PANEL_Y - 0.0125, z))
        quad_face(bm, (-0.045, PANEL_Y + 0.003, z), 0.165, h, MISC[region])
        ob = obj_from_bm(f"PANEL.radio_{region}", bm, ctx.col, pivot=(-0.045, PANEL_Y, z), mat=M["bezel_black"], smooth=False)
        ob.data.materials.append(misc); ob.data.polygons[-1].material_index = 1
        parent_keep(ob, grp)
        labels = {"COMNAV1": ("NAV/COM 1 (360-channel COM, VOR/LOC NAV)", "جهاز الملاحة والاتصال 1"), "COMNAV2": ("NAV/COM 2", "جهاز الملاحة والاتصال 2"), "ADF": ("ADF receiver", "مستقبل ADF"),
                  "XPDR": ("Transponder (mode A/C)", "جهاز الاستجابة"), "AUDIO": ("Audio control panel", "لوحة التحكم الصوتي"), "MARKER": ("Marker beacon lights", "أضواء منارات العلامات")}
        ctx.tag(ob, "PANEL", labels[region][0], labels[region][1], status="estimated", note="Period-correct radio stack representation; specific installed avionics vary by serial number")
        # knobs
        for kx in (-0.07, 0.07):
            bm = new_bm()
            revolve(bm, [(0.0, 0.0), (0.008, 0.0), (0.008, 0.012), (0.0, 0.012)], axis="Y", origin=(-0.045 + kx, PANEL_Y, z - h * 0.1), segs=14)
            kn = obj_from_bm(f"PANEL.radio_{region}.knob_{'R' if kx > 0 else 'L'}", bm, ctx.col, pivot=(-0.045 + kx, PANEL_Y, z), mat=M["black_plastic"])
            parent_keep(kn, ob)
            ctx.tag(kn, "PANEL", "Frequency/volume knob", "مقبض التردد", status="estimated", animate="knob", spin_axis="y", spin_sign=-1)
    # ---- annunciator, flap indicator, hour meter, placards
    for region, x, z, w, h, en, ar in [("LOW_VOLT", -0.36, 1.50, 0.07, 0.022, "LOW VOLTAGE warning light", "ضوء تحذير انخفاض الجهد"),
                                       ("FLAP_IND", -0.22, 1.335, 0.06, 0.03, "Wing flap position indicator", "مؤشر وضع القلابات"),
                                       ("HOURMETER", -0.30, 1.465, 0.05, 0.022, "Hour meter", "عداد الساعات"),
                                       ("PLACARD_SPEED", 0.30, 1.395, 0.20, 0.03, "Limitations placard (POH Section 2)", "لوحة القيود"),
                                       ("IGNITION", 0.43, 1.31, 0.04, 0.04, "Ignition switch placard OFF-R-L-BOTH-START", "لوحة مفتاح الإشعال")]:
        bm = new_bm()
        quad_face(bm, (x, PANEL_Y + 0.003, z), w, h, MISC[region])
        ob = obj_from_bm(f"PANEL.{region.lower()}", bm, ctx.col, pivot=(x, PANEL_Y, z), mat=misc, smooth=False)
        parent_keep(ob, grp)
        ctx.tag(ob, "PANEL", en, ar, status="poh" if region in ("LOW_VOLT", "PLACARD_SPEED") else "estimated", ref="p.7-26" if region == "LOW_VOLT" else "")
    # ---- switches and engine controls on the lower panel
    def rocker(name, x, z, en, ar, red=False, w=0.013):
        bm = new_bm()
        box(bm, (w + 0.006, 0.006, 0.030), center=(x, PANEL_Y + 0.0145, z))
        box(bm, (w, 0.010, 0.022), center=(x, PANEL_Y + 0.020, z + 0.003))
        ob = obj_from_bm(name, bm, ctx.col, pivot=(x, PANEL_Y + 0.015, z), mat=M["knob_red" if red else "black_plastic"], smooth=False)
        parent_keep(ob, grp)
        ctx.tag(ob, "PANEL", en, ar, status="poh", ref="p.7-25/27", animate="switch", hinge_axis="x", hinge_sign=1, range_deg=[-15, 15])
        return ob
    rocker("PANEL.master_bat", 0.505, 1.30, "Master switch — BAT half (red split rocker)", "المفتاح الرئيسي — البطارية", red=True, w=0.010)
    rocker("PANEL.master_alt", 0.492, 1.30, "Master switch — ALT half", "المفتاح الرئيسي — المولد", red=True, w=0.010)
    for i, (nm, en, ar) in enumerate([("beacon", "Beacon light switch", "مفتاح المنارة"), ("nav_lights", "Navigation lights switch", "مفتاح أضواء الملاحة"), ("strobe", "Strobe lights switch", "مفتاح أضواء الوميض"),
                                      ("taxi_light", "Taxi light switch", "مفتاح ضوء التدرج"), ("landing_light", "Landing light switch", "مفتاح ضوء الهبوط"), ("pitot_heat", "Pitot heat switch", "مفتاح تسخين البيتو"),
                                      ("avionics_master", "Avionics power switch", "مفتاح طاقة الأجهزة الإلكترونية")]):
        rocker(f"PANEL.switch_{nm}", 0.37 - i * 0.03, 1.30, en, ar)
    # ignition key switch
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, 0.012), (0.006, 0.016), (0.0, 0.016)], axis="Y", origin=(0.43, PANEL_Y, 1.29), segs=20)
    box(bm, (0.004, 0.02, 0.02), center=(0.43, PANEL_Y + 0.022, 1.282))
    ign = obj_from_bm("PANEL.ignition_switch", bm, ctx.col, pivot=(0.43, PANEL_Y, 1.29), mat=M["black_plastic"])
    parent_keep(ign, grp)
    ctx.tag(ign, "IGNITION", "Ignition switch (key) OFF-R-L-BOTH-START", "مفتاح الإشعال", status="poh", ref="p.7-25", animate="ignition", spin_axis="y", spin_sign=-1, range_deg=[-70, 70])
    # push-pull controls: carb heat, throttle, mixture (vernier), primer, cabin heat/air
    def pull_knob(name, x, z, r, color, en, ar, travel=0.07, ring=False):
        bm = new_bm()
        tube(bm, [Vector((x, PANEL_Y - 0.05, z)), Vector((x, PANEL_Y + 0.045, z))], 0.004, segs=10)
        revolve(bm, [(0.0, 0.045), (r * 0.8, 0.045), (r, 0.052), (r, 0.066), (r * 0.7, 0.070), (0.0, 0.070)], axis="Y", origin=(x, PANEL_Y, z), segs=24)
        if ring:
            revolve(bm, [(0.004, 0.015), (r * 0.75, 0.015), (r * 0.75, 0.03), (0.004, 0.03)], axis="Y", origin=(x, PANEL_Y, z), segs=24)
        ob = obj_from_bm(name, bm, ctx.col, pivot=(x, PANEL_Y, z), mat=color)
        parent_keep(ob, grp)
        ctx.tag(ob, "PANEL", en, ar, status="poh", ref="p.7-23", animate="pull", travel_m=travel)
        bm = new_bm()
        revolve(bm, [(0.0, 0.0), (r * 0.9, 0.0), (r * 0.9, 0.014), (0.0, 0.014)], axis="Y", origin=(x, PANEL_Y, z), segs=20)
        base = obj_from_bm(name + "_bushing", bm, ctx.col, pivot=(x, PANEL_Y, z), mat=M["chrome"])
        parent_keep(base, grp)
        return ob
    pull_knob("PANEL.carb_heat", 0.095, 1.30, 0.012, M["black_plastic"], "Carburetor heat control (pull = ON)", "تحكم تسخين المكربن (اسحب = تشغيل)")
    pull_knob("PANEL.throttle", 0.0, 1.295, 0.021, M["black_plastic"], "Throttle (push = open), friction lock", "الخانق (ادفع = فتح)", travel=0.085)
    pull_knob("PANEL.mixture", -0.095, 1.30, 0.014, M["knob_red"], "Mixture control (vernier, red) — pull = lean / idle cut-off", "تحكم الخليط (أحمر)", ring=True)
    pull_knob("PANEL.primer", 0.47, 1.255, 0.010, M["chrome"], "Engine primer (pull-push, lock)", "مضخة التحضير", travel=0.06)
    pull_knob("PANEL.cabin_heat", -0.34, 1.26, 0.010, M["black_plastic"], "Cabin heat control", "تحكم تدفئة المقصورة")
    pull_knob("PANEL.cabin_air", -0.40, 1.26, 0.010, M["black_plastic"], "Cabin air control", "تحكم هواء المقصورة")
    # flap switch lever (electric, pre-select) under the indicator
    bm = new_bm()
    box(bm, (0.012, 0.03, 0.045), center=(-0.22, PANEL_Y + 0.02, 1.29))
    box(bm, (0.02, 0.012, 0.012), center=(-0.22, PANEL_Y + 0.035, 1.27))
    fl = obj_from_bm("PANEL.flap_switch", bm, ctx.col, pivot=(-0.22, PANEL_Y, 1.305), mat=M["grey_plastic"], smooth=False)
    parent_keep(fl, grp)
    ctx.tag(fl, "PANEL", "Wing flap switch (pre-select 0/10/20/30)", "مفتاح القلابات", status="poh", ref="p.7-9", animate="flap_switch", hinge_axis="x", hinge_sign=1, range_deg=[-30, 0])
    # circuit breakers (two rows)
    for i in range(10):
        for row, z in enumerate((1.345, 1.325)):
            if row == 1 and i > 6: continue
            bm = new_bm()
            revolve(bm, [(0.0, 0.0), (0.0045, 0.0), (0.0045, 0.006), (0.0, 0.006)], axis="Y", origin=(-0.29 - i * 0.022, PANEL_Y, z), segs=10)
            cb = obj_from_bm(f"PANEL.breaker_{row}_{i}", bm, ctx.col, pivot=(-0.29 - i * 0.022, PANEL_Y, z), mat=M["paint_white"])
            parent_keep(cb, grp)
            ctx.tag(cb, "ELECTRICAL", "Push-to-reset circuit breaker", "قاطع دائرة", status="poh", ref="p.7-27")
    # magnetic compass on the windshield centre post
    bm = new_bm()
    box(bm, (0.07, 0.07, 0.06), center=(0, fs(10), 1.86))
    quad_face(bm, (0, fs(10) + 0.038, 1.86), 0.05, 0.02, MISC["COMPASS"])
    comp = obj_from_bm("PANEL.magnetic_compass", bm, ctx.col, pivot=(0, fs(10), 1.86), mat=M["black_plastic"], smooth=False)
    comp.data.materials.append(misc); comp.data.polygons[-1].material_index = 1
    parent_keep(comp, grp)
    ctx.tag(comp, "PANEL", "Magnetic compass", "البوصلة المغناطيسية", status="poh", ref="p.7-x")
    # glareshield: padded roll along the aft edge and a sloping top
    bm = new_bm()
    tube(bm, [Vector((-0.53, PANEL_Y - 0.01, PANEL_Z1 + 0.02)), Vector((-0.3, PANEL_Y - 0.03, PANEL_Z1 + 0.03)), Vector((0, PANEL_Y - 0.035, PANEL_Z1 + 0.035)), Vector((0.3, PANEL_Y - 0.03, PANEL_Z1 + 0.03)), Vector((0.53, PANEL_Y - 0.01, PANEL_Z1 + 0.02))], 0.028, segs=14)
    rings = []
    for t in (0.0, 1.0):
        y = PANEL_Y - 0.02 - t * 0.40; z = PANEL_Z1 + 0.03 - t * 0.0 + t * 0.07
        rings.append([Vector((-0.52, y, z)), Vector((0.52, y, z))])
    verts = [[bm.verts.new(p) for p in r] for r in rings]
    f = bm.faces.new([verts[0][0], verts[0][1], verts[1][1], verts[1][0]]); f.smooth = True
    gs = obj_from_bm("INTERIOR.glareshield", bm, ctx.col, pivot=(0, PANEL_Y, PANEL_Z1), mat=M["vinyl_black"])
    parent_keep(gs, ctx.groups["INTERIOR"])
    ctx.tag(gs, "INTERIOR", "Glareshield (padded)", "واقي الوهج", status="estimated")

def build_controls(ctx):
    M = ctx.mats
    grp = ctx.groups["INTERIOR"]
    # yokes (ram's horn) on push-pull shafts through the panel
    for side, x in (("L", 0.305), ("R", -0.305)):
        hub = Vector((x, PANEL_Y + 0.26, 1.27))
        bm = new_bm()
        tube(bm, [Vector((x, PANEL_Y - 0.1, 1.27)), hub - Vector((0, 0.03, 0))], 0.013, segs=14)
        shaft = obj_from_bm(f"INTERIOR.yoke_shaft_{side}", bm, ctx.col, pivot=(x, PANEL_Y, 1.27), mat=M["chrome"])
        parent_keep(shaft, grp)
        ctx.tag(shaft, "INTERIOR", "Control yoke shaft (elevator push/pull)", "عمود عجلة القيادة", status="estimated", animate="yoke_shaft")
        bm = new_bm()
        box(bm, (0.09, 0.05, 0.055), center=hub)
        for sgn in (-1, 1):
            pts = bezier(hub + Vector((sgn * 0.045, 0, 0)), hub + Vector((sgn * 0.14, 0.0, 0.0)), hub + Vector((sgn * 0.165, 0.03, 0.12)), hub + Vector((sgn * 0.12, 0.09, 0.15)), 14)
            tube(bm, pts, 0.014, segs=12)
        yoke = obj_from_bm(f"INTERIOR.yoke_{side}", bm, ctx.col, pivot=hub, mat=M["vinyl_black"])
        add_subsurf(yoke, 1)
        parent_keep(yoke, shaft)
        ctx.tag(yoke, "INTERIOR", f"Control yoke ({'pilot' if side == 'L' else 'co-pilot'}) — ailerons by rotation, elevator by push/pull", "عجلة القيادة " + ("(الطيار)" if side == "L" else "(مساعد الطيار)"), status="poh", ref="p.7-6", animate="yoke", spin_axis="y", spin_sign=-1, range_deg=[-90, 90])
        # rudder pedals with toe brakes
        for px in (-0.13, 0.13):
            bm = new_bm()
            box(bm, (0.09, 0.012, 0.13), center=(x + px, fs(6), 1.0))
            tube(bm, [Vector((x + px, fs(6), 0.93)), Vector((x + px, fs(14), 0.90))], 0.008, segs=8)
            ped = obj_from_bm(f"INTERIOR.pedal_{side}_{'R' if px > 0 else 'L'}", bm, ctx.col, pivot=(x + px, fs(6), 0.93), mat=M["steel"], smooth=False)
            parent_keep(ped, grp)
            ctx.tag(ped, "INTERIOR", "Rudder pedal with toe brake", "دواسة الدفة مع فرامل", status="poh", ref="p.7-6", animate="pedal", hinge_axis="x", hinge_sign=1, range_deg=[-12, 12])
    # trim wheel on the pedestal below the panel
    bm = new_bm()
    box(bm, (0.16, 0.20, 0.32), center=(-0.05, PANEL_Y + 0.06, 1.06))
    ped = obj_from_bm("INTERIOR.pedestal", bm, ctx.col, pivot=(-0.05, PANEL_Y, 0.9), mat=M["panel_grey"], smooth=False)
    add_bevel(ped, 0.01, 2)
    parent_keep(ped, grp)
    ctx.tag(ped, "INTERIOR", "Control pedestal", "قاعدة أدوات التحكم", status="estimated")
    bm = new_bm()
    revolve(bm, [(0.0, -0.012), (0.075, -0.012), (0.08, -0.004), (0.08, 0.004), (0.075, 0.012), (0.0, 0.012)], axis="X", origin=(-0.13, PANEL_Y + 0.17, 1.14), segs=36)
    tw = obj_from_bm("INTERIOR.trim_wheel", bm, ctx.col, pivot=(-0.13, PANEL_Y + 0.17, 1.14), mat=M["black_plastic"])
    parent_keep(tw, grp)
    ctx.tag(tw, "INTERIOR", "Elevator trim wheel (nose up / nose down) with position indicator", "عجلة موازنة الرافع", status="poh", ref="p.7-6", animate="trim_wheel", spin_axis="x", spin_sign=1)
    # fuel selector on the floor between the seats
    bm = new_bm()
    box(bm, (0.17, 0.15, 0.012), center=(0, fs(44), 0.886))
    sel_base = obj_from_bm("FUEL.selector_plate", bm, ctx.col, pivot=(0, fs(44), 0.88), mat=M["panel_grey"], smooth=False)
    parent_keep(sel_base, grp)
    ctx.tag(sel_base, "FUEL", "Fuel selector placard plate (LEFT · BOTH · RIGHT · OFF)", "لوحة محدد الوقود", status="poh", ref="p.7-28")
    bm = new_bm()
    box(bm, (0.028, 0.10, 0.012), center=(0, fs(44) - 0.02, 0.90))
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.025), (0.0, 0.025)], axis="Z", origin=(0, fs(44), 0.892), segs=20)
    sel = obj_from_bm("FUEL.selector_handle", bm, ctx.col, pivot=(0, fs(44), 0.892), mat=M["knob_red"], smooth=False)
    parent_keep(sel, grp)
    ctx.tag(sel, "FUEL", "Fuel selector valve handle (shown on BOTH)", "مقبض صمام اختيار الوقود", status="poh", ref="p.7-28", animate="fuel_selector", spin_axis="z", spin_sign=1, positions={"LEFT": -90, "BOTH": 0, "RIGHT": 90, "OFF": 180})
    # parking brake handle under the panel, left
    bm = new_bm()
    tube(bm, [Vector((0.25, PANEL_Y + 0.0, 1.20)), Vector((0.25, PANEL_Y + 0.06, 1.19))], 0.006, segs=8)
    revolve(bm, [(0.0, 0.06), (0.012, 0.06), (0.012, 0.08), (0.0, 0.08)], axis="Y", origin=(0.25, PANEL_Y, 1.19), segs=12)
    pb = obj_from_bm("INTERIOR.parking_brake", bm, ctx.col, pivot=(0.25, PANEL_Y, 1.20), mat=M["black_plastic"])
    parent_keep(pb, grp)
    ctx.tag(pb, "INTERIOR", "Parking brake handle", "مقبض فرامل الوقوف", status="poh", ref="p.7-10", animate="pull", travel_m=0.05)

def strap(bm, pts, width, thick=0.003):
    """Flat webbing strip along a polyline (parallel transport)."""
    n = len(pts); rings = []
    nrm = None
    for i in range(n):
        if i == 0: t = (pts[1] - pts[0]).normalized()
        elif i == n - 1: t = (pts[-1] - pts[-2]).normalized()
        else: t = (pts[i + 1] - pts[i - 1]).normalized()
        if nrm is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((0, 1, 0))
            nrm = t.cross(up).normalized()
        else:
            nrm = (nrm - t * nrm.dot(t)).normalized()
        b = t.cross(nrm)
        rings.append([pts[i] + nrm * width / 2 + b * thick / 2, pts[i] - nrm * width / 2 + b * thick / 2, pts[i] - nrm * width / 2 - b * thick / 2, pts[i] + nrm * width / 2 - b * thick / 2])
    loft(bm, rings, close=True, cap_start=True, cap_end=True)

def build_seats(ctx):
    M = ctx.mats
    grp = ctx.groups["INTERIOR"]
    def seat(name, x, y0, w, en, ar):
        bm = new_bm()
        box(bm, (w, 0.46, 0.09), center=(x, y0 + 0.23, 1.035))
        pan = obj_from_bm(name + ".cushion", bm, ctx.col, pivot=(x, y0, 1.0), mat=M["leather_tan"], smooth=False)
        add_bevel(pan, 0.03, 4); add_subsurf(pan, 1)
        parent_keep(pan, grp)
        ctx.tag(pan, "INTERIOR", en + " — seat cushion", ar + " — وسادة المقعد", status="estimated")
        bm = new_bm()
        # back, tilted 14° aft about its lower edge
        box(bm, (w, 0.08, 0.52), center=(x, y0 + 0.44, 1.07 + 0.26))
        back = obj_from_bm(name + ".back", bm, ctx.col, pivot=(x, y0 + 0.44, 1.07), mat=M["leather_tan"], smooth=False)
        back.rotation_euler = (math.radians(-14), 0, 0)
        add_bevel(back, 0.03, 4); add_subsurf(back, 1)
        parent_keep(back, grp)
        ctx.tag(back, "INTERIOR", en + " — seat back", ar + " — ظهر المقعد", status="estimated", animate="seat_back", hinge_axis="x", hinge_sign=1, range_deg=[-25, 0])
        bm = new_bm()
        for sx in (-w / 2 + 0.05, w / 2 - 0.05):
            tube(bm, [Vector((x + sx, y0 + 0.08, 0.90)), Vector((x + sx, y0 + 0.08, 1.0))], 0.012, segs=8)
            tube(bm, [Vector((x + sx, y0 + 0.40, 0.90)), Vector((x + sx, y0 + 0.40, 1.0))], 0.012, segs=8)
            tube(bm, [Vector((x + sx, y0 + 0.02, 0.905)), Vector((x + sx, y0 + 0.46, 0.905))], 0.010, segs=8)
        legs = obj_from_bm(name + ".frame", bm, ctx.col, pivot=(x, y0, 0.9), mat=M["steel"])
        parent_keep(legs, grp)
        ctx.tag(legs, "INTERIOR", en + " — seat frame and rails", ar + " — إطار المقعد", status="estimated")
        # lap belt and shoulder harness
        bm = new_bm()
        pts = bezier(Vector((x - w / 2 + 0.02, y0 + 0.30, 0.98)), Vector((x - w / 2 + 0.06, y0 + 0.26, 1.10)), Vector((x + w / 2 - 0.06, y0 + 0.26, 1.10)), Vector((x + w / 2 - 0.02, y0 + 0.30, 0.98)), 16)
        strap(bm, pts, 0.048)
        belt = obj_from_bm(name + ".lap_belt", bm, ctx.col, pivot=(x, y0 + 0.3, 1.0), mat=M["belt"])
        parent_keep(belt, grp)
        ctx.tag(belt, "INTERIOR", en + " — lap belt", ar + " — حزام الحضن", status="poh", ref="p.7-8")
        bm = new_bm()
        box(bm, (0.05, 0.02, 0.03), center=(x + 0.02, y0 + 0.27, 1.105))
        buckle = obj_from_bm(name + ".buckle", bm, ctx.col, pivot=(x, y0 + 0.3, 1.1), mat=M["chrome"], smooth=False)
        parent_keep(buckle, grp)
        ctx.tag(buckle, "INTERIOR", "Seat belt buckle", "مشبك حزام الأمان", status="estimated")
        return pan
    seat("INTERIOR.seat_pilot", 0.30, fs(42), 0.42, "Pilot seat (adjustable)", "مقعد الطيار")
    seat("INTERIOR.seat_copilot", -0.30, fs(42), 0.42, "Co-pilot seat (adjustable)", "مقعد مساعد الطيار")
    seat("INTERIOR.seat_rear", 0.0, fs(80), 0.84, "Rear bench seat", "المقعد الخلفي")
    # shoulder harnesses for the front seats, from the roof rail behind the door
    for side, x in (("L", 0.30), ("R", -0.30)):
        bm = new_bm()
        o = 1 if side == "L" else -1   # harness comes from the roof rail on the door side
        pts = bezier(Vector((x + o * 0.2, fs(55), 1.90)), Vector((x + o * 0.15, fs(52), 1.70)), Vector((x + o * 0.1, fs(50), 1.45)), Vector((x - o * 0.06, fs(50), 1.13)), 18)
        strap(bm, pts, 0.048)
        sh = obj_from_bm(f"INTERIOR.shoulder_harness_{side}", bm, ctx.col, pivot=pts[0], mat=M["belt"])
        parent_keep(sh, grp)
        ctx.tag(sh, "INTERIOR", "Shoulder harness (inertia reel)", "حزام الكتف", status="poh", ref="p.7-8")
    # door armrests and inner handles (parented to the doors so they swing with them)
    for side, sgn in (("L", 1), ("R", -1)):
        door = bpy.data.objects.get(f"AIRFRAME.door_{side}")
        if not door:
            continue
        bm = new_bm()
        box(bm, (0.05, 0.30, 0.05), center=(sgn * 0.47, fs(34), 1.16))
        arm = obj_from_bm(f"INTERIOR.armrest_{side}", bm, ctx.col, pivot=(sgn * 0.47, fs(34), 1.16), mat=M["leather_tan"], smooth=False)
        add_bevel(arm, 0.012, 3)
        parent_keep(arm, door)
        ctx.tag(arm, "INTERIOR", "Door armrest", "مسند ذراع الباب", status="estimated")
        bm = new_bm()
        box(bm, (0.015, 0.09, 0.02), center=(sgn * 0.49, fs(44), 1.24))
        ih = obj_from_bm(f"INTERIOR.door_inner_handle_{side}", bm, ctx.col, pivot=(sgn * 0.49, fs(44), 1.24), mat=M["chrome"], smooth=False)
        parent_keep(ih, door)
        ctx.tag(ih, "INTERIOR", "Door inner handle", "مقبض الباب الداخلي", status="estimated")
    # baggage shelf / rear bulkhead
    bm = new_bm()
    box(bm, (0.84, 0.02, 0.8), center=(0, fs(112), 1.42))
    bh = obj_from_bm("INTERIOR.baggage_bulkhead", bm, ctx.col, pivot=(0, fs(112), 1.0), mat=M["interior_tan"], smooth=False)
    parent_keep(bh, grp)
    ctx.tag(bh, "INTERIOR", "Baggage compartment aft bulkhead (120 lb area)", "الحاجز الخلفي لمقصورة الأمتعة", status="poh", ref="p.6-x baggage")

def build(ctx):
    build_panel(ctx)
    build_controls(ctx)
    build_seats(ctx)
