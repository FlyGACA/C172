"""Technical-illustration renders of the Phase 8 model for book figures (run inside Blender).

    blender -b ../08_realistic_digital_twin/models/C172N_realistic.blend \\
        --python blender/render_figure.py -- --all            (or --spec data/<figure>.render.json)

Photorealism is not the goal. The airframe is drawn in soft neutral tones with ink outlines, the
parts a figure is about are tinted, and the 2D position of every part that will be labelled is
written next to the image so the page layout can draw leader lines without hand placement.

How a picture is made
  1. shading  — a soft studio render in flat tones (no textures, no paint scheme);
  2. drawing data — two exact, unfiltered renders at twice the size: which part covers each pixel
     and how far away it is, and which way the surface faces;
  3. ink — outlines found in that data: a heavy line round the whole aircraft, a medium line
     wherever two parts meet (door, control surfaces, cowl, windows), a fine line at folds and
     where a part hides part of itself. Lines are grown to their width at double size and
     reduced, which makes them smooth;
  4. the ink is laid over the shading.
The lines come from the parts of the model, so they are the same on every run and there are no
stray strokes; nothing is traced by hand.

Outputs, next to each other in --out (default: renders/):
    <id>.png            transparent RGBA illustration
    <id>.anchors.json   image size + one visible anchor point per labelled part (pixel units)
"""
import argparse
import fnmatch
import json
import math
import os
import shutil
import sys
import tempfile
import time

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ink import draw_ink, halve          # noqa: E402  (the line drawing itself: numpy only, tested outside Blender)
from framing import perspective_distance, orthographic_scale          # noqa: E402

GHOST_INK = dict(outer_px=2.6, part_px=1.5, fine_px=1.0, fine_strength=0.0)     # phantom outlines: lighter and thinner
GHOST_VEIL = ("#9DB8D4", 0.10)                                                 # a faint tint where the phantom skin lies

# Neutral drawing tones. Everything that is not highlighted falls into one of these roles.
TONES = {
    "skin":  dict(rgb=(0.90, 0.91, 0.92), rough=0.62),
    "glass": dict(rgb=(0.50, 0.66, 0.78), rough=0.30),
    "dark":  dict(rgb=(0.17, 0.18, 0.20), rough=0.75),
    "metal": dict(rgb=(0.62, 0.64, 0.67), rough=0.5),
    "inner": dict(rgb=(0.72, 0.72, 0.71), rough=0.85),
}
DARK = {"rubber_tyre", "prop_black", "black_plastic", "vinyl_black", "hose_black", "bezel_black", "interior_dark", "steel_dark"}
METAL = {"bare_aluminium", "chrome", "cast_aluminium", "exhaust_steel", "brass"}
GROUND = "_figure_ground"


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


def hex_srgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


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


def resolve(ids, hidden=False):
    """Mesh objects named in ids, plus everything parented below them. An id is
        a part or group name            "ENGINE.piston_1", "WING_L"
        a shell-style pattern           "WING_L.rib_*"
        an assembly                     "@aileron_control"   (every part tagged with that assembly)
        a system                        "system:FUEL"        (every part of that system)
    Parts that are hidden from the render are left out unless `hidden` is set."""
    found = []
    for name in ids:
        ob = bpy.data.objects.get(name)
        if ob is not None:
            matches = [ob]
        elif name.startswith("@"):
            matches = [o for o in bpy.data.objects if name[1:] in str(o.get("assembly", "")).split(",")]
        elif name.startswith("system:"):
            matches = [o for o in bpy.data.objects if o.get("system") == name[7:] and not o.get("group")]
        else:
            matches = [o for o in bpy.data.objects if fnmatch.fnmatchcase(o.name, name)]
        if not matches:
            raise SystemExit(f"render_figure: unknown part id {name!r}")
        for match in matches:
            for candidate in [match, *match.children_recursive]:
                if candidate.type == "MESH" and (hidden or not candidate.hide_render) and candidate not in found:
                    found.append(candidate)
    return found


def mesh_objects(ids):
    return resolve(ids)


def apply_style(spec):
    """Flat tones for everything, a tint for the parts the figure is about. Windows are drawn as
    tinted panes ("glass": "tint", the default) or see-through ("glass": "clear")."""
    glass_alpha = 0.45 if spec.get("glass", "tint") == "clear" else 1.0
    tones = {key: flat_material("fig_" + key, rgb=t["rgb"], rough=t["rough"], alpha=glass_alpha if key == "glass" else 1.0) for key, t in TONES.items()}
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
    sc.cycles.samples = 16 if quick else spec.get("samples", 96)
    sc.cycles.use_denoising = True
    sc.cycles.seed = 0
    width, height = spec["resolution"]
    scale = 0.4 if quick else 1.0
    sc.render.resolution_x, sc.render.resolution_y = int(width * scale), int(height * scale)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.use_freestyle = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    world = bpy.data.worlds.new("figure_studio")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (1, 1, 1, 1)
    background.inputs["Strength"].default_value = spec.get("ambient", 0.58)
    sc.world = world
    key = bpy.data.lights.new("figure_key", "SUN")
    key.energy = spec.get("key", 1.5)
    key.angle = math.radians(spec.get("key_softness_deg", 22))
    key_ob = bpy.data.objects.new("figure_key", key)
    sc.collection.objects.link(key_ob)
    key_ob.rotation_euler = [math.radians(v) for v in spec.get("key_rotation", (48, 0, -38))]
    if spec.get("ground_shadow", True):
        bpy.ops.mesh.primitive_plane_add(size=160, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.name = GROUND
        ground.is_shadow_catcher = True
    if "detail" in spec:                                 # 0 basic model only ... 2 with the fasteners (hidden in the saved scene)
        for ob in bpy.data.objects:
            if ob.type == "MESH" and "detail" in ob and ob.name != GROUND and not ob.get("kit"):      # the hardware kit is shown only when named
                ob.hide_render = ob.hide_viewport = int(ob["detail"]) > int(spec["detail"])
    for ob in resolve(spec.get("hide", [])):
        ob.hide_render = True
        ob.hide_viewport = True
    if spec.get("only"):
        keep = set(resolve(spec["only"])) | set(resolve(spec.get("ghost", [])))
        for ob in bpy.data.objects:
            if ob.type == "MESH" and ob.name != GROUND and ob not in keep:
                ob.hide_render = True
                ob.hide_viewport = True
    apply_cuts(spec)
    # thin parts (cables, pipes, wires) can be drawn thicker than they are, so that they read at the size of the figure
    for number, entry in enumerate(spec.get("grow", [])):
        for ob in resolve(entry["ids"]):
            modifier = ob.modifiers.new(f"figure_grow_{number}", "DISPLACE")
            modifier.strength = entry.get("by", 0.004)
            modifier.mid_level = 0.0
    return sc


def apply_cuts(spec):
    """Cut-aways: {"ids": [...], "box": [[x0, y0, z0], [x1, y1, z1]]} removes what lies inside the box
    from the listed parts (scene coordinates, metres)."""
    for number, cut in enumerate(spec.get("cut", [])):
        low, high = (Vector(v) for v in cut["box"])
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(low + high) / 2)
        cutter = bpy.context.active_object
        cutter.name = f"_figure_cut_{number}"
        cutter.scale = [max(1e-4, abs(h - l)) for l, h in zip(low, high)]
        if "rotation_deg" in cut:
            cutter.rotation_euler = [math.radians(v) for v in cut["rotation_deg"]]
        cutter.hide_render = True
        cutter.display_type = "WIRE"
        for ob in resolve(cut["ids"]):
            modifier = ob.modifiers.new(cutter.name, "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.solver = "EXACT"
            modifier.object = cutter


def scene_bounds(objects):
    """Centre and radius of the sphere round the given objects (evaluated, world space)."""
    deps = bpy.context.evaluated_depsgraph_get()
    corners = []
    for ob in objects:
        ev = ob.evaluated_get(deps)
        corners.extend(ev.matrix_world @ Vector(c) for c in ev.bound_box)
    if not corners:
        raise SystemExit("render_figure: nothing to frame")
    low = Vector([min(c[i] for c in corners) for i in range(3)])
    high = Vector([max(c[i] for c in corners) for i in range(3)])
    centre = (low + high) / 2
    return centre, max((c - centre).length for c in corners)


def setup_camera(sc, spec):
    cam_spec = dict(spec["camera"])
    cam = bpy.data.cameras.new("figure_cam")
    ob = bpy.data.objects.new("figure_cam", cam)
    sc.collection.objects.link(ob)
    sc.camera = ob
    if cam_spec.get("type") == "auto":
        # frame the listed parts (default: everything drawn) from a direction given as azimuth
        # (0 = from ahead, 90 = from the aircraft's left, 180 = from behind) and elevation
        bpy.context.view_layer.update()
        subjects = resolve(cam_spec["of"]) if cam_spec.get("of") else [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render and o.name != GROUND]
        centre, radius = scene_bounds(subjects)
        if "target" in cam_spec:                          # look at a chosen point ...
            centre = Vector(cam_spec["target"])
        azimuth, elevation = math.radians(cam_spec.get("azimuth_deg", 35)), math.radians(cam_spec.get("elevation_deg", 22))
        direction = Vector((math.sin(azimuth) * math.cos(elevation), -math.cos(azimuth) * math.cos(elevation), math.sin(elevation)))
        margin = cam_spec.get("margin", 1.12)
        aspect = sc.render.resolution_x / sc.render.resolution_y
        if cam_spec.get("ortho"):
            cam_spec.update(type="ortho", ortho_scale=orthographic_scale(radius, aspect, margin), pos=centre + direction * (radius * 4 + 5), target=centre)
        else:
            fov = cam_spec.get("fov", 24)
            distance = cam_spec.get("distance", perspective_distance(radius, fov, aspect, margin))      # ... from a chosen distance
            cam_spec.update(type="persp", fov=fov, pos=centre + direction * distance, target=centre)
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
    cam.clip_start = max(0.0005, min(0.05, direction.length * 0.1))          # a rivet drawn alone is looked at from centimetres away
    cam.clip_end = 1000
    return ob


# ----------------------------------------------------------------------------- drawing data and ink

def _data_material(name, mode):
    """Emission material that writes data instead of colour: 'parts' gives (part number, distance
    along the view axis, 1), 'facing' gives the surface normal packed into 0..1."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    emission = tree.nodes.new("ShaderNodeEmission")
    tree.links.new(emission.outputs["Emission"], out.inputs["Surface"])
    if mode == "parts":
        info = tree.nodes.new("ShaderNodeObjectInfo")
        camera = tree.nodes.new("ShaderNodeCameraData")
        combine = tree.nodes.new("ShaderNodeCombineXYZ")
        combine.inputs["Z"].default_value = 1.0
        tree.links.new(info.outputs["Object Index"], combine.inputs["X"])
        tree.links.new(camera.outputs["View Z Depth"], combine.inputs["Y"])
        tree.links.new(combine.outputs["Vector"], emission.inputs["Color"])
    else:
        geometry = tree.nodes.new("ShaderNodeNewGeometry")
        pack = tree.nodes.new("ShaderNodeVectorMath")
        pack.operation = "MULTIPLY_ADD"
        pack.inputs[1].default_value = (0.5, 0.5, 0.5)
        pack.inputs[2].default_value = (0.5, 0.5, 0.5)
        tree.links.new(geometry.outputs["Normal"], pack.inputs[0])
        tree.links.new(pack.outputs["Vector"], emission.inputs["Color"])
    return mat


def _read_float_image(path):
    image = bpy.data.images.load(path)
    width, height = image.size
    buffer = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(buffer)
    bpy.data.images.remove(image)
    return buffer.reshape(height, width, 4)[::-1]          # rows top to bottom


def render_drawing_data(sc, work):
    """Part number, depth and surface direction for every pixel, at twice the picture size.
    One unfiltered sample per pixel, so a pixel belongs to exactly one part."""
    saved = dict(samples=sc.cycles.samples, denoise=sc.cycles.use_denoising, filter=sc.cycles.pixel_filter_type, width=sc.cycles.filter_width,
                 x=sc.render.resolution_x, y=sc.render.resolution_y, bounces=sc.cycles.max_bounces)
    meshes = sorted((ob for ob in bpy.data.objects if ob.type == "MESH" and not ob.hide_render and ob.name != GROUND), key=lambda ob: ob.name)
    for number, ob in enumerate(meshes, 1):
        ob.pass_index = number
    ground = bpy.data.objects.get(GROUND)
    if ground:
        ground.hide_render = True
    sc.cycles.samples = 1
    sc.cycles.use_denoising = False
    sc.cycles.use_adaptive_sampling = False
    sc.cycles.pixel_filter_type = "BOX"
    sc.cycles.filter_width = 0.01
    sc.cycles.max_bounces = 0
    sc.render.resolution_x, sc.render.resolution_y = saved["x"] * 2, saved["y"] * 2
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    sc.render.image_settings.color_mode = "RGBA"
    layers = {}
    for mode in ("parts", "facing"):
        material = _data_material("fig_data_" + mode, mode)
        for ob in meshes:
            for slot in ob.material_slots:
                slot.material = material
        sc.render.filepath = os.path.join(work, mode + ".exr")
        bpy.ops.render.render(write_still=True)
        layers[mode] = _read_float_image(sc.render.filepath)
    sc.cycles.samples, sc.cycles.use_denoising = saved["samples"], saved["denoise"]
    sc.cycles.pixel_filter_type, sc.cycles.filter_width, sc.cycles.max_bounces = saved["filter"], saved["width"], saved["bounces"]
    sc.render.resolution_x, sc.render.resolution_y = saved["x"], saved["y"]
    inside = layers["parts"][..., 3] > 0.5
    part = np.where(inside, np.rint(layers["parts"][..., 0]), 0).astype(np.int32)
    depth = layers["parts"][..., 1]
    facing = layers["facing"][..., :3] * 2 - 1
    return part, depth, facing, inside, [ob.name for ob in meshes]


def compose(shade_path, coverage, colour, out_path, inside=None, shadow_strength=1.0, shadow_feather=0, ghost=None):
    """Lay the ink over the shaded picture and save a straight-alpha PNG. Outside the aircraft the
    shaded picture holds only the cast shadow, which is lightened to `shadow_strength` and faded
    out over `shadow_feather` pixels at the edges of the picture so that it never ends in a cut.
    `ghost` = (line coverage, silhouette, line colour) of the parts drawn as a phantom: a faint veil
    and light outlines over the picture, under the ink of the parts that are really shown."""
    shade = _read_float_image(shade_path)                             # display-referred values, straight alpha
    h = min(shade.shape[0], coverage.shape[0]); w = min(shade.shape[1], coverage.shape[1])
    shade = shade[:h, :w]; ink = coverage[:h, :w, None]
    shade_alpha = shade[..., 3:4]
    if inside is not None:
        solid = halve(inside)[:h, :w, None]
        fade = np.ones((h, w, 1), dtype=np.float32)
        if shadow_feather > 0:
            x = np.minimum(np.arange(w), np.arange(w)[::-1])[None, :, None]
            y = np.minimum(np.arange(h), np.arange(h)[::-1])[:, None, None]
            ramp = np.clip(np.minimum(x, y) / shadow_feather, 0, 1)
            fade = (ramp * ramp * (3 - 2 * ramp)).astype(np.float32)
        shade_alpha = shade_alpha * (solid + (1 - solid) * shadow_strength * fade)
    rgb = shade[..., :3] * shade_alpha                                # premultiplied from here on
    alpha = shade_alpha

    def over(layer_colour, layer_coverage):
        nonlocal rgb, alpha
        rgb = np.array(layer_colour, dtype=np.float32) * layer_coverage + rgb * (1 - layer_coverage)
        alpha = layer_coverage + alpha * (1 - layer_coverage)

    if ghost is not None:
        ghost_lines, ghost_inside, ghost_colour = ghost
        over(hex_srgb(GHOST_VEIL[0]), halve(ghost_inside)[:h, :w, None] * GHOST_VEIL[1])
        over(ghost_colour, ghost_lines[:h, :w, None])
    over(colour, ink)
    picture = np.concatenate([rgb / np.maximum(alpha, 1e-6), alpha], axis=-1)[::-1].astype(np.float32)
    image = bpy.data.images.new("figure_out", w, h, alpha=True)
    image.pixels.foreach_set(np.clip(picture, 0, 1).ravel())
    image.filepath_raw = out_path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def render_ghost(sc, spec, ghosts, work):
    """Outline of the phantom parts alone: (line coverage, silhouette, colour)."""
    others = [ob for ob in bpy.data.objects if ob.type == "MESH" and ob not in ghosts]
    saved = {ob.name: ob.hide_render for ob in others + ghosts}
    for ob in others:
        ob.hide_render = True
    for ob in ghosts:
        ob.hide_render = False
    folder = os.path.join(work, "ghost")
    os.makedirs(folder, exist_ok=True)
    part, depth, facing, inside, names = render_drawing_data(sc, folder)
    lines = draw_ink(part, depth, facing, inside, names, dict(GHOST_INK, **spec.get("ghost_ink", {})), sc.render.resolution_x)
    for ob in others + ghosts:
        ob.hide_render = saved[ob.name]
    base = np.array(hex_srgb(spec.get("ink", {}).get("color", "#1D2733")))
    return lines, inside, tuple(base * 0.5 + 0.5)


# ----------------------------------------------------------------------------- label anchors

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


def export_anchors(sc, cam, spec, path, see_through=()):
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    width, height = sc.render.resolution_x, sc.render.resolution_y
    anchors = {}
    ignore = {GROUND} | {ob.name for ob in see_through}              # a label may point at a part behind a phantom skin
    for entry in spec.get("anchors", []):
        objects = resolve(entry["ids"], hidden=True)
        point = visible_anchor(sc, cam, deps, objects, ignore=ignore - {ob.name for ob in objects}, at=entry.get("at", (0.5, 0.5)))
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


# ----------------------------------------------------------------------------- one figure

def render_one(spec, args):
    sc = setup_scene(spec, args.quick)
    apply_style(spec)
    apply_pose(spec)
    cam = setup_camera(sc, spec)
    bpy.context.view_layer.update()
    stem = os.path.join(args.out, spec["id"] + ("_quick" if args.quick else ""))
    ghosts = resolve(spec.get("ghost", [])) if spec.get("ghost") else []
    if ghosts and spec.get("only"):                                   # a part named in "only" is drawn solid even if its parent is a phantom
        solid = set(resolve(spec["only"]))
        ghosts = [ob for ob in ghosts if ob not in solid]
    export_anchors(sc, cam, spec, stem + ".anchors.json", see_through=ghosts)
    if args.anchors_only:
        return
    started = time.time()
    work = tempfile.mkdtemp(prefix="figure_")
    try:
        for ob in ghosts:                                             # phantom parts are not shaded: they are drawn over the picture
            ob.hide_render = True
        shade_path = os.path.join(work, "shade.png")
        sc.render.filepath = shade_path
        bpy.ops.render.render(write_still=True)
        ink = spec.get("ink", {})
        if ink.get("enabled", True):
            part, depth, facing, inside, names = render_drawing_data(sc, work)
            coverage = draw_ink(part, depth, facing, inside, names, ink, sc.render.resolution_x)
            feather = spec.get("shadow_feather_px", 0) * sc.render.resolution_x / 2400
            ghost = render_ghost(sc, spec, ghosts, work) if ghosts else None
            compose(shade_path, coverage, hex_srgb(ink.get("color", "#1D2733")), stem + ".png", inside, spec.get("shadow_strength", 0.45), feather, ghost)
        else:
            shutil.copyfile(shade_path, stem + ".png")
        if args.keep:
            shutil.copytree(work, stem + "_layers", dirs_exist_ok=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"render_figure: {stem}.png in {time.time() - started:.0f} s")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", help="one render recipe (JSON)")
    parser.add_argument("--all", action="store_true", help="every figure in figures.json that has a render recipe")
    parser.add_argument("--out", default=os.path.join(ROOT, "renders"))
    parser.add_argument("--quick", action="store_true", help="small, noisy preview for choosing a camera")
    parser.add_argument("--anchors-only", action="store_true", help="recompute the label anchors without rendering")
    parser.add_argument("--keep", action="store_true", help="keep the shading and drawing-data layers next to the picture")
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


if __name__ == "__main__":
    main()
