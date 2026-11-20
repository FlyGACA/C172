"""The blueprint cover: the model as a gold line drawing over a chart-like plan of Thumamah, on the cover's deep blue.

    python3 covers_blueprint.py [w h]     renders/cover-lineart.png (blender/render_lineart.py) + data/oeth_plan.json -> out/covers/cover-blueprint.jpg

The plan is the book's open plan (data/oeth_plan.json: the AIP's runway 4 000 x 50 m and its stopways, the pavements and roofs derived from open imagery) turned
so that north points down and to the left: the runway crosses the page from the upper right (threshold 35) to the lower left (threshold 17), the aprons along its
lower right side. Its few words are the AIP's: the location indicator, the runway designators, the aerodrome reference point and the elevation."""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from openers_blueprint import ground, rose, glow_lines, NAVY, GOLD, PALE
from covers_post import page_top, PAGE

HERE = os.path.dirname(os.path.abspath(__file__))


def font(size, name="IBMPlexMono-latin-500"):
    """One of the book's own faces (FlightBag site/fonts, WOFF2), unpacked once into cache/fonts for PIL."""
    ttf = os.path.join(HERE, "cache", "fonts", name + ".ttf")
    if not os.path.exists(ttf):
        from fontTools.ttLib import TTFont
        os.makedirs(os.path.dirname(ttf), exist_ok=True)
        f = TTFont(os.path.join(os.environ.get("FLIGHTBAG", "/workspace/flightbag"), "site", "fonts", name + ".woff2"))
        f.flavor = None
        f.save(ttf)
    return ImageFont.truetype(ttf, size)


def main(w=1792, h=2400):
    plan = json.load(open(os.path.join(HERE, "data", "oeth_plan.json")))
    k = 2
    u = w / 1792.0
    L, HALF = plan["runway"]["length_m"], plan["runway"]["width_m"] / 2.0
    m = 0.52 * u * k                                       # pixels a metre
    phi = math.radians(215.0)                              # north on the page, clockwise from up
    n = (math.sin(phi), -math.cos(phi))
    wv = (-math.cos(phi), -math.sin(phi))                  # west on the page
    t17 = (330.0 * u * k, 1880.0 * u * k)                  # clear of the cover page's own lines at the foot
    P = lambda t, s: (t17[0] - n[0] * s * m + wv[0] * t * m, t17[1] - n[1] * s * m + wv[1] * t * m)     # s runs south from the threshold of 17, t west
    im = ground(w, h)
    fill = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    line = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    df, dl = ImageDraw.Draw(fill), ImageDraw.Draw(line)
    soft = (214, 178, 104)
    for p in plan["pavements"]:
        ring = [P(t, s) for t, s in p["ring"]]
        df.polygon(ring, fill=(20, 44, 92, 235))
        dl.line(ring + [ring[0]], fill=soft + (215,), width=3, joint="curve")
        for hole in p.get("holes", []):
            hr = [P(t, s) for t, s in hole]
            df.polygon(hr, fill=(0, 0, 0, 0))
            dl.line(hr + [hr[0]], fill=soft + (150,), width=2)
    for b in plan["buildings"]:
        ring = [P(t, s) for t, s in b["ring"]]
        df.polygon(ring, fill=(46, 78, 140, 240))
        dl.line(ring + [ring[0]], fill=GOLD + (240,), width=3)
    for pts in plan["lines"].values():
        dl.line([P(t, s) for t, s in pts], fill=PALE + (110,), width=3)
    rw = [P(-HALF, 0), P(-HALF, L), P(HALF, L), P(HALF, 0)]
    df.polygon(rw, fill=(28, 58, 116, 245))
    dl.line(rw + [rw[0]], fill=GOLD + (255,), width=5)
    for a, b in ((-plan["runway"]["stopway_north_m"], 0), (L, L + plan["runway"]["stopway_south_m"])):
        st = [P(-HALF, a), P(-HALF, b), P(HALF, b), P(HALF, a)]
        dl.line(st + [st[0]], fill=GOLD + (170,), width=3)
    s = 150.0
    while s < L - 150.0:
        dl.line([P(0, s), P(0, s + 30.0)], fill=(255, 240, 210, 235), width=3)
        s += 60.0
    for s0 in (6.0, L - 36.0):
        for j in range(8):
            t = -HALF + 4.0 + j * (2 * HALF - 8.0) / 7.0
            dl.line([P(t, s0), P(t, s0 + 30.0)], fill=(255, 240, 210, 235), width=3)
    for tk in range(-2000, 7000, 500):                     # the extended centreline, fine, with a tick every 500 m
        a = P(0, tk)
        dl.line([P(-18, tk), P(18, tk)], fill=PALE + (120,), width=2)
    dl.line([P(0, -2600), P(0, -plan["runway"]["stopway_north_m"])], fill=PALE + (90,), width=2)
    dl.line([P(0, L + plan["runway"]["stopway_south_m"]), P(0, L + 2600)], fill=PALE + (90,), width=2)
    D, out_, R = 1650.0, 1300.0, 330.0                     # the circuit west of the runway, dashed
    pts = []

    def arc(ct, cs, a0, a1):
        for i in range(25):
            a = math.radians(a0 + (a1 - a0) * i / 24.0)
            pts.append((ct + R * math.cos(a), cs + R * math.sin(a)))
    pts += [(0.0, L * 0.7), (0.0, -out_ + R)]
    arc(R, -out_ + R, 180, 270)
    pts.append((D - R, -out_))
    arc(D - R, -out_ + R, 270, 360)
    pts.append((D, L + out_ - R))
    arc(D - R, L + out_ - R, 0, 90)
    pts.append((R, L + out_))
    arc(R, L + out_ - R, 90, 180)
    pts.append((0.0, L * 0.7))
    dense = []
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        nn = max(1, int(math.hypot(t1 - t0, s1 - s0) / 6.0))
        dense += [(t0 + (t1 - t0) * i / nn, s0 + (s1 - s0) * i / nn) for i in range(nn)]
    on, acc, run = True, 0.0, [dense[0]]
    for q0, q1 in zip(dense, dense[1:]):
        acc += math.hypot(q1[0] - q0[0], q1[1] - q0[1])
        if on:
            run.append(q1)
        if acc >= (60.0 if on else 46.0):
            if on and len(run) > 1:
                dl.line([P(t, s) for t, s in run], fill=(255, 214, 128, 215), width=5, joint="curve")
            on, acc, run = not on, 0.0, [q1]
    # the aerodrome reference point: a small cross and ring
    arp = P(*plan.get("arp_ts", (0.0, L / 2.0)))
    dl.ellipse([arp[0] - 20, arp[1] - 20, arp[0] + 20, arp[1] + 20], outline=GOLD + (230,), width=3)
    dl.line([arp[0] - 34, arp[1], arp[0] + 34, arp[1]], fill=GOLD + (230,), width=3)
    dl.line([arp[0], arp[1] - 34, arp[0], arp[1] + 34], fill=GOLD + (230,), width=3)
    # the aeroplane
    src = Image.open(os.path.join(HERE, "renders", "cover-lineart.png")).convert("RGBA")
    box = src.getbbox()
    src = src.crop(box)
    pw = int(1560 * u)
    src = src.resize((pw, int(src.height * pw / src.width)), Image.LANCZOS)
    px0, py0 = (w - pw) // 2 + int(10 * u), int(1140 * u) - src.height // 2     # below the cover page's title and facts (they end near 600 of 2400)
    a = np.asarray(src, dtype=np.float32) / 255.0
    alpha = a[..., 3]
    ink = alpha * np.clip(1.0 - a[..., :3].mean(axis=2) * 1.15, 0, 1)
    cx, cy = px0 + pw / 2.0, py0 + src.height / 2.0
    im.alpha_composite(rose(w, h, cx, cy, 0.47 * w, north=215.0, alpha=62, marker=False))
    im.alpha_composite(fill.resize((w, h), Image.LANCZOS))
    glow_lines(im, line.resize((w, h), Image.LANCZOS), w / 520.0)
    halo = np.zeros((src.height, pw, 4), dtype=np.float32)   # a soft dark ground under the drawing, so that the plan does not show through it
    halo[..., :3] = np.array((9, 22, 50), dtype=np.float32)
    halo[..., 3] = alpha * 255.0
    hal = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hal.paste(Image.fromarray(halo.astype(np.uint8), "RGBA"), (px0, py0))
    im.alpha_composite(hal.filter(ImageFilter.GaussianBlur(w / 70.0)))
    body = np.zeros((src.height, pw, 4), dtype=np.float32)
    body[..., :3] = np.array((15, 36, 78), dtype=np.float32)
    body[..., 3] = alpha * 240.0
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay.paste(Image.fromarray(body.astype(np.uint8), "RGBA"), (px0, py0))
    im.alpha_composite(lay)
    lines = np.zeros((src.height, pw, 4), dtype=np.float32)
    lines[..., :3] = np.array((240, 196, 104), dtype=np.float32)
    lines[..., 3] = np.clip(ink * 1.3, 0, 1) * 255.0
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay.paste(Image.fromarray(lines.astype(np.uint8), "RGBA"), (px0, py0))
    glow_lines(im, lay, w / 420.0)
    # the chart's words (the AIP's): small, in the book's mono face
    d = ImageDraw.Draw(im)
    f1, f2 = font(int(30 * u)), font(int(21 * u))
    tx = lambda t, s: (P(t, s)[0] / k, P(t, s)[1] / k)
    x, y = tx(-150, 60)
    d.text((x - 24 * u, y - 4 * u), "17", font=f1, fill=GOLD + (255,), anchor="mm")
    bx, by = int(92 * u), int(1588 * u)                         # the chart's words, left of the runway and above the cover page's foot
    back = Image.new("RGBA", (w, h), (0, 0, 0, 0))             # a calm ground under them
    ImageDraw.Draw(back).rounded_rectangle([bx - 22 * u, by - 30 * u, bx + 372 * u, by + 168 * u], radius=int(14 * u), fill=(8, 20, 46, 225))
    im.alpha_composite(back.filter(ImageFilter.GaussianBlur(6 * u)))
    d = ImageDraw.Draw(im)
    d.line([bx, by - 12 * u, bx + 350 * u, by - 12 * u], fill=PALE + (150,), width=max(1, int(2 * u)))
    d.text((bx, by), "OETH", font=font(int(54 * u)), fill=GOLD + (255,))
    d.text((bx, by + 72 * u), "RWY 17/35   4000 x 50 M", font=f2, fill=(214, 226, 250, 255))
    d.text((bx, by + 102 * u), "ARP 25 12 51 N  046 38 27 E", font=f2, fill=(214, 226, 250, 255))
    d.text((bx, by + 132 * u), "ELEV 1870 FT", font=f2, fill=(214, 226, 250, 255))
    for cxm, cym in ((70, 70), (w / u - 70, 70), (70, h / u - 70), (w / u - 70, h / u - 70)):          # corner marks
        X, Y = cxm * u, cym * u
        d.line([X - 22 * u, Y, X + 22 * u, Y], fill=PALE + (150,), width=max(1, int(2 * u)))
        d.line([X, Y - 22 * u, X, Y + 22 * u], fill=PALE + (150,), width=max(1, int(2 * u)))
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    yy = np.arange(h, dtype=np.float32)[:, None, None] / h
    yv, xv = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = 1.0 - 0.36 * np.clip((((xv / w - 0.5) / 0.74) ** 2 + ((yv / h - 0.5) / 0.74) ** 2), 0, 1) ** 1.5
    a = a * vig[..., None] + np.random.default_rng(5).normal(0, 1.4, (h, w, 1)).astype(np.float32)
    top = np.clip((0.31 - yy) / 0.13, 0, 1) ** 1.2 * 0.92         # calm under the title and the facts, in the cover page's own colour: the plan fades in below them
    a = page_top(a * (1 - top) + PAGE * top)
    os.makedirs(os.path.join(HERE, "out", "covers"), exist_ok=True)
    out = os.path.join(HERE, "out", "covers", "cover-blueprint.jpg")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").save(out, quality=92)
    print(out, (w, h))


if __name__ == "__main__":
    main(*((int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else ()))
