"""The finish of the cover pictures (figs/covers.py): a drawn sky under the render of the model and Thumamah, a fine compass rose, a dashed golden track, the
glow of the lamps, a painted look, the cover's deep blue and gold, grain and a vignette.

    python3 covers_post.py <name> [--quick]     renders/<name>.png + .anchors.json + cache/covers/<name>.json -> out/covers/<name>.jpg
    python3 covers_post.py mock <name> [ar|en]  the picture under the book's own cover page (title, facts, badge): out/covers/<name>-mock-<lang>.jpg

Proposals for the owner to choose from; nothing here is in the book."""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from openers_post import kuwahara, rgb
from openers_blueprint import rose as rose_layer

HERE = os.path.dirname(os.path.abspath(__file__))
LUM = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def load(name):
    src = Image.open(os.path.join(HERE, "renders", name + ".png")).convert("RGBA")
    an = json.load(open(os.path.join(HERE, "renders", name + ".anchors.json")))["anchors"]
    rec = json.load(open(os.path.join(HERE, "cache", "covers", name + ".json")))
    return src, an, rec


def gradient(w, h, hz, stops):
    """A sky: colours by height, from the top (0) to the horizon (1, at hz pixels from the top); below the horizon its colour there."""
    y = np.clip(np.arange(h, dtype=np.float32) / max(hz, 1.0), 0.0, 1.0)
    out = np.zeros((h, 3), dtype=np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (y >= a) & (y <= b)
        t = ((y[m] - a) / (b - a))[:, None]
        t = t * t * (3 - 2 * t)
        out[m] = rgb(ca) * (1 - t) + rgb(cb) * t
    return np.repeat(out[:, None, :], w, axis=1)


def stars(a, hz, per_mp=260, seed=11, top=0.8):
    """Faint stars, more of them and brighter toward the top; a few with a soft cross."""
    h, w, _ = a.shape
    rnd = np.random.default_rng(seed)
    n = int(per_mp * w * hz / 1e6)
    for _ in range(n):
        x, y = int(rnd.uniform(1, w - 1)), int(rnd.uniform(1, max(2.0, hz * top)))
        k = (1 - y / (hz * top)) ** 1.5
        b = rnd.uniform(30, 190) * k * rnd.uniform(0.3, 1.0) ** 2
        a[y, x] += b
        if b > 95:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a[y + dy, x + dx] += b * 0.35
    return a


def bloom(a, threshold=215.0, radius=14.0, strength=0.55):
    lum = a @ LUM
    hot = np.clip((lum - threshold) / (255.0 - threshold), 0, 1)[..., None] * a
    g = np.asarray(Image.fromarray(np.clip(hot, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)
    return 255.0 - (255.0 - a) * (1.0 - np.clip(g * strength / 255.0, 0, 1))


def grade(a, shadow="#0B1A3A", light="#FFC878", shadows=0.3, lights=0.1, contrast=1.08, saturation=1.0):
    lum = (a @ LUM)[..., None] / 255.0
    a = a * (1 - shadows * (1 - lum) ** 2) + rgb(shadow) * shadows * (1 - lum) ** 2
    a = a * (1 - lights * lum ** 2) + rgb(light) * lights * lum ** 2
    if saturation != 1.0:
        g = (a @ LUM)[..., None]
        a = g + (a - g) * saturation
    a = (a / 255.0 - 0.5) * contrast + 0.5
    return np.clip(a * 255.0, 0, 255)


def vignette(a, amount=0.3, grain=1.5, seed=3):
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = 1.0 - amount * np.clip((((xx / w - 0.5) / 0.74) ** 2 + ((yy / h - 0.5) / 0.74) ** 2), 0, 1) ** 1.5
    return a * v[..., None] + np.random.default_rng(seed).normal(0, grain, (h, w, 1)).astype(np.float32)


def over(base, layer):
    """A float RGB array with an RGBA picture laid on it."""
    l = np.asarray(layer, dtype=np.float32)
    al = l[..., 3:4] / 255.0
    return base * (1 - al) + l[..., :3] * al


def dashes(w, h, pts, colour=(255, 208, 116), width=7.0, dash=36.0, gap=28.0, grow=(0.25, 1.0), power=1.5):
    """A dashed track along a polyline (pixels): the dashes and their width grow along it from grow[0] to grow[1] of their size; returns its glow and itself."""
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = w * k / 1792.0
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
    done, on, run, acc = 0.0, True, [], 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(seg / 2.0))
        for i in range(n):
            q0 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            q1 = (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)
            step = seg / n
            done += step
            acc += step
            t = done / max(total, 1.0)
            size = grow[0] + (grow[1] - grow[0]) * t ** power
            if on:
                run.append((q1[0] * k, q1[1] * k))
            if acc >= (dash if on else gap) * size * (w / 1792.0):
                if on and len(run) > 1:
                    wd = max(2.0, width * u * size)
                    d.line(run, fill=colour + (255,), width=int(round(wd)), joint="curve")
                    for (x, y) in (run[0], run[-1]):
                        d.ellipse([x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2], fill=colour + (255,))
                on, run, acc = not on, [(q1[0] * k, q1[1] * k)], 0.0
    im = im.resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(w / 200.0)), im


def bezier(p0, p1, p2, p3, n=200):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, e = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def save(a, name):
    os.makedirs(os.path.join(HERE, "out", "covers"), exist_ok=True)
    out = os.path.join(HERE, "out", "covers", name + ".jpg")
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").save(out, quality=92)
    print(out, a.shape[1], a.shape[0])
    return out


def px(an, key, w, h):
    return an[key][0] * w, an[key][1] * h


BLUE_SKY = [(0.0, "#040A1C"), (0.42, "#0A1838"), (0.7, "#1B2C58"), (0.86, "#4A4A74"), (0.94, "#A66E5E"), (0.985, "#E8964A"), (1.0, "#F6BE74")]
DAWN_SKY = [(0.0, "#0C1D45"), (0.35, "#1E3A70"), (0.62, "#4D6FA5"), (0.8, "#9AACCB"), (0.91, "#E3BDB0"), (0.97, "#F5D2A8"), (1.0, "#FBE3BC")]


def night_sky(src, an, rose_at, rose_r, per_mp, k_radius, rose_alpha=54):
    """A blue-hour picture: the drawn sky and a faint rose under the render, the painted look, then the stars (on the sky only, so that they stay points)."""
    w, h = src.size
    hz = an["hz"][1] * h
    a = gradient(w, h, hz, BLUE_SKY)
    a = over(a, rose_layer(w, h, rose_at[0], rose_at[1], rose_r, colour=(150, 178, 240), alpha=rose_alpha, marker=False))
    a = over(a, src)
    a = kuwahara(a, k_radius)
    clear = 1.0 - np.asarray(src, dtype=np.float32)[..., 3:4] / 255.0
    a = a + stars(np.zeros_like(a), hz, per_mp=per_mp) * clear
    return a


def touchdown(name="cover-touchdown"):
    src, an, rec = load(name)
    w, h = src.size
    hz = an["hz"][1] * h
    a = night_sky(src, an, (an["end"][0] * w, hz - 0.02 * h), 0.40 * w, 900, max(1, round(w / 700)))
    a = bloom(a, 205.0, w / 70.0, 0.75)
    a = grade(a, shadows=0.24, lights=0.06, contrast=1.1, saturation=1.08)
    return save(vignette(a, 0.34), name)


def cockpit(name="cover-cockpit"):
    src, an, rec = load(name)
    w, h = src.size
    hz = an["hz"][1] * h
    a = night_sky(src, an, (an["end"][0] * w, hz - 0.03 * h), 0.36 * w, 800, max(1, round(w / 900)), rose_alpha=44)
    a = bloom(a, 212.0, w / 80.0, 0.6)
    a = grade(a, shadows=0.18, lights=0.06, contrast=1.08, saturation=1.06)
    return save(vignette(a, 0.3), name)


def sunrise(name="cover-sunrise"):
    src, an, rec = load(name)
    w, h = src.size
    hz = an["hz"][1] * h
    a = gradient(w, h, hz, DAWN_SKY)
    tx, ty = px(an, "tail", w, h)
    cx, cy = px(an, "mid", w, h)
    a = over(a, src)
    yy = np.arange(h, dtype=np.float32)[:, None, None]          # a morning mist along the horizon: the far plain runs into the sky's glow
    mist = np.where(yy >= hz, np.clip(1.0 - (yy - hz) / (0.06 * h), 0, 1) ** 1.4, np.clip(1.0 - (hz - yy) / (0.012 * h), 0, 1)) * 0.9
    a = a * (1 - mist) + rgb("#F8DCB6") * mist
    a = over(a, Image.fromarray(np.concatenate([np.asarray(src, dtype=np.uint8)[..., :3], (np.asarray(src, dtype=np.float32)[..., 3:4] * (yy < hz - 0.004 * h)).astype(np.uint8)], axis=2), "RGBA"))
    a = kuwahara(a, max(2, round(w / 420)))
    a = over(a, rose_layer(w, h, cx, cy, 0.46 * w, colour=(255, 244, 220), alpha=58, marker=False))
    mx, my = px(an, "rmid", w, h)
    ex, ey = px(an, "t17", w, h)
    p1 = (mx + (ex - mx) * 1.35, my + (ey - my) * 1.35)
    glow, dash = dashes(w, h, bezier((mx, my), p1, (tx + 0.24 * w, ty + 0.16 * h), (tx, ty)), colour=(255, 226, 150))
    a = over(over(a, glow), dash)
    a = bloom(a, 225.0, w / 60.0, 0.4)
    a = grade(a, shadow="#16265A", light="#FFD9A0", shadows=0.22, lights=0.12, contrast=1.08, saturation=1.12)
    return save(vignette(a, 0.26), name)


def topdown(name="cover-topdown"):
    src, an, rec = load(name)
    w, h = src.size
    a = np.asarray(src.convert("RGB"), dtype=np.float32)
    a = kuwahara(a, max(2, round(w / 420)))
    cx, cy = px(an, "t17", w, h)
    sx, sy = px(an, "s300", w, h)
    north = math.degrees(math.atan2(cx - sx, -(cy - sy)))          # the runway's direction toward 17's far side is south: north is the opposite way
    a = over(a, rose_layer(w, h, cx, cy, 0.34 * w, north=north, colour=(255, 232, 170), alpha=110, marker=False))
    tx, ty = px(an, "tail", w, h)
    nx, ny = px(an, "nose", w, h)
    dx, dy = tx - nx, ty - ny
    glow, dash = dashes(w, h, bezier((tx + dx * 3.2 - dy * 0.9, ty + dy * 3.2 + dx * 0.9), (tx + dx * 2.2 - dy * 0.2, ty + dy * 2.2 + dx * 0.2), (tx + dx * 1.0, ty + dy * 1.0), (tx, ty)),
                        colour=(255, 232, 160), grow=(0.5, 1.0))
    a = over(over(a, glow), dash)
    a = grade(a, shadow="#101E48", light="#FFD9A0", shadows=0.3, lights=0.1, contrast=1.1, saturation=1.12)
    yy = np.arange(h, dtype=np.float32)[:, None, None] / h      # the title's ground: deep blue from the top, fading out by 0.44 of the height; a little at the bottom
    top = np.clip(1.0 - yy / 0.44, 0, 1) ** 1.15 * 0.96
    bot = np.clip((yy - 0.86) / 0.14, 0, 1) ** 1.3 * 0.85
    navy = rgb("#081430")
    a = a * (1 - top) + navy * top
    a = a * (1 - bot) + navy * bot
    return save(vignette(a, 0.22), name)


def mock(name, lang="ar"):
    """The picture under the book's own cover page (tools/handbook/pdf.py of the FlightBag repository): its title, facts and badge, as the first page prints."""
    book = os.environ.get("FLIGHTBAG", "/workspace/flightbag")
    sys.path.insert(0, os.path.join(book, "tools", "handbook"))
    from html import escape
    import pdf
    import render
    from weasyprint import HTML
    import pypdfium2
    ctx = render.load_context()
    manifest = ctx["manifest"]
    t = lambda key: render.t(lang, key)
    facts = "".join(f"<li><strong>{escape(n)}</strong>{escape(label)}</li>" for n, label in render.cover_facts(ctx, lang))
    art = os.path.join(HERE, "out", "covers", name + ".jpg")
    body = (f'<section class="cover"><img class="cover-art" src="file://{art}" alt=""><div class="cover-shade"></div><div class="cover-top"><div class="brand">FLYGACA</div>'
            f'<p class="tag">{t("cover_tag")}</p><h1>{t("handbook")}</h1><p class="sub">{render.text(manifest["subtitle"], lang)}</p><ul class="facts">{facts}</ul></div>'
            f'<div class="cover-bottom"><span class="badge">{t("cover_badge")}</span><p class="edition">{t("edition")} <span dir="ltr">{manifest["edition"]}</span></p>'
            f'<p class="indep">{escape(t("not_affiliated"))}</p></div></section>')
    direction = "rtl" if lang == "ar" else "ltr"
    html = f'<!doctype html><html lang="{lang}" dir="{direction}"><head><meta charset="utf-8"><style>{pdf.PRINT_CSS}</style></head><body>{body}</body></html>'
    tmp = os.path.join(HERE, "cache", "covers", f"{name}-mock-{lang}.pdf")
    HTML(string=html, base_url=book + "/").write_pdf(tmp)
    page = pypdfium2.PdfDocument(tmp)[0].render(scale=1500 / 595.276).to_pil().convert("RGB")
    out = os.path.join(HERE, "out", "covers", f"{name}-mock-{lang}.jpg")
    page.save(out, quality=90)
    print(out, page.size)
    return out


COVER = os.path.join(os.environ.get("FLIGHTBAG", "/workspace/flightbag"), "site", "handbook", "assets", "cover.jpg")
# on the present cover (1792 x 2400): the floor of its valley, where the painted runway lies; and the course of its painted track
VALLEY = [(0, 1995), (250, 1985), (520, 1968), (700, 1958), (860, 1945), (960, 1915), (1040, 1885), (1120, 1868), (1250, 1858), (1420, 1856), (1500, 1862),
          (1560, 1880), (1640, 1912), (1700, 1938), (1700, 1946), (1610, 1976), (1500, 2016), (1400, 2052), (1290, 2078), (1200, 2150), (700, 2160),
          (500, 2128), (300, 2106), (150, 2076), (60, 2050), (0, 2040)]
OLD_TRACK = [(975, 1193), (1010, 1215), (1050, 1262), (1085, 1310), (1115, 1360), (1140, 1410), (1150, 1450), (1148, 1480), (1130, 1510), (1095, 1540),
             (1050, 1565), (1000, 1588), (950, 1610), (915, 1635), (903, 1660), (910, 1685), (935, 1705), (980, 1722), (1040, 1735), (1120, 1745),
             (1220, 1752), (1345, 1759)]


def fill_rows(a, mask, pad=3):
    """Each masked run of a row takes the colours on either side of it, blended across the run (for thin marks on a smooth sky)."""
    h, w, _ = a.shape
    out = a.copy()
    for y in np.nonzero(mask.any(axis=1))[0]:
        row = mask[y]
        xs = np.nonzero(row)[0]
        start = xs[0]
        prev = xs[0]
        runs = []
        for x in xs[1:]:
            if x != prev + 1:
                runs.append((start, prev))
                start = x
            prev = x
        runs.append((start, prev))
        for x0, x1 in runs:
            l0, r1 = max(0, x0 - pad), min(w, x1 + 1 + pad)
            cl = a[y, l0:x0].mean(axis=0) if x0 > l0 else a[y, x1 + 1:r1].mean(axis=0)
            cr = a[y, x1 + 1:r1].mean(axis=0) if r1 > x1 + 1 else cl
            t = (np.arange(x0, x1 + 1, dtype=np.float32) - x0 + 0.5) / (x1 - x0 + 1)
            out[y, x0:x1 + 1] = cl[None, :] * (1 - t[:, None]) + cr[None, :] * t[:, None]
    return out


def remake(name="cover-remake", debug=False):
    """The present cover with our aeroplane and our aerodrome: its painted aeroplane and track are taken out of its sky, the floor of its valley is replaced
    by the render of Thumamah (in the painting's own colours, row by row), the model is laid where the painted aeroplane was, and a new dashed track runs
    from our runway's far end up to its tail."""
    src, an, rec = load(name)
    w, h = src.size
    u = w / 1792.0
    P = np.asarray(Image.open(COVER).convert("RGB").resize((w, h), Image.LANCZOS), dtype=np.float32)
    rnd = np.random.default_rng(9)
    # 1 the painted aeroplane: brighter than the sky of its row; closed, spanned row by row, grown a little; filled with the sky (the margins' colour, row by row)
    x0, x1, y0, y1 = [int(v * u) for v in (105, 1465, 730, 1210)]
    margin = np.concatenate([P[:, :int(90 * u)], P[:, int(1520 * u):]], axis=1)
    skyl = np.median(P[:, :int(90 * u)], axis=1)
    skyr = np.median(P[:, int(1520 * u):], axis=1)
    lum = P[y0:y1, x0:x1] @ LUM
    bright = lum > (np.median(margin[y0:y1], axis=1) @ LUM)[:, None] + 46.0
    mk = Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * int(7 * u) + 1)).filter(ImageFilter.MinFilter(2 * int(5 * u) + 1))
    d = ImageDraw.Draw(mk)
    cx, cy, rr = 480 * u - x0, 882 * u - y0, 112 * u
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
    m = np.asarray(mk) > 0
    for y in np.nonzero(m.any(axis=1))[0]:
        xs = np.nonzero(m[y])[0]
        m[y, xs[0]:xs[-1] + 1] = True
    full = np.zeros((h, w), dtype=np.uint8)
    full[y0:y1, x0:x1] = m * 255
    soft = np.asarray(Image.fromarray(full).filter(ImageFilter.MaxFilter(2 * int(9 * u) + 1)).filter(ImageFilter.GaussianBlur(5 * u)), dtype=np.float32)[..., None] / 255.0
    xx = (np.arange(w, dtype=np.float32) / (w - 1))[None, :, None]
    sky = skyl[:, None, :] * (1 - xx) + skyr[:, None, :] * xx
    sky = sky + rnd.normal(0, 1.1, (h, w, 1)).astype(np.float32)
    A = P * (1 - soft) + sky * soft
    # 2 the painted track: a band along its course, filled across each row
    tm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(tm).line([(x * u, y * u) for x, y in OLD_TRACK], fill=255, width=int(110 * u), joint="curve")
    band = np.asarray(tm) > 0                                # near its course: every pixel warmer and brighter than the sky of its row is a dash or its glow
    warm = (A[..., 0] - A[..., 2])
    rowwarm = np.array([np.median(warm[y][~band[y]]) for y in range(h)], dtype=np.float32)
    dash_px = band & (warm > rowwarm[:, None] + 13.0)
    dm = np.asarray(Image.fromarray((dash_px * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * max(2, int(6 * u)) + 1))) > 0
    A = fill_rows(A, dm & band, pad=max(2, int(4 * u)))
    # 3 our valley: the render inside the valley's floor, each row brought to the painting's sand (the sand east of the runway, left of it in the picture)
    R = np.asarray(src, dtype=np.float32)
    rgbk = kuwahara(R[..., :3], max(1, round(w / 800)))
    vm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vm).polygon([(x * u, y * u) for x, y in VALLEY], fill=255)
    vmask = np.asarray(vm.filter(ImageFilter.GaussianBlur(7 * u)), dtype=np.float32) / 255.0
    yy = np.arange(h, dtype=np.float32)[:, None]
    vmask = vmask * np.clip((2150 * u - yy) / (95 * u), 0, 1)                      # the near ground runs out into the painting's dark foreground
    lx0, ly0 = an["t17l"][0] * w, an["t17l"][1] * h
    lx1, ly1 = an["far"][0] * w, an["far"][1] * h
    hard = np.asarray(vm) > 0
    gain = np.ones((h, 3), dtype=np.float32)
    known = []
    for y in range(int(1858 * u), int(2110 * u)):
        xl = lx0 + (lx1 - lx0) * (y - ly0) / (ly1 - ly0)
        xs = np.nonzero(hard[y, :max(0, int(xl - 16 * u))])[0]
        if len(xs) > 30 * u:
            tgt, cur = np.median(A[y, xs], axis=0), np.median(rgbk[y, xs], axis=0)
            gain[y] = np.clip(tgt / np.maximum(cur, 1.0), 0.2, 8.0)
            known.append(y)
    if known:
        gain[:known[0]] = gain[known[0]]
        gain[known[-1] + 1:] = gain[known[-1]]
        kk = int(18 * u)
        pad = np.pad(gain, ((kk, kk), (0, 0)), mode="edge")
        gain = np.stack([np.convolve(pad[:, c], np.ones(2 * kk + 1) / (2 * kk + 1), mode="valid") for c in range(3)], axis=1)
    lit = np.clip(((rgbk @ LUM) - 150.0) / 70.0, 0, 1)[..., None]      # the lamps keep their own brightness
    ours = np.clip(rgbk * (gain[:, None, :] * (1 - lit) + lit), 0, 255)
    vm3 = (vmask * (R[..., 3] / 255.0))[..., None]
    A = A * (1 - vm3) + ours * vm3
    # 4 our aeroplane: what the render shows above the horizon
    hz = an["hz"][1] * h
    pa = (R[..., 3] / 255.0) * (yy < hz - 30 * u)
    pk = kuwahara(R[..., :3], max(1, round(w / 900)))
    # the painting's light on it: a warm edge where it faces the glow (below and to the left), a cool shade on the far side
    dpx = max(2, int(5 * u))
    soft_a = np.asarray(Image.fromarray((pa * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 * u)), dtype=np.float32) / 255.0
    warm_edge = soft_a * (1.0 - np.roll(np.roll(soft_a, dpx, axis=1), -dpx, axis=0))
    cool_edge = soft_a * (1.0 - np.roll(np.roll(soft_a, -dpx, axis=1), dpx, axis=0))
    warm_edge = np.asarray(Image.fromarray((np.clip(warm_edge, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6 * u)), dtype=np.float32)[..., None] / 255.0
    cool_edge = np.asarray(Image.fromarray((np.clip(cool_edge, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2 * u)), dtype=np.float32)[..., None] / 255.0
    pk = grade(pk, shadow="#16234A", light="#FFD08A", shadows=0.22, lights=0.09, contrast=1.1, saturation=1.06)
    pk = 255.0 - (255.0 - pk) * (1.0 - 0.6 * warm_edge * (rgb("#FFC46E") / 255.0))
    pk = pk * (1.0 - 0.3 * cool_edge) + rgb("#1A2850") * 0.3 * cool_edge
    A = A * (1 - pa[..., None]) + pk * pa[..., None]
    # 5 the new track, from the runway's far end up to the tail, shrinking with distance
    tx, ty = px(an, "tail", w, h)
    fx, fy = px(an, "far", w, h)
    c = lambda x, y: (x * u, y * u)
    pts = (bezier((tx, ty), (tx + 70 * u, ty + 60 * u), c(1175, 1370), c(1160, 1460), 80)[:-1] + bezier(c(1160, 1460), c(1140, 1570), c(905, 1570), c(905, 1665), 80)[:-1]
           + bezier(c(905, 1665), c(905, 1760), (fx - 190 * u, fy - 40 * u), (fx - 6 * u, fy - 4 * u), 80))
    glow, dash = dashes(w, h, pts, colour=(255, 214, 122), width=8.5, dash=40.0, gap=30.0, grow=(1.0, 0.16), power=0.8)
    A = over(over(A, glow), dash)
    A = bloom(A, 232.0, w / 110.0, 0.35)
    if debug:
        dbg = Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))
        ImageDraw.Draw(dbg).line([(x * u, y * u) for x, y in VALLEY + VALLEY[:1]], fill=(0, 255, 255), width=2)
        dbg.save(os.path.join(HERE, "out", "covers", name + "-debug.jpg"))
    return save(A, name)


FINISH = {"cover-remake": remake, "cover-touchdown": touchdown, "cover-cockpit": cockpit, "cover-sunrise": sunrise, "cover-topdown": topdown}

if __name__ == "__main__":
    if sys.argv[1] == "mock":
        mock(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "ar")
    else:
        FINISH[sys.argv[1]]()
