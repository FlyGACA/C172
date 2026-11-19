"""The finish of the opening pictures (figs/openers.py): the render of the model and Thumamah laid on a drawn dusk sky with a fine compass rose behind the
aeroplane, the dashed golden track from the runway to its tail, then a painted look (a Kuwahara filter: flat, soft-edged patches of colour), a split tone
toward the cover's deep blue and gold, a little grain and a vignette.

    python3 openers_post.py <name> [--quick]      renders/<name>.png + .anchors.json + cache/openers/<name>.json -> out/openers/<name>.jpg"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def sky(w, h, hz):
    """Deep blue at the top, turning through a dusty violet to amber at the horizon (hz, in pixels from the top); below it the horizon's colour."""
    stops = [(0.0, "#07122A"), (0.45, "#0F2247"), (0.72, "#3A4468"), (0.88, "#9A6E5E"), (0.97, "#E79B4E"), (1.0, "#F6B866")]
    y = np.clip(np.arange(h, dtype=np.float32) / max(hz, 1.0), 0.0, 1.0)
    out = np.zeros((h, 3), dtype=np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (y >= a) & (y <= b)
        t = ((y[m] - a) / (b - a))[:, None]
        t = t * t * (3 - 2 * t)
        out[m] = rgb(ca) * (1 - t) + rgb(cb) * t
    img = np.repeat(out[:, None, :], w, axis=1)
    rnd = np.random.default_rng(7)
    for _ in range(int(w * hz / 9000)):                    # a few faint stars, high up
        x, yy = int(rnd.uniform(0, w)), int(rnd.uniform(0, hz * 0.6))
        img[yy, x] += rnd.uniform(40, 150) * (1 - yy / (hz * 0.6))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def rose(w, h, cx, cy, r, colour=(170, 196, 255), alpha=84):
    """A fine compass rose: rings, a tick every 10 degrees, a 16-point star; drawn four times the size and reduced, for thin clean lines."""
    k = 3
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = colour + (alpha,)
    X, Y, R = cx * k, cy * k, r * k
    for f, wd in ((1.0, 3), (0.9, 2), (0.62, 2), (0.3, 2)):
        d.ellipse([X - R * f, Y - R * f, X + R * f, Y + R * f], outline=c, width=wd)
    for a in range(0, 360, 5):
        t = math.radians(a)
        f0 = 0.9 if a % 30 == 0 else 0.94 if a % 10 == 0 else 0.97
        d.line([X + R * f0 * math.sin(t), Y - R * f0 * math.cos(t), X + R * math.sin(t), Y - R * math.cos(t)], fill=c, width=2)
    for i in range(16):
        t = math.radians(i * 22.5)
        length = 1.16 if i % 4 == 0 else 0.86 if i % 2 == 0 else 0.6
        wdt = math.radians(5.0 if i % 4 == 0 else 3.4)
        tip = (X + R * length * math.sin(t), Y - R * length * math.cos(t))
        for sgn in (-1, 1):
            base_pt = (X + R * 0.16 * math.sin(t + sgn * wdt * 4), Y - R * 0.16 * math.cos(t + sgn * wdt * 4))
            d.line([base_pt, tip], fill=c, width=2)
        d.line([(X, Y), tip], fill=colour + (alpha // 2,), width=1)
    return im.resize((w, h), Image.LANCZOS)


def track(w, h, p0, p1, p2, p3, colour=(255, 206, 110)):
    """The dashed track, drawn on the picture as on the cover: a curve from p0 (on the runway) that leaves along p0 -> p1, swings round and comes up to p3
    (the tail) from p2; fractions of the picture. The dashes and their width grow along it, as if it came toward the viewer; a soft glow under them."""
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = 600
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, e = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        pts.append(((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0]) * w * k, (a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]) * h * k, t))
    u = w * k / 2200.0
    on, run, acc = True, [], 0.0
    for q0, q1 in zip(pts, pts[1:]):
        t = q0[2]
        size = 0.22 + 0.78 * t ** 1.6
        dash, gap, wd = 34.0 * u * size, 26.0 * u * size, max(2.0, 6.5 * u * size)
        acc += math.hypot(q1[0] - q0[0], q1[1] - q0[1])
        if on:
            run.append(q1[:2])
        if acc >= (dash if on else gap):
            if on and len(run) > 1:
                d.line(run, fill=colour + (255,), width=int(round(wd)), joint="curve")
                for (x, y) in (run[0], run[-1]):
                    d.ellipse([x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2], fill=colour + (255,))
            on, run, acc = not on, [q1[:2]], 0.0
    im = im.resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(w / 240.0)), im


def track3d(w, h, pts, depths, colour=(255, 206, 110)):
    """A track given as points evenly spaced in the scene, already projected: every second span a dash, so the dashes shorten with distance as they should;
    thinner with distance; a soft glow under them."""
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    near = min(depths)
    for i in range(0, len(pts) - 1, 2):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if not (-0.2 < x0 < 1.2 and -0.2 < y0 < 1.2):
            continue
        wd = max(2.0, 7.5 * k * (near / depths[i]) ** 0.7 * (w / 2200.0))
        d.line([x0 * w * k, y0 * h * k, x1 * w * k, y1 * h * k], fill=colour + (255,), width=int(round(wd)))
        for (x, y) in ((x0, y0), (x1, y1)):
            d.ellipse([x * w * k - wd / 2, y * h * k - wd / 2, x * w * k + wd / 2, y * h * k + wd / 2], fill=colour + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(w / 240.0)), im


def kuwahara(a, r):
    """a: float array (h, w, 3). For each pixel, the mean of the one of its four (r+1)-square quadrants whose brightness varies least."""
    h, w, _ = a.shape
    n = r + 1
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    pad = np.pad(a, ((r, r), (r, r), (0, 0)), mode="edge")
    padl = np.pad(lum, ((r, r), (r, r)), mode="edge")

    def box(x):                                           # the mean over n x n windows, for every top-left corner
        c = np.cumsum(np.cumsum(np.pad(x, ((1, 0), (1, 0)) + ((0, 0),) * (x.ndim - 2)), axis=0), axis=1)
        return (c[n:, n:] - c[:-n, n:] - c[n:, :-n] + c[:-n, :-n]) / (n * n)
    m = box(pad)                                          # (h + r, w + r, 3)
    m1 = box(padl)
    v = box(padl * padl) - m1 * m1
    best = None
    out = np.zeros_like(a)
    for dy in (0, r):
        for dx in (0, r):
            vq = v[dy:dy + h, dx:dx + w]
            mq = m[dy:dy + h, dx:dx + w]
            if best is None:
                best, out = vq.copy(), mq.copy()
            else:
                pick = vq < best
                best = np.where(pick, vq, best)
                out[pick] = mq[pick]
    return out


def grade(a):
    """A split tone toward the cover: the shadows to deep blue, the lights to warm gold; a little more contrast."""
    lum = (a @ np.array([0.299, 0.587, 0.114], dtype=np.float32))[..., None] / 255.0
    shadow, light = rgb("#0B1A3A"), rgb("#FFC878")
    a = a * (1 - 0.34 * (1 - lum) ** 2) + shadow * 0.34 * (1 - lum) ** 2
    a = a * (1 - 0.10 * lum ** 2) + light * 0.10 * lum ** 2
    a = (a / 255.0 - 0.5) * 1.08 + 0.5
    return np.clip(a * 255.0, 0, 255)


def main():
    name = sys.argv[1]
    src = Image.open(os.path.join(HERE, "renders", name + ".png")).convert("RGBA")
    w, h = src.size
    an = json.load(open(os.path.join(HERE, "renders", name + ".anchors.json")))["anchors"]
    rec = json.load(open(os.path.join(HERE, "cache", "openers", name + ".json")))
    hz = an["hz"][1] * h
    img = sky(w, h, hz).convert("RGBA")
    ax, ay = an["ac"]
    ro = rec.get("rose", {"at": [ax, ay - 0.02], "r": 0.44})
    img.alpha_composite(rose(w, h, ro["at"][0] * w, ro["at"][1] * h, ro["r"] * h))
    img.alpha_composite(src)
    keys = sorted(k for k in an if k.startswith("t") and k[1:].isdigit())
    if keys:
        glow, dash = track3d(w, h, [an[k] for k in keys], rec["track_depths"])
        img.alpha_composite(glow)
        img.alpha_composite(dash)
    tr = rec.get("track")
    if tr:
        p0, pe, p3 = an[tr["from"]], an[tr["through"]], an[tr["to"]]
        p1 = [p0[0] + (pe[0] - p0[0]) * 1.15, p0[1] + (pe[1] - p0[1]) * 1.15]
        p2 = [p3[0] + tr["swing"][0], p3[1] + tr["swing"][1]]
        glow, dash = track(w, h, p0, p1, p2, p3)
        img.alpha_composite(glow)
        img.alpha_composite(glow)
        img.alpha_composite(dash)
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    a = kuwahara(a, max(2, round(w / 520)))
    a = grade(a)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = 1.0 - 0.30 * np.clip((((xx / w - 0.5) / 0.75) ** 2 + ((yy / h - 0.5) / 0.75) ** 2), 0, 1) ** 1.5
    a = a * vig[..., None] + np.random.default_rng(3).normal(0, 1.6, (h, w, 1)).astype(np.float32)
    os.makedirs(os.path.join(HERE, "out", "openers"), exist_ok=True)
    out = os.path.join(HERE, "out", "openers", name + ".jpg")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").save(out, quality=90)
    print(out, (w, h))


main()
