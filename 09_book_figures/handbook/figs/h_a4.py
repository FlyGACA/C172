"""Helpers of worker a4 (maps, navigation geometry, radio and radar figures): plain Python that returns SVG markup, to be joined in the "layers" of a blank re-skin
(reskin.py) with figs/scene.py. Every gradient and filter id is made from the `uid` the caller passes, so that two pieces of one drawing never share one.

    ribbon     a flat-lying course or flow: a ribbon with a white casing, a lit edge and a soft shadow (scene.ribbon with a casing and a uniform width)
    beam       a thin wedge of light from a point (the radials of a VOR), with a soft glow
    bezel      a compass ring with ticks and numerals
    vor_top    a VOR station seen from above: a hexagonal white building with a dome, a pad and a shadow
    vor_side   the same from the side
    plane      the aeroplane sprite as an overlay dict (shadow, outline)
    glass      a dark instrument card (a rounded panel with a lit upper edge and a shadow)
"""
import math

from figs import scene as S

n = S.n
pts = S.pts

INK = "#1F2937"
NAVY = "#16233D"
BLUE = ("#1B4FD0", "#6FA3F5")
AMBER = ("#D8701A", "#F7BE66")
GREEN = ("#0B8A66", "#4FD3A0")
RED = ("#C4282B", "#F47D74")
GREY = ("#566377", "#A8B3C4")


def unit(a_deg):
    """The unit vector of a bearing (degrees clockwise from straight up) on the page."""
    a = math.radians(a_deg)
    return math.sin(a), -math.cos(a)


def polar(cx, cy, r, a_deg):
    ux, uy = unit(a_deg)
    return cx + r * ux, cy + r * uy


# ------------------------------------------------------------------------------------------------------------------ aeroplane
def plane(x, y, width, angle=0.0, name="sprite-top", shadow=True, tint=None, opacity=None, flip=False, dark=False):
    """A sprite overlay (dict) for the layers: the aeroplane of the twin with a soft shadow and a thin dark outline."""
    o = {"name": name, "at": [x, y], "width": width, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}}
    if shadow:
        o["shadow"] = {"dx": 3.0, "dy": 4.4, "blur": 2.6, "opacity": 0.34} if name == "sprite-top" else {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
    if angle:
        o["angle"] = angle
    if tint:
        o["tint"] = tint
        o["tint_strength"] = 0.55
    if opacity is not None:
        o["opacity"] = opacity
    if flip:
        o["flip"] = True
    return o


# ------------------------------------------------------------------------------------------------------------------ ribbons and beams
def _outline(curve, width, head, tail, uniform):
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
        grow = 1.0 if uniform else tail + (1 - tail) * min(1.0, s / max(1.0, total * 0.35))
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
    return left + [(x + nx * wing, y + ny * wing), tip, (x - nx * wing, y - ny * wing)] + right[::-1], left, curve


def ribbon(uid, points, width=6.0, colours=BLUE, head=2.0, tail=1.0, uniform=True, casing=2.0, casing_opacity=0.82, shadow=True, opacity=0.97, per=14, arrow=True, glow=None):
    """A course or a flow lying on the ground: a ribbon along a smooth curve through `points`, shaded along its length, lit along one edge, with a white casing
    (`casing` units wide all round) and a soft shadow; `arrow` False leaves the end square. `glow` (a colour) puts a soft halo of light round it."""
    curve = S.catmull(points, per) if len(points) > 2 else [(points[0][0] + (points[1][0] - points[0][0]) * k / 24.0, points[0][1] + (points[1][1] - points[0][1]) * k / 24.0) for k in range(25)]
    if arrow:
        poly, left, _ = _outline(curve, width, head, tail, uniform)
    else:                                                  # a square end
        left, right = [], []
        for i, (x, y) in enumerate(curve):
            j0, j1 = max(0, i - 1), min(len(curve) - 1, i + 1)
            tx, ty = curve[j1][0] - curve[j0][0], curve[j1][1] - curve[j0][1]
            norm = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / norm, tx / norm
            half = width * 0.5
            left.append((x + nx * half, y + ny * half))
            right.append((x - nx * half, y - ny * half))
        poly = left + right[::-1]
    gid, fid, hid = uid + "g", uid + "s", uid + "h"
    x0, y0 = curve[0]
    tip = curve[-1]
    out = [f'<defs>{S.gradient(gid, [(0, colours[0], 0.78), (0.5, colours[0]), (1, colours[1])], x0, y0, tip[0], tip[1], "userSpaceOnUse")}']
    if shadow:
        out.append(f'<filter id="{fid}" x="-25%" y="-25%" width="150%" height="160%"><feDropShadow dx="1.0" dy="2.6" stdDeviation="1.7" flood-color="#10233F" flood-opacity="0.38"/></filter>')
    if glow:
        out.append(f'<filter id="{hid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.2"/></filter>')
    out.append("</defs>")
    if glow:
        out.append(f'<polygon points="{pts(poly)}" fill="{glow}" stroke="{glow}" stroke-width="{n(casing * 2 + 3)}" stroke-linejoin="round" opacity="0.55" filter="url(#{hid})"/>')
    if casing:
        out.append(f'<polygon points="{pts(poly)}" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="{n(casing * 2)}" stroke-linejoin="round" opacity="{n(casing_opacity)}"' + (f' filter="url(#{fid})"' if shadow else "") + "/>")
    out.append(f'<polygon points="{pts(poly)}" fill="url(#{gid})" opacity="{n(opacity)}" stroke="{colours[0]}" stroke-opacity="0.55" stroke-width="0.5" stroke-linejoin="round"/>')
    hi = [(a[0] * 0.55 + c[0] * 0.45, a[1] * 0.55 + c[1] * 0.45) for a, c in zip(left, curve)]
    out.append(f'<polyline points="{pts(hi[2:])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.42" stroke-width="{n(max(0.6, width * 0.15))}" stroke-linecap="round"/>')
    return "".join(out)


def beam(cx, cy, ang, r0, r1, w0=0.8, w1=2.6, colour="#FFFFFF", a0=0.95, a1=0.3, gid="g"):
    """One thin wedge of light from (cx, cy) at the bearing `ang`, from radius r0 to r1, w0 wide at the start and w1 at the end, fading from a0 to a1 (its gradient id `gid`).
    Returns (the gradient def, the polygon)."""
    ux, uy = unit(ang)
    nx, ny = -uy, ux
    p0 = (cx + ux * r0, cy + uy * r0)
    p1 = (cx + ux * r1, cy + uy * r1)
    poly = [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2), (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]
    d = S.gradient(gid, [(0, colour, a0), (1, colour, a1)], p0[0], p0[1], p1[0], p1[1], "userSpaceOnUse")
    return d, f'<polygon points="{pts(poly)}" fill="url(#{gid})"/>', poly


def rays(uid, cx, cy, angles, r0, r1, w0=0.9, w1=2.8, colour="#FFFFFF", a0=0.95, a1=0.32, glow=5.0, glow_opacity=0.5):
    """A fan of light rays (one beam per bearing) with a soft glow under them."""
    defs, crisp, wide = [], [], []
    for i, a in enumerate(angles):
        d, p, poly = beam(cx, cy, a, r0, r1, w0, w1, colour, a0, a1, f"{uid}r{i}")
        defs.append(d)
        crisp.append(p)
        d2, p2, _ = beam(cx, cy, a, r0, r1, w0 + glow, w1 + glow * 1.6, colour, a0 * glow_opacity, a1 * glow_opacity * 0.6, f"{uid}w{i}")
        defs.append(d2)
        wide.append(p2)
    return (f'<defs>{"".join(defs)}<filter id="{uid}b" filterUnits="userSpaceOnUse" x="{n(cx - r1 - 20)}" y="{n(cy - r1 - 20)}" width="{n(2 * r1 + 40)}" height="{n(2 * r1 + 40)}"><feGaussianBlur stdDeviation="2.2"/></filter></defs>'
            f'<g filter="url(#{uid}b)">{"".join(wide)}</g>' + "".join(crisp))


# ------------------------------------------------------------------------------------------------------------------ compass ring
def bezel(uid, cx, cy, r_in, r_out, labels, bold=(), step=10, major=30, fill="#15233E", opacity=0.82, numeral="#FFFFFF", size=10.5, tick="#FFFFFF"):
    """A compass ring: a dark glass band between r_in and r_out with ticks along its inner edge every `step` degrees (longer every `major`) and the numerals of `labels`
    ({bearing: text}) in the middle of the band, upright; `bold` is the set of bearings drawn heavier and in a warm white."""
    ring = (f'M {n(cx - r_out)},{n(cy)} A {n(r_out)},{n(r_out)} 0 1 1 {n(cx + r_out)},{n(cy)} A {n(r_out)},{n(r_out)} 0 1 1 {n(cx - r_out)},{n(cy)} Z '
            f'M {n(cx - r_in)},{n(cy)} A {n(r_in)},{n(r_in)} 0 1 0 {n(cx + r_in)},{n(cy)} A {n(r_in)},{n(r_in)} 0 1 0 {n(cx - r_in)},{n(cy)} Z')
    out = [f'<defs><filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0.6" dy="2.4" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.38"/></filter>'
           f'{S.gradient(uid + "g", [(0, "#243656"), (1, "#101B31")], cx - r_out, cy - r_out, cx + r_out, cy + r_out, "userSpaceOnUse")}</defs>',
           f'<path d="{ring}" fill-rule="evenodd" fill="url(#{uid}g)" opacity="{n(opacity)}" filter="url(#{uid}s)"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r_out)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.9"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r_in)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="1.0"/>']
    for a in range(0, 360, step):
        is_major = a % major == 0
        x0, y0 = polar(cx, cy, r_in, a)
        x1, y1 = polar(cx, cy, r_in + (7.5 if is_major else 4.2), a)
        out.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{tick}" stroke-opacity="{0.95 if is_major else 0.62}" stroke-width="{1.5 if is_major else 0.8}" stroke-linecap="butt"/>')
    rm = r_in + (r_out - r_in) * 0.64 + 3.4
    for a, txt in labels.items():
        x, y = polar(cx, cy, rm, a)
        heavy = a in bold
        out.append(f'<text x="{n(x)}" y="{n(y + size * 0.36)}" font-family="sans-serif" font-size="{n(size)}" font-weight="{"bold" if heavy else "normal"}" fill="{"#FFE9A8" if heavy else numeral}" text-anchor="middle">{txt}</text>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the station
def vor_top(uid, cx, cy, k=1.0, pad=True, shed=True):
    """A VOR/DME station seen from above: a square concrete pad, a hexagonal white building (a flat roof with a parapet) with a dome in the middle, a small equipment shed for
    the DME, and the long soft shadows the sun from the upper left throws. `k` is the scale (the hexagon's circumradius is 12 k)."""
    R = 12.0 * k
    hexa = lambda r, ox=0.0, oy=0.0: [(cx + ox + r * math.cos(math.radians(a)), cy + oy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    out = [f'<defs><filter id="{uid}b" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="{n(1.7 * k)}"/></filter>'
           f'{S.gradient(uid + "w", [(0, "#FFFFFF"), (1, "#D5DCE8")], cx - R, cy - R, cx + R, cy + R, "userSpaceOnUse")}'
           f'{S.gradient(uid + "r", [(0, "#F9FBFE"), (1, "#C7D0DE")], cx - R, cy - R, cx + R, cy + R, "userSpaceOnUse")}'
           f'<radialGradient id="{uid}d" cx="0.34" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#E2E8F2"/><stop offset="1" stop-color="#8E9CB6"/></radialGradient>'
           f'{S.gradient(uid + "p", [(0, "#EFE8D6"), (1, "#D8CFB6")], cx - 26 * k, cy - 26 * k, cx + 26 * k, cy + 26 * k, "userSpaceOnUse")}</defs>']
    if pad:
        half = 24.0 * k
        out.append(f'<rect x="{n(cx - half + 3 * k)}" y="{n(cy - half + 4 * k)}" width="{n(2 * half)}" height="{n(2 * half)}" rx="{n(2.5 * k)}" fill="#3A2E1E" opacity="0.30" filter="url(#{uid}b)"/>')
        out.append(f'<rect x="{n(cx - half)}" y="{n(cy - half)}" width="{n(2 * half)}" height="{n(2 * half)}" rx="{n(2.5 * k)}" fill="url(#{uid}p)" stroke="#B9AE92" stroke-width="{n(0.9 * k)}"/>')
        out.append(f'<rect x="{n(cx - half + 3.0 * k)}" y="{n(cy - half + 3.0 * k)}" width="{n(2 * half - 6.0 * k)}" height="{n(2 * half - 6.0 * k)}" fill="none" stroke="#6E6350" stroke-opacity="0.75" stroke-width="{n(0.55 * k)}" stroke-dasharray="{n(1.1 * k)} {n(1.5 * k)}"/>')
    # shadow of the building: the hexagon pushed down and to the right, and a longer, fainter one from the dome
    out.append(f'<polygon points="{pts(hexa(R, 4.2 * k, 5.2 * k))}" fill="#2C2216" opacity="0.38" filter="url(#{uid}b)"/>')
    if shed:
        sx, sy = cx + 13.5 * k, cy + 13.5 * k
        out.append(f'<rect x="{n(sx - 3 * k + 2 * k)}" y="{n(sy - 2.4 * k + 2.4 * k)}" width="{n(10 * k)}" height="{n(6.6 * k)}" fill="#2C2216" opacity="0.34" filter="url(#{uid}b)"/>'
                   f'<rect x="{n(sx - 3 * k)}" y="{n(sy - 2.4 * k)}" width="{n(10 * k)}" height="{n(6.6 * k)}" rx="{n(0.8 * k)}" fill="url(#{uid}r)" stroke="#A9B4C6" stroke-width="{n(0.6 * k)}"/>'
                   f'<rect x="{n(sx - 1.8 * k)}" y="{n(sy - 1.2 * k)}" width="{n(7.6 * k)}" height="{n(4.2 * k)}" fill="none" stroke="#B5C0D2" stroke-width="{n(0.5 * k)}"/>')
    out.append(f'<polygon points="{pts(hexa(R))}" fill="url(#{uid}w)" stroke="#9AA6BA" stroke-width="{n(1.0 * k)}" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts(hexa(R * 0.84))}" fill="url(#{uid}r)" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="{n(0.7 * k)}" stroke-linejoin="round"/>')
    # a faint rim light on the upper left edges, a darker lower right edge
    h = hexa(R)
    out.append(f'<polyline points="{pts([h[3], h[4], h[5]])}" fill="none" stroke="#FFFFFF" stroke-width="{n(1.1 * k)}" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pts([h[0], h[1], h[2]])}" fill="none" stroke="#6F7C93" stroke-width="{n(0.9 * k)}" stroke-opacity="0.55" stroke-linecap="round" stroke-linejoin="round"/>')
    # the dome: its own small shadow, the sphere, a highlight
    dr = R * 0.5
    out.append(f'<circle cx="{n(cx + 1.8 * k)}" cy="{n(cy + 2.3 * k)}" r="{n(dr)}" fill="#2C2216" opacity="0.30" filter="url(#{uid}b)"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(dr)}" fill="url(#{uid}d)" stroke="#8695AE" stroke-width="{n(0.6 * k)}"/>')
    out.append(f'<ellipse cx="{n(cx - dr * 0.32)}" cy="{n(cy - dr * 0.38)}" rx="{n(dr * 0.28)}" ry="{n(dr * 0.17)}" fill="#FFFFFF" opacity="0.9" transform="rotate(-35 {n(cx - dr * 0.32)} {n(cy - dr * 0.38)})"/>')
    return "".join(out)


def vor_side(uid, x, y, k=1.0, mast=True):
    """A VOR station seen from the side, standing on the ground at (x, y): a hexagonal drum (three faces, lit on the left), a flat roof, a white dome and a short mast.
    Returns (markup, (x, y_top)) with the point where the signal starts."""
    w, h = 22.0 * k, 12.0 * k
    left, right = x - w / 2, x + w / 2
    out = [f'<defs>{S.gradient(uid + "a", [(0, "#FFFFFF"), (1, "#E4EAF3")], 0, 0, 1, 0)}{S.gradient(uid + "b", [(0, "#EDF1F7"), (1, "#C8D1DF")], 0, 0, 1, 0)}{S.gradient(uid + "c", [(0, "#C2CCDB"), (1, "#8D9AB0")], 0, 0, 1, 0)}'
           f'<radialGradient id="{uid}d" cx="0.34" cy="0.28" r="0.85"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="#E4EAF4"/><stop offset="1" stop-color="#8E9CB6"/></radialGradient>'
           f'<filter id="{uid}s" x="-30%" y="-30%" width="170%" height="160%"><feGaussianBlur stdDeviation="{n(1.4 * k)}"/></filter></defs>']
    out.append(f'<ellipse cx="{n(x + 4 * k)}" cy="{n(y + 0.8 * k)}" rx="{n(w * 0.75)}" ry="{n(2.0 * k)}" fill="#2C2216" opacity="0.30" filter="url(#{uid}s)"/>')
    # three faces: left (lit), middle, right (shade)
    a, b, c = left, x - w * 0.14, x + w * 0.30
    out.append(f'<rect x="{n(a)}" y="{n(y - h)}" width="{n(b - a)}" height="{n(h)}" fill="url(#{uid}a)"/>')
    out.append(f'<rect x="{n(b)}" y="{n(y - h)}" width="{n(c - b)}" height="{n(h)}" fill="url(#{uid}b)"/>')
    out.append(f'<rect x="{n(c)}" y="{n(y - h)}" width="{n(right - c)}" height="{n(h)}" fill="url(#{uid}c)"/>')
    out.append(f'<rect x="{n(left - 0.8 * k)}" y="{n(y - h - 1.6 * k)}" width="{n(w + 1.6 * k)}" height="{n(2.2 * k)}" rx="{n(0.8 * k)}" fill="#F7F9FC" stroke="#9AA6BA" stroke-width="{n(0.5 * k)}"/>')
    # a door and two slit windows
    out.append(f'<rect x="{n(b + 2.2 * k)}" y="{n(y - h * 0.62)}" width="{n(3.4 * k)}" height="{n(h * 0.62)}" fill="#7C8CA6" opacity="0.85"/>')
    out.append(f'<rect x="{n(a + 2.6 * k)}" y="{n(y - h * 0.7)}" width="{n(2.2 * k)}" height="{n(3.2 * k)}" fill="#8EA6C8" opacity="0.9"/>')
    dr = 6.6 * k
    top = y - h - 1.6 * k
    out.append(f'<path d="M {n(x - dr)},{n(top)} A {n(dr)},{n(dr)} 0 0 1 {n(x + dr)},{n(top)} Z" fill="url(#{uid}d)" stroke="#8695AE" stroke-width="{n(0.5 * k)}"/>')
    tip = (x, top - dr)
    if mast:
        out.append(f'<line x1="{n(x)}" y1="{n(top - dr)}" x2="{n(x)}" y2="{n(top - dr - 5 * k)}" stroke="#5B687E" stroke-width="{n(0.9 * k)}" stroke-linecap="round"/>')
        tip = (x, top - dr - 5 * k)
    return "".join(out), tip


# ------------------------------------------------------------------------------------------------------------------ panels
def glass(uid, x, y, w, h, r=8.0, top="#2C3D5E", bottom="#111B31", opacity=0.96, shadow=True):
    """A dark instrument card: a rounded panel with a vertical gradient, a lit upper edge and a soft shadow. Draw the content over it."""
    return (f'<defs>{S.gradient(uid + "g", [(0, top), (1, bottom)])}'
            f'<filter id="{uid}s" x="-12%" y="-12%" width="124%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="3.2" flood-color="#10233F" flood-opacity="0.42"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="url(#{uid}g)" opacity="{n(opacity)}"' + (f' filter="url(#{uid}s)"' if shadow else "") + '/>'
            f'<rect x="{n(x + 0.6)}" y="{n(y + 0.6)}" width="{n(w - 1.2)}" height="{n(h - 1.2)}" rx="{n(r - 0.6)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.30" stroke-width="1"/>'
            f'<path d="M {n(x + r)},{n(y + 1.3)} L {n(x + w - r)},{n(y + 1.3)}" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8" stroke-linecap="round"/>')


def text(x, y, s, size=12, colour="#FFFFFF", weight="bold", anchor="middle", mono=False, halo=None):
    fam = "monospace" if mono else "sans-serif"
    extra = f' stroke="{halo}" stroke-width="3" stroke-opacity="0.85" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return f'<text x="{n(x)}" y="{n(y)}" font-family="{fam}" font-size="{n(size)}" font-weight="{weight}" fill="{colour}" text-anchor="{anchor}"{extra}>{s}</text>'


def arc_path(cx, cy, r, a0, a1):
    """The path data of an arc about (cx, cy) from the bearing a0 to a1 (degrees clockwise from up), the short way round."""
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    sweep = 1 if (a1 - a0) % 360 < 180 else 0
    return f"M {n(x0)},{n(y0)} A {n(r)},{n(r)} 0 0 {sweep} {n(x1)},{n(y1)}"


def cdi(uid, x, y, w, h, dots, spacing=8.0, r=7.0):
    """A course deviation bar in a dark glass card (x, y its top left): five dots each side of a centre ring and the needle (a lit amber bar) `dots` dots to the right of the centre
    (negative: to the left). Returns the markup."""
    cx, cy = x + w / 2, y + h / 2
    out = [glass(uid, x, y, w, h, r=r)]
    for i in range(-5, 6):
        if i == 0:
            out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="3.5" fill="none" stroke="#FFFFFF" stroke-width="1.3" stroke-opacity="0.9"/>')
        else:
            out.append(f'<circle cx="{n(cx + i * spacing)}" cy="{n(cy)}" r="1.8" fill="#B9C6DC" opacity="0.9"/>')
    nx = cx + dots * spacing
    out.append(f'<defs><filter id="{uid}n" x="-200%" y="-30%" width="500%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>{S.gradient(uid + "q", [(0, "#FFC56B"), (1, "#E8761F")], 0, 0, 1, 0)}</defs>'
               f'<rect x="{n(nx - 2.0)}" y="{n(y + 4)}" width="4" height="{n(h - 8)}" rx="2" fill="#FFA43A" opacity="0.8" filter="url(#{uid}n)"/>'
               f'<rect x="{n(nx - 1.7)}" y="{n(y + 4.5)}" width="3.4" height="{n(h - 9)}" rx="1.7" fill="url(#{uid}q)" stroke="#FFF1CF" stroke-opacity="0.7" stroke-width="0.5"/>')
    return "".join(out)


def dotted(points, colour="#FFFFFF", width=1.5, dash="1.6 3.4", casing=True):
    """A thin dotted thread between two points (or along a polyline) with a faint dark edge so that it reads on any ground."""
    d = "M " + " L ".join(f"{n(px)},{n(py)}" for px, py in points)
    out = ""
    if casing:
        out += f'<path d="{d}" fill="none" stroke="#10233F" stroke-opacity="0.35" stroke-width="{n(width + 1.6)}" stroke-dasharray="{dash}" stroke-linecap="round"/>'
    return out + f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(width)}" stroke-dasharray="{dash}" stroke-linecap="round"/>'


def halo_line(x1, y1, x2, y2, colour="#B45309", width=1.8, dash=None, casing=3.6, opacity=0.85):
    """A line with a white casing under it (for something drawn on a picture)."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#FFFFFF" stroke-opacity="{n(opacity)}" stroke-width="{n(width + casing)}" stroke-linecap="round"/>'
            f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{colour}" stroke-width="{n(width)}"{da} stroke-linecap="butt"/>')


def halo_path(d, colour="#B45309", width=1.8, casing=3.6, opacity=0.85, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="{n(opacity)}" stroke-width="{n(width + casing)}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(width)}"{da} stroke-linecap="butt"/>')


def dashed_arrow(points, colour, width=2.2, dash="7 4.5", head=6.0, casing=1.8, start_head=False):
    """A dashed line with an arrowhead at its last point (or its first, `start_head`), a white casing under it (the same dashes, wider) and a soft shadow."""
    d = "M " + " L ".join(f"{n(px)},{n(py)}" for px, py in points)
    (x0, y0), (x1, y1) = points[-2], points[-1]
    if start_head:
        (x1, y1), (x0, y0) = points[0], points[1]
    L = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    bx, by = x1 - ux * head, y1 - uy * head
    tri = [(x1, y1), (bx - uy * head * 0.62, by + ux * head * 0.62), (bx + uy * head * 0.62, by - ux * head * 0.62)]
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="{n(width + casing * 2)}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polygon points="{pts(tri)}" fill="#FFFFFF" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="{n(casing * 2)}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(width)}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polygon points="{pts(tri)}" fill="{colour}"/>')


def planet(uid, x0, x1, apex_y, bottom, radius=1800.0, colours=("#EAD9AE", "#C4A672"), seed=3, haze=True, scrub_count=40):
    """The ground as a piece of a great circle (the curve of the earth): `apex_y` is its highest point (the middle of x0..x1), `radius` its radius, sand shaded
    from the horizon down, a soft haze band over the horizon and a little scrub. Returns (markup, the function x -> y of the horizon)."""
    mid = (x0 + x1) / 2.0

    def gy(x):
        return apex_y + radius - math.sqrt(max(1.0, radius * radius - (x - mid) ** 2))

    edge = gy(x0)
    path = f"M {n(x0)},{n(gy(x0))} A {n(radius)},{n(radius)} 0 0 1 {n(x1)},{n(gy(x1))} L {n(x1)},{n(bottom)} L {n(x0)},{n(bottom)} Z"
    out = [f'<defs>{S.gradient(uid, [(0, colours[0]), (1, colours[1])], 0, apex_y, 0, bottom, "userSpaceOnUse")}'
           f'<filter id="{uid}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="{seed}"/>'
           f'<feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.34  0 0 0 0 0.2  0 0 0 0.5 -0.1"/></filter>'
           f'<clipPath id="{uid}c"><path d="{path}"/></clipPath></defs>',
           f'<path d="{path}" fill="url(#{uid})"/>',
           f'<g clip-path="url(#{uid}c)"><rect x="{n(x0)}" y="{n(apex_y)}" width="{n(x1 - x0)}" height="{n(bottom - apex_y)}" filter="url(#{uid}n)" opacity="0.45"/>'
           f'{S.scrub(seed + 2, x0, x1, apex_y + 14, bottom - 4, scrub_count, scale=0.9)}</g>']
    arc = f"M {n(x0)},{n(gy(x0))} A {n(radius)},{n(radius)} 0 0 1 {n(x1)},{n(gy(x1))}"
    out.append(f'<path d="{arc}" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="1.2"/>')
    if haze:
        out.append(f'<defs>{S.gradient(uid + "z", [(0, "#FFF6DC", 0.0), (1, "#FFF6DC", 0.75)], 0, apex_y - 36, 0, apex_y + 8, "userSpaceOnUse")}</defs>'
                   f'<path d="M {n(x0)},{n(edge)} L {n(x0)},{n(apex_y - 36)} L {n(x1)},{n(apex_y - 36)} L {n(x1)},{n(gy(x1))} A {n(radius)},{n(radius)} 0 0 0 {n(x0)},{n(gy(x0))} Z" fill="url(#{uid}z)"/>')
    return "".join(out), gy


def link(uid, p0, p1, colour, glow, width=1.7, dash=None, glow_width=6.0, opacity=1.0, bounds=(0, 0, 640, 440)):
    """A glowing line: a soft wide halo in `glow`, a thin bright core in `colour` (dashed if asked). `bounds` (x, y, w, h) is the area the blur may spread over."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    bx, by, bw, bh = bounds
    return (f'<defs><filter id="{uid}f" filterUnits="userSpaceOnUse" x="{bx}" y="{by}" width="{bw}" height="{bh}"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
            f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{glow}" stroke-width="{n(glow_width)}" stroke-opacity="{n(0.75 * opacity)}" stroke-linecap="round" filter="url(#{uid}f)"/>'
            f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{colour}" stroke-width="{n(width)}" stroke-opacity="{n(opacity)}" stroke-linecap="round"{da}/>')


def globe(uid, cx, cy, r, glow_colour="#6FB0FF"):
    """A shaded sphere lit from the upper left: an atmosphere glow, a base that goes from a pale day side to a deep night side, a night shadow on the lower right, a rim light
    and a soft highlight. Draw the graticule and the lines over it. Returns the markup."""
    return (f'<defs><radialGradient id="{uid}a" cx="0.5" cy="0.5" r="0.5"><stop offset="0.80" stop-color="{glow_colour}" stop-opacity="0.0"/><stop offset="0.90" stop-color="{glow_colour}" stop-opacity="0.45"/><stop offset="1" stop-color="{glow_colour}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{uid}b" cx="0.36" cy="0.30" r="0.92"><stop offset="0" stop-color="#EAF4FF"/><stop offset="0.22" stop-color="#A9CBF7"/><stop offset="0.5" stop-color="#5A8FDB"/><stop offset="0.8" stop-color="#25458F"/><stop offset="1" stop-color="#0F1E48"/></radialGradient>'
            f'<radialGradient id="{uid}n" cx="0.30" cy="0.26" r="1.05"><stop offset="0.45" stop-color="#050B22" stop-opacity="0"/><stop offset="0.8" stop-color="#050B22" stop-opacity="0.38"/><stop offset="1" stop-color="#050B22" stop-opacity="0.72"/></radialGradient>'
            f'<radialGradient id="{uid}h" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.75"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="{uid}c"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/></clipPath></defs>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 1.16)}" fill="url(#{uid}a)"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{uid}b)"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{uid}n)"/>'
            f'<ellipse cx="{n(cx - r * 0.38)}" cy="{n(cy - r * 0.42)}" rx="{n(r * 0.34)}" ry="{n(r * 0.24)}" fill="url(#{uid}h)" transform="rotate(-38 {n(cx - r * 0.38)} {n(cy - r * 0.42)})"/>')


def glow_line_filter(uid, std=2.4):
    return f'<defs><filter id="{uid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{std}"/></filter></defs>'


def stars(seed, count, x0, y0, x1, y1, rmin=0.3, rmax=0.9):
    import random
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{n(rnd.uniform(x0, x1))}" cy="{n(rnd.uniform(y0, y1))}" r="{n(rnd.uniform(rmin, rmax))}" fill="#FFFFFF" opacity="{n(rnd.uniform(0.25, 0.9))}"/>' for _ in range(count))


def pin(x, y, angle=0.0, k=1.0, colour=("#FF6A5E", "#C4282B")):
    """A map pin standing on (x, y) (its point), leaning `angle` degrees clockwise from straight up: a stalk, a round head with a highlight and a white rim."""
    ux, uy = unit(angle)
    hx, hy = x + ux * 11 * k, y + uy * 11 * k
    nx, ny = -uy, ux
    return (f'<defs><radialGradient id="pn{int(x)}{int(y)}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFC9C2"/><stop offset="0.35" stop-color="{colour[0]}"/><stop offset="1" stop-color="{colour[1]}"/></radialGradient></defs>'
            f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(hx)}" y2="{n(hy)}" stroke="#FFFFFF" stroke-width="{n(2.6 * k + 1.8)}" stroke-linecap="round" stroke-opacity="0.9"/>'
            f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(hx)}" y2="{n(hy)}" stroke="#5A2020" stroke-width="{n(1.5 * k)}" stroke-linecap="round"/>'
            f'<circle cx="{n(hx + ux * 1.5 * k)}" cy="{n(hy + uy * 1.5 * k)}" r="{n(5.4 * k)}" fill="url(#pn{int(x)}{int(y)})" stroke="#FFFFFF" stroke-width="{n(1.3 * k)}"/>'
            f'<circle cx="{n(hx + ux * 1.5 * k - 1.6 * k)}" cy="{n(hy + uy * 1.5 * k - 1.8 * k)}" r="{n(1.5 * k)}" fill="#FFFFFF" opacity="0.85"/>'), (hx, hy)


def vector(uid, p0, p1, width=5.0, colours=BLUE, heads=1, head_len=14.0, head_w=12.0, gap=9.5, casing=1.8, glow=None, dark="#0F172A"):
    """A vector of a triangle (wind, heading, track): a ribbon from p0 to p1 and `heads` arrowheads one behind the other at p1 (one: heading and airspeed, two: track and
    groundspeed, three: the wind). Returns the markup."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    back = (heads - 1) * gap + head_len * 0.7
    end = (x1 - ux * back, y1 - uy * back)
    out = [ribbon(uid, [p0, end], width=width, colours=colours, arrow=False, casing=casing, glow=glow)]
    fid = uid + "hs"
    out.append(f'<defs><filter id="{fid}" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0.8" dy="2.2" stdDeviation="1.5" flood-color="#10233F" flood-opacity="0.38"/></filter></defs><g filter="url(#{fid})">')
    for k in range(heads - 1, -1, -1):
        tx, ty = x1 - ux * k * gap, y1 - uy * k * gap
        bx, by = tx - ux * head_len, ty - uy * head_len
        tri = [(tx, ty), (bx + nx * head_w / 2, by + ny * head_w / 2), (bx - nx * head_w / 2, by - ny * head_w / 2)]
        out.append(f'<polygon points="{pts(tri)}" fill="{colours[0] if heads == 1 else colours[0]}" stroke="#FFFFFF" stroke-width="1.5" stroke-linejoin="round" stroke-opacity="0.9"/>')
    out.append("</g>")
    return "".join(out)


def paper(uid, w, h, origin=(0.0, 0.0), minor=21.0, major=84.0, top="#F6F9FC", bottom="#E3ECF5", line="#B7C8DC"):
    """A chart ground: a pale gradient with a printed grid (a fine line every `minor`, a stronger one every `major`, both passing through `origin`) and a soft vignette."""
    ox, oy = origin
    out = [f'<defs>{S.gradient(uid + "g", [(0, top), (1, bottom)])}<radialGradient id="{uid}v" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#10233F" stop-opacity="0"/><stop offset="1" stop-color="#10233F" stop-opacity="0.16"/></radialGradient></defs>',
           f'<rect x="0" y="0" width="{n(w)}" height="{n(h)}" fill="url(#{uid}g)"/>']
    k = int(-ox // minor) - 1
    x = ox + k * minor
    while x <= w + 1:
        is_major = abs(((x - ox) / major) - round((x - ox) / major)) < 1e-6
        out.append(f'<line x1="{n(x)}" y1="0" x2="{n(x)}" y2="{n(h)}" stroke="{line}" stroke-opacity="{0.9 if is_major else 0.5}" stroke-width="{0.9 if is_major else 0.5}"/>')
        x += minor
    k = int(-oy // minor) - 1
    y = oy + k * minor
    while y <= h + 1:
        is_major = abs(((y - oy) / major) - round((y - oy) / major)) < 1e-6
        out.append(f'<line x1="0" y1="{n(y)}" x2="{n(w)}" y2="{n(y)}" stroke="{line}" stroke-opacity="{0.9 if is_major else 0.5}" stroke-width="{0.9 if is_major else 0.5}"/>')
        y += minor
    out.append(f'<rect x="0" y="0" width="{n(w)}" height="{n(h)}" fill="url(#{uid}v)"/>')
    return "".join(out)


def ruler(uid, x0, y0, length, height, zero, per_unit, ticks, labels, step_minor=None, numeral=10.5):
    """A steel ruler lying on the chart: a brushed-metal strip with a lit upper edge, a soft shadow, engraved ticks and numerals. `zero` is the x of the 0 mark, `per_unit` the
    canvas units to one unit of scale, `ticks` the values with a long tick, `labels` the values that carry a numeral; `step_minor` the value between the short ticks."""
    out = [f'<defs>{S.gradient(uid + "m", [(0, "#F4F7FB"), (0.18, "#E1E8F1"), (0.55, "#C9D3E0"), (1, "#A9B6C8")])}'
           f'<filter id="{uid}s" x="-6%" y="-30%" width="112%" height="190%"><feDropShadow dx="1.2" dy="3" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.38"/></filter></defs>',
           f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(length)}" height="{n(height)}" rx="3" fill="url(#{uid}m)" stroke="#8795AB" stroke-width="0.9" filter="url(#{uid}s)"/>',
           f'<rect x="{n(x0 + 1)}" y="{n(y0 + 1)}" width="{n(length - 2)}" height="1.8" rx="0.9" fill="#FFFFFF" opacity="0.9"/>',
           f'<rect x="{n(x0 + 1)}" y="{n(y0 + height - 2.4)}" width="{n(length - 2)}" height="1.4" rx="0.7" fill="#6F7E95" opacity="0.35"/>']
    for i in range(0, 90):
        pass
    vals = sorted(set(list(ticks) + ([v for v in range(0, 200, step_minor)] if step_minor else [])))
    for v in vals:
        x = zero + v * per_unit
        if x < x0 + 3 or x > x0 + length - 3:
            continue
        long = v in ticks
        out.append(f'<line x1="{n(x)}" y1="{n(y0 + 2.6)}" x2="{n(x)}" y2="{n(y0 + (13 if long else 8))}" stroke="#2A3548" stroke-width="{1.2 if long else 0.8}"/>')
    for v in labels:
        out.append(text(zero + v * per_unit, y0 + height - 6.2, str(v), numeral, "#1F2937", "bold", "middle"))
    return "".join(out)
