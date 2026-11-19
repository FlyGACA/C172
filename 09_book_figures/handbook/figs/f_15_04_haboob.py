"""Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow (redrawn in the second design pass as one 3D view).

One render (figs/oeth3d.haboob_15_04; blender/render_oeth.py): the open picture of the desert east of Thumamah on its relief, seen from the south-west at about
2 000 ft; a cumulonimbus of the cloud library with a high base, and nearer, a wall of dust (billowing towers of the library tinted the colour of the sand)
rolling west towards a generic aerodrome (the plan of 2-4's lower view) in its path. The sky, the rain under the storm and the arrows are drawn on the plate:
the downdraft, the cold outflow along the ground, the warm air forced up at the gust front, the direction of movement. The eight callouts of the old figure
are kept. The places are generic."""
import json
import os

from figs import h_b2 as H
from figs import scene as S

n = S.n
W = 640
U = "f1504"
R3D = "haboob-15-04"
PX, PY, PW = 8.0, 8.0, 624.0
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORANGE = ("#D2691E", "#F3B676")
BLUE = ("#2F63C8", "#8DB3F2")
INK = ("#1F2937", "#667489")


def info():
    with open(os.path.join(HERE, "renders", R3D + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ph = PW * h / w
    return (lambda k: (PX + d["anchors"][k][0] * PW, PY + d["anchors"][k][1] * ph)), ph


_, PH = info() if os.path.exists(os.path.join(HERE, "renders", R3D + ".anchors.json")) else (None, PW * 1125 / 2000)
HT = int(PY + PH + 8)


def layers():
    at, ph = info()
    hx, hy = at("hz")
    sky = (f'<defs>{S.gradient(U + "sk", [(0, "#56677F"), (0.55, "#93A1B3"), (0.9, "#D2BE9C"), (1, "#DCC7A2")])}</defs>'
           .replace('x2="1" y2="0"', 'x2="0" y2="1"')
           + f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(hy - PY + 30)}" fill="url(#{U}sk)"/>')
    (bx, by), (gx, gy) = at("cb_base"), at("rain_ground")
    rain = S.rain(U + "rn", bx - 70, bx + 50, by + 4, gy, slant=-7, count=60, seed=3, colour="#33508F", veil=0.32, bottom=0.2)
    clip = f'<defs><clipPath id="{U}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{U}c)">'
    img = {"name": R3D, "at": [PX + PW / 2, PY + ph / 2], "width": PW, "whole": True}
    (tx, ty), (fx, fy), (mx, my) = at("wall_top"), at("wall_foot"), at("wall_mid")
    (oax, oay), (obx, oby) = at("outflow_a"), at("outflow_b")
    (rx, ry), (cx, cy) = at("rwy"), at("cb")
    (flx, fly), (frx, fry) = at("front_left"), at("front_right")
    arrows = "".join([
        S.ribbon(U + "d1", [(bx - 30, by + 6), (bx - 34, (by + ty) / 2 + 10), (bx - 40, ty - 6)], 6.5, *BLUE),
        S.ribbon(U + "d2", [(bx + 14, by + 6), (bx + 12, (by + ty) / 2 + 10), (bx + 8, ty - 6)], 6.5, *BLUE),
        S.ribbon(U + "o1", [(oax, oay - 4), ((oax + obx) / 2, (oay + oby) / 2 - 2), (obx, oby)], 7.0, *BLUE),
        S.ribbon(U + "u1", [(fx - 18, fy - 6), (fx - 22, (fy + ty) / 2), (tx - 10, ty - 22)], 7.0, *ORANGE),
        S.ribbon(U + "u2", [(fx + 30, fy - 8), (fx + 28, (fy + ty) / 2 - 4), (tx + 34, ty - 26)], 6.0, *ORANGE),
        S.ribbon(U + "mv", [(tx + 60, ty - 70), (tx, ty - 70), (tx - 70, ty - 70)], 6.0, *INK),
    ])
    c = S.callout
    calls = "".join([
        c(1, cx + 90, cy - 20, cx + 30, cy, r=10.5),
        c(2, bx + 54, (by + ty) / 2, bx + 16, (by + ty) / 2, r=10.5),
        c(3, (oax + obx) / 2 + 10, max(oay, oby) + 36, (oax + obx) / 2, (oay + oby) / 2, r=10.5),
        c(4, flx - 34, fly + 30, flx, fly, r=10.5),
        c(5, mx - 70, my - 6, mx - 20, my, r=10.5),
        c(6, tx - 96, ty - 70, tx - 78, ty - 70, r=10.5),
        c(7, rx - 30, ry + 34, rx, ry, r=10.5),
        c(8, fx - 70, (fy + ty) / 2 - 20, fx - 24, (fy + ty) / 2, r=10.5),
    ])
    frame = f'</g><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', clip + sky + rain, img, arrows + frame + calls]


def plate():
    return {
        "id": "fig-15-04-haboob",
        "replaces": "fig-15-04-haboob.svg",
        "book_file": "plate-15-04-haboob.jpg",
        "caption": "Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow",
        "desc": ("Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow. A 3D view over the desert: a thunderstorm with rain falling from its base, the cold "
                 "outflow spreading along the ground, a wall of dust rising at the gust front, and an aerodrome in its path."),
        "legend": [
            "Thunderstorm.",
            "Cold downdraft with heavy rain.",
            "Cold, dense outflow spreading along the surface.",
            "Gust front: sudden wind shift and strong gusts.",
            "Wall of dust.",
            "Direction of movement.",
            "An aerodrome in its path.",
            "Warmer air forced up at the gust front, carrying dust aloft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
