"""Book renders of Thumamah (OETH) from the 3D scene of the saudi-airspace repository, with the C172 model where a view needs it.

    blender -b --factory-startup --python 09_book_figures/blender/render_oeth.py -- --recipe <file.json> [--quick]

The scene is scene/oeth/models/OETH_scene_high.glb and OETH_airspace.glb of saudi-airspace (frame: x east, y north, z up, metres,
origin at the AIP aerodrome reference point, z = 0 at 570 m AMSL). A recipe (JSON) gives:
    id        the picture's name: handbook/renders/<id>.png and <id>.anchors.json
    camera    {"at": [x, y, z], "look": [x, y, z], "lens": mm} or {"ortho": metres across, ...}
    size      [w, h] pixels; samples; sun {"elevation": deg, "azimuth": deg}
    airspace  names (or prefixes) of objects of OETH_airspace.glb to show (none by default)
    hide      name prefixes of scene objects to leave out
    aircraft  [{"at": [x, y, z], "heading": deg true, "pitch": deg, "bank": deg, "scale": 1}] copies of the C172 model (C172N_realistic_medium.glb)
    anchors   {name: [x, y, z] | {"object": name, "at": [u, v, w]}} projected into the picture as fractions (0..1) of its width and height
    tint      {"object prefix": "#RRGGBB"}: paint those objects one flat colour (to show what a callout is about)
    paths     [{"points": [[x, y, z], ...], "colour": "#RRGGBB", "radius": m}] tubes drawn in the scene (a circuit, a track)
"""
import argparse
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
C172 = os.path.dirname(os.path.dirname(HERE))
PLATES = os.path.join(C172, "09_book_figures", "handbook")
SCENE = os.environ.get("OETH_SCENE", "/workspace/saudi-airspace/scene/oeth/models")


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--recipe", required=True)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--anchors-only", action="store_true", help="work out the anchors again without rendering")
    return p.parse_args(a)


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    return [((int(h[i:i + 2], 16) / 255.0) ** 2.2) for i in (0, 2, 4)] + [a]


def flat_material(name, colour, emission=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = hexcol(colour)
    b.inputs["Roughness"].default_value = 0.55
    if emission:
        b.inputs["Emission Color"].default_value = hexcol(colour)
        b.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
    return m


def noisy_material(name, c1, c2, scale=40.0, rough=0.9, detail=6.0, bump=0.0):
    """A ground material: two colours mixed by noise (asphalt, concrete, sand), optionally with a little bump."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    co = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexcol(c1)
    ramp.color_ramp.elements[1].color = hexcol(c2)
    nt.links.new(co.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if bump:
        bm = nt.nodes.new("ShaderNodeBump")
        bm.inputs["Strength"].default_value = bump
        nt.links.new(nz.outputs["Fac"], bm.inputs["Height"])
        nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    return m


def restyle(obs):
    """Book colours for the scene: sand terrain, dark asphalt runway, lighter taxiways and aprons, pale concrete islands, cream buildings."""
    sand = noisy_material("sand", "#B48553", "#D3AC78", scale=0.003, detail=10, bump=0.35)
    rwy = noisy_material("asphalt", "#26292E", "#33373D", scale=0.6, rough=0.9)
    twy = noisy_material("taxi", "#383B41", "#45494F", scale=0.6, rough=0.9)
    apron = noisy_material("apron", "#7E7B74", "#918E86", scale=0.3, rough=0.85)
    island = noisy_material("island", "#C2A577", "#D6BE92", scale=0.05)
    walls = flat_material("walls", "#ECE6DA")
    for o in obs:
        if o.type != "MESH":
            continue
        n = o.name
        mat = None
        if n.startswith("Terrain"):
            mat = sand
        elif n.startswith("RWY") or n.startswith("STOPWAY"):
            mat = rwy
        elif n.startswith("ISLAND"):
            mat = island
        elif n.startswith("MAIN APRON") or "APRON" in n:
            mat = apron
        elif n.isupper() or n.startswith("WEST TAXIWAY") or n.startswith("DIAGONAL") or n.startswith("SOUTH ") or n.startswith("NORTH ") or n.startswith("MID "):
            mat = twy
        elif n.startswith(("Hangar", "Admin", "Office", "Bldg", "Small")):
            mat = walls
        if mat is not None:
            o.data.materials.clear()
            o.data.materials.append(mat)
        if not n.startswith("Terrain"):                 # pavements and paint lie on the flattened terrain: lift them clear of it
            o.location.z += 0.15 if "markings" not in n.lower() and not n.startswith(("Designator", "Stopway chevrons", "Apron pads")) else 0.3


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def world(sun):
    """The sky of the C172 renders (its HDRI) and a sun, as in render_plate.py's outdoor light."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(C172, "08_realistic_digital_twin", "assets", "hdri", "sky.hdr"), check_existing=True)
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = sun.get("sky", 1.0)
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = sun.get("energy", 4.0)
    sun_data.angle = math.radians(1.5)
    sun_ob = bpy.data.objects.new("sun", sun_data)
    bpy.context.scene.collection.objects.link(sun_ob)
    el, az = math.radians(sun.get("elevation", 42)), math.radians(sun.get("azimuth", 135))
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun_ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def bbox_point(ob, at):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector([min(c[i] for c in cs) for i in range(3)])
    hi = Vector([max(c[i] for c in cs) for i in range(3)])
    return Vector([lo[i] + (hi[i] - lo[i]) * at[i] for i in range(3)])


def find(prefix):
    return [o for o in bpy.data.objects if o.name.startswith(prefix)]


def tube(points, colour, radius, name):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for p, q in zip(sp.points, points):
        p.co = (q[0], q[1], q[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    mat = flat_material(name + "m", colour, emission=1.5)
    ob.data.materials.append(mat)
    return ob, mat


def arrows(points, mat, every, size, name):
    """Cones along a path, pointing the way it goes, every `every` metres."""
    acc, nxt = 0.0, every * 0.5
    for i in range(1, len(points)):
        p, q = Vector(points[i - 1]), Vector(points[i])
        seg = (q - p).length
        while acc + seg >= nxt:
            f = (nxt - acc) / seg
            at = p.lerp(q, f)
            bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=size * 0.55, radius2=0.0, depth=size * 1.6, location=at)
            cone = bpy.context.active_object
            cone.name = f"{name}_arrow"
            cone.rotation_euler = (q - p).to_track_quat("Z", "Y").to_euler()
            cone.data.materials.append(mat)
            nxt += every
        acc += seg


def main():
    a = args()
    r = json.load(open(a.recipe))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    scene_obs = import_glb(os.path.join(SCENE, "OETH_scene_high.glb"))
    if r.get("restyle", True):
        restyle(scene_obs)
    if r.get("far_ground", True):                      # the terrain ends 20 km out: a sand plane below it carries the desert to the horizon
        bpy.ops.mesh.primitive_plane_add(size=600000, location=(0, 0, -6.0))
        g = bpy.context.active_object
        g.name = "far ground"
        g.data.materials.append(bpy.data.materials.get("sand"))
    keep_air = r.get("airspace", [])
    air_obs = import_glb(os.path.join(SCENE, "OETH_airspace.glb"))
    for o in air_obs:
        if o.type == "MESH" and not any(o.name.startswith(k) for k in keep_air):
            o.hide_render = True
    for o in scene_obs:
        if any(o.name.startswith(k) for k in r.get("hide", [])):
            o.hide_render = True
    for pre, col in r.get("tint", {}).items():
        mat = flat_material("tint_" + pre, col, emission=0.15)
        for o in find(pre):
            if o.type == "MESH":
                o.data.materials.clear()
                o.data.materials.append(mat)
    for i, ac in enumerate(r.get("aircraft", [])):
        obs = import_glb(os.path.join(C172, "08_realistic_digital_twin", "models", "C172N_realistic_medium.glb"))
        root = bpy.data.objects.new(f"ac{i}", None)
        sc.collection.objects.link(root)
        for o in obs:
            if o.parent is None:
                o.parent = root
        root.location = Vector(ac["at"])
        s = ac.get("scale", 1.0)
        root.scale = (s, s, s)
        # the model's nose points along -y of its build frame after import (glTF: forward is +z, which becomes -y); heading is true, clockwise from north
        root.rotation_euler = Euler((math.radians(ac.get("pitch", 0.0)), math.radians(-ac.get("bank", 0.0)), math.radians(-ac.get("heading", 0.0) + 180.0)), "ZXY")
    for i, p in enumerate(r.get("paths", [])):
        ob, mat = tube(p["points"], p.get("colour", "#1D4ED8"), p.get("radius", 6.0), f"path{i}")
        if p.get("arrows"):
            arrows(p["points"], mat, p["arrows"], p.get("arrow_size", p.get("radius", 6.0) * 5), f"path{i}")
    world(r.get("sun", {}))
    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    c = r["camera"]
    cam.location = Vector(c["at"])
    cam.rotation_euler = (Vector(c["look"]) - Vector(c["at"])).to_track_quat("-Z", "Y").to_euler()
    if "ortho" in c:
        cam_d.type = "ORTHO"
        cam_d.ortho_scale = c["ortho"]
    else:
        cam_d.lens = c.get("lens", 35)
    cam_d.clip_end = 200000
    sc.camera = cam
    w, h = r.get("size", [1920, 1200])
    sc.render.resolution_x, sc.render.resolution_y = (w // 2, h // 2) if a.quick else (w, h)
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 16 if a.quick else r.get("samples", 96)
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = r.get("look", "AgX - Medium High Contrast")
    sc.view_settings.exposure = r.get("exposure", 0.0)
    sc.render.film_transparent = r.get("transparent", False)
    out = os.path.join(PLATES, "renders", r["id"] + ".png")
    sc.render.filepath = out
    sc.render.image_settings.file_format = "PNG"
    bpy.context.view_layer.update()
    anchors = {}
    for k, v in r.get("anchors", {}).items():
        if isinstance(v, dict):
            obs = find(v["object"])
            if not obs:
                continue
            p = bbox_point(obs[0], v.get("at", [0.5, 0.5, 0.5]))
        else:
            p = Vector(v)
        q = world_to_camera_view(sc, cam, p)
        anchors[k] = [round(q.x, 5), round(1.0 - q.y, 5)]
    if not a.anchors_only:
        bpy.ops.render.render(write_still=True)
    with open(os.path.join(PLATES, "renders", r["id"] + ".anchors.json"), "w") as f:
        json.dump({"id": r["id"], "size": [w, h], "anchors": anchors, "curves": {}}, f, indent=1)
    print("rendered", r["id"])


main()
