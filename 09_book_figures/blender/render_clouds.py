"""Cloud sprites for the handbook's weather figures: Cycles renders of procedural clouds on a transparent background, which a figure lays on its
scene the way it lays the aeroplane (an overlay {"type": "sprite", "name": "cloud-cumulus-a", ...}, see handbook/figs/clouds.py and reskin.py).

    blender -b --python 09_book_figures/blender/render_clouds.py -- --all              (or --cloud <id> ..., --quick, --out <folder>)

Each cloud of handbook/figs/clouds.py gives handbook/renders/<id>.png. A cloud is a few nested shells of metaballs (a union of spheres, closed meshes, so that
Cycles fills them with a scattering volume), the density inside eroded by noise so that the edge is ragged and the surface cauliflowered, and cut flat at
the base where the recipe says so. The camera is orthographic and fitted to the cloud; the light is a white sun from the upper left in front and a blue sky.

    kind       cumulus | congestus | cb | anvil | stratus | altocumulus | cirrus | lenticular | roll   (how the elements are laid out, see KINDS)
    seed       the random numbers of the cauliflower (another seed is another cloud of the same kind)
    width      metres across the main body (the units are arbitrary: the camera fits the cloud), height / thickness as the kind takes them
    density    how thick the cloud is (more: whiter and more opaque; less: a thin veil)           absorb  0..1: grey the base (a storm cloud)
    stretch    stretch the noise along x (a fibrous cirrus)      floor  true: cut the base flat      tint  [r, g, b]: colour the scattering (dust)
"""
import argparse
import math
import os
import random
import sys
import time

import bpy
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(os.path.dirname(HERE), "handbook")
sys.path.insert(0, PLATES)


# ------------------------------------------------------------------------------------------------------------------ shapes (lists of elements)
def ball(x, y, z, r):
    return {"type": "BALL", "co": (x, y, z), "radius": r}


def cauliflower(rnd, base, levels=2, first=(7, 12), later=(3, 5), shrink=(0.40, 0.60), reach=0.80, lift=-0.15):
    """Smaller balls over the surface of each ball, again, so that the cloud has billows on its billows (turned up and a little towards the camera)."""
    out, frontier = list(base), list(base)
    for level in range(levels):
        new = []
        for e in frontier:
            x, y, z = e["co"]
            r = e["radius"]
            for _ in range(rnd.randint(*(first if level == 0 else later))):
                th, ph = rnd.uniform(0, 2 * math.pi), math.acos(rnd.uniform(lift, 1.0))
                d = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th) * 0.8 - 0.3, math.cos(ph))).normalized()
                p = Vector((x, y, z)) + d * (r * reach)
                new.append(ball(p.x, p.y, p.z, r * rnd.uniform(*shrink)))
        out += new
        frontier = new
    return out


def kind_cumulus(rnd, width=9.0, height=4.0, **_):
    n = max(3, round(width / 2.0))
    base = []
    for i in range(n):
        u = (i + 0.5) / n * 2 - 1
        h = height * (1 - 0.65 * abs(u) ** 1.5) * rnd.uniform(0.8, 1.1)
        r = h * rnd.uniform(0.38, 0.5) + 0.35
        base.append(ball(u * width * 0.42 + rnd.uniform(-0.2, 0.2), rnd.uniform(-0.5, 0.5), r * 0.8, r))
    return cauliflower(rnd, base)


def kind_congestus(rnd, width=5.0, height=9.0, girth=1.0, **_):
    base, levels = [], max(3, round(height / (1.3 * girth)))
    for k in range(levels):
        t = k / (levels - 1)
        z = 0.9 + t * (height - 1.8)
        w = width * (0.45 + 0.55 * (1 - t) ** 0.5)
        r = (0.9 + 0.7 * (1 - t) ** 0.7 + 0.3 * math.sin(t * math.pi)) * girth
        for j in range(3 if t < 0.7 else 2):
            base.append(ball((j - 1) * w * 0.32 + rnd.uniform(-0.25, 0.25), rnd.uniform(-0.4, 0.4), z + rnd.uniform(-0.2, 0.2), r * rnd.uniform(0.85, 1.1)))
    return cauliflower(rnd, base, first=(5, 8), later=(2, 3))


def ellipsoid(x, y, z, r, sx, sy, sz):
    return {"type": "ELLIPSOID", "co": (x, y, z), "radius": r, "size": (sx, sy, sz)}


def anvil_row(rnd, span, z, thick, n=None):
    """A flat anvil: overlapping flattened ellipsoids along the span, thinner and lower towards the ends."""
    n = n or max(5, round(span / 2.4))
    row = []
    for i in range(n):
        u = (i + 0.5) / n * 2 - 1
        t = thick * (0.45 + 0.55 * (1 - abs(u) ** 2.0)) * rnd.uniform(0.9, 1.1)
        row.append(ellipsoid(u * span / 2, rnd.uniform(-0.5, 0.5), z + rnd.uniform(-0.1, 0.1) - 0.2 * abs(u), 1.0, span / n * 1.1, 2.2, t * 0.55))
    return row


def kind_cb(rnd, width=5.0, height=11.0, anvil=15.0, girth=1.0, **_):
    tower = kind_congestus(rnd, width, height, girth)
    top = [ball(rnd.uniform(-0.8, 0.8), rnd.uniform(-0.3, 0.3), height * 0.97 + 0.3, 1.1), ball(0.5, 0.0, height * 0.9 + 0.8, 0.9)]
    flat = anvil_row(rnd, anvil, height * 0.88, 2.0)
    foot = cauliflower(rnd, [ball(x, rnd.uniform(-0.5, 0.5), 0.9, 1.1) for x in (-2.8, -1.4, 0.0, 1.4, 2.8)], levels=1)
    return tower + top + flat + foot


def kind_anvil(rnd, width=14.0, height=3.0, **_):
    top = anvil_row(rnd, width, height, 1.3)
    hang = [ball(rnd.uniform(-width * 0.35, width * 0.35), rnd.uniform(-0.4, 0.4), height - rnd.uniform(0.9, 1.7), rnd.uniform(0.3, 0.5)) for _ in range(9)]
    stump = cauliflower(rnd, [ball(-width * 0.1, 0.0, 0.8, 1.2), ball(width * 0.04, 0.2, 1.2, 1.0)], levels=1)
    return top + hang + stump


def kind_stratus(rnd, width=18.0, height=1.4, **_):
    out = []
    n = max(8, round(width / 0.9))
    for row in (-0.9, 0.0, 0.9):
        for i in range(n):
            u = (i + 0.5) / n * 2 - 1
            if rnd.random() < 0.08 * abs(u) ** 2 * 6:
                continue
            r = height * (0.55 + 0.45 * (1 - abs(u) ** 3)) * rnd.uniform(0.8, 1.15)
            out.append(ball(u * width / 2, row + rnd.uniform(-0.2, 0.2), rnd.uniform(-0.12, 0.12), r))
    return out


def kind_altocumulus(rnd, width=16.0, rows=3, **_):
    out = []
    per = max(4, round(width / 1.7))
    for row in range(rows):
        for i in range(per):
            u = (i + 0.5) / per * 2 - 1
            x = u * width / 2 + rnd.uniform(-0.3, 0.3) + (0.8 if row % 2 else 0)
            r = rnd.uniform(0.38, 0.62) * (1.0 - 0.12 * row)
            out += cauliflower(rnd, [ball(x, rnd.uniform(-0.3, 0.3), row * 0.95 + 0.4 * r + rnd.uniform(-0.1, 0.1), r)], levels=1, first=(3, 5))
    return out


def kind_lenticular(rnd, width=8.0, layers=3, **_):
    """A pile of lenses, each a chain of balls that swell in the middle and thin out at the ends, each a little shorter than the one under it."""
    out = []
    for k in range(layers):
        length = width * (1 - 0.18 * k)
        n = max(9, round(length / 0.4))
        for i in range(n):
            u = (i + 0.5) / n * 2 - 1
            out.append(ball(u * length / 2 + rnd.uniform(-0.05, 0.05), rnd.uniform(-0.1, 0.1), k * 0.62 + 0.04 * (1 - u * u), 0.2 + 0.26 * (1 - u * u) ** 0.7))
    return out


def kind_roll(rnd, width=9.0, height=1.5, **_):
    out = []
    n = max(6, round(width / 0.9))
    for i in range(n):
        u = (i + 0.5) / n * 2 - 1
        r = height * (0.6 + 0.4 * (1 - u * u)) * rnd.uniform(0.9, 1.1)
        out += cauliflower(rnd, [ball(u * width / 2, rnd.uniform(-0.2, 0.2), height * 0.8, r)], levels=1, first=(4, 6))
    return out


def kind_cirrus(rnd, width=14.0, wisps=6, **_):
    """Wisps: chains of thin capsules along a curve, hooked at the end (the noise is stretched along x for the fibres)."""
    out = []
    for w in range(wisps):
        x0, z0 = rnd.uniform(-width * 0.5, -width * 0.1), rnd.uniform(0.0, 2.4)
        length, drop = rnd.uniform(width * 0.35, width * 0.6), rnd.uniform(-0.2, 0.5)
        n = 7
        for i in range(n):
            t = i / (n - 1)
            x, z = x0 + t * length, z0 - drop * t - (1.1 * max(0.0, t - 0.7) ** 2 * 6)
            slope = (-drop - 1.1 * 2 * max(0.0, t - 0.7) * 6) / length
            out.append({"type": "CAPSULE", "co": (x, rnd.uniform(-0.3, 0.3), z), "radius": 0.2 * (1.0 - 0.45 * t) * rnd.uniform(0.8, 1.2), "size": (length / n * 0.62, 0.0, 0.0),
                        "rotation": Euler((0, -math.atan(slope), 0)).to_quaternion()})
    return out


KINDS = {"cumulus": kind_cumulus, "congestus": kind_congestus, "cb": kind_cb, "anvil": kind_anvil, "stratus": kind_stratus, "altocumulus": kind_altocumulus,
         "cirrus": kind_cirrus, "lenticular": kind_lenticular, "roll": kind_roll}


# ------------------------------------------------------------------------------------------------------------------ the scene
def volume_material(name, recipe, density, width):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = tuple(recipe.get("tint", (1.0, 1.0, 1.0))) + (1.0,)
    pv.inputs["Anisotropy"].default_value = recipe.get("anisotropy", 0.4)
    nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0 / recipe.get("stretch", 1.0), 1.0, 1.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = recipe.get("noise", 27.0) / width
    noise.inputs["Detail"].default_value = 10.0
    noise.inputs["Roughness"].default_value = 0.62
    noise.inputs["Distortion"].default_value = 0.25
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    erode = nt.nodes.new("ShaderNodeMapRange")
    erode.inputs["From Min"].default_value, erode.inputs["From Max"].default_value = recipe.get("erode", (0.30, 0.62))
    nt.links.new(noise.outputs["Fac"], erode.inputs["Value"])
    last = erode.outputs["Result"]
    if recipe.get("floor", False):                                  # a flat base: the density rises over the first stretch above it
        flo = nt.nodes.new("ShaderNodeMapRange")
        flo.inputs["From Min"].default_value, flo.inputs["From Max"].default_value = 0.20, 0.80
        nt.links.new(sep.outputs["Z"], flo.inputs["Value"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(last, mul.inputs[0])
        nt.links.new(flo.outputs["Result"], mul.inputs[1])
        last = mul.outputs["Value"]
    dens = nt.nodes.new("ShaderNodeMath")
    dens.operation = "MULTIPLY"
    dens.inputs[1].default_value = density
    nt.links.new(last, dens.inputs[0])
    nt.links.new(dens.outputs["Value"], pv.inputs["Density"])
    pv.inputs["Absorption Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    if recipe.get("absorb", 0.0) > 0:                               # a storm cloud: the scattering colour (the albedo) is lower at the base and rises to white towards the top
        grad = nt.nodes.new("ShaderNodeMapRange")                   # (Principled Volume absorbs what its colour does not scatter, so a grey colour is a dark cloud)
        grad.inputs["From Min"].default_value, grad.inputs["From Max"].default_value = 0.5, recipe.get("absorb_top", 6.0)
        grad.inputs["To Min"].default_value, grad.inputs["To Max"].default_value = 1.0 - recipe["absorb"], 1.0
        nt.links.new(sep.outputs["Z"], grad.inputs["Value"])
        rgb = nt.nodes.new("ShaderNodeCombineColor")
        for ch in ("Red", "Green", "Blue"):
            nt.links.new(grad.outputs["Result"], rgb.inputs[ch])
        nt.links.new(rgb.outputs["Color"], pv.inputs["Color"])
    return mat


def make_shell(sc, name, elements, scale, density, centre, recipe, width, resolution):
    mb = bpy.data.metaballs.new(name)
    mb.resolution = mb.render_resolution = resolution
    mb.threshold = 0.6
    ob = bpy.data.objects.new(name, mb)
    sc.collection.objects.link(ob)
    for el in elements:
        c = centre + (Vector(el["co"]) - centre) * scale
        e = mb.elements.new(type=el["type"])
        e.co = (c.x, c.y, c.z)
        e.radius = el["radius"] * scale * 1.25
        e.stiffness = 2.0
        if "size" in el:
            e.size_x, e.size_y, e.size_z = (el["size"][0] * scale, el["size"][1] * scale, el["size"][2] * scale)
        if "rotation" in el:
            e.rotation = el["rotation"]
    mb.materials.append(volume_material(name + "_m", recipe, density, width))
    return ob


def render_cloud(recipe, out_path, quick=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    rnd = random.Random(recipe.get("seed", 1))
    width = recipe.get("width", 9.0)
    elements = KINDS[recipe["kind"]](rnd, **{k: v for k, v in recipe.items() if k in ("width", "height", "anvil", "rows", "layers", "wisps", "girth")})
    def reach(e, axis):                                              # how far an element reaches from its centre along an axis (flattened and long ones reach further than their radius)
        size = e.get("size", (0.0, 0.0, 0.0))
        return e["radius"] * 1.25 + (max(size) if e["type"] == "CAPSULE" else size[axis])
    xs = [e["co"][0] + s * reach(e, 0) for e in elements for s in (-1, 1)]
    zs = [e["co"][2] + s * reach(e, 2) for e in elements for s in (-1, 1)]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    pad = 0.08 * max(x1 - x0, z1 - z0)
    if recipe.get("floor"):
        z0 = max(z0, 0.15)
    x0, x1, z0, z1 = x0 - pad, x1 + pad, z0 - pad, z1 + pad
    span_x, span_z = x1 - x0, z1 - z0
    px = recipe.get("pixels", 1400)
    px_w = px // 2 if quick else px
    px_h = max(64, round(px_w * span_z / span_x))
    centre = Vector(((x0 + x1) / 2, 0.0, (z0 + z1) / 2))
    density = recipe.get("density", 12.0)
    resolution = max(0.02, 0.006 * span_x)
    for name, scale, share in (("shellA", 1.00, 0.35), ("shellB", 0.86, 0.40), ("shellC", 0.72, 0.55)):
        make_shell(sc, name, elements, scale, density * share, centre, recipe, width, resolution)
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    wn = world.node_tree
    for n in list(wn.nodes):
        wn.nodes.remove(n)
    bg = wn.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = tuple(recipe.get("sky", (0.50, 0.66, 0.98))) + (1.0,)
    bg.inputs["Strength"].default_value = recipe.get("ambient", 0.9)
    wo = wn.nodes.new("ShaderNodeOutputWorld")
    wn.links.new(bg.outputs["Background"], wo.inputs["Surface"])
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = recipe.get("sun", 5.0)
    sun.angle = math.radians(3.0)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(recipe.get("sun_elevation", 62.0)), 0, math.radians(-40))      # the light travels to the right, away from the camera, and down
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"                                    # (the scale is the width, whatever the shape of the picture)
    cam.ortho_scale = span_x
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    co.location = (centre.x, -60.0, centre.z)
    co.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = co
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24 if quick else recipe.get("samples", 64)
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.volume_bounces = recipe.get("bounces", 12)
    sc.cycles.volume_step_rate = recipe.get("step_rate", 1.0)
    sc.cycles.volume_max_steps = 1024
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = px_w, px_h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.render.filepath = out_path
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"cloud {recipe['id']}: {len(elements)} balls, {px_w}x{px_h}, {time.time() - t0:.0f} s -> {out_path}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--cloud", nargs="*", default=[])
    ap.add_argument("--quick", action="store_true", help="half size, few samples (for choosing a shape)")
    ap.add_argument("--out", default=os.path.join(PLATES, "renders"))
    args = ap.parse_args(argv)
    from figs.clouds import clouds
    os.makedirs(args.out, exist_ok=True)
    for recipe in clouds():
        if args.all or recipe["id"] in args.cloud:
            render_cloud(recipe, os.path.join(args.out, recipe["id"] + ".png"), quick=args.quick)


if __name__ == "__main__":
    main()
