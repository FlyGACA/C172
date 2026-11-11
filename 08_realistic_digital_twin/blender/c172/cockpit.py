"""1979 Cessna 172N cockpit: instrument panel, subpanel, controls, control wheels, pedals, seats, belts and interior trim.

The panel follows the handbook's own figure and description (POH Figure 7-2, p.7-6 and 7-7; text p.7-8 and 7-9): the
gyros one over the other in front of the pilot with the control column under them, the airspeed indicator and the
altimeter to their left and right, the tachometer under the turn coordinator, the omni course indicators and the
ADF bearing indicator between the flight group and the avionics stack; the engine instruments, the fuel quantity
indicators, the ammeter and the low-voltage light near the left edge; the avionics stacked about the centreline;
space for more instruments on the right. The subpanel under it carries the primer, the master, ignition and
avionics power switches, the circuit breakers and the electrical switches on the left, the engine controls in the
middle over the pedestal, and the flap switch, the cabin heat and air controls and the map compartment on the right.
Sizes and exact places are estimated; every control is its own object."""
import math
import bpy
from mathutils import Vector

from . import units as U
from .units import fs, wl
from .shapes import (parent_keep, new_bm, loft, revolve, tube, cylinder, box, bezier, obj_from_bm, add_subsurf,
                     add_bevel, add_boolean, extrude_profile, rounded_rect, ellipse)
from .dials import cell_uv, MISC, CELLS, RADIO_W, RADIO_ROWS, RADIO_KNOBS, radio_height, RECT_W, RECT_H, RECT_PIVOT, RECT_COVER, rect_radius
from .atlas import lettering_cells
from .airframe import fus_half_width_at, floor_z

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))

CABIN_LIFT = 0.10         # applied by build() to everything not fixed to the floor (estimated)
FLOOR_MOUNTED = ("INTERIOR.pedal_", "FUEL.selector_", "INTERIOR.baggage_bulkhead")
PANEL_HALF = 0.50         # half width of the panel plates (m)
FLOOR_TOP = 0.945         # top of the cabin floor panel (airframe.build_details)
PANEL_Y = fs(19)          # instrument panel face (aft side), facing the pilot (+y)
PANEL_T = 0.012           # thickness of the panel plate (detail/instruments.py builds the cases against its back)
PANEL_Z0, PANEL_Z1 = 1.335, 1.64      # the instrument panel: three rows of instruments (heights before CABIN_LIFT)
LOWER_Z0, LOWER_Z1 = 1.22, 1.335      # the subpanel under it
LOWER_FACE = 0.018        # the laminate of the subpanel stands this far aft of the face of the panel
D3 = 0.079; D2 = 0.057; D1 = 0.042    # 3⅛ in and 2¼ in instrument faces, and the small ones at the left edge
ROW1, ROW2, ROW3 = 1.590, 1.496, 1.402                              # the three rows of instruments
COL_ASI, COL_GYRO, COL_ALT, COL_NAV = 0.383, 0.288, 0.194, 0.100    # airspeed and turn; the gyros; altimeter and climb; the omni and ADF indicators
COL_EDGE, COL_RECT = 0.458, 0.4625                                  # the small instruments near the left edge of the panel
YOKE_X, YOKE_Z = COL_GYRO, ROW3       # the control columns come through the panel under the gyros (POH p.7-8)
STACK_X = -0.0425                     # middle of the avionics stack
STACK_TOP = 1.633
SUB_UPPER, SUB_LOWER = 1.311, 1.266   # the two rows of the subpanel
DIAL_DEPTH = 0.0085                   # the dials lie this far behind the face of the panel, each in its recess
RIM = 0.0070                          # width of the moulded rim round an instrument

# (name, cell of the dial atlas, x, z, diameter, pointers)
INSTRUMENTS = [
    ("ASI", "ASI", COL_ASI, ROW1, D3, ["ASI"]),
    ("AI", None, COL_GYRO, ROW1, D3, []),
    ("ALT", "ALT", COL_ALT, ROW1, D3, ["ALT_10000", "ALT_1000", "ALT_100"]),
    ("VOR1", "VOR", COL_NAV, ROW1, D3, []),
    ("TC", "TC", COL_ASI, ROW2, D3, ["TC"]),
    ("DG", None, COL_GYRO, ROW2, D3, []),
    ("VSI", "VSI", COL_ALT, ROW2, D3, ["VSI"]),
    ("VOR2", "VOR", COL_NAV, ROW2, D3, []),
    ("TACH", "TACH", COL_ASI, ROW3, D3, ["TACH"]),
    ("ADF", "ADF", COL_NAV, ROW3, D3, []),
    ("CLOCK", "CLOCK", COL_EDGE, 1.602, D1, ["CLOCK_H", "CLOCK_M"]),
    ("SUCTION", "SUCTION", COL_EDGE, 1.543, D1, ["SUCTION"]),
]
# the small rectangular indicators: (name, x, z, width of the bar on its left (+x) side, on its right side)
RECT_GAUGES = [
    ("FUEL_L", COL_RECT + 0.016, 1.481, 0.0025, 0.002), ("FUEL_R", COL_RECT - 0.016, 1.481, 0.0, 0.0025),
    ("OIL_T", COL_RECT + 0.016, 1.435, 0.0025, 0.002), ("OIL_P", COL_RECT - 0.016, 1.435, 0.0, 0.0025),
    ("AMMETER", COL_RECT, 1.389, 0.0025, 0.0025),
]
BLANKS = [(-0.200, ROW1), (-0.296, ROW1), (-0.200, ROW2)]      # space for additional instruments (POH Figure 7-2, item 19)
STACK = ["AUDIO", "MARKER", "COMNAV1", "COMNAV2", "ADF", "XPDR"]      # the avionics stack, top to bottom
INSTRUMENT_NAMES = {
    "ASI": ("Airspeed indicator", "مؤشر السرعة الجوية"), "AI": ("Attitude indicator", "مؤشر الوضع"), "ALT": ("Altimeter", "مقياس الارتفاع"),
    "TC": ("Turn coordinator", "منسق الانعطاف"), "DG": ("Directional indicator", "المؤشر الاتجاهي"), "VSI": ("Rate-of-climb indicator", "مؤشر معدل الصعود"),
    "TACH": ("Tachometer", "عداد دورات المحرك"), "VOR1": ("Omni course indicator 1", "مؤشر مسار أومني 1"), "VOR2": ("Omni course indicator 2", "مؤشر مسار أومني 2"),
    "ADF": ("ADF bearing indicator", "مؤشر اتجاه ADF"), "CLOCK": ("Clock", "الساعة"), "SUCTION": ("Suction gage", "مقياس التفريغ"),
    "FUEL_L": ("Left fuel quantity indicator", "مؤشر كمية الوقود الأيسر"), "FUEL_R": ("Right fuel quantity indicator", "مؤشر كمية الوقود الأيمن"),
    "OIL_T": ("Oil temperature gage", "مقياس حرارة الزيت"), "OIL_P": ("Oil pressure gage", "مقياس ضغط الزيت"), "AMMETER": ("Ammeter", "مقياس التيار"),
}

# What the pointers show in the saved scene: the engine stopped and the master switch off (the electric indicators
# rest at the foot of their scales). Readings by instrument, in its own units; the clock stands at ten past ten.
REST_READINGS = {"ASI": 0.0, "VSI": 0.0, "TACH": 0.0, "SUCTION": 0.0, "FUEL_L": 0.0, "FUEL_R": 0.0, "OIL_T": 50.0, "OIL_P": 0.0, "AMMETER": 0.0}
REST_ANGLES = {"CLOCK_H": 305.0, "CLOCK_M": 60.0}

def pose_pointers(objects, at_rest=True):
    """Turn the pointers to what they show on a parked aircraft (at_rest), or back to the zero of their dials.
    The editable scene is saved at rest, so that a render of the cockpit does not show a climb and a running
    engine; the web model is exported at zero, where the rig of the viewer takes the pointers over."""
    import json
    from .dials import DATA, value_to_angle
    with open(DATA, encoding="utf-8") as f:
        specs = json.load(f)["instruments"]
    for ob in objects:
        kind = ob.get("needle")
        if not kind:
            continue
        angle = 0.0
        if at_rest:
            angle = value_to_angle(specs[kind], REST_READINGS[kind]) if kind in REST_READINGS and kind in specs else REST_ANGLES.get(kind, 0.0)
        ob.rotation_euler = (0.0, -math.radians(angle), 0.0)          # clockwise as the pilot sees it

def stack_rows():
    """The radios of the stack: (region, height of the middle of its face, height of its face), top to bottom."""
    rows = []; top = STACK_TOP
    for region in STACK:
        h = radio_height(region)
        rows.append((region, top - h / 2, h)); top -= h + 0.0012
    return rows

def disc_face(bm, center, r, region, segs=40, y_offset=0.0, fill=1.0, rings=(0.72, 1.0)):
    """Flat disc facing +y, mapped to the circle inscribed in a square atlas cell (fill: how much of that circle
    the disc shows). Built in rings round a middle vertex, so that the baked shade can differ from rim to middle."""
    uv = bm.loops.layers.uv.active
    c = Vector(center) + Vector((0, y_offset, 0))
    u0, v0, u1, v1 = region
    def tex(p):
        d = p - c
        return (u0 + (u1 - u0) * (0.5 - 0.5 * fill * d.x / r), v0 + (v1 - v0) * (0.5 + 0.5 * fill * d.z / r))
    mid = bm.verts.new(c)
    loops = [[bm.verts.new(c + Vector((r * k * math.cos(2 * math.pi * i / segs), 0, r * k * math.sin(2 * math.pi * i / segs)))) for i in range(segs)] for k in rings]
    faces = []
    for i in range(segs):
        faces.append(bm.faces.new([mid, loops[0][(i + 1) % segs], loops[0][i]]))
    for a, b in zip(loops, loops[1:]):
        for i in range(segs):
            faces.append(bm.faces.new([a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]]))
    for f in faces:
        f.smooth = False
        for l in f.loops:
            l[uv].uv = tex(l.vert.co)
    return faces

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

def letter_quad(bm, word, center, height, axis="panel"):
    """A word of the lettering atlas as a small quad: on the panel (facing aft) or lying flat (read from the seats)."""
    uv = bm.loops.layers.uv.active
    (u0, v0, u1, v1), aspect = lettering_cells()[word]
    w = height * aspect
    c = Vector(center)
    if axis == "panel":
        pts = [(c + Vector((w / 2, 0, -height / 2)), (u0, v0)), (c + Vector((-w / 2, 0, -height / 2)), (u1, v0)),
               (c + Vector((-w / 2, 0, height / 2)), (u1, v1)), (c + Vector((w / 2, 0, height / 2)), (u0, v1))]
    else:      # flat, the top of the letters toward the nose (-y), reading from the pilot's left (+x) to the right
        pts = [(c + Vector((w / 2, height / 2, 0)), (u0, v0)), (c + Vector((-w / 2, height / 2, 0)), (u1, v0)),
               (c + Vector((-w / 2, -height / 2, 0)), (u1, v1)), (c + Vector((w / 2, -height / 2, 0)), (u0, v1))]
    verts = [bm.verts.new(p) for p, _ in pts]
    f = bm.faces.new(verts); f.smooth = False
    for l, (_, t) in zip(f.loops, pts):
        l[uv].uv = t
    return f

def pleated_insert(bm, corner, across, along, normal, width, length, pleats, rise=0.007):
    """A panel of pleated upholstery: rounded ribs side by side, stitched down between them, flat at its edges.
    corner: one corner; across, along, normal: unit vectors; the ribs run along `along`."""
    uv = bm.loops.layers.uv.active
    darken = bm.verts.layers.float.get("darken") or bm.verts.layers.float.new("darken")      # read by the baked shade (ao.py)
    cols = pleats * 6 + 1; rows = 6
    grid = []
    for j in range(rows):
        v = j / (rows - 1)
        edge_v = min(1.0, min(v, 1 - v) / 0.12)
        row = []
        for i in range(cols):
            u = i / (cols - 1)
            edge_u = min(1.0, min(u, 1 - u) / 0.06)
            rib = abs(math.sin(math.pi * u * pleats)) ** 0.55
            h = rise * (0.25 + 0.75 * rib) * edge_u * edge_v
            p = Vector(corner) + Vector(across) * (u * width) + Vector(along) * (v * length) + Vector(normal) * h
            vert = bm.verts.new(p)
            vert[darken] = 0.55 * (1 - rib) * edge_u * edge_v + 0.30 * (1 - edge_u * edge_v)      # the stitched lines between the ribs, and the tucked-in edge
            row.append((vert, (u * width, v * length)))
        grid.append(row)
    for j in range(rows - 1):
        for i in range(cols - 1):
            quad = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            f = bm.faces.new([q[0] for q in quad]); f.smooth = True
            for l, q in zip(f.loops, quad):
                l[uv].uv = q[1]
    bm.normal_update()
    # the faces must look along `normal`
    if bm.faces and sum((f.normal.dot(Vector(normal)) for f in bm.faces)) < 0:
        for f in bm.faces:
            f.normal_flip()

def needle(ctx, name, pivot, length, width, mat, label_en, label_ar, kind, tail=0.0, style="pointer", thickness=0.0007, hub=None):
    """A pointer: a flat blade that turns about `pivot`, its tip up at zero, a little proud of its dial.
    hub: (radius, material) of the cap over its pivot, for the top pointer of an instrument."""
    bm = new_bm()
    c = Vector(pivot); w = width
    if style == "spade":          # short and broad: the thousands of the altimeter
        pts = [(-w * 0.22, -tail), (w * 0.22, -tail), (w * 0.22, length * 0.42), (w * 0.5, length * 0.62), (0.0, length), (-w * 0.5, length * 0.62), (-w * 0.22, length * 0.42)]
    elif style == "marker":       # a thin stem with a triangle at the rim: the ten thousands of the altimeter
        pts = [(-w * 0.5, -tail), (w * 0.5, -tail), (w * 0.5, length * 0.86), (w * 2.4, length), (-w * 2.4, length), (-w * 0.5, length * 0.86)]
    else:
        pts = [(-w * 0.5, -tail), (w * 0.5, -tail), (w * 0.42, length * 0.62), (w * 0.10, length), (-w * 0.10, length), (-w * 0.42, length * 0.62)]
    extrude_profile(bm, pts, X, Z, c, Y, 0.0, thickness, smooth_sides=False)
    if hub:
        n0 = len(bm.faces)
        rh = hub[0]
        revolve(bm, [(rh, thickness), (rh, thickness + 0.0006), (rh * 0.62, thickness + 0.0015), (0.0, thickness + 0.0017)], axis="Y", origin=c, segs=14)
        mark(bm, n0, 1)
    ob = obj_from_bm(name, bm, ctx.col, pivot=c, mat=mat, smooth=False)
    if hub:
        ob.data.materials.append(hub[1])
    parent_keep(ob, ctx.groups["PANEL"])
    ctx.tag(ob, "PANEL", label_en, label_ar, status="poh", needle=kind, spin_axis="y", spin_sign=-1, animate="needle")
    ob["keep_faces"] = True; ob["no_shade"] = True
    return ob

def face_aft(ob, slot=None):
    """Make the flat faces of a part (those of material slot `slot`, or all of them) look aft, at the pilot. A flat
    sheet has no inside: recalculating the normals of a mesh cannot tell which way it should face."""
    turn = ob.matrix_world.to_3x3()
    for p in ob.data.polygons:
        if (slot is None or p.material_index == slot) and (turn @ p.normal).y < 0:
            p.flip()
    ob.data.update()
    return ob

def mark(bm, start, index):
    """Give the faces made since `start` the material slot `index`."""
    bm.faces.ensure_lookup_table()
    for f in bm.faces[start:]:
        f.material_index = index

def knob_profile(r, h, y0=0.0):
    """A turned knob: a short skirt, a straight grip, a rounded shoulder, a flat top."""
    return [(r * 0.94, y0), (r, y0 + 0.0012), (r, y0 + h * 0.58), (r * 0.92, y0 + h * 0.84), (r * 0.78, y0 + h), (0.0, y0 + h)]

def build_panel(ctx):
    M = ctx.mats
    grp = ctx.groups["PANEL"]
    dials = M["dials"]; misc = M["panel_misc"]
    LF = PANEL_Y + LOWER_FACE            # the face of the subpanel

    def make(name, bm, pivot, mat, en, ar, status="estimated", smooth=True, parent=None, system="PANEL", more=(), aft=False, **tags):
        """aft: the part is a flat sheet (True) or carries one in a material slot (its number): turn it to the pilot."""
        ob = obj_from_bm(name, bm, ctx.col, pivot=pivot, mat=mat, smooth=smooth)
        for extra in more:
            ob.data.materials.append(extra)
        if aft is not False:
            face_aft(ob, None if aft is True else aft)
        parent_keep(ob, parent or grp)
        ctx.tag(ob, system, en, ar, status=status, **tags)
        return ob

    # ---- the instrument panel: a black plate that follows the inside of the skin where the cabin narrows toward
    # the roof, with an opening for each instrument
    def plate_half(z):
        return min(PANEL_HALF, fus_half_width_at(19, z + CABIN_LIFT) - 0.034)
    heights = [PANEL_Z0 + (PANEL_Z1 - PANEL_Z0) * i / 6 for i in range(7)]
    outline = [(plate_half(z), z) for z in heights] + [(-plate_half(z), z) for z in reversed(heights)]
    bm = new_bm()
    extrude_profile(bm, outline, X, Z, (0, 0, 0), Y, PANEL_Y - PANEL_T, PANEL_Y, smooth_sides=False)
    panel = make("PANEL.upper_panel", bm, (0, PANEL_Y, PANEL_Z0), M["panel_grey"], "Instrument panel (flight instruments, engine instruments, avionics)",
                 "لوحة العدادات (عدادات الطيران وعدادات المحرك وأجهزة الملاحة والاتصال)", smooth=False, ref="p.7-6 (Fig 7-2), 7-8",
                 note="Arranged as the handbook's figure and description give it; sizes and exact places estimated")
    add_bevel(panel, 0.003, 2)
    cut = new_bm()
    for name, cell, x, z, dia, needles in INSTRUMENTS:
        cylinder(cut, dia / 2 + 0.0007, 0.06, axis="Y", origin=(x, PANEL_Y - 0.04, z), segs=40 if dia > D2 else 28)
    for name, x, z, bar_l, bar_r in RECT_GAUGES:
        box(cut, (RECT_W + 0.0010, 0.06, RECT_H + 0.0010), center=(x, PANEL_Y - 0.01, z))
    cutter = obj_from_bm("_cut_panel_openings", cut, ctx.cutters, smooth=False)
    add_boolean(panel, cutter, name="openings")

    # ---- the subpanel under it: wood-grain laminate
    bm = new_bm()
    box(bm, (2 * PANEL_HALF, PANEL_T + LOWER_FACE, LOWER_Z1 - LOWER_Z0), center=(0, PANEL_Y + (LOWER_FACE - PANEL_T) / 2, (LOWER_Z0 + LOWER_Z1) / 2))
    bm.normal_update()
    uv = bm.loops.layers.uv.active
    for f in bm.faces:
        aft = f.normal.y > 0.5
        for l in f.loops:
            p = l.vert.co
            l[uv].uv = ((p.x + PANEL_HALF) / (2 * PANEL_HALF), (p.z - LOWER_Z0) / (LOWER_Z1 - LOWER_Z0)) if aft else (0.5 + p.x * 0.3, 0.5 + (p.y - PANEL_Y) * 2.0)
    lower = make("PANEL.lower_panel", bm, (0, PANEL_Y, LOWER_Z0), M["woodgrain"], "Subpanel (switches, circuit breakers, engine controls): wood-grain laminate",
                 "اللوحة السفلية (المفاتيح والقواطع وأدوات التحكم بالمحرك): قشرة بنقش الخشب", smooth=False, ref="p.7-8, 7-9")
    add_bevel(lower, 0.0035, 2)

    # ---- instruments: a moulded rim round each opening, the dial at the bottom of its recess, the glass in the rim
    def rim_profile(r, blank=False):
        lip = [(r + RIM, 0.0), (r + RIM - 0.0007, 0.0026), (r + RIM - 0.0024, 0.0045), (r + 0.0028, 0.0050), (r + 0.0012, 0.0041), (r + 0.0003, 0.0018)]
        return lip + ([(r + 0.0003, 0.0006)] if blank else [(r + 0.0003, -DIAL_DEPTH - 0.0006)])

    pointer_of = {"ASI": (0.80, 0.0052, 0.20, "pointer", 0), "VSI": (0.80, 0.0052, 0.20, "pointer", 0), "TACH": (0.80, 0.0052, 0.20, "pointer", 0),
                  "SUCTION": (0.74, 0.0036, 0.20, "pointer", 0),
                  "ALT_10000": (0.90, 0.0016, 0.0, "marker", 0), "ALT_1000": (0.52, 0.0100, 0.0, "spade", 1), "ALT_100": (0.86, 0.0044, 0.16, "pointer", 2),
                  "CLOCK_H": (0.48, 0.0034, 0.0, "pointer", 0), "CLOCK_M": (0.74, 0.0026, 0.0, "pointer", 1)}
    which = {"ALT_10000": (" (tens of thousands of feet)", " (عشرات آلاف الأقدام)"), "ALT_1000": (" (thousands of feet)", " (آلاف الأقدام)"), "ALT_100": (" (hundreds of feet)", " (مئات الأقدام)"),
             "CLOCK_H": (" (hours)", " (الساعات)"), "CLOCK_M": (" (minutes)", " (الدقائق)")}
    y_pointer = PANEL_Y - DIAL_DEPTH + 0.0030
    for name, cell, x, z, dia, needles in INSTRUMENTS:
        r = dia / 2; c = (x, PANEL_Y, z); segs = 40 if dia > D2 else 28
        en, ar = INSTRUMENT_NAMES[name]
        bm = new_bm()
        revolve(bm, rim_profile(r), axis="Y", origin=c, segs=segs, cap_start=False, cap_end=True)
        make(f"PANEL.{name}.bezel", bm, c, M["bezel_black"], f"{en}: rim and recess", f"{ar}: الإطار والتجويف", instrument=name)
        bm = new_bm()
        if name in ("AI", "DG"):
            moving, fixed = ("AI_BALL", "AI_MASK") if name == "AI" else ("DG_CARD", "DG_MASK")
            disc_face(bm, c, r * 0.98, cell_uv(moving), segs, y_offset=-DIAL_DEPTH)
            if name == "AI":
                ob = make("PANEL.AI.ball", bm, (x, PANEL_Y - DIAL_DEPTH, z), dials, "Attitude indicator — gyro horizon (vacuum)", "مؤشر الوضع — الأفق الجيروسكوبي", status="poh", smooth=False,
                          aft=True, ref="p.7-34", animate="ai_ball", spin_axis="y", spin_sign=-1)
            else:
                ob = make("PANEL.DG.card", bm, (x, PANEL_Y - DIAL_DEPTH, z), dials, "Directional indicator — compass card (vacuum)", "المؤشر الاتجاهي — بطاقة البوصلة", status="poh", smooth=False,
                          aft=True, ref="p.7-34", animate="dg_card", spin_axis="y", spin_sign=-1)
            ob["keep_faces"] = True
            bm = new_bm()
            disc_face(bm, c, r, cell_uv(fixed), segs, y_offset=-DIAL_DEPTH + 0.0038, rings=(1.0,))
            ob = make(f"PANEL.{name}.mask", bm, c, M["dials_alpha"], en + (" (miniature aeroplane and bank index)" if name == "AI" else " (lubber line)"),
                      ar + (" (الطائرة المصغرة ومؤشر الميل)" if name == "AI" else " (خط الاتجاه)"), status="poh", smooth=False, aft=True, ref="p.7-34", instrument=name)
            ob["keep_faces"] = True
        else:
            disc_face(bm, c, r, cell_uv(cell), segs, y_offset=-DIAL_DEPTH, fill=0.955)
            ob = make(f"PANEL.{name}.face", bm, c, dials, f"{en}: dial", f"{ar}: القرص", status="poh" if name not in ("VOR1", "VOR2", "ADF") else "estimated", smooth=False, aft=True, instrument=name,
                      **(dict(ref="Fig 2-2 / 2-3 markings") if name in ("ASI", "TACH", "SUCTION") else {}),
                      **(dict(ref="p.7-7 (Fig 7-2)", note="A plain face of its kind; the pointers of the radio aids are not driven") if name in ("VOR1", "VOR2", "ADF") else {}))
            ob["keep_faces"] = True
        bm = new_bm()
        revolve(bm, [(0.0, -0.0004), (r * 0.6, -0.0007), (r + 0.0003, -0.0016)], axis="Y", origin=c, segs=segs, cap_start=False, cap_end=False)
        make(f"PANEL.{name}.glass", bm, c, M["instrument_glass"], "Instrument glass", "زجاج العداد", kind="glass")
        top = max((pointer_of[nd][4] for nd in needles if nd != "TC"), default=0)
        for nd in needles:
            if nd == "TC":
                continue
            length, width, tail, style, layer = pointer_of[nd]
            more_en, more_ar = which.get(nd, ("", ""))
            needle(ctx, f"PANEL.{name}.needle_{nd}", (x, y_pointer + layer * 0.0009, z), length * r, width, M["paint_white"], f"{en}: pointer{more_en}", f"{ar}: المؤشر{more_ar}", nd,
                   tail=tail * r, style=style, hub=(0.0046 if dia > D2 else 0.0030, M["black_plastic"]) if layer == top else None)      # the top pointer carries the hub cap
        if name == "TC":
            # the miniature aeroplane, seen from behind (it banks with the rate of turn), and the ball of the inclinometer
            cc = Vector((x, y_pointer, z))
            bm = new_bm()
            box(bm, (dia * 0.66, 0.0007, 0.0034), center=cc)
            box(bm, (0.0030, 0.0007, 0.0125), center=cc + Vector((0, 0, 0.0075)))
            box(bm, (0.0140, 0.0007, 0.0026), center=cc + Vector((0, 0, 0.0088)))
            revolve(bm, [(0.0046, -0.00035), (0.0046, 0.00035)], axis="Y", origin=cc, segs=14)
            tcn = make("PANEL.TC.needle_TC", bm, cc, M["paint_white"], "Turn coordinator: miniature aeroplane (electric gyro)", "منسق الانعطاف: الطائرة المصغرة (جيروسكوب كهربائي)", status="poh",
                       smooth=False, ref="p.7-34", needle="TC", spin_axis="y", spin_sign=-1, animate="needle")
            tcn["keep_faces"] = True; tcn["no_shade"] = True
            bm = new_bm()
            bc = (x, y_pointer - 0.0006, z - dia * 0.30)
            revolve(bm, [(0.0042, -0.0006), (0.0042, 0.0006)], axis="Y", origin=bc, segs=14)
            ballo = make("PANEL.TC.ball", bm, bc, M["black_plastic"], "Inclinometer ball (slip and skid)", "كرة مؤشر الانزلاق", status="poh", ref="p.7-34", animate="tc_ball")
            ballo["no_shade"] = True

    # ---- the small indicators near the left edge: a rectangular face each, in a common frame where two stand together
    FRAME = 0.0032                       # the frame stands this far proud of the panel
    for name, x, z, bar_l, bar_r in RECT_GAUGES:
        en, ar = INSTRUMENT_NAMES[name]; c = (x, PANEL_Y, z)
        hw, hh = RECT_W / 2, RECT_H / 2
        x_l, x_r = x + hw + bar_l, x - hw - bar_r
        depth = FRAME + DIAL_DEPTH; y_mid = PANEL_Y + (FRAME - DIAL_DEPTH) / 2
        bm = new_bm()
        for sz in (1, -1):
            box(bm, (x_l - x_r, depth, 0.003), center=((x_l + x_r) / 2, y_mid, z + sz * (hh + 0.0015)))
        if bar_l:
            box(bm, (bar_l, depth, RECT_H), center=(x + hw + bar_l / 2, y_mid, z))
        if bar_r:
            box(bm, (bar_r, depth, RECT_H), center=(x - hw - bar_r / 2, y_mid, z))
        cover_top = z - RECT_COVER                                                  # the cover over the foot of the pointer
        box(bm, (RECT_W, 0.0016, cover_top - (z - hh)), center=(x, PANEL_Y - 0.0018, (cover_top + z - hh) / 2))
        make(f"PANEL.{name}.bezel", bm, c, M["bezel_black"], f"{en}: frame", f"{ar}: الإطار", smooth=False, instrument=name, no_screws=True)
        bm = new_bm()
        quad_face(bm, c, RECT_W, RECT_H, MISC["G_" + name], y_offset=-DIAL_DEPTH)
        ob = make(f"PANEL.{name}.face", bm, c, misc, f"{en}: dial", f"{ar}: القرص", status="poh", smooth=False, aft=True, instrument=name, ref="Fig 2-3 markings")
        ob["keep_faces"] = True
        bm = new_bm()
        quad_face(bm, c, RECT_W, RECT_H, (0, 0, 1, 1), y_offset=-0.0006)
        make(f"PANEL.{name}.glass", bm, c, M["instrument_glass"], "Instrument glass", "زجاج العداد", smooth=False, kind="glass")
        needle(ctx, f"PANEL.{name}.needle_{name}", (x, y_pointer, z - RECT_PIVOT), rect_radius(name) * 0.98, 0.0016, M["paint_white"], f"{en}: pointer", f"{ar}: المؤشر", name)

    # ---- space for additional instruments on the right: blanked openings
    for i, (x, z) in enumerate(BLANKS):
        bm = new_bm()
        revolve(bm, rim_profile(D3 / 2, blank=True), axis="Y", origin=(x, PANEL_Y, z), segs=40, cap_start=False, cap_end=False)
        n0 = len(bm.faces)
        disc_face(bm, (x, PANEL_Y, z), D3 / 2 + 0.0003, (0.0, 0.0, 0.05, 0.05), 40, y_offset=0.0009, rings=(1.0,))      # the plug
        mark(bm, n0, 1)
        make(f"PANEL.instrument_space_{i + 1}", bm, (x, PANEL_Y, z), M["bezel_black"], "Space for an additional instrument (blanked)", "موضع لعداد إضافي (مغطّى)", status="poh", more=(M["black_plastic"],), aft=1,
             ref="p.7-6, 7-7 (Fig 7-2)", note="The right side of the panel has space for additional instruments and avionics equipment (POH, instrument panel description)")

    # ---- the avionics stack: each unit a face with its readouts and legends, and its knobs standing on it
    labels = {"COMNAV1": ("NAV/COM 1 (COM transceiver, VOR/LOC NAV receiver)", "جهاز الملاحة والاتصال 1"), "COMNAV2": ("NAV/COM 2", "جهاز الملاحة والاتصال 2"), "ADF": ("ADF receiver", "مستقبل ADF"),
              "XPDR": ("Transponder", "جهاز الاستجابة"), "AUDIO": ("Audio control panel", "لوحة التحكم الصوتي"), "MARKER": ("Marker beacon indicator lights and switches", "أضواء ومفاتيح منارات العلامات")}
    for region, z, h in stack_rows():
        cx = STACK_X; face_y = PANEL_Y + 0.0032
        bm = new_bm()
        box(bm, (RADIO_W, 0.0282, h), center=(cx, PANEL_Y - 0.0109, z))          # from 25 mm behind the face of the panel to 3 mm proud of it
        n0 = len(bm.faces)
        quad_face(bm, (cx, face_y + 0.0001, z), RADIO_W - 0.0004, h - 0.0004, MISC[region])
        n1 = len(bm.faces)
        big = sorted([k for k in RADIO_KNOBS[region] if k[2] >= 0.007], key=lambda k: k[0])
        for u, v, r, kind in RADIO_KNOBS[region]:
            o = (cx + RADIO_W / 2 - u * RADIO_W, face_y, z + h / 2 - v * h)
            if kind == "bat":           # the lever of a small switch, on its nut
                revolve(bm, [(0.0030, 0.0), (0.0030, 0.0014), (0.0019, 0.0022), (0.0, 0.0022)], axis="Y", origin=o, segs=8)
                tube(bm, [Vector(o) + Vector((0, 0.0018, 0)), Vector(o) + Vector((0, 0.0095, 0.0032))], 0.0012, segs=6, radius_end=0.0016)
            elif r < 0.007:
                revolve(bm, knob_profile(r, 0.0095), axis="Y", origin=o, segs=14)
        n2 = len(bm.faces)
        mark(bm, n0, 1); mark(bm, n1, 2)
        bats = any(k[3] == "bat" for k in RADIO_KNOBS[region])
        ob = make(f"PANEL.radio_{region}", bm, (cx, PANEL_Y, z), M["bezel_black"], labels[region][0], labels[region][1], smooth=False, more=(misc, M["chrome"] if bats else M["black_plastic"]), aft=1,
                  ref="p.7-6, 7-7 (Fig 7-2)", note="A plain set of its kind for the period; the avionics fitted vary by aircraft")
        for side, (u, v, r, kind) in zip(("L", "R"), big):
            o = (cx + RADIO_W / 2 - u * RADIO_W, face_y, z + h / 2 - v * h)
            bm = new_bm()
            if kind == "dual":          # two knobs, one on the other
                revolve(bm, knob_profile(r, 0.0062), axis="Y", origin=o, segs=20)
                revolve(bm, knob_profile(r * 0.60, 0.0085, 0.0062), axis="Y", origin=o, segs=16)
            else:
                revolve(bm, knob_profile(r, 0.0105), axis="Y", origin=o, segs=20)
                box(bm, (0.0012, 0.0008, r * 0.9), center=(o[0], o[1] + 0.0107, o[2] + r * 0.45))      # the pointer line on a selector
            kn = make(f"PANEL.radio_{region}.knob_{side}", bm, o, M["black_plastic"], "Selector knob", "مقبض الاختيار", parent=ob, animate="knob", spin_axis="y", spin_sign=-1)

    # ---- small plates on the panel: the low-voltage light near the ammeter, the hour recorder, the limitations placard
    def plate(name, x, z, w, h, region, en, ar, base=PANEL_Y, thick=0.0012, **tags):
        bm = new_bm()
        box(bm, (w, thick, h), center=(x, base + thick / 2, z))
        n0 = len(bm.faces)
        quad_face(bm, (x, base + thick + 0.0002, z), w - 0.0008, h - 0.0008, MISC[region])
        mark(bm, n0, 1)
        ob = make(name, bm, (x, PANEL_Y, z), M["bezel_black"], en, ar, smooth=False, more=(misc,), aft=1, **tags)
        ob["keep_faces"] = True
        return ob
    bm = new_bm()
    quad_face(bm, (COL_RECT, PANEL_Y + 0.0012, 1.351), 0.034, 0.018, MISC["LOW_VOLT"])
    ob = make("PANEL.low_volt", bm, (COL_RECT, PANEL_Y, 1.351), misc, "LOW VOLTAGE warning light", "ضوء تحذير انخفاض الجهد", status="poh", smooth=False, aft=True, ref="p.7-26")
    ob["keep_faces"] = True
    plate("PANEL.hourmeter", -0.296, ROW2 + 0.004, 0.050, 0.024, "HOURMETER", "Flight hour recorder", "مسجل ساعات الطيران", status="poh", ref="p.7-7 (Fig 7-2)")
    plate("PANEL.placard_speed", -0.415, ROW1 + 0.004, 0.128, 0.032, "PLACARD_SPEED", "Limitations placard (POH Section 2)", "لوحة القيود", status="poh", ref="Section 2")

    # ---- the subpanel. Electrical switches: ivory rockers in black frames; the master switch a red split rocker
    frames = new_bm()
    def rocker(name, x, z, en, ar, red=False, w=0.0118, h=0.0220, frame=True):
        bm = new_bm()
        side = [(0.0, -h / 2), (0.0048, -h / 2), (0.0026, 0.0), (0.0048, h / 2), (0.0, h / 2)]       # from the side: both ends proud, the middle low
        extrude_profile(bm, side, Y, Z, (x, LF + 0.0022, z), X, -w / 2, w / 2, smooth_sides=False)
        if frame:
            box(frames, (w + 0.0050, 0.0024, h + 0.0050), center=(x, LF + 0.0012, z))
        return make(name, bm, (x, LF + 0.0022, z), M["knob_red" if red else "switch_ivory"], en, ar, status="poh", smooth=False, ref="p.7-25/27", animate="switch", hinge_axis="x",
                    hinge_sign=1, range_deg=[-15, 15])
    # the right half of the master switch, BAT, controls all electrical power; the left half, ALT, the alternator (POH p.7-25)
    rocker("PANEL.master_alt", 0.4445, 1.305, "Master switch — ALT half (left)", "المفتاح الرئيسي — نصف المولّد (الأيسر)", red=True, w=0.0112, frame=False)
    rocker("PANEL.master_bat", 0.4325, 1.305, "Master switch — BAT half (right)", "المفتاح الرئيسي — نصف البطارية (الأيمن)", red=True, w=0.0112, frame=False)
    box(frames, (0.0290, 0.0024, 0.0270), center=(0.4385, LF + 0.0012, 1.305))
    rocker("PANEL.switch_avionics_master", 0.352, SUB_LOWER, "Avionics power switch", "مفتاح طاقة الأجهزة الإلكترونية")
    for nm, x, z, en, ar in (("beacon", 0.172, SUB_UPPER, "Beacon light switch", "مفتاح المنارة"), ("pitot_heat", 0.150, SUB_UPPER, "Pitot heat switch", "مفتاح تسخين البيتو"),
                             ("nav_lights", 0.194, SUB_LOWER, "Navigation lights switch", "مفتاح أضواء الملاحة"), ("strobe", 0.172, SUB_LOWER, "Strobe lights switch", "مفتاح أضواء الوميض"),
                             ("taxi_light", 0.150, SUB_LOWER, "Taxi light switch", "مفتاح ضوء التدرج"), ("landing_light", 0.128, SUB_LOWER, "Landing light switch", "مفتاح ضوء الهبوط")):
        rocker(f"PANEL.switch_{nm}", x, z, en, ar)
    make("PANEL.switch_frames", frames, (0, PANEL_Y, LOWER_Z0), M["black_plastic"], "Frames of the rocker switches", "إطارات المفاتيح", smooth=False, count=8)

    # ignition switch: the legend plate with its ring, the lock with its key
    ix, iz = 0.403, 1.262
    ign_plate = plate("PANEL.ignition", ix, iz + 0.003, 0.050, 0.050, "IGNITION", "Ignition switch plate: OFF, R, L, BOTH, START", "لوحة مفتاح الإشعال: OFF ،R ،L ،BOTH ،START", base=LF, thick=0.0010,
                      status="poh", ref="p.7-25")
    bm = new_bm()
    revolve(bm, [(0.0122, LOWER_FACE + 0.0010), (0.0160, LOWER_FACE + 0.0010), (0.0160, LOWER_FACE + 0.0034), (0.0138, LOWER_FACE + 0.0048), (0.0122, LOWER_FACE + 0.0048)], axis="Y",
            origin=(ix, PANEL_Y, iz), segs=6)
    make("PANEL.ignition_nut", bm, (ix, PANEL_Y, iz), M["chrome"], "Ignition switch mounting nut", "صامولة تثبيت مفتاح الإشعال", smooth=False)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.0118, 0.0), (0.0118, LOWER_FACE + 0.0052), (0.0104, LOWER_FACE + 0.0064), (0.0, LOWER_FACE + 0.0064)], axis="Y", origin=(ix, PANEL_Y, iz), segs=24)
    n0 = len(bm.faces)
    box(bm, (0.0018, 0.0120, 0.0075), center=(ix, LF + 0.0064 + 0.0060, iz))              # the shank of the key
    box(bm, (0.0026, 0.0200, 0.0190), center=(ix, LF + 0.0064 + 0.0120 + 0.0100, iz))     # its head
    mark(bm, n0, 1)
    make("PANEL.ignition_switch", bm, (ix, PANEL_Y, iz), M["chrome"], "Ignition switch (key): OFF, R, L, BOTH, START", "مفتاح الإشعال (بالمفتاح): OFF ،R ،L ،BOTH ،START", status="poh", system="IGNITION",
         more=(M["black_plastic"],), ref="p.7-25", animate="ignition", spin_axis="y", spin_sign=-1, range_deg=[-70, 70])

    # push-pull controls: carburetor heat, throttle, mixture, primer, cabin heat and cabin air
    def pull_knob(name, x, z, r, mat, en, ar, travel=0.07, style="round", stand=0.024, ref="p.7-23"):
        bm = new_bm()
        k0 = LOWER_FACE + stand                               # where the knob begins, from the face of the panel
        tube(bm, [Vector((x, PANEL_Y - 0.05, z)), Vector((x, PANEL_Y + k0 + 0.002, z))], 0.0035, segs=10)
        if style == "throttle":
            prof = [(0.0, k0), (r * 0.70, k0), (r * 0.97, k0 + 0.004), (r, k0 + 0.011), (r * 0.95, k0 + 0.019), (r * 0.70, k0 + 0.0245), (0.0, k0 + 0.026)]
        elif style == "mixture":                              # the button of the vernier stands in the middle of the knob
            prof = [(0.0, k0), (r * 0.78, k0), (r, k0 + 0.004), (r, k0 + 0.016), (r * 0.86, k0 + 0.020), (r * 0.40, k0 + 0.020), (r * 0.40, k0 + 0.0245), (0.0, k0 + 0.0245)]
        else:
            prof = [(0.0, k0), (r * 0.80, k0), (r, k0 + 0.003), (r, k0 + 0.012), (r * 0.80, k0 + 0.016), (0.0, k0 + 0.017)]
        revolve(bm, prof, axis="Y", origin=(x, PANEL_Y, z), segs=28)
        ob = make(name, bm, (x, PANEL_Y, z), mat, en, ar, status="poh", ref=ref, animate="pull", travel_m=travel)
        bm = new_bm()
        rb = max(0.0075, r * 0.62)
        if style == "throttle":                               # the friction lock: a knurled ring on the shaft, against the panel
            prof = [(0.0045, LOWER_FACE), (0.0110, LOWER_FACE), (0.0130, LOWER_FACE + 0.002), (0.0130, LOWER_FACE + 0.010), (0.0105, LOWER_FACE + 0.012), (0.0045, LOWER_FACE + 0.012)]
        else:
            prof = [(0.0045, LOWER_FACE), (rb, LOWER_FACE), (rb, LOWER_FACE + 0.004), (rb * 0.72, LOWER_FACE + 0.007), (0.0045, LOWER_FACE + 0.007)]
        revolve(bm, prof, axis="Y", origin=(x, PANEL_Y, z), segs=20)
        make(name + "_bushing", bm, (x, PANEL_Y, z), M["cast_alu"], en + ": bushing" + (" and friction lock" if style == "throttle" else ""), ar + ": الجلبة" + (" وقفل الاحتكاك" if style == "throttle" else ""))
        return ob
    pull_knob("PANEL.carb_heat", 0.090, 1.280, 0.0125, M["black_plastic"], "Carburetor heat control (pull = ON)", "تحكم تسخين المكربن (اسحب = تشغيل)")
    pull_knob("PANEL.throttle", 0.0, 1.277, 0.0205, M["black_plastic"], "Throttle (push = open), with friction lock", "الخانق (ادفع = فتح) مع قفل الاحتكاك", travel=0.085, style="throttle", stand=0.030)
    pull_knob("PANEL.mixture", -0.090, 1.280, 0.0145, M["knob_red"], "Mixture control (red, vernier): pull = lean and idle cut-off", "تحكم الخليط (أحمر): اسحب للإفقار وقطع الوقود", style="mixture", stand=0.030)
    pull_knob("PANEL.primer", 0.462, 1.252, 0.0100, M["black_plastic"], "Engine primer (pull and push; locks when turned)", "مضخة التحضير", travel=0.06, stand=0.016, ref="p.7-22")
    pull_knob("PANEL.cabin_heat", -0.325, 1.284, 0.0100, M["black_plastic"], "Cabin heat control", "تحكم تدفئة المقصورة", stand=0.018, ref="p.7-29")
    pull_knob("PANEL.cabin_air", -0.380, 1.284, 0.0100, M["black_plastic"], "Cabin air control", "تحكم هواء المقصورة", stand=0.018, ref="p.7-29")

    # wing flap switch: a lever in a slotted plate, with the scale of the position indicator on its left (POH p.7-9, 7-10)
    fx, fz = -0.185, 1.280
    plate("PANEL.flap_ind", fx + 0.019, fz, 0.018, 0.056, "FLAP_IND", "Wing flap position indicator", "مؤشر وضع القلابات", base=LF, thick=0.0010, status="poh", ref="p.7-9, 7-10")
    bm = new_bm()
    for sx in (1, -1):
        box(bm, (0.0050, 0.0016, 0.056), center=(fx + sx * 0.0052, LF + 0.0008, fz))
    for sz in (1, -1):
        box(bm, (0.0154, 0.0016, 0.0040), center=(fx, LF + 0.0008, fz + sz * 0.0260))
    n0 = len(bm.faces)
    box(bm, (0.0056, 0.0004, 0.0480), center=(fx, LF + 0.0002, fz))                       # the dark of the slot
    mark(bm, n0, 1)
    make("PANEL.flap_slot", bm, (fx, PANEL_Y, fz), M["grey_plastic"], "Slotted plate of the wing flap switch lever", "اللوحة المشقوقة لذراع مفتاح القلابات", smooth=False, more=(M["black_plastic"],),
         status="poh", ref="p.7-9, 7-10", note="The lever moves in a slotted panel with stops at the 10° and 20° positions (POH p.7-10)")
    pivot = Vector((fx, PANEL_Y - 0.030, fz + 0.0034)); reach = 0.075; up = math.radians(12.0)      # the lever at UP
    tip = pivot + Vector((0, reach * math.cos(up), reach * math.sin(up)))
    bm = new_bm()
    tube(bm, [pivot, tip], 0.0022, segs=8)
    n0 = len(bm.faces)
    box(bm, (0.0210, 0.0090, 0.0075), center=tip + Vector((0, 0.002, 0)))                  # the knob: a small flat paddle
    mark(bm, n0, 1)
    make("PANEL.flap_switch", bm, pivot, M["steel"], "Wing flap switch lever (UP, 10°, 20°, FULL)", "ذراع مفتاح القلابات", status="poh", smooth=False, more=(M["switch_ivory"],), ref="p.7-9, 7-10",
         animate="flap_switch", hinge_axis="x", hinge_sign=1, range_deg=[-30, 0])

    # circuit breakers, on the left of the subpanel: a button each, in its collar
    collars = new_bm(); n_breakers = 0
    for row, (z, count, x0) in enumerate(((SUB_UPPER, 10, 0.345), (SUB_LOWER, 7, 0.3295))):
        for i in range(count):
            x = x0 - i * 0.0158
            bm = new_bm()
            revolve(bm, [(0.0041, LOWER_FACE), (0.0041, LOWER_FACE + 0.0062), (0.0034, LOWER_FACE + 0.0070), (0.0, LOWER_FACE + 0.0070)], axis="Y", origin=(x, PANEL_Y, z), segs=10)
            make(f"PANEL.breaker_{row}_{i}", bm, (x, PANEL_Y, z), M["black_plastic"], "Push-to-reset circuit breaker", "قاطع دائرة", status="poh", system="ELECTRICAL", ref="p.7-27")
            revolve(collars, [(0.0044, LOWER_FACE), (0.0062, LOWER_FACE), (0.0062, LOWER_FACE + 0.0016), (0.0050, LOWER_FACE + 0.0024), (0.0044, LOWER_FACE + 0.0024)], axis="Y",
                    origin=(x, PANEL_Y, z), segs=6)
            n_breakers += 1
    make("PANEL.breaker_collars", collars, (0, PANEL_Y, LOWER_Z0), M["cast_alu"], "Mounting nuts of the circuit breakers", "صواميل تثبيت قواطع الدائرة", smooth=False, system="ELECTRICAL", count=n_breakers)

    # ---- mounting screws of the round instruments: four to each, black oxide (one part for all of them)
    bm = new_bm()
    n_screws = 0
    for name, cell, x, z, dia, needles in INSTRUMENTS:
        reach = 0.79 * (dia / 2 + RIM)
        for sx in (-1, 1):
            for sz in (-1, 1):
                revolve(bm, [(0.0, 0.0), (0.0026, 0.0), (0.0030, 0.0012), (0.0030, 0.0022), (0.0, 0.0026)], axis="Y", origin=(x + sx * reach, PANEL_Y, z + sz * reach), segs=8)
                n_screws += 1
    make("PANEL.instrument_screws", bm, (0, PANEL_Y, PANEL_Z0), M["screw"], "Instrument mounting screws", "براغي تثبيت العدادات", count=n_screws, note="Four to an instrument; representative")

    # ---- lettering: the name of each switch and control, white on the panel (one part)
    bm = new_bm()
    face_y = LF + 0.0006
    def word(text, x, z, h=0.0046, y=face_y):
        letter_quad(bm, text, (x, y, z), h)
    word("MASTER", 0.4385, 1.3290, 0.0050); word("ALT", 0.4445, 1.3222, 0.0040); word("BAT", 0.4325, 1.3222, 0.0040)
    word("PRIMER", 0.462, 1.2330, 0.0048)
    word("AVN PWR", 0.352, 1.2845, 0.0042)
    word("CIRCUIT BREAKERS", 0.274, 1.3265, 0.0046); word("PUSH TO RESET", 0.282, 1.2890, 0.0038)
    word("BCN", 0.172, 1.3285, 0.0042); word("PITOT HT", 0.150, 1.3285, 0.0042)
    word("NAV", 0.194, 1.2838, 0.0042); word("STROBE", 0.172, 1.2838, 0.0042); word("TAXI", 0.150, 1.2838, 0.0042); word("LAND", 0.128, 1.2838, 0.0042)
    word("LIGHTS", 0.161, 1.2400, 0.0042)
    word("CARB HEAT", 0.090, 1.3040, 0.0050); word("PULL ON", 0.090, 1.2585, 0.0040)
    word("THROTTLE", 0.0, 1.3080, 0.0052); word("PUSH OPEN", 0.0, 1.2470, 0.0040)
    word("MIXTURE", -0.090, 1.3040, 0.0050); word("PULL LEAN", -0.090, 1.2585, 0.0040)
    word("PANEL LT", -0.0370, 1.2480, 0.0034); word("RADIO LT", -0.0600, 1.2480, 0.0034)
    word("WING FLAPS", fx + 0.008, 1.3160, 0.0046)
    word("CABIN HT", -0.325, 1.3040, 0.0046); word("CABIN AIR", -0.380, 1.3040, 0.0046)
    word("PARK BRAKE", 0.25, 1.2290, 0.0046)
    cover_y = PANEL_Y - 0.0010 + 0.0003                       # on the covers of the small indicators, behind their glass
    word("FUEL", COL_RECT, 1.481 - 0.0130, 0.0040, cover_y); word("OIL", COL_RECT, 1.435 - 0.0130, 0.0040, cover_y)
    lettering = make("PANEL.lettering", bm, (0, PANEL_Y, LOWER_Z0), M["placards"], "Panel lettering: the names of the switches and controls", "كتابات اللوحة: أسماء المفاتيح وأدوات التحكم", smooth=False,
                     note="The plain names of the controls, placed beside them; the typeface and exact wording of the aircraft's placards are not reproduced")
    lettering["keep_faces"] = True

    # ---- magnetic compass: on the glareshield, on the centreline
    cz = PANEL_Z1 + 0.0745; cy = PANEL_Y + 0.016
    bm = new_bm()
    box(bm, (0.066, 0.050, 0.046), center=(0, cy, cz))
    box(bm, (0.018, 0.018, 0.016), center=(0, cy - 0.004, cz - 0.029))                    # its foot on the glareshield
    n0 = len(bm.faces)
    quad_face(bm, (0, cy + 0.0253, cz + 0.002), 0.046, 0.018, MISC["COMPASS"])
    mark(bm, n0, 1)
    comp = make("PANEL.magnetic_compass", bm, (0, cy, cz), M["black_plastic"], "Magnetic compass", "البوصلة المغناطيسية", status="poh", smooth=False, more=(misc,), aft=1, ref="p.7-7 (Fig 7-2)")
    add_bevel(comp, 0.006, 3)

    # ---- glareshield: a padded lip that overhangs the top of the panel, and a deck that rises forward to the foot of
    # the windshield, trimmed to the inside of the skin at every station (heights here are before CABIN_LIFT)
    def inside(station, z):
        return max(0.10, fus_half_width_at(station, z + CABIN_LIFT) - 0.024)
    lip = [(-0.012, 0.0015), (0.030, 0.0015), (0.046, 0.0050), (0.0545, 0.0160), (0.0530, 0.0290), (0.0440, 0.0385), (0.0260, 0.0420), (-0.012, 0.0420)]      # (aft of the panel face, above its top)
    half = inside(19.0, PANEL_Z1 + 0.02)
    stations = [-1.0, -0.94, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.94, 1.0]
    rings = []
    for t in stations:
        x = t * half
        rings.append([Vector((x, PANEL_Y + a, PANEL_Z1 + b)) for a, b in lip])
    bm = new_bm()
    loft(bm, rings, close=True, cap_start=True, cap_end=True, uv_u_scale=0.14, uv_v=[t * half for t in stations])
    uv = bm.loops.layers.uv.active
    deck_z = PANEL_Z1 + 0.042
    strip = []
    for i in range(8):
        t = i / 7
        station = 18.5 - t * 13.5                       # from the panel to FS 5, at the foot of the windshield
        z = deck_z + t * 0.058
        w = inside(station, z)
        strip.append((bm.verts.new(Vector((-w, fs(station), z))), bm.verts.new(Vector((w, fs(station), z)))))
    for (a0, a1), (b0, b1) in zip(strip, strip[1:]):
        f = bm.faces.new([a0, a1, b1, b0]); f.smooth = True
        for l in f.loops:
            l[uv].uv = (l.vert.co.x, l.vert.co.y)
    gs = obj_from_bm("INTERIOR.glareshield", bm, ctx.col, pivot=(0, PANEL_Y, PANEL_Z1), mat=M["vinyl_black"])
    parent_keep(gs, ctx.groups["INTERIOR"])
    ctx.tag(gs, "INTERIOR", "Glareshield (padded)", "واقي الوهج", status="estimated")

def build_controls(ctx):
    M = ctx.mats
    grp = ctx.groups["INTERIOR"]
    LF = PANEL_Y + LOWER_FACE
    # control wheels on push-pull shafts that come through the panel under the gyros (POH p.7-8)
    boots = new_bm()
    for side, x in (("L", YOKE_X), ("R", -YOKE_X)):
        hub = Vector((x, PANEL_Y + 0.26, YOKE_Z))
        bm = new_bm()
        tube(bm, [Vector((x, PANEL_Y - 0.1, YOKE_Z)), hub - Vector((0, 0.022, 0))], 0.0125, segs=16)
        shaft = obj_from_bm(f"INTERIOR.yoke_shaft_{side}", bm, ctx.col, pivot=(x, PANEL_Y, YOKE_Z), mat=M["screw"])
        parent_keep(shaft, grp)
        ctx.tag(shaft, "INTERIOR", "Control wheel shaft (elevator push and pull)", "عمود عجلة القيادة", status="estimated", animate="yoke_shaft")
        revolve(boots, [(0.0135, 0.0), (0.0310, 0.0), (0.0310, 0.0025), (0.0270, 0.0045), (0.0135, 0.0045)], axis="Y", origin=(x, PANEL_Y, YOKE_Z), segs=24)
        # the wheel: a padded centre block on the shaft, an arm from each lower corner, and the two grips standing up from the arms
        bm = new_bm()
        box(bm, (0.176, 0.052, 0.116), center=hub + Vector((0, 0.002, 0.004)))
        box(bm, (0.062, 0.006, 0.017), center=hub + Vector((-0.034, 0.028, -0.030)))      # the name plate, low on the pad
        for sgn in (-1, 1):
            path = bezier(hub + Vector((sgn * 0.070, 0.0, -0.040)), hub + Vector((sgn * 0.118, 0.0, -0.066)), hub + Vector((sgn * 0.158, 0.0, -0.082)), hub + Vector((sgn * 0.172, 0.002, -0.046)), 8)
            path += bezier(hub + Vector((sgn * 0.172, 0.002, -0.046)), hub + Vector((sgn * 0.180, 0.004, 0.012)), hub + Vector((sgn * 0.176, 0.010, 0.066)), hub + Vector((sgn * 0.164, 0.026, 0.110)), 10)[1:]
            tube(bm, path, 0.0125, segs=12, radius_end=0.0158)
        yoke = obj_from_bm(f"INTERIOR.yoke_{side}", bm, ctx.col, pivot=hub, mat=M["vinyl_black"])
        add_bevel(yoke, 0.016, 3); add_subsurf(yoke, 1)
        parent_keep(yoke, shaft)
        ctx.tag(yoke, "INTERIOR", f"Control wheel ({'pilot' if side == 'L' else 'co-pilot'}) — ailerons by rotation, elevator by push and pull", "عجلة القيادة " + ("(الطيار)" if side == "L" else "(مساعد الطيار)"),
                status="poh", ref="p.7-6 (Fig 7-2), 7-8", animate="yoke", spin_axis="y", spin_sign=-1, range_deg=[-90, 90])
        # rudder pedals with toe brakes: just aft of the firewall, where the floor is still narrow
        for px in (-0.075, 0.075):
            bm = new_bm()
            box(bm, (0.07, 0.012, 0.13), center=(x + px, fs(9), FLOOR_TOP + 0.11))
            tube(bm, [Vector((x + px, fs(9), FLOOR_TOP + 0.045)), Vector((x + px, fs(15), FLOOR_TOP + 0.008))], 0.008, segs=8)
            ped = obj_from_bm(f"INTERIOR.pedal_{side}_{'R' if px > 0 else 'L'}", bm, ctx.col, pivot=(x + px, fs(9), FLOOR_TOP + 0.045), mat=M["steel"], smooth=False)
            parent_keep(ped, grp)
            ctx.tag(ped, "INTERIOR", "Rudder pedal with toe brake", "دواسة الدفة مع فرامل", status="poh", ref="p.7-6", animate="pedal", hinge_axis="x", hinge_sign=1, range_deg=[-12, 12])
    boot = obj_from_bm("PANEL.control_wheel_boots", boots, ctx.col, pivot=(0, PANEL_Y, YOKE_Z), mat=M["black_plastic"])
    parent_keep(boot, ctx.groups["PANEL"])
    ctx.tag(boot, "PANEL", "Flanges of the control wheel shafts on the panel", "حلقتا عمودي عجلتي القيادة على اللوحة", status="estimated", count=2)
    # trim wheel on the pedestal below the panel
    bm = new_bm()
    box(bm, (0.16, 0.20, 0.32 + CABIN_LIFT), center=(-0.05, PANEL_Y + 0.06, 1.06 - CABIN_LIFT / 2))
    ped = obj_from_bm("INTERIOR.pedestal", bm, ctx.col, pivot=(-0.05, PANEL_Y, 0.9 - CABIN_LIFT), mat=M["panel_grey"], smooth=False)
    add_bevel(ped, 0.01, 2)
    parent_keep(ped, grp)
    ctx.tag(ped, "INTERIOR", "Control pedestal", "قاعدة أدوات التحكم", status="estimated")
    bm = new_bm()
    revolve(bm, [(0.0, -0.012), (0.075, -0.012), (0.08, -0.004), (0.08, 0.004), (0.075, 0.012), (0.0, 0.012)], axis="X", origin=(-0.13, PANEL_Y + 0.17, 1.14), segs=36)
    tw = obj_from_bm("INTERIOR.trim_wheel", bm, ctx.col, pivot=(-0.13, PANEL_Y + 0.17, 1.14), mat=M["black_plastic"])
    parent_keep(tw, grp)
    ctx.tag(tw, "INTERIOR", "Elevator trim wheel (nose up / nose down) with position indicator", "عجلة موازنة الرافع", status="poh", ref="p.7-6", animate="trim_wheel", spin_axis="x", spin_sign=1)
    # lettering on the pedestal, facing aft, beside the trim wheel
    bm = new_bm()
    ped_y = PANEL_Y + 0.1612
    for text, x, z, h in (("ELEV TRIM", -0.05, 1.262, 0.0072), ("NOSE DN", -0.085, 1.215, 0.0056), ("TAKE OFF", -0.085, 1.14, 0.0056), ("NOSE UP", -0.085, 1.065, 0.0056), ("MIC", 0.0, 1.03, 0.0056)):
        letter_quad(bm, text, (x, ped_y, z - CABIN_LIFT), h)
    pl = obj_from_bm("INTERIOR.pedestal_lettering", bm, ctx.col, pivot=(-0.05, PANEL_Y, 0.9 - CABIN_LIFT), mat=M["placards"], smooth=False)
    parent_keep(pl, grp)
    ctx.tag(pl, "INTERIOR", "Pedestal lettering (elevator trim)", "كتابات القاعدة الوسطى (موازنة الرافع)", status="estimated")
    # fuel selector on the floor between the seats
    bm = new_bm()
    box(bm, (0.17, 0.15, 0.012), center=(0, fs(44), FLOOR_TOP + 0.006))
    sel_base = obj_from_bm("FUEL.selector_plate", bm, ctx.col, pivot=(0, fs(44), FLOOR_TOP), mat=M["panel_grey"], smooth=False)
    parent_keep(sel_base, grp)
    ctx.tag(sel_base, "FUEL", "Fuel selector placard plate (LEFT · BOTH · RIGHT · OFF)", "لوحة محدد الوقود", status="poh", ref="p.7-28")
    bm = new_bm()
    box(bm, (0.028, 0.10, 0.012), center=(0, fs(44) - 0.02, FLOOR_TOP + 0.02))
    revolve(bm, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.025), (0.0, 0.025)], axis="Z", origin=(0, fs(44), FLOOR_TOP + 0.012), segs=20)
    sel = obj_from_bm("FUEL.selector_handle", bm, ctx.col, pivot=(0, fs(44), FLOOR_TOP + 0.012), mat=M["knob_red"], smooth=False)
    parent_keep(sel, grp)
    ctx.tag(sel, "FUEL", "Fuel selector valve handle (shown on BOTH)", "مقبض صمام اختيار الوقود", status="poh", ref="p.7-28", animate="fuel_selector", spin_axis="z", spin_sign=1, positions={"LEFT": -90, "BOTH": 0, "RIGHT": 90, "OFF": 180})
    # lettering of the selector plate: the four positions round the handle, read from the seats
    bm = new_bm()
    top = FLOOR_TOP + 0.0128
    for text, dx, dy in (("BOTH", 0.0, -0.062), ("OFF", 0.0, 0.062), ("LEFT", 0.060, 0.0), ("RIGHT", -0.058, 0.0), ("FUEL", 0.060, 0.058)):
        letter_quad(bm, text, (dx, fs(44) + dy, top), 0.011, axis="flat")
    sl = obj_from_bm("FUEL.selector_lettering", bm, ctx.col, pivot=(0, fs(44), FLOOR_TOP), mat=M["placards"], smooth=False)
    parent_keep(sl, grp)
    ctx.tag(sl, "FUEL", "Fuel selector lettering (LEFT · BOTH · RIGHT · OFF)", "كتابات محدد الوقود (LEFT · BOTH · RIGHT · OFF)", status="poh", ref="p.7-28")
    # parking brake handle below the subpanel, in front of the pilot (POH p.7-9): a rod with a T handle
    bm = new_bm()
    tube(bm, [Vector((0.25, PANEL_Y - 0.01, 1.206)), Vector((0.25, LF + 0.040, 1.196))], 0.0045, segs=8)
    tube(bm, [Vector((0.25 - 0.024, LF + 0.044, 1.1955)), Vector((0.25 + 0.024, LF + 0.044, 1.1955))], 0.0068, segs=10)
    pb = obj_from_bm("INTERIOR.parking_brake", bm, ctx.col, pivot=(0.25, PANEL_Y, 1.20), mat=M["black_plastic"])
    parent_keep(pb, grp)
    ctx.tag(pb, "INTERIOR", "Parking brake handle", "مقبض فرامل الوقوف", status="poh", ref="p.7-9, 7-10", animate="pull", travel_m=0.05)

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

# Where the seats stand (POH Figure 6-3, Loading Arrangements, p.6-7): the centre of gravity of the pilot and
# the front passenger is at station 37 with the seat set for an average occupant (range 34 to 46), that of the
# rear passengers at station 73; baggage area 1 begins behind the rear seat back, at station 82.
# (Build-frame stations; a handbook station lies about 0.7 in further aft at seat height, units.cessna_fs.)
FRONT_SEAT_FS = 28.0      # front edge of the front seat cushions (seat back at 44, occupant at 37)
REAR_SEAT_FS = 64.0       # front edge of the rear seat cushion (seat back at 80 to 82, occupants at 73)


def build_seats(ctx):
    M = ctx.mats
    grp = ctx.groups["INTERIOR"]
    on_rails = getattr(ctx, "detail_level", 0) >= 1      # the detail packs add the seat rails and rollers: the frame then stands on them

    def seat(name, x, y0, w, en, ar, front=True):
        bm = new_bm()
        box(bm, (w, 0.46, 0.09), center=(x, y0 + 0.23, 1.035))
        # vinyl bolsters stand 14 mm proud of the pleated middle: one along each side and a roll under the knees
        for sx in (-1, 1):
            box(bm, (0.058, 0.44, 0.05), center=(x + sx * (w / 2 - 0.029), y0 + 0.23, 1.069))
        box(bm, (w - 0.02, 0.068, 0.052), center=(x, y0 + 0.036, 1.066))
        pan = obj_from_bm(name + ".cushion", bm, ctx.col, pivot=(x, y0, 1.0), mat=M["leather_tan"], smooth=False)
        add_bevel(pan, 0.03, 4); add_subsurf(pan, 1)
        parent_keep(pan, grp)
        ctx.tag(pan, "INTERIOR", en + " — seat cushion", ar + " — وسادة المقعد", status="poh", ref="p.6-7, 7-11",
                note="Stands where POH Figure 6-3 puts its occupant; form and size representative")
        # the middle of the cushion: pleated cloth between vinyl bolsters
        def insert(suffix, parent, corner, across, along, normal, width, length, label_en, label_ar, pivot=None, tilt=None):
            bm = new_bm()
            pleated_insert(bm, corner, across, along, normal, width, length, pleats=max(4, int(round(width / 0.046))))
            ob = obj_from_bm(name + suffix, bm, ctx.col, pivot=pivot or parent.matrix_world.translation, mat=M["cloth"])
            if tilt is not None:
                ob.rotation_euler = tilt
            parent_keep(ob, parent)
            ctx.tag(ob, "INTERIOR", en + " — " + label_en, ar + " — " + label_ar, status="estimated", note="Pleated cloth between vinyl bolsters: a period pattern, not a record of this aircraft's upholstery")
            return ob
        iw = w - 0.11
        insert(".cushion_insert", pan, (x - iw / 2, y0 + 0.065, 1.0805), (1, 0, 0), (0, 1, 0), (0, 0, 1), iw, 0.335, "cushion insert (cloth)", "حشوة الوسادة (قماش)")
        # backs, tilted 14° aft about their lower edge: one for a front seat, two for the split-backed rear seat (POH p.7-11)
        backs = [("", x, w, "seat back", "ظهر المقعد")] if front else [
            ("_L", x + w / 4 + 0.004, w / 2 - 0.012, "left seat back", "ظهر المقعد الأيسر"), ("_R", x - w / 4 - 0.004, w / 2 - 0.012, "right seat back", "ظهر المقعد الأيمن")]
        for suffix, bx, bw, label_en, label_ar in backs:
            bm = new_bm()
            box(bm, (bw, 0.08, 0.52), center=(bx, y0 + 0.44, 1.07 + 0.26))
            # bolsters down each side of the back and a roll across the shoulders
            for sx in (-1, 1):
                box(bm, (0.052, 0.046, 0.50), center=(bx + sx * (bw / 2 - 0.026), y0 + 0.411, 1.07 + 0.26))
            box(bm, (bw - 0.02, 0.048, 0.052), center=(bx, y0 + 0.410, 1.07 + 0.495))
            back = obj_from_bm(name + ".back" + suffix, bm, ctx.col, pivot=(bx, y0 + 0.44, 1.07), mat=M["leather_tan"], smooth=False)
            back.rotation_euler = (math.radians(-14), 0, 0)
            add_bevel(back, 0.03, 4); add_subsurf(back, 1)
            parent_keep(back, grp)
            ctx.tag(back, "INTERIOR", en + " — " + label_en, ar + " — " + label_ar, status="poh", ref="p.7-11", animate="seat_back", hinge_axis="x", hinge_sign=1, range_deg=[-25, 0],
                    note="The seat back angle is adjustable and the back folds forward (POH p.7-11); form representative")
            # its insert: built upright like the back, then tilted with it
            ibw = bw - 0.10
            insert(".back_insert" + suffix, back, (bx - ibw / 2, y0 + 0.44 - 0.0405, 1.07 + 0.07), (1, 0, 0), (0, 0, 1), (0, -1, 0), ibw, 0.40,
                   label_en + " insert (cloth)", "حشوة " + label_ar + " (قماش)", pivot=(bx, y0 + 0.44, 1.07), tilt=(math.radians(-14), 0, 0))
        bm = new_bm()
        floor_top = FLOOR_TOP - CABIN_LIFT               # the frame is lifted with the seat, so start it at the floor
        leg = 0.12 if front else w / 2 - 0.09            # the legs of a front seat stand over its two rails
        base = floor_top + (0.045 if front and on_rails else 0.012)
        for sx in (-leg, leg):
            tube(bm, [Vector((x + sx, y0 + 0.08, base if front and on_rails else floor_top)), Vector((x + sx, y0 + 0.08, 1.0))], 0.012, segs=8)
            tube(bm, [Vector((x + sx, y0 + 0.40, base if front and on_rails else floor_top)), Vector((x + sx, y0 + 0.40, 1.0))], 0.012, segs=8)
            tube(bm, [Vector((x + sx, y0 + 0.02, base)), Vector((x + sx, y0 + 0.46, base))], 0.010, segs=8)
        legs = obj_from_bm(name + ".frame", bm, ctx.col, pivot=(x, y0, floor_top), mat=M["steel"])
        parent_keep(legs, grp)
        ctx.tag(legs, "INTERIOR", en + " — seat frame", ar + " — إطار المقعد", status="estimated")
        # lap belt
        bm = new_bm()
        pts = bezier(Vector((x - w / 2 + 0.02, y0 + 0.30, 0.98)), Vector((x - w / 2 + 0.06, y0 + 0.26, 1.10)), Vector((x + w / 2 - 0.06, y0 + 0.26, 1.10)), Vector((x + w / 2 - 0.02, y0 + 0.30, 0.98)), 16)
        strap(bm, pts, 0.048)
        belt = obj_from_bm(name + ".lap_belt", bm, ctx.col, pivot=(x, y0 + 0.3, 1.0), mat=M["belt"])
        parent_keep(belt, grp)
        ctx.tag(belt, "INTERIOR", en + " — seat belt", ar + " — حزام المقعد", status="poh", ref="p.7-12 (Fig 7-4)",
                note="All seat positions have seat belts, attached to fittings on the floorboard (POH p.7-12)")
        bm = new_bm()
        box(bm, (0.05, 0.02, 0.03), center=(x + 0.02, y0 + 0.27, 1.105))
        buckle = obj_from_bm(name + ".buckle", bm, ctx.col, pivot=(x, y0 + 0.3, 1.1), mat=M["chrome"], smooth=False)
        parent_keep(buckle, grp)
        ctx.tag(buckle, "INTERIOR", "Seat belt buckle", "مشبك حزام المقعد", status="poh", ref="p.7-12 (Fig 7-4)")
        return pan
    seat("INTERIOR.seat_pilot", 0.28, fs(FRONT_SEAT_FS), 0.40, "Pilot seat (adjustable)", "مقعد الطيار")
    seat("INTERIOR.seat_copilot", -0.28, fs(FRONT_SEAT_FS), 0.40, "Front passenger seat (adjustable)", "مقعد الراكب الأمامي")
    seat("INTERIOR.seat_rear", 0.0, fs(REAR_SEAT_FS), 0.76, "Rear seat (fixed, split-backed)", "المقعد الخلفي (ثابت بظهرين)", front=False)
    # shoulder harnesses for the front seats: from the rear door post above the window line, over the outboard
    # shoulder, to the seat belt link at the inboard hip (POH p.7-12, Figure 7-4)
    y0 = fs(FRONT_SEAT_FS)
    for side, x in (("L", 0.28), ("R", -0.28)):
        bm = new_bm()
        o = 1 if side == "L" else -1
        pts = bezier(Vector((x + o * 0.19, fs(69.0), 1.925)), Vector((x + o * 0.17, y0 + 0.62, 1.80)), Vector((x + o * 0.10, y0 + 0.37, 1.50)), Vector((x - o * 0.06, y0 + 0.27, 1.13)), 18)
        strap(bm, pts, 0.048)
        sh = obj_from_bm(f"INTERIOR.shoulder_harness_{side}", bm, ctx.col, pivot=pts[0], mat=M["belt"])
        parent_keep(sh, grp)
        ctx.tag(sh, "INTERIOR", "Shoulder harness of the " + ("pilot's" if side == "L" else "front passenger's") + " seat", "حزام الكتف لمقعد " + ("الطيار" if side == "L" else "الراكب الأمامي"),
                status="poh", ref="p.7-12 (Fig 7-4)",
                note="Attached to the rear door post above the window line; it snaps onto the retaining stud of the seat belt link (POH p.7-12, 7-14)")
    # door armrests and inner handles (parented to the doors so they swing with them)
    for side, sgn in (("L", 1), ("R", -1)):
        door = bpy.data.objects.get(f"AIRFRAME.door_{side}")
        if not door:
            continue
        bm = new_bm()
        box(bm, (0.034, 0.34, 0.05), center=(sgn * 0.478, fs(41), 1.31))      # beside the occupant's elbow, above the seat cushion
        arm = obj_from_bm(f"INTERIOR.armrest_{side}", bm, ctx.col, pivot=(sgn * 0.478, fs(41), 1.31), mat=M["leather_tan"], smooth=False)
        add_bevel(arm, 0.012, 3)
        parent_keep(arm, door)
        ctx.tag(arm, "INTERIOR", "Door arm rest", "مسند ذراع الباب", status="poh", ref="p.7-15", note="The inside door handle is combined with the arm rest (POH p.7-15); form representative")
        bm = new_bm()
        box(bm, (0.015, 0.09, 0.02), center=(sgn * 0.482, fs(49.6), 1.322))    # at the aft end of the arm rest, level with its top
        ih = obj_from_bm(f"INTERIOR.door_inner_handle_{side}", bm, ctx.col, pivot=(sgn * 0.482, fs(48.0), 1.322), mat=M["chrome"], smooth=False)
        parent_keep(ih, door)
        ctx.tag(ih, "INTERIOR", "Inside door handle (OPEN, CLOSE, LOCK)", "مقبض الباب الداخلي (OPEN ،CLOSE ،LOCK)", status="poh", ref="p.7-15",
                note="Three positions: spring-loaded to CLOSE (up); rotated forward to LOCK it lies flush with the arm rest; rotated aft it opens the door (POH p.7-15)")
    # baggage shelf / rear bulkhead
    top = wl(51.5) - 0.03          # lower edge of the rear window at this station
    foot = floor_z(112) + 0.015    # it stands on the raised baggage floor
    heights = [foot + (top - foot) * i / 8 for i in range(9)]
    half = [max(0.05, fus_half_width_at(112, z) - 0.04) for z in heights]
    outline = [(h, z) for h, z in zip(half, heights)] + [(-h, z) for h, z in zip(reversed(half), reversed(heights))]
    bm = new_bm()
    extrude_profile(bm, outline, Vector((1, 0, 0)), Vector((0, 0, 1)), (0, 0, 0), Vector((0, 1, 0)), fs(112) - 0.01, fs(112) + 0.01, smooth_sides=False)
    bh = obj_from_bm("INTERIOR.baggage_bulkhead", bm, ctx.col, pivot=(0, fs(112), 1.0), mat=M["interior_tan"], smooth=False)
    parent_keep(bh, grp)
    ctx.tag(bh, "INTERIOR", "Rear cabin wall: the aft bulkhead of baggage area 1", "الجدار الخلفي للمقصورة: الحاجز الخلفي لمنطقة الأمتعة 1", status="poh", ref="p.6-7 (Fig 6-3), 7-11",
            note="Baggage area 1 extends from the back of the rear seats (station 82) to the rear cabin wall (approximately station 108); baggage area 2 lies behind it")

def build(ctx):
    """Build the cockpit, then lift it to the cowl-deck height of the corrected fuselage.

    The panel, controls and seats were laid out against a lower cowl deck. The photo-profile puts the
    deck and the pilot's eye about 4 in higher above the floor, so everything that is not fixed to
    the floor is raised by CABIN_LIFT; the floor, pedals and fuel selector stay where they are.
    """
    existing = set(bpy.data.objects)
    build_panel(ctx)
    build_controls(ctx)
    build_seats(ctx)
    groups = set(ctx.groups.values())
    for ob in bpy.data.objects:
        if ob in existing:
            continue
        if ob.name.startswith("_cut_panel"):          # the openings of the panel go up with it
            ob.location.z += CABIN_LIFT
        elif ob.parent in groups and not ob.name.startswith(FLOOR_MOUNTED):
            ob.location.z += CABIN_LIFT
