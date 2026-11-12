"""Figure 23-7. Runway width and slope illusions: what you see and where you end up. Four cards, each a pair of pictures of one approach: the windscreen as a window onto a desert
aerodrome in perspective (the runway an asphalt trapezoid with its edge lines, edge lights and centre-line dashes spaced as they are in perspective, over sand, scrub and far hills,
with the usual runway's outline dashed in green) and, to the right, the same approach from the side (sand and far hills under a sky, the runway a slab, flat or on a slope; the correct
path a green ribbon and the path you fly if you trust the picture a red one). The seven numbered callouts of the old figure are kept; the shapes of the runways and of the paths are the
old figure's."""
import math

from figs import scene as S
from figs import h_a3 as H

n = S.n
HORIZON = 62.0                    # y of the horizon in the window, relative to the card's own frame (card 1)
OUTLINE = [(75, 94), (93, 94), (116, 176), (52, 176)]        # the usual runway, seen from the correct path
GREEN = ("#0B7A4E", "#5CCB93")
RED = ("#B3261E", "#F28C7C")
SKY = [(0.0, "#6F9FD4"), (0.62, "#B9D3EE"), (1.0, "#F2F5F7")]

# the four cards: origin of the card in the old figure, the runway's trapezoid in the window (card-relative), the red path (cubic Bezier control points, absolute in the old figure),
# the green path's ends, the runway slab in the side view (the ground and runway ends) and the callout of the card
CARDS = [
    {"n": 1, "ox": 0, "oy": 0, "poly": [(79, 94), (89, 94), (101.6, 176), (66.4, 176)],
     "red": [(148.0, 128.0), (154.0, 133.7), (173.0, 156.0), (184.0, 162.0), (195.0, 168.0), (208.0, 163.2), (214.0, 164.0), (220.0, 164.8), (219.1, 166.1), (220.1, 166.5)],
     "green": ((148, 128), (248, 170)), "ground": [(236, 170), (312, 170)], "slab": ((236, 170), (308, 170))},
    {"n": 2, "ox": 316, "oy": 0, "poly": [(69.6, 94), (98.4, 94), (135.2, 176), (32.8, 176)],
     "red": [(148.0, 128.0), (154.0, 129.0), (171.3, 129.7), (184.0, 134.0), (196.7, 138.3), (209.0, 149.7), (224.0, 154.0), (239.0, 158.3), (264.8, 158.1), (274.0, 160.0), (283.2, 161.9), (278.6, 164.6), (279.5, 165.5)],
     "green": ((148, 128), (248, 170)), "ground": [(236, 170), (312, 170)], "slab": ((236, 170), (308, 170))},
    {"n": 3, "ox": 0, "oy": 196, "poly": [(75.9, 78), (92.1, 78), (116, 176), (52, 176)],
     "red": [(148.0, 125.7), (154.0, 131.3), (173.0, 153.3), (184.0, 159.7), (195.0, 166.1), (208.0, 162.9), (214.0, 164.0), (220.0, 165.1), (219.1, 166.1), (220.1, 166.5)],
     "green": ((148, 125.7), (248, 167.7)), "ground": [(236, 170), (312, 155.2)], "slab": ((236, 170), (308, 156))},
    {"n": 4, "ox": 316, "oy": 196, "poly": [(73.6, 112), (94.4, 112), (116, 176), (52, 176)],
     "red": [(148.0, 130.3), (154.0, 131.3), (171.3, 132.0), (184.0, 136.3), (196.7, 140.7), (209.0, 150.8), (224.0, 156.3), (239.0, 161.8), (264.8, 166.3), (274.0, 169.3), (283.2, 172.4), (278.6, 173.9), (279.5, 174.8)],
     "green": ((148, 130.3), (248, 172.3)), "ground": [(236, 170), (312, 184.8)], "slab": ((236, 170), (308, 184.8))},
]


CLOUDS = [(("cloud-cumulus-b", 262, 46, 52), ("cloud-cumulus-c", 192, 28, 30)), (("cloud-cumulus-a", 250, 38, 64), ("cloud-cumulus-b", 186, 56, 30)),
          (("cloud-cumulus-c", 270, 52, 44), ("cloud-cumulus-b", 200, 26, 36)), (("cloud-cumulus-b", 238, 34, 58), ("cloud-cumulus-c", 292, 62, 26))]


def bezier(nums, per=8):
    """Points along a chain of cubic Beziers given as p0, c1, c2, p1, c3, c4, p2, ..."""
    p = nums
    out = [p[0]]
    for i in range(0, len(p) - 3, 3):
        a, b, c, d = p[i], p[i + 1], p[i + 2], p[i + 3]
        for k in range(1, per + 1):
            t = k / per
            u = 1 - t
            out.append(tuple(u ** 3 * a[j] + 3 * u * u * t * b[j] + 3 * u * t * t * c[j] + t ** 3 * d[j] for j in (0, 1)))
    return out


def edge_x(poly, y):
    """The left and right edge of the trapezoid at height y."""
    (xl0, y0), (xr0, _), (xr1, y1), (xl1, _) = poly
    t = (y - y0) / (y1 - y0)
    return xl0 + (xl1 - xl0) * t, xr0 + (xr1 - xr0) * t


def window_runway(uid, poly, ox, oy):
    """The runway in the window: asphalt trapezoid, edge lines, edge lights and centre dashes spaced in perspective (equal steps along the ground, so they open out towards you)."""
    pts_ = [(x + ox, y + oy) for x, y in poly]
    y_far, y_near = poly[0][1], poly[2][1]
    K = 1000.0
    z_far, z_near = K / (y_far - HORIZON), K / (y_near - HORIZON)
    out = [f'<defs>{S.gradient(uid, [(0, "#8A94A6"), (0.35, "#5A6475"), (1, "#2B3140")])}</defs>',
           f'<polygon points="{S.pts(pts_)}" fill="url(#{uid})"/>']
    # a lighter shoulder of packed sand each side and edge lines
    for side in (0, 1):
        a = (edge_x(poly, y_far)[side], y_far)
        b = (edge_x(poly, y_near)[side], y_near)
        inset = 0.045
        ca = (a[0] + (edge_x(poly, y_far)[1 - side] - a[0]) * inset, a[1])
        cb = (b[0] + (edge_x(poly, y_near)[1 - side] - b[0]) * inset, b[1])
        out.append(f'<line x1="{n(ca[0] + ox)}" y1="{n(ca[1] + oy)}" x2="{n(cb[0] + ox)}" y2="{n(cb[1] + oy)}" stroke="#F3F4F6" stroke-opacity="0.85" stroke-width="0.9"/>')
    count = 5
    period = (z_far - z_near) / count
    for i in range(count):
        za, zb = z_near + (i + 0.16) * period, z_near + (i + 0.64) * period
        ya, yb = HORIZON + K / za, HORIZON + K / zb                      # (ya is the nearer end, lower on the page)
        xla, xra = edge_x(poly, ya)
        xlb, xrb = edge_x(poly, yb)
        ca, cb = (xla + xra) / 2, (xlb + xrb) / 2
        ha, hb = 0.026 * (xra - xla) + 0.15, 0.026 * (xrb - xlb) + 0.15
        out.append(f'<polygon points="{S.pts([(ca - ha + ox, ya + oy), (ca + ha + ox, ya + oy), (cb + hb + ox, yb + oy), (cb - hb + ox, yb + oy)])}" fill="#FFFFFF" fill-opacity="0.95"/>')
    lights = []
    for i in range(count * 2 + 1):
        z = z_near + i * period / 2
        y = HORIZON + K / z
        if y < y_far - 0.5:
            continue
        xl, xr = edge_x(poly, y)
        r = 0.45 + 0.017 * (xr - xl)
        for x in (xl - (xr - xl) * 0.02, xr + (xr - xl) * 0.02):
            lights.append(f'<circle cx="{n(x + ox)}" cy="{n(y + oy)}" r="{n(r * 2.6)}" fill="#FFF4C9" fill-opacity="0.35"/><circle cx="{n(x + ox)}" cy="{n(y + oy)}" r="{n(r)}" fill="#FFFBE8"/>')
    return "".join(out) + "".join(lights)


def window(c, seed):
    """The windscreen: sky, far hills, sand with scrub, the runway, the dashed outline of the usual runway; framed."""
    ox, oy = c["ox"], c["oy"]
    x0, y0, w, h = 20 + ox, 40 + oy, 128, 144
    hz = HORIZON + oy
    uid = f"f2307w{c['n']}"
    clip = f'<clipPath id="{uid}c"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="5"/></clipPath>'
    sky = S.sky(uid + "k", x0, y0, w, hz - y0 + 1, [(0, "#6C9CD2"), (0.7, "#B3CFEC"), (1, "#E6EEF6")])
    hills = S.land_layer(uid + "h", S.ridge(seed, x0, x0 + w, hz + 1, 13, peaks=0.5), hz + 3, ("#7C8DB5", "#B9C6DE"), rim=False, haze=0.18)
    sand = (f'<defs>{S.gradient(uid + "g", [(0, "#EBDDBC"), (0.25, "#E4D2A6"), (1, "#CBAE78")])}</defs><rect x="{x0}" y="{hz}" width="{w}" height="{y0 + h - hz}" fill="url(#{uid}g)"/>'
            + S.scrub(seed + 2, x0, x0 + w, hz + 5, y0 + h - 2, 15, colour=("#8A8A55", "#5E603E"), scale=0.62))
    runway = window_runway(uid + "r", c["poly"], ox, oy)
    usual = [(x + ox, y + oy) for x, y in OUTLINE]
    outline = (f'<polygon points="{S.pts(usual)}" fill="none" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.8" stroke-linejoin="round"/>'
               f'<polygon points="{S.pts(usual)}" fill="none" stroke="#0A7D4F" stroke-width="2" stroke-dasharray="5 3" stroke-linejoin="round"/>')
    glare = (f'<defs>{S.gradient(uid + "s", [(0, "#FFFFFF", 0.0), (0.5, "#FFFFFF", 0.20), (1, "#FFFFFF", 0.0)], 0, 0, 1, 1)}</defs>'
             f'<polygon points="{S.pts([(x0 + 6, y0), (x0 + 50, y0), (x0 + 6, y0 + 56)])}" fill="url(#{uid}s)"/>')
    vign = (f'<defs><radialGradient id="{uid}v" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#101B33" stop-opacity="0"/><stop offset="1" stop-color="#101B33" stop-opacity="0.28"/></radialGradient></defs>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{uid}v)"/>')
    frame = (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="5" fill="none" stroke="#1B2335" stroke-width="3.2"/>'
             f'<rect x="{x0 + 1.4}" y="{y0 + 1.4}" width="{w - 2.8}" height="{h - 2.8}" rx="4" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="0.7"/>')
    return f'<defs>{clip}</defs><g clip-path="url(#{uid}c)">{sky}{hills}{sand}{runway}{vign}{glare}{outline}</g>{frame}'


def side_view(c, seed):
    """The same approach from the side: far hills, sand, the runway slab on its ground, flat or sloping."""
    ox, oy = c["ox"], c["oy"]
    uid = f"f2307v{c['n']}"
    (gx0, gy0), (gx1, gy1) = c["ground"]
    gx0, gx1 = gx0 + ox, gx1 + ox
    gy0, gy1 = gy0 + oy, gy1 + oy
    x_left, x_right, bottom = 8 + ox, 316 + ox, 196 + oy
    ground = [(x_left, gy0), (gx0, gy0), (gx1, gy1), (x_right, gy1)]
    top = min(gy0, gy1)
    hills = S.land_layer(uid + "h", S.ridge(seed + 5, x_left, x_right, top - 3, 22, peaks=0.55), bottom, ("#8696BA", "#BAC6DC"), rim=False, haze=0.30)
    hills2 = S.land_layer(uid + "i", S.ridge(seed + 9, x_left, x_right, top - 1, 10, peaks=0.3), bottom, ("#A3B0CB", "#CDD6E6"), rim=False, haze=0.18)
    sand_poly = ground + [(x_right, bottom), (x_left, bottom)]
    sand = (f'<defs>{S.gradient(uid + "g", [(0, "#EFE2C0"), (0.35, "#E3D0A3"), (1, "#C9AB75")])}</defs>'
            f'<polygon points="{S.pts(sand_poly)}" fill="url(#{uid}g)"/>'
            f'<path d="M {S.pts(ground).replace(" ", " L ")}" fill="none" stroke="#FFF7DE" stroke-opacity="0.8" stroke-width="0.9"/>'
            + S.scrub(seed + 1, x_left + 2, gx0 - 6, gy0 + 3, bottom - 1.5, 7, colour=("#8A8A55", "#5E603E"), scale=0.5))
    (sx0, sy0), (sx1, sy1) = c["slab"]
    sx0, sx1, sy0, sy1 = sx0 + ox, sx1 + ox, sy0 + oy, sy1 + oy
    th = 4.2
    slab = [(sx0, sy0 - 0.6), (sx1, sy1 - 0.6), (sx1, sy1 + th), (sx0, sy0 + th)]
    run = (f'<defs>{S.gradient(uid + "a", [(0, "#7C8698"), (1, "#2C3341")])}</defs>'
           f'<ellipse cx="{n((sx0 + sx1) / 2 + 2)}" cy="{n((sy0 + sy1) / 2 + th + 1.5)}" rx="{n((sx1 - sx0) / 2)}" ry="1.6" fill="#6B573A" fill-opacity="0.25"/>'
           f'<polygon points="{S.pts(slab)}" fill="url(#{uid}a)" stroke="#1D2330" stroke-width="0.5" stroke-linejoin="round"/>'
           f'<line x1="{n(sx0)}" y1="{n(sy0 - 0.6)}" x2="{n(sx1)}" y2="{n(sy1 - 0.6)}" stroke="#E9EEF5" stroke-opacity="0.7" stroke-width="0.8"/>')
    return hills + hills2 + sand + run


def paths(c):
    r = S.ribbon
    ox, oy = c["ox"], c["oy"]
    (a, b) = c["green"]
    k = c["n"]
    red = [(x + ox, y + oy) for x, y in bezier(c["red"], 7)]
    red = red[::3] + [red[-1]]
    green = [(a[0] + ox, a[1] + oy), ((a[0] + b[0]) / 2 + ox, (a[1] + b[1]) / 2 + oy), (b[0] + ox, b[1] + oy)]
    return r(f"f2307g{k}", green, 4.4, *GREEN, head=1.0) + r(f"f2307r{k}", red, 4.4, *RED, head=2.3)


def point_at_x(points, x):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            return (x0 + (x1 - x0) * (x - x0) / ((x1 - x0) or 1.0), y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1.0))
    return points[-1]


def callouts():
    c = S.callout
    first = CARDS[0]
    red = [(x, y) for x, y in bezier(first["red"], 7)]
    rx, ry = point_at_x(red, 205)
    return "".join([c(1, 30, 27), c(2, 346, 27), c(3, 30, 223), c(4, 346, 223),
                    c(5, 124, 27, 104.3, 133), c(6, 232, 104, 205, 150), c(7, 214, 183, rx, ry)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="400" fill="#ffffff"/>', H.common_defs("f2307")]
    for i, c in enumerate(CARDS):
        x, y, w, h = 8 + c["ox"], 8 + c["oy"], 308, 188
        layers.append(S.card(f"f2307c{c['n']}", x, y, w, h, SKY, ""))
        big, small = CLOUDS[i]
        layers += [{"name": big[0], "at": [c["ox"] + big[1], c["oy"] + big[2]], "width": big[3], "opacity": 0.95},
                   {"name": small[0], "at": [c["ox"] + small[1], c["oy"] + small[2]], "width": small[3], "opacity": 0.85}]
        layers.append(f'<g clip-path="url(#f2307c{c["n"]}c)">{side_view(c, 3 + 7 * i)}</g>')
        layers.append(window(c, 5 + 11 * i))
        layers.append(paths(c))
    layers.append(callouts())
    return {
        "id": "fig-23-07-runway-illusions",
        "replaces": "fig-23-07-runway-illusions.svg",
        "book_file": "plate-23-07-runway-illusions.jpg",
        "caption": "Figure 23-7. Runway width and slope illusions: what you see and where you end up",
        "desc": "Figure 23-7. Runway width and slope illusions: what you see and where you end up",
        "legend": [
            "Narrower than usual: you seem high, fly low, and may land short or hit obstacles.",
            "Wider: you seem low, fly high, and may flare high and land hard or long.",
            "Upsloping runway or terrain: you seem high and fly low.",
            "Downsloping: you seem low and fly high.",
            "Green dashed outline: your usual runway, seen from the correct path.",
            "Green: the correct approach path.",
            "Red: the path you fly if you trust the picture.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-23-07-runway-illusions.svg", "blank": True, "layers": layers},
    }
