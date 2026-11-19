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
        if not ob.hide_render and not ob.name.startswith(("air ", "edge ", "path", "cloud", "fog", "lamps", "spot")):
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
    col = mix.outputs[2]
    det = gi.get("detail")
    if det:                                                # fine grain for low views, where 10 m pixels are a blur: noise in the colour and a little bump
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = det.get("scale", 0.08)
        nz.inputs["Detail"].default_value = 12.0
        nz.inputs["Roughness"].default_value = 0.65
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.inputs["To Min"].default_value, rng.inputs["To Max"].default_value = 1.0 - det.get("strength", 0.25), 1.0 + det.get("strength", 0.25) * 0.6
        nt.links.new(nz.outputs["Fac"], rng.inputs["Value"])
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mul.inputs[6])
        gray = nt.nodes.new("ShaderNodeCombineColor")
        for k in ("Red", "Green", "Blue"):
            nt.links.new(rng.outputs["Result"], gray.inputs[k])
        nt.links.new(gray.outputs[0], mul.inputs[7])
        col = mul.outputs[2]
        fine = nt.nodes.new("ShaderNodeTexNoise")
        fine.inputs["Scale"].default_value = det.get("scale", 0.08) * 12.0
        fine.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], fine.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = det.get("bump", 0.35)
        nt.links.new(fine.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(col, bsdf.inputs["Base Color"])
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
        if f.get("noise", 3.0):
            nt.links.new(nz.outputs["Fac"], mul.inputs[1])
        else:                                             # noise 0: an even layer (the noise of a thin, wide box is stretched across its thickness)
            mul.inputs[1].default_value = 0.5
        mul2 = nt.nodes.new("ShaderNodeMath")
        mul2.operation = "MULTIPLY"
        mul2.inputs[1].default_value = 2.0
        nt.links.new(mul.outputs[0], mul2.inputs[0])
        dens = mul2.outputs[0]
        if "soft" in f:                                   # a round patch fading out from `soft` (a fraction of the half-width) to the edge of the box, with no straight sides
            sub = nt.nodes.new("ShaderNodeVectorMath")
            sub.operation = "SUBTRACT"
            sub.inputs[1].default_value = (0.5, 0.5, 0.0)
            nt.links.new(tc.outputs["Generated"], sub.inputs[0])
            flat = nt.nodes.new("ShaderNodeVectorMath")
            flat.operation = "MULTIPLY"
            flat.inputs[1].default_value = (2.0, 2.0, 0.0)
            nt.links.new(sub.outputs[0], flat.inputs[0])
            ln = nt.nodes.new("ShaderNodeVectorMath")
            ln.operation = "LENGTH"
            nt.links.new(flat.outputs[0], ln.inputs[0])
            edge = nt.nodes.new("ShaderNodeMapRange")
            edge.interpolation_type = "SMOOTHSTEP"
            edge.inputs[1].default_value = f["soft"]
            edge.inputs[2].default_value = 1.0
            edge.inputs[3].default_value = 1.0
            edge.inputs[4].default_value = 0.0
            nt.links.new(ln.outputs["Value"], edge.inputs[0])
            m3 = nt.nodes.new("ShaderNodeMath")
            m3.operation = "MULTIPLY"
            nt.links.new(dens, m3.inputs[0])
            nt.links.new(edge.outputs[0], m3.inputs[1])
            dens = m3.outputs[0]
        nt.links.new(dens, vol.inputs["Density"])
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
        ob.data.materials.append(mat)
        ob.visible_shadow = False


def despeckle(path, threshold):
    """Single bright or dark pixels taken out of a saved picture: a pixel that differs from the median of its neighbourhood (3 x 3 twice, then 5 x 5) by more than `threshold`
    (0..1, summed over red, green and blue) takes that median. A thin, wide layer of fog seen at a grazing angle leaves such points, whatever the samples."""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    total = 0
    for k in (1, 1, 2):                                   # twice over 3 x 3, then over 5 x 5 (the points come in small clumps too)
        pad = np.pad(px, ((k, k), (k, k), (0, 0)), mode="edge")
        med = np.median(np.stack([pad[k + dy:k + dy + h, k + dx:k + dx + w] for dy in range(-k, k + 1) for dx in range(-k, k + 1)]), axis=0)
        off = np.abs(px[..., :3] - med[..., :3]).sum(axis=2) > threshold
        px[off] = med[off]
        total += int(off.sum())
    off = total
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    print("despeckled", off, "pixels")


def scene_clouds(items):
    """Clouds of the cloud library (blender/render_clouds.py: the same kinds, shapes and media) set into the scene: each built in its own units, then
    placed by an empty at `at` (the middle of its foot, metres) and scaled by `scale` (metres to the unit); the medium's density is divided by the scale,
    so that a cloud keeps the look it has in the library. items: [{kind, seed, width, height, ..., at, scale, heading}]."""
    import random as _random
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import render_clouds as RC
    sc = bpy.context.scene
    for ci, c in enumerate(items):
        rnd = _random.Random(c.get("seed", 1))
        way, make = RC.KINDS[c["kind"]]
        args = {k: v for k, v in c.items() if k in ("width", "height", "anvil", "rows", "per_row", "layers", "girth", "depth", "lean", "lens_density", "lens_erode", "deck")}
        parts = [RC.lumpy(make(rnd, **args))] if way == "lumpy" else make(rnd, **args)
        x0, x1, z0, z1 = RC.bounds_of(parts)
        span = x1 - x0
        scale = c.get("scale", 100.0)
        recipe = dict(c)
        recipe["density"] = c.get("density", 60.0) / scale
        before = set(bpy.data.objects)
        for k, part in enumerate(parts):
            mat = RC.volume_material(f"c{ci}m{k}", recipe, part)
            band = part.get("band", 1.0) * c.get("band", 0.025) * span
            voxel = max(0.02, c.get("voxel", 0.009) * span)
            if part["part"] == "lumpy":
                RC.soft_volume(sc, f"cloud{ci}p{k}", RC.mesh_of_metaballs(part["elements"], part.get("resolution") or max(0.025, 0.005 * span)), mat, band, voxel)
            elif part["part"] == "lens":
                RC.soft_volume(sc, f"cloud{ci}p{k}", RC.mesh_of_lens(part["centre"], part["size"], wobble=part.get("wobble", 0.0), rnd=_random.Random(c.get("seed", 1) * 31 + k)), mat, band, voxel)
            else:
                RC.hard_volume(sc, f"cloud{ci}p{k}", RC.mesh_of_box(part["centre"], part["size"]), mat)
        root = bpy.data.objects.new(f"cloud{ci}", None)
        sc.collection.objects.link(root)
        for o in bpy.data.objects:
            if o not in before and o is not root and o.parent is None:
                o.parent = root
                o.location.x -= (x0 + x1) / 2
                o.location.z -= z0
        root.location = Vector(c["at"])
        root.scale = (scale, scale, scale)
        root.rotation_euler = (0.0, 0.0, math.radians(-c.get("heading", 0.0)))
        if c.get("clearance"):                            # the distances to keep from the cloud: a glass box round its bounds (above, below, all round)
            bpy.context.view_layer.update()
            pts = [o.matrix_world @ Vector(corner) for o in bpy.data.objects if o.parent is root for corner in o.bound_box]
            xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
            cl = c["clearance"]
            sd = cl.get("side", 610.0)
            x0, x1, y0, y1 = min(xs) - sd, max(xs) + sd, min(ys) - sd, max(ys) + sd
            volumes([{"name": f"clear{ci}", "ring": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], "floor": min(zs) - cl.get("below", 152.0), "ceiling": max(zs) + cl.get("above", 305.0),
                      "colour": cl.get("colour", "#2563EB"), "alpha": cl.get("alpha", 0.12), "edge": cl.get("edge", 6.0), "corner_edges": True}])
            print("clearance", ci, [round(v) for v in (x0, x1, y0, y1, min(zs), max(zs))])


def flatten_ground(plan):
    import numpy as np
    rings = [p["ring"] for p in plan.get("pavements", [])]
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    step = plan.get("grade_step", 40.0)
    hs = [ground_z(min(xs) + i * step, min(ys) + j * step) for i in range(int((max(xs) - min(xs)) / step) + 1) for j in range(int((max(ys) - min(ys)) / step) + 1)]
    gz = float(np.median(hs))
    inner, outer = plan["flatten"].get("inner", 60.0), plan["flatten"].get("outer", 450.0)
    x0, x1, y0, y1 = min(xs) - outer, max(xs) + outer, min(ys) - outer, max(ys) + outer

    def dist(px, py):                                      # distance from the points to the nearest pavement (0 inside one); rings are convex quadrilaterals or polygons
        d = np.full(px.shape, np.inf)
        for r in rings:
            n = len(r)
            inside = np.ones(px.shape, bool)
            sign = None
            dr = np.full(px.shape, np.inf)
            for k in range(n):
                ax, ay = r[k]
                bx, by = r[(k + 1) % n]
                ex, ey = bx - ax, by - ay
                cr = ex * (py - ay) - ey * (px - ax)
                sign = np.sign(cr) if sign is None else sign
                inside &= np.sign(cr) == sign
                t = np.clip(((px - ax) * ex + (py - ay) * ey) / (ex * ex + ey * ey), 0.0, 1.0)
                dr = np.minimum(dr, np.hypot(px - (ax + t * ex), py - (ay + t * ey)))
            d = np.minimum(d, np.where(inside, 0.0, dr))
        return d

    n_moved = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith("Terrain"):
            continue
        me = ob.data
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        mw = np.array(ob.matrix_world)
        w = co @ mw[:3, :3].T + mw[:3, 3]
        sel = (w[:, 0] > x0) & (w[:, 0] < x1) & (w[:, 1] > y0) & (w[:, 1] < y1)
        if not sel.any():
            continue
        d = dist(w[sel, 0], w[sel, 1])
        t = np.clip((d - inner) / (outer - inner), 0.0, 1.0)
        t = t * t * (3 - 2 * t)
        w[sel, 2] = gz * (1 - t) + w[sel, 2] * t
        n_moved += int((t < 1).sum())
        loc = (w - mw[:3, 3]) @ np.linalg.inv(mw[:3, :3]).T
        me.vertices.foreach_set("co", loc.ravel())
        me.update()
    bpy.context.view_layer.update()
    print(f"render_oeth: ground levelled at {gz:.1f} m under the plan ({n_moved} vertices moved)")
    return gz


def lay_plan(plan):
    twy = bpy.data.materials["taxi"]
    apron = bpy.data.materials["apron"]
    island = bpy.data.materials["island"]
    walls = bpy.data.materials["walls"]
    roof = flat_material("roof", "#F4F1EA")
    rwy = bpy.data.materials["asphalt"]
    gz = None
    if plan.get("flatten"):                                # a graded aerodrome: the ground itself levelled under its pavements (at their median height), eased back to
        gz = flatten_ground(plan)                          # the natural ground beyond them, so that nothing floats and nothing is buried
    elif plan.get("grade"):                                  # a graded aerodrome: its pavements and paint level, at the highest ground under them
        xs = [x for p in plan.get("pavements", []) for x, _ in p["ring"]]
        ys = [y for p in plan.get("pavements", []) for _, y in p["ring"]]
        step = plan.get("grade_step", 40.0)
        gz = max(ground_z(x0 + i * step, y0 + j * step) for x0, y0 in [(min(xs), min(ys))]
                 for i in range(int((max(xs) - min(xs)) / step) + 1) for j in range(int((max(ys) - min(ys)) / step) + 1))
    for p in plan.get("pavements", []):
        flat_poly("plan " + p["name"], [p["ring"], *p.get("holes", [])], p.get("lift", 0.30), {"apron": apron, "runway": rwy}.get(p["zone"], twy), z=gz)
    for i, p in enumerate(plan.get("islands", [])):
        flat_poly(f"plan island {i}", [p["ring"]], 0.45, island)
    for b in plan.get("buildings", []):
        build("plan " + b["name"], b["ring"], b["height"], walls, roof)
    for i, bl in enumerate(plan.get("blocks", [])):       # a box of one colour on the ground (a vehicle on a road)
        mat = bpy.data.materials.get("block_" + bl["colour"]) or flat_material("block_" + bl["colour"], bl["colour"], emission=0.15)
        build(f"plan block {i}", bl["ring"], bl["height"], mat, mat)
    for i, mk in enumerate(plan.get("marks", [])):        # paint: flat shapes of one colour (chevrons, holding lines), a little above the pavement
        mat = bpy.data.materials.get("paint_" + mk["colour"]) or flat_material("paint_" + mk["colour"], mk["colour"], emission=0.25)
        flat_poly(f"plan mark {i}", [mk["ring"]], mk.get("lift", 0.55), mat, z=gz)
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


def _frustum(name, a, b, ra, rb, mat, n=32):
    """A tube from point a (radius ra) to point b (radius rb), open at both ends: one band of a windsock."""
    axis = (b - a).normalized()
    u = axis.orthogonal().normalized()
    v = axis.cross(u)
    verts = []
    for p, r in ((a, ra), (b, rb)):
        for k in range(n):
            t = 2 * math.pi * k / n
            verts.append(p + (u * math.cos(t) + v * math.sin(t)) * r)
    faces = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    ob = _mesh(name, [tuple(q) for q in verts], faces, mat)
    ob.data.polygons.foreach_set("use_smooth", [True] * len(faces))
    sol = ob.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.02
    return ob


def windsock(w, i):
    """A windsock on its mast (the scene has none): a 6 m mast, a ring at its head, and a sock of five bands, orange and white, that hangs by `inflate` (0 calm, 1 full);
    it points downwind, its mouth toward the wind's direction `wind_from` (degrees true)."""
    x, y = w["at"]
    z0 = w.get("z", ground_z(x, y))
    mast_h, L, r0, r1 = w.get("mast", 6.0), w.get("length", 3.6), w.get("mouth", 0.45), w.get("tail", 0.22)
    pole = flat_material("windsock pole", "#D9DCE0")
    pole.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.6
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=mast_h, location=(x, y, z0 + mast_h / 2))
    m = bpy.context.active_object
    m.name = f"windsock{i} mast"
    m.data.materials.append(pole)
    cols = [flat_material("sock orange", "#F26A1B"), flat_material("sock white", "#F4F4F0")]
    down = math.radians(w.get("wind_from", 270.0) + 180.0)
    fwd = Vector((math.sin(down), math.cos(down), 0.0))
    droop = math.radians(75.0 * (1.0 - w.get("inflate", 0.8)))
    p = Vector((x, y, z0 + mast_h - 0.15)) + fwd * 0.1
    bpy.ops.mesh.primitive_torus_add(major_radius=r0, minor_radius=0.03, location=tuple(p))
    ring = bpy.context.active_object
    ring.name = f"windsock{i} ring"
    ring.rotation_euler = fwd.to_track_quat("Z", "Y").to_euler()
    ring.data.materials.append(pole)
    for k in range(5):
        ang = droop * (k + 1) / 5.0
        d = (fwd * math.cos(ang) + Vector((0, 0, -math.sin(ang)))).normalized()
        q = p + d * (L / 5.0)
        ra, rb = r0 + (r1 - r0) * k / 5.0, r0 + (r1 - r0) * (k + 1) / 5.0
        _frustum(f"windsock{i} band{k}", p, q, ra, rb, cols[k % 2])
        p = q


def ridges(items, mat):
    """Ridges the scene lacks (the high ground of the south-west, for a mountain wave): a grid laid along a line from a to b, its height a smooth hump across the
    line (width the foot to foot distance) with a noise of 15 percent along and across it, tapering at the two ends; the ground picture as its material."""
    import random as _r
    for i, rg in enumerate(items):
        ax, ay = rg["a"]
        bx, by = rg["b"]
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = uy, -ux
        H, Wd = rg["height"], rg["width"]
        nu, nv = int(rg.get("rows", 120)), int(rg.get("cols", 60))
        rnd = _r.Random(rg.get("seed", 1))
        ph = [rnd.uniform(0, 6.28) for _ in range(6)]
        verts, faces = [], []
        for j in range(nu + 1):
            t = j / nu
            end = min(1.0, min(t, 1 - t) / 0.12)
            end = end * end * (3 - 2 * end)
            for k in range(nv + 1):
                v = (k / nv - 0.5) * Wd
                prof = math.exp(-((v / (0.32 * Wd)) ** 2)) - math.exp(-(0.5 / 0.32) ** 2)
                prof = max(0.0, prof) / (1 - math.exp(-(0.5 / 0.32) ** 2))
                wob = 1.0 + 0.15 * (math.sin(t * 9.0 + ph[0]) * math.cos(v / Wd * 7.0 + ph[1]) + 0.6 * math.sin(t * 23.0 + ph[2] + v / Wd * 11.0))
                x, y = ax + ux * t * L + nx * v, ay + uy * t * L + ny * v
                verts.append((x, y, ground_z(x, y) - 2.0 + H * prof * end * wob))
        for j in range(nu):
            for k in range(nv):
                a0 = j * (nv + 1) + k
                faces.append((a0, a0 + 1, a0 + nv + 2, a0 + nv + 1))
        ob = _mesh(f"Ridge {i}", verts, faces, mat)
        ob.data.polygons.foreach_set("use_smooth", [True] * len(faces))


def frame_camera(f, sc):
    """A camera that frames the named objects (prefixes) from an azimuth (clockwise from north, from the objects to the camera) and an elevation, the
    whole of their bounding sphere in view with a margin."""
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for k in f["objects"] for o in find(k) if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    mid = (lo + hi) / 2
    rad = max((hi - lo).length / 2, 0.5)
    lens = f.get("lens", 50)
    w, h = f.get("size", [1200, 1200])
    fov = 2 * math.atan(18.0 * min(1.0, h / w) / lens)          # (the sensor's 36 mm lies along the longer side)
    d = rad / math.sin(fov / 2) * f.get("margin", 1.05)
    az, el = math.radians(f.get("azimuth", 200)), math.radians(f.get("elevation", 30))
    at = mid + Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))) * d
    print(f"render_oeth: frame {f['objects']} centre {tuple(round(v, 1) for v in mid)} radius {rad:.1f} m")
    return {"at": list(at), "look": list(mid), "lens": lens}


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
    if "ridges" in r:
        bpy.context.view_layer.update()
        ridges(r["ridges"], bpy.data.materials.get("ground_img") or bpy.data.materials.get("sand"))
    inked = []
    keep_air = r.get("airspace", [])
    air_obs = import_glb(os.path.join(SCENE, "OETH_airspace.glb"))
    for o in air_obs:
        if o.type == "MESH" and not any(o.name.startswith(k) for k in keep_air):
            o.hide_render = True
    for o in scene_obs:
        if any(o.name.startswith(k) for k in r.get("hide", [])):
            o.hide_render = True
    for pre, strength in r.get("emit", {}).items():     # lamps of the scene lit (the PAPI lenses): their own colour as emission
        for m in bpy.data.materials:
            if m.name.startswith(pre) and m.use_nodes:
                b = m.node_tree.nodes.get("Principled BSDF")
                if b is not None:
                    b.inputs["Emission Color"].default_value = b.inputs["Base Color"].default_value
                    b.inputs["Emission Strength"].default_value = strength
    for i, w in enumerate(r.get("windsocks", [])):
        bpy.context.view_layer.update()
        windsock(w, i)
    if "only" in r:                                    # a spot: one piece of the scene (or of its airspace) alone, on a clear background
        for o in scene_obs + air_obs:
            if o.type == "MESH":
                o.hide_render = not any(o.name.startswith(k) for k in r["only"])
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
    if "clouds" in r:
        scene_clouds(r["clouds"])
        sc.cycles.volume_bounces = r.get("volume_bounces", 12)     # (as the cloud library: light scattered many times inside the cloud is what makes it white)
        sc.cycles.max_bounces = max(sc.cycles.max_bounces, 16)
        sc.cycles.transparent_max_bounces = max(sc.cycles.transparent_max_bounces, 16)
    for i, sp in enumerate(r.get("spots", [])):         # area lights aimed at a point (a soft key on the aeroplane at night)
        ld = bpy.data.lights.new(f"spot{i}", "AREA")
        ld.energy = sp.get("power", 2000.0)
        ld.size = sp.get("size", 10.0)
        ld.color = hexcol(sp.get("colour", "#C9D6FF"))[:3]
        lo = bpy.data.objects.new(f"spot{i}", ld)
        lo.location = Vector(sp["at"])
        lo.rotation_euler = (Vector(sp["look"]) - Vector(sp["at"])).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    if "haze" in r:
        haze(r["haze"])
    if "ink" in r:
        ink(r["ink"], inked)
    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    c = r["camera"] if "camera" in r else frame_camera(r["frame"], sc)
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
        if r.get("despeckle"):
            despeckle(out, r["despeckle"])
    with open(os.path.join(PLATES, "renders", r["id"] + ".anchors.json"), "w") as f:
        json.dump({"id": r["id"], "size": [w, h], "anchors": anchors, "curves": {}}, f, indent=1)
    print("rendered", r["id"])


main()
