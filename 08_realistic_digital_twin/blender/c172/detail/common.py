"""Builders shared by the detail packs: sheet-metal parts, extruded sections, tubes and cables,
small hardware, and the one function that turns a mesh into a tagged part."""
import math

import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

from ..shapes import new_bm, obj_from_bm, parent_keep, tube, revolve, box, cylinder, bezier, loft
from . import geom2d

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


class Plane:
    """A drawing plane in space: origin and two unit vectors. Points given as (a, b[, depth]) lie at
    origin + a*u + b*v + depth*n, with n = u × v."""

    def __init__(self, origin, u, v):
        self.origin = Vector(origin)
        self.u = Vector(u).normalized()
        self.v = Vector(v).normalized()
        self.n = self.u.cross(self.v).normalized()

    def at(self, a, b, depth=0.0):
        return self.origin + self.u * a + self.v * b + self.n * depth

    def flat(self, point):
        """(a, b, depth) of a point in space."""
        d = Vector(point) - self.origin
        return d.dot(self.u), d.dot(self.v), d.dot(self.n)


def sheet(bm, plane, outline, thickness, holes=(), offset=0.0):
    """Flat plate with optional holes. `outline` and `holes` are closed 2D loops in the plane; the plate
    occupies offset .. offset + thickness along the plane normal."""
    loops = [geom2d.counter_clockwise(outline)] + [list(reversed(geom2d.counter_clockwise(h))) for h in holes]
    flat = [p for loop in loops for p in loop]
    triangles = tessellate_polygon([[Vector((p[0], p[1], 0.0)) for p in loop] for loop in loops])
    layers = []
    for depth in (offset, offset + thickness):
        layers.append([bm.verts.new(plane.at(p[0], p[1], depth)) for p in flat])
    def sliver(a, b, c):                              # a triangle with no area: three points in line
        (ax, ay), (bx, by), (cx, cy) = flat[a], flat[b], flat[c]
        return abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) < 1e-11

    triangles = [t for t in triangles if len(set(t)) == 3 and not sliver(*t)]
    for layer, flip in ((layers[0], True), (layers[1], False)):
        for a, b, c in triangles:
            try:
                bm.faces.new((layer[a], layer[c], layer[b]) if flip else (layer[a], layer[b], layer[c]))
            except ValueError:
                pass
    start = 0
    for loop in loops:
        count = len(loop)
        for i in range(count):
            j = (i + 1) % count
            try:
                bm.faces.new((layers[0][start + i], layers[0][start + j], layers[1][start + j], layers[1][start + i]))
            except ValueError:
                pass
        start += count


def wall(bm, plane, path, thickness, depth0, depth1, closed=True, inward=True):
    """A thin wall standing on a 2D path in the plane, from depth0 to depth1 along the normal: the
    flange of a formed rib or frame. `inward` puts its thickness on the inside of a closed path."""
    pts = list(path)
    if closed:
        inner = geom2d.inset(pts, thickness if inward else -thickness)
        if geom2d.area(pts) < 0:                      # inset() returns the loop counter-clockwise
            inner = list(reversed(inner))
    else:
        inner = []
        for i, (x, y) in enumerate(pts):
            x0, y0 = pts[max(0, i - 1)]; x1, y1 = pts[min(len(pts) - 1, i + 1)]
            tx, ty = x1 - x0, y1 - y0
            length = math.hypot(tx, ty) or 1e-12
            sign = 1.0 if inward else -1.0
            inner.append((x - ty / length * thickness * sign, y + tx / length * thickness * sign))
    rows = []
    for outer_pt, inner_pt in zip(pts, inner):
        rows.append((bm.verts.new(plane.at(outer_pt[0], outer_pt[1], depth0)), bm.verts.new(plane.at(outer_pt[0], outer_pt[1], depth1)),
                     bm.verts.new(plane.at(inner_pt[0], inner_pt[1], depth1)), bm.verts.new(plane.at(inner_pt[0], inner_pt[1], depth0))))
    count = len(rows)
    for i in range(count if closed else count - 1):
        a, b = rows[i], rows[(i + 1) % count]
        for k in range(4):
            try:
                bm.faces.new((a[k], b[k], b[(k + 1) % 4], a[(k + 1) % 4]))
            except ValueError:
                pass
    if not closed:
        for row in (rows[0], rows[-1]):
            try:
                bm.faces.new(row)
            except ValueError:
                pass


def extrude_along(bm, path, section, up, cap=True, twist=None):
    """Sweep a closed 2D `section` [(side, up)] along a 3D polyline. `up` is the direction (a Vector, or
    a function of the index returning one) that the section's second axis follows as nearly as the path
    allows; the first axis is up × tangent."""
    points = [Vector(p) for p in path]
    count = len(points)
    rings = []
    for i, p in enumerate(points):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == count - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[i + 1] - points[i - 1]
        tangent.normalize()
        reference = Vector(up(i)) if callable(up) else Vector(up)
        side = reference.cross(tangent)
        if side.length < 1e-6:
            side = Vector((1, 0, 0)).cross(tangent)
        side.normalize()
        upward = tangent.cross(side).normalized()
        rings.append([p + side * a + upward * b for a, b in section])
    loft(bm, rings, close=True, cap_start=cap, cap_end=cap)
    for face in bm.faces:
        face.smooth = False


def strip(bm, edge_a, edge_b, offset):
    """A thin solid between two polylines of equal length (a spar web, a flange, a doubler): its faces
    are edge_a-edge_b and the same moved by `offset` (one Vector, or one per point)."""
    edge_a = [Vector(p) for p in edge_a]; edge_b = [Vector(p) for p in edge_b]
    offsets = [Vector(o) for o in offset] if isinstance(offset, (list, tuple)) and not isinstance(offset[0], (int, float)) else [Vector(offset)] * len(edge_a)
    rows = [(bm.verts.new(a), bm.verts.new(b), bm.verts.new(b + o), bm.verts.new(a + o)) for a, b, o in zip(edge_a, edge_b, offsets)]
    for first, second in zip(rows, rows[1:]):
        for k in range(4):
            try:
                bm.faces.new((first[k], second[k], second[(k + 1) % 4], first[(k + 1) % 4]))
            except ValueError:
                pass
    for row in (rows[0], rows[-1]):
        try:
            bm.faces.new(row)
        except ValueError:
            pass


def angle_section(leg_a, leg_b, thickness):
    """L section: one leg along +side, one along +up, corner at the origin."""
    t = thickness
    return [(0, 0), (leg_a, 0), (leg_a, t), (t, t), (t, leg_b), (0, leg_b)]


def hat_section(width, height, flange, thickness):
    """Hat (top-hat) stringer section sitting on the skin: flanges on the skin at up = 0, crown at up = -height
    (it hangs inward from the skin)."""
    w, h, f, t = width / 2, height, flange, thickness
    return [(-w - f, 0), (-w, 0), (-w, -h + t), (w, -h + t), (w, 0), (w + f, 0), (w + f, -t), (w + t, -t), (w + t, -h), (-w - t, -h), (-w - t, -t), (-w - f, -t)]


def channel_section(height, flange, thickness, centred=True):
    """C channel: web along `up`, flanges along +side."""
    h, f, t = height, flange, thickness
    y0 = -h / 2 if centred else 0.0
    return [(0, y0), (f, y0), (f, y0 + t), (t, y0 + t), (t, y0 + h - t), (f, y0 + h - t), (f, y0 + h), (0, y0 + h)]


def rect_section(width, height):
    w, h = width / 2, height / 2
    return [(-w, -h), (w, -h), (w, h), (-w, h)]


def polyline_tube(bm, points, radius, segs=8, cap=True):
    tube(bm, [Vector(p) for p in points], radius, segs=segs, cap=cap)


def cable(bm, points, radius=0.0016, segs=5):
    """A control cable through the given points (straight runs between pulleys)."""
    tube(bm, [Vector(p) for p in points], radius, segs=segs, cap=True)


def disc(bm, centre, axis, radius, thickness, segs=20, bore=0.0, rim=None):
    """A disc (pulley, washer, flange) centred on `centre` with its axle along `axis`. `rim` = (groove
    depth) makes a pulley groove round the edge."""
    axis = Vector(axis).normalized()
    helper = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    a = axis.cross(helper).normalized(); b = axis.cross(a).normalized()
    centre = Vector(centre)
    h = thickness / 2
    if rim:
        profile = [(bore, -h), (radius, -h), (radius - rim, -h * 0.25), (radius - rim, h * 0.25), (radius, h), (bore, h)]
    else:
        profile = [(bore, -h), (radius, -h), (radius, h), (bore, h)]
    rings = [[centre + (a * math.cos(2 * math.pi * i / segs) + b * math.sin(2 * math.pi * i / segs)) * r + axis * d for i in range(segs)]
             for r, d in profile if r > 1e-6]
    if bore > 1e-6:
        loft(bm, rings + [rings[0]], close=True)
    else:
        loft(bm, rings, close=True, cap_start=True, cap_end=True)


def rod(bm, a, b, radius, segs=10):
    tube(bm, [Vector(a), Vector(b)], radius, segs=segs, cap=True)


def rod_end(bm, a, b, radius, eye=0.008, segs=10):
    """Push-pull rod from a to b with a flattened eye at each end."""
    a, b = Vector(a), Vector(b)
    rod(bm, a, b, radius, segs)
    axis = (b - a).normalized()
    helper = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    side = axis.cross(helper).normalized()
    for end in (a, b):
        disc(bm, end, side, eye, radius * 1.2, segs=10, bore=eye * 0.4)


# ----------------------------------------------------------------------------- mechanisms

def bar(bm, a, b, width, thickness, up):
    """Rectangular bar from a to b: `thickness` along `up`, `width` across."""
    extrude_along(bm, [Vector(a), Vector(b)], rect_section(width, thickness), up)


def cable_run(corners, radius=0.022, steps=4):
    """A cable led round pulleys. `corners` are the points where the straight runs would meet (the
    first and last are the ends of the cable); `radius` is the bend radius of the cable's centre line
    at each corner (one value, or one per corner). Returns the path, with an arc at every corner, and
    for each corner (centre, axle direction, bend radius, index of the first point of the arc in the
    path, index of the last) of its pulley; where the cable hardly bends there is no pulley and the
    centre is None."""
    points = [Vector(p) for p in corners]
    path = [points[0]]
    pulleys = []
    for i in range(1, len(points) - 1):
        corner = points[i]
        u1 = (points[i - 1] - corner).normalized(); u2 = (points[i + 1] - corner).normalized()
        phi = math.acos(max(-1.0, min(1.0, u1.dot(u2))))          # angle between the two runs at the corner
        r = radius[i - 1] if isinstance(radius, (list, tuple)) else radius
        if phi > math.pi - 0.06 or phi < 0.05:
            path.append(corner)
            pulleys.append((None, None, 0.0, len(path) - 1, len(path) - 1))
            continue
        tangent = r / math.tan(phi / 2)
        tangent = min(tangent, 0.45 * (points[i - 1] - corner).length, 0.45 * (points[i + 1] - corner).length)
        r = tangent * math.tan(phi / 2)
        centre = corner + (u1 + u2).normalized() * (r / math.sin(phi / 2))
        a1 = corner + u1 * tangent - centre; a2 = corner + u2 * tangent - centre
        sweep = math.pi - phi
        first = len(path)
        for k in range(steps + 1):
            t = k / steps
            path.append(centre + (a1 * math.sin((1 - t) * sweep) + a2 * math.sin(t * sweep)) / math.sin(sweep))
        pulleys.append((centre, u1.cross(u2).normalized(), r, first, len(path) - 1))
    path.append(points[-1])
    return path, pulleys


def pulley(bm, centre, axis, bend_radius, cable_radius=0.0016, width=0.009, mount=None, reach=0.012):
    """Pulley that leads a cable round a bend of `bend_radius` (to the centre line of the cable). With
    `mount`, a direction toward the structure, it gets a bracket: two cheek plates and a foot."""
    centre = Vector(centre); axis = Vector(axis).normalized()
    groove = 0.003 + cable_radius
    rim = bend_radius - cable_radius + groove
    disc(bm, centre, axis, rim, width, segs=18, rim=groove)
    rod(bm, centre - axis * (width * 0.5 + 0.004), centre + axis * (width * 0.5 + 0.004), 0.003, segs=6)
    if mount is not None:
        m = Vector(mount); m = m - axis * m.dot(axis)
        if m.length > 1e-6:
            m.normalize()
            for sign in (-1, 1):
                offset = axis * (sign * (width * 0.5 + 0.002))
                bar(bm, centre + offset - m * 0.007, centre + offset + m * (rim + reach), 0.014, 0.0016, axis)
            foot = centre + m * (rim + reach)
            bar(bm, foot - axis * (width * 0.5 + 0.011), foot + axis * (width * 0.5 + 0.011), 0.02, 0.002, m)


def pipe(bm, corners, radius=0.0048, bend=0.02, segs=8):
    """A rigid pipe or a hose through the given corner points, bent to `bend` radius at each. Returns its path."""
    path, _pulleys = cable_run(corners, bend, steps=3)
    tube(bm, path, radius, segs=segs, cap=True)
    return path


def union(bm, point, direction, pipe_radius=0.0048):
    """The nut of a pipe fitting at the end of a pipe."""
    direction = Vector(direction).normalized()
    hex_prism(bm, Vector(point) - direction * (pipe_radius * 1.4), direction, pipe_radius * 3.4, pipe_radius * 2.8)


def fairlead(bm, centre, direction, radius=0.007, length=0.012):
    """A guide block a cable passes straight through."""
    centre = Vector(centre); direction = Vector(direction).normalized()
    disc(bm, centre, direction, radius, length, segs=10, bore=0.0024)


def turnbuckle(bm, a, b, radius=0.0042):
    """Turnbuckle on a cable between a and b: a barrel with a threaded end fitting each side."""
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    rod(bm, a + axis * 0.016, b - axis * 0.016, radius, segs=8)
    rod(bm, a, a + axis * 0.02, radius * 0.5, segs=6)
    rod(bm, b - axis * 0.02, b, radius * 0.5, segs=6)


def plate_lever(bm, plane, arms, hub=0.014, eye=0.008, thickness=0.004, bore=0.0035):
    """A flat bellcrank or horn in `plane`, pivoting at the plane's origin: `arms` are the ends of its
    arms in the plane. The plate is the convex outline round the hub and the arm ends, drilled at each."""
    points = geom2d.circle(0.0, 0.0, hub, 12)
    for a, b in arms:
        points += geom2d.circle(a, b, eye, 10)
    outline = geom2d.convex_hull(points)
    holes = [geom2d.circle(0.0, 0.0, bore, 8)] + [geom2d.circle(a, b, bore * 0.8, 8) for a, b in arms]
    sheet(bm, plane, outline, thickness, holes, offset=-thickness / 2)


def chain(bm, path, axle, width=0.008, thickness=0.0045):
    """A roller chain drawn as a flat band along a path; `axle` is the direction of its sprockets' axles."""
    extrude_along(bm, [Vector(p) for p in path], rect_section(thickness, width), axle)


def arc(centre, a, b, start, end, steps=8):
    """Points of an arc about `centre` in the plane of the unit vectors a and b, from angle start to end."""
    centre = Vector(centre)
    return [centre + a * math.cos(start + (end - start) * i / steps) + b * math.sin(start + (end - start) * i / steps) for i in range(steps + 1)]


# ----------------------------------------------------------------------------- hardware

def dome(bm, base, normal, radius, height, sides=6, rings=1):
    """A low dome on a surface: rivet head, screw head. `rings` = 0 gives a plain pyramid (cheapest)."""
    normal = Vector(normal).normalized()
    helper = Vector((0, 0, 1)) if abs(normal.z) < 0.9 else Vector((1, 0, 0))
    a = normal.cross(helper).normalized(); b = normal.cross(a).normalized()
    base = Vector(base)
    levels = [(1.0, 0.0)] + [(math.cos(math.pi / 2 * k / (rings + 1)), math.sin(math.pi / 2 * k / (rings + 1))) for k in range(1, rings + 1)]
    loops = [[bm.verts.new(base + (a * math.cos(2 * math.pi * i / sides) + b * math.sin(2 * math.pi * i / sides)) * radius * r + normal * height * h)
              for i in range(sides)] for r, h in levels]
    apex = bm.verts.new(base + normal * height)
    for lower, upper in zip(loops, loops[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    top = loops[-1]
    for i in range(sides):
        bm.faces.new((top[i], top[(i + 1) % sides], apex))


def hex_prism(bm, base, axis, across_flats, height):
    axis = Vector(axis).normalized()
    helper = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    a = axis.cross(helper).normalized(); b = axis.cross(a).normalized()
    base = Vector(base)
    r = across_flats / 2 / math.cos(math.pi / 6)
    ring0 = [base + (a * math.cos(math.pi / 3 * i) + b * math.sin(math.pi / 3 * i)) * r for i in range(6)]
    ring1 = [p + axis * height for p in ring0]
    loft(bm, [ring0, ring1], close=True, cap_start=True, cap_end=True)


def bolt(bm, head_seat, axis, diameter, length, head=True, nut=True, grip=None):
    """Hex bolt: `head_seat` is the point under the head, `axis` points along the shank. With `nut`, a nut
    and washer sit at `grip` (default: length less 1.3 diameters) from the head."""
    head_seat = Vector(head_seat); axis = Vector(axis).normalized()
    rod(bm, head_seat, head_seat + axis * length, diameter / 2, segs=8)
    if head:
        hex_prism(bm, head_seat - axis * diameter * 0.65, axis, diameter * 1.6, diameter * 0.65)
    if nut:
        grip = length - diameter * 1.3 if grip is None else grip
        disc(bm, head_seat + axis * (grip + diameter * 0.06), axis, diameter * 0.95, diameter * 0.12, segs=12)
        hex_prism(bm, head_seat + axis * (grip + diameter * 0.12), axis, diameter * 1.6, diameter * 0.8)


def screw(bm, seat, normal, diameter=0.0048, sides=8):
    """Pan-head screw seen from outside: a low round head."""
    dome(bm, seat, normal, diameter * 0.95, diameter * 0.55, sides=sides, rings=1)


def flat_faces(bm):
    for face in bm.faces:
        face.smooth = False


# ----------------------------------------------------------------------------- parts

def part(ctx, name, bm, group, system, label_en, label_ar, mat, detail=1, status="estimated", pivot=None, smooth=False,
         x_axis=None, z_axis=None, parent=None, **tags):
    """Turn a mesh into a part: an object in the model's collection, parented to its assembly and tagged
    with system, bilingual label, status, detail level and any further tags (ref, note, hinge_axis, ...)."""
    if pivot is None:
        total = Vector((0, 0, 0)); count = 0
        for vert in bm.verts:
            total += vert.co; count += 1
        pivot = total / max(1, count)
    material = ctx.mats[mat] if isinstance(mat, str) else mat
    ob = obj_from_bm(name, bm, ctx.col, pivot=pivot, smooth=smooth, mat=material, x_axis=x_axis, z_axis=z_axis)
    target = parent if parent is not None else ctx.groups[group]
    parent_keep(ob, target)
    ctx.tag(ob, system, label_en, label_ar, status=status, detail=detail, **tags)
    return ob
