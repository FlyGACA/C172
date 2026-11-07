"""Validate spatial invariants in a built Phase 8 Blender scene.

Run with:
  blender -b models/C172N_realistic.blend --python blender/validate_geometry.py
"""

import math
import sys

import bpy
from mathutils.bvhtree import BVHTree


REQUIRED = {
    "AIRFRAME.fuselage",
    "WING_L.strut", "WING_R.strut",
    "WING_L.root_fairing", "WING_R.root_fairing",
    "GEAR.main_leg_L", "GEAR.main_leg_R",
    "AIRFRAME.step_L", "AIRFRAME.cabin_vent_L", "AIRFRAME.cabin_vent_R",
}

# Each component must meet or penetrate the fuselage skin by no more than this gap.
CONTACTS = {
    "WING_L.strut": 0.08,
    "WING_R.strut": 0.08,
    "WING_L.root_fairing": 0.08,
    "WING_R.root_fairing": 0.08,
    "GEAR.main_leg_L": 0.08,
    "GEAR.main_leg_R": 0.08,
    "AIRFRAME.step_L": 0.08,
    "AIRFRAME.cabin_vent_L": 0.08,
    "AIRFRAME.cabin_vent_R": 0.08,
}

# Generous safety envelope in Blender world coordinates (metres).
ENVELOPE_MIN = (-5.7, -2.1, -0.15)
ENVELOPE_MAX = (5.7, 7.4, 3.0)

# Existing generator debt, tracked as a ceiling so it cannot silently grow.
DEGENERATE_FACE_BUDGET = {
    "ENGINE.crankcase_L": 56,
    "ENGINE.crankcase_R": 56,
    "POWERPLANT.cowl_lower": 1,
}


def evaluated_mesh(ob, depsgraph):
    evaluated = ob.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    matrix = evaluated.matrix_world
    vertices = [matrix @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(poly.vertices) for poly in mesh.polygons]
    return evaluated, mesh, matrix, vertices, polygons


def main():
    problems = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    missing = sorted(REQUIRED - set(bpy.data.objects.keys()))
    if missing:
        problems.append(f"missing required objects: {missing}")

    all_points = []
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
        evaluated.to_mesh_clear()

    if all_points:
        mins = tuple(min(point[i] for point in all_points) for i in range(3))
        maxs = tuple(max(point[i] for point in all_points) for i in range(3))
        for axis, label in enumerate("xyz"):
            if mins[axis] < ENVELOPE_MIN[axis] or maxs[axis] > ENVELOPE_MAX[axis]:
                problems.append(
                    f"aircraft {label} bounds [{mins[axis]:.3f}, {maxs[axis]:.3f}] "
                    f"outside [{ENVELOPE_MIN[axis]:.3f}, {ENVELOPE_MAX[axis]:.3f}]"
                )

    fuselage = bpy.data.objects.get("AIRFRAME.fuselage")
    if fuselage:
        fus_eval, fus_mesh, _matrix, fus_vertices, fus_polygons = evaluated_mesh(fuselage, depsgraph)
        tree = BVHTree.FromPolygons(fus_vertices, fus_polygons, all_triangles=False)
        for name, maximum_gap in CONTACTS.items():
            ob = bpy.data.objects.get(name)
            if not ob:
                continue
            evaluated, _mesh, _matrix, vertices, _polygons = evaluated_mesh(ob, depsgraph)
            stride = max(1, len(vertices) // 5000)
            distances = []
            for vertex in vertices[::stride]:
                nearest = tree.find_nearest(vertex)
                if nearest:
                    distances.append(nearest[3])
            if not distances:
                problems.append(f"{name}: could not measure fuselage contact")
            elif min(distances) > maximum_gap:
                problems.append(f"{name}: detached from fuselage by {min(distances):.3f} m (limit {maximum_gap:.3f} m)")
            else:
                print(f"contact {name}: {min(distances):.4f} m")
            evaluated.to_mesh_clear()
        fus_eval.to_mesh_clear()

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
    print(f"Geometry validation OK: {len(REQUIRED)} critical objects, {len(CONTACTS)} skin contacts")
    return 0


raise SystemExit(main())
