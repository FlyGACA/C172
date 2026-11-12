"""Ground for the figures seen from above: an aerial view of the country of the Peninsula, made here (numpy and Pillow only, a second or two a picture, the same picture for the same
seed) and written to renders/terrain-<name>.png, from where a figure lays it as a sprite under its diagram:

    terrain.ensure("terrain-26-04", seed=4, kind="plain", features=("tracks", "scrub"))        # writes renders/terrain-26-04.png if it is not there
    {"name": "terrain-26-04", "at": [320, 210], "width": 640}                                   # a sprite of the plate's own canvas (its layers, or a "sprites" overlay)

    soft      how far the ground is blurred (a sigma in pixels of a picture 2560 across): the book takes a JPEG of 800 kB at most, so keep 2 to 3 for a plate full of ground
    veil      0 to 1: how far the ground is washed towards pale sand, so that a diagram laid on it stays the thing to read (0.2 to 0.4 for most figures)
    kind      plain (gravel and sand, a few wadis) | dunes (long ridges of sand) | rock (bare hills, dark gravel) | farm (the plain with fields in green circles, a village) | night
              (any of these under the moon: blue and dark, lights where there are features)
    features  tracks (pale tracks across the plain) | scrub (dark dots of bush, thicker in the wadis) | wadis (dry beds, darker) | road (a tarred road across, `road=[(x0, y0), (x1, y1)]` in
              fractions of the picture) | village (flat-roofed houses and shadows; `village=(x, y)`) | fields (circles of irrigated crop; `fields=[(x, y, radius), ...]`) | none

The look comes from a height field (fractal noise, and for dunes long ridges bent by noise) shaded from the upper left, coloured by height and by a second noise for the patches of darker
gravel, with a fine grain; the features are drawn over it with their own shadows. `size` is the size of the picture in pixels (the plate is flattened at 3 px to a canvas unit, a sprite
is laid at 4, so 2560 across does for a canvas of 640)."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(os.path.dirname(HERE), "renders")

PALETTES = {
    "plain": [(0.0, (168, 140, 100)), (0.35, (212, 186, 140)), (0.7, (232, 210, 166)), (1.0, (243, 227, 192))],
    "dunes": [(0.0, (190, 150, 100)), (0.4, (226, 190, 134)), (0.75, (240, 212, 158)), (1.0, (250, 232, 188))],
    "rock": [(0.0, (92, 76, 58)), (0.4, (150, 124, 92)), (0.75, (196, 170, 128)), (1.0, (222, 200, 160))],
    "farm": [(0.0, (172, 144, 104)), (0.35, (214, 188, 142)), (0.7, (233, 212, 168)), (1.0, (244, 229, 195))],
    "sand": [(0.0, (206, 168, 118)), (0.5, (226, 192, 142)), (1.0, (240, 214, 168))],
    "gravel": [(0.0, (176, 164, 144)), (0.5, (204, 193, 172)), (1.0, (226, 217, 198))],
    "sabkha": [(0.0, (212, 208, 194)), (0.5, (230, 227, 215)), (1.0, (244, 242, 233))],
}


def fractal(w, h, beta, rng):
    """Noise whose power falls off as 1 / f**beta (the bigger the beta, the smoother the ground), in -1 to 1, from the FFT of white noise."""
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) / f ** (beta / 2.0)
    spec[0, 0] = 0
    out = np.fft.irfft2(spec, s=(h, w))
    out -= out.min()
    out /= max(out.max(), 1e-9)
    return out * 2 - 1


def height_field(w, h, kind, rng):
    base = fractal(w, h, 2.6, rng) * 0.55 + fractal(w, h, 1.6, rng) * 0.25 + fractal(w, h, 0.6, rng) * 0.05
    if kind == "dunes":
        ang = math.radians(rng.uniform(15, 40))
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        warp = fractal(w, h, 3.2, rng) * (w * 0.09)
        phase = (xx * math.cos(ang) + yy * math.sin(ang) + warp) * (2 * math.pi / (w * 0.085))
        ridges = (np.abs(np.sin(phase * 0.5)) ** 0.8) * 2 - 1                    # long crests with sharper tops
        base = base * 0.45 + ridges * 0.6
    elif kind == "rock":
        ridged = 1.0 - np.abs(fractal(w, h, 2.2, rng))
        base = base * 0.5 + (ridged ** 2.2) * 0.9
    return base


def shade(height, az=315.0, alt=42.0, strength=4.2):
    gy, gx = np.gradient(height)
    slope = np.sqrt(gx * gx + gy * gy)
    azr, altr = math.radians(az), math.radians(alt)
    lx, ly, lz = math.cos(altr) * math.cos(azr), -math.cos(altr) * math.sin(azr), math.sin(altr)
    nz = 1.0 / np.sqrt(1.0 + (strength * slope) ** 2)
    nx, ny = -strength * gx * nz, -strength * gy * nz
    lam = nx * lx + ny * ly + nz * lz
    return np.clip(lam, 0, 1)


def ramp(values, stops):
    """A colour for each value (0 to 1) along the stops [(position, (r, g, b)), ...]."""
    v = np.clip(values, 0, 1)
    out = np.zeros(v.shape + (3,), dtype=np.float32)
    for c in range(3):
        out[..., c] = np.interp(v, [s[0] for s in stops], [s[1][c] for s in stops])
    return out


def wadi_mask(w, h, rng, width=0.012, beta=2.6):
    """Dry river beds: the places where a smooth noise passes through zero, thin and winding."""
    n = fractal(w, h, beta, rng)
    return np.exp(-(n / width) ** 2)


def to_image(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def draw_features(img, rng, features, kind, road=None, village=None, fields=None, night=False):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    unit = w / 640.0
    if "tracks" in features:
        for _ in range(5):
            x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
            ang = rng.uniform(0, math.pi)
            pts, x, y = [], x0, y0
            for _k in range(30):
                pts.append((x, y))
                ang += rng.uniform(-0.25, 0.25)
                x += math.cos(ang) * w * 0.05
                y += math.sin(ang) * w * 0.05
            d.line(pts, fill=(236, 222, 190, 110), width=max(1, int(1.6 * unit)), joint="curve")
            d.line(pts, fill=(120, 96, 66, 40), width=max(1, int(2.6 * unit)), joint="curve")
    if fields:
        for field in fields:
            fx, fy, fr = field[:3]
            fallow = len(field) > 3 and field[3] == "fallow"                       # a circle that is not planted: bare ploughed ground, the rings of the last crop faint on it
            cx, cy, r = fx * w, fy * h, fr * w
            for k, col in enumerate([(214, 190, 146, 255), (206, 180, 134, 255), (220, 196, 152, 255)] if fallow else [(70, 120, 58, 235), (96, 146, 70, 235), (62, 108, 54, 235)]):
                d.pieslice([cx - r, cy - r, cx + r, cy + r], k * 120 + rng.uniform(0, 20), (k + 1) * 120 + rng.uniform(0, 20), fill=col)
            for k in range(1, 6):
                rr = r * k / 6.0
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(150, 120, 84, 70) if fallow else (40, 84, 40, 60), width=1)
            d.line([(cx, cy), (cx + r * 0.98, cy)], fill=(235, 235, 225, 220), width=max(1, int(unit)))
            d.ellipse([cx - 2.2 * unit, cy - 2.2 * unit, cx + 2.2 * unit, cy + 2.2 * unit], fill=(235, 235, 225, 255))
    if road:
        (x0, y0), (x1, y1) = road
        pts = [(x0 * w, y0 * h), (x1 * w, y1 * h)]
        d.line(pts, fill=(60, 56, 52, 70), width=int(9 * unit))
        d.line(pts, fill=(72, 72, 78, 255), width=int(6.4 * unit))
        d.line(pts, fill=(238, 224, 150, 255), width=max(1, int(0.9 * unit)))
    if village:
        vx, vy = village
        for _ in range(26):
            x = vx * w + rng.gauss(0, 26 * unit)
            y = vy * h + rng.gauss(0, 20 * unit)
            sw, sh = rng.uniform(5, 11) * unit, rng.uniform(5, 10) * unit
            d.rectangle([x + 2.2 * unit, y + 2.2 * unit, x + sw + 2.2 * unit, y + sh + 2.2 * unit], fill=(60, 44, 30, 80))
            d.rectangle([x, y, x + sw, y + sh], fill=(244, 232, 205, 255), outline=(190, 170, 130, 255))
            if night:
                d.rectangle([x + sw * 0.3, y + sh * 0.3, x + sw * 0.6, y + sh * 0.6], fill=(255, 214, 120, 255))
        for _ in range(7):
            x, y = vx * w + rng.gauss(0, 34 * unit), vy * h + rng.gauss(0, 26 * unit)
            r = rng.uniform(2.2, 3.6) * unit
            d.ellipse([x - r + 1.4 * unit, y - r + 1.4 * unit, x + r + 1.4 * unit, y + r + 1.4 * unit], fill=(40, 40, 30, 70))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(78, 118, 62, 255))


def build(w, h, seed, kind="plain", features=("scrub", "wadis"), road=None, village=None, fields=None, night=False, veil=0.0, soft=2.4, bump=None, bump_strength=0.55, darken=1.0):
    rng = np.random.default_rng(seed)
    prng = random.Random(seed)
    base_kind = "plain" if kind == "night" else kind
    if base_kind in ("apron", "sabkha", "sand", "gravel"):
        return special(w, h, seed, base_kind, features, veil, soft)
    height = height_field(w, h, base_kind, rng)
    if bump is not None:                                                         # a raised shape (a hill): a smooth dome added to the height, so that the light finds its slopes
        height = height + bump * bump_strength
    hn = (height - height.min()) / max(height.max() - height.min(), 1e-9)
    lam = shade(hn * (0.012 * w), strength=(1.0 if base_kind != "dunes" else 1.5) * (3.0 if bump is not None else 1.0))
    lam = (lam - lam.mean()) * 2.2 + 0.85
    stops = PALETTES.get(base_kind, PALETTES["plain"])
    col = ramp(hn, stops)
    patch = fractal(w, h, 1.8, rng)
    col *= (1.0 + 0.10 * patch[..., None])                                       # patches of darker gravel
    gravel = np.clip(fractal(w, h, 0.9, rng), -1, 1)
    col *= (1.0 + 0.045 * gravel[..., None])                                     # the fine grain
    col *= np.clip(lam, 0.55, 1.25)[..., None]
    if "wadis" in features:
        m = wadi_mask(w, h, rng, width=0.022 if base_kind != "rock" else 0.03)
        bed = np.array([236.0, 220.0, 184.0], dtype=np.float32)                        # a dry bed: pale sand between darker banks
        bank = np.array([128.0, 100.0, 66.0], dtype=np.float32)
        edge = np.clip(np.abs(np.gradient(m, axis=0)) + np.abs(np.gradient(m, axis=1)), 0, 1) * 9.0
        col = col * (1 - 0.7 * m[..., None]) + bed * (0.7 * m[..., None]) * 1.0
        col = col * (1 - np.clip(edge, 0, 0.5)[..., None]) + bank * np.clip(edge, 0, 0.5)[..., None]
    if darken != 1.0:
        col = col * darken
    if veil:
        col = col * (1 - veil) + np.array([244.0, 233.0, 205.0], dtype=np.float32) * veil
    img = to_image(col).filter(ImageFilter.GaussianBlur(soft * w / 2560.0))      # soft, like a photograph out of focus: the book takes a JPEG of 800 kB at most, and fine grain costs most
    d = ImageDraw.Draw(img, "RGBA")
    unit = w / 640.0
    if "scrub" in features:
        wad = wadi_mask(w, h, np.random.default_rng(seed + 1), width=0.03)
        for _ in range(int(w * h / 3400)):
            x, y = prng.uniform(0, w - 1), prng.uniform(0, h - 1)
            if prng.random() > 0.12 + 0.85 * float(wad[int(y), int(x)]):
                continue
            r = prng.uniform(1.4, 3.2) * unit
            d.ellipse([x - r + 0.8 * unit, y - r + 0.8 * unit, x + r + 0.8 * unit, y + r + 0.8 * unit], fill=(70, 56, 40, 60))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(92 + prng.randint(-12, 12), 100 + prng.randint(-10, 14), 62, 255))
    draw_features(img, prng, features, base_kind, road, village, fields, night=(kind == "night" or night))
    if kind == "night" or night:
        arr = np.asarray(img).astype(np.float32)
        arr = arr * np.array([0.20, 0.27, 0.46], dtype=np.float32) + np.array([6, 10, 22], dtype=np.float32)
        img = to_image(arr)
    return img.filter(ImageFilter.GaussianBlur(0.5))


SPECIAL_NOTE = None


def ensure(name, size=(2560, 1600), seed=1, kind="plain", features=("scrub", "wadis"), road=None, village=None, fields=None, night=False, veil=0.0, soft=2.4):
    """Make renders/<name>.png if it is not there; returns its path."""
    path = os.path.join(RENDERS, name + ".png")
    if not os.path.exists(path):
        os.makedirs(RENDERS, exist_ok=True)
        build(size[0], size[1], seed, kind, tuple(features), road, village, fields, night, veil, soft).save(path, optimize=False, compress_level=3)
    return path


# ---- special grounds: a slab of concrete, a salt flat, soft sand, loose gravel; and pieces of ground cut to a shape -------------------------------------------------------------------

def special(w, h, seed, kind, features, veil, soft):
    rng = np.random.default_rng(seed)
    prng = random.Random(seed)
    unit = w / 640.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    grain = fractal(w, h, 0.9, rng)
    patch = fractal(w, h, 2.0, rng)
    if kind == "apron":                                                          # concrete in slabs, each a little different, with joints, oil, rubber, and a sweep of dust
        base = np.array([200.0, 201.0, 198.0], dtype=np.float32)
        slab = max(8, int(round(46 * unit)))
        sy, sx = (yy // slab).astype(np.int32), (xx // slab).astype(np.int32)
        tone = (np.random.default_rng(seed + 5).random((int(sy.max()) + 1, int(sx.max()) + 1)) - 0.5) * 0.04
        col = base * (1.0 + tone[sy, sx])[..., None]
        col *= (1.0 + 0.05 * patch[..., None] + 0.012 * grain[..., None])
        wob = fractal(w, h, 3.0, rng) * 1.1 * unit
        jx = np.abs(((xx + wob) % slab) - slab / 2.0)
        jy = np.abs(((yy + wob) % slab) - slab / 2.0)
        joint = np.maximum(np.exp(-(((slab / 2.0 - jx) / (0.9 * unit)) ** 2)), np.exp(-(((slab / 2.0 - jy) / (0.9 * unit)) ** 2)))
        col *= (1.0 - 0.17 * joint)[..., None]
        stain = np.clip(fractal(w, h, 2.4, rng) - 0.35, 0, 1)
        col *= (1.0 - 0.28 * stain)[..., None] * np.array([1.0, 0.985, 0.96], dtype=np.float32)
        col += ((0.5 * (1.0 + shade(patch * 0.01 * w, strength=1.0)) - 0.6) * 5.0)[..., None]
    elif kind == "sabkha":                                                       # a salt flat: a pale crust cracked into polygons, dark where it is wet
        n = 26 + int(w * h / (24.0 * 24.0 * unit * unit * 16.0))
        srng = np.random.default_rng(seed + 2)
        pts = np.stack([srng.random(n) * w, srng.random(n) * h], axis=1).astype(np.float32)
        best = np.full((h, w), 1e9, dtype=np.float32)
        label = np.zeros((h, w), dtype=np.int32)
        for i, (px, py) in enumerate(pts):
            dd = (xx - px) ** 2 + (yy - py) ** 2
            better = dd < best
            best = np.where(better, dd, best)
            label = np.where(better, i, label)
        edge = ((label != np.roll(label, 1, axis=0)) | (label != np.roll(label, 1, axis=1))).astype(np.uint8) * 255
        crack = np.asarray(Image.fromarray(edge, "L").filter(ImageFilter.GaussianBlur(0.75 * unit))).astype(np.float32) / 255.0
        crack = np.clip(crack * 1.9, 0, 1)
        plate = (np.random.default_rng(seed + 7).random(n) - 0.5)[label] * 0.05             # each plate of crust a little different
        stops = PALETTES["sabkha"]
        col = ramp((patch + 1) * 0.5, stops) * (1.0 + plate)[..., None]
        col *= (1.0 + 0.012 * grain[..., None])
        col *= (1.0 - 0.34 * crack)[..., None]
        wet = np.clip((fractal(w, h, 2.6, rng) - 0.30) * 5.0, 0, 1)
        col = col * (1 - 0.6 * wet[..., None]) + np.array([142.0, 144.0, 140.0], dtype=np.float32) * (0.6 * wet[..., None])
    elif kind == "sand":                                                         # soft sand: smooth, warm, with fine wind ripples
        stops = PALETTES["sand"]
        col = ramp((patch + 1) * 0.5, stops)
        ang = math.radians(rng.uniform(10, 30))
        warp = fractal(w, h, 3.0, rng) * (14.0 * unit)
        ripple = np.sin((xx * math.cos(ang) + yy * math.sin(ang) + warp) * (2 * math.pi / (9.0 * unit)))
        swell = shade(fractal(w, h, 4.4, rng) * 0.03 * w, strength=1.4)
        col *= (1.0 + 0.028 * ripple[..., None] + 0.012 * grain[..., None])
        col *= (0.93 + 0.14 * swell)[..., None]
    else:                                                                        # gravel: grey-tan ground strewn with stones
        stops = PALETTES["gravel"]
        col = ramp((patch + 1) * 0.5, stops)
        col *= (1.0 + 0.03 * grain[..., None])
    if veil:
        col = col * (1 - veil) + np.array([244.0, 233.0, 205.0], dtype=np.float32) * veil
    img = to_image(col).filter(ImageFilter.GaussianBlur(soft * w / 2560.0))
    d = ImageDraw.Draw(img, "RGBA")
    if kind == "gravel" or ("stones" in features):
        for _ in range(int(w * h / (140.0 * unit * unit))):
            x, y = prng.uniform(0, w - 1), prng.uniform(0, h - 1)
            r = prng.uniform(0.8, 1.9) * unit
            tone = prng.randint(-14, 16)
            d.ellipse([x - r + 0.5 * unit, y - r + 0.6 * unit, x + r + 0.5 * unit, y + r + 0.6 * unit], fill=(80, 70, 56, 55))
            d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=(184 + tone, 170 + tone, 146 + tone, 255))
    if kind == "apron" and "tyres" in features:
        for _ in range(4):
            x0, y0 = prng.uniform(0, w), prng.uniform(0, h)
            ang = prng.uniform(0, math.pi)
            ln = w * prng.uniform(0.1, 0.25)
            d.line([(x0, y0), (x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln)], fill=(60, 60, 62, 40), width=max(1, int(2.4 * unit)))
    return img.filter(ImageFilter.GaussianBlur(0.5))


def shape_mask(size, canvas_origin, shape, k=4.0, feather=0.8):
    """An 'L' mask (255 inside) of a shape in canvas units, drawn at k pixels a unit with its top left at canvas_origin: ("rect", x, y, w, h, r) | ("poly", [(x, y), ...]) |
    ("stroke", [(x, y), ...], width); softened at the edge by `feather` units."""
    ox, oy = canvas_origin
    big = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    d = ImageDraw.Draw(big)

    def px(pt):
        return ((pt[0] - ox) * k * 2, (pt[1] - oy) * k * 2)
    if shape[0] == "rect":
        _, x, y, w, h, r = shape
        d.rounded_rectangle([px((x, y)), px((x + w, y + h))], radius=r * k * 2, fill=255)
    elif shape[0] == "poly":
        d.polygon([px(p) for p in shape[1]], fill=255)
    else:
        pts = [px(p) for p in shape[1]]
        wd = shape[2] * k * 2
        d.line(pts, fill=255, width=int(wd), joint="curve")
        for x, y in (pts[0], pts[-1]):
            d.ellipse([x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2], fill=255)
    mask = big.resize(size, Image.LANCZOS)
    return mask.filter(ImageFilter.GaussianBlur(feather * k)) if feather else mask


def shape_box(shape, pad=2.0):
    if shape[0] == "rect":
        _, x, y, w, h, _r = shape
        return x - pad, y - pad, x + w + pad, y + h + pad
    pts = shape[1]
    half = (shape[2] / 2.0 if shape[0] == "stroke" else 0.0) + pad
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs) - half, min(ys) - half, max(xs) + half, max(ys) + half


def box_of(shape, pad=2.0):
    """The box (x0, y0, x1, y1), whole canvas units, of the piece that piece() cuts for a shape: the positions of its fields, village and road are fractions of it."""
    x0, y0, x1, y1 = shape_box(shape, pad)
    return math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)


def sprite_of(path, origin, k=4.0):
    """The sprite dict that lays a piece (an RGBA file whose top left is `origin` on the canvas) where it was cut: the alpha box, as build_plates.py crops it."""
    a = Image.open(path).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 8 else 0)
    l, t, r, b = a.getbbox()
    return {"name": os.path.splitext(os.path.basename(path))[0], "at": [round(origin[0] + (l + r) / 2.0 / k, 2), round(origin[1] + (t + b) / 2.0 / k, 2)], "width": round((r - l) / k, 2)}


def piece(name, shape, seed=1, kind="plain", features=("scrub",), veil=0.2, soft=1.6, raised=0.0, feather=0.7, fields=None, village=None, road=None, strokes=(), pad=2.0, darken=1.0):
    """A piece of ground cut to `shape` (see shape_mask), for a tile inside a figure (a rounded rectangle laid over the old drawing), a hill, a strip of wadi. Written to renders/<name>.png
    (RGBA, 4 px a unit) if it is not there; returns the sprite dict that lays it. `raised` gives the shape a dome so that the light finds slopes on it (a hill: 0.6 to 1.2); `fields`,
    `village`, `road` are positions as fractions of the piece's own box; `strokes` [(colour_rgba, width_units, [(x, y) on the canvas, ...]), ...] are drawn over the ground (a wadi bed)."""
    x0, y0, x1, y1 = shape_box(shape, pad)
    x0, y0 = math.floor(x0), math.floor(y0)
    x1, y1 = math.ceil(x1), math.ceil(y1)
    size = (int((x1 - x0) * 4), int((y1 - y0) * 4))
    path = os.path.join(RENDERS, name + ".png")
    if not os.path.exists(path):
        os.makedirs(RENDERS, exist_ok=True)
        mask = shape_mask(size, (x0, y0), shape, 4.0, feather)
        bump = None
        if raised:
            inner = shape_mask(size, (x0, y0), shape, 4.0, 0).filter(ImageFilter.GaussianBlur(0.16 * min(size)))
            arr = np.asarray(inner).astype(np.float32) / 255.0
            bump = arr / max(arr.max(), 1e-6)
        if kind == "dust":
            inside = shape_mask(size, (x0, y0), shape, 4.0, 0).filter(ImageFilter.GaussianBlur(0.09 * min(size)))
            depth = np.asarray(inside).astype(np.float32) / 255.0
            img = dust(size[0], size[1], seed, np.clip(depth * 2.2, 0, 1))
        else:
            img = build(size[0], size[1], seed, kind, tuple(features), road, village, fields, False, veil, soft, bump=bump, bump_strength=raised, darken=darken)
        img = img.convert("RGBA")
        if strokes:
            d = ImageDraw.Draw(img, "RGBA")
            for colour, width, pts in strokes:
                p = [((x - x0) * 4, (y - y0) * 4) for x, y in pts]
                d.line(p, fill=colour, width=int(width * 4), joint="curve")
        if kind == "dust":
            alpha = ImageChops.multiply(img.getchannel("A"), mask)
        else:
            alpha = mask
        img.putalpha(alpha)
        img.save(path, optimize=False, compress_level=3)
    return sprite_of(path, (x0, y0))


def dust(w, h, seed, depth=None):
    """A wall of dust seen from above: soft billows of tan, lit from the upper left, thin and pale at its edge and dense in its middle (`depth` 0 to 1: how far inside the shape), thick
    enough there to hide the ground under it (RGBA)."""
    rng = np.random.default_rng(seed)

    def up(a):
        return np.asarray(Image.fromarray(((a + 1) * 127.5).astype(np.uint8), "L").resize((w, h), Image.BICUBIC)).astype(np.float32) / 127.5 - 1.0
    puff = 1.0 - np.abs(up(fractal(max(8, w // 9), max(8, h // 9), 2.0, rng)))      # ridged noise at a large scale: round billows with soft creases between them
    mid = 1.0 - np.abs(up(fractal(max(8, w // 3), max(8, h // 3), 2.4, rng)))
    body = puff ** 1.3 * 0.78 + mid ** 1.5 * 0.22
    lit = shade(body * 0.05 * w, az=315.0, alt=46.0, strength=1.6)
    d = np.ones((h, w), dtype=np.float32) if depth is None else np.clip(depth, 0, 1)
    tone = np.clip((lit - 0.5) * 1.3 + 0.52 + (body - body.mean()) * 0.6 - 0.12 * d, 0, 1)
    dark = np.array([160.0, 118.0, 74.0], dtype=np.float32)
    midc = np.array([206.0, 168.0, 116.0], dtype=np.float32)
    light = np.array([238.0, 210.0, 162.0], dtype=np.float32)
    lo, hi = tone[..., None] * 2.0, tone[..., None] * 2.0 - 1.0
    col = np.where(tone[..., None] < 0.5, dark + (midc - dark) * lo, midc + (light - midc) * np.clip(hi, 0, 1))
    alpha = np.clip(0.34 + 0.62 * d, 0.3, 0.97)
    rgba = np.dstack([np.clip(col, 0, 255), alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA").filter(ImageFilter.GaussianBlur(2.6 * w / 2560.0 * 2.0))
