"""Figure 31-7. Judging the flare at night, with the landing light and without it. Three night scenes on the old figure's canvas. Above: the approach with the landing light on, the
model's aeroplane (by moonlight) high on final with a cone that does not reach the ground and lower with a cone that lights the runway (a pool of light with the tyre marks in it), the
dashed path down to the touchdown ring, runway edge lamps along the band of asphalt. Below left: the same approach without the landing light, the sight lines (grey to the cowling's
line, red dashed to the far-end lights) and the dashed flare path. Below right: the view over the cowling, the two rows of edge lamps running to the red bar of the far-end lights, the
dark hump of the cowling with the dashed line of its top. The eight numbered callouts of the old figure are kept (5 and 6 appear in the windscreen view too, as before)."""
import math

from figs import scene as S
from figs import h_a3 as H
from figs.kit import NIGHT, side_plane

n = S.n
U = "f3107"
SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
SKY = [(0, "#070D22"), (0.55, "#14214A"), (0.86, "#1E2E58"), (1, "#05070D")]
PATH_A = [(40.0, 67.0), (150.0, 110.0), (300.0, 146.0), (360.0, 160.0), (410.0, 166.0), (450.0, 169.0)]
PATH_B = [(40.0, 295.0), (100.0, 327.0), (150.0, 347.0), (230.0, 369.0), (290.0, 380.0), (340.0, 384.0)]


def night_card(uid, x, y, w, h, horizon, seed, stars=44, extra="", sky=None):
    body = [H.stars(x, y, w, horizon - y, stars, seed=seed),
            f'<defs>{S.gradient(uid + "gr", [(0, "#0A0F1C"), (1, "#05070D")])}{S.gradient(uid + "hz", [(0, "#2C3C6C", 0.0), (0.55, "#2C3C6C", 0.5), (1, "#2C3C6C", 0.0)])}</defs>'
            f'<rect x="{x}" y="{horizon}" width="{w}" height="{y + h - horizon}" fill="url(#{uid}gr)"/><rect x="{x}" y="{horizon - 10}" width="{w}" height="20" fill="url(#{uid}hz)"/>', extra]
    return S.card(uid + "c", x, y, w, h, sky or SKY, "".join(body))


def band(uid, x0, x1, far_y, near_y, lamps_far, lamps_near, overshoot=6):
    """The runway as a band of asphalt (far edge, near edge) with a row of lamps along each."""
    out = [f'<defs>{S.gradient(uid + "as", [(0, "#46526F"), (1, "#1A2133")])}</defs>',
           f'<polygon points="{S.pts([(x0, far_y), (x1, far_y), (x1 + overshoot, near_y), (x0 - overshoot, near_y)])}" fill="url(#{uid}as)"/>',
           f'<line x1="{x0}" y1="{far_y}" x2="{x1}" y2="{far_y}" stroke="#9FB0D4" stroke-opacity="0.35" stroke-width="0.8"/>']
    out.append(H.lamp_row(U, lamps_far, "w", 1.5, 0.95))
    out.append(H.lamp_row(U, lamps_near, "w", 1.95, 1.05))
    return "".join(out)


def dashed_path(points, uid, glow=True):
    pts_ = S.catmull(points, 10)
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in pts_)
    return ((f'<path d="{d}" fill="none" stroke="#BCD0FF" stroke-opacity="0.28" stroke-width="5" stroke-linecap="round" filter="url(#{U}b2)"/>' if glow else "")
            + f'<path d="{d}" fill="none" stroke="#DCE6FF" stroke-opacity="0.9" stroke-width="1.5" stroke-dasharray="6 4.2" stroke-linecap="round"/>')


def nose_of(o):
    a = math.radians(o.get("angle", 0.0))
    return o["at"][0] + o["width"] / 2 * math.cos(a), o["at"][1] + o["width"] / 2 * math.sin(a)


def panel_a():
    x, y, w, h = 10, 12, 620, 195
    hz = 171.0
    glow = (f'<defs><radialGradient id="{U}ag" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.22"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="420" cy="{hz}" rx="230" ry="24" fill="url(#{U}ag)"/>')
    return night_card(U + "A", x, y, w, h, hz, 71, 70, glow + band(U + "A", 210, 630, 172, 181.2, [(216 + 22 * i, 171.7) for i in range(19)], [(210 + 23.4 * i, 181.6) for i in range(18)]))


def pad_a():
    """The beam's pool on the runway and the surface it shows: a lit patch with the dark streaks of tyre marks."""
    out = [f'<defs><radialGradient id="{U}pa" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF1C8" stop-opacity="0.8"/><stop offset="0.7" stop-color="#FFF1C8" stop-opacity="0.35"/><stop offset="1" stop-color="#FFF1C8" stop-opacity="0"/></radialGradient></defs>',
           f'<ellipse cx="405" cy="176.6" rx="40" ry="8.4" fill="url(#{U}pa)"/>']
    for i, (x0, y0) in enumerate([(384, 174.5), (394, 177.2), (404, 174.5), (414, 177.2), (424, 174.5)]):
        out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0 + 8}" y2="{y0}" stroke="#2A3248" stroke-opacity="0.85" stroke-width="1.5" stroke-linecap="round"/>')
    return "".join(out)


def panel_b():
    x, y, w, h = 10, 222, 400, 195
    hz = 385.0
    return night_card(U + "B", x, y, w, h, hz, 72, 46, band(U + "B", 150, 410, 387, 395.6, [(156 + 22 * i, 386.4) for i in range(12)], [(151 + 23.6 * i, 396) for i in range(11)]) + dashed_path(PATH_B, U + "pb"))


def sight_lines():
    return (f'<line x1="156" y1="342" x2="405" y2="363.8" stroke="#E6ECFA" stroke-opacity="0.85" stroke-width="1.3"/>'
            f'<line x1="156" y1="342" x2="396" y2="352.2" stroke="#FF5A48" stroke-opacity="0.35" stroke-width="5" stroke-linecap="round" filter="url(#{U}b2)"/>'
            f'<line x1="156" y1="342" x2="396" y2="352.2" stroke="#FF7C6C" stroke-width="2" stroke-dasharray="6 4"/>'
            f'<polygon points="404,353 394.8,357.6 395.2,347.7" fill="#FF7C6C" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="0.8" stroke-linejoin="round"/>')


def panel_c():
    x, y, w, h = 425, 222, 205, 195
    hz = 278.0
    sky = [(0, "#060B1E"), (0.14, "#0E1A3E"), (0.27, "#2A3C6E"), (0.2875, "#34467A"), (0.29, "#05070D"), (1, "#05070D")]
    out = [night_card(U + "C", x, y, w, h, hz, 73, 46, sky=sky)]
    out.append(f'<defs>{S.gradient(U + "cr", [(0, "#38425F"), (1, "#141A2A")])}<radialGradient id="{U}cg" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFC27A" stop-opacity="0.30"/><stop offset="1" stop-color="#FFC27A" stop-opacity="0"/></radialGradient></defs>'
               f'<ellipse cx="527.5" cy="320" rx="86" ry="30" fill="url(#{U}cg)"/>'
               f'<polygon points="{S.pts([(517, 318), (538, 318), (612, 400), (443, 400)])}" fill="url(#{U}cr)" opacity="0.95"/>'
               f'<line x1="433" y1="{hz}" x2="622" y2="{hz}" stroke="#8FA0C8" stroke-opacity="0.5" stroke-width="1"/>')
    left = [(517.5, 318, 1.2), (508.8, 328, 1.4), (500, 338, 1.6), (491.2, 348, 1.8), (482.5, 358, 2.0), (473.8, 368, 2.2), (465, 378, 2.4), (456.2, 388, 2.6), (447.5, 398, 2.8)]
    for lx, ly, r in left:
        out.append(H.lamp(U, lx, ly, "w", r, 1.0) + H.lamp(U, 1055 - lx, ly, "w", r, 1.0))
    out.append("".join(H.lamp(U, 517.9 + 2.4 * i, 318, "r", 0.95, 0.9) for i in range(9)))
    # the cowling: a dark hump with a faint rim of light along its top edge
    hump = "M 425 417 L 425 350 Q 527.5 322 630 350 L 630 417 Z"
    out.append(f'<defs>{S.gradient(U + "cw", [(0, "#171C28"), (1, "#080B12")])}<clipPath id="{U}cc"><rect x="425" y="222" width="205" height="195" rx="9"/></clipPath></defs>'
               f'<g clip-path="url(#{U}cc)"><path d="{hump}" fill="url(#{U}cw)"/><path d="M 425 350 Q 527.5 322 630 350" fill="none" stroke="#7E92C6" stroke-opacity="0.55" stroke-width="1.2"/>'
               f'<path d="M 428 354 Q 527.5 327 627 354" fill="none" stroke="#7E92C6" stroke-opacity="0.18" stroke-width="3" filter="url(#{U}b2)"/></g>'
               f'<line x1="433" y1="334" x2="622" y2="334" stroke="#C9D3EA" stroke-opacity="0.85" stroke-width="1.2" stroke-dasharray="4 3"/>')
    return "".join(out)


def beams(p1, p3):
    n1, n3 = nose_of(p1), nose_of(p3)
    out = [H.beam(U + "bm1", n1[0] - 2, n1[1] + 0.6, 258.0, 147.0, 0.9, 11.0, "#FFF3D2", 0.78, 1.3, U),
           H.beam(U + "bm3", n3[0] - 2, n3[1] + 0.6, 408.0, 172.0, 0.9, 12.5, "#FFF3D2", 0.85, 1.3, U)]
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 140, 72, 156, 102), c(2, 408, 122, 404, 172), c(3, 280, 106, 303, 138), c(4, 470, 132, 452, 165),
                    c(5, 305, 374, 305, 357), c(6, 360, 308, 360, 349), c(7, 250, 357, 262, 374.6), c(8, 60, 377, 158, 385),
                    c(6, 608, 292, 539.5, 316), c(5, 447, 372, 466, 336)])


def plate():
    p3 = side_plane(300, 146, 4, 1.1, SILHOUETTE, grow=1.45, look=NIGHT)
    p1 = side_plane(150, 110, 7, 1.1, SILHOUETTE, grow=1.45, look=NIGHT)
    p2 = side_plane(150, 347, 4, 1.1, SILHOUETTE, grow=1.45, look=NIGHT)
    layers = ['<rect x="0" y="0" width="640" height="430" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U), panel_a(), dashed_path(PATH_A, U + "pa"), beams(p1, p3), pad_a(), p1, p3,
              f'<circle cx="450" cy="170" r="6.5" fill="#FFFFFF" fill-opacity="0.22" filter="url(#{U}b2)"/><circle cx="450" cy="170" r="5" fill="none" stroke="#FFFFFF" stroke-width="2"/>',
              panel_b(), sight_lines(), p2, panel_c(), callouts()]
    return {
        "id": "fig-31-07-night-flare",
        "replaces": "fig-31-07-night-flare.svg",
        "book_file": "plate-31-07-night-flare.jpg",
        "caption": "Figure 31-7. Judging the flare at night, with the landing light and without it",
        "desc": "Figure 31-7. Judging the flare at night, with the landing light and without it",
        "legend": [
            "Higher on final: the beam does not reach the ground.",
            "The beam shows the surface and tyre marks: round out.",
            "Hold the approach descent until this point.",
            "Throttle closed gradually as the wheels touch.",
            "Nose reference, the top of the cowling.",
            "Far-end lights rise above the nose: round out.",
            "Hold the landing attitude; feel for the runway with small power and pitch changes.",
            "Runway edge lights.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {"svg": "fig-31-07-night-flare.svg", "blank": True, "layers": layers},
    }
