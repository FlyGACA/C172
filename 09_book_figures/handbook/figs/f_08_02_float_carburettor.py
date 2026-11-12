"""Figure 8-2. A float-type carburettor and where ice forms. An up-draft carburettor drawn as a cutaway: the cast body with its walls cut to show the air passage (the venturi, the throttle
valve above it), the float bowl at its side (the fuel and the float, the needle valve at the fuel inlet, the mixture needle in the jet) and the fuel passage to the discharge nozzle in the
throat, with a flow band through the passage and the ice where the air is coldest. The drawing is made by this module (figs/scene.py supplies the callouts and gradients); the nine numbered
callouts of the old figure are kept."""
import math
import random

from figs import scene as S

CX = 430.0                       # the axis of the air passage
Y_TOP, Y_BOTTOM = 44.0, 316.0    # the faces of the flanges
Y_THROAT = 196.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def inner(y):
    """Half the width of the air passage at height y: the venturi narrows towards the throat and opens gradually above it."""
    if y >= 270:
        return 54.0
    if y >= Y_THROAT:
        return 54.0 - 28.0 * smooth((270 - y) / 74.0)
    if y >= 126:
        return 26.0 + 28.0 * smooth((Y_THROAT - y) / 70.0)
    return 54.0


def outer(y):
    """Half the width of the cast body: thicker round the throat, which holds the nozzle."""
    u = (y - 195.0) / 78.0
    return 80.0 + 9.0 * max(0.0, 1.0 - u * u)


def contour(fn, side, y0=Y_TOP, y1=Y_BOTTOM, step=4.0):
    pts, y = [], y0
    while y <= y1 + 0.01:
        pts.append((CX + side * fn(y), y))
        y += step
    return pts


def defs():
    g = S.gradient
    return ("<defs>"
            + g("f0802bg", [(0, "#F7FAFD"), (1, "#E1EAF4")])
            + g("f0802wl", [(0, "#C95F12"), (0.55, "#F0A33B"), (1, "#FFD98A")], 0, 0, 1, 0)           # the left wall: outside dark, the cut face light
            + g("f0802wr", [(0, "#FFD98A"), (0.45, "#F0A33B"), (1, "#C95F12")], 0, 0, 1, 0)
            + g("f0802bore", [(0, "#0F3541"), (0.5, "#2B7280"), (1, "#0F3541")], 0, 0, 1, 0)
            + g("f0802bore2", [(0, "#000000", 0.0), (1, "#06202A", 0.35)])
            + g("f0802fl", [(0, "#F4B03F"), (1, "#C86A12")], 0, 0, 1, 0)
            + g("f0802bowl", [(0, "#C95F12"), (0.4, "#F0A33B"), (1, "#C95F12")], 0, 0, 1, 0)
            + g("f0802cav", [(0, "#12404D"), (1, "#0B2A35")])
            + g("f0802fuel", [(0, "#F7C45F", 0.95), (1, "#D98A1E", 0.95)])
            + g("f0802steel", [(0, "#8E9BB0"), (0.45, "#E9EEF5"), (1, "#7B8799")], 0, 0, 0, 1)
            + g("f0802steelv", [(0, "#8E9BB0"), (0.45, "#E9EEF5"), (1, "#7B8799")], 0, 0, 1, 0)
            + g("f0802blue", [(0, "#4F78B5"), (1, "#1F3A63")], 0, 0, 1, 1)
            + g("f0802pipe", [(0, "#B9C3D2"), (0.5, "#F1F4F9"), (1, "#8D98AB")], 0, 0, 0, 1)
            + f'<radialGradient id="f0802ball" cx="0.36" cy="0.32" r="0.75"><stop offset="0" stop-color="#FFFDF0"/><stop offset="0.6" stop-color="#F2E3B0"/><stop offset="1" stop-color="#C9B06A"/></radialGradient>'
            + f'<linearGradient id="f0802flow" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#8FD0F7" stop-opacity="0.85"/><stop offset="0.5" stop-color="#C9E9FB" stop-opacity="0.9"/>'
              f'<stop offset="0.6" stop-color="#FFF0C4" stop-opacity="0.92"/><stop offset="1" stop-color="#FFD58A" stop-opacity="0.95"/></linearGradient>'
            + f'<filter id="f0802sh" x="-20%" y="-10%" width="140%" height="130%"><feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#1B2B44" flood-opacity="0.28"/></filter>'
            + f'<filter id="f0802blur"><feGaussianBlur stdDeviation="2.2"/></filter>'
            + "</defs>")


def body():
    left_out, right_out = contour(outer, -1), contour(outer, +1)
    left_in, right_in = contour(inner, -1), contour(inner, +1)
    out = [f'<rect x="0" y="0" width="640" height="360" fill="url(#f0802bg)"/>',
           f'<ellipse cx="{S.n(CX)}" cy="346" rx="130" ry="9" fill="#1B2B44" opacity="0.16" filter="url(#f0802blur)"/>']
    # the bore: what is seen of the far half of the passage once the near half is cut away
    cav = left_in + list(reversed(right_in))
    out.append(f'<polygon points="{S.pts(cav)}" fill="url(#f0802bore)"/><polygon points="{S.pts(cav)}" fill="url(#f0802bore2)"/>')
    # the cast walls, cut: left and right
    lw = left_out + list(reversed(left_in))
    rw = right_in + list(reversed(right_out))
    out.append(f'<g filter="url(#f0802sh)"><polygon points="{S.pts(lw)}" fill="url(#f0802wl)"/><polygon points="{S.pts(rw)}" fill="url(#f0802wr)"/></g>')
    for pts_ in (left_in, right_in):
        out.append(f'<path d="M {" L ".join(f"{S.n(a)},{S.n(b)}" for a, b in pts_)}" fill="none" stroke="#FFF1C9" stroke-width="1.6" stroke-opacity="0.9"/>')
    for pts_ in (left_out, right_out):
        out.append(f'<path d="M {" L ".join(f"{S.n(a)},{S.n(b)}" for a, b in pts_)}" fill="none" stroke="#7A3A08" stroke-width="1.2" stroke-opacity="0.55"/>')
    # flanges and their bolts
    for y0 in (Y_TOP - 24, Y_BOTTOM):
        out.append(f'<g filter="url(#f0802sh)"><rect x="{S.n(CX - 100)}" y="{S.n(y0)}" width="200" height="24" rx="6" fill="url(#f0802wl)"/></g>'
                   f'<rect x="{S.n(CX - 100)}" y="{S.n(y0)}" width="200" height="4" rx="2" fill="#FFF1C9" opacity="0.7"/>')
        for dx in (-86, 86):
            out.append(f'<circle cx="{S.n(CX + dx)}" cy="{S.n(y0 + 13)}" r="5" fill="url(#f0802steelv)" stroke="#5A6578" stroke-width="0.8"/><line x1="{S.n(CX + dx - 3)}" y1="{S.n(y0 + 13)}" x2="{S.n(CX + dx + 3)}" y2="{S.n(y0 + 13)}" stroke="#5A6578" stroke-width="1"/>')
    return "".join(out)


def flow():
    """A flow band through the passage: air blue below the throat and the mixture warm above it, with arrowheads."""
    ys = [Y_BOTTOM - 6 - i * 4 for i in range(int((Y_BOTTOM - Y_TOP - 8) / 4))]
    left = [(CX - 0.74 * inner(y), y) for y in ys]
    right = [(CX + 0.74 * inner(y), y) for y in ys]
    band = left + list(reversed(right))
    out = [f'<polygon points="{S.pts(band)}" fill="url(#f0802flow)" opacity="0.86"/>']
    for y, k in ((284, 20), (206, 11), (112, 20)):
        out.append(f'<path d="M {S.n(CX - k)},{S.n(y + 12)} L {S.n(CX)},{S.n(y - 8)} L {S.n(CX + k)},{S.n(y + 12)} L {S.n(CX + k * 0.45)},{S.n(y + 8)} L {S.n(CX)},{S.n(y - 1)} L {S.n(CX - k * 0.45)},{S.n(y + 8)} Z" fill="#FFFFFF" opacity="0.85" stroke="#6BA7D6" stroke-width="0.8"/>')
    return "".join(out)


def nozzle_and_spray():
    rnd = random.Random(4)
    ty = 202.0
    tip_x = CX - inner(ty) + 1
    out = [f'<path d="M {S.n(CX - 80)},{S.n(ty - 4)} L {S.n(tip_x - 6)},{S.n(ty - 4)} L {S.n(tip_x + 12)},{S.n(ty - 9)} L {S.n(tip_x + 12)},{S.n(ty + 9)} L {S.n(tip_x - 6)},{S.n(ty + 4)} L {S.n(CX - 80)},{S.n(ty + 4)} Z" fill="url(#f0802pipe)" stroke="#5A6578" stroke-width="0.9"/>',
           f'<ellipse cx="{S.n(tip_x + 12)}" cy="{S.n(ty)}" rx="2.4" ry="8.4" fill="#0B2A35" stroke="#5A6578" stroke-width="0.8"/>']
    for _ in range(46):
        d = rnd.uniform(4, 50)
        a = math.radians(rnd.uniform(-52, 8))
        x, y = tip_x + 14 + d * math.cos(a) * 1.05, ty + d * math.sin(a) * 0.9
        if abs(x - CX) < inner(y) - 2:
            out.append(f'<circle cx="{S.n(x)}" cy="{S.n(y)}" r="{S.n(rnd.uniform(0.9, 2.0))}" fill="#F6B34A" stroke="#FFF2C9" stroke-width="0.4" opacity="{S.n(rnd.uniform(0.7, 1.0))}"/>')
    return "".join(out)


def ice():
    """Ice at the throat and on the throttle valve, where the air is coldest: pale angular crystals with a bright edge."""
    rnd = random.Random(11)
    out = []
    spots = [(CX - inner(y) + 1, y, -1) for y in (170, 186, 214, 228)] + [(CX + inner(y) - 1, y, +1) for y in (168, 182, 198, 212, 226)]
    for x, y, side in spots:
        for _ in range(3):
            w, h = rnd.uniform(3.5, 7.5), rnd.uniform(6, 13)
            bx, by = x + side * rnd.uniform(-1, 4), y + rnd.uniform(-4, 4)
            pts_ = [(bx, by - h * 0.5), (bx - side * w, by - h * 0.15), (bx - side * w * 0.5, by + h * 0.5), (bx + side * 0.5, by + h * 0.35)]
            out.append(f'<polygon points="{S.pts(pts_)}" fill="#E9F8FF" stroke="#FFFFFF" stroke-width="0.9" opacity="0.95"/><polygon points="{S.pts([(bx, by - h * 0.5), (bx - side * w * 0.45, by - h * 0.1), (bx - side * w * 0.2, by + h * 0.2)])}" fill="#9ED8F2" opacity="0.8"/>')
    return f'<g filter="url(#f0802blur)" opacity="0.55"><ellipse cx="{S.n(CX)}" cy="198" rx="40" ry="38" fill="#BFEFFF"/></g>' + "".join(out)


def throttle():
    y = 90.0
    w = inner(y)
    return (f'<g filter="url(#f0802sh)"><rect x="{S.n(CX - 88)}" y="{S.n(y - 5)}" width="176" height="10" rx="5" fill="url(#f0802steel)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<ellipse cx="{S.n(CX)}" cy="{S.n(y)}" rx="{S.n(w - 3)}" ry="12" transform="rotate(-10 {S.n(CX)} {S.n(y)})" fill="url(#f0802blue)" stroke="#16294A" stroke-width="1.3"/>'
            f'<ellipse cx="{S.n(CX - 8)}" cy="{S.n(y - 3)}" rx="{S.n(w * 0.45)}" ry="3.4" transform="rotate(-10 {S.n(CX)} {S.n(y)})" fill="#FFFFFF" opacity="0.35"/>'
            f'<path d="M {S.n(CX + 90)},{S.n(y)} L {S.n(CX + 122)},{S.n(y - 26)}" stroke="url(#f0802steelv)" stroke-width="6" stroke-linecap="round"/>'
            f'<circle cx="{S.n(CX + 124)}" cy="{S.n(y - 28)}" r="6" fill="url(#f0802ball)" stroke="#5A6578" stroke-width="0.9"/></g>')


def bowl():
    x0, y0, w, h = 56.0, 134.0, 244.0, 188.0
    fuel_y = 232.0
    out = [f'<g filter="url(#f0802sh)"><rect x="{S.n(x0)}" y="{S.n(y0)}" width="{S.n(w)}" height="{S.n(h)}" rx="18" fill="url(#f0802bowl)"/></g>',
           f'<rect x="{S.n(x0 + 2)}" y="{S.n(y0 + 2)}" width="{S.n(w - 4)}" height="5" rx="2.5" fill="#FFF1C9" opacity="0.7"/>',
           # the web that joins the bowl to the body
           f'<path d="M {S.n(x0 + w - 6)},{S.n(y0 + 120)} L {S.n(CX - 80)},{S.n(y0 + 128)} L {S.n(CX - 80)},{S.n(y0 + h - 4)} L {S.n(x0 + w - 6)},{S.n(y0 + h - 4)} Z" fill="url(#f0802fl)" stroke="#7A3A08" stroke-opacity="0.5" stroke-width="1"/>']
    cx0, cy0, cw, ch = x0 + 16, y0 + 18, w - 32, h - 34
    out.append(f'<rect x="{S.n(cx0)}" y="{S.n(cy0)}" width="{S.n(cw)}" height="{S.n(ch)}" rx="10" fill="url(#f0802cav)"/>')
    # the fuel and its level
    wave = "".join(f" Q {S.n(cx0 + 12 + i * 30 + 7)},{S.n(fuel_y + (2.2 if i % 2 else -2.2))} {S.n(cx0 + 12 + (i + 1) * 30)},{S.n(fuel_y)}" for i in range(int((cw - 24) / 30)))
    out.append(f'<path d="M {S.n(cx0)},{S.n(fuel_y)}{wave} L {S.n(cx0 + cw)},{S.n(fuel_y)} L {S.n(cx0 + cw)},{S.n(cy0 + ch - 4)} Q {S.n(cx0 + cw)},{S.n(cy0 + ch)} {S.n(cx0 + cw - 10)},{S.n(cy0 + ch)} L {S.n(cx0 + 10)},{S.n(cy0 + ch)} Q {S.n(cx0)},{S.n(cy0 + ch)} {S.n(cx0)},{S.n(cy0 + ch - 10)} Z" fill="url(#f0802fuel)"/>')
    out.append(f'<path d="M {S.n(cx0 + 4)},{S.n(fuel_y + 1)}{wave} " fill="none" stroke="#FFF2C9" stroke-width="1.2" stroke-opacity="0.9"/>')
    # needle valve at the fuel inlet, the float arm and the float
    vx = 120.0
    out.append(f'<rect x="{S.n(vx - 9)}" y="{S.n(cy0 - 2)}" width="18" height="26" rx="3" fill="url(#f0802pipe)" stroke="#5A6578" stroke-width="0.9"/>'
               f'<path d="M {S.n(vx - 2.5)},{S.n(cy0 + 24)} L {S.n(vx + 2.5)},{S.n(cy0 + 24)} L {S.n(vx + 1)},{S.n(cy0 + 40)} L {S.n(vx - 1)},{S.n(cy0 + 40)} Z" fill="#EDEFF3" stroke="#5A6578" stroke-width="0.7"/>'
               f'<circle cx="{S.n(vx - 12)}" cy="{S.n(cy0 + 47)}" r="3.4" fill="url(#f0802steelv)" stroke="#5A6578" stroke-width="0.8"/>'
               f'<path d="M {S.n(vx - 12)},{S.n(cy0 + 47)} L {S.n(vx + 12)},{S.n(cy0 + 43)} L 156,{S.n(fuel_y - 6)}" fill="none" stroke="#C7CFDB" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<path d="M {S.n(vx + 12)},{S.n(cy0 + 43)} L {S.n(vx + 1)},{S.n(cy0 + 40)}" stroke="#8E9BB0" stroke-width="2" stroke-linecap="round"/>'
               f'<circle cx="158" cy="{S.n(fuel_y - 4)}" r="23" fill="url(#f0802ball)" stroke="#8C7A44" stroke-width="1"/><ellipse cx="150" cy="{S.n(fuel_y - 12)}" rx="7" ry="4.5" fill="#FFFFFF" opacity="0.7"/>')
    # the mixture needle, its jet and the passage to the nozzle
    nx = 244.0
    jet_y = cy0 + ch - 12
    out.append(f'<rect x="{S.n(nx - 3)}" y="{S.n(cy0 - 4)}" width="6" height="{S.n(jet_y - cy0 - 6)}" fill="url(#f0802steelv)" stroke="#5A6578" stroke-width="0.7"/>'
               f'<path d="M {S.n(nx - 3)},{S.n(jet_y - 12)} L {S.n(nx)},{S.n(jet_y + 4)} L {S.n(nx + 3)},{S.n(jet_y - 12)} Z" fill="#EDEFF3" stroke="#5A6578" stroke-width="0.7"/>'
               f'<rect x="{S.n(nx - 14)}" y="{S.n(jet_y)}" width="28" height="12" rx="3" fill="url(#f0802pipe)" stroke="#5A6578" stroke-width="0.8"/>'
               f'<rect x="{S.n(nx - 9)}" y="{S.n(y0 - 3)}" width="18" height="12" rx="3" fill="url(#f0802pipe)" stroke="#5A6578" stroke-width="0.8"/>'
               f'<rect x="{S.n(nx - 16)}" y="{S.n(y0 - 56)}" width="32" height="7" rx="3.5" fill="url(#f0802blue)" stroke="#16294A" stroke-width="0.9"/>'
               f'<rect x="{S.n(nx - 3)}" y="{S.n(y0 - 50)}" width="6" height="{S.n(y0 - 4 - (y0 - 50))}" fill="url(#f0802steelv)" stroke="#5A6578" stroke-width="0.7"/>')
    py = jet_y + 6
    passage = f"M {S.n(nx + 4)},{S.n(py)} L {S.n(CX - outer(py) + 16)},{S.n(py)} L {S.n(CX - outer(py) + 16)},202 L {S.n(CX - 80)},202"
    out.append(f'<path d="{passage}" fill="none" stroke="#5A2A06" stroke-width="9" stroke-linejoin="round" opacity="0.9"/><path d="{passage}" fill="none" stroke="#F4B03F" stroke-width="5.4" stroke-linejoin="round"/>')
    return "".join(out)


def fuel_inlet():
    return (f'<g filter="url(#f0802sh)"><path d="M 14,64 L 120,64 L 120,{S.n(134 + 18)}" fill="none" stroke="url(#f0802pipe)" stroke-width="15" stroke-linejoin="round"/></g>'
            f'<path d="M 14,64 L 120,64 L 120,152" fill="none" stroke="#5A6578" stroke-width="0.8" opacity="0.6" transform="translate(-7.5 0)"/>'
            f'<rect x="108" y="120" width="24" height="12" rx="3" fill="url(#f0802steelv)" stroke="#5A6578" stroke-width="0.9"/>'
            + S.ribbon("f0802fi", [(24, 64), (70, 64), (120, 64), (120, 110)], 6.0, "#E8A33A", "#FBE3A6", opacity=0.97, shadow=False))


def callouts():
    c = S.callout
    return "".join([c(1, 566, 326, 474, 311), c(2, 572, 224, 458, 212), c(3, 346, 166, 408, 196), c(4, 572, 118, 484, 94), c(5, 30, 262, 62, 262), c(6, 296, 34, 247, 70), c(7, 66, 26, 66, 58),
                    c(8, 572, 170, 456, 186), c(9, 572, 64, 468, 58)])


def plate():
    return {
        "id": "fig-08-02-float-carburettor",
        "replaces": "fig-08-02-float-carburettor.svg",
        "book_file": "plate-08-02-float-carburettor.jpg",
        "caption": "Figure 8-2. A float-type carburettor and where ice forms",
        "desc": "Figure 8-2. A float-type carburettor and where ice forms",
        "legend": [
            "Air inlet, from the filter or, with carburettor heat on, from the heat source.",
            "Venturi: the air speeds up and its pressure falls.",
            "Discharge nozzle: the low pressure draws fuel into the airstream.",
            "Throttle valve, turned by the throttle, which controls the flow of mixture.",
            "Float chamber: the float and needle valve keep the fuel level constant.",
            "Mixture needle, moved by the mixture control, which meters the fuel.",
            "Fuel from the aeroplane's fuel system.",
            "Ice, which forms in the venturi and on the throttle valve, where the air is coldest.",
            "Mixture to the intake manifold and cylinders.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-08-02-float-carburettor.svg", "blank": True,
                   "layers": [defs(), body(), flow(), nozzle_and_spray(), ice(), throttle(), bowl(), fuel_inlet(), callouts()]},
    }
