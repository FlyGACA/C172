"""Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind. Drawn again on an aerial view of the country (figs/terrain.py): the station a hexagonal white
building with a dome, the 060 radial a blue course ribbon with a casing, the 120 radial a ray of light, the track of the aeroplane a dark ribbon (the 015 leg, the lead and the turn onto
the radial), the aeroplanes of the model, the wind a green ribbon, and the three displays and the OBS window as lit instrument cards. The geometry of the old figure is kept
(figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-21-03", size=(2560, 1640), seed=213, kind="plain", features=("scrub", "wadis", "tracks"), veil=0.3, soft=2.6)

STN = (96.0, 300.0)


def track_points():
    """The aeroplane's track: the straight leg on heading 015 (from the 120 radial), then the turn of radius 39 onto the radial."""
    pts = [(225.9, 375.0), (247.6, 294.1), (269.3, 213.2)]
    cx, cy = 269.3 + 39 * math.cos(math.radians(15)), 213.2 + 39 * math.sin(math.radians(15))
    for phi in (285.0, 296.25, 307.5, 318.75, 330.0):
        pts.append((cx + 39 * math.sin(math.radians(phi)), cy - 39 * math.cos(math.radians(phi))))
    return pts[:3] + pts[4:]


def plate():
    st = H.vor_top("a3s", STN[0], STN[1], 1.2)
    layers = [{"name": "terrain-21-03", "at": [320, 205], "width": 640}]
    # the 120 radial: a ray of light from the station to the aeroplane's starting point
    layers.append(H.rays("a3y", STN[0], STN[1], [120], 20, 160, w0=1.4, w1=3.6, a0=1.0, a1=0.75, glow=5.6, glow_opacity=0.62))
    # dotted threads from the three places to their displays
    layers.append(H.dotted([(239.9, 375.0), (512, 330.5)]) + H.dotted([(279.3, 213.2), (512, 235.0)]) + H.dotted([(382.8, 146.5), (512, 140.0)]))
    # the 060 radial, the track, the wind
    layers.append(H.ribbon("a3t", track_points(), width=3.8, colours=("#1B2433", "#586377"), head=1.0, arrow=False, casing=1.8, per=10))
    layers.append(H.ribbon("a3r", [(96 + 24 * math.sin(math.radians(60)), 300 - 24 * math.cos(math.radians(60))), (480.0, 78.5)], width=5.8, colours=H.BLUE, head=2.1))
    layers.append(H.ribbon("a3w", [(298.8, 72.5), (321.8, 112.3)], width=5.0, colours=H.GREEN, head=2.2, casing=1.8))
    # the heading ahead of the aeroplane on the radial, the 15 degree line through the turn point and the 45 degree angle
    layers.append(H.halo_line(368.8, 142.5, 424.0, 99.4, "#1F2937", 1.4, "4 3"))
    layers.append(H.halo_line(269.3, 213.2, 273.5, 197.5, "#1F2937", 1.4, "4 3"))
    layers.append(H.halo_line(273.5, 197.5, 287.9, 143.5, "#B45309", 1.5, "3 3"))
    layers.append(H.halo_path("M284.3,157.0 A42.0,42.0 0 0,1 309.8,176.5", "#B45309", 2.1))
    layers.append(H.text(310.5, 155.5, "45°", 13.5, "#B45309", "bold", "middle", halo="#FFFFFF"))
    layers.append(st)
    # the aeroplanes: at the start on the 120 radial (heading 015) and on the radial (heading 052)
    layers.append(H.plane(228.0, 376.3, 54, 15))
    layers.append(H.plane(368.5, 142.7, 54, 52))
    # the displays: three course deviation bars and the OBS window
    layers.append(H.cdi("a3d1", 512, 313, 96, 35, -5))
    layers.append(H.cdi("a3d2", 512, 218, 96, 35, -2))
    layers.append(H.cdi("a3d3", 512, 123, 96, 35, 0))
    layers.append(H.glass("a3o", 512, 60, 96, 34, r=7))
    layers.append(H.text(541, 82.5, "060", 14, "#FFFFFF", "bold", "middle"))
    layers.append('<polygon points="565,86 559.5,77.5 570.5,77.5" fill="#FFFFFF"/>')
    layers.append(H.text(588, 82, "FR", 11.5, "#FFFFFF", "bold", "middle", mono=True))
    c = S.callout
    layers.append("".join([
        c(1, 62, 262, 84, 284), c(2, 266, 392, 244, 380), c(3, 212, 306, 239, 314), c(4, 306, 240, 275, 215),
        c(5, 350, 108, 361, 132), c(6, 276, 64, 301, 78), c(7, 622, 77, 608, 77),
    ]))
    return {
        "id": "fig-21-03-intercept",
        "replaces": "fig-21-03-intercept.svg",
        "book_file": "plate-21-03-intercept.jpg",
        "caption": "Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind",
        "desc": "Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind",
        "legend": [
            "The station; the OBS stays on 060.",
            "On the 120 radial, 10 NM out: needle full scale left.",
            "Heading 015: a 45° intercept angle.",
            "Lead the turn as the needle leaves full scale: here about 2 dots, with the radial 3° to 4° away.",
            "On the radial, needle centred, heading 052.",
            "Wind 330° at 15 kt.",
            "All three displays: OBS 060, `FR`.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-21-03-intercept.svg", "blank": True, "layers": layers},
    }
