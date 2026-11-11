"""Shade baked into the model: how much of the sky each point of the cabin and of the outside can see.

A web viewer lights every surface as if nothing stood round it, so a cabin looks flat: the footwells are as
bright as the seats. Here each vertex of the basic model gets a value, 1 where it is open to its surroundings
and lower in corners, under the panel and between the seats. It travels in the exported model as a vertex
colour, which the viewer multiplies into the surface colour. The editable scene and the renders, which work
out light properly, do not use it.

Only the parts one looks at from outside and from the seats are shaded, against each other: the systems and what
lies under the skin are left alone, so that a part shown on its own is not dark from a skin that is not there.
"""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

NAME = "ao"
# What one looks at from outside and from the seats. The systems (fuel, electrical, controls, engine) are left
# alone: they are shown through a ghosted skin or with the cowl off, and must not be dark from what hid them.
SHADED = {"AIRFRAME", "WING_L", "WING_R", "EMPENNAGE", "GEAR", "POWERPLANT", "INTERIOR", "PANEL"}


def _directions(n):
    """n directions over the hemisphere about +z, more of them near the pole (a cosine-weighted set, fixed)."""
    out = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        r = math.sqrt((i + 0.5) / n); phi = i * golden
        out.append((r * math.cos(phi), r * math.sin(phi), math.sqrt(max(0.0, 1 - r * r))))
    return out


def shaded(ob):
    """Whether a part takes baked shade (and casts it)."""
    if ob.type != "MESH" or ob.hide_get() or ob.get("detail", 0) > 0:
        return False
    if ob.get("kind") in ("glass", "marking") or ob.get("system") not in SHADED:
        return False
    mats = [m.name for m in ob.data.materials if m]
    return not any(n.startswith(("glass", "instrument_glass", "lens_", "panel_placards", "instrument_dials_alpha")) for n in mats)


def bake(objects, samples=14, reach=0.55, strength=0.92, floor=0.22):
    """Give each shaded object the colour attribute `ao`. Returns the number of vertices shaded."""
    deps = bpy.context.evaluated_depsgraph_get()
    objects = [ob for ob in objects if shaded(ob)]
    verts, polys, own = [], [], {}
    for ob in objects:
        ev = ob.evaluated_get(deps); me = ev.to_mesh(); M = ob.matrix_world
        base = len(verts)
        pts = [M @ v.co for v in me.vertices]
        faces = [tuple(base + i for i in p.vertices) for p in me.polygons]
        verts.extend(pts); polys.extend(faces)
        own[ob.name] = BVHTree.FromPolygons(pts, [tuple(i - base for i in f) for f in faces]) if faces else None
        ev.to_mesh_clear()
    scene = BVHTree.FromPolygons(verts, polys)
    dirs = _directions(samples)
    count = 0
    for ob in objects:
        me = ob.data
        attr = me.color_attributes.get(NAME) or me.color_attributes.new(NAME, "FLOAT_COLOR", "POINT")
        M = ob.matrix_world; N = M.to_3x3().inverted_safe().transposed()
        tree = own[ob.name]
        darken = me.attributes.get("darken")            # shade a builder asked for at a vertex: the seams of pleated upholstery
        for v in me.vertices:
            p = M @ v.co
            n = (N @ v.normal)
            if n.length_squared < 1e-12:
                attr.data[v.index].color = (1, 1, 1, 1); continue
            n.normalize()
            # The modifiers move the surface: stand on the finished surface nearest this vertex. Where that is the rim
            # of an opening (the vertex lay in a window that was cut out), keep the vertex's own direction: tilted
            # into the opening, the rays would look into the cabin and bring its shade out onto the skin.
            start = p + n * 0.006
            if tree is not None:
                loc, nrm, _i, dist = tree.find_nearest(p)
                if loc is not None and dist < 0.05:
                    if nrm.dot(n) < 0:
                        nrm = -nrm
                    if nrm.dot(n) > 0.5:
                        n = (nrm * 0.6 + n * 0.4).normalized()
                    start = loc + n * 0.006
            # inside a skin with a thickness (its own, or a door's that fills the opening this vertex lay in): step out
            # through the outer face
            for _ in range(3):
                ahead = scene.ray_cast(start, n, 0.04)
                if ahead[0] is None or ahead[1].dot(n) <= 0:
                    break
                start = ahead[0] + n * 0.006
            t = n.orthogonal().normalized(); b = n.cross(t)
            blocked = 0.0
            for dx, dy, dz in dirs:
                hit = scene.ray_cast(start, t * dx + b * dy + n * dz, reach)
                if hit[0] is not None:
                    blocked += 1.0 - hit[3] / reach          # what is close shades more
            a = max(floor, 1.0 - strength * blocked / samples)
            if darken is not None:
                a *= 1.0 - darken.data[v.index].value
            attr.data[v.index].color = (a, a, a, 1.0)
            count += 1
        me.color_attributes.active_color = attr
        me.color_attributes.render_color_index = list(me.color_attributes).index(attr)
    return count
