"""Lycoming O-320-H2AD educational engine assembly. Structured as separate objects so the
viewer can animate the crank train (same conventions as js/kinematics.js) and explode the
assembly. Geometry is representative, not manufacturer drawings."""
import math
import bpy
from mathutils import Vector

from . import units as U
from .units import fs
from .shapes import (parent_keep, new_bm, loft, revolve, tube, cylinder, box, bezier, obj_from_bm, add_subsurf,
                     add_bevel, extrude_profile, rounded_rect, ellipse)

CRANK_R = 0.0492          # m, half the 3.875 in stroke (type data; verify TCDS E-274)
ROD_L = 0.162             # m, illustrative
BORE = 0.1302             # 5.125 in (type data)
ORIGIN = Vector((0, fs(-20), U.PROP_Z))   # ENGINE node origin = crank centre
# cylinder: side (-1 right bank / +1 left bank), z forward of origin (engine frame), pin angle deg
CYL = {1: (-1, 0.140, 180), 2: (1, 0.096, 0), 3: (-1, -0.095, 0), 4: (1, -0.139, 180)}
CASE_HALF_W = 0.125       # crankcase half width at the cylinder decks
HEAD_X0 = CASE_HALF_W + 0.118    # start of the head
HEAD_X1 = HEAD_X0 + 0.115        # end of the head (rocker cover beyond)

def cyl_center_y(c):
    return ORIGIN.y - CYL[c][1]

def pin_xz(c):
    a = math.radians(CYL[c][2])
    return CRANK_R * math.cos(a), CRANK_R * math.sin(a)

def piston_x(c):
    side = CYL[c][0]
    px, pz = pin_xz(c)
    u = px * side
    return side * (u + math.sqrt(ROD_L ** 2 - pz ** 2))

def _link(ob, grp):
    parent_keep(ob, grp)

def build_case(ctx, grp):
    M = ctx.mats
    y0, y1 = fs(-32), fs(-9.5)
    for side, nm in ((1, "L"), (-1, "R")):
        bm = new_bm()
        # half crankcase: rounded box with the bearing saddle; split at the vertical centre plane
        box(bm, (CASE_HALF_W, y1 - y0, 0.30), center=(side * CASE_HALF_W / 2, (y0 + y1) / 2, ORIGIN.z))
        # cylinder deck pads
        for c in (1, 3) if side < 0 else (2, 4):
            revolve(bm, [(0.0, 0.0), (0.095, 0.0), (0.095, 0.02 * side), (0.0, 0.02 * side)], axis="X", origin=(side * CASE_HALF_W, cyl_center_y(c), ORIGIN.z), segs=28)
        ob = obj_from_bm(f"ENGINE.crankcase_{nm}", bm, ctx.col, pivot=(side * CASE_HALF_W / 2, ORIGIN.y, ORIGIN.z), mat=M["lycoming_grey"], smooth=False)
        add_bevel(ob, 0.02, 3)
        _link(ob, grp)
        ctx.tag(ob, "ENGINE", f"Crankcase {'left' if side > 0 else 'right'} half (cast aluminium, split vertically)", "نصف علبة المرفق " + ("الأيسر" if side > 0 else "الأيمن"), status="estimated", xray=True)
    # accessory housing (rear) with the dual magneto, oil pump, vacuum pump pads
    bm = new_bm()
    box(bm, (0.30, 0.09, 0.32), center=(0, fs(-7), ORIGIN.z))
    acc = obj_from_bm("ENGINE.accessory_housing", bm, ctx.col, pivot=(0, fs(-7), ORIGIN.z), mat=M["lycoming_grey"], smooth=False)
    add_bevel(acc, 0.015, 3)
    _link(acc, grp)
    ctx.tag(acc, "ENGINE", "Accessory housing (rear): drives magneto, oil pump, vacuum pump", "علبة الملحقات الخلفية", status="estimated")
    # oil sump
    bm = new_bm()
    box(bm, (0.34, 0.40, 0.11), center=(0, fs(-18), ORIGIN.z - 0.205))
    sump = obj_from_bm("OIL.sump", bm, ctx.col, pivot=(0, fs(-18), ORIGIN.z - 0.15), mat=M["lycoming_grey"], smooth=False)
    add_bevel(sump, 0.02, 3)
    _link(sump, grp)
    ctx.tag(sump, "OIL", "Oil sump (6 qt) with intake-air passages (induction heats the sump)", "حوض الزيت (6 كوارت)", status="poh", ref="p.1-4, 7-24")
    # crank flange and alternator drive pulley at the front
    bm = new_bm()
    revolve(bm, [(0.0, fs(-32.5)), (0.05, fs(-32.5)), (0.05, fs(-33.6)), (0.0, fs(-33.6))], axis="Y", origin=(0, 0, ORIGIN.z), segs=28)
    revolve(bm, [(0.0, fs(-32.3)), (0.075, fs(-32.3)), (0.075, fs(-32.0)), (0.0, fs(-32.0))], axis="Y", origin=(0, 0, ORIGIN.z), segs=28)
    fl = obj_from_bm("ENGINE.crank_flange_pulley", bm, ctx.col, pivot=(0, fs(-33), ORIGIN.z), mat=M["steel"])
    _link(fl, grp)
    ctx.tag(fl, "ENGINE", "Propeller flange and alternator drive pulley", "شفة المروحة وبكرة المولد", status="estimated", spin_axis="y", spin_sign=-1, animate="prop")

def build_cylinder(ctx, grp, c):
    M = ctx.mats
    side, _, _ = CYL[c]
    yc = cyl_center_y(c); zc = ORIGIN.z
    x0 = CASE_HALF_W
    # barrel with cooling fins
    bm = new_bm()
    revolve(bm, [(0.072, 0.0), (0.072, side * 0.118)], axis="X", origin=(side * x0, yc, zc), segs=32, cap_start=False, cap_end=False)
    nfin = 15 if ctx.subsurf >= 2 else 9
    for i in range(nfin):
        xx = side * (x0 + 0.012 + i * 0.105 / (nfin - 1))
        revolve(bm, [(0.072, xx - side * x0), (0.108, xx - side * x0), (0.108, xx - side * x0 + side * 0.0018), (0.072, xx - side * x0 + side * 0.0018)], axis="X", origin=(side * x0, yc, zc), segs=32, cap_start=False, cap_end=False)
    barrel = obj_from_bm(f"ENGINE.cylinder_barrel_{c}", bm, ctx.col, pivot=(side * x0, yc, zc), mat=M["lycoming_grey"])
    _link(barrel, grp)
    ctx.tag(barrel, "ENGINE", f"Cylinder {c} barrel (steel, finned) — bore 5.125 in", f"أسطوانة {c} (الجزء الأسطواني المزعنف)", status="type_data", cyl=c, xray=True)
    # head: finned block with the rocker box
    bm = new_bm()
    # core block (rounded) and fin plates perpendicular to the crank axis, rounded like a cast head
    core = rounded_rect(HEAD_X1 - HEAD_X0, 0.15, 0.03, 4)
    extrude_profile(bm, core, Vector((side, 0, 0)), Vector((0, 0, 1)), (side * (HEAD_X0 + HEAD_X1) / 2, yc, zc), Vector((0, 1, 0)), -0.08, 0.08, smooth_sides=True)
    nh = 14 if ctx.subsurf >= 2 else 8
    fin = rounded_rect(HEAD_X1 - HEAD_X0 - 0.012, 0.215, 0.045, 5)
    for i in range(nh):
        yy = yc - 0.082 + i * 0.164 / (nh - 1)
        extrude_profile(bm, fin, Vector((side, 0, 0)), Vector((0, 0, 1)), (side * (HEAD_X0 + HEAD_X1) / 2, yy, zc), Vector((0, 1, 0)), -0.001, 0.001, smooth_sides=False)
    head = obj_from_bm(f"ENGINE.cylinder_head_{c}", bm, ctx.col, pivot=(side * HEAD_X0, yc, zc), mat=M["lycoming_grey"], smooth=False)
    _link(head, grp)
    ctx.tag(head, "ENGINE", f"Cylinder {c} head (aluminium, deep cooling fins, two plugs)", f"رأس الأسطوانة {c}", status="estimated", cyl=c, xray=True)
    # rocker cover
    bm = new_bm()
    box(bm, (0.04, 0.16, 0.11), center=(side * (HEAD_X1 + 0.02), yc, zc))
    rc = obj_from_bm(f"ENGINE.rocker_cover_{c}", bm, ctx.col, pivot=(side * HEAD_X1, yc, zc), mat=M["lycoming_grey"], smooth=False)
    add_bevel(rc, 0.012, 3)
    _link(rc, grp)
    ctx.tag(rc, "ENGINE", f"Rocker cover {c} (valve gear)", f"غطاء الروافع {c}", status="estimated", cyl=c)
    # pushrod shroud tubes (Lycoming: camshaft above the crank, tubes along the top of the cylinder)
    bm = new_bm()
    for dy in (-0.032, 0.032):
        tube(bm, [Vector((side * (x0 - 0.01), yc + dy, zc + 0.085)), Vector((side * (HEAD_X1 - 0.02), yc + dy, zc + 0.095))], 0.009, segs=10)
    pr = obj_from_bm(f"ENGINE.pushrod_tubes_{c}", bm, ctx.col, pivot=(side * x0, yc, zc + 0.085), mat=M["bare_alu"])
    _link(pr, grp)
    ctx.tag(pr, "ENGINE", f"Pushrod shroud tubes {c}", f"أنابيب قضبان الدفع {c}", status="estimated", cyl=c)
    # spark plugs: top and bottom of the head, with leads to the dual magneto
    for pos, zz in (("top", 0.105), ("bottom", -0.105)):
        bm = new_bm()
        tube(bm, [Vector((side * (HEAD_X0 + 0.055), yc, zc + zz * 0.9)), Vector((side * (HEAD_X0 + 0.055), yc, zc + zz + 0.03 * (1 if zz > 0 else -1)))], 0.010, segs=12)
        revolve(bm, [(0.0, 0.0), (0.012, 0.0), (0.012, 0.012), (0.0, 0.012)], axis="Z", origin=(side * (HEAD_X0 + 0.055), yc, zc + zz + (0.03 if zz > 0 else -0.042)), segs=12)
        # POH p.7-19 plug map: right magneto -> lower right & upper left; left magneto -> lower left & upper right
        mag = "R" if (side < 0 and pos == "bottom") or (side > 0 and pos == "top") else "L"
        plug = obj_from_bm(f"ENGINE.plug_{pos}_{c}", bm, ctx.col, pivot=(side * (HEAD_X0 + 0.055), yc, zc + zz), mat=M["brass"])
        _link(plug, grp)
        ctx.tag(plug, "IGNITION", f"Spark plug cylinder {c} {pos} — fired by the {'right' if mag == 'R' else 'left'} magneto", f"شمعة الإشعال {c} {'العلوية' if pos == 'top' else 'السفلية'}", status="poh", ref="p.7-19", cyl=c, magneto=mag, animate="plug")
        bm = new_bm()
        start = Vector((side * (HEAD_X0 + 0.055), yc, zc + zz + (0.04 if zz > 0 else -0.052)))
        mid = Vector((side * 0.22, yc + 0.05, zc + (0.19 if zz > 0 else -0.21)))
        end = Vector((side * 0.06, fs(-5.2), zc + 0.16 + (0.0 if zz > 0 else -0.03)))
        tube(bm, bezier(start, mid, (mid + end) / 2 + Vector((0, 0, 0.05)), end, 16), 0.004, segs=8)
        lead = obj_from_bm(f"ENGINE.plug_lead_{pos}_{c}", bm, ctx.col, pivot=start, mat=M["hose_black"])
        _link(lead, grp)
        ctx.tag(lead, "IGNITION", f"Ignition lead (shielded) — plug {c} {pos}", f"سلك الإشعال {c}", status="estimated", cyl=c, magneto=mag)
    # intake pipe from the sump to the bottom-rear of the head, exhaust stack from the bottom-front
    bm = new_bm()
    p0 = Vector((side * 0.10, yc + 0.03, zc - 0.21)); p3 = Vector((side * (HEAD_X0 + 0.06), yc + 0.045, zc - 0.095))
    tube(bm, bezier(p0, p0 + Vector((side * 0.12, 0, 0)), p3 + Vector((0, 0, -0.09)), p3, 14), 0.018, segs=12)
    ip = obj_from_bm(f"INDUCTION.intake_pipe_{c}", bm, ctx.col, pivot=p0, mat=M["bare_alu"])
    _link(ip, grp)
    ctx.tag(ip, "INDUCTION", f"Intake pipe to cylinder {c} (from the sump plenum)", f"أنبوب السحب للأسطوانة {c}", status="poh", ref="p.7-24", cyl=c)
    bm = new_bm()
    e0 = Vector((side * (HEAD_X0 + 0.06), yc - 0.05, zc - 0.095)); e3 = Vector((side * 0.17, fs(-14), zc - 0.40))
    tube(bm, bezier(e0, e0 + Vector((0, 0, -0.12)), e3 + Vector((side * 0.05, -0.05, 0.08)), e3, 14), 0.021, segs=12)
    ex = obj_from_bm(f"ENGINE.exhaust_stack_{c}", bm, ctx.col, pivot=e0, mat=M["exhaust"])
    _link(ex, grp)
    ctx.tag(ex, "ENGINE", f"Exhaust riser cylinder {c} (to the muffler)", f"ماسورة العادم للأسطوانة {c}", status="estimated", cyl=c)
    # ---- internals (shown in X-ray / exploded views): piston, connecting rod, valves
    px = piston_x(c)
    bm = new_bm()
    revolve(bm, [(0.0, -0.035), (0.062, -0.035), (0.064, -0.02), (0.064, 0.045), (0.0, 0.045)], axis="X", origin=(px, yc, zc), segs=28)
    for g in (-0.012, 0.0, 0.012):
        revolve(bm, [(0.064, g - 0.002), (0.0655, g - 0.002), (0.0655, g + 0.002), (0.064, g + 0.002)], axis="X", origin=(px, yc, zc), segs=28, cap_start=False, cap_end=False)
    if side < 0:
        for v in bm.verts: v.co.x = 2 * px - v.co.x
        for f in bm.faces: f.normal_flip()
    pis = obj_from_bm(f"ENGINE.piston_{c}", bm, ctx.col, pivot=(px, yc, zc), mat=M["bare_alu"])
    _link(pis, grp)
    ctx.tag(pis, "ENGINE", f"Piston {c} with rings (stroke 3.875 in)", f"المكبس {c}", status="type_data", cyl=c, animate="piston", internal=True)
    # rod authored along +X from the big end; rotated to the theta = 0 pose about the crank axis
    pxz = pin_xz(c)
    big = Vector((pxz[0], yc, zc + pxz[1]))
    ang = math.atan2(0 - pxz[1], px - pxz[0])
    bm = new_bm()
    revolve(bm, [(0.0, -0.02), (0.034, -0.02), (0.034, 0.02), (0.0, 0.02)], axis="X", origin=(0, 0, 0), segs=20)   # big end (local)
    box(bm, (ROD_L - 0.04, 0.014, 0.03), center=(ROD_L / 2, 0, 0))
    revolve(bm, [(0.0, -0.016), (0.02, -0.016), (0.02, 0.016), (0.0, 0.016)], axis="X", origin=(ROD_L, 0, 0), segs=16)
    me = bpy.data.meshes.new(f"ENGINE.rod_{c}")
    from .shapes import finish
    finish(bm, me, smooth=True)
    rod = bpy.data.objects.new(f"ENGINE.rod_{c}", me); ctx.col.objects.link(rod)
    me.materials.append(M["steel"])
    rod.location = big
    rod.rotation_euler = (0, -ang, 0)       # rotation about Blender -Y == glTF +Z
    _link(rod, grp)
    ctx.tag(rod, "ENGINE", f"Connecting rod {c}", f"ذراع التوصيل {c}", status="estimated", cyl=c, animate="rod", internal=True)
    for kind, dy in (("intake", 0.032), ("exhaust", -0.032)):
        bm = new_bm()
        xv = side * (HEAD_X0 + 0.01)
        tube(bm, [Vector((xv, yc + dy, zc)), Vector((xv + side * 0.09, yc + dy, zc))], 0.004, segs=8)
        revolve(bm, [(0.0, 0.0), (0.021, 0.0), (0.021, side * 0.004), (0.0, side * 0.004)], axis="X", origin=(xv, yc + dy, zc), segs=16)
        vo = obj_from_bm(f"ENGINE.valve_{kind}_{c}", bm, ctx.col, pivot=(xv, yc + dy, zc), mat=M["chrome"])
        _link(vo, grp)
        ctx.tag(vo, "ENGINE", f"{kind.capitalize()} valve cylinder {c}", f"صمام {'السحب' if kind == 'intake' else 'العادم'} للأسطوانة {c}", status="estimated", cyl=c, animate="valve", valve=kind, internal=True)

def build_crank_train(ctx, grp):
    M = ctx.mats
    bm = new_bm()
    y_front, y_rear = fs(-32.8), fs(-9)
    # main journals between throws
    ys = sorted([cyl_center_y(c) for c in CYL])
    segs = [(y_front, ys[0] - 0.035), (ys[1] + 0.035, ys[2] - 0.035), (ys[3] + 0.035, y_rear)]
    for a, b in segs:
        revolve(bm, [(0.0, a), (0.03, a), (0.03, b), (0.0, b)], axis="Y", origin=(0, 0, ORIGIN.z), segs=20)
    # throws: webs + pin per cylinder; pins of 1/4 at 180 deg, 2/3 at 0 deg
    for c, (side, zf, pin_deg) in CYL.items():
        yc = cyl_center_y(c); px, pz = pin_xz(c)
        a = math.radians(pin_deg)
        for dy in (-0.028, 0.028):
            # web: box from the axis to the pin (local xz plane), rotated by the pin angle
            w0 = Vector((0, yc + dy, ORIGIN.z)); w1 = Vector((px, yc + dy, ORIGIN.z + pz))
            tube(bm, [w0 - Vector((px, 0, pz)) * 0.6, w1], 0.028, segs=10)
        revolve(bm, [(0.0, yc - 0.03), (0.026, yc - 0.03), (0.026, yc + 0.03), (0.0, yc + 0.03)], axis="Y", origin=(px, 0, ORIGIN.z + pz), segs=16)
    crank = obj_from_bm("ENGINE.crankshaft", bm, ctx.col, pivot=ORIGIN, mat=M["steel"])
    _link(crank, grp)
    ctx.tag(crank, "ENGINE", "Crankshaft (pins 1 & 4 at 180°, 2 & 3 at 0°; firing order 1-3-2-4)", "عمود المرفق", status="type_data", ref="Lycoming O-320 firing order 1-3-2-4", animate="crank", spin_axis="y", spin_sign=-1, internal=True)
    # camshaft above the crank with lobes, half speed
    bm = new_bm()
    zc = ORIGIN.z + 0.082
    revolve(bm, [(0.0, fs(-31)), (0.014, fs(-31)), (0.014, fs(-9.5)), (0.0, fs(-9.5))], axis="Y", origin=(0, 0, zc), segs=14)
    for c in CYL:
        yc = cyl_center_y(c)
        for dy in (-0.032, 0.032):
            pts = [(0.022 * math.cos(2 * math.pi * i / 16) * (1.5 if abs(math.cos(2 * math.pi * i / 16) - 1) < 0.3 else 1.0), 0.022 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
            extrude_profile(bm, pts, Vector((1, 0, 0)), Vector((0, 0, 1)), (0, yc + dy - 0.006, zc), Vector((0, 1, 0)), 0, 0.012, smooth_sides=True)
    cam = obj_from_bm("ENGINE.camshaft", bm, ctx.col, pivot=(0, ORIGIN.y, zc), mat=M["steel"])
    _link(cam, grp)
    ctx.tag(cam, "ENGINE", "Camshaft (above the crankshaft, half crank speed)", "عمود الكامات", status="estimated", animate="cam", spin_axis="y", spin_sign=-1, internal=True)

def build_accessories(ctx, grp):
    M = ctx.mats
    zc = ORIGIN.z
    # dual magneto (single drive, two sets of points/coils) on the accessory case top
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.055, 0.0), (0.055, 0.11), (0.045, 0.13), (0.0, 0.13)], axis="Y", origin=(0.0, fs(-7.5), zc + 0.175), segs=24)
    box(bm, (0.14, 0.05, 0.06), center=(0, fs(-4.0), zc + 0.175))
    mag = obj_from_bm("IGNITION.dual_magneto", bm, ctx.col, pivot=(0, fs(-7.5), zc + 0.175), mat=M["black_plastic"])
    _link(mag, grp)
    ctx.tag(mag, "IGNITION", "Dual magneto (one housing, two independent magnetos, impulse coupling for starting)", "المغناطيس المزدوج", status="poh", ref="p.7-18/19")
    # starter (rear right lower) and alternator (front left lower, belt driven)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.048, 0.0), (0.048, 0.17), (0.03, 0.19), (0.0, 0.19)], axis="Y", origin=(-0.14, fs(-7.0), zc - 0.13), segs=20)
    st = obj_from_bm("ELECTRICAL.starter", bm, ctx.col, pivot=(-0.14, fs(-7.0), zc - 0.13), mat=M["black_plastic"])
    _link(st, grp)
    ctx.tag(st, "ELECTRICAL", "Starter motor (key START, engages the ring gear)", "محرك البدء", status="poh", ref="p.7-18")
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.06, 0.0), (0.062, 0.10), (0.04, 0.12), (0.0, 0.12)], axis="Y", origin=(0.22, fs(-33.5), zc - 0.15), segs=20)
    revolve(bm, [(0.0, -0.012), (0.045, -0.012), (0.045, -0.002), (0.0, -0.002)], axis="Y", origin=(0.22, fs(-33.5), zc - 0.15), segs=20)
    alt = obj_from_bm("ELECTRICAL.alternator", bm, ctx.col, pivot=(0.22, fs(-33.5), zc - 0.15), mat=M["cast_alu"])
    _link(alt, grp)
    ctx.tag(alt, "ELECTRICAL", "60 A alternator (belt driven from the crankshaft pulley)", "المولد 60 أمبير", status="poh", ref="p.7-26")
    # belt: racetrack around the crank pulley (r 0.075) and alternator pulley (r 0.045)
    bm = new_bm()
    c1 = Vector((0, fs(-33.8), zc)); c2 = Vector((0.22, fs(-33.8), zc - 0.15)); r1, r2 = 0.078, 0.047
    d = (c2 - c1); L = d.length; dn = d / L
    a = math.acos((r1 - r2) / L)
    n = Vector((-dn.z, 0, dn.x))
    pts = []
    base = math.atan2(dn.z, dn.x)
    for i in range(19):
        t = base + a + (2 * math.pi - 2 * a) * i / 18
        pts.append(c1 + Vector((r1 * math.cos(t), 0, r1 * math.sin(t))))
    for i in range(19):
        t = base - a + (2 * a) * i / 18
        pts.append(c2 + Vector((r2 * math.cos(t), 0, r2 * math.sin(t))))
    pts.append(pts[0])
    tube(bm, pts, 0.005, segs=8, cap=False)
    belt = obj_from_bm("ELECTRICAL.alternator_belt", bm, ctx.col, pivot=c1, mat=M["hose_black"])
    _link(belt, grp)
    ctx.tag(belt, "ELECTRICAL", "Alternator drive belt", "سير المولد", status="estimated")
    # oil filter (rear), oil cooler (right rear baffle), dipstick
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.045, 0.0), (0.045, 0.12), (0.0, 0.12)], axis="Y", origin=(0.13, fs(-4.0), zc + 0.02), segs=20)
    of = obj_from_bm("OIL.oil_filter", bm, ctx.col, pivot=(0.13, fs(-4.0), zc + 0.02), mat=M["paint_white"])
    _link(of, grp)
    ctx.tag(of, "OIL", "Full-flow oil filter (spin-on)", "فلتر الزيت", status="poh", ref="p.7-24")
    bm = new_bm()
    box(bm, (0.05, 0.14, 0.13), center=(-0.30, fs(-9), zc - 0.02))
    for i in range(10):
        box(bm, (0.052, 0.002, 0.13), center=(-0.30, fs(-9) - 0.06 + i * 0.013, zc - 0.02))
    oc = obj_from_bm("OIL.oil_cooler", bm, ctx.col, pivot=(-0.30, fs(-9), zc - 0.02), mat=M["bare_alu"], smooth=False)
    _link(oc, grp)
    ctx.tag(oc, "OIL", "Oil cooler (on the right rear baffle, cooling air from the inlet)", "مبرّد الزيت", status="poh", ref="p.7-24")
    bm = new_bm()
    tube(bm, [Vector((0.05, fs(-10), zc + 0.15)), Vector((0.05, fs(-10.5), zc + 0.29))], 0.012, segs=10)
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.02), (0.0, 0.02)], axis="Z", origin=(0.05, fs(-10.5), zc + 0.29), segs=12)
    ds = obj_from_bm("OIL.dipstick_filler", bm, ctx.col, pivot=(0.05, fs(-10), zc + 0.15), mat=M["wire_yellow"])
    _link(ds, grp)
    ctx.tag(ds, "OIL", "Oil filler cap / dipstick (reached through the cowl oil door)", "غطاء تعبئة الزيت ومقياسه", status="poh", ref="p.8-x")
    # carburetor under the sump, airbox with carb heat valve, air filter in the lower nose
    bm = new_bm()
    box(bm, (0.10, 0.12, 0.11), center=(0, fs(-17), zc - 0.315))
    carb = obj_from_bm("INDUCTION.carburetor", bm, ctx.col, pivot=(0, fs(-17), zc - 0.26), mat=M["cast_alu"], smooth=False)
    add_bevel(carb, 0.01, 2)
    _link(carb, grp)
    ctx.tag(carb, "INDUCTION", "Carburetor (updraft, float type) with mixture and throttle arms", "المكربن (سحب علوي)", status="poh", ref="p.7-23")
    bm = new_bm()
    box(bm, (0.20, 0.18, 0.07), center=(0, fs(-17), zc - 0.405))
    ab = obj_from_bm("INDUCTION.airbox", bm, ctx.col, pivot=(0, fs(-17), zc - 0.37), mat=M["bare_alu"], smooth=False)
    _link(ab, grp)
    ctx.tag(ab, "INDUCTION", "Airbox with carburetor heat valve (heated air from the muffler shroud)", "صندوق الهواء مع صمام تسخين المكربن", status="poh", ref="p.7-24")
    bm = new_bm()
    box(bm, (0.24, 0.06, 0.12), center=(0, fs(-33), zc - 0.38))
    af = obj_from_bm("INDUCTION.air_filter", bm, ctx.col, pivot=(0, fs(-33), zc - 0.38), mat=M["grey_plastic"], smooth=False)
    _link(af, grp)
    ctx.tag(af, "INDUCTION", "Induction air filter (behind the lower cowl inlet)", "فلتر هواء السحب", status="poh", ref="p.7-24")
    bm = new_bm()
    tube(bm, [Vector((0, fs(-30), zc - 0.40)), Vector((0, fs(-20), zc - 0.42))], 0.035, segs=14)
    duct = obj_from_bm("INDUCTION.filter_duct", bm, ctx.col, pivot=(0, fs(-30), zc - 0.40), mat=M["hose_black"])
    _link(duct, grp)
    ctx.tag(duct, "INDUCTION", "Filtered air duct to the airbox", "قناة الهواء المفلتر", status="estimated")
    # muffler with heat shroud (cabin heat / carb heat source)
    bm = new_bm()
    revolve(bm, [(0.0, -0.19), (0.06, -0.19), (0.06, 0.19), (0.0, 0.19)], axis="X", origin=(0, fs(-13), zc - 0.43), segs=24)
    revolve(bm, [(0.065, -0.10), (0.08, -0.10), (0.08, 0.10), (0.065, 0.10)], axis="X", origin=(0, fs(-13), zc - 0.43), segs=24)
    muf = obj_from_bm("ENGINE.muffler", bm, ctx.col, pivot=(0, fs(-13), zc - 0.43), mat=M["exhaust"])
    _link(muf, grp)
    ctx.tag(muf, "ENGINE", "Muffler with heat shroud (source of cabin and carburetor heat)", "كاتم الصوت مع غلاف التسخين", status="poh", ref="p.7-24/35")
    # engine mount: tubular truss from four firewall points to the accessory housing lugs
    bm = new_bm()
    fw = [Vector((sx * 0.40, fs(0.5), z)) for sx in (-1, 1) for z in (1.02, 1.72)]
    lugs = [Vector((sx * 0.16, fs(-4.2), zc + sz * 0.15)) for sx in (-1, 1) for sz in (-1, 1)]
    for f_ in fw:
        for l in lugs:
            if (f_.x > 0) == (l.x > 0):
                tube(bm, [f_, l], 0.011, segs=8)
    for l in lugs:
        revolve(bm, [(0.0, -0.02), (0.03, -0.02), (0.03, 0.02), (0.0, 0.02)], axis="Y", origin=l, segs=12)
    mount = obj_from_bm("ENGINE.engine_mount", bm, ctx.col, pivot=(0, fs(0), zc), mat=M["paint_white"])
    _link(mount, ctx.groups["AIRFRAME"])
    ctx.tag(mount, "ENGINE", "Engine mount (welded steel tube truss with rubber shock mounts)", "حامل المحرك (هيكل أنابيب فولاذية)", status="estimated")
    # baffles: rear baffle plates with rubber seals, inter-cylinder baffles
    bm = new_bm()
    for sx in (-1, 1):
        box(bm, (0.33, 0.015, 0.30), center=(sx * 0.29, fs(-9.5), zc + 0.08))
        box(bm, (0.33, 0.02, 0.05), center=(sx * 0.29, fs(-9.5), zc + 0.255))
        box(bm, (0.015, 0.30, 0.22), center=(sx * 0.45, fs(-20), zc + 0.06))
    baf = obj_from_bm("ENGINE.baffles", bm, ctx.col, pivot=(0, fs(-10), zc), mat=M["bare_alu"], smooth=False)
    _link(baf, grp)
    ctx.tag(baf, "ENGINE", "Cooling baffles with rubber seals (pressure cooling from the inlets)", "حواجز هواء التبريد", status="poh", ref="p.7-25")
    bm = new_bm()
    for sx in (-1, 1):
        box(bm, (0.33, 0.02, 0.05), center=(sx * 0.29, fs(-9.5), zc + 0.255))
        box(bm, (0.015, 0.30, 0.03), center=(sx * 0.45, fs(-20), zc + 0.185))
    seal = obj_from_bm("ENGINE.baffle_seals", bm, ctx.col, pivot=(0, fs(-10), zc), mat=M["hose_black"], smooth=False)
    _link(seal, grp)
    ctx.tag(seal, "ENGINE", "Baffle seals (silicone/rubber strips against the cowl)", "أختام الحواجز المطاطية", status="estimated")
    # vacuum pump (rear accessory pad, left) and oil breather
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.09), (0.0, 0.09)], axis="Y", origin=(0.13, fs(-4.0), zc + 0.12), segs=16)
    vp = obj_from_bm("VACUUM.engine_driven_pump", bm, ctx.col, pivot=(0.13, fs(-4.0), zc + 0.12), mat=M["black_plastic"])
    _link(vp, grp)
    ctx.tag(vp, "VACUUM", "Engine-driven vacuum pump (dry, drives AI and DG)", "مضخة التفريغ", status="poh", ref="p.7-34")
    # fuel strainer on the firewall and fuel line to the carburetor
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.11), (0.0, 0.11)], axis="Z", origin=(0.25, fs(-2.5), 0.98), segs=14)
    fsx = obj_from_bm("FUEL.strainer", bm, ctx.col, pivot=(0.25, fs(-2.5), 0.98), mat=M["cast_alu"])
    _link(fsx, grp)
    ctx.tag(fsx, "FUEL", "Fuel strainer (gascolator) with drain — firewall, left", "مصفاة الوقود", status="poh", ref="p.7-28, 8-x")
    bm = new_bm()
    tube(bm, bezier(Vector((0.25, fs(-2.5), 0.98)), Vector((0.25, fs(-8), 0.95)), Vector((0.08, fs(-14), 1.02)), Vector((0.05, fs(-17), zc - 0.30)), 12), 0.006, segs=8)
    fl_ = obj_from_bm("FUEL.line_to_carburetor", bm, ctx.col, pivot=(0.25, fs(-2.5), 0.98), mat=M["bare_alu"])
    _link(fl_, grp)
    ctx.tag(fl_, "FUEL", "Fuel line strainer → carburetor", "خط الوقود إلى المكربن", status="poh", ref="p.7-28")
    # battery on the firewall (left, forward side)
    bm = new_bm()
    box(bm, (0.22, 0.14, 0.20), center=(0.30, fs(-5.5), 1.45))
    bat = obj_from_bm("ELECTRICAL.battery", bm, ctx.col, pivot=(0.30, fs(-5.5), 1.35), mat=M["black_plastic"], smooth=False)
    add_bevel(bat, 0.01, 2)
    _link(bat, grp)
    ctx.tag(bat, "ELECTRICAL", "24 V battery (firewall, left forward side)", "البطارية 24 فولت", status="poh", ref="p.7-26")

def build(ctx):
    grp = ctx.groups["ENGINE"]
    grp.location = ORIGIN
    build_case(ctx, grp)
    for c in (1, 2, 3, 4):
        build_cylinder(ctx, grp, c)
    build_crank_train(ctx, grp)
    build_accessories(ctx, grp)
