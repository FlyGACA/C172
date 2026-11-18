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
    keep_sources  statuses of scene/oeth/models/scene_index.json to keep (all by default); every other object of the scene is deleted
    plan      {"pavements": [{"zone", "ring", "holes"}], "islands": [{"ring"}], "buildings": [{"ring", "height"}], "roads": [{"points", "width"}]}
              in the scene frame (x, y): a ground plan laid on the terrain in place of the scene's own (figs/oeth3d.py: the book's open plan); zone "runway" is asphalt
    zscale    heights of the ground (the scene and the far ground) drawn this many times their scale; the recipe's own heights (volumes, paths,
              aircraft, anchors) are given already multiplied
    volumes   [{"name", "ring": [[x, y], ...], "floor": z | {"agl": m}, "ceiling": z, "colour", "alpha", "edge": m, "subtract": [names]}]
              airspace: a prism between floor and ceiling (a floor "agl" follows the ground at each corner), see-through, with its rings drawn as tubes
    paths     ... "dash": [on, off] metres draws the tube in dashes
"""
import argparse
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Vector
from mathutils.geometry import tessellate_polygon

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


def drop_sources(obs, keep):
    """Delete the scene objects whose status (scene_index.json) is not in keep; a mesh carries its index entry's name, or that name and a suffix."""
    index = json.load(open(os.path.join(SCENE, "scene_index.json")))["objects"]
    status = {e["name"]: e.get("status") for e in index}
    names = sorted(status, key=len, reverse=True)
    left, unlisted = [], 0
    for o in obs:
        base = next((n for n in names if o.name == n or o.name.startswith(n + ".") or o.name.startswith(n + "_")), None)
        unlisted += base is None and o.type == "MESH"     # the lights (listed apart in the index) and anything new: left out
        if base is None or status[base] not in keep:
            if o.type == "MESH":
                bpy.data.objects.remove(o, do_unlink=True)
                continue
        left.append(o)
    print(f"render_oeth: kept {len(left)} objects of the scene; {unlisted} meshes not in scene_index.json left out")
    return left


def ground_z(x, y):
    """The height of the ground (the scene, the far ground, the plan) under (x, y): blocks of airspace, their edges and paths are passed through."""
    origin = Vector((x, y, 200000.0))
    for _ in range(50):
        hit, loc, _n, _i, ob, _m = bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(), origin, Vector((0, 0, -1)))
        if not hit:
            return 0.0
        if not ob.name.startswith(("air ", "edge ", "path")):
            return loc.z
        origin = loc - Vector((0, 0, 0.01))
    return 0.0


def _mesh(name, verts, faces, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def flat_poly(name, rings, lift, mat, z=None):
    """A flat polygon (an outer ring and holes) draped on the ground at the height of its first point, lift metres above it."""
    pts = [Vector((x, y, 0.0)) for r in rings for x, y in r]
    z0 = (ground_z(*rings[0][0]) if z is None else z) + lift
    tris = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in r] for r in rings])
    return _mesh(name, [(p.x, p.y, z0) for p in pts], [tuple(t) for t in tris], mat)


def build(name, ring, height, walls, roof):
    """A building: its footprint extruded to height (the walls), with a roof."""
    r = ring[:-1] if ring[0] == ring[-1] else ring
    z0 = min(ground_z(x, y) for x, y in r) - 0.5
    n = len(r)
    verts = [(x, y, z0) for x, y in r] + [(x, y, z0 + 0.5 + height) for x, y in r]
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    ob = _mesh(name, verts, faces, walls)
    tris = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in r]])
    _mesh(name + " roof", [(x, y, z0 + 0.5 + height + 0.05) for x, y in r], [tuple(t) for t in tris], roof)
    return ob


def glass_material(name, colour, alpha):
    """A see-through tint for a block of airspace: transparent, mixed with a little emission of its colour."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hexcol(colour)
    em.inputs["Strength"].default_value = 0.9
    mix.inputs["Fac"].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m


def volumes(vols):
    built = {}
    for v in vols:
        ring = v["ring"][:-1] if v["ring"][0] == v["ring"][-1] else v["ring"]
        n = len(ring)
        fl = v["floor"]
        bottom = [(x, y, ground_z(x, y) + fl["agl"]) if isinstance(fl, dict) else (x, y, fl) for x, y in ring]
        top = [(x, y, v["ceiling"]) for x, y in ring]
        faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        mat = glass_material("air_" + v["name"], v.get("colour", "#1D4ED8"), v.get("alpha", 0.15))
        ob = _mesh("air " + v["name"], bottom + top, faces, mat)
        built[v["name"]] = ob
        for cut in v.get("subtract", []):
            c = built[cut].copy()
            c.data = built[cut].data.copy()
            bpy.context.scene.collection.objects.link(c)
            mod = ob.modifiers.new("cut_" + cut, "BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.object = c
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(c, do_unlink=True)
        if v.get("edge"):
            emat = flat_material("edge_" + v["name"], v.get("edge_colour", v.get("colour", "#1D4ED8")), emission=0.4)
            for k, rng in (("floor", bottom), ("ceiling", top)):
                if k == "floor" and v.get("no_floor_edge"):
                    continue
                pts = [list(p) for p in rng] + [list(rng[0])]
                tube_mat(pts, emat, v["edge"], f"edge {v['name']} {k}")
            if v.get("corner_edges"):                   # a prism with few corners: its upright edges too, so that it reads as a box
                for i, (p, q) in enumerate(zip(bottom, top)):
                    tube_mat([list(p), list(q)], emat, v["edge"] * 0.8, f"edge {v['name']} corner {i}")
    return built


def lay_plan(plan):
    twy = bpy.data.materials["taxi"]
    apron = bpy.data.materials["apron"]
    island = bpy.data.materials["island"]
    walls = bpy.data.materials["walls"]
    roof = flat_material("roof", "#F4F1EA")
    rwy = bpy.data.materials["asphalt"]
    for p in plan.get("pavements", []):
        flat_poly("plan " + p["name"], [p["ring"], *p.get("holes", [])], 0.30, {"apron": apron, "runway": rwy}.get(p["zone"], twy))
    for i, p in enumerate(plan.get("islands", [])):
        flat_poly(f"plan island {i}", [p["ring"]], 0.45, island)
    for b in plan.get("buildings", []):
        build("plan " + b["name"], b["ring"], b["height"], walls, roof)
    for i, rd in enumerate(plan.get("roads", [])):
        pts, w = rd["points"], rd.get("width", 8.0) / 2.0
        for j, (a, c) in enumerate(zip(pts, pts[1:])):
            dx, dy = c[0] - a[0], c[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L * w, dx / L * w
            flat_poly(f"plan road {i}.{j}", [[(a[0] + nx, a[1] + ny), (c[0] + nx, c[1] + ny), (c[0] - nx, c[1] - ny), (a[0] - nx, a[1] - ny)]], 0.25, twy)


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


def tube_mat(points, mat, radius, name):
    """A tube along points with a given material (an edge of a block of airspace)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for p, q in zip(sp.points, points):
        p.co = (q[0], q[1], q[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def dashes(points, on, off):
    """The polyline cut into pieces on metres long with gaps of off metres."""
    out, cur, acc, drawing = [], [list(points[0])], 0.0, True
    for i in range(1, len(points)):
        p, q = Vector(points[i - 1]), Vector(points[i])
        seg = (q - p).length
        t = 0.0
        while seg - t > 1e-6:
            left = (on if drawing else off) - acc
            step = min(left, seg - t)
            t += step
            acc += step
            pt = p.lerp(q, t / seg)
            if drawing:
                cur.append(list(pt))
            if acc >= (on if drawing else off) - 1e-6:
                if drawing:
                    out.append(cur)
                drawing, acc, cur = not drawing, 0.0, [list(pt)]
    if drawing and len(cur) > 1:
        out.append(cur)
    return out


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
    if "keep_sources" in r:
        scene_obs = drop_sources(scene_obs, set(r["keep_sources"]))
    if r.get("restyle", True):
        restyle(scene_obs)
    k = r.get("zscale", 1.0)
    if k != 1.0:                                       # the ground drawn k times its height (the recipe's own heights come multiplied already)
        for o in bpy.data.objects:
            if o.parent is None:
                o.location.z *= k
                o.scale.z *= k
    if "plan" in r:
        bpy.context.view_layer.update()
        lay_plan(r["plan"])
    if "volumes" in r:
        bpy.context.view_layer.update()
        volumes(r["volumes"])
    if r.get("far_ground", True):                      # the terrain ends 20 km out: a sand plane below it carries the desert to the horizon
        bpy.ops.mesh.primitive_plane_add(size=r.get("far_ground_size", 600000), location=(0, 0, r.get("far_ground_z", -6.0)))
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
        if "drape" in p:                               # laid on the ground, drape metres above it (the section line of a map)
            bpy.context.view_layer.update()
            p = {**p, "points": [[x, y, ground_z(x, y) + p["drape"]] for x, y, *_ in p["points"]]}
        if p.get("dash"):
            mat = flat_material(f"path{i}m", p.get("colour", "#1D4ED8"), emission=1.5)
            for j, piece in enumerate(dashes(p["points"], *p["dash"])):
                tube_mat(piece, mat, p.get("radius", 6.0), f"path{i}.{j}")
            continue
        ob, mat = tube(p["points"], p.get("colour", "#1D4ED8"), p.get("radius", 6.0), f"path{i}")
        if p.get("arrows"):
            arrows(p["points"], mat, p["arrows"], p.get("arrow_size", p.get("radius", 6.0) * 5), f"path{i}")
        if p.get("end_arrow"):                          # a head at the end of the path (a wind arrow)
            q0, q1 = Vector(p["points"][-2]), Vector(p["points"][-1])
            size = p.get("arrow_size", p.get("radius", 6.0) * 5)
            u = (q1 - q0).normalized()
            bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=size * 0.55, radius2=0.0, depth=size * 1.6, location=q1 + u * size * 0.8)
            cone = bpy.context.active_object
            cone.name = f"path{i}_head"
            cone.rotation_euler = u.to_track_quat("Z", "Y").to_euler()
            cone.data.materials.append(mat)
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
    cam_d.clip_end = r.get("clip_end", 200000)
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
