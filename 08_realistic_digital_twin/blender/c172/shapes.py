"""Geometry helpers for the Phase 8 build (bmesh based)."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

from .profiles import naca4, airfoil_interp, split_airfoil, superellipse, rounded_rect, ellipse, smoothstep, resample_loop, interp_table

# ----------------------------------------------------------------------------- bmesh builders

def new_bm():
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")
    return bm

def loft(bm, rings, close=True, cap_start=False, cap_end=False, uv_u_scale=1.0, uv_v=None, flip=False):
    """Connect successive rings (lists of Vector) with quads. Rings must have equal length.
    Adds UVs: u around the ring, v along the loft. Returns the created faces."""
    uv = bm.loops.layers.uv.active
    k = len(rings[0]); m = len(rings)
    verts = [[bm.verts.new(p) for p in ring] for ring in rings]
    faces = []
    if uv_v is None:
        uv_v = [i / (m - 1) for i in range(m)]
    kk = k if close else k - 1
    for j in range(m - 1):
        for i in range(kk):
            i2 = (i + 1) % k
            quad = [verts[j][i], verts[j][i2], verts[j + 1][i2], verts[j + 1][i]]
            if flip:
                quad.reverse()
            try:
                f = bm.faces.new(quad)
            except ValueError:
                continue
            f.smooth = True
            faces.append(f)
            u0, u1 = i / k * uv_u_scale, (i + 1) / k * uv_u_scale
            coords = [(u0, uv_v[j]), (u1, uv_v[j]), (u1, uv_v[j + 1]), (u0, uv_v[j + 1])]
            if flip:
                coords.reverse()
            for l, c in zip(f.loops, coords):
                l[uv].uv = c
    if cap_start:
        f = bm.faces.new(list(reversed(verts[0])) if not flip else verts[0]); f.smooth = False; faces.append(f)
        for l in f.loops:
            l[uv].uv = (0.5 + 0.1 * l.vert.co.x, 0.5 + 0.1 * l.vert.co.z)
    if cap_end:
        f = bm.faces.new(verts[-1] if not flip else list(reversed(verts[-1]))); f.smooth = False; faces.append(f)
        for l in f.loops:
            l[uv].uv = (0.5 + 0.1 * l.vert.co.x, 0.5 + 0.1 * l.vert.co.z)
    return faces

def extrude_profile(bm, pts2d, axis_u, axis_v, origin, depth_axis, d0, d1, uv_scale=1.0, smooth_sides=True):
    """Prism from a closed 2D loop: axis_u/axis_v (Vectors) span the loop plane, extruded
    from d0 to d1 along depth_axis. UVs: sides unrolled, caps planar."""
    uv = bm.loops.layers.uv.active
    o = Vector(origin)
    ring0 = [bm.verts.new(o + axis_u * u + axis_v * v + depth_axis * d0) for u, v in pts2d]
    ring1 = [bm.verts.new(o + axis_u * u + axis_v * v + depth_axis * d1) for u, v in pts2d]
    k = len(pts2d)
    faces = []
    for i in range(k):
        i2 = (i + 1) % k
        f = bm.faces.new([ring0[i], ring0[i2], ring1[i2], ring1[i]])
        f.smooth = smooth_sides
        for l, c in zip(f.loops, [(i / k, 0), ((i + 1) / k, 0), ((i + 1) / k, 1), (i / k, 1)]):
            l[uv].uv = (c[0] * uv_scale, c[1] * uv_scale)
        faces.append(f)
    c0 = bm.faces.new(list(reversed(ring0)))
    c1 = bm.faces.new(ring1)
    for f in (c0, c1):
        f.smooth = False
        for l in f.loops:
            l[uv].uv = (0.5 + l.vert.co.dot(axis_u) * uv_scale, 0.5 + l.vert.co.dot(axis_v) * uv_scale)
    bmesh.ops.recalc_face_normals(bm, faces=faces + [c0, c1])
    return faces + [c0, c1]

def revolve(bm, profile, axis="Y", segs=32, origin=(0, 0, 0), cap_start=True, cap_end=True, uv_u_scale=1.0):
    """Revolve a profile of (radius, along) pairs around an axis through origin.
    Radii of 0 at the ends create poles."""
    rings = []
    o = Vector(origin)
    for r, a in profile:
        ring = []
        for i in range(segs):
            t = 2 * math.pi * i / segs
            if axis == "Y":
                p = o + Vector((r * math.cos(t), a, r * math.sin(t)))
            elif axis == "Z":
                p = o + Vector((r * math.cos(t), r * math.sin(t), a))
            else:
                p = o + Vector((a, r * math.cos(t), r * math.sin(t)))
            ring.append(p)
        rings.append(ring)
    faces = loft(bm, rings, close=True, cap_start=cap_start and profile[0][0] > 1e-6,
                 cap_end=cap_end and profile[-1][0] > 1e-6, uv_u_scale=uv_u_scale)
    # merge pole verts
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    return faces

def box(bm, size, center=(0, 0, 0), uv_scale=1.0):
    sx, sy, sz = [s / 2 for s in size]
    c = Vector(center)
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * sx * 2, v.co.y * sy * 2, v.co.z * sz * 2)) + c
    uv = bm.loops.layers.uv.active
    for f in bm.faces:
        if f in r.get("faces", []) or True:
            n = f.normal
            for l in f.loops:
                p = l.vert.co
                if abs(n.z) > 0.5: l[uv].uv = (p.x * uv_scale, p.y * uv_scale)
                elif abs(n.x) > 0.5: l[uv].uv = (p.y * uv_scale, p.z * uv_scale)
                else: l[uv].uv = (p.x * uv_scale, p.z * uv_scale)
    return r["verts"]

def cylinder(bm, r, length, axis="Y", origin=(0, 0, 0), segs=24, r2=None, caps=True):
    r2 = r if r2 is None else r2
    prof = [(r, 0.0), (r2, length)]
    return revolve(bm, prof, axis=axis, segs=segs, origin=origin, cap_start=caps, cap_end=caps)

def tube(bm, points, radius, segs=12, radius_end=None, cap=True):
    """Tube along a polyline of Vectors using parallel-transport frames."""
    n = len(points)
    frames = []
    t_prev = None; nrm = None
    for i in range(n):
        if i == 0: t = (points[1] - points[0]).normalized()
        elif i == n - 1: t = (points[-1] - points[-2]).normalized()
        else: t = (points[i + 1] - points[i - 1]).normalized()
        if nrm is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nrm = t.cross(up).normalized()
        else:
            nrm = (nrm - t * nrm.dot(t)).normalized()
        frames.append((t, nrm, t.cross(nrm)))
    rings = []
    for i, (t, a, b) in enumerate(frames):
        rr = radius if radius_end is None else radius + (radius_end - radius) * i / (n - 1)
        rings.append([points[i] + (a * math.cos(2 * math.pi * j / segs) + b * math.sin(2 * math.pi * j / segs)) * rr for j in range(segs)])
    return loft(bm, rings, close=True, cap_start=cap, cap_end=cap)

def bezier(p0, p1, p2, p3, n=12):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(p0 * (1 - t)**3 + p1 * 3 * t * (1 - t)**2 + p2 * 3 * t**2 * (1 - t) + p3 * t**3)
    return out

def finish(bm, me, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    me.update()

# ----------------------------------------------------------------------------- object helpers

def frame_matrix(origin, x_axis=None, z_axis=None):
    """World matrix with the given origin and local X / Z directions (Y = Z × X)."""
    x = Vector(x_axis).normalized() if x_axis is not None else Vector((1, 0, 0))
    z = Vector(z_axis).normalized() if z_axis is not None else Vector((0, 0, 1))
    if abs(x.dot(z)) > 0.999:
        z = Vector((0, 1, 0))
    y = z.cross(x).normalized(); z = x.cross(y).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m

def obj_from_bm(name, bm, collection, pivot=(0, 0, 0), parent=None, smooth=True, mat=None, props=None, x_axis=None, z_axis=None):
    """Create an object whose origin sits at `pivot` (world) with optional local axes; the
    mesh is built in world coordinates and transformed into the object frame."""
    me = bpy.data.meshes.new(name)
    M = frame_matrix(pivot, x_axis, z_axis)
    Mi = M.inverted()
    for v in bm.verts:
        v.co = Mi @ v.co
    finish(bm, me, smooth=smooth)
    ob = bpy.data.objects.new(name, me)
    ob.matrix_world = M
    collection.objects.link(ob)
    if parent is not None:
        parent_keep(ob, parent)
    if mat is not None:
        me.materials.append(mat)
    if props:
        for k, v in props.items():
            ob[k] = v
    return ob

def parent_keep(child, parent):
    """Parent `child` to `parent` keeping the child's current world transform."""
    bpy.context.view_layer.update()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    return child

def empty(name, collection, location=(0, 0, 0), parent=None, props=None):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.2
    ob.location = location
    collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    if props:
        for k, v in props.items():
            ob[k] = v
    return ob

def add_subsurf(ob, levels=2):
    m = ob.modifiers.new("subsurf", "SUBSURF")
    m.levels = levels; m.render_levels = levels
    m.subdivision_type = "CATMULL_CLARK"
    return m

def add_boolean(ob, cutter, op="DIFFERENCE", name="bool"):
    m = ob.modifiers.new(name, "BOOLEAN")
    m.operation = op; m.object = cutter; m.solver = "EXACT"
    cutter.hide_render = True; cutter.display_type = "WIRE"
    return m

def add_solidify(ob, thickness=0.02, offset=-1.0):
    m = ob.modifiers.new("solidify", "SOLIDIFY")
    m.thickness = thickness; m.offset = offset; m.use_even_offset = True
    return m

def add_edge_split(ob, angle_deg=40):
    m = ob.modifiers.new("edgesplit", "EDGE_SPLIT")
    m.split_angle = math.radians(angle_deg)
    return m

def add_bevel(ob, width=0.004, segments=2, angle_deg=40):
    m = ob.modifiers.new("bevel", "BEVEL")
    m.width = width; m.segments = segments; m.limit_method = "ANGLE"; m.angle_limit = math.radians(angle_deg)
    return m

def apply_all(ob):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        for m in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)

def mirror_x(ob, name):
    """Return an X-mirrored copy (separate mesh data) with flipped normals fixed."""
    me = ob.data.copy()
    new = ob.copy(); new.data = me; new.name = name; me.name = name
    for v in me.vertices:
        v.co.x = -v.co.x
    me.flip_normals()
    new.location = (-ob.location.x, ob.location.y, ob.location.z)
    for c in ob.users_collection:
        c.objects.link(new)
    return new

def smart_uv(ob, angle=66, margin=0.02):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
        bpy.ops.object.mode_set(mode="OBJECT")
