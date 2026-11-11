"""Markings laid on the skin as separate pieces: the operator's wordmark and a few placards.

A marking painted into the skin's own texture is only as sharp as that texture and is stretched wherever the skin
is unrolled unevenly. Each marking here is a small sheet with its own texels, pressed onto the skin where it
belongs, so it stays sharp and undistorted in every quality level.
"""
import bpy
from mathutils import Vector

from .units import fs, wl
from .shapes import new_bm, obj_from_bm, parent_keep
from .atlas import decal_cells

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
STAND_OFF = 0.30       # the sheet starts this far off the skin and is pressed onto it
LIFT = 0.0012          # how far it stays above the paint


def marking(ctx, name, cell, centre, width, across, up, target, parent, label_en, label_ar, segments=(18, 5), note=""):
    """A marking of the decal atlas, `width` wide, its letters running along `across` with their tops toward `up`,
    pressed onto `target` from the side that across x up looks out of."""
    (u0, v0, u1, v1), aspect = decal_cells()[cell]
    height = width / aspect
    out = Vector(across).cross(Vector(up)).normalized()
    centre = Vector(centre)
    bm = new_bm(); uv = bm.loops.layers.uv.active
    nx, ny = segments
    grid = [[(bm.verts.new(centre + Vector(across) * ((i / nx - 0.5) * width) + Vector(up) * ((j / ny - 0.5) * height) + out * STAND_OFF),
              (u0 + (u1 - u0) * i / nx, v0 + (v1 - v0) * j / ny)) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            quad = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            f = bm.faces.new([q[0] for q in quad]); f.smooth = True
            for l, q in zip(f.loops, quad):
                l[uv].uv = q[1]
    ob = obj_from_bm(name, bm, ctx.col, pivot=centre, mat=ctx.mats["decals"])
    m = ob.modifiers.new("onto_skin", "SHRINKWRAP")
    m.target = target; m.wrap_method = "PROJECT"; m.offset = LIFT
    axis = max(range(3), key=lambda k: abs(out[k]))
    m.use_project_x, m.use_project_y, m.use_project_z = axis == 0, axis == 1, axis == 2
    m.use_negative_direction = out[axis] > 0; m.use_positive_direction = out[axis] < 0      # back toward the skin
    m.project_limit = STAND_OFF * 2.5
    parent_keep(ob, parent)
    # every corner of the sheet must have found the skin: one that did not would hang in the air beside the aircraft
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    missed = sum(1 for v in me.vertices if (ob.matrix_world @ v.co - centre).dot(out) > STAND_OFF * 0.8)
    ev.to_mesh_clear()
    if missed:
        raise RuntimeError(f"{name}: {missed} points of the marking do not lie over {target.name}; move it or make it smaller")
    ob["keep_faces"] = True                 # the low quality level must not thin it out: its texels are its picture
    ctx.tag(ob, "AIRFRAME", label_en, label_ar, status="estimated", kind="marking",
            note=note or "A marking of this model's own paint scheme; not a record of any aircraft's markings")
    return ob


def build(ctx):
    scene = bpy.data.objects
    fus = scene.get("AIRFRAME.fuselage")
    # ---- the operator's wordmark on the rear fuselage, above the band, read from each side
    if fus:
        for side, sx in (("L", 1), ("R", -1)):
            marking(ctx, f"AIRFRAME.marking_wordmark_{side}", "WORDMARK", (sx * 0.34, fs(137.5), 1.548), 0.50, Y * sx, Z, fus, ctx.groups["AIRFRAME"],
                    f"Operator's wordmark, {'left' if sx > 0 else 'right'} side", "شعار المشغّل، الجانب " + ("الأيسر" if sx > 0 else "الأيمن"))
    # ---- the fin: the wordmark again, above the band
    fin = scene.get("EMPENNAGE.fin")
    if fin:
        for side, sx in (("L", 1), ("R", -1)):
            # between the band and the point where the ADF sense wire meets the leading edge (WL 80), so the wire does not cross it
            marking(ctx, f"EMPENNAGE.marking_wordmark_{side}", "WORDMARK", (sx * 0.02, fs(243.5), wl(75.4)), 0.36, Y * sx, Z, fin, ctx.groups["EMPENNAGE"],
                    f"Operator's wordmark on the fin, {'left' if sx > 0 else 'right'} side", "شعار المشغّل على الزعنفة، الجانب " + ("الأيسر" if sx > 0 else "الأيمن"), segments=(12, 4))
    # ---- beside each fuel filler: the grade and the quantity (POH p.1-3: 100LL or 100; p.1-4: 21.5 gal in each standard tank)
    for side in ("L", "R"):
        cap = scene.get(f"WING_{side}.fuel_cap"); wing = scene.get(f"WING_{side}.wing")
        if cap and wing:
            at = cap.matrix_world.translation
            marking(ctx, f"WING_{side}.marking_fuel", "FUEL", (at.x, at.y + 0.105, at.z), 0.13, X, Y, wing, wing,      # read from the leading edge, where one stands to fill the tank
                    f"Fuel placard at the {'left' if side == 'L' else 'right'} filler: grade and quantity", "لوحة الوقود عند فتحة التعبئة " + ("اليسرى" if side == "L" else "اليمنى") + ": النوع والكمية",
                    segments=(6, 3), note="Grade 100LL (POH p.1-3) and 21.5 US gal a tank (POH p.1-4); the wording and form of the aircraft's own placard are not reproduced")
    # ---- on each flap, near the root: no step
    for side, sx in (("L", 1), ("R", -1)):
        flap = scene.get(f"WING_{side}.flap")
        if flap:
            box = [flap.matrix_world @ Vector(c) for c in flap.bound_box]
            y0, y1 = min(p.y for p in box), max(p.y for p in box); x_in = min(abs(p.x) for p in box); z1 = max(p.z for p in box)
            marking(ctx, f"WING_{side}.marking_no_step", "NO_STEP", (sx * (x_in + 0.28), (y0 + y1) / 2 + 0.02, z1), 0.24, -X, -Y, flap, flap,
                    f"NO STEP marking on the {'left' if sx > 0 else 'right'} flap", "علامة «ممنوع الدوس» على القلاب " + ("الأيسر" if sx > 0 else "الأيمن"), segments=(8, 3))
