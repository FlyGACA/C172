"""Figure 12-3. Moving a passenger forward moves the CG forward. The old figure's two scenes drawn as a balance on drafting paper: the beam (an aluminium bar, broken between the datum and
2 m, running off to the right) with the rest of the loaded aeroplane as a solid blue block (1 001 kg), the 95 kg passenger as a solid amber block (at the rear seat, 3.25 m, above; moved to
the front seat, 2.30 m, below, his old place dashed), the steel wedge of the balance point under the beam (CG 2.540 m above, 2.458 m below), the orange arrow of the move (0.95 m) and the
measure of the change in CG (0.082 m), all at the old figure's positions and with its numbers; the datum as a glowing orange plumb line. The eight numbered callouts are kept."""
from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f1203"
ORANGE = ("#E8782E", "#F8BE73")
INK = "#334155"


def gradients():
    g = S.gradient
    return ("<defs>"
            + g(U + "beam", [(0, "#F1F4F9"), (0.45, "#C3CCDA"), (1, "#7F8CA3")])
            + g(U + "blue", [(0, "#D7E6FF"), (0.5, "#8DB5F4"), (1, "#4E83DC")]) + g(U + "bluet", [(0, "#EEF4FF"), (1, "#B9D1FA")]) + g(U + "blues", [(0, "#4E83DC"), (1, "#2B58B0")], 0, 0, 1, 0)
            + g(U + "amber", [(0, "#FFE9A8"), (0.5, "#F8B63A"), (1, "#D9860C")]) + g(U + "ambert", [(0, "#FFF4D2"), (1, "#FCD785")]) + g(U + "ambers", [(0, "#D9860C"), (1, "#A55E04")], 0, 0, 1, 0)
            + g(U + "steel", [(0, "#FFFFFF"), (0.5, "#C3CCDA"), (1, "#6B7890")], 0, 0, 1, 0) + g(U + "steelv", [(0, "#E4EAF3"), (1, "#8794AA")])
            + g(U + "datum", [(0, "#FFC06A"), (0.5, "#F08A12"), (1, "#C26106")], 0, 0, 1, 0)
            + "</defs>")


def paper():
    body = ("".join(f'<line x1="8" y1="{yy}" x2="632" y2="{yy}" stroke="#B9C6DB" stroke-opacity="0.35" stroke-width="0.6"/>' for yy in range(20, 352, 20))
            + "".join(f'<line x1="{xx}" y1="8" x2="{xx}" y2="352" stroke="#B9C6DB" stroke-opacity="0.35" stroke-width="0.6"/>' for xx in range(20, 632, 40)))
    return S.card(U + "c", 8, 8, 624, 344, [(0, "#FBFCFE"), (1, "#E9EFF7")], body)


def datum():
    return (f'<line x1="40" y1="40" x2="40" y2="336" stroke="#FFB45A" stroke-opacity="0.35" stroke-width="9" stroke-linecap="round" filter="url(#{U}b2)"/>'
            f'<rect x="37.8" y="40" width="4.4" height="296" rx="2.2" fill="url(#{U}datum)" stroke="#8F4300" stroke-width="0.6"/>'
            f'<rect x="38.8" y="42" width="1.2" height="292" rx="0.6" fill="#FFFFFF" fill-opacity="0.55"/>')


def beam(y):
    """The beam: two pieces of aluminium bar (one short by the datum, one running off to the right) with the cut ends slanted where it is broken, bolts along it."""
    h = 8.0
    left = [(40, y), (66, y), (62, y + h), (40, y + h)]
    right = [(84, y), (632, y), (632, y + h), (80, y + h)]
    out = [f'<polygon points="{S.pts(left)}" fill="#14233F" fill-opacity="0.2" transform="translate(1 2.6)" filter="url(#{U}b1)"/><polygon points="{S.pts(right)}" fill="#14233F" fill-opacity="0.2" transform="translate(1 2.6)" filter="url(#{U}b1)"/>']
    for poly in (left, right):
        out.append(f'<polygon points="{S.pts(poly)}" fill="url(#{U}beam)" stroke="#5E6B82" stroke-width="0.9" stroke-linejoin="round"/>')
    out.append(f'<rect x="41" y="{n(y + 0.8)}" width="22" height="1.4" rx="0.7" fill="#FFFFFF" fill-opacity="0.75"/><rect x="86" y="{n(y + 0.8)}" width="544" height="1.4" rx="0.7" fill="#FFFFFF" fill-opacity="0.75"/>')
    out.append("".join(f'<circle cx="{xx}" cy="{n(y + h / 2)}" r="1.2" fill="#5E6B82"/>' for xx in range(100, 630, 48)))
    return "".join(out)


def block(uid, x, y, w, h, kind, label, size=11, bold=False, depth=7.0):
    """A solid block standing on its base line at y + h: the front face, a lit top and a shaded side, a soft shadow, its number on the front."""
    grad, top, side, edge = (("blue", "bluet", "blues", "#1E40AF") if kind == "blue" else ("amber", "ambert", "ambers", "#B45309"))
    dy = depth * 0.72
    tcol = "#FFFFFF" if bold else INK
    weight = 'font-weight="bold" ' if bold else ""
    rim = ' stroke="#8A4B00" stroke-width="0.6" stroke-opacity="0.6"' if bold else ""
    ty = y + h / 2 + size * 0.36 + (4 if size < 12 else 0)
    return (f'<ellipse cx="{n(x + w / 2 + depth / 2)}" cy="{n(y + h + 1)}" rx="{n(w / 2 + depth)}" ry="2.6" fill="#14233F" fill-opacity="0.28" filter="url(#{U}b1)"/>'
            f'<polygon points="{S.pts([(x, y), (x + depth, y - dy), (x + w + depth, y - dy), (x + w, y)])}" fill="url(#{U}{top})" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<polygon points="{S.pts([(x + w, y), (x + w + depth, y - dy), (x + w + depth, y + h - dy), (x + w, y + h)])}" fill="url(#{U}{side})" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="1.6" fill="url(#{U}{grad})" stroke="{edge}" stroke-width="1.3"/>'
            f'<rect x="{n(x + 2)}" y="{n(y + 2)}" width="{n(w - 4)}" height="{n(2.2)}" rx="1.1" fill="#FFFFFF" fill-opacity="0.55"/>'
            f'<text x="{n(x + w / 2)}" y="{n(ty)}" font-family="sans-serif" font-size="{size}" {weight}fill="{tcol}" text-anchor="middle"{rim}>{label}</text>')


def ghost(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="#F8B63A" fill-opacity="0.14" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.85"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="none" stroke="#D9860C" stroke-width="1.8" stroke-dasharray="4 3"/>')


def fulcrum(apex_x, apex_y, base_y, half):
    """The balance point: a steel wedge under the beam on a base plate."""
    pts_ = [(apex_x, apex_y), (apex_x + half, base_y), (apex_x - half, base_y)]
    return (f'<polygon points="{S.pts(pts_)}" fill="#14233F" fill-opacity="0.22" transform="translate(1.4 2.4)" filter="url(#{U}b1)"/>'
            f'<polygon points="{S.pts(pts_)}" fill="url(#{U}steel)" stroke="#4B586E" stroke-width="1.2" stroke-linejoin="round"/>'
            f'<rect x="{n(apex_x - half - 10)}" y="{base_y}" width="{n(2 * half + 20)}" height="4" rx="1.4" fill="url(#{U}steelv)" stroke="#4B586E" stroke-width="0.9"/>')


def text(x, y, s, colour=INK, size=12, anchor="middle"):
    return f'<text x="{n(x)}" y="{n(y)}" font-family="sans-serif" font-size="{size}" fill="{colour}" text-anchor="{anchor}" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">{s}</text>'


def scenes():
    out = []
    # above: the passenger at the rear seat, the balance point at 2.540 m
    out.append(beam(110))
    out.append(fulcrum(326.1, 118, 140, 12))
    out.append(block(U + "a", 277.2, 48, 44, 62, "blue", "1 001", 11))
    out.append(block(U + "b", 595, 80, 30, 30, "amber", "95", 12, True, 6.0))
    out.append(text(610, 134, "3.25"))
    # below: the passenger moved to the front seat, the balance point at 2.458 m
    out.append(beam(262))
    out.append(ghost(595, 232, 30, 30))
    out.append(fulcrum(293.2, 270, 292, 12))
    out.append(block(U + "c", 277.2, 200, 44, 62, "blue", "1 001", 11))
    out.append(block(U + "d", 215, 232, 30, 30, "amber", "95", 12, True, 6.0))
    out.append(text(230, 286, "2.30"))
    out.append(S.ribbon(U + "mv", [(592, 216), (430, 216), (257, 216)], 5.4, *ORANGE, head=2.4))
    out.append(text(510, 207, "0.95", "#C2570C"))
    # the change in CG
    out.append(f'<line x1="326.1" y1="142" x2="326.1" y2="322" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.8"/><line x1="326.1" y1="142" x2="326.1" y2="322" stroke="#5A6A86" stroke-width="1.2" stroke-dasharray="3 3"/>'
               f'<line x1="293.2" y1="298" x2="293.2" y2="322" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.8"/><line x1="293.2" y1="298" x2="293.2" y2="322" stroke="#5A6A86" stroke-width="1.2" stroke-dasharray="3 3"/>')
    out.append(S.ribbon(U + "dc", [(326.1, 316), (310, 316), (293.2, 316)], 4.4, "#1F2937", "#667489", head=2.3))
    out.append(text(334.1, 320, "0.082", INK, 12, "start"))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 40, 26), c(2, 341.2, 62), c(3, 574, 66), c(4, 194, 244), c(5, 352.1, 128), c(6, 256.2, 282), c(7, 390, 196), c(8, 396.1, 316)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', H.common_defs(U), gradients(), paper(), datum(), scenes(), callouts()]
    return {
        "id": "fig-12-03-shifting-mass",
        "replaces": "fig-12-03-shifting-mass.svg",
        "book_file": "plate-12-03-shifting-mass.jpg",
        "caption": "Figure 12-3. Moving a passenger forward moves the CG forward",
        "desc": "Figure 12-3. Moving a passenger forward moves the CG forward",
        "legend": [
            "The datum. The beam is broken between the datum and 2 m.",
            "The rest of the loaded aeroplane: 1 001 kg with its own CG at 2.473 m.",
            "The 95 kg passenger in a rear seat, at 3.25 m.",
            "The same passenger in the front seat, at 2.30 m.",
            "Balance point before the move: CG 2.540 m.",
            "Balance point after the move: CG 2.458 m.",
            "Distance moved, 0.95 m.",
            "Change in CG, 0.082 m forward.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-12-03-shifting-mass.svg", "blank": True, "layers": layers},
    }
