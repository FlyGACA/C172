"""Helpers of worker a3 (not a figure: plates_spec.py only loads f_*.py). Plain Python, no Blender, no Pillow.

    geometry      ellipse_points, d_of, lerp, along
    glossy parts  tube (a stroke-built tube lit from the upper left), ribbon_tube (a tapering tube as nested polygons), ball (a lit sphere)
    night         night_defs (the glows of the lamps), sky_night, stars, lamp, lamp_row, beam
    shared defs   common_defs (blurs and a drop shadow, once per figure)

Every id that a piece defines starts with the prefix the figure hands in, so that two pieces of one drawing never share one."""
import math
import random

from figs import scene as S

n = S.n
pts = S.pts


# ------------------------------------------------------------------------------------------------------------------ geometry
def ellipse_points(cx, cy, rx, ry, rot=0.0, count=120, a0=0.0, a1=360.0):
    """Points round an ellipse, turned by `rot` degrees (clockwise on the page), from the angle a0 to a1 (degrees)."""
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(count + 1):
        a = math.radians(a0 + (a1 - a0) * i / count)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def d_of(points, close=False):
    return "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points) + (" Z" if close else "")


def catmull_points(points, per=8):
    """A smooth curve through the points, as many points (figs/scene.py catmull)."""
    return S.catmull(points, per)


def lerp(a, b, t):
    return a + (b - a) * t


def along(points, t):
    """The point at the fraction t of the length of a polyline, and its direction (unit vector)."""
    dist = [0.0]
    for a, b in zip(points, points[1:]):
        dist.append(dist[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    target = dist[-1] * t
    for i in range(1, len(points)):
        if dist[i] >= target:
            seg = dist[i] - dist[i - 1] or 1.0
            u = (target - dist[i - 1]) / seg
            (x0, y0), (x1, y1) = points[i - 1], points[i]
            return (lerp(x0, x1, u), lerp(y0, y1, u)), ((x1 - x0) / seg, (y1 - y0) / seg)
    (x0, y0), (x1, y1) = points[-2], points[-1]
    seg = math.hypot(x1 - x0, y1 - y0) or 1.0
    return points[-1], ((x1 - x0) / seg, (y1 - y0) / seg)


def common_defs(p):
    """Blurs and a drop shadow, once per figure; the ids are p + 'b1', p + 'b2', p + 'b4', p + 'sh' (and p + 'sh2' for a hard small one)."""
    return (f'<defs><filter id="{p}b1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9"/></filter>'
            f'<filter id="{p}b2" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2"/></filter>'
            f'<filter id="{p}b4" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
            f'<filter id="{p}sh" x="-15%" y="-15%" width="135%" height="145%"><feDropShadow dx="1.2" dy="2.6" stdDeviation="2.2" flood-color="#1B2B44" flood-opacity="0.30"/></filter>'
            f'<filter id="{p}sh2" x="-15%" y="-15%" width="135%" height="145%"><feDropShadow dx="0.6" dy="1.4" stdDeviation="1" flood-color="#1B2B44" flood-opacity="0.34"/></filter></defs>')


# ------------------------------------------------------------------------------------------------------------------ glossy parts
def tube(d, w, base="#CAD6F1", edge="#55679F", shade="#9AAEE0", light="#FFFFFF", p="a3", shadow=0.20, lift=1.0, close=False, extra=""):
    """A glossy tube along the path data `d` (strokes, lit from the upper left): a soft shadow, a dark rim, the body, a darker core a little to the lower right, a broad highlight and a thin
    specular line up and to the left. `w` is the width of the tube; `p` the figure's prefix (its common_defs blur is used)."""
    dx, dy = -w * 0.16 * lift, -w * 0.20 * lift
    sd = f'<path d="{d}" fill="none" stroke="#14233F" stroke-opacity="{n(shadow)}" stroke-width="{n(w + 1.2)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(1.6 3.4)" filter="url(#{p}b2)"/>' if shadow else ""
    return (sd
            + f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{n(w + 1.7)}" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<path d="{d}" fill="none" stroke="{base}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<path d="{d}" fill="none" stroke="{shade}" stroke-opacity="0.75" stroke-width="{n(w * 0.52)}" stroke-linecap="round" stroke-linejoin="round" transform="translate({n(-dx * 0.55)} {n(-dy * 0.55)})"/>'
            + f'<path d="{d}" fill="none" stroke="{light}" stroke-opacity="0.92" stroke-width="{n(w * 0.26)}" stroke-linecap="round" stroke-linejoin="round" transform="translate({n(dx)} {n(dy)})" filter="url(#{p}b1)"/>'
            + f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="{n(w * 0.085)}" stroke-linecap="round" stroke-linejoin="round" transform="translate({n(dx * 1.35)} {n(dy * 1.35)})"/>'
            + extra)


def offsets(points, widths):
    """Left and right edges of a ribbon of half-widths `widths` along a polyline (as two lists of points)."""
    left, right = [], []
    for i, (x, y) in enumerate(points):
        j0, j1 = max(0, i - 1), min(len(points) - 1, i + 1)
        tx, ty = points[j1][0] - points[j0][0], points[j1][1] - points[j0][1]
        norm = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / norm, tx / norm
        left.append((x + nx * widths[i], y + ny * widths[i]))
        right.append((x - nx * widths[i], y - ny * widths[i]))
    return left, right


def ribbon_tube(points, widths, colours, p="a3", shadow=0.22, lift=1.0, cap=True):
    """A tube that tapers, as nested polygons along the points (`widths` are half-widths): rim, body, core, highlight and specular, each narrower than the last and shifted towards
    the upper left in proportion to the local width, so that it reads as a lit tube. `colours` = (rim, body, core, light)."""
    rim, body, core, light = colours
    out = []
    if shadow:
        l, r = offsets(points, [w + 0.6 for w in widths])
        out.append(f'<polygon points="{pts(l + r[::-1])}" fill="#14233F" fill-opacity="{n(shadow)}" transform="translate(1.6 3.4)" filter="url(#{p}b2)"/>')
    for scale, colour, ox, oy, opacity in ((1.0, rim, 0.0, 0.0, 1.0), (0.90, body, 0.0, 0.0, 1.0), (0.56, core, 0.12, 0.16, 0.75), (0.30, light, -0.26 * lift, -0.30 * lift, 0.9), (0.10, "#FFFFFF", -0.34 * lift, -0.40 * lift, 0.95)):
        l, r = offsets(points, [w * scale for w in widths])
        shift = [(x + ox * widths[i], y + oy * widths[i]) for i, (x, y) in enumerate(l)], [(x + ox * widths[i], y + oy * widths[i]) for i, (x, y) in enumerate(r)]
        out.append(f'<polygon points="{pts(shift[0] + shift[1][::-1])}" fill="{colour}" fill-opacity="{n(opacity)}" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="0.4" stroke-linejoin="round"/>')
    return "".join(out)


def ball(uid, cx, cy, r, c0="#FFFFFF", c1="#C9D6F2", c2="#6679B4", rim=None, shadow=True, p="a3", sx=1.0, sy=1.0):
    """A lit sphere (or ellipsoid, with sx and sy): a radial gradient with its light at the upper left, an optional rim and a soft shadow. `uid` is an id for the gradient."""
    g = (f'<defs><radialGradient id="{uid}" cx="0.36" cy="0.32" r="0.78"><stop offset="0" stop-color="{c0}"/><stop offset="0.45" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient></defs>')
    sh = f'<ellipse cx="{n(cx + r * 0.12)}" cy="{n(cy + r * 0.28)}" rx="{n(r * sx)}" ry="{n(r * sy)}" fill="#14233F" fill-opacity="0.22" filter="url(#{p}b2)"/>' if shadow else ""
    edge = f' stroke="{rim}" stroke-width="{n(max(0.6, r * 0.07))}"' if rim else ""
    return g + sh + f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * sx)}" ry="{n(r * sy)}" fill="url(#{uid})"{edge}/>'


# ------------------------------------------------------------------------------------------------------------------ night
LAMP = {"w": ("#FFFFFF", "#FFF1CF", "#FFE2A0"), "r": ("#FFD6CF", "#FF5A4A", "#E0301F"), "g": ("#D9FFE9", "#33E08E", "#12A860"), "a": ("#FFF3D0", "#FFC253", "#F2962B"),
        "b": ("#E1EEFF", "#4F8DFF", "#2A5BD6"), "y": ("#FFFBD6", "#FFE66B", "#F3C21E")}


def night_defs(p):
    """The glows of lamps, once per figure: radial gradients p + 'gl-' + colour (w, r, g, a, b, y) and a beam gradient."""
    out = ["<defs>"]
    for key, (core, mid, outer) in LAMP.items():
        out.append(f'<radialGradient id="{p}gl-{key}"><stop offset="0" stop-color="{mid}" stop-opacity="0.95"/><stop offset="0.22" stop-color="{mid}" stop-opacity="0.55"/>'
                   f'<stop offset="0.55" stop-color="{outer}" stop-opacity="0.16"/><stop offset="1" stop-color="{outer}" stop-opacity="0"/></radialGradient>')
        out.append(f'<radialGradient id="{p}co-{key}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="{core}"/><stop offset="1" stop-color="{mid}"/></radialGradient>')
    out.append("</defs>")
    return "".join(out)


def lamp(p, x, y, colour="w", r=1.6, halo=1.0, glow=True):
    """A lamp seen at night: a wide soft halo, a nearer glow and a bright core."""
    big = r * 5.2 * halo
    out = ""
    if glow:
        out += f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(big)}" fill="url(#{p}gl-{colour})"/>'
    out += f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#{p}co-{colour})"/>'
    return out


def lamp_row(p, points, colour="w", r=1.6, halo=1.0):
    return "".join(lamp(p, x, y, colour, r, halo) for x, y in points)


def stars(x, y, w, h, count, seed=1, bright=0.9, fade_bottom=0.25):
    """Stars over a rectangle: mostly faint dots of different sizes, a few brighter ones with a little glow; thinner towards the bottom (the horizon)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(count):
        sx, sy = rnd.uniform(x, x + w), rnd.uniform(y, y + h)
        near_horizon = (sy - y) / h
        if rnd.random() < near_horizon * (1 - fade_bottom):
            continue
        k = rnd.random()
        r = 0.35 + 0.55 * k * k
        op = bright * (0.35 + 0.65 * k) * (1 - 0.6 * near_horizon)
        out.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(r)}" fill="#FFFFFF" fill-opacity="{n(op)}"/>')
    return "".join(out)


def sky_night(uid, x, y, w, h, horizon, glow_x=None, glow_colour="#F2A14A", glow_strength=0.34, top="#070D22", mid="#16264F", low="#3C5189"):
    """A night sky from y to the horizon (an absolute y): deep blue overhead, a lighter band at the horizon, and a warm glow of distant lights at glow_x."""
    hh = horizon - y
    out = [f'<defs>{S.gradient(uid, [(0, top), (0.55, mid), (1, low)])}</defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(hh)}" fill="url(#{uid})"/>']
    if glow_x is not None:
        out.append(f'<defs><radialGradient id="{uid}g" cx="0.5" cy="1" r="0.5"><stop offset="0" stop-color="{glow_colour}" stop-opacity="{n(glow_strength)}"/><stop offset="1" stop-color="{glow_colour}" stop-opacity="0"/></radialGradient></defs>'
                   f'<ellipse cx="{n(glow_x)}" cy="{n(horizon)}" rx="{n(w * 0.36)}" ry="{n(hh * 0.55)}" fill="url(#{uid}g)"/>')
    return "".join(out)


def beam(uid, x0, y0, x1, y1, spread0=0.8, spread1=14.0, colour="#FFF3C8", opacity=0.55, soften=2.0, p="a3"):
    """A soft cone of light from (x0, y0) to (x1, y1): a thin source widening to `spread1` half-width at the far end, brightest at the lamp and fading to nothing, a little blurred."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    poly = [(x0 + nx * spread0, y0 + ny * spread0), (x1 + nx * spread1, y1 + ny * spread1), (x1 - nx * spread1, y1 - ny * spread1), (x0 - nx * spread0, y0 - ny * spread0)]
    return (f'<defs><linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}"><stop offset="0" stop-color="{colour}" stop-opacity="{n(opacity)}"/>'
            f'<stop offset="0.55" stop-color="{colour}" stop-opacity="{n(opacity * 0.34)}"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient>'
            f'<filter id="{uid}f" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="{n(soften)}"/></filter></defs>'
            f'<polygon points="{pts(poly)}" fill="url(#{uid})" filter="url(#{uid}f)"/>')


# ------------------------------------------------------------------------------------------------------------------ ground for plan views
def terrain_card(name, w_units, h_units, radius=8.0, seed=1, kind="night", features=("scrub", "wadis"), veil=0.0, soft=2.4, px=4, road=None, village=None, fields=None, dim=1.0, flatten=0.0):
    """An aerial view of the country (figs/terrain.py) cut to a card of w_units by h_units with rounded corners, written to renders/<name>.png if it is not there (the same picture for
    the same seed); lay it as a sprite {"name": name, "at": [centre], "width": w_units}. Its corners are transparent, so that it sits in a card made with scene.card."""
    import os
    from PIL import Image, ImageDraw
    from figs import terrain
    path = os.path.join(terrain.RENDERS, name + ".png")
    if not os.path.exists(path):
        os.makedirs(terrain.RENDERS, exist_ok=True)
        w, h = round(w_units * px), round(h_units * px)
        img = terrain.build(w, h, seed, kind, tuple(features), road, village, fields, False, veil, soft).convert("RGBA")
        if dim != 1.0 or flatten:                                    # darker, and the picture pulled towards its own mean (a quieter ground under a diagram)
            import numpy as np
            arr = np.asarray(img).astype(np.float32)
            rgb = arr[..., :3]
            mean = rgb.reshape(-1, 3).mean(axis=0)
            rgb = (mean + (rgb - mean) * (1.0 - flatten)) * dim
            arr[..., :3] = rgb
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
        big = Image.new("L", (w * 2, h * 2), 0)
        ImageDraw.Draw(big).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], radius=radius * px * 2, fill=255)
        img.putalpha(big.resize((w, h), Image.LANCZOS))
        img.save(path, optimize=False, compress_level=3)
    return path
