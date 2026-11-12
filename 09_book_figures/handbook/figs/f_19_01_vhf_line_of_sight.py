"""Figure 19-1. VHF radio reaches only as far as the line of sight. The earth's curve in section, drawn as a lit segment of a globe: a desert surface shaded from the upper left,
a thin glowing atmosphere along its limb, a ridge of rock on it, a mast for the station; the line of sight and the paths to the three aeroplanes as beams of light (blue for the line,
green where there is contact, red where the bulge or the ridge blocks the path, ending in a cross); the radio shadows as veils of dusk; the model seen from the right (and from the left
for the aeroplane behind the ridge); the heights of the line of sight above the ground as dimension lines with their numbers and the distances as a ruler. Every number and place of the
old figure is kept, with its eight numbered callouts (figs/h_a1.py and figs/scene.py make the pieces)."""
import math

from figs import h_a1 as H
from figs import scene as S

CARD = (4, 6, 632, 362)
K = 0.0011811790                        # the surface: y = 118 + K (x - 200)^2, as in the old figure (the earth's curve, much exaggerated)
X0, X1, BOTTOM = 4, 636, 370


def surface(x):
    return 118.0 + K * (x - 200.0) ** 2


def curve_points(x0=4, x1=636, step=4):
    out, x = [], float(x0)
    while x <= x1 + 0.01:
        out.append((x, round(surface(x), 2)))
        x += step
    return out


CURVE = curve_points()
CURVE_D = "M " + " L ".join(f"{S.n(x)},{S.n(y)}" for x, y in CURVE)
SHADOW_B = [(116, 51.3), (79, 22), (4, 22)] + [(x, y) for x, y in CURVE if x <= 86] + [(86, 133.3)]
SKY = [(0.0, "#143F82"), (0.34, "#3A72BE"), (0.62, "#7FB0E6"), (0.8, "#C6DDF4"), (1.0, "#EFEAD6")]


def region_under_line():
    """The radio shadow to the right of the station: between the line of sight and the surface."""
    return [(200, 118)] + [(x, y) for x, y in CURVE if x >= 200] + [(636, 118)]


def atmosphere():
    out = []
    for w, op in ((46, 0.10), (32, 0.14), (20, 0.2), (11, 0.3), (5, 0.5)):
        out.append(f'<path d="{CURVE_D}" fill="none" stroke="#BEE0FF" stroke-width="{w}" stroke-opacity="{op}" stroke-linejoin="round"/>')
    return "".join(out)


def earth():
    pl = CURVE + [(636, BOTTOM), (4, BOTTOM)]
    g = S.gradient
    out = [f'<defs>{g("a1e1", [(0, "#EBD9AA"), (0.35, "#D5B87F"), (1, "#7F6444")])}{g("a1e2", [(0, "#2A1E10", 0.0), (0.55, "#2A1E10", 0.1), (1, "#1B1208", 0.5)], 0, 0, 1, 0)}'
           f'<radialGradient id="a1e3" cx="0.2" cy="0.0" r="0.9"><stop offset="0" stop-color="#FFF4D2" stop-opacity="0.55"/><stop offset="1" stop-color="#FFF4D2" stop-opacity="0"/></radialGradient>'
           f'<clipPath id="a1eclip"><polygon points="{S.pts(pl)}"/></clipPath></defs>',
           f'<polygon points="{S.pts(pl)}" fill="url(#a1e1)"/><polygon points="{S.pts(pl)}" fill="url(#a1e2)"/><polygon points="{S.pts(pl)}" fill="url(#a1e3)"/>']
    # strata of the ground, following the curve at a few depths, and a few dunes' highlights
    strata = []
    for d, op in ((18, 0.16), (38, 0.14), (62, 0.12), (92, 0.10), (128, 0.08)):
        strata.append(f'<path d="M {" L ".join(f"{S.n(x)},{S.n(y + d)}" for x, y in CURVE)}" fill="none" stroke="#5E4529" stroke-opacity="{op}" stroke-width="1.4"/>')
    out.append(f'<g clip-path="url(#a1eclip)">{"".join(strata)}</g>')
    out.append(f'<path d="{CURVE_D}" fill="none" stroke="#FFF6DA" stroke-opacity="0.9" stroke-width="1.3" stroke-linejoin="round"/>')
    return "".join(out)


def shadows():
    a = region_under_line()
    g = S.gradient
    out = [f'<defs>{g("a1sa", [(0, "#FFD08A", 0.62), (1, "#F0A04A", 0.36)])}{g("a1sb", [(0, "#FFD08A", 0.62), (1, "#F0A04A", 0.34)], 1, 0, 0, 0)}</defs>',
           f'<polygon points="{S.pts(a)}" fill="url(#a1sa)"/>',
           f'<polygon points="{S.pts(SHADOW_B)}" fill="url(#a1sb)"/>',
           H.line_cased(116, 51.3, 79, 22, "#C2640F", 1.6, dash="5 4", casing=2.0)]
    return "".join(out)


def coverage():
    """A glow round the station over the sky where the radio reaches (cut out behind the ridge)."""
    top = [(4, 6), (636, 6), (636, 118), (4, 118)]
    return (f'<defs><radialGradient id="a1cov" gradientUnits="userSpaceOnUse" cx="200" cy="118" r="440"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.5"/><stop offset="0.5" stop-color="#CFE8FF" stop-opacity="0.2"/>'
            f'<stop offset="1" stop-color="#CFE8FF" stop-opacity="0"/></radialGradient>'
            f'<mask id="a1covm" maskUnits="userSpaceOnUse" x="0" y="0" width="640" height="370"><polygon points="{S.pts(top)}" fill="#FFFFFF"/><polygon points="{S.pts(SHADOW_B)}" fill="#000000"/></mask></defs>'
            f'<rect x="0" y="0" width="640" height="370" fill="url(#a1cov)" mask="url(#a1covm)"/>')


def ridge():
    outline = S.jag([(86, 135), (96, 100), (104, 73.3), (116, 51.3), (126, 69.3), (136, 98), (146, 123.4)], 1.6, 9)
    clip = [(4, 0), (636, 0)] + [(x, y + 1.5) for x, y in CURVE][::-1]
    body = S.rock("a1ridge", outline, 140, 86, 146, 7, tones=("#CDB78F", "#8F7752"), spine=[(116, 51.3), (112, 86), (118, 118), (116, 140)])
    return f'<defs><clipPath id="a1rc"><polygon points="{S.pts([(4, 0), (636, 0)] + [(x, y + 1.0) for x, y in reversed(CURVE)])}"/></clipPath></defs><g clip-path="url(#a1rc)">{body}</g>'


def station():
    return (H.mast(200, 118, 11, 5, 2.4, light=False)
            + '<circle cx="200" cy="105.5" r="2" fill="#FFFFFF"/>'
            + '<path d="M192.5,102 A10,10 0 0,1 207.5,102" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-opacity="0.95"/>'
            + '<path d="M187.2,97 A17,17 0 0,1 212.8,97" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-opacity="0.8"/>')


def beam(x1, y1, x2, y2, colour, core="#FFFFFF", width=2.6, dash=None, fade=True):
    """A beam of light from (x1, y1) to (x2, y2): a wide soft glow, the coloured beam, a thin bright core."""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{S.n(x1)}" y1="{S.n(y1)}" x2="{S.n(x2)}" y2="{S.n(y2)}" stroke="{colour}" stroke-width="{S.n(width * 3.4)}" stroke-opacity="0.45" stroke-linecap="round" filter="url(#a1glow)"/>'
            f'<line x1="{S.n(x1)}" y1="{S.n(y1)}" x2="{S.n(x2)}" y2="{S.n(y2)}" stroke="{colour}" stroke-width="{S.n(width)}" stroke-linecap="round"{dash_attr}/>'
            f'<line x1="{S.n(x1)}" y1="{S.n(y1)}" x2="{S.n(x2)}" y2="{S.n(y2)}" stroke="{core}" stroke-width="{S.n(width * 0.38)}" stroke-opacity="0.9" stroke-linecap="round"{dash_attr}/>')


def cross(cx, cy, r=6.0):
    return (f'<g stroke-linecap="round"><line x1="{S.n(cx - r)}" y1="{S.n(cy - r)}" x2="{S.n(cx + r)}" y2="{S.n(cy + r)}" stroke="#FFFFFF" stroke-width="6"/><line x1="{S.n(cx - r)}" y1="{S.n(cy + r)}" x2="{S.n(cx + r)}" y2="{S.n(cy - r)}" stroke="#FFFFFF" stroke-width="6"/>'
            f'<line x1="{S.n(cx - r)}" y1="{S.n(cy - r)}" x2="{S.n(cx + r)}" y2="{S.n(cy + r)}" stroke="#D32F2F" stroke-width="3"/><line x1="{S.n(cx - r)}" y1="{S.n(cy + r)}" x2="{S.n(cx + r)}" y2="{S.n(cy - r)}" stroke="#D32F2F" stroke-width="3"/></g>')


def dimension(x, y0, y1):
    return (f'<line x1="{x}" y1="{y0 + 5.6}" x2="{x}" y2="{y1 - 5.6}" stroke="#FFFFFF" stroke-width="4.2" stroke-opacity="0.85"/>'
            f'<line x1="{x}" y1="{y0 + 5.6}" x2="{x}" y2="{y1 - 5.6}" stroke="#10233F" stroke-width="1.6"/>'
            f'<polygon points="{x},{y0} {x + 3.9},{y0 + 7} {x - 3.8},{y0 + 7}" fill="#10233F" stroke="#FFFFFF" stroke-width="1" paint-order="stroke"/>'
            f'<polygon points="{x},{y1} {x - 3.8},{y1 - 7} {x + 3.9},{y1 - 7}" fill="#10233F" stroke="#FFFFFF" stroke-width="1" paint-order="stroke"/>')


def label(x, y, text):
    return (f'<rect x="{x - 20}" y="{y - 9}" width="40" height="18" rx="3" fill="#FFFFFF" fill-opacity="0.96" stroke="#1F2937" stroke-width="1" filter="url(#a1ds)"/>'
            f'<text x="{x}" y="{y + 4}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1F2937" text-anchor="middle">{text}</text>')


def ruler():
    out = ['<rect x="180" y="334" width="444" height="34" rx="8" fill="#FFFFFF" fill-opacity="0.9" filter="url(#a1ds)"/>',
           '<line x1="200" y1="348" x2="603.2" y2="348" stroke="#1F2937" stroke-width="1.5" stroke-linecap="round"/>']
    for x, t in ((200.0, "0"), (300.8, "24"), (401.6, "48"), (502.4, "72"), (603.2, "96")):
        out.append(f'<line x1="{x}" y1="344" x2="{x}" y2="352" stroke="#1F2937" stroke-width="1.5" stroke-linecap="round"/>'
                   f'<text x="{x}" y="365" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="middle">{t}</text>')
    return "".join(out)


def layers():
    out = [f'<defs>{S.gradient("a1page", [(0, "#F1F5FA"), (1, "#E6EDF5")])}<filter id="a1glow" filterUnits="userSpaceOnUse" x="0" y="0" width="640" height="370"><feGaussianBlur stdDeviation="2.8"/></filter></defs>'
           '<rect x="0" y="0" width="640" height="370" fill="url(#a1page)"/>', H.defs()]
    x, y, w, h = CARD
    out.append(S.card("a1card", x, y, w, h, SKY, "", radius=10))
    inner = [atmosphere(), coverage(), shadows(), earth(), ridge(), station(),
             beam(200, 118, 636, 118, "#58A6FF", dash="9 5"),
             beam(206, 116, 556, 50.8, "#19B27A", width=3.2),
             beam(206, 119, 309.2, 132.1, "#E5483C", width=2.2, dash="6 4"), cross(309.2, 132.1),
             beam(194, 117, 141.8, 110.5, "#E5483C", width=2.2, dash="6 4"), cross(141.8, 110.5),
             dimension(401.6, 119, 165), dimension(502.4, 119, 225), dimension(603.2, 119, 309),
             label(375.6, 141, "1 600"), label(476.4, 171, "3 600"), label(577.2, 213, "6 400"), ruler()]
    out += H.clipped("a1cc", CARD, 10, inner)
    out.append(S.card_front("a1cf", x, y, w, h, "", radius=10))
    out.append({"name": "sprite-side", "at": [577, 43], "width": 64, **H.LOOK})
    out.append({"name": "sprite-side", "at": [577, 163], "width": 64, **H.LOOK})
    out.append({"name": "sprite-side-left", "at": [58, 95], "width": 64, **H.LOOK})
    c = S.callout
    out.append("".join([c(1, 200, 80, 200, 99), c(2, 300, 98, 296, 117.5), c(3, 578, 252), c(4, 612, 38.8, 600, 40), c(5, 577, 130, 577, 150),
                         c(6, 116, 32, 116, 50), c(7, 52, 62, 56, 86), c(8, 401.6, 98, 401.6, 119)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-19-01-vhf-line-of-sight",
        "replaces": "fig-19-01-vhf-line-of-sight.svg",
        "book_file": "plate-19-01-vhf-line-of-sight.jpg",
        "caption": "Figure 19-1. VHF radio reaches only as far as the line of sight",
        "desc": "Figure 19-1. VHF radio reaches only as far as the line of sight",
        "legend": [
            "A ground station, antenna height ignored.",
            "The line of sight from the station.",
            "The radio shadow below it.",
            "An aircraft above the line: two-way contact.",
            "An aircraft at the same distance, lower: the bulge of the earth blocks the path.",
            "A ridge casts its own shadow.",
            "An aircraft behind the ridge: no contact, even close to the station.",
            "Height of the line of sight above the ground, in feet, at 48, 72 and 96 NM.",
        ],
        "canvas": [640, 370],
        "background": "pale",
        "reskin": {"svg": "fig-19-01-vhf-line-of-sight.svg", "blank": True, "layers": layers()},
    }
