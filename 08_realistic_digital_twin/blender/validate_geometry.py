"""Validate spatial invariants in a built Phase 8 Blender scene.

Run with:
  blender -b models/C172N_realistic.blend --python blender/validate_geometry.py

Checks: mesh health, the overall envelope, the published dimensions the model has to reproduce
(span over the tips and over the strobe lights, length, wheel base, track, tail span, tyres on the
ground, and the maximum height together with the propeller clearance, which the POH gives for the
nose gear depressed), the attachment of struts, fairings, doors and gear to their neighbours, and
that nothing inside the cabin or the cowl sticks out through the skin.
"""

import fnmatch
import math
import os
import sys

import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c172 import units as U                      # noqa: E402
from c172 import airframe, powerplant            # noqa: E402
from c172.profiles import interp_pchip           # noqa: E402
from c172.detail import structure_wing           # noqa: E402


REQUIRED = {
    "AIRFRAME.fuselage",
    "WING_L.strut", "WING_R.strut",
    "WING_L.root_fairing", "WING_R.root_fairing",
    "GEAR.main_leg_L", "GEAR.main_leg_R",
    "AIRFRAME.step_L", "AIRFRAME.step_R", "AIRFRAME.cabin_vent_L", "AIRFRAME.cabin_vent_R",
    "AIRFRAME.door_L", "AIRFRAME.door_R", "AIRFRAME.baggage_door",
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
    "AIRFRAME.door_L": ("AIRFRAME.fuselage", 0.01),
    "AIRFRAME.door_R": ("AIRFRAME.fuselage", 0.01),
    "AIRFRAME.baggage_door": ("AIRFRAME.fuselage", 0.01),
    "WING_L.wing": ("AIRFRAME.fuselage", 0.01),
    "WING_R.wing": ("AIRFRAME.fuselage", 0.01),
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
    "span_strobes": ("POH Fig 1-1: 36 ft, wing span with strobe lights installed", U.ref("wingspan_strobes_m"), 0.02),
    "wingspan": ("type data: 35 ft 10 in over the wing tips, lights excluded", U.ref("wingspan_m"), 0.02),
    "length": ("POH Fig 1-1: 26 ft 11 in, spinner tip to rudder, aircraft on its wheels", U.ref("length_m"), 0.03),
    "wheel_base": ("POH Fig 1-1: 65 in", U.ref("wheel_base_m"), 0.01),
    "track": ("POH Fig 1-1: 8 ft 4½ in", U.ref("gear_track_m"), 0.01),
    "tail_span": ("POH Fig 1-1: 11 ft 4 in over the elevator horns", U.ref("h_tail_span_m"), 0.02),
    "height_nose_depressed": ("POH Fig 1-1: 8 ft 9½ in maximum, with the nose pushed down until the propeller clears the ground by 11¾ in",
                              U.ref("height_m"), 0.03),
}
NOSE_DROP_RANGE = (0.06, 0.12)      # m: how far the nose wheel has to go down for that; a strut and a tyre can give this much

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
    point_x, point_y, z = U.from_ground(tuple(point))          # the tables are in the build frame
    station = point_y / U.IN + U.FS_ORIGIN
    cowl0, firewall = powerplant.COWL_TABLE[0][0], powerplant.COWL_TABLE[-1][0]
    if station < cowl0 - 0.05 or station > airframe.FUS_END_FS + 0.05:
        return None
    station = min(max(station, cowl0), airframe.FUS_END_FS)
    table = powerplant.COWL_TABLE if station < firewall else airframe.FUS_TABLE
    half_width, z_bottom, z_top, z_centre, n_top, n_bottom = interp_pchip(table, station)
    height, n = ((z_top - z_centre), n_top) if z >= z_centre else ((z_centre - z_bottom), n_bottom)
    r = ((abs(point_x) / half_width) ** n + (abs(z - z_centre) / height) ** n) ** (1 / n)
    return (r - 1) * math.hypot(point_x, z - z_centre) / max(r, 1e-6)


def outside_wing(point):
    """Distance (m) by which a point lies outside the wing skin: above the upper surface, below the lower
    one, or beyond the leading or trailing edge of its section. Negative inside."""
    point_x, point_y, point_z = U.from_ground(tuple(point))
    side = 1 if point_x >= 0 else -1
    xabs = min(max(abs(point_x), airframe.WING_ROOT_X), U.SEMISPAN)
    plane = structure_wing.section_plane(xabs, side)
    along, up, _depth = plane.flat((side * xabs, point_y, point_z))
    chord = airframe.wing_chord(xabs)
    section = airframe.wing_airfoil(xabs)
    fraction = min(max(along / chord, 0.0), 1.0)
    upper = airframe.airfoil_y(section, fraction, True) * chord
    lower = airframe.airfoil_y(section, fraction, False) * chord
    return max(up - upper, lower - up, -along, along - chord)


# A run is a pipe, a hose, a cable or a wire. It may touch the parts it joins: those of its own
# assembly, a panel instrument or control, and any part named in its "joins" tag. It may pass through
# the skins, linings and walls in RUN_PASSES, which have an opening for it in the aircraft that the
# model does not cut. It must not cut through anything else: another run, structure, the engine.
RUNS = (
    "FUEL.line_*", "FUEL.primer_line_*", "FUEL.vent_crossover", "WING_?.fuel_line_*", "WING_?.fuel_vent_crossover",
    "BRAKES.line_?", "GEAR.brake_line_feed_?",
    "ELECTRICAL.cable_*", "ELECTRICAL.harness_*", "ELECTRICAL.wire_*", "EMPENNAGE.wiring_fin", "WING_?.wiring_harness",
    "VACUUM.hose_*", "VACUUM.line_*", "VACUUM.overboard_vent",
    "PITOT_STATIC.pitot_line", "PITOT_STATIC.static_line", "WING_?.pitot_line", "WING_?.stall_warning_tube",
    "OIL.hose_*", "OIL.breather_line", "OIL.pressure_gauge_line", "OIL.temperature_sensor",
    "ENGINE.throttle_cable", "ENGINE.mixture_cable", "INDUCTION.carb_heat_cable", "INDUCTION.carb_heat_hose", "PANEL.TACH.drive_cable",
    "CABIN_AIR.*", "WING_?.ventilator_duct",
)
RUN_PASSES = (
    "AIRFRAME.firewall", "AIRFRAME.fuselage", "INTERIOR.cabin_liner", "INTERIOR.headliner", "INTERIOR.floor", "INTERIOR.baggage_bulkhead", "INTERIOR.glareshield",
    "WING_?.root_fairing", "WING_?.wing", "POWERPLANT.cowl_*", "ENGINE.baffles", "ENGINE.baffle_seals", "EMPENNAGE.fin",
    "AIRFRAME.door_post_*",                # a channel: the runs lie in it and leave it through openings in its flanges
)


def matches(name, patterns):
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)


def assemblies(ob):
    return {name for name in str(ob.get("assembly", "")).split(",") if name}


def check_runs(problems, tree_of):
    """Every run against every other part of detail levels 0 and 1."""
    parts = [ob for ob in bpy.data.objects if ob.type == "MESH" and not ob.name.startswith("_") and not ob.get("kit") and int(ob.get("detail", 0)) <= 1]
    runs = [ob for ob in parts if matches(ob.name, RUNS)]
    for run in runs:
        tree, _vertices = tree_of(run.name)
        own = assemblies(run)
        joins = tuple(pattern for pattern in str(run.get("joins", "")).split(",") if pattern)
        for other in parts:
            if other is run or other.name.startswith("PANEL.") or matches(other.name, RUN_PASSES + joins) or own & assemblies(other):
                continue
            if matches(other.name, RUNS) and (other.name < run.name or matches(run.name, tuple(p for p in str(other.get("joins", "")).split(",") if p))):
                continue                                   # each pair of runs once
            if tree.overlap(tree_of(other.name)[0]):
                problems.append(f"{run.name}: cuts through {other.name}")
    return len(runs)


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
    strobes = world_bounds(["WING_L.strobe", "WING_R.strobe"], depsgraph)
    if strobes:
        measured["span_strobes"] = strobes[0][1] - strobes[0][0]
    # POH Fig 1-1 gives the maximum height "with nose gear depressed" and a propeller clearance of 11¾ in.
    # At rest the propeller clears the ground by more: push the nose down about the main wheels until it
    # clears it by 11¾ in and measure the height of the beacon then.
    propeller = bpy.data.objects.get("POWERPLANT.propeller")
    beacon = world_bounds(["ELECTRICAL.beacon"], depsgraph)
    if propeller and beacon and main_l:
        hub = propeller.matrix_world.translation
        main_y = main_l.matrix_world.translation.y
        rest_clearance = hub.z - U.PROP_R
        low, high = 0.0, 0.25
        for _ in range(60):
            phi = (low + high) / 2
            clearance = (hub.y - main_y) * math.sin(phi) + hub.z * math.cos(phi) - U.PROP_R
            low, high = (phi, high) if clearance > U.ref("prop_clearance_m") else (low, phi)
        top_y = bpy.data.objects["ELECTRICAL.beacon"].matrix_world.translation.y
        measured["height_nose_depressed"] = (top_y - main_y) * math.sin(phi) + beacon[2][1] * math.cos(phi)
        drop = U.ref("wheel_base_m") * math.sin(phi)
        print(f"at rest: propeller clearance {rest_clearance / U.IN:.1f} in, height {beacon[2][1] / U.IN:.1f} in; "
              f"nose wheel {drop / U.IN:.1f} in lower for the published 11.75 in")
        if rest_clearance <= U.ref("prop_clearance_m"):
            problems.append(f"propeller clearance at rest is {rest_clearance / U.IN:.1f} in: no more than the 11.75 in the POH gives with the nose gear depressed")
        if not NOSE_DROP_RANGE[0] <= drop <= NOSE_DROP_RANGE[1]:
            problems.append(f"the published propeller clearance needs the nose wheel {drop:.3f} m lower, outside {NOSE_DROP_RANGE}")
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
    wing_checked = 0
    for ob in bpy.data.objects:
        level = int(ob.get("detail", 0))
        if ob.type != "MESH" or ob.name.startswith("_") or (ob.hide_render and level < 2):
            continue                                   # fasteners (level 2) are hidden in the saved scene but checked all the same
        kit = bool(ob.get("kit"))                      # a specimen of standard hardware, kept beside the aircraft
        evaluated, mesh, _matrix, vertices, _polygons = evaluated_mesh(ob, depsgraph)
        if not kit:
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
        if kit:
            evaluated.to_mesh_clear()
            continue
        if level >= 1 and ob.name.startswith("WING_") and not ob.get("outside"):
            # structure and mechanisms in the wing stay under its skin
            wing_checked += 1
            worst = max(outside_wing(vertex) for vertex in vertices)
            if worst > SKIN_TOLERANCE:
                problems.append(f"{ob.name}: sticks {worst * 1000:.0f} mm out through the wing skin")
        if (not ob.name.startswith(EXTERIOR_PREFIXES) and ob.name not in MOUNTED_OUTSIDE) or ob.get("inside") == "fuselage":
            inside_checked += 1
            distances = [d for d in (outside_skin(vertex) for vertex in vertices) if d is not None]
            if len(distances) < len(vertices):
                problems.append(f"{ob.name}: reaches beyond the ends of the hull")
            elif distances and max(distances) > SKIN_TOLERANCE:
                problems.append(f"{ob.name}: sticks {max(distances) * 1000:.0f} mm out through the skin")
        evaluated.to_mesh_clear()
    print(f"skin containment: {inside_checked} parts checked against the fuselage and cowl, {wing_checked} against the wing")

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

    runs_checked = check_runs(problems, tree_of)
    print(f"runs: {runs_checked} pipes, hoses, cables and wires checked against every other part")

    if problems:
        print(f"Geometry validation failed with {len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"Geometry validation OK: {len(REQUIRED)} critical objects, {len(CONTACTS)} contacts, "
          f"{len(DIMENSIONS)} published dimensions, {inside_checked} parts inside the fuselage skin, {wing_checked} inside the wing skin, "
          f"{runs_checked} runs clear of other parts")
    return 0


raise SystemExit(main())
