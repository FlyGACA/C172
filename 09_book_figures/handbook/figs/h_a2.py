"""Helpers of worker a2 (aerodrome, airspace and traffic figures): pavement and paint, lights, small buildings, windsocks and a few other pieces, as SVG markup.
Plain Python (no Blender, no Pillow). Light falls from the upper left everywhere: shadows go to the lower right. Every gradient and filter takes an id made from the
figure's `uid`, so that two pieces of one drawing never share one (the figures use ids that start with their own tag)."""
import math
import random

from figs import scene as S

n = S.n
pts = S.pts

SHADOW = "#3A2C1A"          # the colour of a shadow on sand


# ------------------------------------------------------------------------------------------------------------------ small helpers
def rrect_path(x, y, w, h, r):
    """A rounded rectangle as path data (so that it can be a hole in a bigger path)."""
    r = min(r, w / 2, h / 2)
    return (f"M {n(x + r)},{n(y)} L {n(x + w - r)},{n(y)} A {n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} L {n(x + w)},{n(y + h - r)} A {n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} "
            f"L {n(x + r)},{n(y + h)} A {n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} L {n(x)},{n(y + r)} A {n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)} Z")


def shadow_filter(uid, dx=1.4, dy=2.0, blur=1.3, opacity=0.34, colour=SHADOW):
    """A drop shadow, as a filter (put the result in a <defs>); use it as filter="url(#uid)" on a shape or a group."""
    return (f'<filter id="{uid}" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="{n(dx)}" dy="{n(dy)}" stdDeviation="{n(blur)}" '
            f'flood-color="{colour}" flood-opacity="{n(opacity)}"/></filter>')


def blur_filter(uid, sd=1.5):
    return f'<filter id="{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{n(sd)}"/></filter>'


# ------------------------------------------------------------------------------------------------------------------ pavement
def asphalt_filter(uid, seed=4, relief=0.9, tone=0, blotch=0.34):
    """A filter that turns any shape into asphalt: fine aggregate lit from the upper left, big soft blotches of a darker and a lighter tone. `tone` (0 dark, 1 a lighter,
    worn surface) moves the colours; the shape's own fill does not matter."""
    lo = [0.105 + 0.05 * tone, 0.115 + 0.05 * tone, 0.135 + 0.05 * tone]
    hi = [0.40 + 0.07 * tone, 0.43 + 0.07 * tone, 0.49 + 0.07 * tone]
    mid = [(a + b) / 2 for a, b in zip(lo, hi)]
    table = lambda i: f"{n(lo[i])} {n(lo[i] + (mid[i] - lo[i]) * 1.1)} {n(mid[i] + (hi[i] - mid[i]) * 0.5)} {n(hi[i])}"
    return (f'<filter id="{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="{seed}" result="g"/>'
            f'<feDiffuseLighting in="g" surfaceScale="{n(relief)}" diffuseConstant="1" lighting-color="#ffffff" result="lit"><feDistantLight azimuth="225" elevation="60"/></feDiffuseLighting>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.016 0.03" numOctaves="3" seed="{seed + 5}" result="b"/>'
            f'<feColorMatrix in="b" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="blot"/>'
            f'<feComposite in="lit" in2="blot" operator="arithmetic" k1="0" k2="{n(1 - blotch)}" k3="{n(blotch)}" k4="0" result="mix"/>'
            f'<feComponentTransfer in="mix"><feFuncR type="table" tableValues="{table(0)}"/><feFuncG type="table" tableValues="{table(1)}"/><feFuncB type="table" tableValues="{table(2)}"/></feComponentTransfer>'
            f'<feComposite in2="SourceAlpha" operator="in"/></filter>')


def concrete_filter(uid, seed=8, relief=0.5):
    """A filter that turns a shape into pale concrete (the apron): a light grey with a fine grain and a few soft stains."""
    return (f'<filter id="{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="{seed}" result="g"/>'
            f'<feDiffuseLighting in="g" surfaceScale="{n(relief)}" diffuseConstant="1" lighting-color="#ffffff" result="lit"><feDistantLight azimuth="225" elevation="62"/></feDiffuseLighting>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.02 0.03" numOctaves="3" seed="{seed + 3}" result="b"/>'
            f'<feColorMatrix in="b" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="blot"/>'
            f'<feComposite in="lit" in2="blot" operator="arithmetic" k1="0" k2="0.7" k3="0.3" k4="0" result="mix"/>'
            f'<feComponentTransfer in="mix"><feFuncR type="table" tableValues="0.50 0.62 0.70 0.76"/><feFuncG type="table" tableValues="0.51 0.63 0.71 0.77"/><feFuncB type="table" tableValues="0.52 0.64 0.71 0.76"/></feComponentTransfer>'
            f'<feComposite in2="SourceAlpha" operator="in"/></filter>')


def paint_filter(uid, seed=11, wear=1.0, thickness=0.5):
    """A filter for paint laid on asphalt: the shapes lose a few specks and flakes (`wear` 0 none, 1 a little, 2 a lot) and stand a little off the surface (a thin dark edge on
    the lower right, as the shadow of a coat that is a millimetre thick)."""
    # the mask is 1 where the paint stays: its alpha falls to 0 only where the noise is low
    cut = 1.75 + 0.5 * (wear - 1.0)
    shape = (f'<feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="3" seed="{seed}" result="n"/>'
             f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  7 0 0 0 {n(-cut)}" result="m"/>') if wear > 0 else ""
    worn = '<feComposite in="SourceGraphic" in2="m" operator="in" result="worn"/>' if wear > 0 else '<feOffset in="SourceGraphic" result="worn"/>'
    return (f'<filter id="{uid}" x="-2%" y="-4%" width="104%" height="108%" color-interpolation-filters="sRGB">{shape}{worn}'
            f'<feGaussianBlur in="worn" stdDeviation="{n(thickness)}" result="ba"/><feOffset in="ba" dx="{n(thickness)}" dy="{n(thickness * 1.2)}" result="o"/>'
            f'<feColorMatrix in="o" type="matrix" values="0 0 0 0 0.05  0 0 0 0 0.06  0 0 0 0 0.09  0 0 0 0.62 0" result="sh"/>'
            f'<feMerge><feMergeNode in="sh"/><feMergeNode in="worn"/></feMerge></filter>')


# ------------------------------------------------------------------------------------------------------------------ lights
LAMP = {"white": ("#FFFFFF", "#FFF4CF", "#FFE9A8"), "green": ("#D9FFE7", "#3FE08A", "#17B061"), "red": ("#FFE3E0", "#FF5648", "#D7261B"),
        "blue": ("#E1F0FF", "#5AA8FF", "#2B6FE0"), "amber": ("#FFF6D6", "#FFC94A", "#F29A12"), "yellow": ("#FFFBD9", "#FFE459", "#F2C21A")}


def lamp_defs(uid):
    """The glow of every colour of lamp, as radial gradients (ids uid + colour name). Put the result in a <defs> once per figure."""
    out = []
    for name, (core, mid, edge) in LAMP.items():
        out.append(f'<radialGradient id="{uid}{name}"><stop offset="0" stop-color="{mid}" stop-opacity="0.95"/><stop offset="0.25" stop-color="{mid}" stop-opacity="0.55"/>'
                   f'<stop offset="0.6" stop-color="{edge}" stop-opacity="0.16"/><stop offset="1" stop-color="{edge}" stop-opacity="0"/></radialGradient>')
        out.append(f'<radialGradient id="{uid}{name}c" cx="0.38" cy="0.34" r="0.75"><stop offset="0" stop-color="{core}"/><stop offset="0.55" stop-color="{mid}"/><stop offset="1" stop-color="{edge}"/></radialGradient>')
    return "".join(out)


def lamp(uid, cx, cy, r, colour="white", glow=3.4, strength=1.0):
    """A lit lamp: a soft halo (`glow` times its radius), then a small bulb with a bright centre and a dark rim."""
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * glow)}" fill="url(#{uid}{colour})" opacity="{n(strength)}"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{uid}{colour}c)" stroke="#1B2230" stroke-opacity="0.55" stroke-width="{n(max(0.25, r * 0.22))}"/>')


# ------------------------------------------------------------------------------------------------------------------ solid blocks
def shade(hexcolour, k):
    """The colour multiplied by k (k < 1 darker, k > 1 lighter, towards white)."""
    r, g, b = (int(hexcolour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if k <= 1:
        r, g, b = r * k, g * k, b * k
    else:
        t = k - 1
        r, g, b = r + (255 - r) * t, g + (255 - g) * t, b + (255 - b) * t
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


DEPTH = (0.5, -0.30)         # a block's depth runs up and to the right: for each unit of depth, x grows by 0.5 and y falls by 0.3


def block(x, y, w, d, h, colour, roof=None, uid="b", shadow=True, edge="#FFFFFF", window=None, lean=1.0):
    """A solid block standing on the ground: its front face is w wide and h tall with its foot on (x .. x+w, y), it runs back d (up and to the right), its roof is lit,
    its front is in half shade and its right side is darker; a soft shadow lies on the ground to the lower right. `window`: a colour for a band of glass along the front."""
    ox, oy = DEPTH[0] * d, DEPTH[1] * d
    top = [(x, y - h), (x + w, y - h), (x + w + ox, y - h + oy), (x + ox, y - h + oy)]
    front = [(x, y), (x + w, y), (x + w, y - h), (x, y - h)]
    side = [(x + w, y), (x + w + ox, y + oy), (x + w + ox, y - h + oy), (x + w, y - h)]
    out = []
    if shadow:
        sx, sy = 0.75 * h * lean, 0.45 * h * lean
        base = [(x + w, y), (x + w + ox, y + oy), (x + ox, y + oy)]
        cast = [(x, y), (x + w, y), (x + w + ox, y + oy), (x + w + ox + sx, y + oy + sy), (x + w + sx, y + sy), (x + sx, y + sy)]
        out.append(f'<defs>{blur_filter(uid + "sb", 1.1)}</defs><polygon points="{pts(cast)}" fill="{SHADOW}" opacity="0.32" filter="url(#{uid}sb)"/>')
    out.append(f'<polygon points="{pts(side)}" fill="{shade(colour, 0.72)}"/>')
    out.append(f'<polygon points="{pts(front)}" fill="{shade(colour, 0.9)}"/>')
    if window:
        out.append(f'<rect x="{n(x + w * 0.08)}" y="{n(y - h * 0.62)}" width="{n(w * 0.84)}" height="{n(h * 0.3)}" fill="{window}" opacity="0.9"/>'
                   f'<rect x="{n(x + w * 0.08)}" y="{n(y - h * 0.62)}" width="{n(w * 0.84)}" height="{n(h * 0.08)}" fill="#FFFFFF" opacity="0.25"/>')
    out.append(f'<polygon points="{pts(top)}" fill="{roof or shade(colour, 1.18)}"/>')
    out.append(f'<polyline points="{pts([(x, y), (x, y - h), (x + ox, y - h + oy)])}" fill="none" stroke="{edge}" stroke-opacity="0.55" stroke-width="0.5" stroke-linejoin="round"/>'
               f'<polyline points="{pts([(x, y - h), (x + w, y - h), (x + w + ox, y - h + oy)])}" fill="none" stroke="{edge}" stroke-opacity="0.7" stroke-width="0.5" stroke-linejoin="round"/>')
    return "".join(out)


def tower(uid, x, y, s=1.0):
    """The aerodrome control tower on (x, y) (the middle of its foot): a squat base, a slender shaft and a glazed cab with a roof that overhangs, a mast and a red light on top;
    s scales it. About 28 s wide and 52 s tall."""
    k = s
    out = [f'<defs>{blur_filter(uid + "ts", 1.4)}</defs>']
    # the long shadow of the whole thing, to the lower right
    out.append(f'<polygon points="{pts([(x - 6 * k, y + 1 * k), (x + 6 * k, y + 1 * k), (x + 38 * k, y + 24 * k), (x + 30 * k, y + 29 * k), (x + 12 * k, y + 20 * k)])}" fill="{SHADOW}" opacity="0.26" filter="url(#{uid}ts)"/>')
    out.append(block(x - 9 * k, y + 2 * k, 18 * k, 8 * k, 10 * k, "#E9DFC9", uid=uid + "b", shadow=False))                       # the base
    out.append(block(x - 4.2 * k, y - 5 * k, 8.4 * k, 6 * k, 30 * k, "#F3EEE2", roof="#FFFFFF", uid=uid + "s", shadow=False))      # the shaft
    out.append(block(x - 9.5 * k, y - 35 * k, 19 * k, 12 * k, 9 * k, "#F6F2E8", roof="#C9D3E0", uid=uid + "c", shadow=False, window="#27415F"))   # the cab
    # roof overhang and the mast
    top = y - 44 * k
    roof = [(x - 11 * k, top + 0.8 * k), (x + 11 * k, top + 0.8 * k), (x + 11 * k + 7 * k, top - 4 * k + 0.8 * k), (x - 11 * k + 7 * k, top - 4 * k + 0.8 * k)]
    out.append(f'<polygon points="{pts(roof)}" fill="#8D97A6"/><polygon points="{pts([(x - 11 * k, top + 0.8 * k), (x + 11 * k, top + 0.8 * k), (x + 11 * k, top + 2.6 * k), (x - 11 * k, top + 2.6 * k)])}" fill="#5E6879"/>')
    out.append(f'<line x1="{n(x + 3 * k)}" y1="{n(top - 1 * k)}" x2="{n(x + 3 * k)}" y2="{n(top - 12 * k)}" stroke="#4B5565" stroke-width="{n(0.9 * k)}" stroke-linecap="round"/>'
               f'<line x1="{n(x - 3 * k)}" y1="{n(top - 1 * k)}" x2="{n(x - 3 * k)}" y2="{n(top - 7 * k)}" stroke="#4B5565" stroke-width="{n(0.7 * k)}" stroke-linecap="round"/>')
    out.append(f'<defs>{lamp_defs(uid + "l")}</defs>' + lamp(uid + "l", x + 3 * k, top - 12.5 * k, 1.0 * k, "red", 3.0))
    return "".join(out)


def tank(uid, x, y, r=7.0):
    """A fuel tank seen from above and a little to one side: a pale roof with a lit rim, the cylinder under it and its shadow."""
    wall = r * 0.9
    return (f'<defs>{blur_filter(uid + "k", 1.2)}<linearGradient id="{uid}w" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D7DCE2"/><stop offset="0.45" stop-color="#F6F8FA"/><stop offset="1" stop-color="#9AA3B0"/></linearGradient>'
            f'<radialGradient id="{uid}r" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.7" stop-color="#E3E8EE"/><stop offset="1" stop-color="#B7C0CC"/></radialGradient></defs>'
            f'<ellipse cx="{n(x + r * 1.1)}" cy="{n(y + wall * 0.7)}" rx="{n(r * 1.25)}" ry="{n(r * 0.7)}" fill="{SHADOW}" opacity="0.32" filter="url(#{uid}k)"/>'
            f'<path d="M {n(x - r)},{n(y)} L {n(x - r)},{n(y + wall)} A {n(r)},{n(r * 0.55)} 0 0 0 {n(x + r)},{n(y + wall)} L {n(x + r)},{n(y)} Z" fill="url(#{uid}w)"/>'
            f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r)}" ry="{n(r * 0.55)}" fill="url(#{uid}r)" stroke="#8D97A6" stroke-width="0.4"/>'
            f'<ellipse cx="{n(x - r * 0.15)}" cy="{n(y - r * 0.08)}" rx="{n(r * 0.32)}" ry="{n(r * 0.17)}" fill="#C4CCD6" opacity="0.75"/>')


# ------------------------------------------------------------------------------------------------------------------ windsocks
SOCK_ORANGE = ("#FFB877", "#F0782B", "#B04A0F")
SOCK_WHITE = ("#FFFFFF", "#EEF1F6", "#A9B4C6")


def windsock(uid, px, py, length=34.0, angle=0.0, mouth=7.0, segments=4, droop=0.12, pole=34.0, base=True, shadow=True, flutter=0.0, taper=0.6, wobble=0.0, seed=1):
    """A windsock on a pole whose foot is on (px, py): the pole is `pole` tall and the sock hangs from a ring on its top, a sleeve of `segments` bands, orange and white, pointing at
    `angle` degrees from straight down towards the right (0 hangs, 90 streams out to the right). The cloth is shaded across the sleeve (lit on the upper left, dark on the lower
    right), with a seam between the bands, a few creases along it and a light along its upper edge; `mouth` is the width of the ring and the sleeve narrows to (1 - taper) of it;
    `droop` bends a sock that streams out down at its far end, `wobble` makes the sleeve of a slack sock uneven and `flutter` waves it. Returns markup."""
    rnd = random.Random(seed)
    out = []
    tx, ty = px, py - pole
    a = math.radians(angle)
    dirx, diry = math.sin(a), math.cos(a)
    if shadow:
        sh = [(px - 0.8, py), (px + 0.8, py), (px + 0.8 + pole * 0.34, py + pole * 0.20), (px - 0.8 + pole * 0.34, py + pole * 0.20)]
        out.append(f'<defs>{blur_filter(uid + "sk", 1.0)}</defs><polygon points="{pts(sh)}" fill="{SHADOW}" opacity="0.30" filter="url(#{uid}sk)"/>')
    if base:
        out.append(f'<ellipse cx="{n(px)}" cy="{n(py + 0.5)}" rx="{n(3.6)}" ry="1.5" fill="#CFD2D6"/><ellipse cx="{n(px)}" cy="{n(py + 0.1)}" rx="2.6" ry="1.0" fill="#8D9299"/>')
    out.append(f'<defs><linearGradient id="{uid}pl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F3F5F8"/><stop offset="0.5" stop-color="#B8BFCA"/><stop offset="1" stop-color="#6F7886"/></linearGradient></defs>'
               f'<polygon points="{pts([(px - 1.2, py), (px + 1.2, py), (tx + 0.8, ty), (tx - 0.8, ty)])}" fill="url(#{uid}pl)"/>')
    # the centre line of the sock, from the ring along `angle`, bending down towards the far end
    steps = 48
    centre = []
    for i in range(steps + 1):
        t = i / steps
        x = tx + length * dirx * t
        y = ty + length * diry * t + length * droop * (t ** 2) * (math.sin(a) ** 2) + flutter * math.sin(t * 9) * 1.2
        if wobble:
            x += wobble * length * 0.09 * math.sin(t * 6.0 + 1.3) * t
        centre.append((x, y))
    left, right = [], []
    for i, (x, y) in enumerate(centre):
        j0, j1 = max(0, i - 1), min(steps, i + 1)
        dx, dy = centre[j1][0] - centre[j0][0], centre[j1][1] - centre[j0][1]
        nn = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / nn, dx / nn
        t = i / steps
        r = mouth * 0.5 * (1.0 - taper * t) * (1.0 + (wobble * 0.22 * math.sin(t * 9 + 0.7) if wobble else 0.0))
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    # the side that faces the light (upper left) is the lit one
    mid = steps // 2
    nx_m, ny_m = left[mid][0] - centre[mid][0], left[mid][1] - centre[mid][1]
    lit_left = (nx_m + ny_m) < 0
    lit, dark = (left, right) if lit_left else (right, left)
    per = steps // segments
    for s_ in range(segments):
        a0, a1 = s_ * per, (s_ + 1) * per if s_ < segments - 1 else steps
        stops = SOCK_ORANGE if s_ % 2 == 0 else SOCK_WHITE
        m = (a0 + a1) // 2
        gx0, gy0 = lit[m]
        gx1, gy1 = dark[m]
        out.append(f'<defs><linearGradient id="{uid}g{s_}" gradientUnits="userSpaceOnUse" x1="{n(gx0)}" y1="{n(gy0)}" x2="{n(gx1)}" y2="{n(gy1)}">'
                   f'<stop offset="0" stop-color="{stops[0]}"/><stop offset="0.42" stop-color="{stops[1]}"/><stop offset="1" stop-color="{stops[2]}"/></linearGradient></defs>')
        poly = lit[a0:a1 + 1] + dark[a0:a1 + 1][::-1]
        out.append(f'<polygon points="{pts(poly)}" fill="url(#{uid}g{s_})" stroke="#3B2A1C" stroke-opacity="0.45" stroke-width="0.3" stroke-linejoin="round"/>')
        # a soft seam where the band is sewn to the next
        out.append(f'<polyline points="{pts([lit[a0], dark[a0]])}" fill="none" stroke="#2B1D12" stroke-opacity="0.22" stroke-width="0.7"/>')
    # creases along the cloth and the light along its upper edge
    for f_, op in ((-0.45, 0.10), (0.30, 0.13), (0.62, 0.09)):
        line = [(c[0] + (d[0] - c[0]) * (0.5 + f_ * 0.5), c[1] + (d[1] - c[1]) * (0.5 + f_ * 0.5)) for c, d in zip(centre[4:-3], dark[4:-3])]
        out.append(f'<polyline points="{pts(line)}" fill="none" stroke="#1A1208" stroke-opacity="{op}" stroke-width="0.55" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pts(lit[2:-1])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"/>')
    # the open far end, and the wire ring at the mouth (seen almost edge on) with its swivel on the pole
    ex, ey = centre[-1]
    rend = mouth * 0.5 * (1.0 - taper)
    deg = math.degrees(math.atan2(diry, dirx))
    out.append(f'<ellipse cx="{n(ex)}" cy="{n(ey)}" rx="0.7" ry="{n(rend)}" transform="rotate({n(deg)} {n(ex)} {n(ey)})" fill="#4A2A12" opacity="0.7"/>')
    out.append(f'<ellipse cx="{n(tx)}" cy="{n(ty)}" rx="0.95" ry="{n(mouth * 0.54)}" transform="rotate({n(deg)} {n(tx)} {n(ty)})" fill="#2A303B" stroke="#C7CFDB" stroke-width="0.5"/>')
    out.append(f'<circle cx="{n(tx)}" cy="{n(ty)}" r="1.3" fill="#C9D0DA" stroke="#4B5565" stroke-width="0.4"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ signs
SIGNS = {"location": ("#27303F", "#141A25", "#F4C430"), "mandatory": ("#D8372D", "#A5171B", "#FFFFFF"), "direction": ("#FBD233", "#F0B80F", "#1B2230"), "destination": ("#FBD233", "#F0B80F", "#1B2230")}


def arrow_poly(cx, cy, length, thick, head, direction=1, colour="#1B2230"):
    """A solid arrow (a bar and a triangular head) centred on (cx, cy), pointing right (direction 1) or left (-1)."""
    x0, x1 = cx - direction * length / 2, cx + direction * length / 2
    hx = x1 - direction * head
    p = [(x0, cy - thick / 2), (hx, cy - thick / 2), (hx, cy - head * 0.62), (x1, cy), (hx, cy + head * 0.62), (hx, cy + thick / 2), (x0, cy + thick / 2)]
    return f'<polygon points="{pts(p)}" fill="{colour}"/>'


def sign(uid, x, y, text, w=10.0, h=8.0, post=5.0, kind="location", arrow=0, lit=True, glow=0.0, cap=None, shadow=True):
    """A taxiway sign standing on (x, y) (the middle of its foot): two posts or one, a board of `kind` (location: black with a yellow border and a yellow letter; mandatory: red with
    white; direction and destination: yellow with black) and its text in outlines of Inter Bold; `arrow` -1 or 1 puts an arrow to the left or right of the text (direction), a
    destination sign has its arrow after the text. The board is lit a little (a glow along its upper edge, and, with `glow`, a soft halo round it) and casts a shadow to the lower right."""
    c1, c2, ink = SIGNS[kind]
    cap = cap or h * 0.44
    top = y - post - h
    mid = top + h / 2
    out = [f'<defs>{blur_filter(uid + "b", 0.9 + h * 0.04)}{blur_filter(uid + "gl", 1.0 + h * 0.12)}<linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{shade(c1, 1.12)}"/><stop offset="0.55" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>']
    if shadow:
        reach = (post + h) * (1.0 if shadow is True else float(shadow))
        sh = [(x - w / 2, y), (x + w / 2, y), (x + w / 2 + reach * 0.62 + 1, y + reach * 0.40), (x - w / 2 + reach * 0.62 + 1, y + reach * 0.40)]
        out.append(f'<polygon points="{pts(sh)}" fill="{SHADOW}" opacity="0.28" filter="url(#{uid}b)"/>')
    if glow:
        out.append(f'<rect x="{n(x - w / 2 - 1)}" y="{n(top - 1)}" width="{n(w + 2)}" height="{n(h + 2)}" rx="2" fill="{shade(c1, 1.1)}" opacity="{n(glow)}" filter="url(#{uid}gl)"/>')
    posts = [x - w * 0.22, x + w * 0.22] if w > 12 else [x]
    pw = max(0.7, min(2.6, w * 0.035))
    for px in posts:
        out.append(f'<line x1="{n(px)}" y1="{n(y)}" x2="{n(px)}" y2="{n(top + h)}" stroke="#2B323E" stroke-width="{n(pw)}"/><line x1="{n(px - pw * 0.28)}" y1="{n(y)}" x2="{n(px - pw * 0.28)}" y2="{n(top + h)}" stroke="#9AA4B3" stroke-width="{n(pw * 0.3)}"/>')
    out.append(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(min(1.4, h * 0.05))}" fill="url(#{uid}g)" stroke="#10151F" stroke-width="{n(max(0.5, h * 0.025))}"/>')
    if kind == "location":
        out.append(f'<rect x="{n(x - w / 2 + h * 0.09)}" y="{n(top + h * 0.09)}" width="{n(w - h * 0.18)}" height="{n(h * 0.82)}" fill="none" stroke="{ink}" stroke-width="{n(max(0.45, h * 0.06))}"/>')
    if arrow and kind == "direction":
        out.append(arrow_poly(x + arrow * w * 0.22, mid, w * 0.36, h * 0.2, h * 0.36, arrow, ink))
        out.append(glyph_text(text, x - arrow * w * 0.24, mid, cap, ink, stroke=ink, stroke_width=cap * 0.05))
    elif arrow and kind == "destination":
        out.append(glyph_text(text, x - arrow * w * 0.20, mid, cap, ink, stroke=ink, stroke_width=cap * 0.05, spacing=cap * 0.06))
        out.append(arrow_poly(x + arrow * w * 0.26, mid, w * 0.30, h * 0.2, h * 0.36, arrow, ink))
    else:
        out.append(glyph_text(text, x, mid, cap, ink, stroke=ink, stroke_width=cap * 0.05, spacing=cap * 0.06))
    if lit:
        out.append(f'<rect x="{n(x - w / 2 + 0.4)}" y="{n(top + 0.4)}" width="{n(w - 0.8)}" height="{n(h * 0.28)}" rx="0.5" fill="#FFFFFF" opacity="0.20"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ painted and printed letters
_GLYPHS = {}


def _glyphs():
    if not _GLYPHS:
        import json
        import os
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "glyphs.json"), encoding="utf-8") as f:
            _GLYPHS.update(json.load(f))
    return _GLYPHS


def glyph_text(s, cx, cy, height, fill="#FFFFFF", rotate=0.0, spacing=0.0, stroke=None, stroke_width=0.0, anchor="middle", opacity=None):
    """A string of outlines of Inter Bold (digits, capitals, ° % and a few signs; no font is needed), `height` units tall at the capitals, centred on (cx, cy) and turned by
    `rotate` degrees clockwise about that point. `stroke` and `stroke_width` (canvas units) make the strokes heavier, as a coat of paint is."""
    g = _glyphs()
    k = height / g["cap_height"]
    advances = [(height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s]
    total = sum(advances) - spacing
    cursor = cx - (total / 2 if anchor == "middle" else total if anchor == "end" else 0.0)
    out = []
    edge = f' stroke="{stroke}" stroke-width="{n(stroke_width / k)}" stroke-linejoin="round"' if stroke else ""
    for c, adv in zip(s, advances):
        if c != " ":
            out.append(f'<path d="{g["glyphs"][c]["d"]}" transform="translate({n(cursor)} {n(cy + height / 2)}) scale({k:.5f})" fill="{fill}"{edge}/>')
        cursor += adv
    op = f' opacity="{n(opacity)}"' if opacity is not None else ""
    turn = f' transform="rotate({n(rotate)} {n(cx)} {n(cy)})"' if rotate else ""
    return f'<g{turn}{op}>' + "".join(out) + "</g>"


def grain(uid, x, y, w, h, opacity=0.05, freq=1.0, seed=3):
    """A veil of fine grain over a rectangle (a sky, a glow): it breaks the bands that a smooth gradient shows in 8 bits and keeps the picture from looking sprayed."""
    return (f'<defs><filter id="{uid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="{n(freq)}" numOctaves="1" seed="{seed}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="1.6 0 0 0 -0.3  1.6 0 0 0 -0.3  1.6 0 0 0 -0.3  0 0 0 0 1"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" filter="url(#{uid})" opacity="{n(opacity)}"/>')
