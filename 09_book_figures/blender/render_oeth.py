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
    plan      {"pavements": [{"zone", "ring", "holes"}], "islands": [{"ring"}], "buildings": [{"ring", "height"}], "roads": [{"points", "width"}], "marks": [{"ring", "colour"}]}
              in the scene frame (x, y): a ground plan laid on the terrain in place of the scene's own (figs/oeth3d.py: the book's open plan); zone "runway" is asphalt
    zscale    heights of the ground (the scene and the far ground) drawn this many times their scale; the recipe's own heights (volumes, paths,
              aircraft, anchors) are given already multiplied
    volumes   [{"name", "ring": [[x, y], ...], "floor": z | {"agl": m}, "ceiling": z, "colour", "alpha", "edge": m, "subtract": [names]}]
              airspace: a prism between floor and ceiling (a floor "agl" follows the ground at each corner), see-through, with its rings drawn as tubes
    paths     ... "dash": [on, off] metres draws the tube in dashes; "shadow": false casts none
    ground_image  {"path", "x0", "x1", "y0", "y1"}: a picture (RGBA, north up) laid on the terrain and the far ground over that box of the scene frame;
              outside it (or where its alpha is 0) the sand
    ink       {"thickness": px, "colour"}: outlines (Freestyle) on the aircraft and the paths only, for the crisp look of an illustration
    haze      {"start": m, "depth": m, "colour", "strength"}: aerial perspective (the mist pass mixed toward the colour in the compositor)
"""
import argparse
import json
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Euler, Vector
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


def ground_material(gi):
    """Sand mixed with a picture of the ground, mapped by world x, y onto [x0, x1] x [y0, y1]."""
    m = bpy.data.materials.new("ground_img")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.95
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    tc.object = bpy.data.objects.get("world origin") or _origin()
    def lin(inp, a, b):
        n = nt.nodes.new("ShaderNodeMapRange")
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, b
        n.clamp = False
        nt.links.new(inp, n.inputs["Value"])
        return n.outputs["Result"]
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(lin(sep.outputs["X"], gi["x0"], gi["x1"]), comb.inputs["X"])
    nt.links.new(lin(sep.outputs["Y"], gi["y0"], gi["y1"]), comb.inputs["Y"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(gi["path"], check_existing=True)
    tex.extension = "CLIP"
    tex.interpolation = "Cubic"
    nt.links.new(comb.outputs["Vector"], tex.inputs["Vector"])
    sand = nt.nodes.new("ShaderNodeRGB")
    sand.outputs[0].default_value = hexcol(gi.get("sand", "#D9C29A"))
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Factor"])
    nt.links.new(sand.outputs[0], mix.inputs[6])
    nt.links.new(tex.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return m


def _origin():
    e = bpy.data.objects.new("world origin", None)
    bpy.context.scene.collection.objects.link(e)
    return e


def ink(cfg, obs):
    """Outlines on the given objects (a collection of their own), as an illustration's line art."""
    sc = bpy.context.scene
    col = bpy.data.collections.new("ink")
    sc.collection.children.link(col)
    for o in obs:
        if o.name not in col.objects:
            col.objects.link(o)
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    for ls in list(fs.linesets):
        fs.linesets.remove(ls)
    ls = fs.linesets.new("ink")
    ls.select_by_collection = True
    ls.collection = col
    ls.select_silhouette, ls.select_border, ls.select_crease = True, True, False
    ls.linestyle.color = hexcol(cfg.get("colour", "#1F2937"))[:3]
    ls.linestyle.thickness = cfg.get("thickness", 1.6)


def haze(cfg):
    """Aerial perspective on the ground only: the render mixed toward a pale colour by distance (the Z pass, from start over depth, up to strength); the sky, which has
    no distance, keeps its own colours."""
    sc = bpy.context.scene
    vl = bpy.context.view_layer
    vl.use_pass_z = True
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rng = nt.nodes.new("CompositorNodeMapRange")
    rng.inputs[1].default_value = cfg.get("start", 4000.0)
    rng.inputs[2].default_value = cfg.get("start", 4000.0) + cfg.get("depth", 20000.0)
    rng.inputs[3].default_value = 0.0
    rng.inputs[4].default_value = cfg.get("strength", 0.7)
    rng.use_clamp = True
    nt.links.new(rl.outputs["Depth"], rng.inputs[0])
    ground = nt.nodes.new("CompositorNodeMath")
    ground.operation = "LESS_THAN"
    ground.inputs[1].default_value = 1.0e7
    nt.links.new(rl.outputs["Depth"], ground.inputs[0])
    fac = nt.nodes.new("CompositorNodeMath")
    fac.operation = "MULTIPLY"
    nt.links.new(rng.outputs[0], fac.inputs[0])
    nt.links.new(ground.outputs[0], fac.inputs[1])
    mix = nt.nodes.new("CompositorNodeMixRGB")
    mix.inputs[2].default_value = hexcol(cfg.get("colour", "#DCE6EE"))
    nt.links.new(fac.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    last = mix.outputs[0]
    if cfg.get("glare"):                                  # night: a soft glow round the bright lights
        g = nt.nodes.new("CompositorNodeGlare")
        gl = cfg["glare"]
        try:
            g.glare_type = "FOG_GLOW"
        except Exception:
            pass
        for key, val in (("Threshold", gl.get("threshold", 1.0)), ("Strength", gl.get("strength", 1.0)), ("Size", gl.get("size", 0.5))):
            if key in g.inputs:
                g.inputs[key].default_value = val
        for attr, val in (("threshold", gl.get("threshold", 1.0)), ("size", gl.get("size_steps", 8)), ("quality", "HIGH")):
            try:
                setattr(g, attr, val)
            except Exception:
                pass
        nt.links.new(last, g.inputs[0])
        last = g.outputs[0]
    out = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(last, out.inputs["Image"])


def night_world(cfg):
    """A night sky instead of the day HDRI: a gradient from a glow at the horizon to a deep zenith, stars (points of a Voronoi field on the sphere of
    directions, above the horizon only), and the moon as a faint bluish sun that gives the ground its relief."""
    w = bpy.data.worlds.new("night")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs[1].default_value = -0.02
    rng.inputs[2].default_value = 0.45
    nt.links.new(sep.outputs["Z"], rng.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, hexcol(cfg.get("horizon", "#3A4A78"))
    els[1].position, els[1].color = 1.0, hexcol(cfg.get("zenith", "#060B1C"))
    mid = els.new(0.18)
    mid.color = hexcol(cfg.get("low", "#16224A"))
    nt.links.new(rng.outputs[0], ramp.inputs[0])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = cfg.get("star_scale", 260.0)
    nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
    st = nt.nodes.new("ShaderNodeMapRange")              # a star where the point of its cell is very near: 1 at the point, 0 a little away
    st.inputs[1].default_value = 0.0
    st.inputs[2].default_value = cfg.get("star_size", 0.035)
    st.inputs[3].default_value = 1.0
    st.inputs[4].default_value = 0.0
    nt.links.new(vor.outputs["Distance"], st.inputs[0])
    keep = nt.nodes.new("ShaderNodeMath")                # only some cells hold a visible star, and only above the horizon
    keep.operation = "GREATER_THAN"
    keep.inputs[1].default_value = 1.0 - cfg.get("star_fraction", 0.35)
    nt.links.new(vor.outputs["Color"], keep.inputs[0])
    up = nt.nodes.new("ShaderNodeMath")
    up.operation = "GREATER_THAN"
    up.inputs[1].default_value = 0.03
    nt.links.new(sep.outputs["Z"], up.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    nt.links.new(st.outputs[0], m1.inputs[0])
    nt.links.new(keep.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    m2.inputs[1].default_value = cfg.get("star_bright", 6.0)
    nt.links.new(m1.outputs[0], m2.inputs[0])
    m3 = nt.nodes.new("ShaderNodeMath")
    m3.operation = "MULTIPLY"
    nt.links.new(m2.outputs[0], m3.inputs[0])
    nt.links.new(up.outputs[0], m3.inputs[1])
    add = nt.nodes.new("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    add.inputs["Factor"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], add.inputs[6])
    nt.links.new(m3.outputs[0], add.inputs[7])
    nt.links.new(add.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = cfg.get("strength", 1.0)
    moon = bpy.data.lights.new("moon", "SUN")
    moon.energy = cfg.get("moon", 0.12)
    moon.color = hexcol(cfg.get("moon_colour", "#AFC4FF"))[:3]
    moon.angle = math.radians(1.0)
    mo = bpy.data.objects.new("moon", moon)
    bpy.context.scene.collection.objects.link(mo)
    el, az = math.radians(cfg.get("moon_elevation", 30)), math.radians(cfg.get("moon_azimuth", 120))
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    mo.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def night_lights(groups):
    """Lights on the ground at night: for each group a set of points (x, y; set on the ground, lifted a little), each a small emitting sphere that the
    camera sees and, every `light_every` points, a point light that lights the ground round it. groups: [{points, colour, size, strength, power,
    lift, light_every}]."""
    import bmesh
    for gi, g in enumerate(groups):
        col = hexcol(g.get("colour", "#FFD27A"))
        mat = bpy.data.materials.new(f"lamp{gi}")
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = col
        em.inputs["Strength"].default_value = g.get("strength", 60.0)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        bm = bmesh.new()
        size = g.get("size", 6.0)
        every = g.get("light_every", 1)
        for k, pt in enumerate(g["points"]):
            z = (pt[2] if len(pt) > 2 else ground_z(pt[0], pt[1]) + g.get("lift", 4.0))
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=size, matrix=Matrix.Translation((pt[0], pt[1], z)))
            if every and k % every == 0 and g.get("power", 0.0) > 0:
                ld = bpy.data.lights.new(f"l{gi}_{k}", "POINT")
                ld.energy = g["power"]
                ld.color = col[:3]
                ld.shadow_soft_size = size
                lo = bpy.data.objects.new(f"l{gi}_{k}", ld)
                lo.location = (pt[0], pt[1], z + g.get("light_lift", 12.0))
                bpy.context.scene.collection.objects.link(lo)
        me = bpy.data.meshes.new(f"lamps{gi}")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(f"lamps{gi}", me)
        ob.visible_shadow = False
        me.materials.append(mat)
        bpy.context.scene.collection.objects.link(ob)


def fogs(items):
    """Patches of fog or haze: boxes of a scattering volume, thickest at the bottom (a vertical gradient of density). items: [{center: [x, y], size: [sx, sy, sz],
    density, colour}]."""
    for i, f in enumerate(items):
        cx, cy = f["center"]
        sx, sy, sz = f["size"]
        z0 = ground_z(cx, cy) + f.get("base", 0.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, z0 + sz / 2))
        ob = bpy.context.active_object
        ob.name = f"fog{i}"
        ob.scale = (sx, sy, sz)
        mat = bpy.data.materials.new(f"fog{i}")
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = hexcol(f.get("colour", "#8D9AB8"))
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        rng = nt.nodes.new("ShaderNodeMapRange")          # densest at the floor of the box, none at its top; soft at the sides through a noise
        rng.inputs[1].default_value = 0.0
        rng.inputs[2].default_value = 1.0
        rng.inputs[3].default_value = f.get("density", 0.0008)
        rng.inputs[4].default_value = 0.0
        nt.links.new(sep.outputs["Z"], rng.inputs[0])
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = f.get("noise", 3.0)
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(rng.outputs[0], mul.inputs[0])
        nt.links.new(nz.outputs["Fac"], mul.inputs[1])
        mul2 = nt.nodes.new("ShaderNodeMath")
        mul2.operation = "MULTIPLY"
        mul2.inputs[1].default_value = 2.0
        nt.links.new(mul.outputs[0], mul2.inputs[0])
        nt.links.new(mul2.outputs[0], vol.inputs["Density"])
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
        ob.data.materials.append(mat)
        ob.visible_shadow = False


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
    for i, bl in enumerate(plan.get("blocks", [])):       # a box of one colour on the ground (a vehicle on a road)
        mat = bpy.data.materials.get("block_" + bl["colour"]) or flat_material("block_" + bl["colour"], bl["colour"], emission=0.15)
        build(f"plan block {i}", bl["ring"], bl["height"], mat, mat)
    for i, mk in enumerate(plan.get("marks", [])):        # paint: flat shapes of one colour (chevrons, holding lines), a little above the pavement
        mat = bpy.data.materials.get("paint_" + mk["colour"]) or flat_material("paint_" + mk["colour"], mk["colour"], emission=0.25)
        flat_poly(f"plan mark {i}", [mk["ring"]], 0.55, mat)
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


def _path(i, p):
    """One path of a recipe: a tube (or its dashes), its arrows and its end head."""
    if "drape" in p:                               # laid on the ground, drape metres above it (the section line of a map)
        bpy.context.view_layer.update()
        p = {**p, "points": [[x, y, ground_z(x, y) + p["drape"]] for x, y, *_ in p["points"]]}
    if p.get("dash"):
        mat = flat_material(f"path{i}m", p.get("colour", "#1D4ED8"), emission=1.5)
        for j, piece in enumerate(dashes(p["points"], *p["dash"])):
            tube_mat(piece, mat, p.get("radius", 6.0), f"path{i}.{j}")
        return
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
    if "ground_image" in r:                            # the picture of the ground on the terrain and the far ground
        gm = ground_material(r["ground_image"])
        for o in bpy.data.objects:
            if o.type == "MESH" and (o.name.startswith("Terrain") or o.name == "far ground"):
                o.data.materials.clear()
                o.data.materials.append(gm)
    inked = []
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
        inked += [o for o in obs if o.type == "MESH"]
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
        before = set(bpy.data.objects)
        _path(i, p)
        made = [o for o in bpy.data.objects if o not in before]
        for o in made:
            if p.get("shadow", True) is False:
                o.visible_shadow = False
        if p.get("ink", True):
            inked += made
    if "night" in r:
        night_world(r["night"])
    else:
        world(r.get("sun", {}))
    if "lights" in r:
        bpy.context.view_layer.update()
        night_lights(r["lights"])
    if "fogs" in r:
        bpy.context.view_layer.update()
        fogs(r["fogs"])
    if "haze" in r:
        haze(r["haze"])
    if "ink" in r:
        ink(r["ink"], inked)
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
        elif len(v) == 2:                              # (x, y): on the ground
            p = Vector((v[0], v[1], ground_z(v[0], v[1]) + 5.0))
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
