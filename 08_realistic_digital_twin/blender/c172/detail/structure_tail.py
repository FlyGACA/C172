"""Tail structure: what is inside the fin, the rudder, the stabiliser and the elevator (POH p.7-3, 7-8).

"The vertical stabilizer consists of a spar, formed sheet metal ribs and reinforcements, a wrap-around
skin panel, formed leading edge skin and a dorsal. The rudder is constructed of a formed leading edge
skin containing hinge halves, a center wrap-around skin panel, ribs, an aft wrap-around skin panel
which is joined at the trailing edge of the rudder by a filler strip, and a ground adjustable trim tab
at the base of the trailing edge. The top of the rudder incorporates a leading edge extension which
contains a balance weight. The horizontal stabilizer is constructed of a forward and aft spar, ribs
and stiffeners, center, left, and right wrap-around skin panels, and formed leading edge skins. ...
Construction of the elevator consists of formed leading edge skins, a forward spar, aft channel, ribs,
torque tube and bellcrank ... The leading edge of both left and right elevator tips incorporate
extensions which contain balance weights."

poh: which members exist. estimated: where they lie (spar lines from the skin seams of the
manufacturer's drawings, rib positions and every section representative).
"""
import bpy
from mathutils import Vector

from .. import units as U
from ..units import IN, fs, wl
from .. import airframe as A
from . import geom2d
from .common import Plane, sheet, wall, strip, rod, disc, box, bolt, part, new_bm, X, Y, Z

SKIN = 0.0012
FIN_RIBS = [58.0, 66.0, 74.0, 82.0, 89.5]            # water lines of the fin ribs (in)
RUDDER_RIBS = [36.0, 44.0, 52.0, 60.0, 68.0, 76.0, 84.0]
STAB_RIBS = [8.0, 20.0, 32.0, 44.0, 56.0]            # butt lines of the stabiliser and elevator ribs (in)


FIN_WIRE_OFFSET = 2.4                  # the wiring to the beacon runs this far (in) behind the leading-edge former, through a hole in each rib
FIN_COAX_X = 0.013                     # the cable to the navigation antenna passes each rib beside the wiring, this far to the right, through a hole of its own


def fin_wire_station(water):
    """Station (in) of the wiring in the vertical stabiliser at a water line (in)."""
    (s0, w0), (s1, w1) = A.FIN_SPAR
    return s0 + (s1 - s0) * (water - w0) / (w1 - w0) + FIN_WIRE_OFFSET


def _fin_rib_outline(water, front, rear, steps=10):
    """Outline of a horizontal slice of the vertical tail between two stations, in (aft, left) metres."""
    stations = [front + (rear - front) * i / steps for i in range(steps + 1)]
    left = [(fs(st), max(0.002, A.fin_half_thickness(st, water) - SKIN)) for st in stations]
    return left + [(y, -x) for y, x in reversed(left)]


def build(ctx):
    fin = bpy.data.objects["EMPENNAGE.fin"]
    rudder = bpy.data.objects["EMPENNAGE.rudder"]
    elevator = bpy.data.objects["EMPENNAGE.elevator"]

    # ------------------------------------------------------------------ vertical stabiliser
    def along(line, water):
        (s0, w0), (s1, w1) = line
        return s0 + (s1 - s0) * (water - w0) / (w1 - w0)

    def fin_spar(name, line, offset, low, high, depth, label_en, label_ar, status, note):
        waters = [low + (high - low) * i / 8 for i in range(9)]
        centre, width = [], []
        for water in waters:
            station = along(line, water) + offset
            centre.append(Vector((0, fs(station), wl(water))))
            width.append(max(0.004, A.fin_half_thickness(station, water) - SKIN - 0.001))
        bm = new_bm()
        strip(bm, [c + X * w for c, w in zip(centre, width)], [c - X * w for c, w in zip(centre, width)], Vector((0, 0.002, 0)))
        for sign in (1, -1):                                   # a flange under each skin
            edge = [c + X * (sign * w) for c, w in zip(centre, width)]
            strip(bm, edge, [p + Vector((0, depth, 0)) for p in edge], Vector((-sign * 0.0015, 0, 0)))
        return part(ctx, name, bm, "EMPENNAGE", "EMPENNAGE", label_en, label_ar, "bare_alu", status=status, note=note, ref="p.7-3")

    top = A.FIN_TOP[0][1] - 1.5
    fin_spar("EMPENNAGE.fin_spar", A.RUD_HINGE, -1.6, 41.5, min(top, 91.5), -0.03, "Vertical stabiliser spar (carries the rudder hinges)",
             "عارضة المثبت الرأسي (تحمل مفصلات الدفة)", "poh", "The vertical stabiliser has one spar (POH); it stands just ahead of the rudder hinge line")
    fin_spar("EMPENNAGE.fin_leading_edge_former", A.FIN_SPAR, 0.0, 46.0, 88.5, 0.02, "Leading-edge skin former of the vertical stabiliser",
             "مُشكِّل جلد الحافة الأمامية للمثبت الرأسي", "estimated", "Where the formed leading-edge skin meets the wrap-around panel: the skin seam of the manufacturer's side view")
    for water in FIN_RIBS:
        front = along(A.FIN_SPAR, water) + 0.6
        rear = along(A.RUD_HINGE, water) - 2.2
        if rear - front < 3.0:
            continue
        plane = Plane((0, 0, wl(water)), Y, X)
        outline = _fin_rib_outline(water, front, rear)
        wire_station = fin_wire_station(water)
        if A.fin_half_thickness(wire_station, water) - SKIN > 0.011:            # an opening for the wiring to the beacon, the lightening holes behind it
            holes = geom2d.lightening_holes(outline, fs(wire_station) + 0.014, fs(rear) - 0.02, 3, 0.016, segments=10) + [geom2d.circle(fs(wire_station), 0.0, 0.006, 10),
                                                                                                                                 geom2d.circle(fs(wire_station), -FIN_COAX_X, 0.005, 10)]
        else:
            holes = geom2d.lightening_holes(outline, fs(front) + 0.02, fs(rear) - 0.02, 3, 0.016, segments=10)
        bm = new_bm()
        sheet(bm, plane, outline, 0.001, holes, offset=-0.0005)
        part(ctx, f"EMPENNAGE.fin_rib_wl{int(water):02d}", bm, "EMPENNAGE", "EMPENNAGE", f"Vertical stabiliser rib, water line {water:g}",
             f"ضلع المثبت الرأسي، خط الماء {water:g}", "bare_alu", status="estimated", note="Formed sheet-metal ribs (POH p.7-3); position representative")

    # ------------------------------------------------------------------ rudder (parts move with it)
    for water in RUDDER_RIBS:
        hinge = max(along(A.RUD_HINGE, water), A.RUD_FOOT[0][0])
        te = A.rudder_te_fs(water)
        if te - hinge < 5.0:
            continue
        plane = Plane((0, 0, wl(water)), Y, X)
        nose = max(0.004, A.fin_half_thickness(hinge, water) * 0.92 - SKIN)
        steps = 6
        left = []
        for i in range(steps + 1):
            t = i / steps
            station = hinge + 0.8 + (te - 1.6 - hinge - 0.8) * t
            left.append((fs(station), max(0.0015, nose * (1 - (station - hinge) / (te - hinge)))))
        outline = left + [(y, -x) for y, x in reversed(left)]
        bm = new_bm()
        sheet(bm, plane, outline, 0.001, offset=-0.0005)
        part(ctx, f"EMPENNAGE.rudder_rib_wl{int(water):02d}", bm, "EMPENNAGE", "EMPENNAGE", f"Rudder rib, water line {water:g}", f"ضلع الدفة، خط الماء {water:g}",
             "bare_alu", status="estimated", parent=rudder, note="Ribs between the rudder's skin panels (POH p.7-3); position representative")
    # balance weight in the extension at the top of the rudder, ahead of the hinge line
    water = 91.0
    hinge = along(A.RUD_HINGE, water)
    bm = new_bm()
    box(bm, (0.018, 0.10, 0.03), center=(0, fs(hinge) - 0.02, wl(water) + 0.004))
    part(ctx, "EMPENNAGE.rudder_balance_weight", bm, "EMPENNAGE", "EMPENNAGE", "Rudder balance weight (in the leading-edge extension at the top)",
         "ثقل موازنة الدفة (في امتداد الحافة الأمامية عند القمة)", "steel", status="poh", ref="p.7-3", parent=rudder)
    # ground-adjustable trim tab at the base of the trailing edge
    bm = new_bm()
    te = A.RUD_TE[0][0]
    box(bm, (0.0012, 0.045, 0.20), center=(0, fs(te) + 0.02, wl(40.5)))
    part(ctx, "EMPENNAGE.rudder_trim_tab", bm, "EMPENNAGE", "EMPENNAGE", "Rudder trim tab (ground adjustable)", "لسان موازنة الدفة (يُضبط على الأرض)",
         "bare_alu", status="poh", ref="p.7-3", parent=rudder)
    # hinges: bracket on the fin spar with a bolt through the rudder's hinge half
    for number, water in enumerate((44.0, 64.0, 86.0), 1):
        hinge = along(A.RUD_HINGE, water)
        centre = Vector((0, fs(hinge), wl(water)))
        bm = new_bm()
        for sign in (1, -1):
            box(bm, (0.003, 0.05, 0.022), center=centre + Vector((sign * 0.008, -0.018, 0)))
        bolt(bm, centre + Vector((-0.012, 0, 0)), X, 0.005, 0.024)
        part(ctx, f"EMPENNAGE.rudder_hinge_{number}", bm, "EMPENNAGE", "EMPENNAGE", f"Rudder hinge {number} (bracket and bolt)", f"مفصلة الدفة {number} (حامل ومسمار)",
             "steel", status="estimated", note="The rudder's leading-edge skin contains the hinge halves (POH p.7-3); three hinges are representative")

    # ------------------------------------------------------------------ horizontal stabiliser
    def chord_point(xabs, side, xc, z=0.0):
        c = A.stab_chord(xabs)
        return Vector((side * xabs, A.stab_te_y(xabs) - c + xc * c, A.STAB_Z + z))

    def half_thickness(xabs, xc):
        return max(0.003, A.airfoil_y(A.AF_TAIL, xc, True) * A.stab_chord(xabs) - SKIN)

    def hinge_xc(xabs):
        return 1 - A.elev_chord(xabs) / A.stab_chord(xabs)

    def stab_spar(name, xc_fn, depth, label_en, label_ar):
        xs = [-A.STAB_END + 0.02 + (2 * A.STAB_END - 0.04) * i / 16 for i in range(17)]
        tops, bottoms = [], []
        for x in xs:
            xc = xc_fn(abs(x))
            h = half_thickness(abs(x), xc)
            p = chord_point(abs(x), 1 if x >= 0 else -1, xc)
            tops.append(p + Z * h); bottoms.append(p - Z * h)
        bm = new_bm()
        strip(bm, tops, bottoms, Vector((0, 0.002, 0)))
        strip(bm, tops, [p + Vector((0, depth, 0)) for p in tops], Vector((0, 0, -0.0015)))
        strip(bm, bottoms, [p + Vector((0, depth, 0)) for p in bottoms], Vector((0, 0, 0.0015)))
        return part(ctx, name, bm, "EMPENNAGE", "EMPENNAGE", label_en, label_ar, "bare_alu", status="poh", ref="p.7-8",
                    note="The stabiliser has a forward and an aft spar (POH); their lines follow the skin seams of the manufacturer's top view")
    stab_spar("EMPENNAGE.stabilizer_front_spar", lambda x: A.STAB_SPAR_XC, 0.022, "Horizontal stabiliser forward spar", "العارضة الأمامية للمثبت الأفقي")
    stab_spar("EMPENNAGE.stabilizer_rear_spar", lambda x: hinge_xc(x) - 0.045, -0.022, "Horizontal stabiliser aft spar", "العارضة الخلفية للمثبت الأفقي")

    def section_rib(name, xabs, side, x0, x1, holes, label_en, label_ar, parent=None, status="estimated"):
        c = A.stab_chord(xabs)
        steps = 10
        upper = []
        for i in range(steps + 1):
            xc = x0 + (x1 - x0) * i / steps
            upper.append((xc * c, max(0.0015, A.airfoil_y(A.AF_TAIL, xc, True) * c - SKIN)))
        outline = [(a, -b) for a, b in upper] + list(reversed(upper))
        plane = Plane(chord_point(xabs, side, 0.0), Y, Z)
        cut = geom2d.lightening_holes(outline, x0 * c + 0.015, x1 * c - 0.015, holes, 0.014, segments=10) if holes else []
        bm = new_bm()
        sheet(bm, plane, outline, 0.001, cut, offset=-0.0005)
        return part(ctx, name, bm, "EMPENNAGE", "EMPENNAGE", label_en, label_ar, "bare_alu", status=status, parent=parent, station_in=round(side * xabs / IN, 1))

    for station in STAB_RIBS:
        for side, S in ((1, "L"), (-1, "R")):
            x = station * IN
            h = hinge_xc(x)
            section_rib(f"EMPENNAGE.stabilizer_rib_{S}{int(station):02d}", x, side, A.STAB_SPAR_XC + 0.012, h - 0.057, 2,
                        f"Stabiliser rib, butt line {station:g} {'left' if side > 0 else 'right'}", f"ضلع المثبت الأفقي، {'يسار' if side > 0 else 'يمين'} {station:g}")
            section_rib(f"EMPENNAGE.stabilizer_nose_rib_{S}{int(station):02d}", x, side, 0.012, A.STAB_SPAR_XC - 0.012, 0,
                        f"Stabiliser nose rib, butt line {station:g} {'left' if side > 0 else 'right'}", f"ضلع مقدمة المثبت الأفقي، {'يسار' if side > 0 else 'يمين'} {station:g}")
            # elevator rib behind it (moves with the elevator)
            section_rib(f"EMPENNAGE.elevator_rib_{S}{int(station):02d}", x, side, h + 0.06, 0.97, 1,
                        f"Elevator rib, butt line {station:g} {'left' if side > 0 else 'right'}", f"ضلع الرافع، {'يسار' if side > 0 else 'يمين'} {station:g}", parent=elevator)

    # ------------------------------------------------------------------ elevator: forward spars, torque tube, balance weights
    for side, S in ((1, "L"), (-1, "R")):
        xs = [0.12 + (A.STAB_END - 0.14) * i / 10 for i in range(11)]
        tops, bottoms = [], []
        for x in xs:
            xc = hinge_xc(x) + 0.035
            h = half_thickness(x, xc)
            p = chord_point(x, side, xc)
            tops.append(p + Z * h); bottoms.append(p - Z * h)
        bm = new_bm()
        strip(bm, tops, bottoms, Vector((0, 0.0018, 0)))
        part(ctx, f"EMPENNAGE.elevator_spar_{S}", bm, "EMPENNAGE", "EMPENNAGE", f"Elevator forward spar, {'left' if side > 0 else 'right'}",
             f"العارضة الأمامية للرافع، {'اليسرى' if side > 0 else 'اليمنى'}", "bare_alu", status="poh", ref="p.7-8", parent=elevator)
        # balance weight in the extension ahead of the hinge line at the tip
        tip = A.STAB_END + 0.06
        bm = new_bm()
        box(bm, (0.07, 0.11, 0.02), center=chord_point(tip, side, 0.16))
        part(ctx, f"EMPENNAGE.elevator_balance_weight_{S}", bm, "EMPENNAGE", "EMPENNAGE", f"Elevator balance weight, {'left' if side > 0 else 'right'} tip",
             f"ثقل موازنة الرافع، الطرف {'الأيسر' if side > 0 else 'الأيمن'}", "steel", status="poh", ref="p.7-8", parent=elevator)
    hinge_y = A.ELEV_HINGE_Y
    bm = new_bm()
    rod(bm, (-0.16, hinge_y + 0.012, A.STAB_Z), (0.16, hinge_y + 0.012, A.STAB_Z), 0.016, segs=14)
    part(ctx, "EMPENNAGE.elevator_torque_tube", bm, "EMPENNAGE", "EMPENNAGE", "Elevator torque tube (joins the two halves)", "أنبوب عزم الرافع (يربط النصفين)",
         "steel", status="poh", ref="p.7-8", parent=elevator)
