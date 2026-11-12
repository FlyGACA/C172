"""Cloud sprites for the handbook's weather figures: Cycles renders of procedural clouds on a transparent background, which a figure lays on its
scene the way it lays the aeroplane (an overlay {"type": "sprite", "name": "cloud-cumulus-a", ...}, see handbook/figs/clouds.py and reskin.py).

    blender -b --python 09_book_figures/blender/render_clouds.py -- --all
        or  --cloud <id> ...   --quick (half size, 24 samples)   --pixels N   --samples N   --set '{"voxel": 0.01}' (recipe keys for this run)   --suffix _try   --out <folder>

A cloud is a few volumes filled with a scattering medium (Principled Volume), lit by a physical sky and a white sun from the upper left in front, and photographed
from the front by an orthographic camera fitted to it. Where a part has a grid, the density of the medium is the grid (how deep inside the shape a point lies: it
rises gently from the surface, so no edge is sharp) times a pattern in the shader (noise eats the shape into billows and wisps). The parts:

    lumpy    heaps: metaballs (balls and flattened ellipsoids) make a closed mesh, which geometry nodes turn into the grid (Mesh to Volume, with an interior band
             for the soft edge): cumulus, towering cumulus, cumulonimbus with its anvil (a flat slab of ellipsoids), a roll, the fields of cloudlets (altocumulus,
             stratocumulus), a dying anvil
    lens     smooth lenses, the same way: a flattened sphere with a waving rim (lenticular)
    sheet    layers (stratus, nimbostratus, a veil, cirrus): a box with no grid, the pattern all in the shader: a half-thickness that tapers towards the ends and
             follows a slow noise, a foot ragged by noise that counts for more lower down, fibres of ridged noise stretched along x, patches and gaps

    kind       cumulus | congestus | cb | anvil | altocumulus | stratocumulus | lenticular | roll | stratus | nimbostratus | veil | cirrus    (see KINDS)
    seed       the random numbers of the shapes (another seed is another cloud of the same kind)
    width      across the cloud (the units are arbitrary: the camera fits the cloud); height, anvil, depth, rows, layers, girth as the kind takes them
    density    how thick the medium is (60 for the heaps, 3 to 22 for the layers)           floor   cut the heap flat at its foot
    absorb     0..1: the scattering colour at the foot goes grey, rising to white by absorb_top (a storm cloud)          tint   [r, g, b]: colour it (dust)
    erode      [low, high]: the noise below `low` is no cloud, above `high` it is full cloud (a narrow range is a ragged cloud)      noise  the size of the noise (27)
    band       the soft edge, as a fraction of the cloud's width (0.025)       voxel  the grid's cell, the same way (0.009)       elevation  look from above, in degrees
    pixels     the width of the picture       samples  path tracing samples (the finished renders use 72 to 240)
"""
import argparse
import math
import os
import random
import sys
import time

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(os.path.dirname(HERE), "handbook")
sys.path.insert(0, PLATES)


# ------------------------------------------------------------------------------------------------------------------ shapes of the lumpy clouds
def ball(x, y, z, r):
    return {"type": "BALL", "co": (x, y, z), "radius": r}


def ellipsoid(x, y, z, hx, hy, hz):
    """A flattened (or stretched) ball whose visible half-axes are hx, hy, hz (the metaball shows 0.72 of its radius, along axes scaled by `size`)."""
    m = max(hx, hy, hz)
    return {"type": "ELLIPSOID", "co": (x, y, z), "radius": m / 0.72, "size": (hx / m, hy / m, hz / m)}


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
    """A tower of billows: wide at the foot and narrowing upwards, its lobes smaller higher up, a few turrets at its head."""
    base, levels = [], max(3, round(height / (1.25 * girth)))
    for k in range(levels):
        t = k / (levels - 1)
        z = 0.9 * girth + t * (height - 1.8 * girth)
        w = width * (1.0 - 0.42 * t ** 1.2)
        r = (1.25 - 0.55 * t ** 0.8 + 0.25 * math.sin(t * math.pi)) * girth
        n = 3 if t < 0.7 else 2
        for j in range(n):
            u = (j + 0.5) / n * 2 - 1
            base.append(ball(u * w * 0.40 + rnd.uniform(-0.25, 0.25) * girth, rnd.uniform(-0.4, 0.4), z + rnd.uniform(-0.2, 0.2) * girth, r * rnd.uniform(0.85, 1.1)))
    for _ in range(2):                                                      # turrets rising from the head
        base.append(ball(rnd.uniform(-0.3, 0.3) * width * 0.6, rnd.uniform(-0.3, 0.3), height - 1.4 * girth + rnd.uniform(-0.2, 0.5) * girth, 0.7 * girth * rnd.uniform(0.9, 1.15)))
    return cauliflower(rnd, base, first=(5, 8), later=(2, 3))


# ------------------------------------------------------------------------------------------------------------------ parts: what a cloud is made of
def lumpy(elements, band=1.0, resolution=None, **extra):
    return {"part": "lumpy", "elements": elements, "band": band, "resolution": resolution, **extra}


def lens_part(centre, size, band=1.0, **extra):
    """A flattened sphere (half-axes `size` along x, y, z), its rim waving by `wobble` (a fraction of its radius)."""
    return {"part": "lens", "centre": centre, "size": size, "band": band, **extra}


def sheet_part(centre, size, **extra):
    """A box (full sizes `size`) whose medium carries the whole pattern; `pattern` is "stratus", "veil" or "cirrus" (see volume_material)."""
    return {"part": "sheet", "centre": centre, "size": size, **extra}


def flat_slab(rnd, x0, x1, z, half_y, thick, taper=1.7, bumps=True):
    """A flat layer of cloud as a row of overlapping flat ellipsoids: thick in the middle and thin at the rim (`taper` 1.7: a lens; 4: nearly even), with small
    billows along its top, so that it has a lumpy upper surface and a ragged rim and not the machined edge of a smooth lens."""
    n = max(8, round((x1 - x0) / (1.1 * thick)))
    cx, hx = (x0 + x1) / 2, (x1 - x0) / 2
    out = []
    for i in range(n):
        u = (i + 0.5) / n * 2 - 1
        t = max(0.0, 1 - abs(u) ** taper)
        h = thick * (0.30 + 0.70 * t) * rnd.uniform(0.85, 1.15)
        w = hx / n * rnd.uniform(1.7, 2.3)
        wy = half_y * (0.30 + 0.70 * t ** 0.6) * rnd.uniform(0.85, 1.1)
        x = cx + u * hx
        out.append(ellipsoid(x, rnd.uniform(-0.25, 0.25) * half_y * 0.2, z + rnd.uniform(-0.15, 0.15) * thick, w, wy, h))
        if bumps and t > 0.25 and rnd.random() < 0.75:
            out.append(ellipsoid(x + rnd.uniform(-0.4, 0.4) * w, rnd.uniform(-0.3, 0.3) * wy, z + h * rnd.uniform(0.45, 0.8), w * 0.55, wy * 0.5, h * 0.75))
    return out


def cb_tower(rnd, width, top, girth):
    """The column of a cumulonimbus: broad at the foot, a waist, a bulging head (levels of lobes, each level as wide as the profile says), with big turrets on its sides, billows on all of it."""
    base, levels = [], max(6, round(top / (1.1 * girth)))
    for k in range(levels):
        t = k / (levels - 1)
        w = width * (0.95 - 0.8 * t + 0.85 * t * t)
        z = 0.9 * girth + t * (top - 0.9 * girth)
        lobes = max(2, round(w / (1.5 * girth)))
        r = max(0.9 * girth, w / lobes * 0.70)
        for j in range(lobes):
            u = (j + 0.5) / lobes * 2 - 1
            base.append(ball(u * w * 0.42 + rnd.uniform(-0.35, 0.35) * girth, rnd.uniform(-0.45, 0.45), z + rnd.uniform(-0.3, 0.3) * girth, r * rnd.uniform(0.75, 1.3)))
    for _ in range(max(4, round(top / (2.4 * girth)))):                        # turrets on the flanks
        t = rnd.uniform(0.04, 0.85)
        w = width * (0.95 - 0.8 * t + 0.85 * t * t)
        side = rnd.choice((-1, 1))
        base.append(ball(side * w * rnd.uniform(0.40, 0.55), rnd.uniform(-0.4, 0.4), 0.9 * girth + t * (top - 0.9 * girth), girth * rnd.uniform(1.0, 1.7)))
    return cauliflower(rnd, base, levels=2, first=(4, 7), later=(2, 3))


def kind_cb(rnd, width=5.0, height=11.0, anvil=15.0, girth=1.0, lean=0.2, **_):
    """A cumulonimbus: a tall tower of billows whose head spreads into an anvil: a thin flat slab, thick over the tower, thin and torn at its rim, longer downwind (to the right, by `lean`: 0 is even),
    with small pouches (mammatus) under it and a dome pushing up through it."""
    z_a = height * 0.84
    thick = min(0.05 * height, 0.06 * anvil)
    tower = cb_tower(rnd, width, z_a + thick * 0.4, girth)
    flare = [ellipsoid(rnd.uniform(-0.2, 0.2) * width, rnd.uniform(-0.3, 0.3), z_a - thick * 0.9, width * rnd.uniform(0.62, 0.85), width * 0.4, thick * 1.2) for _ in range(3)]
    slab = flat_slab(rnd, -(0.5 - lean) * anvil, (0.5 + lean) * anvil, z_a, anvil * 0.22, thick, taper=1.5)
    pouches = [ball(rnd.uniform(-0.3 + lean, 0.42 + lean) * anvil, rnd.uniform(-0.4, 0.4), z_a - thick * rnd.uniform(0.55, 1.0), thick * rnd.uniform(0.35, 0.6)) for _ in range(int(anvil * 1.2))]
    dome = cauliflower(rnd, [ball(0.08 * width, 0.0, z_a + thick * 0.9, width * 0.17 + 0.3 * girth), ball(-0.18 * width, 0.2, z_a + thick * 0.55, width * 0.13 + 0.22 * girth)], levels=1, first=(5, 7))
    return [lumpy(tower + flare + slab + pouches + dome)]


def kind_anvil(rnd, width=14.0, height=3.0, **_):
    """A dying anvil: a long thin slab torn at its rim, with the broken remains of the tower under it (billows, thinning upwards) and a few pouches hanging from it."""
    thick = width * 0.034
    slab = flat_slab(rnd, -0.5 * width, 0.5 * width, height, width * 0.2, thick)
    stump_base = [ball(-width * 0.14, 0.0, 0.9, 1.15), ball(-width * 0.05, 0.25, 1.35, 1.0), ball(-width * 0.20, 0.1, 1.7, 0.8), ball(-width * 0.10, 0.0, 2.15, 0.65), ball(width * 0.02, 0.1, 2.0, 0.5)]
    stump = cauliflower(rnd, stump_base, levels=2, first=(4, 6), later=(2, 3))
    hang = [ball(rnd.uniform(-width * 0.38, width * 0.38), rnd.uniform(-0.4, 0.4), height - thick - rnd.uniform(0.0, 0.35), rnd.uniform(0.35, 0.55)) for _ in range(12)]
    return [lumpy(slab + stump + hang)]


def kind_lenticular(rnd, width=8.0, layers=3, lens_density=40.0, lens_erode=(0.10, 0.38), **_):
    """A pile of lenses, smooth and almond-shaped, each a little shorter than the one under it, and each its own volume (so that a clear gap lies between them);
    thin enough in the medium that their edges are soft and a little of the sky shows through them."""
    return [lens_part((rnd.uniform(-0.2, 0.2) * k, 0.0, k * 0.95), (width * 0.5 * (1 - 0.2 * k), width * 0.2 * (1 - 0.2 * k), 0.5 * (1 - 0.08 * k)),
                      band=1.0, wobble=0.1, erode=lens_erode, detail=5.0, noise=22.0, density=lens_density) for k in range(layers)]


def kind_roll(rnd, width=9.0, height=1.5, **_):
    """A roll: a long soft cylinder, billowing: a chain of balls that thins out towards its ends, lumps of different heights, a crest of small billows."""
    n = max(6, round(width / (0.8 * height)))
    base = []
    for i in range(n):
        u = (i + 0.5) / n * 2 - 1
        t = max(0.15, 1 - abs(u) ** 2.2)
        r = height * (0.55 + 0.5 * t) * rnd.uniform(0.85, 1.1)
        base.append(ball(u * width / 2 * 0.96, rnd.uniform(-0.25, 0.25), r * 0.95 + rnd.uniform(0, 0.25) * height * t, r))
    return [lumpy(cauliflower(rnd, base, levels=1, first=(4, 6), shrink=(0.32, 0.5)))]


def cloudlet(rnd, x, y, z, size, flat):
    """One puff: a flat-bottomed ellipsoid with three or four billows on its top."""
    out = [ellipsoid(x, y, z, size, size * 0.8, size * flat)]
    for _ in range(rnd.randint(3, 4)):
        out.append(ball(x + rnd.uniform(-0.6, 0.6) * size, y + rnd.uniform(-0.2, 0.2), z + size * flat * rnd.uniform(0.35, 0.9), size * rnd.uniform(0.34, 0.5)))
    return out


def cloudlet_field(rnd, width, per_row, rows, flat=0.55, jitter=0.2, depth=2.0):
    """A field of cloudlets (altocumulus, stratocumulus): a row of separate puffs, and behind it rows of smaller ones in the gaps and a little higher (the rows go away from us),
    with clear sky between them, so that it still reads as puffs when it is drawn small."""
    out, pitch = [], width / per_row
    size = pitch * 0.40
    for r in range(rows):
        n = per_row - (r % 2)
        shrink = 1.0 - 0.18 * r
        y = r * depth / max(1, rows - 1) if rows > 1 else 0.0
        for i in range(n):
            x = -width / 2 + (i + (0.5 if r % 2 == 0 else 1.0) + rnd.uniform(-jitter, jitter)) * pitch
            sz = size * shrink * rnd.uniform(0.8, 1.15)
            out += cloudlet(rnd, x, y + rnd.uniform(-0.15, 0.15), sz * flat * 0.95 + 0.25 * r * size, sz, flat)
    return out


def kind_altocumulus(rnd, width=16.0, height=2.4, depth=1.6, rows=2, per_row=6, **_):
    return [lumpy(cloudlet_field(rnd, width, per_row, rows, flat=0.62, depth=depth))]


def kind_stratocumulus(rnd, width=16.0, height=1.8, depth=1.4, rows=2, per_row=5, **_):
    return [lumpy(cloudlet_field(rnd, width, per_row, rows, flat=0.46, jitter=0.12, depth=depth))]


def kind_sheet_parts(rnd, width=18.0, height=1.4, pattern="stratus", depth=None, **_):
    return [sheet_part((0.0, 0.0, 0.0), (width, depth or width * 0.5, height), pattern=pattern)]


def kind_screen_parts(rnd, width=14.0, height=4.0, pattern="cirrus", depth=0.8, **_):
    """A sheet turned to face the camera (the pattern is in the picture, not along the view): fibres, veils."""
    return [sheet_part((0.0, 0.0, 0.0), (width, depth, height), pattern=pattern)]


KINDS = {
    "cumulus": ("lumpy", kind_cumulus), "congestus": ("lumpy", kind_congestus),
    "cb": ("parts", kind_cb), "anvil": ("parts", kind_anvil), "lenticular": ("parts", kind_lenticular), "roll": ("parts", kind_roll),
    "altocumulus": ("parts", kind_altocumulus), "stratocumulus": ("parts", kind_stratocumulus),
    "stratus": ("parts", lambda rnd, **k: kind_sheet_parts(rnd, pattern="stratus", **k)),
    "nimbostratus": ("parts", lambda rnd, **k: kind_sheet_parts(rnd, pattern="stratus", **k)),
    "veil": ("parts", lambda rnd, **k: kind_screen_parts(rnd, pattern="veil", **k)),
    "cirrus": ("parts", lambda rnd, **k: kind_screen_parts(rnd, pattern="cirrus", **k)),
}


# ------------------------------------------------------------------------------------------------------------------ the medium (a shader)
def _n(nt, kind, **inputs):
    node = nt.nodes.new(kind)
    for k, v in inputs.items():
        node.inputs[k].default_value = v
    return node


def _math(nt, op, a=None, b=None, clamp=False):
    node = nt.nodes.new("ShaderNodeMath")
    node.operation = op
    node.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            node.inputs[i].default_value = v
        else:
            nt.links.new(v, node.inputs[i])
    return node.outputs["Value"]


def _ramp(nt, value, lo, hi, smooth=True, to_min=0.0, to_max=1.0):
    """Map Range: `value` from lo..hi to to_min..to_max, clamped (smoothstep); the ends can be numbers or sockets."""
    node = nt.nodes.new("ShaderNodeMapRange")
    node.interpolation_type = "SMOOTHSTEP" if smooth else "LINEAR"
    node.clamp = True
    for name, v in (("From Min", lo), ("From Max", hi), ("To Min", to_min), ("To Max", to_max)):
        if isinstance(v, (int, float)):
            node.inputs[name].default_value = v
        else:
            nt.links.new(v, node.inputs[name])
    nt.links.new(value, node.inputs["Value"])
    return node.outputs["Result"]


def volume_material(name, recipe, part):
    """The medium of one part: scattering white (or tinted), its density the base density times the shapes of the pattern.
    A part can carry keys of its own (erode, noise, stretch, density, detail ...) that replace the cloud's for that part."""
    recipe = {**recipe, **{k: v for k, v in part.items() if k in ("erode", "noise", "stretch", "detail", "roughness", "warp", "density", "absorb", "absorb_top", "absorb_white", "floor", "fibre", "gaps", "taper", "ragged", "haze")}}
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    scatter = nt.nodes.new("ShaderNodeVolumePrincipled")
    scatter.inputs["Color"].default_value = tuple(recipe.get("tint", (1.0, 1.0, 1.0))) + (1.0,)
    scatter.inputs["Anisotropy"].default_value = recipe.get("anisotropy", 0.55)
    scatter.inputs["Absorption Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    nt.links.new(scatter.outputs["Volume"], out.inputs["Volume"])
    width = recipe.get("width", 9.0)
    seed = recipe.get("seed", 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    noise_scale = recipe.get("noise", 27.0) / width
    stretch = recipe.get("stretch", 1.0)
    # the position, warped a little by a slow noise (so that nothing is a regular blob), shifted by the seed, stretched along x for fibres
    shift = nt.nodes.new("ShaderNodeMapping")
    shift.inputs["Location"].default_value = (seed * 7.31, seed * 3.17, seed * 5.53)
    shift.inputs["Scale"].default_value = (1.0 / stretch, 1.0, 1.0)
    nt.links.new(tc.outputs["Object"], shift.inputs["Vector"])
    warp_noise = _n(nt, "ShaderNodeTexNoise", Scale=noise_scale * 0.45, Detail=2.0, Roughness=0.5)
    nt.links.new(shift.outputs["Vector"], warp_noise.inputs["Vector"])
    centre = nt.nodes.new("ShaderNodeVectorMath")
    centre.operation = "SUBTRACT"
    nt.links.new(warp_noise.outputs["Color"], centre.inputs[0])
    centre.inputs[1].default_value = (0.5, 0.5, 0.5)
    scaled = nt.nodes.new("ShaderNodeVectorMath")
    scaled.operation = "SCALE"
    scaled.inputs["Scale"].default_value = recipe.get("warp", 0.22) * width / recipe.get("noise", 27.0) * 6.0
    nt.links.new(centre.outputs["Vector"], scaled.inputs[0])
    warped = nt.nodes.new("ShaderNodeVectorMath")
    warped.operation = "ADD"
    nt.links.new(shift.outputs["Vector"], warped.inputs[0])
    nt.links.new(scaled.outputs["Vector"], warped.inputs[1])
    detail = _n(nt, "ShaderNodeTexNoise", Scale=noise_scale, Detail=recipe.get("detail", 10.0), Roughness=recipe.get("roughness", 0.62), Distortion=0.2)
    nt.links.new(warped.outputs["Vector"], detail.inputs["Vector"])
    lo, hi = recipe.get("erode", (0.30, 0.62))
    density = _ramp(nt, detail.outputs["Fac"], lo, hi)                      # the ragged edge and the billows: noise under the threshold is no cloud
    pattern = part.get("pattern")
    z_lo = 0.5                                                              # (where the storm-cloud grey ends at the foot of the cloud)
    if pattern in ("stratus", "veil", "cirrus"):
        sx, sy, sz = part["size"]
        zc = part["centre"][2]
        z_lo = zc - sz / 2
        big = _n(nt, "ShaderNodeTexNoise", Scale=noise_scale * recipe.get("big_scale", 0.22), Detail=3.0, Roughness=0.5)      # the slow noise: where the layer is thick, where thin
        nt.links.new(warped.outputs["Vector"], big.inputs["Vector"])
        gaps = recipe.get("gaps", (0.30, 0.55))
        patches = _ramp(nt, big.outputs["Fac"], gaps[0], gaps[1], to_min=recipe.get("gap_floor", 0.0))
        # a layer: its half-thickness tapers towards its ends (a lens in section) and follows the slow noise, its sides thin out before they reach the box, so that nothing has a machined edge
        u = _math(nt, "MINIMUM", _math(nt, "DIVIDE", _math(nt, "ABSOLUTE", x), sx / 2), 1.0)
        hz = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, _math(nt, "POWER", u, recipe.get("taper", 3.0))), sz / 2)
        if pattern == "stratus":
            hz = _math(nt, "MULTIPLY", hz, patches)
        dz = _math(nt, "SUBTRACT", hz, _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", z, zc)))
        density = _math(nt, "MULTIPLY", density, _ramp(nt, dz, 0.0, _math(nt, "MULTIPLY", hz, recipe.get("lens", 0.9))))
        density = _math(nt, "MULTIPLY", density, _ramp(nt, _math(nt, "SUBTRACT", sy / 2, _math(nt, "ABSOLUTE", y)), 0.0, sy / 2 * 0.5))
        density = _math(nt, "MULTIPLY", density, _ramp(nt, _math(nt, "SUBTRACT", sx / 2, _math(nt, "ABSOLUTE", x)), 0.0, sx / 2 * recipe.get("end_fade", 0.30)))
        height01 = _math(nt, "DIVIDE", _math(nt, "SUBTRACT", z, z_lo), sz)  # 0 at the foot of the layer, 1 at its top
        if pattern == "stratus":                                            # a ragged foot (the noise has to be stronger lower down to count), a soft top
            profile = _math(nt, "MINIMUM", _math(nt, "SUBTRACT", height01, 0.45), _math(nt, "SUBTRACT", 0.69, _math(nt, "MULTIPLY", height01, 0.9)))
            shifted = _math(nt, "ADD", detail.outputs["Fac"], _math(nt, "MULTIPLY", profile, recipe.get("ragged", 0.5)))
            density = _math(nt, "MULTIPLY", density, _ramp(nt, shifted, lo, hi))
        else:                                                               # the high thin layers: fibres (ridged noise stretched along x; only its crests remain), in patches
            ridge = _n(nt, "ShaderNodeTexNoise", Scale=noise_scale * recipe.get("fibre_scale", 0.9), Detail=6.0, Roughness=0.55, Distortion=recipe.get("curl", 0.6))
            nt.links.new(warped.outputs["Vector"], ridge.inputs["Vector"])
            folded = _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", ridge.outputs["Fac"], 0.5))
            streak = _ramp(nt, folded, 0.0, recipe.get("fibre", 0.12), to_min=1.0, to_max=0.0)
            haze = recipe.get("haze", 0.0)                                  # (a veil keeps a haze between its fibres)
            fibres = _math(nt, "ADD", _math(nt, "MULTIPLY", streak, 1.0 - haze), haze)
            density = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", density, fibres), patches)
    elif recipe.get("floor"):                                               # lumpy: the flat base (the cut is a little more than a ball's radius high on a slender cloud, less on a small one)
        g = recipe.get("girth", 1.0)
        flo = _ramp(nt, z, 0.20 * g, 0.80 * g)
        density = _math(nt, "MULTIPLY", density, flo)
    density = _math(nt, "MULTIPLY", density, part.get("density", recipe.get("density", 60.0)))
    nt.links.new(density, scatter.inputs["Density"])
    if recipe.get("absorb", 0.0) > 0:                                       # a storm cloud: the scattering colour (the albedo) is lower at the base and rises to white up the cloud
        top = z_lo + part["size"][2] if pattern in ("stratus", "veil", "cirrus") else recipe.get("absorb_top", 6.0)
        grad = _ramp(nt, z, z_lo, top, smooth=True, to_min=1.0 - recipe["absorb"], to_max=recipe.get("absorb_white", 1.0))
        rgb = nt.nodes.new("ShaderNodeCombineColor")
        for ch in ("Red", "Green", "Blue"):
            nt.links.new(grad, rgb.inputs[ch])
        nt.links.new(rgb.outputs["Color"], scatter.inputs["Color"])
    return mat


# ------------------------------------------------------------------------------------------------------------------ meshes and volumes
def mesh_of_metaballs(elements, resolution):
    mb = bpy.data.metaballs.new("mb")
    mb.resolution = mb.render_resolution = resolution
    mb.threshold = 0.6
    for el in elements:
        e = mb.elements.new(type=el["type"])
        e.co = el["co"]
        e.radius = el["radius"] * 1.25
        e.stiffness = 2.0
        if "size" in el:
            e.size_x, e.size_y, e.size_z = el["size"]
    ob = bpy.data.objects.new("mb", mb)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    return mesh


def mesh_of_lens(centre, size, rings=48, wobble=0.0, rnd=None):
    """A flattened sphere (half-axes `size`), its outline wavering a little if `wobble` says so (a few slow waves round the rim, so that no lens is a perfect almond)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=rings, v_segments=rings // 2, radius=1.0)
    waves = [(rnd.randint(2, 5), rnd.uniform(0, 2 * math.pi), rnd.uniform(0.4, 1.0)) for _ in range(3)] if wobble and rnd else []
    for v in bm.verts:
        theta = math.atan2(v.co.y, v.co.x)
        k = 1.0 + wobble * sum(a * math.sin(n * theta + ph) for n, ph, a in waves)
        v.co = Vector((v.co.x * k * size[0] + centre[0], v.co.y * k * size[1] + centre[1], v.co.z * size[2] + centre[2]))
    mesh = bpy.data.meshes.new("lens")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def mesh_of_box(centre, size):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0] + centre[0], v.co.y * size[1] + centre[1], v.co.z * size[2] + centre[2]))
    mesh = bpy.data.meshes.new("box")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def soft_volume(sc, name, mesh, material, band, voxel):
    """A closed mesh as a fog volume whose density ramps up from the surface inwards over `band` (a soft edge), with the medium's shader on it."""
    ob = bpy.data.objects.new(name, mesh)
    sc.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(name + "_gn", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi, go = ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")
    m2v = ng.nodes.new("GeometryNodeMeshToVolume")
    m2v.resolution_mode = "VOXEL_SIZE"
    m2v.inputs["Voxel Size"].default_value = voxel
    m2v.inputs["Density"].default_value = 1.0
    m2v.inputs["Interior Band Width"].default_value = band
    sm = ng.nodes.new("GeometryNodeSetMaterial")
    sm.inputs["Material"].default_value = material
    ng.links.new(gi.outputs[0], m2v.inputs["Mesh"])
    ng.links.new(m2v.outputs["Volume"], sm.inputs["Geometry"])
    ng.links.new(sm.outputs["Geometry"], go.inputs[0])
    ob.modifiers.new("gn", "NODES").node_group = ng
    return ob


def hard_volume(sc, name, mesh, material):
    ob = bpy.data.objects.new(name, mesh)
    sc.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob


# ------------------------------------------------------------------------------------------------------------------ the scene
def bounds_of(parts):
    xs, zs = [], []
    for p in parts:
        if p["part"] == "lumpy":
            for e in p["elements"]:
                rx = rz = e["radius"] * 0.72 * 1.12                          # (the visible radius, and a little for the overlaps)
                if "size" in e:
                    rx, rz = rx * e["size"][0], rz * e["size"][2]
                xs += [e["co"][0] - rx, e["co"][0] + rx]
                zs += [e["co"][2] - rz, e["co"][2] + rz]
        else:
            c, s = p["centre"], p["size"]
            h = (s[0] / 2, s[2] / 2) if p["part"] == "sheet" else (s[0], s[2])
            xs += [c[0] - h[0], c[0] + h[0]]
            zs += [c[2] - h[1], c[2] + h[1]]
    return min(xs), max(xs), min(zs), max(zs)


def depth_of(parts):
    """How far the parts reach from the picture plane (along y), for the framing of a view from above."""
    ey = 0.0
    for p in parts:
        if p["part"] == "lumpy":
            for e in p["elements"]:
                ry = e["radius"] * 0.72 * 1.12 * (e["size"][1] if "size" in e else 1.0)
                ey = max(ey, abs(e["co"][1]) + ry)
        else:
            ey = max(ey, abs(p["centre"][1]) + (p["size"][1] / 2 if p["part"] == "sheet" else p["size"][1]))
    return ey


def lights_and_sky(sc, recipe):
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    wn = world.node_tree
    for n in list(wn.nodes):
        wn.nodes.remove(n)
    sky = wn.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(recipe.get("sky_sun_elevation", 55.0))
    sky.sun_rotation = math.radians(recipe.get("sky_sun_rotation", 140.0))
    sky.sun_disc = False
    sky.air_density = recipe.get("air", 1.0)
    sky.dust_density = recipe.get("dust", 0.6)
    sky.altitude = 200.0
    bg = wn.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = recipe.get("ambient", 0.5)
    wo = wn.nodes.new("ShaderNodeOutputWorld")
    wn.links.new(sky.outputs["Color"], bg.inputs["Color"])
    wn.links.new(bg.outputs["Background"], wo.inputs["Surface"])
    # the sun, from the upper left and in front of the cloud (the light travels to the right, away from the camera, and down) ...
    for name, energy, rotation, colour in (("sun", recipe.get("sun", 4.5), (math.radians(recipe.get("sun_elevation", 62.0)), 0, math.radians(-40)), (1.0, 0.98, 0.94)),
                                           # ... and a weaker one behind and above, on the right (the bright edge of a cloud against the sun)
                                           ("rim", recipe.get("rim", 0.8), (math.radians(-115), 0, math.radians(35)), (1.0, 0.97, 0.9)),
                                           # ... and the light the ground throws up under the cloud, a little warm
                                           ("fill", recipe.get("fill", 0.7), (math.radians(160), 0, math.radians(-20)), (1.0, 0.93, 0.82))):
        lamp = bpy.data.lights.new(name, "SUN")
        lamp.energy = energy
        lamp.angle = math.radians(4.0)
        lamp.color = colour
        ob = bpy.data.objects.new(name, lamp)
        sc.collection.objects.link(ob)
        ob.rotation_euler = rotation


def render_cloud(recipe, out_path, quick=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    rnd = random.Random(recipe.get("seed", 1))
    width = recipe.get("width", 9.0)
    way, make = KINDS[recipe["kind"]]
    args = {k: v for k, v in recipe.items() if k in ("width", "height", "anvil", "rows", "per_row", "layers", "girth", "depth", "lean", "lens_density", "lens_erode")}
    if way == "lumpy":
        parts = [lumpy(make(rnd, **args))]
    else:
        parts = make(rnd, **args)
    x0, x1, z0, z1 = bounds_of(parts)
    pad = 0.08 * max(x1 - x0, z1 - z0)
    if recipe.get("floor"):
        z0 = max(z0, 0.15)
    x0, x1, z0, z1 = x0 - pad, x1 + pad, z0 - pad, z1 + pad
    elevation = math.radians(recipe.get("elevation", 0.0))                  # a field of cloudlets is seen from a little above
    span_x = x1 - x0
    span_z = (z1 - z0) * math.cos(elevation) + 2 * depth_of(parts) * math.sin(elevation)
    px = recipe.get("pixels", 1200)
    px_w = recipe.get("pixels_override") or (px // 2 if quick else px)
    px_h = max(64, round(px_w * span_z / span_x))
    voxel = max(0.02, recipe.get("voxel", 0.009) * span_x)
    band_unit = recipe.get("band", 0.025) * span_x                           # (the soft edge is a fraction of the cloud, so a big cloud and a small one have the same crispness)
    resolution = max(0.025, 0.005 * span_x)
    for k, part in enumerate(parts):
        mat = volume_material(f"m{k}", recipe, part)
        band = part.get("band", 1.0) * band_unit
        if part["part"] == "lumpy":
            mesh = mesh_of_metaballs(part["elements"], part.get("resolution") or resolution)
            soft_volume(sc, f"p{k}", mesh, mat, band, voxel)
        elif part["part"] == "lens":
            mesh = mesh_of_lens(part["centre"], part["size"], wobble=part.get("wobble", 0.0), rnd=random.Random(recipe.get("seed", 1) * 31 + k))
            soft_volume(sc, f"p{k}", mesh, mat, band, voxel)
        else:
            hard_volume(sc, f"p{k}", mesh_of_box(part["centre"], part["size"]), mat)
    lights_and_sky(sc, recipe)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"                                           # (the scale is the width, whatever the shape of the picture)
    cam.ortho_scale = span_x
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    centre = Vector(((x0 + x1) / 2, 0.0, (z0 + z1) / 2))
    co.location = centre + Vector((0.0, -60.0 * math.cos(elevation), 60.0 * math.sin(elevation)))
    co.rotation_euler = (math.radians(90) - elevation, 0, 0)
    sc.camera = co
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = recipe.get("samples_override") or (24 if quick else recipe.get("samples", 150))
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 12
    sc.cycles.volume_bounces = recipe.get("bounces", 12)
    sc.cycles.volume_step_rate = recipe.get("step_rate", 1.5)
    sc.cycles.volume_max_steps = 1024
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = px_w, px_h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16" if recipe.get("deep") else "8"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = recipe.get("exposure", 0.0)
    sc.render.filepath = out_path
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"cloud {recipe['id']}: {len(parts)} parts, {px_w}x{px_h}, {time.time() - t0:.0f} s -> {out_path}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--cloud", nargs="*", default=[])
    ap.add_argument("--quick", action="store_true", help="half size, few samples (for choosing a shape)")
    ap.add_argument("--pixels", type=int, help="the width of the picture, whatever the recipe says")
    ap.add_argument("--samples", type=int, help="path tracing samples, whatever the recipe says")
    ap.add_argument("--set", default="{}", help='JSON of recipe keys to change for this run, e.g. \'{"voxel": 0.01, "step_rate": 2}\'')
    ap.add_argument("--suffix", default="", help="added to the file name (to keep a trial next to the finished render)")
    ap.add_argument("--out", default=os.path.join(PLATES, "renders"))
    args = ap.parse_args(argv)
    import json
    from figs.clouds import clouds
    os.makedirs(args.out, exist_ok=True)
    for recipe in clouds():
        if args.all or recipe["id"] in args.cloud:
            recipe = {**recipe, **json.loads(args.set)}
            recipe["pixels_override"], recipe["samples_override"] = args.pixels, args.samples
            render_cloud(recipe, os.path.join(args.out, recipe["id"] + args.suffix + ".png"), quick=args.quick)


if __name__ == "__main__":
    main()
