"""Cycles reference renders of the built scene (run after build.py in the same Blender session or on the .blend).
    blender -b models/C172N_realistic.blend --python blender/render_preview.py -- --out docs/renders --samples 64 --views all
"""
import argparse, math, os, sys
import bpy
from mathutils import Vector

VIEWS = {
    "front_quarter": dict(pos=(-9.5, -9.0, 3.2), target=(0, 1.2, 1.2), fov=36),
    "rear_quarter": dict(pos=(8.5, 9.5, 3.0), target=(0, 1.4, 1.3), fov=36),
    "side": dict(pos=(-14.0, 1.2, 1.6), target=(0, 1.2, 1.4), fov=32),
    "front": dict(pos=(0, -13.0, 2.0), target=(0, 0.5, 1.4), fov=40),
    "top": dict(pos=(0.0, 1.5, 16.0), target=(0, 1.5, 1.0), fov=44),
    "nose_detail": dict(pos=(-3.2, -4.2, 1.7), target=(0, -0.6, 1.3), fov=35),
    "tail_detail": dict(pos=(4.0, 7.5, 2.2), target=(0, 5.0, 1.8), fov=35),
    "gear_detail": dict(pos=(-3.5, -1.0, 0.6), target=(-1.0, 0.5, 0.35), fov=35),
    "cockpit": dict(pos=(0.0, 0.95, 1.78), target=(0.0, -1.6, 1.30), fov=80),
    "cockpit_pilot": dict(pos=(0.30, 0.30, 1.74), target=(0.12, -1.6, 1.36), fov=68),
    "cockpit_side": dict(pos=(1.4, 0.3, 1.5), target=(-0.2, -0.2, 1.3), fov=60),
    "engine": dict(pos=(-2.2, -3.6, 1.9), target=(0, -0.5, 1.35), fov=40),
    "engine_right": dict(pos=(2.4, -2.6, 1.6), target=(0, -0.55, 1.35), fov=40),
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

def ground(mat_apron):
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    g = bpy.context.active_object; g.name = "_ground"
    if mat_apron:
        g.data.materials.append(mat_apron)
        uv = g.data.uv_layers.active
    return g

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="docs/renders"); ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--views", default="front_quarter,rear_quarter,side"); ap.add_argument("--res", default="1280x720"); ap.add_argument("--prefix", default="phase8_")
    ap.add_argument("--hdr", default=None); ap.add_argument("--hide", default="")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = a.samples; sc.cycles.device = "CPU"; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = [int(v) for v in a.res.split("x")]
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    hdr = a.hdr or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "hdri", "sky.hdr")
    setup_world(hdr)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(48), 0, math.radians(35))
    ground(bpy.data.materials.get("apron_asphalt"))
    for n in a.hide.split(","):
        if n and bpy.data.objects.get(n):
            bpy.data.objects[n].hide_render = True
    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    views = list(VIEWS) if a.views == "all" else a.views.split(",")
    for v in views:
        spec = VIEWS[v]
        co.location = spec["pos"]
        d = Vector(spec["target"]) - Vector(spec["pos"])
        co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.angle = math.radians(spec["fov"]); cam.clip_start = 0.05
        sc.render.filepath = os.path.join(a.out, f"{a.prefix}{v}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", sc.render.filepath)

main()
