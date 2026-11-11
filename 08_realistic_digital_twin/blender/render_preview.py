"""Cycles reference renders of the built scene (run after build.py in the same Blender session or on the .blend).
    blender -b models/C172N_realistic.blend --python blender/render_preview.py -- --out docs/renders --samples 64 --views reference

--views takes view names separated by commas, or one of the sets in VIEW_SETS: "reference" (the
images in docs/renders), "gallery" (docs/gallery) or "all". The engine views leave the upper cowl
off and the exploded views move the parts apart; every other view shows the complete aircraft.
"""
import argparse, math, os, sys
import bpy
from mathutils import Vector

# Camera positions and targets in Blender world coordinates (m): +x left wing, -y nose, z up from the ground.
CABIN_LIGHT = 30.0
VIEWS = {
    "front_quarter": dict(pos=(-9.5, -9.0, 2.9), target=(0, 1.1, 0.95), fov=36),
    "rear_quarter": dict(pos=(9.5, 10.6, 3.0), target=(0, 2.1, 1.0), fov=36),
    "side": dict(pos=(-14.0, 1.95, 1.3), target=(0, 1.95, 1.1), fov=34),
    "front": dict(pos=(0, -13.0, 1.7), target=(0, 0.5, 1.1), fov=40),
    "top": dict(pos=(0.0, 1.95, 21.0), target=(0, 1.95, 1.0), fov=44),
    "nose_detail": dict(pos=(-3.2, -4.15, 1.65), target=(0.0, -0.57, 1.14), fov=35),
    "tail_detail": dict(pos=(4.4, 8.66, 2.03), target=(0.0, 5.24, 1.37), fov=38),
    "gear_detail": dict(pos=(-3.5, -0.98, 0.7), target=(-1.0, 0.51, 0.41), fov=35),
    # in the cabin a soft light under the roof (cabin, in watts) stands in for the daylight that the eye, unlike a camera
    # exposed for the sky, sees the panel by
    "cockpit": dict(pos=(0.0, 1.0, 1.55), target=(0.0, -1.57, 1.14), fov=80, cabin=CABIN_LIGHT),
    "cockpit_pilot": dict(pos=(0.28, -0.015, 1.55), target=(0.12, -1.57, 1.2), fov=84, cabin=CABIN_LIGHT),     # the pilot's eye: the occupant sits at station 37 (POH Figure 6-3)
    "cockpit_side": dict(pos=(-0.18, 0.02, 1.42), target=(0.26, -0.47, 1.17), fov=78, cabin=CABIN_LIGHT),      # from the right seat, across to the pilot's side
    "engine": dict(pos=(-2.2, -3.55, 1.88), target=(0.0, -0.46, 1.29), fov=40, hide=("POWERPLANT.cowl_upper",)),
    "engine_right": dict(pos=(2.4, -2.55, 1.6), target=(0.0, -0.51, 1.29), fov=40, hide=("POWERPLANT.cowl_upper",)),
    # gallery views: long lens so wings read as lines in profile, hero three-quarter
    "side_long": dict(pos=(-42.0, 1.95, 1.5), target=(0, 1.95, 1.1), fov=13),
    "hero": dict(pos=(-9.2, -8.4, 3.1), target=(0, 1.3, 1.0), fov=31),
    "rear_long": dict(pos=(30.0, 32.6, 5.7), target=(0, 1.95, 1.05), fov=12),
    "front_long": dict(pos=(0.3, -42.0, 1.9), target=(0, 0.5, 1.1), fov=16),
    "top_long": dict(pos=(0.0, 1.95, 62.0), target=(0, 1.95, 1.0), fov=15),
    "exploded": dict(pos=(-16.0, -13.0, 7.0), target=(0.3, 0.9, 1.3), fov=36, explode=1.0),
    "exploded_side": dict(pos=(-46.0, 2.0, 4.0), target=(0, 1.7, 1.5), fov=15, explode=1.0),
}
VIEW_SETS = {
    "reference": ["front_quarter", "rear_quarter", "side", "front", "top", "nose_detail", "tail_detail", "gear_detail",
                  "cockpit", "cockpit_pilot", "cockpit_side", "engine", "engine_right"],
    "gallery": ["hero", "side_long", "front_long", "top_long", "rear_long", "cockpit_pilot", "engine", "exploded", "exploded_side"],
    "all": list(VIEWS),
}

def setup_world(hdr):
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    bg = nt.nodes.new("ShaderNodeBackground"); out = nt.nodes.new("ShaderNodeOutputWorld")
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdr, check_existing=True)
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(env.outputs["Color"], bg.inputs["Color"]); nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

def ground(mat_apron, shadow_catcher=False):
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    g = bpy.context.active_object; g.name = "_ground"
    if shadow_catcher:
        g.is_shadow_catcher = True
    elif mat_apron:
        g.data.materials.append(mat_apron)
    return g

EXPLODE = {"AIRFRAME": 0.9, "WING_L": 1.0, "WING_R": 1.0, "EMPENNAGE": 1.0, "GEAR": 0.8, "POWERPLANT": 1.1, "ENGINE": 0.8, "INTERIOR": 0.6, "PANEL": 0.25}

def explode(f):
    """Move each direct child of a system group away from the group centre (viewer rule)."""
    deps = bpy.context.evaluated_depsgraph_get()
    def centre(obs):
        pts = []
        for o in obs:
            for ob in [o] + [c for c in o.children_recursive]:
                if ob.type == "MESH" and not ob.hide_render:
                    ev = ob.evaluated_get(deps)
                    pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
        if not pts:
            return None
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        return (mn + mx) / 2
    for g in [o for o in bpy.data.objects if o.type == "EMPTY" and o.get("group")]:
        gc = centre(g.children)
        if gc is None:
            continue
        dist = EXPLODE.get(g["system"], 0.6)
        for o in g.children:
            pc = centre([o])
            if pc is None:
                continue
            d = pc - gc
            if d.length < 1e-3:
                d = Vector((0, 0, 1))
            d.normalize(); d.z += 0.25; d.normalize()
            o.matrix_world.translation += d * dist * f * (1.6 if o.get("internal") else 1.0)

def white_world():
    w = bpy.context.scene.world
    bg = w.node_tree.nodes.get("Background")
    env = [n for n in w.node_tree.nodes if n.type == "TEX_ENVIRONMENT"]
    if bg and env:
        w.node_tree.links.remove(env[0].outputs["Color"].links[0]) if env[0].outputs["Color"].links else None
        bg.inputs["Color"].default_value = (1, 1, 1, 1); bg.inputs["Strength"].default_value = 1.2

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="docs/renders"); ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--views", default="front_quarter,rear_quarter,side"); ap.add_argument("--res", default="1280x720"); ap.add_argument("--prefix", default="phase8_")
    ap.add_argument("--hdr", default=None); ap.add_argument("--hide", default="")
    ap.add_argument("--explode", type=float, default=0.0, help="exploded-assembly factor 0..1 for every view (same rule as the viewer)")
    ap.add_argument("--white", action="store_true", help="plain white studio background")
    ap.add_argument("--transparent", action="store_true", help="transparent background with a shadow catcher (print/gallery)")
    ap.add_argument("--fill", type=float, default=0.0, help="soft fill light strength (W) from the camera side")
    ap.add_argument("--no-denoise", action="store_true", help="disable optional OpenImageDenoise (portable CI smoke renders)")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = a.samples; sc.cycles.device = "CPU"; sc.cycles.use_denoising = not a.no_denoise
    sc.render.resolution_x, sc.render.resolution_y = [int(v) for v in a.res.split("x")]
    sc.render.film_transparent = bool(a.transparent)
    sc.render.image_settings.color_mode = "RGBA" if a.transparent else "RGB"
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    hdr = a.hdr or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "hdri", "sky.hdr")
    setup_world(hdr)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(48), 0, math.radians(35))
    ground(bpy.data.materials.get("apron_asphalt"), shadow_catcher=a.transparent)
    if a.fill > 0:
        fl = bpy.data.lights.new("fill", "AREA"); fl.energy = a.fill; fl.size = 12; fl.color = (0.9, 0.95, 1.0)
        fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
        fo.location = (-12, -10, 9); fo.rotation_euler = (Vector((12, 10, -9)).to_track_quat("-Z", "Y").to_euler())
        fl2 = bpy.data.lights.new("rim", "AREA"); fl2.energy = a.fill * 0.6; fl2.size = 10
        fo2 = bpy.data.objects.new("rim", fl2); sc.collection.objects.link(fo2)
        fo2.location = (10, 12, 7); fo2.rotation_euler = (Vector((-10, -12, -7)).to_track_quat("-Z", "Y").to_euler())
    if a.white:
        white_world()
        sc.view_settings.look = "AgX - Base"
    cabin = bpy.data.lights.new("cabin", "AREA"); cabin.size = 0.5; cabin.color = (1.0, 0.97, 0.93)
    cabin_ob = bpy.data.objects.new("cabin", cabin); sc.collection.objects.link(cabin_ob)
    cabin_ob.location = (0.0, 0.42, 1.88); cabin_ob.rotation_euler = (Vector((0.05, -0.52, 1.36)) - Vector(cabin_ob.location)).to_track_quat("-Z", "Y").to_euler()
    always_hidden = [n for n in a.hide.split(",") if n]
    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    views = VIEW_SETS.get(a.views) or a.views.split(",")
    for v in views:
        spec = VIEWS[v]
        # per-view state: parts left off, parts moved apart; both are undone after the render
        hidden = []
        for name in list(spec.get("hide", ())) + always_hidden:
            ob = bpy.data.objects.get(name)
            if ob is not None and not ob.hide_render:
                ob.hide_render = True; hidden.append(ob)
        factor = max(a.explode, spec.get("explode", 0.0))
        placed = {}
        if factor > 0:      # explode() moves the direct children of the system groups
            placed = {o: o.matrix_world.copy() for g in bpy.data.objects if g.type == "EMPTY" and g.get("group") for o in g.children}
            explode(factor)
        cabin.energy = spec.get("cabin", 0.0); cabin_ob.hide_render = cabin.energy <= 0
        co.location = spec["pos"]
        d = Vector(spec["target"]) - Vector(spec["pos"])
        co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.angle = math.radians(spec["fov"]); cam.clip_start = 0.05
        sc.render.filepath = os.path.join(a.out, f"{a.prefix}{v}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", sc.render.filepath)
        for ob in hidden:
            ob.hide_render = False
        for ob, matrix in placed.items():
            ob.matrix_world = matrix
        if placed:
            bpy.context.view_layer.update()

main()
