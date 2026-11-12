"""Shared parts for the drawings of the aircraft's systems (figs/f_08_02, f_09_01, f_09_02, f_09_03, f_10_02): the gradients they use, tubes with a lit edge, a few valves and fittings.
Plain Python (no Blender, no Pillow). `defs()` returns the gradients and filters; every drawing puts it first among its layers."""
import math

from figs import scene as S

n = S.n


def defs():
    g = S.gradient
    return ("<defs>"
            + g("ptbg", [(0, "#F7FAFD"), (1, "#E1EAF4")])
            + g("ptsteel", [(0, "#8E9BB0"), (0.45, "#EEF2F8"), (1, "#7B8799")], 0, 0, 1, 0) + g("ptsteelv", [(0, "#EEF2F8"), (1, "#8E9BB0")])
            + g("ptbrass", [(0, "#B98A2E"), (0.45, "#F6DC8A"), (1, "#A37820")], 0, 0, 1, 0)
            + g("ptblack", [(0, "#3A4458"), (1, "#151B28")]) + g("ptgrey", [(0, "#A3ADBC"), (0.5, "#E6EAF0"), (1, "#8A95A6")], 0, 0, 1, 0)
            + g("ptblue", [(0, "#7FB1F2"), (0.5, "#3F78D0"), (1, "#244E96")]) + g("ptblueh", [(0, "#2A56A0"), (0.4, "#6FA3EA"), (1, "#2A56A0")], 0, 0, 1, 0)
            + g("ptred", [(0, "#EE5A4F"), (1, "#B5251E")]) + g("ptface", [(0, "#FFFFFF"), (1, "#DCE3EC")])
            + g("ptorange", [(0, "#FFC568"), (0.5, "#F29A2E"), (1, "#C96A10")], 0, 0, 1, 0) + g("ptcast", [(0, "#C95F12"), (0.45, "#F0A33B"), (1, "#C95F12")], 0, 0, 1, 0)
            + g("ptfuel", [(0, "#F7C45F", 0.95), (1, "#D98A1E", 0.95)]) + g("ptcav", [(0, "#12404D"), (1, "#0B2A35")])
            + g("ptpurple", [(0, "#B79BEF"), (0.5, "#7C57D6"), (1, "#4B2FA0")], 0, 0, 1, 0)
            + f'<radialGradient id="ptball" cx="0.36" cy="0.32" r="0.75"><stop offset="0" stop-color="#FFFDF0"/><stop offset="0.6" stop-color="#F2E3B0"/><stop offset="1" stop-color="#C9B06A"/></radialGradient>'
            + f'<filter id="ptsh" x="-20%" y="-20%" width="145%" height="150%"><feDropShadow dx="1.5" dy="3" stdDeviation="2.6" flood-color="#1B2B44" flood-opacity="0.28"/></filter>'
            + f'<filter id="ptblur"><feGaussianBlur stdDeviation="2.2"/></filter>'
            + "</defs>")


def tube(points, base, edge, light, w=7.0, shadow=True):
    """A pipe or a hose through the points: a dark edge, the colour, a bright line along its upper side (as a lit tube), with a soft shadow."""
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points)
    sh = f'<path d="{d}" fill="none" stroke="#1B2B44" stroke-opacity="0.18" stroke-width="{n(w + 1)}" stroke-linejoin="round" stroke-linecap="round" transform="translate(1.5 3)"/>' if shadow else ""
    return (sh + f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{n(w + 1.8)}" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{base}" stroke-width="{n(w)}" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{light}" stroke-width="{n(w * 0.26)}" stroke-opacity="0.85" stroke-linejoin="round" stroke-linecap="round" transform="translate({n(-w * 0.16)} {n(-w * 0.16)})"/>')


def chevrons(points, colour="#FFFFFF", every=34.0, size=3.6, opacity=0.9):
    """Small arrowheads along a path, to show which way the stuff in a tube flows."""
    out, carry = [], every / 2
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        if length == 0:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        pos = carry
        while pos < length:
            cx, cy = x0 + ux * pos, y0 + uy * pos
            out.append(f'<path d="M {n(cx - ux * size - uy * size)},{n(cy - uy * size + ux * size)} L {n(cx + ux * size)},{n(cy + uy * size)} L {n(cx - ux * size + uy * size)},{n(cy - uy * size - ux * size)}" '
                       f'fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')
            pos += every
        carry = pos - length
    return "".join(out)


def hex_nut(cx, cy, r=5.2):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return f'<polygon points="{S.pts(pts)}" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.8"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 0.42)}" fill="#7A5614" opacity="0.45"/>'


def dial_vector(cx, cy, r, needle_deg=40, arc=None, plus_minus=False):
    """A small round gauge drawn in vectors: a black bezel, a white face, ticks, a needle and, if given, a coloured arc."""
    ticks = "".join(f'<line x1="{n(cx + (r - 6.5) * math.sin(math.radians(a)))}" y1="{n(cy - (r - 6.5) * math.cos(math.radians(a)))}" x2="{n(cx + (r - 4.2) * math.sin(math.radians(a)))}" y2="{n(cy - (r - 4.2) * math.cos(math.radians(a)))}" stroke="#374151" stroke-width="1.1"/>' for a in range(-120, 121, 30))
    arc_svg = ""
    if arc:
        a0, a1, col = arc
        x0, y0 = cx + (r - 8) * math.sin(math.radians(a0)), cy - (r - 8) * math.cos(math.radians(a0))
        x1, y1 = cx + (r - 8) * math.sin(math.radians(a1)), cy - (r - 8) * math.cos(math.radians(a1))
        arc_svg = f'<path d="M {n(x0)},{n(y0)} A {n(r - 8)},{n(r - 8)} 0 0 1 {n(x1)},{n(y1)}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>'
    ang = math.radians(needle_deg)
    return (f'<g filter="url(#ptsh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#ptblack)" stroke="#0E1422" stroke-width="1"/></g><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 3.2)}" fill="url(#ptface)"/>'
            + ticks + arc_svg + f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + (r - 7) * math.sin(ang))}" y2="{n(cy - (r - 7) * math.cos(ang))}" stroke="#D6342C" stroke-width="1.8" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy)}" r="2.4" fill="#374151"/>'
            f'<path d="M {n(cx - r + 5)},{n(cy - 5)} A {n(r - 4)},{n(r - 4)} 0 0 1 {n(cx + 1)},{n(cy - r + 4)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="1.2" stroke-linecap="round"/>')
