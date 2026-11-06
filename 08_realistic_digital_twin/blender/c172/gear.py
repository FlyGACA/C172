"""Fixed tricycle landing gear: tubular main gear with fairings, nose oleo strut, wheels,
brakes and wheel fairings (optional equipment, modelled as separate toggleable parts)."""
import math
from mathutils import Vector

from . import units as U
from .units import fs
from .airframe import fus_surface_z
from .shapes import (parent_keep, new_bm, loft, revolve, tube, cylinder, box, bezier, obj_from_bm, add_subsurf, add_boolean,
                     add_solidify, superellipse, ellipse, interp_table)

def _link(ob, grp):
    parent_keep(ob, grp)

def wheel(ctx, name, axle, r, w, side_sign, label_en, label_ar, brake=True):
    M = ctx.mats
    bm = new_bm()
    prof = [(r * 0.5, -w / 2), (r * 0.86, -w / 2), (r * 0.975, -w * 0.33), (r, 0.0), (r * 0.975, w * 0.33), (r * 0.86, w / 2), (r * 0.5, w / 2)]
    revolve(bm, prof, axis="X", origin=axle, segs=40, cap_start=False, cap_end=False, uv_u_scale=1.0)
    tyre = obj_from_bm(name + ".tyre", bm, ctx.col, pivot=axle, mat=M["rubber"])
    add_subsurf(tyre, max(1, ctx.subsurf - 1))
    ctx.tag(tyre, "GEAR", label_en, label_ar, status="type_data")
    bm = new_bm()
    revolve(bm, [(0.0, -w * 0.42), (r * 0.52, -w * 0.42), (r * 0.56, -w * 0.3), (r * 0.56, w * 0.3), (r * 0.52, w * 0.42), (0.0, w * 0.42)], axis="X", origin=axle, segs=32)
    hub = obj_from_bm(name + ".hub", bm, ctx.col, pivot=axle, mat=M["bare_alu"])
    ctx.tag(hub, "GEAR", "Wheel (Cleveland type)", "جنط العجلة", status="type_data")
    parent_keep(hub, tyre)
    if brake:
        bm = new_bm()
        inboard = -side_sign
        revolve(bm, [(0.0, 0), (r * 0.46, 0), (r * 0.46, inboard * 0.012), (0.0, inboard * 0.012)], axis="X", origin=(axle[0] + inboard * w * 0.46, axle[1], axle[2]), segs=32)
        disc = obj_from_bm(name + ".brake_disc", bm, ctx.col, pivot=axle, mat=M["steel"])
        parent_keep(disc, tyre)
        ctx.tag(disc, "GEAR", "Brake disc", "قرص الفرامل", status="estimated")
        bm = new_bm()
        box(bm, (0.045, 0.09, 0.06), center=(axle[0] + inboard * (w * 0.46 + 0.015), axle[1] + 0.02, axle[2] + r * 0.36))
        cal = obj_from_bm(name + ".brake_caliper", bm, ctx.col, pivot=axle, mat=M["cast_alu"])
        ctx.tag(cal, "GEAR", "Hydraulic brake caliper (toe brakes, pilot side)", "ملقط الفرامل الهيدروليكي", status="poh", ref="p.7-10")
    return tyre

def fairing(ctx, name, axle, r, w, length, height, width, parent, label_en, label_ar, nose_frac=0.45):
    """Streamlined wheel fairing open at the bottom, cleared around the tyre."""
    M = ctx.mats
    y0 = axle[1] - length * nose_frac; y1 = axle[1] + length * (1 - nose_frac)
    rings = []
    ys = [0, 0.04, 0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.95, 1.0]
    for t in ys:
        y = y0 + (y1 - y0) * t
        # width and height envelopes (teardrop)
        ww = width / 2 * math.sin(math.pi * min(1, t * 1.15)) ** 0.6 if t < 0.999 else 0.012
        hh = height * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.1)) ** 0.5) if t < 0.999 else 0.08
        zb = axle[2] - r * 0.45; zt = zb + hh
        zc = zb + hh * 0.45
        rings.append([Vector((axle[0] + x, y, z)) for x, z in superellipse(max(ww, 0.008), zc - zb, zt - zc, zc, 2.2, 2.0, 32)])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    f = obj_from_bm(name, bm, ctx.col, pivot=axle, mat=M["cowl"])
    add_subsurf(f, ctx.subsurf)
    # open the bottom and clear the tyre
    bm = new_bm()
    box(bm, (1.0, length + 0.2, 0.4), center=(axle[0], axle[1], axle[2] - r * 0.45 - 0.2 + 0.0))
    cut1 = obj_from_bm(name + "_cut_bottom", bm, ctx.cutters, smooth=False)
    bm = new_bm()
    revolve(bm, [(0, -w * 0.62), (r + 0.02, -w * 0.62), (r + 0.02, w * 0.62), (0, w * 0.62)], axis="X", origin=axle, segs=32)
    cut2 = obj_from_bm(name + "_cut_tyre", bm, ctx.cutters, smooth=False)
    add_boolean(f, cut1, "DIFFERENCE", "open_bottom")
    add_boolean(f, cut2, "DIFFERENCE", "tyre_clearance")
    add_solidify(f, 0.006)
    _link(f, parent)
    ctx.tag(f, "GEAR", label_en, label_ar, status="estimated", optional=True, note="Wheel fairings were optional equipment")
    return f

def build_main_gear(ctx, side):
    M = ctx.mats
    name = "L" if side > 0 else "R"          # +x is the left side
    grp = ctx.groups["GEAR"]
    axle = Vector((side * U.TRACK / 2, U.MAIN_AXLE_Y, U.MAIN_TYRE_R))
    attach = Vector((side * 0.27, fs(63), fus_surface_z(63, 0.27) + 0.03))
    mid1 = Vector((side * 0.55, fs(62), 0.70))
    mid2 = Vector((side * 1.05, fs(59.5), 0.42))
    leg_pts = bezier(attach, mid1, mid2, axle + Vector((-side * 0.09, 0, 0.02)), 16)
    bm = new_bm()
    tube(bm, leg_pts, 0.027, segs=16)
    leg = obj_from_bm(f"GEAR.main_leg_{name}", bm, ctx.col, pivot=attach, mat=M["steel"])
    add_subsurf(leg, 1)
    _link(leg, grp)
    ctx.tag(leg, "GEAR", f"{'Left' if side > 0 else 'Right'} main gear leg (tubular spring steel)", "ساق عجلة الهبوط الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"), status="poh", ref="p.7-10")
    # streamlined leg fairing over the middle of the leg
    rings = []
    for i in range(3, 14):
        p = leg_pts[i]; d = (leg_pts[i + 1] - leg_pts[i - 1]).normalized()
        a = Vector((0, 1, 0)); a = (a - d * a.dot(d)).normalized(); b = a.cross(d).normalized()
        taper = 1.0 - 0.35 * (i - 3) / 10
        rings.append([p + a * y * 0.085 * taper + b * x * 0.032 for x, y in ellipse(1, 1, 20)])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    lf = obj_from_bm(f"GEAR.main_leg_fairing_{name}", bm, ctx.col, pivot=attach, mat=M["cowl"])
    add_subsurf(lf, 1)
    _link(lf, grp)
    ctx.tag(lf, "GEAR", "Main gear leg fairing", "غطاء انسيابي لساق عجلة الهبوط", status="estimated", optional=True)
    tyre = wheel(ctx, f"GEAR.main_wheel_{name}", axle, U.MAIN_TYRE_R, U.MAIN_TYRE_W, side, f"{'Left' if side > 0 else 'Right'} main wheel tyre 6.00-6", "إطار العجلة الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"))
    _link(tyre, grp)
    tyre["spin_axis"] = "x"; tyre["animate"] = "wheel"
    fairing(ctx, f"GEAR.main_wheel_fairing_{name}", axle, U.MAIN_TYRE_R, U.MAIN_TYRE_W, 1.0, 0.50, 0.32, grp,
            f"{'Left' if side > 0 else 'Right'} main wheel fairing", "غطاء العجلة الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"))
    # brake line along the leg
    bm = new_bm()
    tube(bm, [p + Vector((0, 0.035, 0)) for p in leg_pts[2:15]], 0.004, segs=8)
    bl_ = obj_from_bm(f"GEAR.brake_line_{name}", bm, ctx.col, pivot=attach, mat=M["bare_alu"])
    _link(bl_, grp)
    ctx.tag(bl_, "GEAR", "Brake hydraulic line", "خط الفرامل الهيدروليكي", status="estimated")

def build_nose_gear(ctx):
    M = ctx.mats
    grp = ctx.groups["GEAR"]
    axle = Vector((0, U.NOSE_AXLE_Y, U.NOSE_TYRE_R))
    top = Vector((0, fs(-3.0), 0.97))
    piston_top = Vector((0, fs(-5.5), 0.50))
    bottom = Vector((0, fs(-6.5), 0.27))
    # strut housing (outer cylinder) with a taper to the fuselage mount
    bm = new_bm()
    d = (piston_top - top).normalized()
    rings = []
    for i, (t, r) in enumerate([(0.0, 0.05), (0.08, 0.05), (0.12, 0.042), (1.0, 0.042)]):
        p = top + (piston_top - top) * t
        a = Vector((1, 0, 0)); b = a.cross(d).normalized()
        rings.append([p + a * r * math.cos(2 * math.pi * j / 20) + b * r * math.sin(2 * math.pi * j / 20) for j in range(20)])
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    outer = obj_from_bm("GEAR.nose_strut", bm, ctx.col, pivot=top, z_axis=-(piston_top - top), mat=M["bare_alu"])
    _link(outer, grp)
    ctx.tag(outer, "GEAR", "Nose gear oleo strut (air/oil shock)", "دعامة عجلة المقدمة الزيتية الهوائية", status="poh", ref="p.7-10, 8-x", hinge_axis="z", hinge_sign=1, range_deg=[-10, 10], animate="nose_steer")
    bm = new_bm()
    tube(bm, [piston_top - d * 0.02, bottom], 0.030, segs=20)
    piston = obj_from_bm("GEAR.nose_piston", bm, ctx.col, pivot=piston_top, mat=M["chrome"])
    parent_keep(piston, outer)
    ctx.tag(piston, "GEAR", "Oleo piston (chromed)", "مكبس الدعامة", status="estimated")
    # fork
    bm = new_bm()
    for sx in (-1, 1):
        box(bm, (0.014, 0.08, 0.16), center=(sx * 0.085, axle.y + 0.0, axle.z + 0.06))
    box(bm, (0.19, 0.08, 0.03), center=(0, bottom.y, bottom.z - 0.01))
    fork = obj_from_bm("GEAR.nose_fork", bm, ctx.col, pivot=bottom, mat=M["steel"])
    parent_keep(fork, outer)
    ctx.tag(fork, "GEAR", "Nose wheel fork", "شوكة عجلة المقدمة", status="estimated")
    # torque links (scissors)
    bm = new_bm()
    lug_top = Vector((0, top.y - 0.06, 0.60)); knee = Vector((0, top.y - 0.17, 0.44)); lug_bot = Vector((0, bottom.y - 0.055, 0.30))
    for sx in (-0.02, 0.02):
        tube(bm, [lug_top + Vector((sx, 0, 0)), knee + Vector((sx, 0, 0))], 0.009, segs=8)
        tube(bm, [knee + Vector((sx * 1.6, 0, 0)), lug_bot + Vector((sx * 1.6, 0, 0))], 0.009, segs=8)
    tl = obj_from_bm("GEAR.nose_torque_links", bm, ctx.col, pivot=lug_top, mat=M["steel"])
    parent_keep(tl, outer)
    ctx.tag(tl, "GEAR", "Torque links (scissors)", "وصلات العزم", status="estimated")
    tyre = wheel(ctx, "GEAR.nose_wheel", axle, U.NOSE_TYRE_R, U.NOSE_TYRE_W, 1, "Nose wheel tyre 5.00-5", "إطار عجلة المقدمة", brake=False)
    parent_keep(tyre, outer)
    tyre["spin_axis"] = "x"; tyre["animate"] = "wheel"
    fairing(ctx, "GEAR.nose_wheel_fairing", axle, U.NOSE_TYRE_R, U.NOSE_TYRE_W, 0.80, 0.42, 0.26, outer, "Nose wheel fairing", "غطاء عجلة المقدمة", nose_frac=0.42)
    # shimmy damper
    bm = new_bm()
    tube(bm, [Vector((0.06, top.y + 0.02, 0.92)), Vector((0.06, top.y + 0.22, 0.90))], 0.016, segs=10)
    sd = obj_from_bm("GEAR.shimmy_damper", bm, ctx.col, pivot=top, mat=M["cast_alu"])
    _link(sd, grp)
    ctx.tag(sd, "GEAR", "Nose wheel shimmy damper", "مخمد اهتزاز عجلة المقدمة", status="estimated")
