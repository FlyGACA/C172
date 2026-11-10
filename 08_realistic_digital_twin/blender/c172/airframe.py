"""Exterior airframe: fuselage (with window/door cut-outs), wings, control surfaces,
empennage, struts and exterior details. All dimensions see units.py for status."""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

from . import units as U
from .units import fs, bl, wl, IN
from .shapes import (parent_keep, new_bm, loft, extrude_profile, revolve, tube, cylinder, box, bezier, obj_from_bm, empty,
                     add_subsurf, add_boolean, add_solidify, add_edge_split, add_bevel, naca4, airfoil_interp,
                     split_airfoil, superellipse, rounded_rect, ellipse, resample_loop, interp_table, smoothstep)
from .profiles import interp_pchip, interp_linear

K_RING = 40          # points around fuselage sections
K_WING = 72          # points around wing box sections
K_CTRL = 48          # points around control-surface sections

# Fuselage sections, build frame: FS, half width, WL of the bottom, WL of the top, WL of the widest
# point (all inches), then the superellipse exponents of the upper and lower half.
# Status: estimated. Sources, laid under the model (docs/05_shape_reference.md):
#   belly and cowl deck   photo-profile, confirmed by the 172S side view (within 0.3 in over FS 0-240)
#   windshield, roof slope, tailcone top, tail end   172S side view
#   widths                172S top view (20.3 in at the firewall, 21.6 in at the doors, then a straight
#                         taper of 0.119 in per inch from FS 94 to the tail); POH Fig 6-4 agrees at FS 142
#   cabin roof            the upper surface of the wing root, which the cabin top is flush with
# The cabin is slab-sided with a flat belly and tight lower corners; the tailcone is widest near the
# top and narrows toward a rounded keel. The fuselage ends at the bulkhead that carries the rudder.
_FUS_IN = [
    (0.0,   20.30, 19.80, 57.80, 41.0, 2.6, 3.0),
    (4.0,   20.60, 19.40, 57.80, 40.6, 2.6, 3.2),
    (8.0,   20.75, 19.00, 57.80, 40.2, 2.6, 3.4),
    (10.3,  20.80, 18.75, 57.85, 40.0, 2.6, 3.5),     # foot of the windshield
    (13.0,  21.00, 18.60, 61.60, 40.0, 2.5, 3.6),
    (16.0,  21.20, 18.30, 64.40, 40.0, 2.8, 3.8),
    (19.7,  21.40, 17.95, 67.00, 40.0, 3.2, 4.0),
    (22.5,  21.50, 17.75, 68.60, 40.0, 3.6, 4.0),
    (25.5,  21.60, 17.55, 69.90, 40.0, 4.2, 4.0),
    (28.0,  21.60, 17.35, 70.90, 40.0, 5.0, 4.0),
    (31.0,  21.60, 17.15, 72.20, 40.5, 7.0, 4.0),     # top of the windshield, just behind the wing leading edge
    (34.0,  21.60, 16.95, 72.60, 41.5, 10.0, 4.0),
    (37.0,  21.60, 16.90, 72.95, 42.0, 14.0, 4.0),
    (43.0,  21.60, 16.90, 73.45, 42.0, 14.0, 4.0),
    (49.0,  21.60, 16.90, 73.30, 42.0, 14.0, 4.0),
    (55.5,  21.60, 16.95, 72.80, 42.0, 14.0, 4.0),
    (62.0,  21.60, 17.05, 71.90, 42.0, 14.0, 4.0),
    (68.5,  21.35, 17.40, 70.85, 42.0, 14.0, 4.0),
    (75.0,  21.10, 17.75, 69.60, 42.0, 12.0, 4.0),
    (81.0,  20.75, 18.15, 68.25, 42.0, 10.0, 3.9),
    (87.5,  20.25, 18.55, 66.60, 42.0, 8.0, 3.7),
    (93.8,  19.50, 19.00, 64.60, 42.0, 5.5, 3.5),     # wing trailing edge: the rear window slopes down from here ...
    (97.0,  19.10, 19.20, 62.60, 41.5, 5.0, 3.4),
    (101.0, 18.60, 19.50, 60.50, 41.0, 4.5, 3.3),
    (105.0, 18.10, 19.75, 58.40, 40.0, 4.0, 3.2),
    (109.0, 17.65, 20.00, 56.20, 39.0, 3.6, 3.0),
    (112.5, 17.25, 20.20, 54.40, 38.0, 3.3, 2.9),
    (115.5, 16.90, 20.35, 52.80, 37.5, 3.0, 2.8),     # ... to the top of the tailcone
    (120.0, 16.35, 20.70, 52.00, 38.2, 3.0, 2.5),
    (130.0, 15.15, 21.30, 51.00, 39.0, 3.0, 2.1),
    (140.0, 13.95, 21.90, 50.10, 39.5, 3.0, 1.9),
    (150.0, 12.80, 22.60, 49.30, 39.8, 3.0, 1.8),
    (165.0, 11.00, 23.45, 47.85, 39.6, 3.0, 1.75),
    (180.0, 9.20,  24.40, 46.60, 39.5, 3.0, 1.7),
    (200.0, 6.80,  25.70, 44.60, 38.8, 3.0, 1.7),
    (215.0, 5.05,  26.65, 43.10, 38.0, 3.0, 1.7),
    (225.0, 3.85,  27.20, 41.60, 37.0, 2.8, 1.8),
    (231.5, 3.10,  27.30, 40.60, 36.0, 2.6, 2.0),
]
# FS(in) -> half width, z bottom, z top, z of the widest point (m, build frame), n_top, n_bottom
FUS_TABLE = [(s, w * IN, wl(zb), wl(zt), wl(zc), nt, nb) for s, w, zb, zt, zc, nt, nb in _FUS_IN]
FUS_STATIONS = [0, 3, 6, 10.3, 12.5, 15, 17.5, 20, 22.5, 25.5, 28, 31, 34, 37, 43, 49, 55.5, 62, 68.5, 75, 81, 87.5,
                93.8, 96, 99, 102, 105, 108, 111, 113.5, 115.5, 117.5, 121, 127, 135, 145, 160, 180, 200, 215, 225, 231.5]
FUS_END_FS = FUS_STATIONS[-1]          # the bulkhead that carries the rudder; nothing of the fuselage lies aft of it
FUS_UV_END_FS = 283                    # texture v = 1 (kept from the first layout so the livery atlas stays valid)

def fus_ring(s, k=K_RING):
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    return [Vector((x, fs(s), z)) for x, z in superellipse(w, zc - zb, zt - zc, zc, nt, nb, k)]

def fus_top_z(s):
    return interp_pchip(FUS_TABLE, s)[2]

def fus_half_width(s):
    return interp_pchip(FUS_TABLE, s)[0]

def fus_half_width_at(s, z):
    """Half width of the skin at station s (in) and height z (m); 0 above or below the section."""
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    if not zb < z < zt:
        return 0.0
    t, n = ((z - zc) / (zt - zc), nt) if z >= zc else ((zc - z) / (zc - zb), nb)
    return w * (1 - t ** n) ** (1 / n)

def fus_surface_z(s, x, top=False):
    """Skin height at station s (in) and lateral x (m): bottom of the section, or top."""
    w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
    t = min(1.0, abs(x) / w)
    if top:
        return zc + (zt - zc) * (1 - t ** nt) ** (1 / nt)
    return zc - (zc - zb) * (1 - t ** nb) ** (1 / nb)

# ----------------------------------------------------------------------------- cutters

def _cutter(ctx, name, pts2d, axis_u, axis_v, origin, depth_axis, d0, d1):
    bm = new_bm()
    extrude_profile(bm, pts2d, Vector(axis_u), Vector(axis_v), origin, Vector(depth_axis), d0, d1, smooth_sides=False)
    ob = obj_from_bm("_cut_" + name, bm, ctx.cutters, smooth=False)
    ob.hide_render = True
    ob.display_type = "WIRE"
    return ob

def _side_polygon(pts_fs_z):
    """(FS in, z m) -> (y, z) tuples."""
    return [(fs(s), z) for s, z in pts_fs_z]

def _round_corners(poly, r=0.03, n=4):
    """Round every corner of a closed polygon (simple arc insertion). r: one radius, or one per corner."""
    out = []
    m = len(poly)
    radii = list(r) if isinstance(r, (list, tuple)) else [r] * m
    for i in range(m):
        p0 = Vector(poly[i - 1]); p1 = Vector(poly[i]); p2 = Vector(poly[(i + 1) % m])
        d0 = (p0 - p1).normalized(); d2 = (p2 - p1).normalized()
        rr = min(radii[i], (p0 - p1).length * 0.45, (p2 - p1).length * 0.45)
        a = p1 + d0 * rr; b = p1 + d2 * rr
        for j in range(n + 1):
            t = j / n
            q = a * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + b * t * t
            out.append((q.x, q.y))
    return out

def _inset(poly, d):
    """Move every edge of a convex polygon inward by d."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sign = 1.0 if area > 0 else -1.0                     # counter-clockwise: the interior is left of each edge
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        length = math.hypot(ex, ey)
        nx, ny = -ey / length * sign, ex / length * sign
        lines.append(((x0 + nx * d, y0 + ny * d), (ex, ey)))
    out = []
    for i in range(n):
        (p, e), (q, f) = lines[i - 1], lines[i]
        t = ((q[0] - p[0]) * f[1] - (q[1] - p[1]) * f[0]) / (e[0] * f[1] - e[1] * f[0])
        out.append((p[0] + e[0] * t, p[1] + e[1] * t))
    return out

# Glazing and door outlines, side elevation in (FS in, WL in), build frame. Status: estimated, read
# off the 172S side view; the sizes of the door openings agree with POH Fig 6-4 (cabin door 37 in wide
# at the sill and 32 in at the top, 40 in high in front and 41 in behind; baggage door 15¼ in wide,
# 22 in high in front and 21 in behind).
#   * The door stands behind the front door post, which leans back with the wing strut in front of it;
#     its rear edge is the rear door post.
#   * The sill of the door window drops toward the rear; the rear side window continues that line level.
#   * The rear window covers the sloping back of the cabin behind a post that leans forward.
#   * The baggage door is on the left side only, below the rear side window.
DOOR = [(30.9, 24.4), (67.9, 23.6), (70.4, 65.0), (38.4, 65.0)]
DOOR_RADII = [0.05, 0.12, 0.05, 0.04]
DOOR_WINDOW = [(37.1, 49.8), (68.3, 47.3), (69.3, 63.2), (39.8, 64.3)]
DOOR_WINDOW_RADII = [0.02, 0.055, 0.055, 0.02]
REAR_SIDE_WINDOW = [(71.9, 47.4), (99.6, 48.3), (100.3, 50.0), (94.6, 57.8), (72.2, 59.9)]
REAR_SIDE_WINDOW_RADII = [0.035, 0.03, 0.03, 0.05, 0.035]
# Rear window: everything of the sloping back that lies behind the post (first two points) and above
# the lower edge (third and fourth point). The remaining corners lie outside the hull.
REAR_WINDOW = [(94.5, 67.0), (97.2, 61.6), (105.5, 49.9), (115.8, 52.5), (117.0, 54.5)]
# Windshield: everything ahead of the front door post, above a lower edge that leaves the cowl deck at
# its foot (FS 10) and runs down and back to the post, and ahead of a top edge that reaches the roof at
# FS 33 on the centreline. The last two corners lie outside the hull.
WINDSHIELD = [(9.6, 57.2), (22.6, 50.3), (33.4, 51.6), (36.2, 66.5), (30.5, 76.0), (9.6, 76.0)]
BAGGAGE_DOOR = [(92.3, 22.9), (108.9, 22.9), (110.2, 44.3), (94.8, 45.5)]
DOOR_GAP = 0.004            # the doors are this much smaller than their openings all round (m)

def window_cutters(ctx):
    """Return dict of cutter objects for every glazed opening and the doors."""
    C = {}
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
    def side(points):
        return [(fs(s), wl(w)) for s, w in points]
    door = _round_corners(side(DOOR), r=DOOR_RADII)
    door_fit = _round_corners(_inset(side(DOOR), DOOR_GAP), r=[max(0.005, v - DOOR_GAP) for v in DOOR_RADII])
    door_win = _round_corners(side(DOOR_WINDOW), r=DOOR_WINDOW_RADII)
    rear_win = _round_corners(side(REAR_SIDE_WINDOW), r=REAR_SIDE_WINDOW_RADII)
    for name, sgn in (("L", 1), ("R", -1)):
        C["door_" + name] = _cutter(ctx, "door_" + name, door, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["door_fit_" + name] = _cutter(ctx, "door_fit_" + name, door_fit, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["door_win_" + name] = _cutter(ctx, "door_win_" + name, door_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
        C["rear_win_" + name] = _cutter(ctx, "rear_win_" + name, rear_win, Y, Z, (0, 0, 0), X, 0.25 * sgn, 1.0 * sgn)
    # baggage door: left side only (+x)
    C["baggage_L"] = _cutter(ctx, "baggage_L", _round_corners(side(BAGGAGE_DOOR), r=0.04), Y, Z, (0, 0, 0), X, 0.15, 1.0)
    C["baggage_fit_L"] = _cutter(ctx, "baggage_fit_L", _round_corners(_inset(side(BAGGAGE_DOOR), DOOR_GAP), r=0.04 - DOOR_GAP), Y, Z, (0, 0, 0), X, 0.15, 1.0)
    # windshield and rear window: side-profile prisms cut right across the fuselage
    C["windshield"] = _cutter(ctx, "windshield", _round_corners(side(WINDSHIELD), r=0.03), Y, Z, (0, 0, 0), X, -1.0, 1.0)
    C["rear_window"] = _cutter(ctx, "rear_window", _round_corners(side(REAR_WINDOW), r=0.012), Y, Z, (0, 0, 0), X, -1.0, 1.0)
    return C

# ----------------------------------------------------------------------------- fuselage

def build_fuselage(ctx):
    M = ctx.mats
    parent = ctx.groups["AIRFRAME"]
    y0, y1 = fs(0), fs(FUS_UV_END_FS)
    rings = [fus_ring(s) for s in FUS_STATIONS]
    uv_v = [(fs(s) - y0) / (y1 - y0) for s in FUS_STATIONS]
    cut = window_cutters(ctx)
    ctx.cutter_objects = cut

    def shell(name, thickness=0.014):
        """Closed loft -> subdivision -> thin skin. Booleans see a closed mesh as a solid, so
        the skin must be solidified BEFORE any cut, otherwise the cabin volume is solid."""
        bm = new_bm()
        loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v)
        # crease both end rings: without it the subdivision rounds the firewall end and opens a gap behind the cowl
        crease = bm.edges.layers.float.new("crease_edge")
        ends = (rings[0][0].y, rings[-1][0].y)
        for e in bm.edges:
            if any(all(abs(v.co.y - y) < 1e-6 for v in e.verts) for y in ends):
                e[crease] = 1.0
        ob = obj_from_bm(name, bm, ctx.col, mat=M["fuselage"])
        add_subsurf(ob, ctx.subsurf)
        add_solidify(ob, thickness)
        return ob

    def crisp(ob):
        """Hard shading along the cut edges of an opening (added after the booleans)."""
        add_edge_split(ob, 50)

    # main shell with every opening removed
    fus = shell("AIRFRAME.fuselage")
    parent_keep(fus, parent)
    for key in ("door_R", "door_L", "baggage_L", "rear_win_R", "rear_win_L", "windshield", "rear_window"):
        add_boolean(fus, cut[key], "DIFFERENCE", "cut_" + key)
    crisp(fus)
    ctx.tag(fus, "AIRFRAME", "Fuselage", "جسم الطائرة", status="estimated",
            note="Overall dimensions from POH Fig 1-1; outline and sections estimated from the manufacturer's three-views")

    # glazing: intersection of the same shell with the cutters
    def glass(name, key, parent_ob, label_en, label_ar):
        g = shell(name, thickness=0.005)
        add_boolean(g, cut[key], "INTERSECT", "glass")
        crisp(g)
        g.data.materials.clear(); g.data.materials.append(M["glass"])
        parent_keep(g, parent_ob)
        ctx.tag(g, "AIRFRAME", label_en, label_ar, status="estimated", kind="glass")
        return g

    glass("AIRFRAME.windshield", "windshield", fus, "Windshield (acrylic)", "الزجاج الأمامي")
    glass("AIRFRAME.rear_window", "rear_window", fus, "Rear window", "النافذة الخلفية")
    glass("AIRFRAME.window_rear_R", "rear_win_R", fus, "Right rear side window", "النافذة الجانبية الخلفية اليمنى")
    glass("AIRFRAME.window_rear_L", "rear_win_L", fus, "Left rear side window", "النافذة الجانبية الخلفية اليسرى")
    # (cutter names already follow +x = left)

    def on_skin(point, sgn, inset=0.01):
        station, water = point
        return Vector((sgn * (fus_half_width_at(station, wl(water)) - inset), fs(station), wl(water)))

    def hinged(name, fit_key, edge, sgn, window_key=None):
        """The part of the shell inside the cutter `fit_key`, as an object whose origin lies on the hinge
        line (the two side-elevation points of `edge`, on the skin) and whose local z axis runs along it."""
        ob = shell(name)
        add_boolean(ob, cut[fit_key], "INTERSECT", "door")
        if window_key:
            add_boolean(ob, cut[window_key], "DIFFERENCE", "win")
        crisp(ob)
        a, b_ = on_skin(edge[0], sgn), on_skin(edge[1], sgn)
        z = (b_ - a).normalized()
        x = Vector((1, 0, 0)); x = (x - z * x.dot(z)).normalized()
        y = z.cross(x)
        frame = Matrix((x, y, z)).transposed().to_4x4()
        frame.translation = a
        inverse = frame.inverted()
        for v in ob.data.vertices:
            v.co = inverse @ v.co
        ob.matrix_world = frame
        return ob

    # cabin doors: shell ∩ door cutter, minus the window; hinged on the front door post
    for side, sgn in (("L", 1), ("R", -1)):
        d = hinged(f"AIRFRAME.door_{side}", "door_fit_" + side, (DOOR[0], DOOR[3]), sgn, "door_win_" + side)
        parent_keep(d, parent)
        ctx.tag(d, "AIRFRAME", f"{'Left' if sgn > 0 else 'Right'} cabin door", "باب المقصورة " + ("الأيسر" if sgn > 0 else "الأيمن"),
                status="estimated", hinge_axis="z", hinge_sign=sgn, range_deg=[0, 65], animate="door",
                note="Opening 37 in wide at the sill, 32 in at the top, 40-41 in high (POH Fig 6-4); position from the 172S side view")
        glass(f"AIRFRAME.door_window_{side}", "door_win_" + side, d, f"{'Left' if sgn > 0 else 'Right'} door window", "نافذة الباب " + ("الأيسر" if sgn > 0 else "الأيمن"))
        # outside handle: a flush lever below the window, toward the rear of the door
        bm = new_bm()
        centre = on_skin((60.7, 45.2), sgn, inset=-0.006)
        box(bm, (0.012, 0.19, 0.024), center=centre)
        box(bm, (0.016, 0.045, 0.034), center=centre + Vector((0, -0.085, 0)))
        h = obj_from_bm(f"AIRFRAME.door_handle_{side}", bm, ctx.col, pivot=centre, mat=M["chrome"])
        parent_keep(h, d)
        ctx.tag(h, "AIRFRAME", "Door handle", "مقبض الباب", status="estimated")
    # baggage door (left side), hinged on its forward edge
    bd = hinged("AIRFRAME.baggage_door", "baggage_fit_L", (BAGGAGE_DOOR[0], BAGGAGE_DOOR[3]), 1)
    parent_keep(bd, parent)
    ctx.tag(bd, "AIRFRAME", "Baggage door (left side)", "باب الأمتعة (الجانب الأيسر)", status="poh", ref="p.6-8 (Fig 6-4), p.7-10",
            hinge_axis="z", hinge_sign=1, range_deg=[0, 100], animate="baggage_door",
            note="Opening 15¼ in wide, 22 in high in front and 21 in behind (POH Fig 6-4); position from the 172S side view")
    bm = new_bm()
    centre = on_skin((105.5, 31.2), 1, inset=-0.005)
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, 0.006), (0.0, 0.008)], axis="X", origin=centre, segs=16)
    box(bm, (0.01, 0.05, 0.014), center=centre + Vector((0.006, -0.02, 0)))
    latch = obj_from_bm("AIRFRAME.baggage_door_latch", bm, ctx.col, pivot=centre, mat=M["chrome"])
    parent_keep(latch, bd)
    ctx.tag(latch, "AIRFRAME", "Baggage door latch and lock", "مزلاج وقفل باب الأمتعة", status="estimated")
    return fus

# ----------------------------------------------------------------------------- wings

DIH = math.radians(U.ref("dihedral_deg"))
WASHOUT = math.radians(U.ref("washout_deg"))
INC_ROOT = math.radians(U.ref("incidence_root_deg") + U.FRL_PITCH_DEG)     # root incidence in the build frame
AF_ROOT = naca4("2412", 36)
AF_TIP = naca4("0012", 36)
# Planform and skin lines, estimated from the 172S top view (same wing): constant 64 in chord to BL 100,
# then a straight taper to 44.5 in at the tip rib (BL 208), 27 % of it on the leading edge. The fixed
# skin ends at 79 % chord over the flap; the visible chord of the aileron is a constant 9.8 in. Skin
# seams lie at 14.5 % chord (leading-edge skin on the front spar) and 64.5 % chord (rear spar).
FLAP_XC = 0.79
AIL_VISIBLE = 9.8 * IN
FRONT_SPAR_XC = 0.155
REAR_SPAR_XC = 0.645
ROOT_X = 0.0                 # span origin of the dihedral, the washout and the texture
WING_ROOT_X = 0.46           # inboard end of the wing skin, inside the cabin side (the cabin top is fuselage)
CABIN_SIDE_X = 0.545         # where the wing meets the cabin
# Wing strut, estimated from the 172S side and front views: from the fuselage frame at the foot of the
# front door post up to the front spar where the wing starts to taper (BL 100.5).
STRUT_FS = (28.2, 38.2)      # fuselage end, wing end
STRUT_FOOT_WL = 22.6
STRUT_TOP_X = 100.5 * IN
FLAP_SPAN = (0.56, 2.525)
AIL_SPAN = (2.555, 5.25)
TIP_START = U.TIP_RIB

def wing_chord(x):
    return U.ROOT_CHORD - U.TAPER_PER_M * max(0.0, abs(x) - U.TAPER_START)

def wing_le_y(x):
    """Leading edge (build-frame y): straight to BL 100, swept back outboard of it."""
    return U.WING_LE_Y + U.TAPER_LE_SHARE * (U.ROOT_CHORD - wing_chord(x))

def wing_le_z(x):
    return U.WING_Z + max(0.0, abs(x) - 0.5) * math.tan(DIH)

def _span_fraction(xabs):
    return min(1.0, max(0.0, (xabs - 0.5) / (U.SEMISPAN - 0.5)))

def wing_incidence(xabs):
    """Incidence in the build frame (radians): the published +1.5 deg root / -1.5 deg tip plus FRL_PITCH_DEG."""
    return INC_ROOT - WASHOUT * _span_fraction(xabs)

def ail_xc(x):
    return 1.0 - AIL_VISIBLE / wing_chord(x)

def wing_point(xabs, side, xc, yc):
    """World point of the wing at span |x|, chord fraction xc and height yc (fraction of the chord above the chord line)."""
    c = wing_chord(xabs); inc = wing_incidence(xabs)
    yy = xc * c; zz = yc * c
    return Vector((side * xabs, wing_le_y(xabs) + yy * math.cos(inc) + zz * math.sin(inc),
                   wing_le_z(xabs) - yy * math.sin(inc) + zz * math.cos(inc)))

def wing_airfoil(xabs):
    return airfoil_interp(AF_ROOT, AF_TIP, _span_fraction(xabs))

def airfoil_y(af, xc, upper):
    """Height (fraction of chord) of the upper or lower surface of a closed airfoil loop at chord fraction xc."""
    n = len(af)
    pts = af[: n // 2 + 1] if upper else [af[0]] + list(reversed(af[n // 2:]))
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        if (x0 - xc) * (x1 - xc) <= 0 and x0 != x1:
            return y0 + (y1 - y0) * (xc - x0) / (x1 - x0)
    return 0.0

def wing_surface_point(xabs, side, xc, upper=True, inset=0.0):
    """Point on the upper or lower skin at chord fraction xc; inset moves it into the wing (fraction of chord)."""
    y = airfoil_y(wing_airfoil(xabs), xc, upper)
    return wing_point(xabs, side, xc, y - inset if upper else y + inset)

def wing_section(xabs, side, cut=None, k=K_WING):
    """World-space ring for the wing at |x| = xabs. cut: None (full airfoil), ('box', xc) or ('surf', xc)."""
    af = wing_airfoil(xabs)
    if cut is None:
        prof = resample_loop(af, k)
    else:
        boxp, surfp = split_airfoil(af, cut[1])
        prof = resample_loop(boxp if cut[0] == "box" else surfp, k)
    return [wing_point(xabs, side, xc, yc) for xc, yc in prof]

def wing_hinge_point(xabs, side, xc):
    af = wing_airfoil(xabs)
    return wing_point(xabs, side, xc, 0.5 * (airfoil_y(af, xc, True) + airfoil_y(af, xc, False)))

def _stations(a, b, step):
    n = max(2, int(round((b - a) / step)) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def build_wing(ctx, side):
    M = ctx.mats
    name = "L" if side > 0 else "R"          # +x is the left wing
    grp = ctx.groups["WING_" + name]
    # ---- main wing box: sections through root → flap span → aileron span → tip rib
    rings = []
    xs = []
    def add(x, cut):
        rings.append(wing_section(x, side, cut)); xs.append(x)
    for x in _stations(WING_ROOT_X, FLAP_SPAN[0] - 0.01, 0.14): add(x, None)
    for x in _stations(FLAP_SPAN[0], FLAP_SPAN[1], 0.2): add(x, ("box", FLAP_XC))
    for x in _stations(AIL_SPAN[0], AIL_SPAN[1], 0.2): add(x, ("box", ail_xc(x)))
    for x in _stations(AIL_SPAN[1] + 0.012, TIP_START, 0.03): add(x, None)
    # tip cap: nearly square in plan with rounded corners, drooped slightly
    ring = wing_section(TIP_START, side, None)
    cy = sum(v.y for v in ring) / len(ring); cz = sum(v.z for v in ring) / len(ring)
    for i in range(1, 7):
        t = i / 6
        x = TIP_START + (U.SEMISPAN - TIP_START) * t
        sc = math.sqrt(max(1e-4, 1 - t * t))
        rings.append([Vector((side * x, cy + (v.y - cy) * (0.78 + 0.22 * sc), cz + (v.z - cz) * sc - 0.03 * t)) for v in ring])
        xs.append(x)
    uv_v = [(x - ROOT_X) / (U.SEMISPAN - ROOT_X) for x in xs]
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v, flip=(side < 0))
    wing = obj_from_bm(f"WING_{name}.wing", bm, ctx.col, pivot=(side * 0.5, U.WING_LE_Y, U.WING_Z), mat=M["wing"])
    parent_keep(wing, grp)
    ctx.tag(wing, "WING_" + name, f"{'Left' if side > 0 else 'Right'} wing", "الجناح " + ("الأيسر" if side > 0 else "الأيمن"),
            status="type_data", note="NACA 2412 root / 0012 tip, 1°44′ dihedral, 3° washout, 64 in root chord (type data); "
                                     "taper from BL 100 and the leading-edge sweep estimated from the manufacturer's three-view")
    # ---- flap and aileron
    def surface(nm, span, xc, label_en, label_ar, mat, rng):
        rr = []; xx = []
        for x in _stations(span[0] + 0.015, span[1] - 0.015, 0.2):
            rr.append(wing_section(x, side, ("surf", xc(x)), k=K_CTRL)); xx.append(x)
        h0 = wing_hinge_point(span[0] + 0.015, side, xc(span[0] + 0.015))
        h1 = wing_hinge_point(span[1] - 0.015, side, xc(span[1] - 0.015))
        bm = new_bm()
        loft(bm, rr, close=True, cap_start=True, cap_end=True, uv_v=[(x - span[0]) / (span[1] - span[0]) for x in xx], flip=(side < 0))
        axis = (h1 - h0); axis = axis if axis.x > 0 else -axis
        ob = obj_from_bm(nm, bm, ctx.col, pivot=h0 if side > 0 else h1, x_axis=axis, mat=mat)
        parent_keep(ob, grp)
        ctx.tag(ob, "WING_" + name, label_en, label_ar, status="estimated", hinge_axis="x", hinge_sign=-1, range_deg=rng, animate=nm.split(".")[1])
        return ob
    surface(f"WING_{name}.flap", FLAP_SPAN, lambda x: FLAP_XC, f"{'Left' if side > 0 else 'Right'} flap (0° to 40°)", "القلاب " + ("الأيسر" if side > 0 else "الأيمن"), M["control"], [0, 40])
    surface(f"WING_{name}.aileron", AIL_SPAN, ail_xc, f"{'Left' if side > 0 else 'Right'} aileron", "الجنيح " + ("الأيسر" if side > 0 else "الأيمن"), M["control"], [-20, 15])
    # ---- strut (streamlined section) from the fuselage frame under the front door post to the front spar
    foot_z = wl(STRUT_FOOT_WL)
    p0 = Vector((side * (fus_half_width_at(STRUT_FS[0], foot_z) - 0.015), fs(STRUT_FS[0]), foot_z))
    xc_top = (fs(STRUT_FS[1]) - wing_le_y(STRUT_TOP_X)) / wing_chord(STRUT_TOP_X)
    p1 = wing_surface_point(STRUT_TOP_X, side, xc_top, upper=False, inset=0.004)
    d = (p1 - p0).normalized()
    # section: ellipse 0.11 × 0.040, long axis along the flight direction
    sec = ellipse(0.020, 0.055, 20)
    ax_v = Vector((0, 1, 0))
    ax_v = (ax_v - d * ax_v.dot(d)).normalized()
    ax_u = ax_v.cross(d).normalized()
    bm = new_bm()
    ring0 = [p0 + ax_u * a + ax_v * b for a, b in sec]
    ring1 = [p1 + ax_u * a + ax_v * b for a, b in sec]
    # end fairings: slightly larger sections near the ends
    ring0b = [p0 + d * 0.12 + ax_u * a * 1.6 + ax_v * b * 1.25 for a, b in sec]
    ring1b = [p1 - d * 0.12 + ax_u * a * 1.6 + ax_v * b * 1.25 for a, b in sec]
    loft(bm, [ring0, ring0b, ring1b, ring1], close=True, cap_start=True, cap_end=True)
    strut = obj_from_bm(f"WING_{name}.strut", bm, ctx.col, pivot=p0, mat=M["paint_white"])
    add_subsurf(strut, 1)
    parent_keep(strut, grp)
    ctx.tag(strut, "WING_" + name, "Wing strut", "دعامة الجناح", status="estimated",
            note="Ends placed from the manufacturer's side and front views: fuselage frame at the foot of the front door post, front spar at BL 100.5")
    # ---- wing root fairing: a band wrapped round the wing where it meets the cabin
    def band(x, grow):
        ring = wing_section(x, side, None, k=48)
        cy = sum(v.y for v in ring) / len(ring); cz = sum(v.z for v in ring) / len(ring)
        out = []
        for i, v in enumerate(ring):
            t = ring[(i + 1) % len(ring)] - ring[i - 1]
            n = Vector((0, t.z, -t.y))
            if n.length < 1e-9:
                n = Vector((0, v.y - cy, v.z - cz))
            n.normalize()
            if n.dot(Vector((0, v.y - cy, v.z - cz))) < 0:
                n = -n
            out.append(v + n * grow)
        return out
    rings = [band(CABIN_SIDE_X - 0.05, 0.010), band(CABIN_SIDE_X, 0.010), band(CABIN_SIDE_X + 0.03, 0.008), band(CABIN_SIDE_X + 0.055, 0.0005)]
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=False, cap_end=False, flip=(side < 0))
    fair = obj_from_bm(f"WING_{name}.root_fairing", bm, ctx.col, pivot=(side * 0.5, U.WING_LE_Y, U.WING_Z), mat=M["paint_white"])
    parent_keep(fair, grp)
    ctx.tag(fair, "WING_" + name, "Wing root fairing", "غطاء جذر الجناح الانسيابي", status="estimated")
    # ---- details: fuel cap, nav light, strobe, tie-down, pitot (left), stall vane (left), fuel vent (left)
    xcap = 34.5 * IN
    cap_top = wing_surface_point(xcap, side, 0.25, upper=True)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.055, 0.0), (0.055, 0.006), (0.02, 0.008), (0.0, 0.009)], axis="Z", origin=(cap_top.x, cap_top.y, cap_top.z - 0.002), segs=24)
    cap = obj_from_bm(f"WING_{name}.fuel_cap", bm, ctx.col, pivot=cap_top, mat=M["bare_alu"])
    parent_keep(cap, grp)
    ctx.tag(cap, "FUEL", f"{'Left' if side > 0 else 'Right'} fuel filler cap (21.5 gal tank)", "غطاء خزان الوقود " + ("الأيسر" if side > 0 else "الأيمن"), status="poh", ref="p.1-4, 7-28")
    # navigation light on the leading corner of the tip, strobe light behind it. The strobes are what
    # the 36 ft span of POH Fig 1-1 is measured over, so their lenses end exactly there.
    tip_mid = wing_point(TIP_START, side, 0.5, 0.0)
    nav_pos = wing_point(TIP_START + 0.06, side, 0.10, 0.0) + Vector((0, 0, -0.012))
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.03, 0.0), (0.028, 0.02), (0.012, 0.035), (0.0, 0.04)], axis="X", origin=(abs(nav_pos.x), nav_pos.y, nav_pos.z), segs=16)
    nav = obj_from_bm(f"WING_{name}.nav_light", bm, ctx.col, pivot=(abs(nav_pos.x), nav_pos.y, nav_pos.z), mat=M["nav_red" if side > 0 else "nav_green"])
    if side < 0:
        for v in nav.data.vertices: v.co.x = -v.co.x
        nav.data.flip_normals()
        nav.matrix_world.translation = nav_pos
    parent_keep(nav, grp)
    ctx.tag(nav, "ELECTRICAL", f"{'Red (left)' if side > 0 else 'Green (right)'} navigation light", "ضوء الملاحة " + ("الأحمر" if side > 0 else "الأخضر"), status="poh", ref="p.7-27")
    half_span_strobes = U.ref("wingspan_strobes_m") / 2
    strobe_pos = wing_point(TIP_START + 0.06, side, 0.34, 0.0) + Vector((0, 0, -0.012))
    reach = half_span_strobes - abs(strobe_pos.x)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, reach * 0.55), (0.011, reach * 0.9), (0.0, reach)], axis="X", origin=(abs(strobe_pos.x), strobe_pos.y, strobe_pos.z), segs=14)
    st = obj_from_bm(f"WING_{name}.strobe", bm, ctx.col, pivot=(abs(strobe_pos.x), strobe_pos.y, strobe_pos.z), mat=M["nav_white"])
    if side < 0:
        for v in st.data.vertices: v.co.x = -v.co.x
        st.data.flip_normals()
        st.matrix_world.translation = strobe_pos
    parent_keep(st, grp)
    ctx.tag(st, "ELECTRICAL", "Wingtip strobe light", "ضوء الوميض في طرف الجناح", status="poh", ref="p.1-2 (wing span shown with strobe lights installed), p.7-27")
    tie = wing_surface_point(STRUT_TOP_X + 0.10, side, xc_top + 0.03, upper=False)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.018, 0.0), (0.018, -0.02), (0.0, -0.02)], axis="Z", origin=(tie.x, tie.y, tie.z + 0.003), segs=12)
    tiedown = obj_from_bm(f"WING_{name}.tiedown", bm, ctx.col, pivot=tie, mat=M["steel"])
    parent_keep(tiedown, grp)
    ctx.tag(tiedown, "AIRFRAME", "Wing tie-down ring", "حلقة ربط الجناح", status="estimated")
    if side > 0:
        # pitot tube: L-shaped mast under the left wing ahead of the leading edge (POH p.7-31)
        px = 1.75
        le_y = wing_le_y(px)
        pz = wing_surface_point(px, side, 0.10, upper=False).z - 0.004
        # a short mast about 5 in below the wing with the tube pointing forward about 6 in (estimated)
        pts = [Vector((px, le_y + 0.16, pz)), Vector((px, le_y + 0.16, pz - 0.115)), Vector((px, le_y + 0.10, pz - 0.13)), Vector((px, le_y + 0.0, pz - 0.13))]
        bm = new_bm()
        tube(bm, bezier(pts[0], pts[1], pts[2], pts[3], 14), 0.011, segs=14)
        pit = obj_from_bm("PITOT_STATIC.pitot_tube", bm, ctx.col, pivot=pts[0], mat=M["bare_alu"])
        add_subsurf(pit, 1)
        parent_keep(pit, grp)
        ctx.tag(pit, "PITOT_STATIC", "Pitot tube (heated)", "أنبوب البيتو (مسخّن)", status="poh", ref="p.7-31")
        # stall warning opening in the leading edge
        sw_le = wing_point(1.05, side, 0.0, 0.0)
        bm = new_bm()
        box(bm, (0.012, 0.03, 0.045), center=(sw_le.x, sw_le.y + 0.004, sw_le.z + 0.006))
        sw = obj_from_bm("AIRFRAME.stall_warning", bm, ctx.col, pivot=sw_le, mat=M["black_plastic"])
        parent_keep(sw, grp)
        ctx.tag(sw, "AIRFRAME", "Stall warning horn inlet (reed type)", "فتحة إنذار الانهيار", status="poh", ref="p.7-11")
        # fuel vent below the left wing near the strut
        vent_top = wing_surface_point(2.2, side, 0.12, upper=False)
        bm = new_bm()
        tube(bm, [vent_top + Vector((0, 0, 0.004)), vent_top + Vector((0, 0, -0.12)), vent_top + Vector((0, -0.07, -0.13))], 0.006, segs=10)
        vent = obj_from_bm("FUEL.vent_line", bm, ctx.col, pivot=vent_top, mat=M["bare_alu"])
        parent_keep(vent, grp)
        ctx.tag(vent, "FUEL", "Fuel tank vent (left wing, interconnected)", "فتحة تهوية خزان الوقود", status="poh", ref="p.7-28")
    return wing

# ----------------------------------------------------------------------------- empennage
# Status: estimated, read off the 172S side and top views (same tail). Outlines are tabulated as
# (FS in, WL in) in the build frame; wl() gives the build-frame z.

AF_TAIL = naca4("0009", 32)
STAB_SEMISPAN = U.H_TAIL_SPAN / 2
STAB_Z = wl(36.9)
STAB_TE_FS = (253.0, 243.5)             # elevator trailing edge: root, tip (it sweeps forward 9.5 in)
STAB_CHORD = (49.5 * IN, 27.6 * IN)     # stabiliser + elevator chord: root, tip (the leading edge sweeps back 12 in)
ELEV_CHORD = (21.1 * IN, 11.5 * IN)     # elevator chord: root, tip (the hinge line is straight across)
STAB_END = STAB_SEMISPAN - 0.17         # the elevator horn wraps round the stabiliser tip beyond this
STAB_SPAR_XC = 0.14                     # skin seam on the front spar, fraction of the local chord
TRIM_TAB_SPAN = (12.5 * IN, 52.0 * IN)  # right elevator
TRIM_TAB_CHORD = (5.8 * IN, 4.0 * IN)   # inboard, outboard

def _span_t(xabs):
    return min(1.0, xabs / STAB_SEMISPAN)

def stab_te_y(xabs):
    return fs(STAB_TE_FS[0] + (STAB_TE_FS[1] - STAB_TE_FS[0]) * _span_t(xabs))

def stab_chord(xabs):
    return STAB_CHORD[0] + (STAB_CHORD[1] - STAB_CHORD[0]) * _span_t(xabs)

def elev_chord(xabs):
    """Elevator chord, with the V cut-out at the centre that lets the rudder swing."""
    full = ELEV_CHORD[0] + (ELEV_CHORD[1] - ELEV_CHORD[0]) * _span_t(xabs)
    return min(full, 0.15 + max(0.0, xabs - 0.02) * 3.2)

ELEV_HINGE_Y = fs(STAB_TE_FS[0]) - ELEV_CHORD[0]

def stab_section(xabs, side, kind, k):
    c = stab_chord(xabs)
    y_le = stab_te_y(xabs) - c
    if kind == "full":
        prof = resample_loop(AF_TAIL, k)
    else:
        boxp, surfp = split_airfoil(AF_TAIL, 1 - elev_chord(xabs) / c)
        prof = resample_loop(boxp if kind == "box" else surfp, k)
    return [Vector((side * xabs, y_le + x * c, STAB_Z + y * c)) for x, y in prof]

# Vertical tail, side elevation. Leading edge as WL -> FS: the dorsal fin starts as a point at the foot
# of the rear window (FS 130), its top edge climbs gently and then turns into the 45-degree leading edge
# of the fin. Rows below WL 51.6 follow the top of the tailcone, where the blade grows out of it.
FIN_LE = [(40.6, 231.5), (41.6, 225.0), (42.3, 220.0), (43.1, 215.0), (44.6, 200.0), (46.6, 180.0), (48.3, 160.0), (49.3, 150.0),
          (50.1, 140.0), (51.0, 130.2), (51.6, 130.0), (52.3, 140.0), (53.0, 150.0), (53.8, 160.0), (54.5, 170.0), (55.2, 180.0),
          (55.9, 190.0), (56.4, 200.0), (57.2, 205.0), (58.6, 210.0), (60.0, 213.2), (61.7, 215.2), (66.6, 220.2), (76.5, 230.2),
          (86.0, 239.85), (93.5, 247.5), (94.7, 249.3), (95.2, 251.0)]
TAIL_END_FS = U.ref("tail_end_fs_in")            # rear top corner of the rudder
FIN_TOP = ((251.0, 95.2), (TAIL_END_FS, 91.0))  # top edge: front corner, rear corner (highest at the front)
RUD_TE = ((255.6, 41.7), (TAIL_END_FS, 91.0))   # rudder trailing edge, raked 21 degrees above WL 41.7; vertical below it
RUD_FOOT = ((232.1, 28.3), (255.75, 33.3))      # lower edge of the rudder, continuing the underside of the tailcone
RUD_HINGE = ((229.4, 33.0), (265.5, 91.7))      # rudder hinge line (32 degrees: the rudder is 20 in wide at the foot, 8 in at the top)
FIN_VLE = ((215.2, 61.7), (249.3, 94.7))        # straight part of the fin leading edge (chord reference)
FIN_SPAR = ((209.75, 43.75), (245.2, 89.8))     # skin seam on the fin's front spar (for the structure)
FIN_BASE_WL = FIN_LE[0][0]
FIN_TIP_WL = FIN_TOP[0][1]
DORSAL_HALF_T = 0.011                            # the dorsal fin is a thin sheet-metal blade ...
DORSAL_ROOT = [(130.0, 0.0), (140.0, 0.016), (215.0, 0.045), (231.5, 0.030)]   # FS -> half width of its faired root (m)
DORSAL_ROOT_H = 4.5                              # ... flaring out over this height (in) above the tailcone

def _line(a, b, at, index):
    """Value of the other coordinate on the line a-b; index 0 = given FS, 1 = given WL."""
    other = 1 - index
    return a[other] + (b[other] - a[other]) * (at - a[index]) / (b[index] - a[index])

def fin_le_fs(w):
    return interp_pchip(FIN_LE, w)[0]

def fin_top_fs(w):
    """Station of the sloping top edge at water line w (only meaningful above the rear corner)."""
    return _line(FIN_TOP[0], FIN_TOP[1], w, 1)

def rudder_hinge_fs(w):
    return _line(RUD_HINGE[0], RUD_HINGE[1], w, 1)

def rudder_te_fs(w):
    if w >= FIN_TOP[1][1]:
        return fin_top_fs(w)
    if w >= RUD_TE[0][1]:
        return _line(RUD_TE[0], RUD_TE[1], w, 1)
    if w >= RUD_FOOT[1][1]:
        return RUD_TE[0][0]
    return _line(RUD_FOOT[0], RUD_FOOT[1], max(w, RUD_FOOT[0][1]), 1)

def tailcone_top_wl(station):
    return (fus_top_z(min(max(station, 0.0), FUS_END_FS)) - U.GROUND_Z) / IN

def fin_half_thickness(station, w):
    """Half thickness (m) of the vertical tail at (FS, WL): a symmetric section between the extended
    fin leading edge and the rudder trailing edge, the dorsal blade ahead of it, and a root fairing
    that flares out into the top of the tailcone."""
    le = fin_le_fs(w)
    nose = min(1.0, max(0.0, (station - le) / 4.0)) ** 0.5
    blade = DORSAL_HALF_T * nose
    height = w - tailcone_top_wl(station)
    root = interp_linear(DORSAL_ROOT, min(max(station, DORSAL_ROOT[0][0]), DORSAL_ROOT[-1][0]))[0]
    flare = root * nose * (1.0 if height <= 0 else max(0.0, 1 - height / DORSAL_ROOT_H) ** 2)
    v_le = _line(FIN_VLE[0], FIN_VLE[1], w, 1)
    te = max(rudder_te_fs(min(w, FIN_TOP[1][1])), v_le + 12.0)
    chord_m = (te - v_le) * IN
    u = (station - v_le) / (te - v_le)
    if u <= 0.0:
        return max(blade, flare)
    u = min(u, 1.0)
    thickness = min(0.09, 0.07 * chord_m)
    section = 5 * thickness * (0.2969 * math.sqrt(u) - 0.1260 * u - 0.3516 * u ** 2 + 0.2843 * u ** 3 - 0.1036 * u ** 4)
    return max(blade, section, flare)

def _fin_ring(w, n):
    """Fixed fin at water line w: from the hinge line forward along the left side to the leading
    edge and back along the right side (same order as naca4(), so the livery atlas still fits)."""
    le = fin_le_fs(w)
    aft = min(rudder_hinge_fs(w), fin_top_fs(w)) if w > FIN_TOP[1][1] else rudder_hinge_fs(w)
    aft = max(aft, le + 0.5)
    stations = [le + (aft - le) * (1 - j / n) ** 1.6 for j in range(n + 1)]        # hinge ... leading edge
    left = [Vector((fin_half_thickness(st, w), fs(st), wl(w))) for st in stations]
    right = [Vector((-fin_half_thickness(st, w), fs(st), wl(w))) for st in reversed(stations[:-1])]
    return left + right[:-1]

def _rudder_ring(w, n):
    """Rudder at water line w: trailing edge, left side forward to the rounded nose at the hinge, back."""
    hinge = max(rudder_hinge_fs(w), RUD_FOOT[0][0])       # below the fin the rudder starts behind the end of the tailcone
    te = max(rudder_te_fs(w), hinge + 0.6)
    nose_h = max(0.004, fin_half_thickness(hinge, w) * 0.92)
    def half(st):
        t = (st - hinge) / (te - hinge)
        return nose_h * (1 - t) + 0.0015 * t
    stations = [te - (te - hinge) * j / n for j in range(n + 1)]                   # trailing edge ... hinge
    left = [Vector((half(st), fs(st), wl(w))) for st in stations]
    nose = [Vector((nose_h * math.cos(a), fs(hinge) - nose_h * 0.9 * math.sin(a), wl(w))) for a in (math.radians(d) for d in (30, 60, 90, 120, 150))]
    right = [Vector((-half(st), fs(st), wl(w))) for st in reversed(stations)]
    return left + nose + right[:-1]

def build_empennage(ctx):
    M = ctx.mats
    grp = ctx.groups["EMPENNAGE"]
    # ---- horizontal stabiliser (one piece through the tailcone)
    stations = _stations(0.0, STAB_END, 0.15)
    right = [stab_section(x, 1, "box", K_WING) for x in stations]
    left = [stab_section(x, -1, "box", K_WING) for x in stations]
    rings = list(reversed(left)) + right[1:]
    def cap_rings(base_ring, side):
        out = []
        cy = sum(v.y for v in base_ring) / len(base_ring); cz = sum(v.z for v in base_ring) / len(base_ring)
        for i in range(1, 4):
            t = i / 3
            sc = math.sqrt(max(1e-4, 1 - t * t))
            out.append([Vector((v.x + side * 0.05 * t, cy + (v.y - cy) * (0.3 + 0.7 * sc), cz + (v.z - cz) * sc)) for v in base_ring])
        return out
    rings = list(reversed(cap_rings(left[-1], -1))) + rings + cap_rings(right[-1], 1)
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[i / (len(rings) - 1) for i in range(len(rings))])
    stab = obj_from_bm("EMPENNAGE.stabilizer", bm, ctx.col, pivot=(0, stab_te_y(0) - STAB_CHORD[0], STAB_Z), mat=M["stab"])
    parent_keep(stab, grp)
    ctx.tag(stab, "EMPENNAGE", "Horizontal stabilizer", "المثبت الأفقي", status="poh", ref="Fig 1-1 (span 11 ft 4 in)", note="Chords, sweep and position estimated from the manufacturer's three-view")
    # ---- elevator: one piece, horns wrap round the stabiliser tips, V cut-out at the centre for the rudder
    stations = [0.03, 0.07, 0.12, 0.20] + _stations(0.30, STAB_END - 0.01, 0.15)
    def elev_half(side):
        rr = [stab_section(x, side, "surf", K_CTRL) for x in stations]
        horn = [stab_section(x, side, "full", K_CTRL) for x in _stations(STAB_END + 0.012, STAB_SEMISPAN - 0.03, 0.05)]
        # rounded tip out to the full span (11 ft 4 in over the elevator horns)
        last = horn[-1]
        cy = sum(v.y for v in last) / len(last)
        for dx, scale in ((0.018, 0.82), (0.027, 0.55), (0.03, 0.25)):
            horn.append([Vector((v.x + side * dx, cy + (v.y - cy) * (0.5 + 0.5 * scale), STAB_Z + (v.z - STAB_Z) * scale)) for v in last])
        return rr + horn
    r = elev_half(1); l = elev_half(-1)
    rings = list(reversed(l)) + r
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=[i / (len(rings) - 1) for i in range(len(rings))])
    elev = obj_from_bm("EMPENNAGE.elevator", bm, ctx.col, pivot=(0, ELEV_HINGE_Y, STAB_Z), mat=M["control"])
    parent_keep(elev, grp)
    ctx.tag(elev, "EMPENNAGE", "Elevator (with balance horns)", "الرافع (مع أذرع الموازنة)", status="estimated", hinge_axis="x", hinge_sign=-1, range_deg=[-28, 23], animate="elevator", ref="p.2-x travel")
    # ---- trim tab on the right elevator (-x)
    def tab_chord(xabs):
        t = (xabs - TRIM_TAB_SPAN[0]) / (TRIM_TAB_SPAN[1] - TRIM_TAB_SPAN[0])
        return TRIM_TAB_CHORD[0] + (TRIM_TAB_CHORD[1] - TRIM_TAB_CHORD[0]) * t
    rr = []
    xs = _stations(-TRIM_TAB_SPAN[1], -TRIM_TAB_SPAN[0], 0.1)
    for x in xs:
        c = stab_chord(abs(x)); y_le = stab_te_y(abs(x)) - c
        boxp, surfp = split_airfoil(AF_TAIL, 1 - tab_chord(abs(x)) / c)
        prof = resample_loop(surfp, 32)
        # a hair proud of the elevator skin it is let into, so the two surfaces never coincide
        proud = lambda py: py * c * 1.12 + (0.0012 if py > 1e-6 else -0.0012 if py < -1e-6 else 0.0)
        rr.append([Vector((x, y_le + px * c, STAB_Z + proud(py))) for px, py in prof])
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True)
    tab_in = Vector((-TRIM_TAB_SPAN[0], stab_te_y(TRIM_TAB_SPAN[0]) - TRIM_TAB_CHORD[0], STAB_Z))
    tab_out = Vector((-TRIM_TAB_SPAN[1], stab_te_y(TRIM_TAB_SPAN[1]) - TRIM_TAB_CHORD[1], STAB_Z))
    tab = obj_from_bm("EMPENNAGE.trim_tab", bm, ctx.col, pivot=tab_in, x_axis=tab_in - tab_out, mat=M["control"])
    parent_keep(tab, elev)
    ctx.tag(tab, "EMPENNAGE", "Elevator trim tab (right side)", "لسان موازنة الرافع", status="poh", ref="p.7-6 (manual trim wheel)", hinge_axis="x", hinge_sign=-1, range_deg=[-25, 25], animate="trim_tab")
    # ---- vertical fin with dorsal fin: horizontal slices, closely spaced where the dorsal ramp is shallow
    levels = [FIN_BASE_WL, 41.6, 42.3, 43.1, 44.6, 46.6, 48.3, 49.3, 50.1, 51.0, 51.3, 51.6, 52.0, 52.3, 53.0, 53.8, 54.5, 55.2,
              55.9, 56.4, 57.2, 57.9, 58.6, 59.3, 60.0, 60.9, 61.7, 63.5, 66.6, 70.0, 73.5, 76.5, 80.0, 83.0, 86.0, 89.0, 91.0, 92.5,
              93.5, 94.2, 94.7, 95.0, 95.15]
    rings = [_fin_ring(w, 26) for w in levels]
    visible0 = 51.6
    uv_v = [max(0.0, (w - visible0) / (FIN_TIP_WL - visible0)) for w in levels]
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_v=uv_v)
    fin = obj_from_bm("EMPENNAGE.fin", bm, ctx.col, pivot=(0, fs(215), wl(55)), mat=M["fin"])
    parent_keep(fin, grp)
    ctx.tag(fin, "EMPENNAGE", "Vertical fin with dorsal fin", "المثبت الرأسي مع الزعنفة الظهرية", status="estimated",
            note="Outline from the manufacturer's side view; section thickness estimated")
    # ---- rudder: raked trailing edge, foot continuing the tailcone underside
    levels = [28.3, 28.8, 29.6, 30.8, 32.2, 33.3, 35.0, 37.5, 40.0, 41.7, 44.5, 48.0, 52.0, 56.0, 60.0, 64.0, 68.0, 72.0, 76.0,
              80.0, 84.0, 87.5, 90.0, 91.0, 91.6, 92.0, 92.25]
    rr = [_rudder_ring(w, 10) for w in levels]
    bm = new_bm()
    loft(bm, rr, close=True, cap_start=True, cap_end=True, uv_v=[(w - levels[0]) / (levels[-1] - levels[0]) for w in levels])
    h0 = Vector((0, fs(RUD_HINGE[0][0]), wl(RUD_HINGE[0][1]))); h1 = Vector((0, fs(RUD_HINGE[1][0]), wl(RUD_HINGE[1][1])))
    rud = obj_from_bm("EMPENNAGE.rudder", bm, ctx.col, pivot=h0, z_axis=(h1 - h0), mat=M["control"])
    parent_keep(rud, grp)
    ctx.tag(rud, "EMPENNAGE", "Rudder", "الدفة", status="estimated", hinge_axis="z", hinge_sign=1, range_deg=[-16, 16], animate="rudder",
            note="Outline and hinge line from the manufacturer's side view")
    # white tail light at the top rear corner of the rudder, beacon on the fin tip
    tl_pos = (0, fs(FIN_TOP[1][0] - 0.8), wl(FIN_TOP[1][1] - 0.4))
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.018, 0.02), (0.0, 0.03)], axis="Y", origin=tl_pos, segs=12)
    tl = obj_from_bm("ELECTRICAL.tail_nav_light", bm, ctx.col, pivot=tl_pos, mat=M["nav_white"])
    parent_keep(tl, rud)
    ctx.tag(tl, "ELECTRICAL", "Tail navigation light (white)", "ضوء الملاحة الخلفي", status="poh", ref="p.7-27")
    bc_fs = 253.2
    bc_pos = (0, fs(bc_fs), wl(_line(FIN_TOP[0], FIN_TOP[1], bc_fs, 0)) - 0.012)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.035, 0.0), (0.035, 0.015), (0.03, 0.04), (0.012, 0.06), (0.0, 0.065)], axis="Z", origin=bc_pos, segs=16)
    bc = obj_from_bm("ELECTRICAL.beacon", bm, ctx.col, pivot=bc_pos, mat=M["nav_red"])
    parent_keep(bc, grp)
    ctx.tag(bc, "ELECTRICAL", "Flashing beacon (fin tip)", "منارة الوميض (قمة المثبت)", status="poh", ref="p.7-27")
    # tail tie-down ring under the tailcone
    td_pos = (0, fs(229), fus_surface_z(229, 0.0) + 0.004)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.016, 0.0), (0.016, -0.025), (0.0, -0.025)], axis="Z", origin=td_pos, segs=12)
    td = obj_from_bm("AIRFRAME.tail_tiedown", bm, ctx.col, pivot=td_pos, mat=M["steel"])
    parent_keep(td, grp)
    ctx.tag(td, "AIRFRAME", "Tail tie-down ring", "حلقة ربط الذيل", status="estimated")
    return fin

# ----------------------------------------------------------------------------- fuselage-mounted details

FLOOR_Z = 0.93                 # centre plane of the cabin floor panel, 30 mm thick (m, build frame)
FLOOR_STEP_FS = (94.0, 97.0)   # behind the rear seat the floor steps up to the baggage floor ...
BAGGAGE_FLOOR_RISE = 0.045     # ... by this much (estimated: the belly rises aft, the baggage floor rides on it)

def floor_z(station):
    """Centre plane of the floor panel at a station (in)."""
    t = (station - FLOOR_STEP_FS[0]) / (FLOOR_STEP_FS[1] - FLOOR_STEP_FS[0])
    return FLOOR_Z + BAGGAGE_FLOOR_RISE * min(1.0, max(0.0, t))

def build_details(ctx):
    M = ctx.mats
    grp = ctx.groups["AIRFRAME"]
    # comm antenna: bent whip on the roof
    bm = new_bm()
    az = fus_top_z(70) - 0.01
    pts = bezier(Vector((0, fs(70), az)), Vector((0, fs(72), az + 0.30)), Vector((0, fs(80), az + 0.45)), Vector((0, fs(90), az + 0.55)), 10)
    tube(bm, pts, 0.009, segs=10, radius_end=0.003)
    ant = obj_from_bm("ELECTRICAL.comm_antenna", bm, ctx.col, pivot=(0, fs(70), az), mat=M["paint_white"])
    parent_keep(ant, grp)
    ctx.tag(ant, "ELECTRICAL", "COM antenna (bent whip)", "هوائي الاتصال", status="estimated")
    # ELT antenna aft
    bm = new_bm()
    elt_z = fus_surface_z(150, 0.12, top=True)
    tube(bm, [Vector((0.12, fs(150), elt_z)), Vector((0.12, fs(152), elt_z + 0.32))], 0.005, segs=8)
    elt = obj_from_bm("ELECTRICAL.elt_antenna", bm, ctx.col, pivot=(0.12, fs(150), elt_z), mat=M["paint_white"])
    parent_keep(elt, grp)
    ctx.tag(elt, "ELECTRICAL", "ELT antenna", "هوائي جهاز تحديد موقع الطوارئ", status="estimated")
    # ADF sense wire from the roof to the fin
    bm = new_bm()
    wire_z = fus_top_z(84) + 0.02
    tube(bm, [Vector((0, fs(84), wire_z)), Vector((0, fs(fin_le_fs(80.0) + 0.3), wl(80.0)))], 0.0025, segs=6)
    wire = obj_from_bm("ELECTRICAL.adf_sense_wire", bm, ctx.col, pivot=(0, fs(84), wire_z), mat=M["steel"], smooth=True)
    parent_keep(wire, grp)
    ctx.tag(wire, "ELECTRICAL", "ADF sense antenna wire", "سلك هوائي ADF", status="estimated")
    # static port (left side)
    bm = new_bm()
    # forward fuselage, left side (POH p.7-31); position from the manufacturer's side view
    sp_z = wl(40.4); sp_x = fus_half_width_at(11.9, sp_z)
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.004), (0.0, 0.004)], axis="X", origin=(sp_x - 0.002, fs(11.9), sp_z), segs=16)
    sp = obj_from_bm("PITOT_STATIC.static_port", bm, ctx.col, pivot=(sp_x, fs(11.9), sp_z), mat=M["bare_alu"])
    parent_keep(sp, grp)
    ctx.tag(sp, "PITOT_STATIC", "Static port (left fuselage)", "منفذ الضغط الساكن", status="poh", ref="p.7-31")
    # cabin air inlets: round openings in the leading edge of each wing root (ramp photograph)
    for side in (-1, 1):
        name = "L" if side > 0 else "R"
        vx = side * 0.70
        le = Vector((vx, U.WING_LE_Y, U.WING_Z + (abs(vx) - 0.5) * math.tan(DIH)))
        bm = new_bm()
        revolve(bm, [(0.0, -0.001), (0.018, -0.001), (0.018, 0.02), (0.0, 0.02)], axis="Y", origin=le, segs=20)
        v = obj_from_bm(f"AIRFRAME.cabin_vent_{name}", bm, ctx.col, pivot=le, mat=M["interior_dark"])
        parent_keep(v, ctx.groups["WING_" + name])
        ctx.tag(v, "AIRFRAME", "Cabin ventilation air inlet (wing root leading edge)", "فتحة تهوية المقصورة (مقدمة جذر الجناح)", status="estimated")
    # ---- cabin interior liner (dark) so windows show a cabin, not the outside through the shell
    y0, y1 = fs(2), fs(116)
    rings = []
    for s in [2, 6, 10.3, 13, 16, 20, 25, 31, 37, 45, 55, 62, 70, 78, 86, 93.8, 97, 101, 105, 109, 112.5, 116]:
        w, zb, zt, zc, nt, nb = interp_pchip(FUS_TABLE, s)
        rings.append([Vector((x, fs(s), z)) for x, z in superellipse(w - 0.03, zc - zb - 0.03, zt - zc - 0.03, zc, nt, nb, K_RING)])
    def liner_shell(name):
        bm = new_bm()
        loft(bm, rings, close=True, cap_start=True, cap_end=True, flip=True)
        ob = obj_from_bm(name, bm, ctx.col, mat=M["interior_tan"])
        add_subsurf(ob, max(1, ctx.subsurf - 1))
        add_solidify(ob, 0.008)
        return ob
    liner = liner_shell("INTERIOR.cabin_liner")
    # the liner needs the same openings as the shell, otherwise it blocks the windows
    for key, c in ctx.cutter_objects.items():
        if "_fit" not in key:
            add_boolean(liner, c, "DIFFERENCE", "cut_" + key)
    parent_keep(liner, ctx.groups["INTERIOR"])
    ctx.tag(liner, "INTERIOR", "Cabin interior liner", "بطانة المقصورة الداخلية", status="estimated")
    # door trim panels: the part of the liner inside each door opening, carried by the door, so the
    # inside of a door shows trim rather than the back of the painted skin
    for side in ("L", "R"):
        door = bpy.data.objects.get(f"AIRFRAME.door_{side}")
        panel = liner_shell(f"INTERIOR.door_panel_{side}")
        add_boolean(panel, ctx.cutter_objects["door_fit_" + side], "INTERSECT", "door")
        add_boolean(panel, ctx.cutter_objects["door_win_" + side], "DIFFERENCE", "win")
        parent_keep(panel, door)
        ctx.tag(panel, "INTERIOR", f"{'Left' if side == 'L' else 'Right'} door trim panel", "بطانة الباب " + ("الأيسر" if side == "L" else "الأيمن"), status="estimated")
    # cabin floor: a panel that narrows with the hull so its edges stay inside the skin; the baggage
    # floor behind the rear seat is higher, as the belly rises there (floor_z)
    floor_stations = [4, 12, 20, 30, 45, 60, 75, 88, FLOOR_STEP_FS[0], FLOOR_STEP_FS[1], 104, 112]
    bm = new_bm()
    rings = []
    for st in floor_stations:
        z = floor_z(st)
        half = max(0.12, fus_half_width_at(st, z - 0.015) - 0.03)
        rings.append([Vector((half, fs(st), z + 0.015)), Vector((-half, fs(st), z + 0.015)),
                      Vector((-half, fs(st), z - 0.015)), Vector((half, fs(st), z - 0.015))])
    loft(bm, rings, close=True, cap_start=True, cap_end=True)
    floor = obj_from_bm("INTERIOR.floor", bm, ctx.col, mat=M["carpet"], smooth=False)
    parent_keep(floor, ctx.groups["INTERIOR"])
    ctx.tag(floor, "INTERIOR", "Cabin floor", "أرضية المقصورة", status="estimated")
