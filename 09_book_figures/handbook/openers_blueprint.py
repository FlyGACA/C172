"""The blueprint-style opening pictures: gold lines on the cover's deep blue, with a fine grid and a compass rose.

    python3 openers_blueprint.py aircraft [w h]     renders/opener-lineart.png (blender/render_lineart.py) -> out/openers/opener-blueprint-aircraft.jpg
    python3 openers_blueprint.py aerodrome [w h]    data/oeth_plan.json (the book's open plan of Thumamah) -> out/openers/opener-blueprint-aerodrome.jpg

The aerodrome is drawn in plan with north to the left (the runway across the picture): the AIP's runway and stopways, the open plan's pavements and roofs, and
the circuit west of the runway as a dashed track. Decorative: no numbers, no callouts."""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, GOLD, PALE = (9, 22, 48), (233, 188, 96), (150, 180, 240)


def ground(w, h):
    """Deep blue, a little lighter in the middle, with a fine grid."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.75)) ** 2)
    k = np.clip(1.0 - r, 0, 1)[..., None]
    a = np.array(NAVY, dtype=np.float32) * (0.72 + 0.6 * k) + np.array((10, 26, 58), dtype=np.float32) * 0.5 * k
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    step = w / 44.0
    for i in range(int(w / step) + 2):
        d.line([i * step, 0, i * step, h], fill=PALE + (20 if i % 4 else 38,), width=1)
    for j in range(int(h / step) + 2):
        d.line([0, j * step, w, j * step], fill=PALE + (20 if j % 4 else 38,), width=1)
    im.alpha_composite(g)
    return im


def rose(w, h, cx, cy, r, north=0.0, colour=PALE, alpha=70):
    """Rings, ticks and a 16-point star; `north` turns it (degrees clockwise from up)."""
    k = 3
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = colour + (alpha,)
    X, Y, R = cx * k, cy * k, r * k
    for f, wd in ((1.0, 3), (0.92, 2), (0.66, 2), (0.36, 2)):
        d.ellipse([X - R * f, Y - R * f, X + R * f, Y + R * f], outline=c, width=wd)
    for a in range(0, 360, 5):
        t = math.radians(a + north)
        f0 = 0.92 if a % 30 == 0 else 0.955 if a % 10 == 0 else 0.975
        d.line([X + R * f0 * math.sin(t), Y - R * f0 * math.cos(t), X + R * math.sin(t), Y - R * math.cos(t)], fill=c, width=2)
    for i in range(16):
        t = math.radians(i * 22.5 + north)
        length = 1.2 if i % 4 == 0 else 0.86 if i % 2 == 0 else 0.6
        tip = (X + R * length * math.sin(t), Y - R * length * math.cos(t))
        for sgn in (-1, 1):
            d.line([(X + R * 0.14 * math.sin(t + sgn * 0.42), Y - R * 0.14 * math.cos(t + sgn * 0.42)), tip], fill=c, width=2)
    t = math.radians(north)                                # the north point, a small gold arrowhead outside the outer ring
    tip = (X + R * 1.3 * math.sin(t), Y - R * 1.3 * math.cos(t))
    for sgn in (-1, 1):
        d.line([tip, (X + R * 1.2 * math.sin(t + sgn * 0.03), Y - R * 1.2 * math.cos(t + sgn * 0.03))], fill=GOLD + (220,), width=4)
    return im.resize((w, h), Image.LANCZOS)


def finish(im, name):
    w, h = im.size
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = 1.0 - 0.34 * np.clip((((xx / w - 0.5) / 0.72) ** 2 + ((yy / h - 0.5) / 0.72) ** 2), 0, 1) ** 1.5
    a = a * vig[..., None] + np.random.default_rng(5).normal(0, 1.4, (h, w, 1)).astype(np.float32)
    os.makedirs(os.path.join(HERE, "out", "openers"), exist_ok=True)
    out = os.path.join(HERE, "out", "openers", name + ".jpg")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").save(out, quality=92)
    print(out, (w, h))


def glow_lines(im, layer, blur):
    g = layer.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(g)
    im.alpha_composite(layer)


def aircraft(w, h):
    src = Image.open(os.path.join(HERE, "renders", "opener-lineart.png")).convert("RGBA").resize((w, h), Image.LANCZOS)
    a = np.asarray(src, dtype=np.float32) / 255.0
    alpha = a[..., 3]
    line = alpha * np.clip(1.0 - a[..., :3].mean(axis=2) * 1.15, 0, 1)
    im = ground(w, h)
    ys, xs = np.nonzero(alpha > 0.5)
    cx, cy = float(xs.mean()), float(ys.mean())
    im.alpha_composite(rose(w, h, cx, cy, 0.46 * h))
    d = ImageDraw.Draw(im)
    for f in (0.0,):                                       # the cross of the drawing's axes, fine
        d.line([0, cy, w, cy], fill=PALE + (40,), width=1)
        d.line([cx, 0, cx, h], fill=PALE + (40,), width=1)
    body = np.zeros((h, w, 4), dtype=np.float32)
    body[..., :3] = np.array((16, 38, 80), dtype=np.float32)
    body[..., 3] = alpha * 205.0
    im.alpha_composite(Image.fromarray(body.astype(np.uint8), "RGBA"))
    lines = np.zeros((h, w, 4), dtype=np.float32)
    lines[..., :3] = np.array(GOLD, dtype=np.float32)
    lines[..., 3] = np.clip(line * 1.25, 0, 1) * 255.0
    glow_lines(im, Image.fromarray(lines.astype(np.uint8), "RGBA"), w / 520.0)
    finish(im, "opener-blueprint-aircraft")


def aerodrome(w, h):
    plan = json.load(open(os.path.join(HERE, "data", "oeth_plan.json")))
    k = 3
    L, HALF = plan["runway"]["length_m"], plan["runway"]["width_m"] / 2.0
    m = w * k / 7700.0                                     # pixels a metre
    x0, y0 = (w * k - L * m) / 2.0, 0.24 * h * k           # the threshold of 17 on the picture; the runway's centreline
    P = lambda t, s: (x0 + s * m, y0 + t * m)              # north to the left, west down
    im = ground(w, h)
    im.alpha_composite(rose(w, h, (x0 + 0.5 * L * m) / k, (y0 + 825.0 * m) / k, 0.5 * h, north=-90.0))
    fill = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    line = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    df, dl = ImageDraw.Draw(fill), ImageDraw.Draw(line)
    for p in plan["pavements"]:
        ring = [P(t, s) for t, s in p["ring"]]
        df.polygon(ring, fill=(22, 48, 96, 215))
        dl.line(ring + [ring[0]], fill=GOLD + (200,), width=3, joint="curve")
        for hole in p.get("holes", []):
            hr = [P(t, s) for t, s in hole]
            df.polygon(hr, fill=(0, 0, 0, 0))
            dl.line(hr + [hr[0]], fill=GOLD + (150,), width=2)
    for b in plan["buildings"]:
        ring = [P(t, s) for t, s in b["ring"]]
        df.polygon(ring, fill=(40, 70, 130, 230))
        dl.line(ring + [ring[0]], fill=GOLD + (230,), width=3)
    for pts in plan["lines"].values():
        dl.line([P(t, s) for t, s in pts], fill=PALE + (120,), width=3)
    rw = [P(-HALF, 0), P(-HALF, L), P(HALF, L), P(HALF, 0)]
    df.polygon(rw, fill=(30, 60, 118, 240))
    dl.line(rw + [rw[0]], fill=GOLD + (255,), width=5)
    for a, b in ((-plan["runway"]["stopway_north_m"], 0), (L, L + plan["runway"]["stopway_south_m"])):
        st = [P(-HALF, a), P(-HALF, b), P(HALF, b), P(HALF, a)]
        dl.line(st + [st[0]], fill=GOLD + (170,), width=3)
    s = 120.0
    while s < L - 120.0:                                   # the centreline
        dl.line([P(0, s), P(0, s + 30.0)], fill=(255, 240, 210, 230), width=3)
        s += 60.0
    for s0 in (6.0, L - 36.0):                             # the threshold stripes
        for j in range(8):
            t = -HALF + 4.0 + j * (2 * HALF - 8.0) / 7.0
            dl.line([P(t, s0), P(t, s0 + 30.0)], fill=(255, 240, 210, 230), width=4)
    D, out = 1650.0, 1300.0                                # the circuit west of the runway: a rounded rectangle, dashed
    R = 330.0
    pts = []
    def arc(ct, cs, a0, a1):
        for i in range(25):
            a = math.radians(a0 + (a1 - a0) * i / 24.0)
            pts.append((ct + R * math.cos(a), cs + R * math.sin(a)))
    pts += [(0.0, L * 0.7), (0.0, -out + R)]
    arc(R, -out + R, 180, 270)
    pts.append((D - R, -out))
    arc(D - R, -out + R, 270, 360)
    pts.append((D, L + out - R))
    arc(D - R, L + out - R, 0, 90)
    pts.append((R, L + out))
    arc(R, L + out - R, 90, 180)
    pts.append((0.0, L * 0.7))
    dash, gap, on, acc, run = 52.0, 40.0, True, 0.0, [pts[0]]
    dense = []
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(t1 - t0, s1 - s0) / 6.0))
        dense += [(t0 + (t1 - t0) * i / n, s0 + (s1 - s0) * i / n) for i in range(n)]
    for q0, q1 in zip(dense, dense[1:]):
        acc += math.hypot(q1[0] - q0[0], q1[1] - q0[1])
        if on:
            run.append(q1)
        if acc >= (dash if on else gap):
            if on and len(run) > 1:
                dl.line([P(t, s) for t, s in run], fill=(255, 214, 128, 255), width=6, joint="curve")
            on, acc, run = not on, 0.0, [q1]
    im.alpha_composite(fill.resize((w, h), Image.LANCZOS))
    glow_lines(im, line.resize((w, h), Image.LANCZOS), w / 420.0)
    finish(im, "opener-blueprint-aerodrome")


if __name__ == "__main__":
    size = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (2200, 1000)
    {"aircraft": aircraft, "aerodrome": aerodrome}[sys.argv[1]](*size)
