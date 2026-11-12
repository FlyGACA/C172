"""The pieces of the illustrated weather figures, as SVG markup: skies, a landscape of the Arabian Peninsula (far mountains, hills, plain, date palms, acacias,
flat-roofed houses), ribbon arrows, rain, lightning, the sun, glass blocks and a few other things. A figure module joins them with the cloud sprites
(figs/clouds.py) in the "layers" of a blank re-skin (reskin.py): the sky first, the clouds in the middle, the land and the callouts at the front.

Plain Python (no Blender, no Pillow). Every gradient and filter takes an id made from the figure's `uid`, so that two pieces of one drawing never share one."""
import math
import random


def n(v):
    """A number for an SVG attribute, short."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pts(points):
    return " ".join(f"{n(x)},{n(y)}" for x, y in points)


# ------------------------------------------------------------------------------------------------------------------ colours
SKY = [(0.0, "#3A74C0"), (0.42, "#73A6DE"), (0.80, "#CFE3F6"), (1.0, "#FCF3DA")]            # a clear day: deep blue overhead, a pale warm horizon
SKY_PALE = [(0.0, "#7EAAD9"), (0.55, "#B7D2EE"), (1.0, "#EEF4FB")]                          # the book's own sky, quieter (small scenes)
STORM = [(0.0, "#566B8C"), (0.5, "#8795AD"), (1.0, "#C5CCD6")]
DUSK = [(0.0, "#44588F"), (0.5, "#9A8FB8"), (0.85, "#F1B58C"), (1.0, "#F9D9A2")]
NIGHT = [(0.0, "#16213F"), (0.6, "#2E4272"), (1.0, "#5A6F9E")]
SAND = {"far": ("#97A6C4", "#C9D2E4"), "hills": ("#CDB085", "#E3CFA4"), "plain": ("#E7D5AA", "#D3BA88"), "scrub": ("#7F8F55", "#5F7345"), "rock": ("#A88B68", "#7E6549")}


def gradient(uid, stops, x1=0, y1=0, x2=0, y2=1, units=None):
    extra = f' gradientUnits="{units}"' if units else ""
    body = "".join(f'<stop offset="{n(o)}" stop-color="{c}"' + (f' stop-opacity="{n(a)}"' if a is not None else "") + "/>" for o, c, a in [(s[0], s[1], s[2] if len(s) > 2 else None) for s in stops])
    return f'<linearGradient id="{uid}" x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}"{extra}>{body}</linearGradient>'


def sky(uid, x, y, w, h, stops=SKY):
    """A sky: a vertical gradient over the rectangle."""
    return f'<defs>{gradient(uid, stops)}</defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid})"/>'


def glow(uid, cx, cy, r, colour="#FFF4D2", opacity=0.9):
    """A soft round glow (the sun's halo, a lamp)."""
    return (f'<defs><radialGradient id="{uid}"><stop offset="0" stop-color="{colour}" stop-opacity="{n(opacity)}"/><stop offset="0.35" stop-color="{colour}" stop-opacity="{n(opacity * 0.45)}"/>'
            f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/></radialGradient></defs><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{uid})"/>')


def sun(uid, cx, cy, r, colour="#FFF1C4", halo=4.5):
    return glow(uid + "h", cx, cy, r * halo, "#FFF1C4", 0.85) + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{colour}"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 0.78)}" fill="#FFFAE6" opacity="0.9"/>'


# ------------------------------------------------------------------------------------------------------------------ land
def ridge(seed, x0, x1, y, amp, step=4.0, peaks=0.0):
    """The line of a hill or a mountain range from x0 to x1 about y (up is smaller y), as points; `peaks` (0 to 1) sharpens it into mountains."""
    rnd = random.Random(seed)
    waves = [(rnd.uniform(0.012, 0.022), rnd.uniform(0, 6.28), 0.55), (rnd.uniform(0.03, 0.05), rnd.uniform(0, 6.28), 0.28), (rnd.uniform(0.07, 0.11), rnd.uniform(0, 6.28), 0.12)]
    out, x = [], x0
    while x <= x1 + 0.01:
        v = sum(a * math.sin(f * (x - x0) + p) for f, p, a in waves)
        v = (1 - peaks) * v + peaks * (1 - 2 * abs(math.sin(0.5 * sum(a * math.sin(f * (x - x0) + p) for f, p, a in waves[:2]) * 3.0)))
        out.append((x, y - amp * (0.5 + 0.5 * v)))
        x += step
    return out


def land_layer(uid, points, y_bottom, colours, opacity=1.0, rim=True, haze=0.0, haze_colour="#E4EEF8"):
    """A band of land under a ridge line, shaded from the crest down, with a light line along the crest."""
    top = min(y for _, y in points)
    path = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points) + f" L {n(points[-1][0])},{n(y_bottom)} L {n(points[0][0])},{n(y_bottom)} Z"
    out = [f'<defs>{gradient(uid, [(0, colours[0]), (1, colours[1])])}</defs><path d="{path}" fill="url(#{uid})" opacity="{n(opacity)}"/>']
    if rim:
        out.append(f'<path d="M {" L ".join(f"{n(x)},{n(y)}" for x, y in points)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.30" stroke-width="0.8"/>')
    if haze:
        out.append(f'<defs>{gradient(uid + "z", [(0, haze_colour, haze), (1, haze_colour, 0)])}</defs><path d="{path}" fill="url(#{uid}z)"/>')
    return "".join(out)


def scrub(seed, x0, x1, y0, y1, count, colour=SAND["scrub"], scale=1.0):
    """Low bushes in loose clumps over a stretch of ground (small darker blobs with a light top; smaller and paler towards the horizon)."""
    rnd = random.Random(seed)
    out, placed = [], 0
    while placed < count:
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        for _ in range(rnd.randint(2, 5)):
            x, y = cx + rnd.uniform(-9, 9), cy + rnd.uniform(-2.5, 2.5)
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                continue
            k = scale * (0.55 + 0.9 * (y - y0) / max(1.0, y1 - y0)) * rnd.uniform(0.7, 1.25)
            out.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(3.4 * k)}" ry="{n(1.6 * k)}" fill="{colour[1]}" opacity="0.8"/><ellipse cx="{n(x - 0.4 * k)}" cy="{n(y - 0.55 * k)}" rx="{n(2.5 * k)}" ry="{n(1.0 * k)}" fill="{colour[0]}" opacity="0.9"/>')
            placed += 1
    return "".join(out)


def palm(x, y, h=26.0, lean=0.12, seed=1):
    """A date palm standing on (x, y): a slim curved trunk and a crown of drooping fronds."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, y - h
    trunk = (f'<path d="M {n(x - 0.9)},{n(y)} Q {n(x + lean * h * 0.2)},{n(y - h * 0.55)} {n(tx - 0.55)},{n(ty)} L {n(tx + 0.55)},{n(ty)} Q {n(x + lean * h * 0.2 + 1.6)},{n(y - h * 0.55)} {n(x + 0.9)},{n(y)} Z" fill="#7A5C3C"/>')
    rings = "".join(f'<line x1="{n(x + lean * h * (j / 9) ** 1.6 - 0.9)}" y1="{n(y - h * j / 9)}" x2="{n(x + lean * h * (j / 9) ** 1.6 + 1.0)}" y2="{n(y - h * j / 9 - 0.4)}" stroke="#5E452B" stroke-width="0.35" opacity="0.6"/>' for j in range(1, 9))
    fronds = []
    for i in range(9):
        a = math.radians(-165 + i * 20.5 + rnd.uniform(-5, 5))
        length = h * rnd.uniform(0.40, 0.52)
        ex, ey = tx + length * math.cos(a), ty + length * math.sin(a) * 0.55 + length * 0.30
        cx, cy = tx + length * 0.55 * math.cos(a), ty + length * 0.55 * math.sin(a) * 0.9 - length * 0.18
        tone = "#4F8038" if i % 2 else "#5E9443"
        fronds.append(f'<path d="M {n(tx)},{n(ty)} Q {n(cx)},{n(cy - 1.5)} {n(ex)},{n(ey)} Q {n(cx)},{n(cy + 1.8)} {n(tx)},{n(ty + 0.5)} Z" fill="{tone}"/>')
    shadow = f'<ellipse cx="{n(x + 3)}" cy="{n(y + 0.6)}" rx="{n(h * 0.28)}" ry="{n(h * 0.05)}" fill="#6B573A" opacity="0.28"/>'
    return shadow + trunk + rings + "".join(fronds) + f'<circle cx="{n(tx)}" cy="{n(ty + 0.4)}" r="1.1" fill="#6A4F31"/>'


def acacia(x, y, h=14.0, seed=1):
    """A flat-topped acacia: a thin trunk and a wide umbrella of leaves."""
    rnd = random.Random(seed)
    w = h * rnd.uniform(0.9, 1.15)
    return (f'<ellipse cx="{n(x + 1.5)}" cy="{n(y + 0.5)}" rx="{n(w * 0.45)}" ry="{n(h * 0.06)}" fill="#6B573A" opacity="0.28"/>'
            f'<path d="M {n(x - 0.7)},{n(y)} Q {n(x - 0.3)},{n(y - h * 0.5)} {n(x - 1.8)},{n(y - h * 0.72)} L {n(x + 1.8)},{n(y - h * 0.72)} Q {n(x + 0.5)},{n(y - h * 0.5)} {n(x + 0.7)},{n(y)} Z" fill="#6E5539"/>'
            f'<ellipse cx="{n(x)}" cy="{n(y - h * 0.8)}" rx="{n(w * 0.52)}" ry="{n(h * 0.2)}" fill="#5F7F3B"/><ellipse cx="{n(x - w * 0.08)}" cy="{n(y - h * 0.88)}" rx="{n(w * 0.4)}" ry="{n(h * 0.13)}" fill="#7C9C4D"/>')


def house(x, y, w=18.0, h=10.0, seed=1):
    """A flat-roofed house of the plain (sand-coloured walls, a lit side and a shaded side, a door, a parapet) standing on (x, y)."""
    rnd = random.Random(seed)
    d = w * 0.28
    body = (f'<path d="M {n(x)},{n(y)} L {n(x)},{n(y - h)} L {n(x + w)},{n(y - h)} L {n(x + w)},{n(y)} Z" fill="#EEDFBC"/>'
            f'<path d="M {n(x + w)},{n(y)} L {n(x + w)},{n(y - h)} L {n(x + w + d)},{n(y - h - d * 0.35)} L {n(x + w + d)},{n(y - d * 0.35)} Z" fill="#CDB98F"/>'
            f'<path d="M {n(x)},{n(y - h)} L {n(x + d)},{n(y - h - d * 0.35)} L {n(x + w + d)},{n(y - h - d * 0.35)} L {n(x + w)},{n(y - h)} Z" fill="#F7EBCF"/>')
    door = f'<rect x="{n(x + w * 0.42)}" y="{n(y - h * 0.55)}" width="{n(w * 0.16)}" height="{n(h * 0.55)}" fill="#7A5B3A"/>'
    windows = "".join(f'<rect x="{n(x + w * fx)}" y="{n(y - h * 0.72)}" width="{n(w * 0.1)}" height="{n(h * 0.24)}" fill="#6D86A6"/>' for fx in (0.14, 0.76))
    return (f'<ellipse cx="{n(x + w * 0.65)}" cy="{n(y + 0.8)}" rx="{n(w * 0.7)}" ry="{n(h * 0.12)}" fill="#6B573A" opacity="0.25"/>' + body + door + windows)


def dune(uid, x0, x1, y, amp, seed, colours=("#F1E1B8", "#D7BC8A"), crest="#FFF6DA"):
    """A sand dune ridge: the sunlit slope on one side, the shaded slope on the other, a bright crest line."""
    pts_ = ridge(seed, x0, x1, y, amp, step=3.0)
    path = "M " + " L ".join(f"{n(x)},{n(yy)}" for x, yy in pts_) + f" L {n(x1)},{n(y + amp * 4)} L {n(x0)},{n(y + amp * 4)} Z"
    return (f'<defs>{gradient(uid, [(0, colours[0]), (0.5, colours[0]), (1, colours[1])], 0, 0, 1, 0)}</defs><path d="{path}" fill="url(#{uid})"/>'
            f'<path d="M {" L ".join(f"{n(x)},{n(yy)}" for x, yy in pts_)}" fill="none" stroke="{crest}" stroke-opacity="0.55" stroke-width="0.9"/>')


def landscape(uid, x0, x1, horizon, bottom, seed=3, mountains=26.0, hills=11.0, palms=(), acacias=(), houses=(), haze=0.0, grain=True):
    """A stretch of country from the horizon down to `bottom`: blue far mountains, ochre hills, dunes and a plain with bushes, and whatever stands on it
    (`palms`, `acacias`, `houses`: lists of (x, y, size)). Drawn back to front, as one string."""
    h = bottom - horizon
    far = ridge(seed, x0, x1, horizon + 2, mountains, peaks=0.6)
    far2 = ridge(seed + 7, x0, x1, horizon + 3, mountains * 0.6, peaks=0.35)
    mid = ridge(seed + 11, x0, x1, horizon + h * 0.10, hills)
    near = ridge(seed + 23, x0, x1, horizon + h * 0.30, 3.0)
    out = [land_layer(uid + "f", far, bottom, ("#7F8DB0", "#B3BFD6"), rim=True, haze=0.38),
           land_layer(uid + "g", far2, bottom, ("#97A3C0", "#C4CCDD"), rim=True, haze=0.25),
           land_layer(uid + "m", mid, bottom, ("#C9A874", "#E4CF9F"), rim=True, haze=0.10),
           dune(uid + "d1", x0, x1, horizon + h * 0.20, hills * 0.55, seed + 31),
           land_layer(uid + "p", near, bottom, ("#ECDCB2", "#D5BB88"), rim=False, haze=haze)]
    out.append(scrub(seed + 5, x0, x1, horizon + h * 0.34, bottom - 2, int((x1 - x0) / 9), scale=1.1))
    if grain:
        gid = uid + "n"
        out.append(f'<defs><filter id="{gid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed}"/>'
                   f'<feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.34  0 0 0 0 0.2  0 0 0 0.55 -0.12"/></filter></defs>'
                   f'<rect x="{n(x0)}" y="{n(horizon + h * 0.3)}" width="{n(x1 - x0)}" height="{n(h * 0.7)}" filter="url(#{gid})" opacity="0.5"/>')
    for (x, y, s_) in houses:
        out.append(house(x, y, 18.0 * s_, 10.0 * s_, seed + int(x)))
    for (x, y, s_) in acacias:
        out.append(acacia(x, y, 14.0 * s_, seed + int(x)))
    for (x, y, s_) in palms:
        out.append(palm(x, y, 26.0 * s_, 0.10, seed + int(x)))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ arrows
def catmull(points, per=10):
    """A smooth curve through the points (Catmull-Rom), as many points."""
    p = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(p) - 2):
        for k in range(per):
            t = k / per
            a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
            out.append(tuple(0.5 * ((2 * b[j]) + (-a[j] + c[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t * t + (-a[j] + 3 * b[j] - 3 * c[j] + d[j]) * t ** 3) for j in (0, 1)))
    out.append(points[-1])
    return out


def ribbon(uid, points, width=7.0, c1="#E8782E", c2="#F6B36B", opacity=0.93, head=2.1, tail=0.5, shadow=True, per=10):
    """A wide arrow that follows a smooth curve through `points`: narrow at the tail, full width along the body, a head at the tip; shaded along its length, lit
    along one edge, with a soft shadow."""
    curve = catmull(points, per)
    dist = [0.0]
    for a, b in zip(curve, curve[1:]):
        dist.append(dist[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = dist[-1]
    head_len = min(total * 0.4, width * 2.6)
    body_end = total - head_len
    left, right = [], []
    for i, (x, y) in enumerate(curve):
        j0, j1 = max(0, i - 1), min(len(curve) - 1, i + 1)
        tx, ty = curve[j1][0] - curve[j0][0], curve[j1][1] - curve[j0][1]
        norm = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / norm, tx / norm
        s = dist[i]
        if s > body_end:
            break
        grow = tail + (1 - tail) * min(1.0, s / max(1.0, total * 0.35))
        half = width * 0.5 * grow
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    x, y = curve[len(left) - 1]
    tx, ty = curve[-1][0] - x, curve[-1][1] - y
    norm = math.hypot(tx, ty) or 1.0
    ux, uy = tx / norm, ty / norm
    nx, ny = -uy, ux
    wing = width * 0.5 * head
    tip = curve[-1]
    outline = left + [(x + nx * wing, y + ny * wing), tip, (x - nx * wing, y - ny * wing)] + right[::-1]
    x0, y0 = curve[0]
    gid, fid = uid + "g", uid + "s"
    out = [f'<defs>{gradient(gid, [(0, c1, 0.55), (0.55, c1), (1, c2)], x0, y0, tip[0], tip[1], "userSpaceOnUse")}']
    if shadow:
        out.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0.8" dy="2.2" stdDeviation="1.5" flood-color="#10233F" flood-opacity="0.35"/></filter>')
    out.append("</defs>")
    out.append(f'<polygon points="{pts(outline)}" fill="url(#{gid})" opacity="{n(opacity)}"' + (f' filter="url(#{fid})"' if shadow else "") + ' stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.7" stroke-linejoin="round"/>')
    hi = [(a[0] * 0.5 + c[0] * 0.5 + (a[0] - c[0]) * 0.0, a[1] * 0.5 + c[1] * 0.5) for a, c in zip(left, curve)]
    out.append(f'<polyline points="{pts(hi[2:])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.38" stroke-width="{n(width * 0.16)}" stroke-linecap="round"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ weather
def rain(uid, x0, x1, y0, y1, slant=-5.0, count=36, seed=1, colour="#3A63B4", veil=0.16, bottom=0.55):
    """A curtain of rain between x0 and x1 from y0 down to y1: a soft veil and thin slanting streaks of different lengths and strengths."""
    rnd = random.Random(seed)
    h = y1 - y0
    out = [f'<defs>{gradient(uid, [(0, colour, 0.0), (0.25, colour, veil), (1, colour, veil * bottom)])}</defs>'
           f'<polygon points="{pts([(x0, y0), (x1, y0), (x1 + slant, y1), (x0 + slant, y1)])}" fill="url(#{uid})"/>']
    for _ in range(count):
        x = rnd.uniform(x0, x1)
        a = y0 + rnd.uniform(0.0, 0.3) * h
        b = y1 - rnd.uniform(0.0, 0.18) * h
        sl = slant * (b - y0) / h
        out.append(f'<line x1="{n(x + slant * (a - y0) / h)}" y1="{n(a)}" x2="{n(x + sl)}" y2="{n(b)}" stroke="{colour}" stroke-width="{n(rnd.uniform(0.5, 1.1))}" stroke-opacity="{n(rnd.uniform(0.28, 0.6))}" stroke-linecap="round"/>')
    return "".join(out)


def lightning(uid, x, y0, y1, seed=1, colour="#FFF2A8", forks=2):
    """A bolt from (x, y0) down to y1, forked, with a glow."""
    rnd = random.Random(seed)

    def bolt(xa, ya, yb, wobble, depth=0):
        points, steps = [(xa, ya)], max(4, int((yb - ya) / 5))
        for i in range(1, steps + 1):
            points.append((points[-1][0] + rnd.uniform(-wobble, wobble), ya + (yb - ya) * i / steps))
        return points
    main = bolt(x, y0, y1, 4.5)
    paths = [(main, 1.0)]
    for _ in range(forks):
        k = rnd.randint(1, len(main) - 3)
        px, py = main[k]
        paths.append((bolt(px, py, py + rnd.uniform(14, 26), 3.5)[:5], 0.6))
    fid = uid + "b"
    out = [f'<defs><filter id="{fid}" x="-100%" y="-30%" width="300%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>']
    for p, w in paths:
        d = "M " + " L ".join(f"{n(a)},{n(b)}" for a, b in p)
        out.append(f'<path d="{d}" fill="none" stroke="#FFC93D" stroke-width="{n(5 * w)}" stroke-opacity="0.7" stroke-linejoin="round" filter="url(#{fid})"/>'
                   f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(1.7 * w)}" stroke-linejoin="round" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(0.7 * w)}" stroke-linejoin="round"/>')
    return "".join(out)


def altitude_line(x0, x1, y, colour="#F7FAFF", opacity=0.75, dash="5 4", width=1.2):
    return f'<line x1="{n(x0)}" y1="{n(y)}" x2="{n(x1)}" y2="{n(y)}" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-dasharray="{dash}"/>'


def callout(k, cx, cy, tx=None, ty=None, r=11.0):
    """A numbered callout (the book's: a dark disc with a white ring and the number), with a leader line to (tx, ty)."""
    line = f'<line x1="{n(tx)}" y1="{n(ty)}" x2="{n(cx)}" y2="{n(cy)}" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.85" stroke-linecap="round"/><line x1="{n(tx)}" y1="{n(ty)}" x2="{n(cx)}" y2="{n(cy)}" stroke="#263244" stroke-width="1.1" stroke-linecap="round"/><circle cx="{n(tx)}" cy="{n(ty)}" r="1.8" fill="#263244" stroke="#FFFFFF" stroke-width="0.9"/>' if tx is not None else ""
    return (line + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#1f2937" stroke="#ffffff" stroke-width="1.5"/>'
            f'<text x="{n(cx)}" y="{n(cy + r * 0.42)}" font-family="sans-serif" font-size="{n(r * 1.18)}" font-weight="bold" fill="#ffffff" text-anchor="middle">{k}</text>')


# ------------------------------------------------------------------------------------------------------------------ blocks
def face(points, fill, opacity=1.0, stroke="#FFFFFF", stroke_opacity=0.7, width=0.9):
    return f'<polygon points="{pts(points)}" fill="{fill}" opacity="{n(opacity)}" stroke="{stroke}" stroke-opacity="{n(stroke_opacity)}" stroke-width="{n(width)}" stroke-linejoin="round"/>'


def clip(uid, points):
    return f'<clipPath id="{uid}"><polygon points="{pts(points)}"/></clipPath>'


def air(uid, points, c1, c2, opacity=0.6):
    """A region of air (a polygon of the cross-section), shaded from c1 above to c2 below."""
    return f'<defs>{gradient(uid, [(0, c1), (1, c2)])}</defs><polygon points="{pts(points)}" fill="url(#{uid})" opacity="{n(opacity)}"/>'


def front_symbols(kind, p0, p1, size=7.0, spacing=19.0, motion=1.0):
    """The line of a front on a map and the marks along it that point the way it moves: blue triangles (cold), red half-circles (warm), the two alternating on
    the same side, in purple (occluded). `kind` is "cold", "warm" or "occluded"; the marks stand on the side of the line the front moves towards (motion +1: to the right)."""
    colours = {"cold": "#2358C4", "warm": "#D32F2F", "occluded": "#7B3FA8"}
    c = colours[kind]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = (uy, -ux) if uy * 1.0 >= 0 else (-uy, ux)
    if nx * motion < 0:
        nx, ny = -nx, -ny
    out = [f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>']
    count = max(1, int(length // spacing))
    for i in range(count):
        t = (i + 0.5) * length / count
        bx, by = p0[0] + ux * t, p0[1] + uy * t
        shape = kind if kind != "occluded" else ("cold" if i % 2 == 0 else "warm")
        sc = colours[shape]
        if shape == "cold":
            a = (bx - ux * size * 0.7, by - uy * size * 0.7)
            b = (bx + ux * size * 0.7, by + uy * size * 0.7)
            tip = (bx + nx * size * 1.05, by + ny * size * 1.05)
            out.append(f'<polygon points="{pts([a, b, tip])}" fill="{sc}"/>')
        else:
            r = size * 0.62
            a = (bx - ux * r, by - uy * r)
            b = (bx + ux * r, by + uy * r)
            out.append(f'<path d="M {n(a[0])},{n(a[1])} A {n(r)},{n(r)} 0 0 {1 if nx > 0 else 0} {n(b[0])},{n(b[1])} Z" fill="{sc}"/>')
    return "".join(out)


def fog(uid, x0, x1, y_bottom, height, seed=1, opacity=0.95, colour="#FFFFFF", wisp=0.9, middle=False, side_fade=0.0, foot=1.0):
    """A bank of fog lying on the ground: dense and white at the bottom, thinning upwards into wisps (noise cut out of a gradient, then softened);
    with `middle` it is thickest in the middle of the stretch and thin towards its ends (fog in a hollow); `side_fade` (0 to 0.5, the fraction of the width) lets it thin out
    towards both ends, `foot` (0 to 1) is how dense its lowest edge is (below 1 the bank melts into the ground instead of ending in a line)."""
    fid = uid + "f"
    shape = (f'<radialGradient id="{uid}" cx="0.5" cy="1" r="0.62" fx="0.5" fy="1" gradientTransform="translate(0 0.0) scale(1 1)"><stop offset="0" stop-color="{colour}" stop-opacity="{n(opacity)}"/>'
             f'<stop offset="0.55" stop-color="{colour}" stop-opacity="{n(opacity * 0.7)}"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></radialGradient>') if middle else \
            gradient(uid, [(0, colour, 0.0), (0.35, colour, opacity * 0.55), (0.85, colour, opacity), (1, colour, opacity * foot)])
    box = f'x="{n(x0)}" y="{n(y_bottom - height)}" width="{n(x1 - x0)}" height="{n(height)}"'
    masks, outer_open, outer_close, rect_mask = "", "", "", ""
    if side_fade:
        mid = uid + "m"
        masks += (f'<linearGradient id="{mid}g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset="{n(side_fade)}" stop-color="#fff"/><stop offset="{n(1 - side_fade)}" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
                  f'<mask id="{mid}" maskUnits="userSpaceOnUse" {box}><rect {box} fill="url(#{mid}g)"/></mask>')
        outer_open, outer_close = f'<g mask="url(#{mid})">', "</g>"
    if foot < 1.0 and middle:
        bid = uid + "b"
        level = int(round(255 * foot))
        masks += (f'<linearGradient id="{bid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="0.7" stop-color="#fff"/><stop offset="1" stop-color="rgb({level},{level},{level})"/></linearGradient>'
                  f'<mask id="{bid}" maskUnits="userSpaceOnUse" {box}><rect {box} fill="url(#{bid}g)"/></mask>')
        rect_mask = f' mask="url(#{bid})"'
    return (f'<defs>{shape}{masks}'
            f'<filter id="{fid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.016 0.055" numOctaves="4" seed="{seed}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  {n(3.2 * wisp)} 0 0 0 {n(-0.78 * wisp)}" result="a"/>'
            f'<feComposite in="SourceGraphic" in2="a" operator="in" result="c"/><feGaussianBlur in="c" stdDeviation="1.4"/></filter></defs>'
            f'{outer_open}<rect {box} fill="url(#{uid})" filter="url(#{fid})"{rect_mask}/>{outer_close}')


def valley(uid, x0, x1, top, bottom, seed=1, depth=22.0, sides=44.0, colours=(("#7F8DB0", "#B3BFD6"), ("#C9A874", "#E4CF9F"), ("#ECDCB2", "#D5BB88"))):
    """Hills round a hollow: far blue hills, nearer ochre hills and a plain in the hollow, which is `depth` lower than the hill tops; as one string.
    The tops of the hills are at `top`, the foot of the picture is `bottom`."""
    rnd = random.Random(seed)

    def line(base, amp, sd, bowl):
        out, x = [], x0
        waves = [(rnd.uniform(0.02, 0.04), rnd.uniform(0, 6.28), 0.6), (rnd.uniform(0.06, 0.1), rnd.uniform(0, 6.28), 0.4)]
        while x <= x1 + 0.01:
            u = (x - (x0 + x1) / 2) / ((x1 - x0) / 2)                                    # -1 to 1 across
            v = sum(a * math.sin(f * (x - x0) + p) for f, p, a in waves)
            out.append((x, base + bowl * (1 - u * u) ** 1.2 + amp * v))
            x += 3.0
        return out
    far = line(top + 8, 4.0, 0, depth * 0.55)
    mid = line(top + 12, 3.0, 0, depth * 0.85)
    near = line(top + 20, 1.6, 0, depth * 1.05)
    return "".join([land_layer(uid + "f", far, bottom, colours[0], rim=True, haze=0.35), land_layer(uid + "m", mid, bottom, colours[1], rim=True, haze=0.10),
                    land_layer(uid + "p", near, bottom, colours[2], rim=False)])


def card(uid, x, y, w, h, sky_stops, body, radius=9.0):
    """A picture in a card: a rounded frame with a soft shadow and a white edge, the sky and the body (markup) clipped to it."""
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + sky(uid + "k", x, y, w, h, sky_stops) + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def sea(uid, x0, x1, y0, y1, seed=1, light="#6FB3DE", dark="#2C6FAE", sparkle=True):
    """The sea from y0 (the horizon) down to y1: deeper blue near the horizon (a flat sea is darker far away), lighter near, small white crests and the glitter of the sun."""
    rnd = random.Random(seed)
    out = [f'<defs>{gradient(uid, [(0, dark), (1, light)])}</defs><rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="url(#{uid})"/>']
    for _ in range(int((x1 - x0) * (y1 - y0) / 260)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0 + 2, y1)
        k = 0.5 + 1.2 * (y - y0) / max(1.0, y1 - y0)
        out.append(f'<path d="M {n(x - 3 * k)},{n(y)} q {n(1.5 * k)},{n(-1.2 * k)} {n(3 * k)},0 q {n(1.5 * k)},{n(1.2 * k)} {n(3 * k)},0" fill="none" stroke="#FFFFFF" stroke-width="0.6" stroke-opacity="{n(rnd.uniform(0.25, 0.6))}"/>')
    out.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y0)}" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="0.8"/>')
    return "".join(out)


def dhow(x, y, s=1.0):
    """A small dhow (the old sailing boat of the Gulf) on the water, seen from the side."""
    hull = f'<path d="M {n(x - 9 * s)},{n(y - 3 * s)} L {n(x + 11 * s)},{n(y - 5.5 * s)} L {n(x + 8 * s)},{n(y)} L {n(x - 6 * s)},{n(y)} Z" fill="#7A4B2A"/><path d="M {n(x - 6 * s)},{n(y)} L {n(x + 8 * s)},{n(y)}" stroke="#3E2713" stroke-width="0.8"/>'
    sail = f'<path d="M {n(x)},{n(y - 4 * s)} L {n(x - 0.5 * s)},{n(y - 17 * s)} L {n(x + 9 * s)},{n(y - 6 * s)} Z" fill="#FFFFFF" opacity="0.95"/><line x1="{n(x)}" y1="{n(y - 4 * s)}" x2="{n(x - 0.5 * s)}" y2="{n(y - 17.5 * s)}" stroke="#5B4430" stroke-width="0.8"/>'
    refl = f'<ellipse cx="{n(x + s)}" cy="{n(y + 1.4 * s)}" rx="{n(10 * s)}" ry="{n(1.2 * s)}" fill="#FFFFFF" opacity="0.28"/>'
    return refl + hull + sail


def slope_valley(uid, x0, x1, top, bottom, left=0.30, right=0.70, colours=(("#C7B79E", "#9A8566"), ("#D8CAB2", "#A99677")), far=None, fog_level=None, fog_seed=6, seed=3, night=False):
    """Two mountain sides round a V-shaped valley (the figure's 14-3 profile): a ridge each side coming down to the valley floor, lit on the left, shaded on the right, with rock
    strata, scree and a few bushes on them. `far` (a pair of colours) puts a range of hazy hills at the far end of the valley, between the sides; `fog_level` (a y) lays a lake of
    fog in the valley up to that height, behind the near ground, so that the ground cuts its lower edge and the slopes its sides."""
    rnd = random.Random(seed)
    w = x1 - x0
    lp = [(x0, top + 14), (x0 + w * 0.10, top + 4), (x0 + w * left, bottom - 30), (x0 + w * 0.5 - 12, bottom - 14), (x0 + w * 0.5 + 12, bottom - 14), (x0 + w * right, bottom - 30), (x0 + w * 0.9, top + 4), (x1, top + 14)]
    poly_ = lp + [(x1, bottom), (x0, bottom)]
    out = []
    if far:
        fr = ridge(seed + 3, x0 + w * 0.10, x1 - w * 0.10, top + 66, 62, step=3.0, peaks=0.7)
        fr2 = ridge(seed + 8, x0 + w * 0.10, x1 - w * 0.10, top + 92, 40, step=3.0, peaks=0.45)
        out.append(land_layer(uid + "r", fr, bottom, far, rim=not night, haze=0.12 if not night else 0.0))
        out.append(land_layer(uid + "q", fr2, bottom, (far[0] if night else "#B9AF9E", far[1] if night else "#D6C9AC"), rim=not night, haze=0.10 if not night else 0.0))
    if fog_level is not None:
        out.append(fog(uid + "g", x0, x1, bottom + 4, fog_level, seed=fog_seed, opacity=1.0, wisp=0.36, middle=False))
    cid = uid + "c"
    out.append(f'<defs>{gradient(uid, [(0, colours[0][0]), (1, colours[0][1])])}{gradient(uid + "s", [(0, "#000000", 0.0), (1, "#0B1F3F", 0.30)], 0, 0, 1, 0)}'
               f'<clipPath id="{cid}"><polygon points="{pts(poly_)}"/></clipPath>'
               f'<filter id="{uid}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="{seed}"/>'
               f'<feColorMatrix type="matrix" values="0 0 0 0 0.30  0 0 0 0 0.22  0 0 0 0 0.14  0 0 0 0.9 -0.28"/></filter></defs>'
               f'<polygon points="{pts(poly_)}" fill="url(#{uid})"/><polygon points="{pts(poly_)}" fill="url(#{uid}s)"/>')
    strata = []
    for k in range(1, 7):
        off = k * 11.0
        line = [(a, b + off + 2.2 * math.sin(a * 0.13 + k)) for a, b in lp]
        strata.append(f'<path d="M {" L ".join(f"{n(a)},{n(b)}" for a, b in line)}" fill="none" stroke="#3B2C1B" stroke-opacity="{n(0.10 + 0.012 * k)}" stroke-width="{n(0.7 + 0.18 * k)}"/>')
        strata.append(f'<path d="M {" L ".join(f"{n(a)},{n(b - 1.4)}" for a, b in line)}" fill="none" stroke="#FFF6E0" stroke-opacity="0.12" stroke-width="0.6"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(strata) + f'<rect x="{n(x0)}" y="{n(top)}" width="{n(w)}" height="{n(bottom - top)}" filter="url(#{uid}n)" opacity="0.55"/></g>')
    bushes = []
    for _ in range(10):
        side = rnd.choice((0, 1))
        t = rnd.uniform(0.10, 0.85)
        a_, b_ = (lp[1], lp[2]) if side == 0 else (lp[5], lp[6])
        bx = a_[0] + (b_[0] - a_[0]) * t
        by = a_[1] + (b_[1] - a_[1]) * t + rnd.uniform(3, 15)
        k = 0.7 + 0.7 * t
        bushes.append(f'<ellipse cx="{n(bx)}" cy="{n(by)}" rx="{n(2.1 * k)}" ry="{n(1.0 * k)}" fill="{"#5A5B3C" if not night else "#2A3338"}" opacity="0.85"/>')
    out.append("".join(bushes))
    out.append(f'<path d="M {" L ".join(f"{n(a)},{n(b)}" for a, b in lp)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1"/>')
    return "".join(out)


def card_front(uid, x, y, w, h, body, radius=9.0):
    """The front of a card whose back is `card()`: pieces that stand in front of the sprites laid on it (the land, the rain, the arrows), cut to the card's rounded edge,
    with the white edge drawn once more on top."""
    return (f'<defs><clipPath id="{uid}c2"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}c2)">{body}</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def plain(uid, x0, x1, horizon, bottom, seed=1, tone="day", houses=(), palms=(), acacias=(), hills=14.0):
    """A flat country of the Peninsula seen from afar: a low range of hills on the horizon, a sandy plain with scrub, and what stands on it (lists of (x, y, size)).
    `tone` is day, storm (darkened under a storm) or dusk."""
    sets = {"day": (("#7F8DB4", "#B6C2DA"), ("#E8D7AC", "#D2B988"), 0.0), "storm": (("#4D5C80", "#7C89A8"), ("#BBA97F", "#9C8A63"), 0.18), "dusk": (("#8794B4", "#C0C9DD"), ("#E4CFA2", "#C9AD7C"), 0.06)}
    far, ground_, shade = sets[tone]
    out = [land_layer(uid + "h", ridge(seed, x0, x1, horizon + 2, hills, peaks=0.5), horizon + 6, far, rim=tone != "storm", haze=0.2 if tone != "storm" else 0.0)]
    out.append(f'<defs>{gradient(uid + "g", [(0, ground_[0]), (1, ground_[1])])}</defs><rect x="{n(x0)}" y="{n(horizon)}" width="{n(x1 - x0)}" height="{n(bottom - horizon + 2)}" fill="url(#{uid}g)"/>')
    out.append(scrub(seed + 3, x0, x1, horizon + 4, bottom - 2, int((x1 - x0) / 11), scale=0.6))
    for (x, y, s_) in houses:
        out.append(house(x, y, 18.0 * s_, 10.0 * s_, seed + int(x)))
    for (x, y, s_) in acacias:
        out.append(acacia(x, y, 14.0 * s_, seed + int(x)))
    for (x, y, s_) in palms:
        out.append(palm(x, y, 26.0 * s_, 0.10, seed + int(x)))
    if shade:
        out.append(f'<defs>{gradient(uid + "s", [(0, "#14233F", 0.0), (0.3, "#14233F", shade * 0.8), (1, "#14233F", shade * 1.3)])}</defs>'
                   f'<rect x="{n(x0)}" y="{n(horizon - 34)}" width="{n(x1 - x0)}" height="{n(bottom - horizon + 36)}" fill="url(#{uid}s)"/>')
    return "".join(out)


def hailstones(points, r=3.9):
    """Hailstones: small white balls with a shaded side and a short streak above each."""
    out = []
    for x, y in points:
        out.append(f'<line x1="{n(x + 1.2)}" y1="{n(y - 9)}" x2="{n(x)}" y2="{n(y - r)}" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="1.1" stroke-linecap="round"/>'
                   f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#F4F8FF" stroke="#7C8DAA" stroke-width="0.8"/><circle cx="{n(x - r * 0.3)}" cy="{n(y - r * 0.3)}" r="{n(r * 0.4)}" fill="#FFFFFF"/>')
    return "".join(out)


def snowflake(cx, cy, r=5.0, colour="#FFFFFF", opacity=0.95):
    """A small snowflake (the freezing level): three crossing strokes with notched ends."""
    out = []
    for a in (0, 60, 120):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        out.append(f'<line x1="{n(cx - r * ca)}" y1="{n(cy - r * sa)}" x2="{n(cx + r * ca)}" y2="{n(cy + r * sa)}"/>')
        for sgn in (-1, 1):
            ex, ey = cx + sgn * r * ca, cy + sgn * r * sa
            for b in (35, -35):
                ba = math.radians(a + (180 if sgn < 0 else 0) + b)
                out.append(f'<line x1="{n(ex)}" y1="{n(ey)}" x2="{n(ex - r * 0.38 * math.cos(ba))}" y2="{n(ey - r * 0.38 * math.sin(ba))}"/>')
    return f'<g stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="1" stroke-linecap="round" fill="none">' + "".join(out) + "</g>"


def jag(points, amp, seed, parts=3):
    """A polyline with every segment cut into `parts` and the new points moved a little up or down (a rough edge of rock)."""
    rnd = random.Random(seed)
    out = [points[0]]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for k in range(1, parts):
            t = k / parts
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
        out.append((x1, y1))
    return out


def rock(uid, outline, bottom, x0, x1, seed, tones=("#D6C39C", "#A18A62"), spine=None):
    """A mass of rock under the outline (a polyline from left to right), lit from the left: a lit face and a shaded face (`spine`, a polyline from the summit to the foot, divides
    them), gullies running down from the crest, grain and a pale edge along the top."""
    rnd = random.Random(seed)
    poly_ = list(outline) + [(x1, bottom), (x0, bottom)]
    p = pts(poly_)
    out = [f'<defs>{gradient(uid, [(0, tones[0]), (1, tones[1])])}<clipPath id="{uid}c"><polygon points="{p}"/></clipPath>'
           f'<filter id="{uid}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="{seed}"/>'
           f'<feColorMatrix type="matrix" values="0 0 0 0 0.30  0 0 0 0 0.22  0 0 0 0 0.14  0 0 0 0.9 -0.28"/></filter></defs>'
           f'<polygon points="{p}" fill="url(#{uid})"/>']
    inner = []
    if spine:
        top = min(b for _, b in outline)
        right = [pt for pt in outline if pt[0] >= spine[0][0]]
        shade_poly = list(spine) + [(x1, bottom)] + [(x1, outline[-1][1])] + list(reversed(right[1:])) if False else None
        face = [spine[0]] + [pt for pt in outline if pt[0] > spine[0][0]] + [(x1, bottom), (spine[-1][0], bottom)] + list(reversed(spine[1:-1]))
        inner.append(f'<polygon points="{pts(face)}" fill="#14233F" opacity="0.30"/>')
        inner.append(f'<path d="M {" L ".join(f"{n(a)},{n(b)}" for a, b in spine)}" fill="none" stroke="#FFF3D8" stroke-opacity="0.45" stroke-width="1"/>')
    for _ in range(26):
        t = rnd.uniform(0.05, 0.95)
        k = min(len(outline) - 2, int(t * (len(outline) - 1)))
        (xa, ya), (xb, yb) = outline[k], outline[k + 1]
        gx, gy = xa + (xb - xa) * rnd.random(), ya + (yb - ya) * rnd.random()
        ln = rnd.uniform(14, 46)
        drift = rnd.uniform(-5, 5)
        inner.append(f'<path d="M {n(gx)},{n(gy + 1)} q {n(drift * 0.5)},{n(ln * 0.5)} {n(drift)},{n(ln)}" fill="none" stroke="#3B2C1B" stroke-opacity="{n(rnd.uniform(0.14, 0.32))}" stroke-width="{n(rnd.uniform(0.7, 1.5))}" stroke-linecap="round"/>')
    inner.append(f'<rect x="{n(x0)}" y="{n(min(b for _, b in outline))}" width="{n(x1 - x0)}" height="{n(bottom - min(b for _, b in outline))}" filter="url(#{uid}n)" opacity="0.5"/>')
    out.append(f'<g clip-path="url(#{uid}c)">{"".join(inner)}</g>')
    out.append(f'<path d="M {" L ".join(f"{n(a)},{n(b)}" for a, b in outline)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="1"/>')
    return "".join(out)
