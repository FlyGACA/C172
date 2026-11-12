"""Figure 31-4. A night takeoff: from the runway lights to the instruments. Drawn again as a night scene on the old figure's canvas: a deep-blue sky with stars over ground so dark that the
horizon is lost (the point of the figure), the runway as a band of asphalt between two rows of glowing edge lamps with green threshold and red end lamps, the model's aeroplane by moonlight
lined up, rotating at VR and climbing at VY, each with its landing light as a soft cone (on the runway, then lost in the air), the dashed climb path, and under it a dark instrument panel
with the model's own four instruments (nose 10 degrees up, 75 kt, climbing through 1,200 ft, 700 ft/min up). The ten numbered callouts of the old figure are kept."""
from figs import scene as S
from figs import h_a3 as H
from figs.kit import NIGHT, side_plane

n = S.n
U = "f3104"
SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
HZ = 221.0                                    # the (lost) horizon
GREEN = ("#0F9460", "#7DEBB4")
SH = 3.5                                      # the runway is a band 10 high here (far edge 222, near edge 232): the aeroplanes on it stand 3.5 lower than on the old line

PLANES = [(64, 218 + SH, 0, 54), (250, 217 + SH, -7, 54), (470, 184.2, -9, 54)]


def top_card():
    x, y, w, h = 10, 15, 620, 255
    body = [H.stars(x, y, w, HZ - y, 70, seed=31),
            f'<defs>{S.gradient(U + "gr", [(0, "#0A0F1C"), (1, "#05070D")])}{S.gradient(U + "hz", [(0, "#2C3C6C", 0.0), (0.55, "#2C3C6C", 0.55), (1, "#2C3C6C", 0.0)])}'
            f'<radialGradient id="{U}ag" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.22"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient></defs>'
            f'<rect x="{x}" y="{HZ}" width="{w}" height="{y + h - HZ}" fill="url(#{U}gr)"/>'
            f'<rect x="{x}" y="{HZ - 12}" width="{w}" height="22" fill="url(#{U}hz)"/>'
            f'<ellipse cx="195" cy="{HZ}" rx="200" ry="26" fill="url(#{U}ag)"/>']
    return S.card(U + "c", x, y, w, h, [(0, "#070D22"), (0.5, "#14214A"), (0.84, "#1E2E58"), (1, "#05070D")], "".join(body))


def runway():
    """A band of asphalt with a lamp row on each edge (the far row small, the near row a little larger), green threshold and red end lamps."""
    out = [f'<defs>{S.gradient(U + "as", [(0, "#46526F"), (1, "#1A2133")])}</defs>',
           f'<polygon points="{S.pts([(30, 222), (360, 222), (368, 232.5), (22, 232.5)])}" fill="url(#{U}as)"/>',
           f'<line x1="30" y1="222" x2="360" y2="222" stroke="#9FB0D4" stroke-opacity="0.35" stroke-width="0.8"/>']
    far = [(38 + 22 * i, 222.4) for i in range(15)]
    near = [(31 + 22.8 * i, 232.6) for i in range(16)]
    out.append(H.lamp_row(U, far, "w", 1.55, 0.95))
    out.append(H.lamp_row(U, near, "w", 2.0, 1.05))
    out.append(H.lamp_row(U, [(27, 222.4), (25, 227.4), (22.5, 232.6)], "g", 1.8, 1.1))
    out.append(H.lamp_row(U, [(361, 222.4), (363.5, 227.4), (366, 232.6)], "r", 1.8, 1.1))
    return "".join(out)


def labels():
    return ('<text x="248" y="195" font-family="monospace" font-size="12" fill="#FFFFFF" text-anchor="middle" fill-opacity="0.95">VR 55</text>'
            '<text x="466" y="162.2" font-family="monospace" font-size="12" fill="#FFFFFF" text-anchor="middle" fill-opacity="0.95">VY 75</text>')


def climb_path():
    d = "M 250,222.5 L 560,169.9"
    return (f'<path d="{d}" fill="none" stroke="#BCD0FF" stroke-opacity="0.30" stroke-width="5" stroke-linecap="round" filter="url(#{U}b2)"/>'
            f'<path d="{d}" fill="none" stroke="#DCE6FF" stroke-opacity="0.85" stroke-width="1.4" stroke-dasharray="5 4.2" stroke-linecap="round"/>')


def beams():
    out = [H.beam(U + "bm1", 97, 221.8, 206.0, 227.6, 0.9, 12.5, "#FFF3D2", 0.80, 1.2, U),
           H.beam(U + "bm2", 283, 217.6, 382.0, 223.4, 0.9, 12.0, "#FFF3D2", 0.80, 1.2, U),
           H.beam(U + "bm3", 502, 180.0, 606.0, 166.0, 0.9, 12.0, "#FFF3D2", 0.72, 1.2, U)]
    # the pool of light where the first two reach the runway
    out.append(f'<defs><radialGradient id="{U}pl" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF1C8" stop-opacity="0.55"/><stop offset="1" stop-color="#FFF1C8" stop-opacity="0"/></radialGradient></defs>'
               f'<ellipse cx="178" cy="227.4" rx="38" ry="5.6" fill="url(#{U}pl)"/><ellipse cx="352" cy="227.4" rx="28" ry="5.2" fill="url(#{U}pl)" opacity="0.8"/>')
    return "".join(out)


def panel():
    x, y, w, h = 10, 282, 620, 128
    body = (f'<defs>{S.gradient(U + "pn", [(0, "#232B3D"), (0.5, "#171D2B"), (1, "#0E121C")])}{S.gradient(U + "pg", [(0, "#FFFFFF", 0.10), (1, "#FFFFFF", 0.0)])}</defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{U}pn)"/><rect x="{x}" y="{y}" width="{w}" height="22" fill="url(#{U}pg)"/>'
            f'<line x1="{x}" y1="{y + 1}" x2="{x + w}" y2="{y + 1}" stroke="#7E8DB0" stroke-opacity="0.4" stroke-width="1"/>')
    return S.card(U + "p", x, y, w, h, [(0, "#232B3D"), (1, "#0E121C")], body)


def dials():
    shadow = {"dx": 0.0, "dy": 2.4, "blur": 3.0, "opacity": 0.55}
    return [{"name": nme, "at": [cx, 345], "width": 92, "shadow": shadow} for nme, cx in (("dial-31-04-ai", 110), ("dial-31-04-asi", 250), ("dial-31-04-alt", 390), ("dial-31-04-vsi", 530))]


def altitude_arrow():
    import math
    pts_ = [(390 + 52 * math.cos(math.radians(a)), 345 + 52 * math.sin(math.radians(a))) for a in (-62, -52, -42, -32, -20, -12)]
    return S.ribbon(U + "al", pts_, 4.2, *GREEN, head=2.4)


def callouts():
    c = S.callout
    return "".join([c(1, 54, 173, 62, 211), c(2, 150, 177, 150, 227), c(3, 200, 165, 233, 207), c(4, 400, 136, 448, 180), c(5, 590, 140, 586, 169), c(6, 480, 251, 470, 231),
                    c(7, 48, 309, 80, 318), c(8, 188, 309, 220, 318), c(9, 328, 309, 360, 318), c(10, 468, 309, 500, 318)])


def plate():
    planes = [side_plane(cx, cy, ang, 1.1, SILHOUETTE, grow=1.45, look=NIGHT) for cx, cy, ang, _w in PLANES]
    layers = ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U), top_card(), runway(), climb_path(), beams(), planes[0], planes[1], planes[2],
              labels(), panel(), *dials(), altitude_arrow(), callouts()]
    return {
        "id": "fig-31-04-night-takeoff",
        "replaces": "fig-31-04-night-takeoff.svg",
        "book_file": "plate-31-04-night-takeoff.jpg",
        "caption": "Figure 31-4. A night takeoff: from the runway lights to the instruments",
        "desc": "Figure 31-4. A night takeoff: from the runway lights to the instruments",
        "legend": [
            "Lined up; heading indicator checked; landing and taxi lights on.",
            "Accelerate straight between the edge lights.",
            "Rotate at `VR`, 55 kt (example aeroplane).",
            "After liftoff nothing ahead: eyes to the attitude indicator.",
            "Climb at `VY`, 75 kt (example aeroplane); the landing light no longer reaches the ground.",
            "Dark ground: no horizon.",
            "Attitude: climb, wings level.",
            "Airspeed: 75 kt.",
            "Altimeter: increasing.",
            "Vertical speed: climbing.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-31-04-night-takeoff.svg", "blank": True, "layers": layers},
    }
