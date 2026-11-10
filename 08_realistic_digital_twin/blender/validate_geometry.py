"""Validate spatial invariants in a built Phase 8 Blender scene.

Run with:
  blender -b models/C172N_realistic.blend --python blender/validate_geometry.py

Checks: mesh health, the overall envelope, the published dimensions the model has to reproduce
(span, length, wheel base, track, propeller clearance, tyres on the ground), the attachment of
struts, fairings and gear to their neighbours, and that nothing inside the cabin or the cowl
sticks out through the skin.
"""

import math
import os
import sys

import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c172 import units as U                      # noqa: E402
from c172 import airframe, powerplant            # noqa: E402
from c172.profiles import interp_pchip           # noqa: E402


REQUIRED = {
    "AIRFRAME.fuselage",
    "WING_L.strut", "WING_R.strut",
    "WING_L.root_fairing", "WING_R.root_fairing",
    "GEAR.main_leg_L", "GEAR.main_leg_R",
    "AIRFRAME.step_L", "AIRFRAME.step_R", "AIRFRAME.cabin_vent_L", "AIRFRAME.cabin_vent_R",
}

# Each component must intersect its neighbour, or come within this gap of it (m).
CONTACTS = {
    "WING_L.strut": ("AIRFRAME.fuselage", 0.02),
    "WING_R.strut": ("AIRFRAME.fuselage", 0.02),
    "WING_L.root_fairing": ("AIRFRAME.fuselage", 0.02),
    "WING_R.root_fairing": ("AIRFRAME.fuselage", 0.02),
    "GEAR.main_leg_L": ("AIRFRAME.fuselage", 0.02),
    "GEAR.main_leg_R": ("AIRFRAME.fuselage", 0.02),
    "AIRFRAME.cabin_vent_L": ("WING_L.wing", 0.02),
    "AIRFRAME.cabin_vent_R": ("WING_R.wing", 0.02),
    "AIRFRAME.step_L": ("GEAR.main_leg_L", 0.03),
    "AIRFRAME.step_R": ("GEAR.main_leg_R", 0.03),
    "EMPENNAGE.fin": ("AIRFRAME.fuselage", 0.03),
    "EMPENNAGE.stabilizer": ("AIRFRAME.fuselage", 0.03),
    "POWERPLANT.cowl_lower": ("AIRFRAME.fuselage", 0.02),
    "POWERPLANT.cowl_upper": ("AIRFRAME.fuselage", 0.02),
}

# Safety envelope in Blender world coordinates (metres): +x left wing, -y nose, z up from the ground.
ENVELOPE_MIN = (-5.7, -2.25, -0.05)
ENVELOPE_MAX = (5.7, 6.3, 2.75)

# Existing generator debt, tracked as a ceiling so it cannot silently grow.
DEGENERATE_FACE_BUDGET = {
    "ENGINE.crankcase_L": 56,
    "ENGINE.crankcase_R": 56,
}

# Published dimensions the built model must reproduce: (description, expected m, tolerance m).
DIMENSIONS = {
    "wingspan": ("POH Fig 1-1: 35 ft 10 in over the wing tips, lights excluded", U.ref("wingspan_m"), 0.02),
    "length": ("POH Fig 1-1: 26 ft 11 in, spinner tip to rudder", U.ref("length_m"), 0.03),
    "wheel_base": ("65 in", U.ref("wheel_base_m"), 0.01),
    "track": ("8 ft 3½ in", U.ref("gear_track_m"), 0.01),
    "prop_clearance": ("11¾ in under the propeller disc", U.ref("prop_clearance_m"), 0.015),
    "tail_span": ("11 ft 4 in over the elevator horns", U.ref("h_tail_span_m"), 0.02),
}

# Parts that live inside the cabin or under the cowl must stay inside the skin. Everything is checked
# except the exterior assemblies and the parts that are mounted outside on purpose.
EXTERIOR_PREFIXES = ("AIRFRAME.", "WING_", "EMPENNAGE.", "GEAR.", "POWERPLANT.", "PITOT_STATIC.", "_")
MOUNTED_OUTSIDE = {
    "ELECTRICAL.tail_nav_light", "ELECTRICAL.beacon", "ELECTRICAL.adf_sense_wire", "ELECTRICAL.comm_antenna",
    "ELECTRICAL.elt_antenna", "FUEL.vent_line", "ENGINE.exhaust_tailpipe",
}
SKIN_TOLERANCE = 0.003


def evaluated_mesh(ob, depsgraph):
    evaluated = ob.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    matrix = evaluated.matrix_world
    vertices = [matrix @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(poly.vertices) for poly in mesh.polygons]
    return evaluated, mesh, matrix, vertices, polygons


def world_bounds(names, depsgraph):
    points = []
    for name in names:
        ob = bpy.data.objects.get(name)
        if ob is None:
            continue
        evaluated, _mesh, _matrix, vertices, _polygons = evaluated_mesh(ob, depsgraph)
        points.extend(vertices)
        evaluated.to_mesh_clear()
    if not points:
        return None
    return [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]


def outside_skin(point):
    """Distance (m, approximate) by which a point lies outside the cowl or fuselage skin; negative
    inside, None beyond either end of the hull. Uses the section tables the skin is lofted from."""
    station = point.y / U.IN + U.FS_ORIGIN
    cowl0, firewall = powerplant.COWL_TABLE[0][0], powerplant.COWL_TABLE[-1][0]
    if station < cowl0 or station > airframe.FUS_END_FS:
        return None
    table = powerplant.COWL_TABLE if station < firewall else airframe.FUS_TABLE
    half_width, z_bottom, z_top, z_centre, n_top, n_bottom = interp_pchip(table, station)
    z = point.z + U.GROUND_Z
    height, n = ((z_top - z_centre), n_top) if z >= z_centre else ((z_centre - z_bottom), n_bottom)
    r = ((abs(point.x) / half_width) ** n + (abs(z - z_centre) / height) ** n) ** (1 / n)
    return (r - 1) * math.hypot(point.x, z - z_centre) / max(r, 1e-6)


def check_dimensions(problems, depsgraph):
    measured = {}
    wings = world_bounds(["WING_L.wing", "WING_R.wing"], depsgraph)
    if wings:
        measured["wingspan"] = wings[0][1] - wings[0][0]
    hull = world_bounds(["POWERPLANT.spinner", "EMPENNAGE.rudder"], depsgraph)
    if hull:
        measured["length"] = hull[1][1] - hull[1][0]
    nose, main_l, main_r = (bpy.data.objects.get(n) for n in ("GEAR.nose_wheel.tyre", "GEAR.main_wheel_L.tyre", "GEAR.main_wheel_R.tyre"))
    if nose and main_l and main_r:
        measured["wheel_base"] = main_l.matrix_world.translation.y - nose.matrix_world.translation.y
        measured["track"] = abs(main_l.matrix_world.translation.x - main_r.matrix_world.translation.x)
        for tyre in (nose, main_l, main_r):
            lowest = world_bounds([tyre.name], depsgraph)[2][0]
            if not -0.02 <= lowest <= 0.005:
                problems.append(f"{tyre.name}: lowest point is {lowest:.3f} m, not on the ground (z = 0)")
    spinner = bpy.data.objects.get("POWERPLANT.spinner")
    if spinner:
        measured["prop_clearance"] = spinner.matrix_world.translation.z - U.PROP_R
    tail = world_bounds(["EMPENNAGE.elevator"], depsgraph)
    if tail:
        measured["tail_span"] = tail[0][1] - tail[0][0]
    for key, (description, expected, tolerance) in DIMENSIONS.items():
        if key not in measured:
            problems.append(f"dimension {key}: could not be measured")
        elif abs(measured[key] - expected) > tolerance:
            problems.append(f"dimension {key}: {measured[key]:.3f} m, expected {expected:.3f} m ± {tolerance} ({description})")
        else:
            print(f"dimension {key}: {measured[key]:.3f} m ({description})")
    if powerplant.COWL_TABLE[-1][1:] != airframe.FUS_TABLE[0][1:]:
        problems.append("cowl and fuselage sections differ at the firewall (COWL_TABLE[-1] vs FUS_TABLE[0])")


def main():
    problems = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    missing = sorted(REQUIRED - set(bpy.data.objects.keys()))
    if missing:
        problems.append(f"missing required objects: {missing}")

    all_points = []
    inside_checked = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.hide_render or ob.name.startswith("_"):
            continue
        evaluated, mesh, _matrix, vertices, _polygons = evaluated_mesh(ob, depsgraph)
        all_points.extend(vertices)
        invalid = [vertex.index for vertex in mesh.vertices if not all(math.isfinite(v) for v in vertex.co)]
        if invalid:
            problems.append(f"{ob.name}: {len(invalid)} non-finite vertices")
        degenerate = sum(1 for polygon in mesh.polygons if polygon.area <= 1e-12)
        budget = DEGENERATE_FACE_BUDGET.get(ob.name, 0)
        if degenerate > budget:
            problems.append(f"{ob.name}: {degenerate} degenerate faces (budget {budget})")
        elif degenerate:
            print(f"known mesh debt {ob.name}: {degenerate}/{budget} degenerate faces")
        if not ob.name.startswith(EXTERIOR_PREFIXES) and ob.name not in MOUNTED_OUTSIDE:
            inside_checked += 1
            distances = [d for d in (outside_skin(vertex) for vertex in vertices) if d is not None]
            if len(distances) < len(vertices):
                problems.append(f"{ob.name}: reaches beyond the ends of the hull")
            elif distances and max(distances) > SKIN_TOLERANCE:
                problems.append(f"{ob.name}: sticks {max(distances) * 1000:.0f} mm out through the skin")
        evaluated.to_mesh_clear()
    print(f"skin containment: {inside_checked} interior parts checked")

    if all_points:
        mins = tuple(min(point[i] for point in all_points) for i in range(3))
        maxs = tuple(max(point[i] for point in all_points) for i in range(3))
        for axis, label in enumerate("xyz"):
            if mins[axis] < ENVELOPE_MIN[axis] or maxs[axis] > ENVELOPE_MAX[axis]:
                problems.append(
                    f"aircraft {label} bounds [{mins[axis]:.3f}, {maxs[axis]:.3f}] "
                    f"outside [{ENVELOPE_MIN[axis]:.3f}, {ENVELOPE_MAX[axis]:.3f}]"
                )

    check_dimensions(problems, depsgraph)

    trees = {}

    def tree_of(name):
        if name not in trees:
            evaluated, _mesh, _matrix, vertices, polygons = evaluated_mesh(bpy.data.objects[name], depsgraph)
            trees[name] = (BVHTree.FromPolygons(vertices, polygons, all_triangles=False), vertices)
            evaluated.to_mesh_clear()
        return trees[name]

    for name, (target_name, maximum_gap) in CONTACTS.items():
        if name not in bpy.data.objects or target_name not in bpy.data.objects:
            problems.append(f"{name}: cannot check contact with {target_name} (object missing)")
            continue
        tree, vertices = tree_of(name)
        target_tree, _target_vertices = tree_of(target_name)
        if tree.overlap(target_tree):
            print(f"contact {name} -> {target_name}: surfaces intersect")
            continue
        stride = max(1, len(vertices) // 5000)
        distances = [nearest[3] for nearest in (target_tree.find_nearest(vertex) for vertex in vertices[::stride]) if nearest]
        if not distances:
            problems.append(f"{name}: could not measure contact with {target_name}")
        elif min(distances) > maximum_gap:
            problems.append(f"{name}: detached from {target_name} by {min(distances):.3f} m (limit {maximum_gap:.3f} m)")
        else:
            print(f"contact {name} -> {target_name}: {min(distances):.4f} m")

    for name in ("WING_L.root_fairing", "WING_R.root_fairing"):
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        evaluated = ob.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        normal_matrix = evaluated.matrix_world.to_3x3().inverted().transposed()
        mean_up = sum((normal_matrix @ polygon.normal).normalized().z for polygon in mesh.polygons) / max(1, len(mesh.polygons))
        if mean_up <= 0.1:
            problems.append(f"{name}: exterior normals face down (mean world Z {mean_up:.3f})")
        else:
            print(f"normals {name}: mean world Z {mean_up:.3f}")
        evaluated.to_mesh_clear()

    if problems:
        print(f"Geometry validation failed with {len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"Geometry validation OK: {len(REQUIRED)} critical objects, {len(CONTACTS)} contacts, "
          f"{len(DIMENSIONS)} published dimensions, {inside_checked} interior parts inside the skin")
    return 0


raise SystemExit(main())
