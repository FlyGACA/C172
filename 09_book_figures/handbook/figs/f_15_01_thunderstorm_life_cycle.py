"""Figure 15-1. The three stages of a thunderstorm cell (redrawn in the second design pass as one 3D view).

One render (figs/oeth3d.storm_15_01; blender/render_oeth.py): the open picture of the desert east of Thumamah, seen from the south at about 11 000 ft, with three
clouds of the cloud library side by side, their bases near 5 000 ft above the ground: a towering cumulus (cumulus stage), a cumulonimbus with its anvil
(mature stage), and a spent anvil over a crumbling tower (dissipating stage). Drawn on the plate: the sky, the updrafts and downdrafts, the rain, the hail
falling from under the anvil, the gust front and the freezing level. The nine callouts of the old figure are kept."""
import json
import os

from figs import h_b2 as H
from figs import scene as S

n = S.n
W = 640
U = "f1501"
R3D = "storm-15-01"
PX, PY, PW = 8.0, 8.0, 624.0
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")


def info():
    with open(os.path.join(HERE, "renders", R3D + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ph = PW * h / w
    return (lambda k: (PX + d["anchors"][k][0] * PW, PY + d["anchors"][k][1] * ph)), ph


PH = PW * 1125 / 2000
HT = int(PY + PH + 8)


def layers():
    at, ph = info()
    hx, hy = at("hz")
    sky = (f'<defs>{S.gradient(U + "sk", [(0, "#3A70BC"), (0.6, "#86B4E6"), (1, "#D8E5F1")])}</defs>'
           f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(hy - PY + 20)}" fill="url(#{U}sk)"/>')
    (b0, by), (b1, _), (b2, _) = at("base0"), at("base1"), at("base2")
    (g0, gy), (g1, _), (g2, _) = at("ground0"), at("ground1"), at("ground2")
    (t0x, t0y), (t1x, t1y) = at("top0"), at("top1")
    (fa, fy), (fb, fby) = at("fz_a"), at("fz_b")
    (ax, ay) = at("anvil1")
    rain = (S.rain(U + "r1", b1 + 6, b1 + 46, by - 2, gy, slant=-6, count=44, seed=4, colour="#3A63B4", veil=0.30, bottom=0.4)
            + S.rain(U + "r2", b2 - 34, b2 + 14, by - 2, gy, slant=-4, count=20, seed=6, colour="#4F73B8", veil=0.10, bottom=0.3))
    clip = f'<defs><clipPath id="{U}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{U}c)">'
    img = {"name": R3D, "at": [PX + PW / 2, PY + ph / 2], "width": PW, "whole": True}
    r = S.ribbon
    arrows = "".join([
        r(U + "u1", [(b0 - 14, gy - 4), (b0 - 14, by - 30), (b0 - 12, t0y + 50)], 6.0, *ORANGE),
        r(U + "u2", [(b0 + 10, gy - 4), (b0 + 10, by - 40), (b0 + 12, t0y + 30)], 6.5, *ORANGE),
        r(U + "u3", [(b1 - 30, gy - 4), (b1 - 30, by - 50), (b1 - 26, t1y + 60)], 6.0, *ORANGE),
        r(U + "u4", [(b1 - 12, gy - 4), (b1 - 12, by - 60), (b1 - 8, t1y + 40)], 6.0, *ORANGE),
        r(U + "d1", [(b1 + 18, t1y + 70), (b1 + 18, by - 30), (b1 + 18, gy - 6)], 6.0, *BLUE),
        r(U + "d2", [(b1 + 36, t1y + 90), (b1 + 36, by - 20), (b1 + 36, gy - 6)], 6.0, *BLUE),
        r(U + "gf", [(b1 + 40, gy + 2), (b1 + 66, gy + 4), (b1 + 98, gy + 2)], 5.5, *BLUE),
        r(U + "d3", [(b2 - 24, by - 60), (b2 - 24, by - 20), (b2 - 24, gy - 6)], 5.5, *BLUE),
        r(U + "d4", [(b2 + 4, by - 70), (b2 + 4, by - 24), (b2 + 4, gy - 6)], 5.5, *BLUE),
    ])
    hail = S.hailstones([(ax + 14, ay + 26), (ax + 22, ay + 44), (ax + 12, ay + 60), (ax + 22, ay + 78), (ax + 14, ay + 96), (ax + 24, ay + 114)])
    freeze = S.altitude_line(PX, PX + PW, fy, "#FFFFFF", 0.9, dash="6 5", width=1.4) + S.snowflake(PX + 14, fy)
    c = S.callout
    calls = "".join([
        c(1, b0 - 50, t0y - 6, b0 - 20, t0y + 20, r=10.5),
        c(2, b1 - 100, t1y + 4, b1 - 60, t1y + 30, r=10.5),
        c(3, b2 + 70, at("top2")[1] - 20, b2 + 40, at("top2")[1] + 4, r=10.5),
        c(4, b0 - 52, by - 20, b0 - 22, by - 20, r=10.5),
        c(5, b1 + 70, by - 40, b1 + 42, by - 40, r=10.5),
        c(6, ax + 30, ay - 34, ax + 4, ay - 6, r=10.5),
        c(7, b1 + 108, gy + 22, b1 + 90, gy + 6, r=10.5),
        c(8, ax + 60, ay + 70, ax + 28, ay + 70, r=10.5),
        c(9, PX + PW - 30, fy - 20, PX + PW - 30, fy - 2, r=10.5),
    ])
    frame = f'</g><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', clip + sky, img, rain + arrows + hail + freeze + frame + calls]


def plate():
    return {
        "id": "fig-15-01-thunderstorm-life-cycle",
        "replaces": "fig-15-01-thunderstorm-life-cycle.svg",
        "book_file": "plate-15-01-thunderstorm-life-cycle.jpg",
        "caption": "Figure 15-1. The three stages of a thunderstorm cell",
        "desc": ("Figure 15-1. The three stages of a thunderstorm cell, in one 3D view over the desert: a towering cumulus with updrafts only, a mature cumulonimbus with "
                 "updrafts and downdrafts side by side, heavy rain, hail falling from under its anvil and a gust front on the ground, and a dissipating cell with "
                 "downdrafts only under a spent anvil; one dashed line marks the freezing level."),
        "legend": [
            "Cumulus stage: updrafts only.",
            "Mature stage: updrafts and downdrafts side by side, heavy rain and hail.",
            "Dissipating stage: downdrafts only.",
            "Updraft.",
            "Downdraft with rain.",
            "Anvil.",
            "Gust front: cold outflow spreading along the surface.",
            "Hail falling from under the anvil into clear air.",
            "Freezing level (0 °C).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
