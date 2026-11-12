"""Helpers of worker a1 for the profile figures (the aeroplane seen from the side, a path, a runway): a graded sky, hills on the horizon, a desert plain with scrub, a runway
seen almost edge-on (dark asphalt, white markings, edge lights), a windsock, a mast, a hangar, soft shadows, small cards for the speeds, casings under the paths.

Plain Python, no Blender and no Pillow. Everything that needs a gradient or a filter takes an id that starts with `a1`; a plate puts `defs()` first among its layers once."""
import math
import random

from figs import scene as S

n = S.n
pts = S.pts

LOOK = {"outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.9}, "shadow": {"dx": 1.2, "dy": 2.0, "blur": 1.5, "opacity": 0.26}}
LOOK_SOFT = {"outline": {"width": 0.45, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.0, "dy": 1.6, "blur": 1.3, "opacity": 0.2}}
SKY = [(0.0, "#4A84CB"), (0.45, "#86B4E6"), (0.86, "#D5E5F5"), (1.0, "#F7F0DA")]
SKY_HIGH = [(0.0, "#3F78C2"), (0.5, "#7DAEE3"), (0.9, "#D7E7F7"), (1.0, "#F4F1DF")]
INK = "#1F2937"
PAGE = "#EDF2F8"

# the main wheels of sprite-side, as fractions of the picture (cropped to the aeroplane): where they stand across and down
MAIN_X, MAIN_Y = 0.685, 0.997
ASPECT = 0.2922


def defs():
    return ('<defs>'
            '<radialGradient id="a1lg"><stop offset="0" stop-color="#FFF6D0" stop-opacity="0.95"/><stop offset="0.35" stop-color="#FFE9A6" stop-opacity="0.5"/><stop offset="1" stop-color="#FFE9A6" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="a1red"><stop offset="0" stop-color="#FF8A80" stop-opacity="0.95"/><stop offset="0.35" stop-color="#FF5A4E" stop-opacity="0.5"/><stop offset="1" stop-color="#FF5A4E" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="a1sh"><stop offset="0" stop-color="#1B2338" stop-opacity="0.55"/><stop offset="0.6" stop-color="#1B2338" stop-opacity="0.25"/><stop offset="1" stop-color="#1B2338" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="a1puff"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.9"/><stop offset="0.5" stop-color="#F6EFE0" stop-opacity="0.5"/><stop offset="1" stop-color="#EFE3C8" stop-opacity="0"/></radialGradient>'
            '<filter id="a1b1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.1"/></filter>'
            '<filter id="a1b2" x="-40%" y="-60%" width="180%" height="220%"><feGaussianBlur stdDeviation="2.2"/></filter>'
            '<filter id="a1ds" x="-20%" y="-20%" width="145%" height="160%"><feDropShadow dx="0.6" dy="1.6" stdDeviation="1.5" flood-color="#10233F" flood-opacity="0.3"/></filter>'
            '</defs>')


# ------------------------------------------------------------------------------------------------------------------ the aeroplane
def plane(x, y, angle=0.0, width=88.0, name="sprite-side", look=None, **extra):
    """sprite-side placed by the point where its main wheels touch (x, y), turned about that point by `angle` (degrees, clockwise: nose up is negative)."""
    h = width * ASPECT
    lx, ly = -(MAIN_X - 0.5) * width, -(MAIN_Y - 0.5) * h - h / 2 + h * 0.0     # the middle of the picture, from the wheels
    ly = -(MAIN_Y - 0.5) * h
    a = math.radians(angle)
    cx, cy = x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)
    o = {"name": name, "at": [round(cx, 1), round(cy, 1)], "width": width, **(look or LOOK), **extra}
    if angle:
        o["angle"] = angle
    return o


def drop_shadow(x, y, width=62.0, ry=2.6, opacity=0.4):
    """A soft shadow on the ground under an aeroplane: x the middle, y the ground."""
    return f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(width / 2)}" ry="{n(ry)}" fill="url(#a1sh)" opacity="{n(opacity)}"/>'


def puff(x, y, r=8.0, count=4, seed=1, opacity=0.8):
    """A little cloud of dust or tyre smoke on the ground: a few overlapping soft discs."""
    rnd = random.Random(seed)
    out = []
    for i in range(count):
        px, py = x + rnd.uniform(-r, r) * 1.2, y - rnd.uniform(0.0, r * 0.6)
        rr = r * rnd.uniform(0.55, 1.0)
        out.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(rr)}" fill="url(#a1puff)" opacity="{n(opacity)}"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ land
def backdrop(uid, x0, x1, gy, bottom, seed=3, far=26.0, mid=12.0, base=14.0, grain=True, scrub_count=None, haze=0.0, palms=(), acacias=(), houses=(), tone="day"):
    """The land of a profile: pale hills on the horizon (their foot `base` units above the line `gy`), a plain of sand from there to `bottom` that warms towards the foot,
    scrub that grows towards the foot, whatever stands on it. Drawn from the horizon forward as one string."""
    hz = gy - base
    f1 = S.ridge(seed, x0, x1, hz + 2, far, peaks=0.62)
    f2 = S.ridge(seed + 7, x0, x1, hz + 3, far * 0.55, peaks=0.35)
    f3 = S.ridge(seed + 11, x0, x1, hz + 5, mid)
    out = [S.land_layer(uid + "f", f1, bottom, ("#8391B3", "#BDC8DD"), rim=True, haze=0.34),
           S.land_layer(uid + "g", f2, bottom, ("#9DA9C6", "#C9D1E0"), rim=True, haze=0.22),
           S.land_layer(uid + "m", f3, bottom, ("#CDB085", "#E4D0A6"), rim=True, haze=0.08)]
    out.append(f'<defs>{S.gradient(uid + "p", [(0, "#EEDFB8"), (0.25, "#E8D5A8"), (1, "#D3B882")])}</defs>'
               f'<rect x="{n(x0)}" y="{n(hz + 6)}" width="{n(x1 - x0)}" height="{n(bottom - hz - 6)}" fill="url(#{uid}p)"/>')
    out.append(f'<defs>{S.gradient(uid + "q", [(0, "#F7EFD6", 0.7), (1, "#F7EFD6", 0.0)])}</defs><rect x="{n(x0)}" y="{n(hz + 6)}" width="{n(x1 - x0)}" height="{n(base * 0.8)}" fill="url(#{uid}q)"/>')
    out.append(S.dune(uid + "d", x0, x1, hz + 9, 4.5, seed + 31))
    count = scrub_count if scrub_count is not None else int((x1 - x0) / 10)
    out.append(S.scrub(seed + 5, x0, x1, hz + 8, bottom - 2, count, scale=0.9))
    if grain:
        gid = uid + "n"
        out.append(f'<defs><filter id="{gid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed}"/>'
                   f'<feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.34  0 0 0 0 0.2  0 0 0 0.45 -0.1"/></filter></defs>'
                   f'<rect x="{n(x0)}" y="{n(gy + 5)}" width="{n(x1 - x0)}" height="{n(bottom - gy - 5)}" filter="url(#{gid})" opacity="0.4"/>')
    for (x, y, s_) in houses:
        out.append(S.house(x, y, 18.0 * s_, 10.0 * s_, seed + int(x)))
    for (x, y, s_) in acacias:
        out.append(S.acacia(x, y, 14.0 * s_, seed + int(x)))
    for (x, y, s_) in palms:
        out.append(S.palm(x, y, 26.0 * s_, 0.10, seed + int(x)))
    return "".join(out)


def runway(uid, x0, x1, gy, half=4.2, centre=True, threshold=False, aim=None, lights=True, far_lights_only=False, dash_from=None, shoulder=True):
    """A runway seen almost edge-on from a little above: a dark asphalt strip from gy - half (its far edge) to gy + half (its near edge) between x0 and x1, a paler shoulder of
    gravel either side, a dashed centreline, bars across the threshold at x0 when `threshold` is set, the aiming-point marks as two broad bars at x = `aim` and the
    edge lights of the far edge (those of the near edge are drawn by `edge_lights`, after the aeroplanes)."""
    h2 = half * 2
    out = []
    if shoulder:
        out.append(f'<rect x="{n(x0 - 1)}" y="{n(gy - half - 1.6)}" width="{n(x1 - x0 + 2)}" height="{n(h2 + 4.2)}" fill="#C9B48A" opacity="0.8"/>')
    out.append(f'<defs>{S.gradient(uid + "a", [(0, "#6B7587"), (0.18, "#4C5565"), (1, "#323A48")])}</defs>'
               f'<rect x="{n(x0)}" y="{n(gy - half)}" width="{n(x1 - x0)}" height="{n(h2)}" fill="url(#{uid}a)"/>'
               f'<rect x="{n(x0)}" y="{n(gy - half)}" width="{n(x1 - x0)}" height="0.9" fill="#AEB8C8" opacity="0.65"/>'
               f'<rect x="{n(x0)}" y="{n(gy + half - 0.7)}" width="{n(x1 - x0)}" height="1.4" fill="#222934" opacity="0.7"/>')
    if centre:
        start = (dash_from if dash_from is not None else x0) + 8
        x = start
        d = []
        while x + 12 < x1 - 4:
            d.append(f'<rect x="{n(x)}" y="{n(gy - 0.7)}" width="12" height="1.4" rx="0.3" fill="#F4F6FA" opacity="0.92"/>')
            x += 24
        out.append("".join(d))
    if threshold:
        for i in range(7):
            yy = gy - half + 1.0 + i * (h2 - 2.0) / 7.0
            out.append(f'<rect x="{n(x0 + 3)}" y="{n(yy)}" width="15" height="{n((h2 - 2.0) / 7.0 * 0.66)}" fill="#FAFBFD" opacity="0.97"/>')
    if aim is not None:
        for yy in (gy - half + 1.0, gy + 0.9):
            out.append(f'<rect x="{n(aim - 9)}" y="{n(yy)}" width="18" height="{n(half - 1.8)}" fill="#F8FAFD" opacity="0.96"/>')
    if lights:
        x = x0 + 12
        while x < x1 - 6:
            out.append(f'<circle cx="{n(x)}" cy="{n(gy - half - 0.2)}" r="2.6" fill="url(#a1lg)" opacity="0.9"/><circle cx="{n(x)}" cy="{n(gy - half - 0.2)}" r="0.7" fill="#FFFBE6"/>')
            x += 24
    return "".join(out)


def edge_lights(x0, x1, gy, half=4.2, step=24.0, start=0.0):
    """The lights along the near edge of a runway (these stand in front of an aeroplane on it)."""
    out = []
    x = x0 + 12 + start
    while x < x1 - 6:
        out.append(f'<circle cx="{n(x)}" cy="{n(gy + half + 0.6)}" r="3.2" fill="url(#a1lg)" opacity="0.95"/><circle cx="{n(x)}" cy="{n(gy + half + 0.6)}" r="0.95" fill="#FFFBE6"/>')
        x += step
    return "".join(out)


def windsock(x, gy, h=24.0, wind=-1.0, seed=1):
    """A windsock on a pole standing at (x, gy), blowing towards the left when `wind` is -1 and towards the right when it is +1."""
    topx, topy = x, gy - h
    pole = (f'<line x1="{n(x)}" y1="{n(gy)}" x2="{n(topx)}" y2="{n(topy)}" stroke="#E8ECF2" stroke-width="1.6" stroke-linecap="round"/>'
            f'<line x1="{n(x + 0.5)}" y1="{n(gy)}" x2="{n(topx + 0.5)}" y2="{n(topy)}" stroke="#7C8798" stroke-width="0.6"/>')
    segs = 5
    length, r0, r1 = 17.0, 3.6, 1.6
    cols = ["#F26B21", "#FFFFFF", "#F26B21", "#FFFFFF", "#F26B21"]
    sock = []
    for i in range(segs):
        t0, t1 = i / segs, (i + 1) / segs
        xa, xb = topx + wind * length * t0, topx + wind * length * t1
        ya, yb = topy + 1.5 * t0 * t0 * 3.0, topy + 1.5 * t1 * t1 * 3.0
        ra, rb = r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1
        sock.append(f'<polygon points="{pts([(xa, ya - ra), (xb, yb - rb), (xb, yb + rb), (xa, ya + ra)])}" fill="{cols[i]}"/>')
    shade = f'<polygon points="{pts([(topx, topy), (topx + wind * length, topy + 4.5 - 1.6), (topx + wind * length, topy + 4.5 + 1.6), (topx, topy + 3.6)])}" fill="#1B2338" opacity="0.1"/>'
    ring = f'<ellipse cx="{n(topx)}" cy="{n(topy)}" rx="0.9" ry="3.8" fill="none" stroke="#9AA6B8" stroke-width="0.8"/>'
    ground = f'<ellipse cx="{n(x + 2)}" cy="{n(gy + 0.4)}" rx="5" ry="1.1" fill="#6B573A" opacity="0.3"/>'
    return ground + pole + "".join(sock) + shade + ring


def mast(x, gy, h=48.0, base=12.0, top=4.0, light=True):
    """A lattice mast standing at (x, gy): two splayed legs, cross-bracing in bays, a platform and a red light on the top, with a shadow on the ground."""
    out = [f'<ellipse cx="{n(x + 5)}" cy="{n(gy + 0.6)}" rx="{n(base * 0.8)}" ry="1.4" fill="#6B573A" opacity="0.3"/>']
    ytop = gy - h
    xl0, xr0 = x - base / 2, x + base / 2
    xl1, xr1 = x - top / 2, x + top / 2
    bays = 4
    rows = [(gy - h * i / bays, x - (base / 2 - (base - top) / 2 * i / bays), x + (base / 2 - (base - top) / 2 * i / bays)) for i in range(bays + 1)]
    for (y1, a1, b1), (y2, a2, b2) in zip(rows, rows[1:]):
        out.append(f'<line x1="{n(a1)}" y1="{n(y1)}" x2="{n(b2)}" y2="{n(y2)}" stroke="#F3F5F9" stroke-width="0.9"/><line x1="{n(b1)}" y1="{n(y1)}" x2="{n(a2)}" y2="{n(y2)}" stroke="#F3F5F9" stroke-width="0.9"/>')
        out.append(f'<line x1="{n(a2)}" y1="{n(y2)}" x2="{n(b2)}" y2="{n(y2)}" stroke="#C7CFDB" stroke-width="1"/>')
    out.append(f'<line x1="{n(xl0)}" y1="{n(gy)}" x2="{n(xl1)}" y2="{n(ytop)}" stroke="#DDE3EC" stroke-width="1.9" stroke-linecap="round"/><line x1="{n(xr0)}" y1="{n(gy)}" x2="{n(xr1)}" y2="{n(ytop)}" stroke="#9AA5B6" stroke-width="1.9" stroke-linecap="round"/>')
    out.append(f'<line x1="{n(xl0)}" y1="{n(gy)}" x2="{n(xl1)}" y2="{n(ytop)}" stroke="#FFFFFF" stroke-width="0.6" opacity="0.8"/>')
    out.append(f'<rect x="{n(x - top / 2 - 1.8)}" y="{n(ytop - 1.4)}" width="{n(top + 3.6)}" height="2.4" rx="0.8" fill="#C7CFDB" stroke="#7C8798" stroke-width="0.5"/>')
    out.append(f'<line x1="{n(x)}" y1="{n(ytop - 1.4)}" x2="{n(x)}" y2="{n(ytop - 7)}" stroke="#9AA5B6" stroke-width="0.9"/>')
    if light:
        out.append(f'<circle cx="{n(x)}" cy="{n(ytop - 2.8)}" r="6.5" fill="url(#a1red)"/><circle cx="{n(x)}" cy="{n(ytop - 2.8)}" r="1.8" fill="#E5322B" stroke="#FFFFFF" stroke-width="0.5"/>')
    return "".join(out)


def hangar(x, gy, w=44.0, h=22.0):
    """A hangar with a round roof and a door, standing on (x, gy) (its left foot)."""
    r = h * 0.42
    return (f'<ellipse cx="{n(x + w / 2 + 3)}" cy="{n(gy + 0.5)}" rx="{n(w * 0.62)}" ry="1.6" fill="#6B573A" opacity="0.28"/>'
            f'<path d="M {n(x)},{n(gy)} L {n(x)},{n(gy - h + r)} Q {n(x + w / 2)},{n(gy - h - r * 0.6)} {n(x + w)},{n(gy - h + r)} L {n(x + w)},{n(gy)} Z" fill="#D8DFEA"/>'
            f'<path d="M {n(x + w * 0.7)},{n(gy)} L {n(x + w * 0.7)},{n(gy - h + r * 0.5)} Q {n(x + w * 0.85)},{n(gy - h - r * 0.1)} {n(x + w)},{n(gy - h + r)} L {n(x + w)},{n(gy)} Z" fill="#9FACC2" opacity="0.5"/>'
            f'<path d="M {n(x)},{n(gy - h + r)} Q {n(x + w / 2)},{n(gy - h - r * 0.6)} {n(x + w)},{n(gy - h + r)}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.9"/>'
            f'<rect x="{n(x + w * 0.2)}" y="{n(gy - h * 0.62)}" width="{n(w * 0.52)}" height="{n(h * 0.62)}" fill="#8B98B0"/><rect x="{n(x + w * 0.2)}" y="{n(gy - h * 0.62)}" width="{n(w * 0.52)}" height="1.6" fill="#65728B"/>')


# ------------------------------------------------------------------------------------------------------------------ paths and cards
def path_line(d, colour, width=2.4, dash=None, casing=2.4, opacity=1.0, cap="round", gradient_id=None, glow=True):
    """A path with a white casing under it. `colour` may be "url(#id)" for a gradient defined elsewhere."""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out = ""
    if glow:
        out += f'<path d="{d}" fill="none" stroke="#10233F" stroke-opacity="0.16" stroke-width="{n(width + casing + 1.2)}" stroke-linecap="{cap}" stroke-linejoin="round"{dash_attr} transform="translate(0.8 1.6)"/>'
    out += f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="{n(width + casing)}" stroke-linecap="{cap}" stroke-linejoin="round"{dash_attr}/>'
    out += f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-linecap="{cap}" stroke-linejoin="round"{dash_attr}/>'
    return out


def line_cased(x1, y1, x2, y2, colour, width=1.4, dash=None, casing=2.2, opacity=1.0):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#FFFFFF" stroke-opacity="0.88" stroke-width="{n(width + casing)}" stroke-linecap="round"{dash_attr}/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-linecap="round"{dash_attr}/>')


def arrow_head(x, y, angle_deg, size=7.0, colour="#1F2937"):
    """A solid arrowhead with its tip at (x, y) pointing along `angle_deg` (clockwise from the +x axis, y down)."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    p = [(x, y), (x - ux * size - nx * size * 0.52, y - uy * size - ny * size * 0.52), (x - ux * size * 0.7, y - uy * size * 0.7), (x - ux * size + nx * size * 0.52, y - uy * size + ny * size * 0.52)]
    return f'<polygon points="{pts(p)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" paint-order="stroke"/>'


def leader(x1, y1, x2, y2):
    """A thin leader from a card or a label to the thing it belongs to: a pale casing, a dark core, a dot at the end (x2, y2)."""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.85" stroke-linecap="round"/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#4B5870" stroke-width="0.9" stroke-linecap="round"/>'
            f'<circle cx="{n(x2)}" cy="{n(y2)}" r="1.8" fill="#4B5870" stroke="#FFFFFF" stroke-width="0.9"/>')


def card(uid, x, y, w, h, radius=6.0):
    """A small white card with a soft shadow (the speed and the height boxes of the old figures)."""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}" fill="#FFFFFF" fill-opacity="0.96" filter="url(#a1ds)"/>'
            f'<rect x="{n(x + 0.5)}" y="{n(y + 0.5)}" width="{n(w - 1)}" height="{n(h - 1)}" rx="{n(radius - 0.5)}" fill="none" stroke="#C5CFDD" stroke-width="0.9"/>')


def speed_card(uid, x, y, label, flap=None, w=66.0, h=None, mono=True, flap_colour="#1D4ED8"):
    """The old figures' box with a speed (VR 55, 60) and, under it, the flap setting: a small aeroplane, a dashed reference line and the flap as a bar turned down by
    `flap` degrees from it, the angle. With no `label` the box holds the flap setting alone. Returns a list of layers (markup and a sprite)."""
    h = h or (42.0 if flap is not None and label else 25.0)
    family = "monospace" if mono else "sans-serif"
    out = [card(uid, x, y, w, h)]
    if label:
        out.append(f'<text x="{n(x + w / 2)}" y="{n(y + 16.5)}" font-family="{family}" font-size="12.5" font-weight="bold" fill="#1F2937" text-anchor="middle">{label}</text>')
    if flap is not None:
        cy = y + (31.0 if label else h / 2 + 0.2)
        out.append({"name": "sprite-side", "at": [x + 16, cy - 0.5], "width": 28, **LOOK_SOFT})
        a = math.radians(flap)
        hx, hy = x + 29.5, cy + 0.5
        out.append(f'<line x1="{n(hx)}" y1="{n(hy)}" x2="{n(hx + 11)}" y2="{n(hy)}" stroke="#94A3B8" stroke-width="1" stroke-dasharray="2 2"/>'
                   f'<line x1="{n(hx)}" y1="{n(hy)}" x2="{n(hx + 11 * math.cos(a))}" y2="{n(hy + 11 * math.sin(a))}" stroke="{flap_colour}" stroke-width="2.8" stroke-linecap="round"/>'
                   f'<text x="{n(x + w - 14)}" y="{n(cy + 4.2)}" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="middle">{flap}°</text>')
    return out


def flatten(items):
    out = []
    for it in items:
        if isinstance(it, (list, tuple)):
            out.extend(flatten(it))
        else:
            out.append(it)
    return out


# ------------------------------------------------------------------------------------------------------------------ a card with a scene in it
def cloud(name, cx, cy, width, opacity=0.95, haze=0.18, **kw):
    return {"name": name, "at": [cx, cy], "width": width, "opacity": opacity, "haze": {"colour": "#CFE0F3", "amount": haze}, **kw}


def profile(uid, box, gy, seed=3, sun=(80, 70), runway_args=None, clouds=(), far=24.0, mid=11.0, base=13.0, palms=(), acacias=(), houses=(), objects="", sky=SKY, radius=10.0, scrub_count=None, grain=True):
    """A card with a profile scene: the sky and the sun's glow, the clouds (sprites), the land (hills on the horizon, the plain, scrub, what stands on it), a runway
    (`runway_args`: a dict for `runway()`; its x range is `x0`, `x1`) and `objects` (markup: a mast, a windsock). Returns a list of layers, back to front."""
    x, y, w, h = box
    back = [S.card(uid + "c", x, y, w, h, sky, S.glow(uid + "g", x + sun[0], y + sun[1], 190, "#FFF1CC", 0.5), radius=radius)]
    back += list(clouds)
    land = backdrop(uid + "l", x, x + w, gy, y + h, seed=seed, far=far, mid=mid, base=base, palms=palms, acacias=acacias, houses=houses, scrub_count=scrub_count, grain=grain)
    if runway_args:
        land += runway(uid + "r", gy=gy, **runway_args)
    land += objects
    back.append(S.card_front(uid + "w", x, y, w, h, land, radius=radius))
    return back


def foreground(uid, box, gy, seed=3, lights=None, scrub=11, scale=1.25, radius=10.0, extra=""):
    """What stands in front of the aeroplanes: the near edge lights of a runway (`lights` = (x0, x1)), the scrub of the foot of the card."""
    x, y, w, h = box
    inner = edge_lights(lights[0], lights[1], gy, 4.2) if lights else ""
    inner += S.scrub(seed + 40, x + 6, x + w - 6, gy + 12, y + h - 3, scrub, scale=scale) + extra
    return S.card_front(uid + "f", x, y, w, h, inner, radius=radius)


def page(uid, w, h):
    return f'<defs>{S.gradient(uid, [(0, "#F1F5FA"), (1, "#E6EDF5")])}</defs><rect x="0" y="0" width="{w}" height="{h}" fill="url(#{uid})"/>'


def plane_mid(tx, ty, angle=0.0, width=84.0, name="sprite-side", look=None, **extra):
    """sprite-side with the middle of its wheel line on (tx, ty) (where an old silhouette's origin was), turned about that point by `angle` (degrees clockwise; nose up is negative)."""
    h = width * ASPECT
    a = math.radians(angle)
    ly = -h / 2
    o = {"name": name, "at": [round(tx - ly * math.sin(a), 1), round(ty + ly * math.cos(a), 1)], "width": width, **(look or LOOK), **extra}
    if angle:
        o["angle"] = angle
    return o


def flap_mark(o, deg, colour="#1D4ED8", length=0.1, hinge=(0.565, 0.295), width=2.1):
    """The flap of the old figure's aeroplane: a short bar turned down by `deg` from the trailing edge of the wing of sprite `o` (placed by `plane`, `plane_mid` or by hand: it
    needs its "at", "width" and "angle"), as markup."""
    w = o["width"]
    h = w * ASPECT
    a = math.radians(o.get("angle", 0.0))
    cx, cy = o["at"]

    def where(u, v):
        dx, dy = (u - 0.5) * w, (v - 0.5) * h
        return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
    x1, y1 = where(*hinge)
    d = math.radians(deg)
    x2, y2 = where(hinge[0] - length * math.cos(d), hinge[1] + length * w / h * math.sin(d))
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#FFFFFF" stroke-width="{n(width + 1.6)}" stroke-linecap="round" opacity="0.9"/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{colour}" stroke-width="{n(width)}" stroke-linecap="round"/>')


def grass_strip(uid, x0, x1, gy, half=4.6, seed=1):
    """A soft strip, grass and loose sand, seen almost edge-on: a pale-green band from gy - half to gy + half with a sandy shoulder, two faint wheel tracks, tufts of grass."""
    rnd = random.Random(seed)
    h2 = half * 2
    out = [f'<rect x="{n(x0 - 1)}" y="{n(gy - half - 2.0)}" width="{n(x1 - x0 + 2)}" height="{n(h2 + 4.6)}" fill="#E4D2A0" opacity="0.7"/>',
           f'<defs>{S.gradient(uid + "g", [(0, "#C9C98B"), (0.5, "#B2B873"), (1, "#97A25C")])}</defs><rect x="{n(x0)}" y="{n(gy - half)}" width="{n(x1 - x0)}" height="{n(h2)}" fill="url(#{uid}g)"/>',
           f'<rect x="{n(x0)}" y="{n(gy - half)}" width="{n(x1 - x0)}" height="0.8" fill="#EFEBC0" opacity="0.7"/>',
           f'<rect x="{n(x0)}" y="{n(gy + half - 0.8)}" width="{n(x1 - x0)}" height="1.2" fill="#6F7B43" opacity="0.5"/>']
    for yy in (gy - 1.6, gy + 1.9):
        out.append(f'<line x1="{n(x0)}" y1="{n(yy)}" x2="{n(x1)}" y2="{n(yy)}" stroke="#7D8A4B" stroke-width="0.9" opacity="0.45"/>')
    x = x0 + 4
    while x < x1 - 2:
        yy = gy + rnd.uniform(-half, half + 1.5)
        cols = ["#6E8B3A", "#85A04B", "#9BB259"]
        for k in range(rnd.randint(3, 5)):
            ang = math.radians(rnd.uniform(-35, 35))
            ln = rnd.uniform(1.8, 3.4)
            out.append(f'<line x1="{n(x + k * 0.6)}" y1="{n(yy)}" x2="{n(x + k * 0.6 + math.sin(ang) * ln)}" y2="{n(yy - math.cos(ang) * ln)}" stroke="{rnd.choice(cols)}" stroke-width="0.6" stroke-linecap="round"/>')
        x += rnd.uniform(5, 13)
    return "".join(out)


def air_block(uid, x0, y0, x1, y1, top_dash=True, colour="#CFE3FA", opacity=0.42, dash_colour="#1D4ED8"):
    """A region of air (the ground effect zone): a translucent veil, clearer at the top, with a dashed line along its top."""
    out = [f'<defs>{S.gradient(uid, [(0, colour, opacity), (1, "#EAF3FC", opacity * 0.3)])}</defs><rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="url(#{uid})"/>',
           f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x0)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="1"/>']
    if top_dash:
        out.append(line_cased(x0, y0, x1, y0, dash_colour, 1.3, dash="4 4", casing=2.0))
    return "".join(out)


def clipped(uid, box, radius, layers):
    """Layers (markup and sprites) cut to a rounded card: returns the list with a group opened before and closed after them."""
    x, y, w, h = box
    return [f'<defs><clipPath id="{uid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(radius)}"/></clipPath></defs><g clip-path="url(#{uid})">', *layers, "</g>"]


def plane_c(cx, cy, angle=0.0, width=72.0, name="sprite-side", look=None, **extra):
    """sprite-side centred on (cx, cy), turned about its centre by `angle` (degrees clockwise; nose up is negative)."""
    o = {"name": name, "at": [round(cx, 1), round(cy, 1)], "width": width, **(look or LOOK), **extra}
    if angle:
        o["angle"] = angle
    return o


def horizon_sky(frac):
    """Sky stops for a card whose horizon lies at `frac` of its height from the top: deep blue above, pale by the horizon, warm at it."""
    return [(0.0, "#4A84CB"), (round(frac * 0.5, 3), "#86B4E6"), (round(frac * 0.9, 3), "#D5E5F5"), (round(frac, 3), "#F7F0DA"), (1.0, "#F7F0DA")]


def airliner(uid, cx, cy, length=150.0, angle=0.0, gear=True, tail="#2F5A93"):
    """A heavy aeroplane seen from the side, nose to the right, drawn as a vector (the model has no such aeroplane): a white fuselage shaded from the top down, a window row, a fin in
    colour, a swept wing and an engine, and, when `gear` is set, the wheels. (cx, cy) is the middle of the fuselage; `angle` turns it clockwise about that point; the wheels reach
    15 * length / 150 below it."""
    k = length / 150.0
    fus = "M -75 -5 C -62 -9 -45 -8.6 -30 -8.8 L 46 -8.8 C 62 -8.8 72 -4.6 76 0 C 72 4.4 62 7.6 46 8.2 L -30 8.2 C -48 8.2 -62 4.2 -75 -1.5 Z"
    fin = "M -72 -6.4 L -81 -35 L -68.5 -35 L -46 -8.7 Z"
    stab = "M -73 -6.5 L -50 -7.2 L -45 -3.4 L -70 -3.2 Z"
    wing = "M -10 4.8 L 22 4.8 L 4 11 L -36 11 Z"
    out = [f'<defs>{S.gradient(uid + "f", [(0, "#FFFFFF"), (0.55, "#E6EBF3"), (1, "#AEB8C9")])}{S.gradient(uid + "t", [(0, "#5A8AC6"), (1, "#24477C")], 0, 0, 1, 0)}'
           f'{S.gradient(uid + "w", [(0, "#C9D1DE"), (1, "#8E9AB0")])}<clipPath id="{uid}c"><path d="{fus}"/></clipPath></defs>',
           f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(angle)}) scale({n(k)})">']
    if gear:
        out.append('<g stroke="#2B3648" stroke-width="1.5" stroke-linecap="round"><line x1="-6" y1="7" x2="-6" y2="12"/><line x1="2" y1="7" x2="2" y2="12"/><line x1="58" y1="6" x2="58" y2="12"/></g>'
                   '<g fill="#1B2338"><circle cx="-6" cy="12.2" r="3"/><circle cx="2" cy="12.2" r="3"/><circle cx="58" cy="12.2" r="2.6"/></g><g fill="#9AA6B8"><circle cx="-6" cy="12.2" r="1.1"/><circle cx="2" cy="12.2" r="1.1"/><circle cx="58" cy="12.2" r="1"/></g>')
    out.append(f'<path d="{wing}" fill="url(#{uid}w)" stroke="#5B6578" stroke-width="0.5"/>')
    out.append(f'<path d="{stab}" fill="#C9D1DE" stroke="#5B6578" stroke-width="0.5"/>')
    out.append(f'<path d="{fin}" fill="url(#{uid}t)" stroke="#1C3560" stroke-width="0.6"/><path d="M -76 -22 L -70 -22 L -59 -8.8" fill="none" stroke="#FFFFFF" stroke-width="1.1" opacity="0.7"/>')
    out.append(f'<rect x="3" y="8.2" width="22" height="8" rx="3.6" fill="url(#{uid}w)" stroke="#5B6578" stroke-width="0.5"/><ellipse cx="24.2" cy="12.2" rx="1.3" ry="3.4" fill="#2B3648"/>')
    out.append(f'<path d="{fus}" fill="url(#{uid}f)" stroke="#5B6578" stroke-width="0.7"/>')
    win = "".join(f'<rect x="{-48 + 4.4 * i}" y="-5.2" width="2" height="2.6" rx="0.8" fill="#35517F"/>' for i in range(23))
    out.append(f'<g clip-path="url(#{uid}c)">{win}<path d="M 53 -6.4 L 64 -6.4 Q 68 -5 70 -2.4 L 54 -2.4 Z" fill="#2B3E63"/><rect x="-75" y="1.6" width="150" height="1" fill="#2F5A93" opacity="0.5"/></g>')
    out.append('</g>')
    return "".join(out)


def dim_line(x0, y0, x1, y1, colour="#10233F", width=1.6, head=7.0, casing=2.6, both=True):
    """A dimension line from (x0, y0) to (x1, y1) with an arrowhead at each end (at the far end only when `both` is off): a pale casing, the line, solid heads."""
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    a = (x0 + ux * head * 0.8, y0 + uy * head * 0.8) if both else (x0, y0)
    b = (x1 - ux * head * 0.8, y1 - uy * head * 0.8)

    def tip(px, py, sx):
        return [(px, py), (px - sx * ux * head + nx * head * 0.5, py - sx * uy * head + ny * head * 0.5), (px - sx * ux * head - nx * head * 0.5, py - sx * uy * head - ny * head * 0.5)]
    out = [f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#FFFFFF" stroke-width="{n(width + casing)}" stroke-opacity="0.85" stroke-linecap="round"/>',
           f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="{colour}" stroke-width="{n(width)}" stroke-linecap="round"/>',
           f'<polygon points="{pts(tip(x1, y1, 1))}" fill="{colour}" stroke="#FFFFFF" stroke-width="1" paint-order="stroke" stroke-linejoin="round"/>']
    if both:
        out.append(f'<polygon points="{pts(tip(x0, y0, -1))}" fill="{colour}" stroke="#FFFFFF" stroke-width="1" paint-order="stroke" stroke-linejoin="round"/>')
    return "".join(out)


def pill(cx, cy, w, h, text, colour="#1F2937", size=13, border=None):
    """A white label with a thin coloured border and bold text, centred on (cx, cy)."""
    border = border or colour
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="4.5" fill="#FFFFFF" fill-opacity="0.97" stroke="{border}" stroke-width="1.3" filter="url(#a1ds)"/>'
            f'<text x="{n(cx)}" y="{n(cy + size * 0.35)}" font-family="sans-serif" font-size="{size}" font-weight="bold" fill="{colour}" text-anchor="middle">{text}</text>')


def vor_station(x, gy, scale=1.0):
    """A VOR/DME station: a low white round building with a flat roof and a cone radome on it, a DME antenna (a mast with a disc), a little shadow; standing on (x, gy)."""
    k = scale
    out = [f'<ellipse cx="{n(x + 6 * k)}" cy="{n(gy + 0.8)}" rx="{n(20 * k)}" ry="{n(1.8 * k)}" fill="#6B573A" opacity="0.3"/>',
           f'<defs>{S.gradient("a1vb", [(0, "#FFFFFF"), (0.5, "#E7EBF2"), (1, "#B8C1D1")], 0, 0, 1, 0)}{S.gradient("a1vc", [(0, "#FFFFFF"), (1, "#C9D1DE")], 0, 0, 1, 0)}</defs>',
           f'<rect x="{n(x - 11 * k)}" y="{n(gy - 11 * k)}" width="{n(22 * k)}" height="{n(11 * k)}" fill="url(#a1vb)" stroke="#7C8798" stroke-width="0.6"/>',
           f'<rect x="{n(x - 12 * k)}" y="{n(gy - 12.4 * k)}" width="{n(24 * k)}" height="{n(2.4 * k)}" rx="0.8" fill="#D8DEE8" stroke="#7C8798" stroke-width="0.5"/>',
           f'<path d="M {n(x - 7 * k)},{n(gy - 12.4 * k)} Q {n(x)},{n(gy - 26 * k)} {n(x + 7 * k)},{n(gy - 12.4 * k)} Z" fill="url(#a1vc)" stroke="#7C8798" stroke-width="0.5"/>',
           f'<rect x="{n(x - 3 * k)}" y="{n(gy - 7 * k)}" width="{n(6 * k)}" height="{n(7 * k)}" fill="#6F7E96"/>',
           f'<line x1="{n(x + 8 * k)}" y1="{n(gy - 12 * k)}" x2="{n(x + 8 * k)}" y2="{n(gy - 22 * k)}" stroke="#7C8798" stroke-width="1"/><ellipse cx="{n(x + 8 * k)}" cy="{n(gy - 22.4 * k)}" rx="{n(3 * k)}" ry="{n(1.1 * k)}" fill="#E5EAF2" stroke="#7C8798" stroke-width="0.5"/>']
    return "".join(out)


def beam(x1, y1, x2, y2, colour, core="#FFFFFF", width=2.6, dash=None):
    """A beam of light: a wide soft glow, the coloured beam, a thin bright core (the plate needs the filter `a1glow`, see `glow_defs`)."""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{colour}" stroke-width="{n(width * 3.4)}" stroke-opacity="0.45" stroke-linecap="round" filter="url(#a1glow)"/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{colour}" stroke-width="{n(width)}" stroke-linecap="round"{dash_attr}/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{core}" stroke-width="{n(width * 0.38)}" stroke-opacity="0.9" stroke-linecap="round"{dash_attr}/>')


def glow_defs(w, h):
    """The soft filter the beams use, over the whole canvas of a plate (w, h)."""
    return f'<defs><filter id="a1glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><feGaussianBlur stdDeviation="2.8"/></filter></defs>'


def control_tower(x, gy, h=36.0, shaft=7.0, cab=17.0):
    """A control tower standing on (x, gy): a slim shaft, a cab with dark glass all round and a roof slab with a mast, a shadow."""
    top = gy - h
    out = [f'<ellipse cx="{n(x + 5)}" cy="{n(gy + 0.6)}" rx="{n(shaft * 1.4)}" ry="1.4" fill="#6B573A" opacity="0.3"/>',
           f'<defs>{S.gradient("a1twr", [(0, "#FFFFFF"), (0.55, "#DDE3EC"), (1, "#A5B0C2")], 0, 0, 1, 0)}{S.gradient("a1twg", [(0, "#5A7FB0"), (1, "#26406A")])}</defs>',
           f'<rect x="{n(x - shaft / 2)}" y="{n(top + 9)}" width="{n(shaft)}" height="{n(h - 9)}" fill="url(#a1twr)" stroke="#7C8798" stroke-width="0.5"/>',
           f'<path d="M {n(x - cab / 2 - 1)},{n(top + 9)} L {n(x - cab / 2 + 1)},{n(top + 1)} L {n(x + cab / 2 - 1)},{n(top + 1)} L {n(x + cab / 2 + 1)},{n(top + 9)} Z" fill="url(#a1twg)" stroke="#2B3648" stroke-width="0.6"/>',
           f'<line x1="{n(x - cab / 2 + 4)}" y1="{n(top + 1.5)}" x2="{n(x - cab / 2 + 3)}" y2="{n(top + 8.5)}" stroke="#FFFFFF" stroke-width="0.6" opacity="0.7"/>',
           f'<rect x="{n(x - cab / 2 - 2)}" y="{n(top - 1.6)}" width="{n(cab + 4)}" height="2.8" rx="1" fill="#E7ECF3" stroke="#7C8798" stroke-width="0.5"/>',
           f'<line x1="{n(x)}" y1="{n(top - 1.6)}" x2="{n(x)}" y2="{n(top - 8)}" stroke="#7C8798" stroke-width="0.9"/><circle cx="{n(x)}" cy="{n(top - 8.4)}" r="1.2" fill="#E5322B"/>']
    return "".join(out)
