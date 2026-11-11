"""Fixed tricycle landing gear: tubular main gear with fairings, nose oleo strut, wheels,
brakes and wheel fairings (optional equipment, modelled as separate toggleable parts)."""
import math
from mathutils import Vector

from . import units as U
from .units import fs
from .airframe import fus_surface_z
from .shapes import (parent_keep, new_bm, loft, revolve, tube, cylinder, box, bezier, obj_from_bm, add_subsurf, add_boolean,
                     add_solidify, add_edge_split, extrude_profile, superellipse, ellipse, rounded_rect, interp_table, smoothstep)

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

def fairing(ctx, name, axle, r, w, length, height, width, parent, label_en, label_ar, nose_frac=0.38):
    """Streamlined wheel fairing ('speed pant'): a teardrop that is fullest about a third of the
    way back and tapers to a point, open underneath where the tyre shows."""
    M = ctx.mats
    y0 = axle[1] - length * nose_frac; y1 = axle[1] + length * (1 - nose_frac)
    zb = axle[2] - r * 0.42                      # lower edge of the fairing; the tyre shows below it
    rings = []
    def envelope(t):
        """Fullness along the fairing, 1.0 at its fullest: a NACA thickness form made blunter over the
        wheel (so the walls stay outside the tyre from its front to its rear edge), fine at the tail."""
        naca = (0.2969 * math.sqrt(t) - 0.1260 * t - 0.3516 * t ** 2 + 0.2843 * t ** 3 - 0.1036 * t ** 4) / 0.1
        return max(0.0, min(1.0, naca)) ** (0.4 + 0.6 * smoothstep(0.6, 0.95, t))
    for t in [0.004, 0.02, 0.06, 0.13, 0.22, 0.32, 0.44, 0.56, 0.68, 0.79, 0.88, 0.95, 0.995]:
        y = y0 + (y1 - y0) * t
        e = max(0.03, envelope(t))
        ww = max(0.006, width / 2 * e)
        hh = max(0.02, height * (0.18 + 0.82 * e))
        droop = 0.085 * (1 - e)                  # nose and tail sit higher than the middle
        zc = zb + droop + hh * 0.42
        # slab-sided below its widest point so the walls come straight down past the tyre; square-shouldered
        # above, so the top clears the tyre across its whole width
        rings.append([Vector((axle[0] + x, y, z)) for x, z in superellipse(ww, hh * 0.42, hh * 0.58, zc, 3.2, 7.0, 32)])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    f = obj_from_bm(name, bm, ctx.col, pivot=axle, mat=M["cowl"])
    add_subsurf(f, ctx.subsurf)
    add_solidify(f, 0.006)                       # a hollow shell first, so that the cut below opens it
    # open the underside round the tyre: a slot with rounded ends, a little wider and longer than the tyre
    bm = new_bm()
    extrude_profile(bm, rounded_rect(w * 1.2, r * 2.3, w * 0.45, 5), Vector((1, 0, 0)), Vector((0, 1, 0)), (axle[0], axle[1], 0.0),
                    Vector((0, 0, 1)), zb - 0.3, zb + 0.035, smooth_sides=False)
    cut = obj_from_bm(name + "_cut_bottom", bm, ctx.cutters, smooth=False)
    add_boolean(f, cut, "DIFFERENCE", "open_bottom")
    add_edge_split(f, 50)
    _link(f, parent)
    ctx.tag(f, "GEAR", label_en, label_ar, status="estimated", optional=True, note="Wheel fairings were optional equipment")
    return f

# Landing gear, build frame. The ground is not level in this frame (units.ground_z): the wheels stand
# on it where it passes under their stations, so that the aircraft sits in the "normal ground attitude"
# of the manufacturer's side view once build.py has turned it. Status: estimated: the tubular spring
# leg leaves the belly at the main-gear bulkhead and runs outboard and down to a track of 8 ft 4½ in.
MAIN_AXLE_Z = U.ground_z(U.MAIN_AXLE_Y) + U.MAIN_TYRE_R * 0.96      # tyre slightly flattened under load
NOSE_AXLE_Z = U.ground_z(U.NOSE_AXLE_Y) + U.NOSE_TYRE_R * 0.96

MAIN_LEG_ROOT_FS = 65.0      # the gear bulkhead at the foot of the rear door posts (handbook station 65.3)

def main_leg_points(side, n=16):
    """Tubular spring leg: from the gear bulkhead inside the belly straight down and outboard to the
    axle, sweeping forward to the wheel station (manufacturer's front and side views)."""
    axle = Vector((side * U.TRACK / 2, U.MAIN_AXLE_Y, MAIN_AXLE_Z))
    attach = Vector((side * 0.20, fs(MAIN_LEG_ROOT_FS), fus_surface_z(MAIN_LEG_ROOT_FS, 0.20) + 0.045))
    end = axle + Vector((-side * 0.085, 0, 0.012))
    mid1 = attach.lerp(end, 0.33) + Vector((0, 0, 0.022))
    mid2 = attach.lerp(end, 0.66) + Vector((0, 0, 0.012))
    return bezier(attach, mid1, mid2, end, n), axle, attach

def build_main_gear(ctx, side):
    M = ctx.mats
    name = "L" if side > 0 else "R"          # +x is the left side
    grp = ctx.groups["GEAR"]
    leg_pts, axle, attach = main_leg_points(side)
    bm = new_bm()
    tube(bm, leg_pts, 0.026, segs=16, radius_end=0.021)
    leg = obj_from_bm(f"GEAR.main_leg_{name}", bm, ctx.col, pivot=attach, mat=M["steel"])
    add_subsurf(leg, 1)
    _link(leg, grp)
    ctx.tag(leg, "GEAR", f"{'Left' if side > 0 else 'Right'} main gear leg (tubular spring steel)", "ساق عجلة الهبوط الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"), status="poh", ref="p.7-10")
    # streamlined leg fairing over the middle of the leg
    rings = []
    for i in range(4, 14):
        p = leg_pts[i]; d = (leg_pts[i + 1] - leg_pts[i - 1]).normalized()
        a = Vector((0, 1, 0)); a = (a - d * a.dot(d)).normalized(); b = a.cross(d).normalized()
        taper = 1.0 - 0.3 * (i - 4) / 9
        rings.append([p + a * y * 0.075 * taper + b * x * 0.030 for x, y in ellipse(1, 1, 20)])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    lf = obj_from_bm(f"GEAR.main_leg_fairing_{name}", bm, ctx.col, pivot=attach, mat=M["cowl"])
    add_subsurf(lf, 1)
    _link(lf, grp)
    ctx.tag(lf, "GEAR", "Main gear leg fairing", "غطاء انسيابي لساق عجلة الهبوط", status="estimated", optional=True)
    tyre = wheel(ctx, f"GEAR.main_wheel_{name}", axle, U.MAIN_TYRE_R, U.MAIN_TYRE_W, side, f"{'Left' if side > 0 else 'Right'} main wheel tyre 6.00-6", "إطار العجلة الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"))
    _link(tyre, grp)
    tyre["spin_axis"] = "x"; tyre["animate"] = "wheel"
    fairing(ctx, f"GEAR.main_wheel_fairing_{name}", axle, U.MAIN_TYRE_R, U.MAIN_TYRE_W, 0.94, 0.36, 0.25, grp,
            f"{'Left' if side > 0 else 'Right'} main wheel fairing", "غطاء العجلة الرئيسية " + ("اليسرى" if side > 0 else "اليمنى"))
    # brake line along the leg
    bm = new_bm()
    tube(bm, [p + Vector((0, 0.032, 0)) for p in leg_pts[2:15]], 0.004, segs=8)
    bl_ = obj_from_bm(f"GEAR.brake_line_{name}", bm, ctx.col, pivot=attach, mat=M["bare_alu"])
    _link(bl_, grp)
    ctx.tag(bl_, "GEAR", "Brake hydraulic line", "خط الفرامل الهيدروليكي", status="estimated")
    # cabin entry step: a small plate clamped to each leg just outboard of the fuselage
    p = leg_pts[5]
    bm = new_bm()
    box(bm, (0.16, 0.10, 0.012), center=(p.x, p.y - 0.005, p.z + 0.034))
    tube(bm, [p + Vector((0, 0, 0.0)), p + Vector((0, 0, 0.03))], 0.012, segs=8)
    step = obj_from_bm(f"AIRFRAME.step_{name}", bm, ctx.col, pivot=p, mat=M["steel"], smooth=False)
    _link(step, ctx.groups["AIRFRAME"])
    ctx.tag(step, "AIRFRAME", f"Cabin entry step ({'left' if side > 0 else 'right'} main gear leg)",
            "درجة الصعود إلى المقصورة (ساق العجلة " + ("اليسرى" if side > 0 else "اليمنى") + ")", status="estimated")

def build_nose_gear(ctx):
    M = ctx.mats
    grp = ctx.groups["GEAR"]
    axle = Vector((0, U.NOSE_AXLE_Y, NOSE_AXLE_Z))
    top = Vector((0, fs(-1.4), fus_surface_z(0, 0.0) + 0.16))          # inside the lower cowl, on the firewall bracket
    piston_top = Vector((0, fs(-5.0), axle.z + 0.20))                  # about 3 in of chromed piston show at rest
    bottom = Vector((0, fs(-6.2), axle.z + 0.125))
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
        box(bm, (0.014, 0.08, 0.15), center=(sx * 0.085, axle.y + 0.0, axle.z + 0.055))
    box(bm, (0.19, 0.08, 0.03), center=(0, bottom.y, bottom.z - 0.005))
    fork = obj_from_bm("GEAR.nose_fork", bm, ctx.col, pivot=bottom, mat=M["steel"])
    parent_keep(fork, outer)
    ctx.tag(fork, "GEAR", "Nose wheel fork", "شوكة عجلة المقدمة", status="estimated")
    # torque links (scissors), behind the strut
    bm = new_bm()
    lug_top = piston_top + Vector((0, 0.055, 0.04)); knee = Vector((0, piston_top.y + 0.15, (piston_top.z + bottom.z) / 2)); lug_bot = bottom + Vector((0, 0.05, 0.01))
    for sx in (-0.02, 0.02):
        tube(bm, [lug_top + Vector((sx, 0, 0)), knee + Vector((sx, 0, 0))], 0.009, segs=8)
        tube(bm, [knee + Vector((sx * 1.6, 0, 0)), lug_bot + Vector((sx * 1.6, 0, 0))], 0.009, segs=8)
    tl = obj_from_bm("GEAR.nose_torque_links", bm, ctx.col, pivot=lug_top, mat=M["steel"])
    parent_keep(tl, outer)
    ctx.tag(tl, "GEAR", "Torque links (scissors)", "وصلات العزم", status="estimated")
    tyre = wheel(ctx, "GEAR.nose_wheel", axle, U.NOSE_TYRE_R, U.NOSE_TYRE_W, 1, "Nose wheel tyre 5.00-5", "إطار عجلة المقدمة", brake=False)
    parent_keep(tyre, outer)
    tyre["spin_axis"] = "x"; tyre["animate"] = "wheel"
    fairing(ctx, "GEAR.nose_wheel_fairing", axle, U.NOSE_TYRE_R, U.NOSE_TYRE_W, 0.74, 0.30, 0.21, outer, "Nose wheel fairing", "غطاء عجلة المقدمة", nose_frac=0.40)
    # shimmy damper
    bm = new_bm()
    tube(bm, [Vector((0.06, top.y + 0.02, top.z - 0.05)), Vector((0.06, top.y + 0.20, top.z - 0.07))], 0.016, segs=10)
    sd = obj_from_bm("GEAR.shimmy_damper", bm, ctx.col, pivot=top, mat=M["cast_alu"])
    _link(sd, grp)
    ctx.tag(sd, "GEAR", "Nose wheel shimmy damper", "مخمد اهتزاز عجلة المقدمة", status="estimated")
