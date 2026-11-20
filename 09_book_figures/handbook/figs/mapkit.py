"""Pieces of the route maps drawn on an aerial view of the country (Figures 20-7 and 29-9; Figure 29-1 has its own copies): what a feature looks like from above,
with the chart's mark over it where the chart has one.

    frame(w, h, box)           white over what of the picture lies outside the rounded panel, and its white edge (sprites cannot be clipped)
    aerodrome(cx, cy, ang)     a small runway seen from above inside the chart's blue ring
    wadi(d)                    a pale channel with scrub along it and the chart's dashed blue line
    road(d)                    a grey road with its shadow and a dashed centre line
    town(cx, cy, seed)         a cluster of flat-roofed houses with shadows
    dunes(poly, seed)          a dune field: a sand-coloured patch with crest lines
    salt_flat(cx, cy, rx, ry)  a white crust with a soft edge
    restricted(points)         the chart's red border with its inner tick band
    leg(points)                a course line: a dark ribbon with a white casing
    ticks(p0, p1, every)       ticks across a leg
    ring(x, y)                 a checkpoint's orange ring
"""
import math
import random

from figs import h_a4 as A
from figs import scene as S

n = S.n
INK, ORANGE, BLUE, RED = "#1F2937", "#B45309", "#1D4ED8", "#B91C1C"


def frame(w, h, box=(8.0, 8.0, None, None), r=9.0):
    x0, y0 = box[0], box[1]
    x1, y1 = (box[2] if box[2] else w - x0), (box[3] if box[3] else h - y0)
    k = 0.5523 * r
    m = (f'<rect x="0" y="0" width="{w}" height="{n(y0)}" fill="#ffffff"/><rect x="0" y="{n(y1)}" width="{w}" height="{n(h - y1)}" fill="#ffffff"/>'
         f'<rect x="0" y="0" width="{n(x0)}" height="{h}" fill="#ffffff"/><rect x="{n(x1)}" y="0" width="{n(w - x1)}" height="{h}" fill="#ffffff"/>')
    for d in (f"M{n(x0)} {n(y0)} L{n(x0 + r)} {n(y0)} C{n(x0 + r - k)} {n(y0)} {n(x0)} {n(y0 + r - k)} {n(x0)} {n(y0 + r)} Z",
              f"M{n(x1)} {n(y0)} L{n(x1)} {n(y0 + r)} C{n(x1)} {n(y0 + r - k)} {n(x1 - r + k)} {n(y0)} {n(x1 - r)} {n(y0)} Z",
              f"M{n(x0)} {n(y1)} L{n(x0)} {n(y1 - r)} C{n(x0)} {n(y1 - r + k)} {n(x0 + r - k)} {n(y1)} {n(x0 + r)} {n(y1)} Z",
              f"M{n(x1)} {n(y1)} L{n(x1 - r)} {n(y1)} C{n(x1 - r + k)} {n(y1)} {n(x1)} {n(y1 - r + k)} {n(x1)} {n(y1 - r)} Z"):
        m += f'<path d="{d}" fill="#ffffff"/>'
    return m + f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="{n(r)}" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'


def aerodrome(cx, cy, ang, ring=BLUE, r=10.0):
    return (f'<g transform="rotate({n(ang)} {n(cx)} {n(cy)})"><rect x="{n(cx - 14 + 1.5)}" y="{n(cy - 2.2 + 2)}" width="28" height="4.4" fill="#2C2216" opacity="0.3"/>'
            f'<rect x="{n(cx - 14)}" y="{n(cy - 2.2)}" width="28" height="4.4" rx="0.8" fill="#4B5563" stroke="#E5E7EB" stroke-width="0.6"/>'
            f'<line x1="{n(cx - 10)}" y1="{n(cy)}" x2="{n(cx + 10)}" y2="{n(cy)}" stroke="#FFFFFF" stroke-width="0.6" stroke-dasharray="2 2"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="#FFFFFF" stroke-width="4.2" stroke-opacity="0.85"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{ring}" stroke-width="2.2"/>')


def wadi(d):
    return (f'<path d="{d}" fill="none" stroke="#F3E6C6" stroke-opacity="0.85" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#7F8F55" stroke-opacity="0.55" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 6"/>'
            f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="5 3"/>')


def road(d):
    return (f'<path d="{d}" fill="none" stroke="#2C2216" stroke-opacity="0.25" stroke-width="7.5"/>'
            f'<path d="{d}" fill="none" stroke="#6B7280" stroke-width="5.2"/><path d="{d}" fill="none" stroke="#F8FAFC" stroke-width="0.9" stroke-dasharray="4 4"/>')


def town(cx, cy, seed=1, count=14, spread=12.0):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x, y = cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread * 0.8, spread * 0.8)
        w, h = rng.uniform(4, 7.5), rng.uniform(4, 7)
        out.append(f'<rect x="{n(x - w / 2 + 1.5)}" y="{n(y - h / 2 + 2)}" width="{n(w)}" height="{n(h)}" fill="#2C2216" opacity="0.32"/>'
                   f'<rect x="{n(x - w / 2)}" y="{n(y - h / 2)}" width="{n(w)}" height="{n(h)}" fill="#F1E7D3" stroke="#9C8A6A" stroke-width="0.6"/>')
    return "".join(out)


def dunes(poly, seed=1, uid="dn"):
    """A dune field: a warmer sand patch with a soft edge and rows of crest lines, each lit on one side and shaded on the other."""
    rng = random.Random(seed)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    out = [f'<defs><clipPath id="{uid}c"><polygon points="{S.pts(poly)}"/></clipPath><filter id="{uid}b"><feGaussianBlur stdDeviation="3"/></filter></defs>',
           f'<polygon points="{S.pts(poly)}" fill="#E7C98F" opacity="0.75" filter="url(#{uid}b)"/>',
           f'<g clip-path="url(#{uid}c)">']
    y = min(ys) + 4
    while y < max(ys):
        x = min(xs) - 10
        d, ds = f"M {n(x)} {n(y)}", ""
        while x < max(xs) + 10:
            x2 = x + rng.uniform(10, 18)
            d += f" Q {n((x + x2) / 2)} {n(y - rng.uniform(3, 6))} {n(x2)} {n(y)}"
            x = x2
        out.append(f'<path d="{d}" fill="none" stroke="#B88A4A" stroke-opacity="0.7" stroke-width="1.6" transform="translate(0 1.2)"/>'
                   f'<path d="{d}" fill="none" stroke="#FFF3D6" stroke-opacity="0.85" stroke-width="1.1"/>')
        y += rng.uniform(7, 10)
    out.append('</g>')
    return "".join(out)


def salt_flat(cx, cy, rx, ry, uid="sf"):
    return (f'<defs><radialGradient id="{uid}"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.7" stop-color="#F4F1EA" stop-opacity="0.85"/>'
            f'<stop offset="1" stop-color="#F4F1EA" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="url(#{uid})"/>')


def restricted(points):
    inner = []
    cx, cy = sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)
    for x, y in points:
        inner.append((x + (cx - x) * 0.06, y + (cy - y) * 0.06))
    return (f'<polygon points="{S.pts(points)}" fill="{RED}" fill-opacity="0.08" stroke="#FFFFFF" stroke-width="4" stroke-opacity="0.7"/>'
            f'<polygon points="{S.pts(points)}" fill="none" stroke="{RED}" stroke-width="1.8"/>'
            f'<polygon points="{S.pts(inner)}" fill="none" stroke="{RED}" stroke-width="7" stroke-dasharray="1.6 4.5" stroke-opacity="0.8"/>')


def leg(points, uid, colours=("#1B2433", "#475569"), width=3.6):
    return A.ribbon(uid, points, width=width, colours=colours, arrow=False, casing=1.8, per=4)


def ticks(p0, p1, every, half=5.0, start=None):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    out, t = [], (start if start is not None else every)
    while t < L - 1:
        x, y = x0 + ux * t, y0 + uy * t
        a, b = (x - uy * half, y + ux * half), (x + uy * half, y - ux * half)
        out.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>'
                   f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
        t += every
    return "".join(out)


def ring(x, y, colour=ORANGE, r=6.5):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.9"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="{colour}" stroke-width="2.8"/>')


def north(x, y0, y1):
    return (f'<path d="M{n(x)} {n(y1)} V{n(y0 + 10)}" stroke="#FFFFFF" stroke-width="4.4" stroke-linecap="round"/><path d="M{n(x)} {n(y1)} V{n(y0 + 10)}" stroke="{INK}" stroke-width="2"/>'
            f'<polygon points="{n(x)},{n(y0)} {n(x + 6.5)},{n(y0 + 14)} {n(x - 6.5)},{n(y0 + 14)}" fill="{INK}" stroke="#FFFFFF" stroke-width="1"/>')


def scale(x0, y, seg, count):
    out = [f'<rect x="{n(x0 - 2)}" y="{n(y - 3)}" width="{n(seg * count + 4)}" height="12" rx="3" fill="#FFFFFF" opacity="0.85"/>']
    for i in range(count):
        out.append(f'<rect x="{n(x0 + seg * i)}" y="{n(y)}" width="{n(seg)}" height="6" fill="{INK if i % 2 == 0 else "#FFFFFF"}" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)
