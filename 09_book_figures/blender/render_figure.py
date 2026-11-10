"""Technical-illustration renders of the Phase 8 model for book figures (run inside Blender).

    blender -b ../08_realistic_digital_twin/models/C172N_realistic.blend \
        --python blender/render_figure.py -- --all            (or --spec data/<figure>.render.json)

Photorealism is not the goal. The airframe is drawn in flat neutral tones with ink outlines, the
parts a figure is about are tinted, and the 2D position of every part that will be labelled is
written next to the image so the page layout can draw leader lines without hand placement.

Outputs, next to each other in --out (default: renders/):
    <id>.png            transparent RGBA illustration
    <id>.anchors.json   image size + one visible anchor point per labelled part (pixel units)
"""
import argparse
import json
import math
import os
import sys
import time

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Neutral drawing tones. Everything that is not highlighted falls into one of these roles.
TONES = {
    "skin":  dict(rgb=(0.86, 0.875, 0.89), rough=0.65),
    "glass": dict(rgb=(0.52, 0.67, 0.78), rough=0.2, alpha=0.5),
    "dark":  dict(rgb=(0.16, 0.17, 0.19), rough=0.75),
    "metal": dict(rgb=(0.60, 0.62, 0.65), rough=0.5),
    "inner": dict(rgb=(0.70, 0.70, 0.69), rough=0.85),
}
DARK = {"rubber_tyre", "prop_black", "black_plastic", "vinyl_black", "hose_black", "bezel_black", "interior_dark", "steel_dark"}
METAL = {"bare_aluminium", "chrome", "cast_aluminium", "exhaust_steel", "brass"}


def tone_of(material_name):
    if "glass" in material_name or "lens" in material_name:
        return "glass"
    if material_name in DARK:
        return "dark"
    if material_name.startswith("skin_") or material_name in ("paint_white", "prop_tip_yellow"):
        return "skin"
    if material_name in METAL:
        return "metal"
    return "inner"


def hex_rgb(value):
    value = value.lstrip("#")
    srgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)   # scene-linear


def flat_material(name, rgb, rough=0.6, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    if alpha < 1:
        bsdf.inputs["Alpha"].default_value = alpha
    return mat


def mesh_objects(ids):
    """Objects named in ids plus everything parented below them."""
    found = []
    for name in ids:
        ob = bpy.data.objects.get(name)
        if ob is None:
            raise SystemExit(f"render_figure: unknown part id {name!r}")
        for candidate in [ob, *ob.children_recursive]:
            if candidate.type == "MESH" and not candidate.hide_render and candidate not in found:
                found.append(candidate)
    return found


def apply_style(spec):
    tones = {key: flat_material("fig_" + key, **{"rgb": t["rgb"], "rough": t["rough"], "alpha": t.get("alpha", 1.0)}) for key, t in TONES.items()}
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            for slot in ob.material_slots:
                if slot.material:
                    slot.material = tones[tone_of(slot.material.name)]
    for number, group in enumerate(spec.get("highlights", [])):
        mat = flat_material(f"fig_highlight_{number}", hex_rgb(group["color"]), rough=0.6)
        for ob in mesh_objects(group["ids"]):
            for slot in ob.material_slots:
                slot.material = mat


# The model stores hinge axes in glTF terms (see AXIS_MAP in 08_realistic_digital_twin/blender/build.py).
# Back in Blender's frame: glTF x = Blender x, glTF y = Blender z, glTF z = Blender -y.
HINGE = {"x": ("X", 1), "y": ("Z", 1), "z": ("Y", -1)}


def apply_pose(spec):
    """Deflect hinged parts. Degrees mean what they mean in the web viewer: the same number gives
    the same deflection (for example {"WING_L.flap": 30} is full flap in both)."""
    for name, degrees in spec.get("pose", {}).items():
        ob = bpy.data.objects.get(name)
        if ob is None or "hinge_axis" not in ob:
            raise SystemExit(f"render_figure: {name!r} is not a hinged part of the model")
        axis, flip = HINGE[ob["hinge_axis"]]
        angle = math.radians(degrees) * ob.get("hinge_sign", 1) * flip
        ob.matrix_basis = ob.matrix_basis @ Matrix.Rotation(angle, 4, axis)      # about the part's own hinge line


def setup_scene(spec, quick):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 12 if quick else spec.get("samples", 64)
    sc.cycles.use_denoising = True
    width, height = spec["resolution"]
    scale = 0.4 if quick else 1.0
    sc.render.resolution_x, sc.render.resolution_y = int(width * scale), int(height * scale)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    world = bpy.data.worlds.new("figure_studio")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (1, 1, 1, 1)
    background.inputs["Strength"].default_value = spec.get("ambient", 0.62)
    sc.world = world
    key = bpy.data.lights.new("figure_key", "SUN")
    key.energy = spec.get("key", 1.5)
    key.angle = math.radians(14)
    key_ob = bpy.data.objects.new("figure_key", key)
    sc.collection.objects.link(key_ob)
    key_ob.rotation_euler = [math.radians(v) for v in spec.get("key_rotation", (48, 0, -38))]
    if spec.get("ground_shadow", True):
        bpy.ops.mesh.primitive_plane_add(size=160, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.name = "_figure_ground"
        ground.is_shadow_catcher = True
    for name in spec.get("hide", []):
        for ob in mesh_objects([name]):
            ob.hide_render = True
            ob.hide_viewport = True
    return sc


def setup_camera(sc, spec):
    cam_spec = spec["camera"]
    cam = bpy.data.cameras.new("figure_cam")
    ob = bpy.data.objects.new("figure_cam", cam)
    sc.collection.objects.link(ob)
    sc.camera = ob
    ob.location = cam_spec["pos"]
    direction = Vector(cam_spec["target"]) - Vector(cam_spec["pos"])
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if "roll_deg" in cam_spec:
        ob.rotation_euler.rotate_axis("Z", math.radians(cam_spec["roll_deg"]))
    if cam_spec.get("type", "persp") == "ortho":
        cam.type = "ORTHO"
        cam.ortho_scale = cam_spec["ortho_scale"]
    else:
        cam.angle = math.radians(cam_spec["fov"])
    cam.clip_start = 0.5
    cam.clip_end = 1000
    return ob


def setup_ink(sc, spec, quick):
    """Freestyle outlines: a heavier outer contour and lighter interior lines (thick-thin technique)."""
    ink = spec.get("ink", {})
    if ink.get("enabled", True) is False:
        return
    scale = sc.render.resolution_x / 2400
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    settings = bpy.context.view_layer.freestyle_settings
    settings.crease_angle = math.radians(ink.get("crease_deg", 132))
    for lineset in list(settings.linesets):
        settings.linesets.remove(lineset)
    colour = hex_rgb(ink.get("color", "#1D2733"))

    def lineset(name, thickness, **select):
        ls = settings.linesets.new(name)
        ls.select_silhouette = select.get("silhouette", False)
        ls.select_border = select.get("border", False)
        ls.select_crease = select.get("crease", False)
        ls.select_external_contour = select.get("external", False)
        ls.select_contour = False
        ls.select_material_boundary = select.get("material", False)
        ls.select_edge_mark = False
        style = bpy.data.linestyles.new(name)
        style.color = colour
        style.thickness = max(0.6, thickness * scale)
        style.thickness_position = "CENTER"
        ls.linestyle = style

    lineset("inner", ink.get("inner_px", 2.0), silhouette=True, border=True, crease=True, material=ink.get("material_lines", True))
    lineset("outer", ink.get("outer_px", 4.2), external=True)


def visible_anchor(sc, cam, deps, objects, ignore, at=(0.5, 0.5)):
    """Pick a point that is really visible in the image for a set of objects.

    Every vertex is projected; the ones a camera ray reaches first are kept. The anchor is the
    visible vertex closest to the centre of the visible ones, so a leader line always ends on the part.
    `at` moves the target inside the visible bounding box (0..1 across, 0..1 down) for parts that
    would otherwise be labelled on the centreline, e.g. (0.2, 0.5) for the left side of the elevator.
    """
    cam_pos = cam.matrix_world.translation
    forward = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    ortho = cam.data.type == "ORTHO"
    visible = []
    names = {ob.name for ob in objects}
    for ob in objects:
        ev = ob.evaluated_get(deps)
        mesh = ev.to_mesh()
        step = max(1, len(mesh.vertices) // 1500)
        for index in range(0, len(mesh.vertices), step):
            world = ev.matrix_world @ mesh.vertices[index].co
            ndc = world_to_camera_view(sc, cam, world)
            if not (0 <= ndc.x <= 1 and 0 <= ndc.y <= 1 and ndc.z > 0):
                continue
            if ortho:
                origin = world - forward * ndc.z
                direction = forward
                distance = ndc.z
            else:
                direction = (world - cam_pos)
                distance = direction.length
                direction.normalize()
                origin = cam_pos
            hit, location, _normal, _index, hit_ob, _matrix = sc.ray_cast(deps, origin + direction * 0.4, direction, distance=distance + 0.05)
            while hit and hit_ob.name in ignore:                      # look through helpers (ground plane)
                hit, location, _normal, _index, hit_ob, _matrix = sc.ray_cast(deps, location + direction * 1e-3, direction, distance=distance)
            if hit and (hit_ob.name in names or (location - world).length < 0.012):
                visible.append((ndc.x, 1 - ndc.y))
        ev.to_mesh_clear()
    if not visible:
        return None
    x0, x1 = min(p[0] for p in visible), max(p[0] for p in visible)
    y0, y1 = min(p[1] for p in visible), max(p[1] for p in visible)
    cx = sum(p[0] for p in visible) / len(visible) + (at[0] - 0.5) * (x1 - x0)
    cy = sum(p[1] for p in visible) / len(visible) + (at[1] - 0.5) * (y1 - y0)
    aspect = sc.render.resolution_x / sc.render.resolution_y
    ax, ay = min(visible, key=lambda p: ((p[0] - cx) * aspect) ** 2 + (p[1] - cy) ** 2)
    return dict(x=ax, y=ay, cx=cx, cy=cy, x0=x0, x1=x1, y0=y0, y1=y1, samples=len(visible))


def export_anchors(sc, cam, spec, path):
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    width, height = sc.render.resolution_x, sc.render.resolution_y
    anchors = {}
    for entry in spec.get("anchors", []):
        objects = mesh_objects(entry["ids"])
        point = visible_anchor(sc, cam, deps, objects, ignore={"_figure_ground"}, at=entry.get("at", (0.5, 0.5)))
        first = bpy.data.objects[entry["ids"][0]]
        record = dict(ids=entry["ids"], visible=point is not None, label_en=first.get("label_en", ""), label_ar=first.get("label_ar", ""),
                      system=first.get("system", ""), status=first.get("status", ""))
        if point:
            for key in ("x", "cx", "x0", "x1"):
                record[key] = round(point[key] * width, 1)
            for key in ("y", "cy", "y0", "y1"):
                record[key] = round(point[key] * height, 1)
        anchors[entry["key"]] = record
    payload = dict(figure=spec["id"], image=os.path.basename(path).replace(".anchors.json", ".png"), width=width, height=height,
                   model=os.path.basename(bpy.data.filepath), anchors=anchors)
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=1)
        stream.write("\n")


def render_one(spec, args):
    sc = setup_scene(spec, args.quick)
    apply_style(spec)
    apply_pose(spec)
    cam = setup_camera(sc, spec)
    setup_ink(sc, spec, args.quick)
    bpy.context.view_layer.update()
    stem = os.path.join(args.out, spec["id"] + ("_quick" if args.quick else ""))
    export_anchors(sc, cam, spec, stem + ".anchors.json")
    if not args.anchors_only:
        started = time.time()
        sc.render.filepath = stem + ".png"
        bpy.ops.render.render(write_still=True)
        print(f"render_figure: {stem}.png in {time.time() - started:.0f} s")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", help="one render recipe (JSON)")
    parser.add_argument("--all", action="store_true", help="every figure in figures.json that has a render recipe")
    parser.add_argument("--out", default=os.path.join(ROOT, "renders"))
    parser.add_argument("--quick", action="store_true", help="small, noisy preview for choosing a camera")
    parser.add_argument("--anchors-only", action="store_true", help="recompute the label anchors without rendering")
    args = parser.parse_args(argv)
    if args.all:
        with open(os.path.join(ROOT, "figures.json"), encoding="utf-8") as stream:
            specs = [os.path.join(ROOT, figure["render"]) for figure in json.load(stream)["figures"] if figure.get("render")]
    elif args.spec:
        specs = [args.spec]
    else:
        parser.error("give --spec <recipe.json> or --all")
    os.makedirs(args.out, exist_ok=True)
    for number, path in enumerate(specs):
        if number:
            bpy.ops.wm.revert_mainfile()          # each figure starts from the untouched model
        with open(path, encoding="utf-8") as stream:
            render_one(json.load(stream), args)


main()
