"""Colour plates for the handbook: Cycles renders of the model on a transparent background, with the
places of named points of the aircraft in the picture, for handbook/build_plates.mjs to draw on.

    blender -b 08_realistic_digital_twin/models/C172N_realistic.blend \
        --python 09_book_figures/blender/render_plate.py -- --all            (or --plate <id>, --quick)

Each plate of handbook/plates.json that has a "render" recipe gives handbook/renders/<id>.png and
handbook/renders/<id>.anchors.json. A recipe works in the build frame of the model (metres; x to the left
wing, y aft, z up; see 08_realistic_digital_twin/blender/c172/units.py): the aircraft is taken out of its
attitude on the ground first, so a side view is a view of level flight and the panel stands upright.

    camera   {"view": "side"|"panel", "target": [x, y, z], "width": metres across the picture,
              "azimuth": deg, "elevation": deg}      side: from the right, nose to the right of the picture;
                                                      panel: from the cabin, square on to the instrument panel
    show     only these parts are drawn (glob patterns on part names); hide: these are left out. Parts of detail
             level 1 and 2 (what lies under the skin, fasteners) are never drawn unless "detail": true
    pitch    {"deg": nose up, "about": [x, y, z]}: the aircraft is turned about that point (level flight: 3 degrees,
             which brings the fuselage reference line level)
    panel_window  [x0, x1, z0, z1]: only the openings of the panel inside this window are cut (the other instruments
                  are not drawn, and their holes would show the cabin behind); panel_extend [up, down] metres: the
                  panel plate is made taller, so that a picture of a few instruments is all panel
    pose     what the instruments show: {"ASI": kt, "ALT": ft, "VSI": ft/min, "TACH": rpm, "heading": deg, ...}
    propeller "disc": the blades give way to a faint disc, as the eye sees a turning propeller
    light    "outdoor" | "panel" | "instrument"
    anchors  {name: [x, y, z] | {"fs": in, "bl": in, "wl": in} | {"part": id, "at": [u, v, w]} |
              {"from": anchor, "add": [dx, dy, dz]} | {"dial": instrument, "angle": deg, "radius": fraction}}:
             a point is in the build frame of the aircraft (turned with it by "pitch"); u, v, w are fractions of the
             part's bounding box along x, y, z; "from"/"add" is an offset in the picture's own frame (z up, whatever
             the pitch); "dial" is a point on the face of an instrument, angle clockwise from 12 o'clock as the pilot
             sees it, radius as a fraction of the dial's radius
"""
import argparse
import fnmatch
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TWIN = os.path.join(ROOT, "08_realistic_digital_twin")
sys.path.insert(0, os.path.join(TWIN, "blender"))
from c172 import units as U                              # noqa: E402
from c172.dials import DATA, value_to_angle             # noqa: E402

PLATES = os.path.join(os.path.dirname(HERE), "handbook")


def level_the_aircraft():
    """Undo the attitude at rest that build.py gave the saved scene: back to the build frame."""
    pivot_y, pivot_z = U.fs(U.GROUND_PIVOT_FS), U.wl(-U.GROUND_DROP_IN)
    at_rest = (Matrix.Translation((0, pivot_y, 0)) @ Matrix.Rotation(-math.radians(U.GROUND_PITCH_DEG), 4, "X")
               @ Matrix.Translation((0, -pivot_y, -pivot_z)))
    undo = at_rest.inverted()
    for ob in bpy.data.objects:
        if ob.parent is None:
            ob.matrix_world = undo @ ob.matrix_world
    bpy.context.view_layer.update()


PITCH = Matrix.Identity(4)           # what "pitch" did to the aircraft: points given in its own frame are turned the same way
ANCHORS = {}


def turn_aircraft(deg, about):
    """Nose up by deg about a point (build frame): every root object, so the cutters stay where they were."""
    global PITCH
    about = Vector(about)
    PITCH = Matrix.Translation(about) @ Matrix.Rotation(-math.radians(deg), 4, "X") @ Matrix.Translation(-about)
    for ob in bpy.data.objects:
        if ob.parent is None:
            ob.matrix_world = PITCH @ ob.matrix_world
    bpy.context.view_layer.update()


def dial_point(spec):
    """A point on the face of an instrument, in the build frame (before the pitch)."""
    face = bpy.data.objects[f"PANEL.{spec['dial']}.face"] if f"PANEL.{spec['dial']}.face" in bpy.data.objects else bpy.data.objects[f"PANEL.{spec['dial']}.bezel"]
    centre = face.matrix_world.translation.copy()
    bezel = bpy.data.objects[f"PANEL.{spec['dial']}.bezel"]
    deps = bpy.context.evaluated_depsgraph_get()
    corners = [bezel.evaluated_get(deps).matrix_world @ Vector(c) for c in bezel.evaluated_get(deps).bound_box]
    radius = 0.5 * (max(c.x for c in corners) - min(c.x for c in corners)) - 0.007            # the dial: inside the moulded rim
    a = math.radians(spec["angle"]); rho = radius * 0.984 * spec.get("radius", 1.0)           # the drawn dial stops at 0.984 of the opening
    return Vector((centre.x - rho * math.sin(a), centre.y, centre.z + rho * math.cos(a)))


def point(spec):
    """A point of a recipe, in the build frame (turned with the aircraft by the pitch)."""
    if isinstance(spec, dict) and "from" in spec:
        return ANCHORS[spec["from"]] + Vector(spec["add"])
    if isinstance(spec, dict) and "dial" in spec:
        return dial_point(spec)
    if isinstance(spec, dict) and "part" in spec:
        ob = bpy.data.objects[spec["part"]]
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        corners = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
        low = Vector([min(c[i] for c in corners) for i in range(3)]); high = Vector([max(c[i] for c in corners) for i in range(3)])
        at = spec.get("at", [0.5, 0.5, 0.5])
        return Vector([low[i] + (high[i] - low[i]) * at[i] for i in range(3)])
    if isinstance(spec, dict):
        return PITCH @ Vector((spec.get("bl", 0.0) * U.IN, U.fs(spec["fs"]), U.wl(spec["wl"])))
    return PITCH @ Vector(spec)


def choose_parts(recipe):
    show, hide = recipe.get("show"), recipe.get("hide", [])
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if ob.get("detail", 0) > 0 and not recipe.get("detail"):
            ob.hide_render = True
        if show is not None and not any(fnmatch.fnmatchcase(ob.name, p) for p in show):
            ob.hide_render = True
        if any(fnmatch.fnmatchcase(ob.name, p) for p in hide):
            ob.hide_render = True


def trim_panel_openings(window):
    """Keep only the openings of the panel, and the screws of the instruments, that lie inside window = [x0, x1, z0, z1]."""
    for name in ("_cut_panel_openings", "PANEL.instrument_screws"):
        trim_loose_parts(bpy.data.objects.get(name), window)


def trim_loose_parts(cutter, window):
    import bmesh
    if cutter is None:
        return
    bm = bmesh.new(); bm.from_mesh(cutter.data)
    seen, drop = set(), []
    for start in bm.verts:
        if start.index in seen:
            continue
        stack, comp = [start], []
        seen.add(start.index)
        while stack:
            v = stack.pop(); comp.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w.index not in seen:
                    seen.add(w.index); stack.append(w)
        centre = sum((cutter.matrix_world @ v.co for v in comp), Vector()) / len(comp)
        if not (window[0] <= centre.x <= window[1] and window[2] <= centre.z <= window[3]):
            drop += comp
    bmesh.ops.delete(bm, geom=drop, context="VERTS")
    bm.to_mesh(cutter.data); bm.free(); cutter.data.update()


def extend_panel(up, down):
    """Make the panel plate taller: its top edge up by `up` metres, its bottom edge down by `down`. The texture of its
    two faces is laid again from where each point now lies (the build maps them from x and z in metres, before the cabin
    was lifted by CABIN_LIFT)."""
    panel = bpy.data.objects.get("PANEL.upper_panel")
    if panel is None:
        return
    me = panel.data
    zs = [(panel.matrix_world @ v.co).z for v in me.vertices]
    mid = 0.5 * (min(zs) + max(zs))
    inverse = panel.matrix_world.inverted().to_3x3()
    for v, z in zip(me.vertices, zs):
        v.co += inverse @ Vector((0.0, 0.0, up if z > mid else -down))
    me.update()
    uv = me.uv_layers.active
    for poly in me.polygons:
        if abs((panel.matrix_world.to_3x3() @ poly.normal).y) > 0.5:
            for i in poly.loop_indices:
                p = panel.matrix_world @ me.vertices[me.loops[i].vertex_index].co
                uv.data[i].uv = (0.5 + p.x, 0.5 + p.z - 0.10)


def finer_panel_grain(factor, strength):
    """The wrinkle finish is a tile made for the cabin seen from a seat: in a close-up it looks like bark. Finer and
    flatter."""
    mat = bpy.data.materials.get("panel_grey")
    if mat is None or not mat.use_nodes:
        return
    for node in mat.node_tree.nodes:
        if node.type == "MAPPING":
            scale = node.inputs["Scale"].default_value
            node.inputs["Scale"].default_value = (scale[0] * factor, scale[1] * factor, 1.0)
        elif node.type == "NORMAL_MAP":
            node.inputs["Strength"].default_value = strength


def clear_instrument_glass():
    """Instrument glass as the eye sees it: clear, with the faint reflection of a surface of glass (Fresnel), not the
    pale veil of the viewer's alpha-blended glass."""
    mat = bpy.data.materials.new("plate_instrument_glass"); mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    fres = nt.nodes.new("ShaderNodeFresnel"); fres.inputs["IOR"].default_value = 1.45
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy"); gloss.inputs["Roughness"].default_value = 0.32        # a soft sheen: a mirror would show the edge of a lamp
    gloss.inputs["Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fres.outputs["Fac"], mix.inputs[0]); nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(gloss.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith("PANEL.") and ob.name.endswith(".glass"):
            ob.data.materials.clear(); ob.data.materials.append(mat)


def pose(readings):
    """Turn the pointers, the card of the directional indicator and the horizon to the readings given."""
    with open(DATA, encoding="utf-8") as f:
        specs = json.load(f)["instruments"]
    alt = readings.get("ALT", 0.0)
    special = {"ALT_100": (alt % 1000.0) * 0.36, "ALT_1000": (alt % 10000.0) * 0.036, "ALT_10000": alt * 0.0036,
               "TC": readings.get("turn", 0.0) * 20.0,
               "CLOCK_H": (readings.get("clock", [10, 10])[0] % 12 + readings.get("clock", [10, 10])[1] / 60.0) * 30.0,
               "CLOCK_M": readings.get("clock", [10, 10])[1] * 6.0}
    for ob in bpy.data.objects:
        kind = ob.get("needle")
        if not kind:
            continue
        if kind in special:
            angle = special[kind]
        elif kind in specs and kind in readings:
            angle = value_to_angle(specs[kind], readings[kind])
        else:
            continue
        ob.rotation_euler = (0.0, -math.radians(angle), 0.0)        # clockwise as the pilot sees it
    card = bpy.data.objects.get("PANEL.DG.card")
    if card is not None and "heading" in readings:
        card.rotation_euler = (0.0, math.radians(readings["heading"]), 0.0)
    ball = bpy.data.objects.get("PANEL.AI.ball")
    if ball is not None and ("pitch" in readings or "bank" in readings):
        ball.rotation_euler = (0.0, math.radians(readings.get("bank", 0.0)), 0.0)
        ball.location.z -= max(-20.0, min(20.0, readings.get("pitch", 0.0))) * 0.0005
    bpy.context.view_layer.update()


def propeller_disc():
    """The blades give way to a thin disc that lets most of the light through."""
    prop = bpy.data.objects.get("POWERPLANT.propeller")
    if prop is None:
        return
    ev = prop.evaluated_get(bpy.context.evaluated_depsgraph_get())
    corners = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    radius = 0.5 * max(max(c.x for c in corners) - min(c.x for c in corners), max(c.z for c in corners) - min(c.z for c in corners))
    centre = prop.matrix_world.translation.copy()
    prop.hide_render = True
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=0.010, location=centre, rotation=(math.radians(90), 0, 0))
    disc = bpy.context.active_object; disc.name = "_propeller_disc"
    mat = bpy.data.materials.new("_propeller_disc"); mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.10, 0.10, 0.11, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Alpha"].default_value = 0.13
    disc.data.materials.append(mat)
    disc.visible_shadow = False


def use_textures(folder):
    """Finer copies of the dial and panel artwork, where a plate looks at an instrument from close by."""
    if not folder or not os.path.isdir(folder):
        return
    for img in bpy.data.images:
        name = os.path.basename(img.filepath or "")
        fine = os.path.join(folder, name)
        if name and os.path.exists(fine):
            img.filepath = fine
            img.reload()


def area_light(name, location, target, energy, size, colour=(1.0, 0.98, 0.95)):
    light = bpy.data.lights.new(name, "AREA"); light.energy = energy; light.size = size; light.color = colour
    ob = bpy.data.objects.new(name, light); bpy.context.scene.collection.objects.link(ob)
    ob.location = location
    ob.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    return ob


def lights(kind, target):
    sc = bpy.context.scene
    world = sc.world or bpy.data.worlds.new("World"); sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    bg = nt.nodes.new("ShaderNodeBackground"); out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    tx, ty, tz = target
    if kind == "outdoor":
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(os.path.join(TWIN, "assets", "hdri", "sky.hdr"), check_existing=True)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
        sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0; sun.angle = math.radians(2.0)
        so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
        so.rotation_euler = (math.radians(50), 0, math.radians(215))          # high, from ahead of the camera's side
        area_light("fill", (tx - 14, ty - 6, tz + 5), target, 900.0, 12.0, (0.92, 0.96, 1.0))     # opens the shade under the wing
    else:
        bg.inputs["Color"].default_value = (0.55, 0.60, 0.68, 1.0); bg.inputs["Strength"].default_value = 0.22 if kind == "panel" else 0.30
        reach = 0.55 if kind == "panel" else 0.42
        area_light("key", (tx + 0.10, ty + reach, tz + reach * 0.85), target, 9.0 if kind == "panel" else 5.0, 0.55)
        area_light("fill", (tx + 0.28, ty + reach * 0.9, tz - 0.08), target, 2.2 if kind == "panel" else 1.4, 0.5, (0.90, 0.95, 1.0))


def camera(recipe, size):
    cam = bpy.data.cameras.new("plate"); ob = bpy.data.objects.new("plate", cam)
    bpy.context.scene.collection.objects.link(ob); bpy.context.scene.camera = ob
    spec = recipe["camera"]
    target = Vector(spec["target"])
    cam.type = "ORTHO"; cam.ortho_scale = spec["width"]; cam.clip_start = 0.01; cam.clip_end = 200.0
    az, el = math.radians(spec.get("azimuth", 0.0)), math.radians(spec.get("elevation", 0.0))
    if spec["view"] == "side":          # from the right of the aircraft: azimuth swings the camera toward the nose
        away = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), math.sin(el)))
        distance = 40.0
    else:                               # from the cabin, looking forward at the panel
        away = Vector((math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)))
        distance = spec.get("distance", 0.20)
    ob.location = target + away * distance
    ob.rotation_euler = (-away).to_track_quat("-Z", "Y").to_euler()
    return ob


def render(plate, quick, textures):
    global PITCH
    bpy.ops.wm.revert_mainfile()
    PITCH = Matrix.Identity(4); ANCHORS.clear()
    recipe = plate["render"]
    sc = bpy.context.scene
    level_the_aircraft()
    choose_parts(recipe)
    if recipe.get("panel_window"):
        trim_panel_openings(recipe["panel_window"])
    if recipe.get("panel_extend"):
        extend_panel(*recipe["panel_extend"])
    if recipe.get("panel_grain"):
        finer_panel_grain(*recipe["panel_grain"])
    if recipe.get("instrument_glass") == "clear":
        clear_instrument_glass()
    if recipe.get("pitch"):
        turn_aircraft(recipe["pitch"]["deg"], recipe["pitch"]["about"])
    if recipe.get("pose"):
        pose(recipe["pose"])
    prop = recipe.get("propeller")
    if prop == "disc":
        propeller_disc()
    elif isinstance(prop, dict) and "turn" in prop:         # the blades stopped at an angle: seen from the side they are then a blade, not a stub
        blade = bpy.data.objects.get("POWERPLANT.propeller")
        if blade is not None:
            blade.rotation_mode = "XYZ"
            blade.rotation_euler = (0.0, math.radians(prop["turn"]), 0.0) if blade.parent is None else blade.rotation_euler
            if blade.parent is not None:
                blade.matrix_world = Matrix.Translation(blade.matrix_world.translation) @ Matrix.Rotation(math.radians(prop["turn"]), 4, "Y") @ blade.matrix_world.to_3x3().to_4x4()
            bpy.context.view_layer.update()
    if recipe.get("fine_textures"):
        use_textures(textures)
    width, height = recipe.get("size", [1920, 1080])
    cam = camera(recipe, (width, height))
    lights(recipe.get("light", "outdoor"), recipe["camera"]["target"])
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24 if quick else recipe.get("samples", 128)
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = (width // 2, height // 2) if quick else (width, height)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = recipe.get("look", "AgX - Medium High Contrast")
    sc.view_settings.exposure = recipe.get("exposure", 0.0)
    out = os.path.join(PLATES, "renders")
    os.makedirs(out, exist_ok=True)
    sc.render.filepath = os.path.join(out, plate["id"] + ".png")
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    anchors = {}
    for name, spec in recipe.get("anchors", {}).items():
        ANCHORS[name] = point(spec)
        u, v, depth = world_to_camera_view(sc, cam, ANCHORS[name])
        anchors[name] = [round(u, 5), round(1.0 - v, 5)]                 # fractions of the picture, from its top left
    with open(os.path.join(out, plate["id"] + ".anchors.json"), "w", encoding="utf-8") as f:
        json.dump({"id": plate["id"], "size": [width, height], "anchors": anchors}, f, indent=1)
        f.write("\n")
    print("plate", plate["id"], "rendered", "(quick)" if quick else "")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", default=None); ap.add_argument("--all", action="store_true")
    ap.add_argument("--quick", action="store_true", help="half size and few samples, for choosing a camera")
    ap.add_argument("--textures", default=os.path.join(PLATES, "cache"), help="folder with finer dials.png and panel_misc.png (handbook/fine_textures.py)")
    a = ap.parse_args(argv)
    with open(os.path.join(PLATES, "plates.json"), encoding="utf-8") as f:
        plates = [p for p in json.load(f)["plates"] if "render" in p]
    chosen = plates if a.all else [p for p in plates if p["id"] == a.plate]
    if not chosen:
        raise SystemExit(f"no plate to render: {a.plate!r} (plates with a render recipe: {[p['id'] for p in plates]})")
    for plate in chosen:
        render(plate, a.quick, a.textures)


main()
