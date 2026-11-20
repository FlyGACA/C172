"""Figure 15-2. Flying an approach through a microburst (redrawn in the second design pass as one 3D view).

One render (figs/oeth3d.microburst_15_02; blender/render_oeth.py): the open picture of the desert east of Thumamah on its relief, seen from behind and to the left
of the approach to a generic aerodrome (the plan of 2-4's lower view); the intended 3 degree glide path dashed in green and the path flown in red: above the
glide path in the increasing headwind, pushed down in the downdraft, sinking fast in the increasing tailwind, touching the ground short of the runway; the
base of a cumulonimbus over the approach and a ring of dust raised by the outflow; the aeroplane (the model, enlarged) where it floats. The sky, the virga
and rain shaft and the wind arrows are drawn on the plate. The heights of the paths and of the cloud base are drawn 2.5 times their size."""
import json
import os

from figs import h_b2 as H
from figs import scene as S

n = S.n
W = 640
U = "f1502"
R3D = "microburst-15-02"
PX, PY, PW = 8.0, 8.0, 624.0
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = ("#2F63C8", "#8DB3F2")
GREEN = ("#15803D", "#86EFAC")
RED = ("#B91C1C", "#FCA5A5")


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
    sky = (f'<defs>{S.gradient(U + "sk", [(0, "#4F6079"), (0.5, "#8A9BB2"), (0.92, "#D6CBB6"), (1, "#DED2BC")])}</defs>'
           f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(hy - PY + 30)}" fill="url(#{U}sk)"/>')
    # the storm's base as the render shows it (checked on the built plate): a dark dome over x 318-482 whose underside is near y 58
    (mx, my) = at("mb_ground")
    bx, by, blx, brx = 400.0, 56.0, 330.0, 470.0
    rain = (S.rain(U + "vg", blx, brx, by, by + (my - by) * 0.5, slant=-4, count=50, seed=7, colour="#5A6E95", veil=0.16, bottom=0.0)
            + S.rain(U + "rn", (bx + blx) / 2, (bx + brx) / 2, by, max(my, 224.0), slant=-4, count=70, seed=3, colour="#33508F", veil=0.30, bottom=0.25))
    clip = f'<defs><clipPath id="{U}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{U}c)">'
    img = {"name": R3D, "at": [PX + PW / 2, PY + ph / 2], "width": PW, "whole": True}
    (ha, hay), (hb, hby) = at("head_a"), at("head_b")
    (ta, tay), (tb, tby) = at("tail_a"), at("tail_b")
    (fx, fy), (dx, dy), (sx, sy), (cx, cy) = at("float"), at("down"), at("sink"), at("contact")
    (gx, gy), (thx, thy) = at("gp_mid"), at("thr")
    (dlx, dly), (drx, dry) = at("dust_left"), at("dust_right")
    arrows = "".join([
        S.ribbon(U + "hw", [(hb, hby), ((ha + hb) / 2, (hay + hby) / 2), (ha, hay)], 6.5, *BLUE),
        S.ribbon(U + "dd", [(bx, by + 30), ((bx + dx) / 2, (by + dy) / 2), (dx + 10, dy - 22)], 7.0, *BLUE),
        S.ribbon(U + "tw", [(ta, tay), ((ta + tb) / 2, (tay + tby) / 2), (tb, tby)], 6.5, *BLUE),
        S.ribbon(U + "ol", [(mx - 8, my - 6), ((mx + dlx) / 2, (my + dly) / 2 - 4), (dlx + 6, dly - 4)], 5.0, *BLUE),
        S.ribbon(U + "or", [(mx + 8, my - 6), ((mx + drx) / 2, (my + dry) / 2 - 4), (drx - 6, dry - 4)], 5.0, *BLUE),
    ])
    c = S.callout
    calls = "".join([
        c(1, fx - 10, fy - 46, fx - 4, fy - 10, r=10.5),
        c(2, (bx + dx) / 2 + 40, (by + dy) / 2, (bx + dx) / 2 + 10, (by + dy) / 2, r=10.5),
        c(3, sx + 44, sy - 30, sx + 4, sy - 2, r=10.5),
        c(4, cx + 30, cy + 34, cx, cy, r=10.5),
        c(5, gx - 6, gy + 40, gx, gy + 4, r=10.5),
        c(6, dlx - 30, dly + 32, dlx, dly + 6, r=10.5),
        c(7, thx + 40, thy + 30, thx + 6, thy + 2, r=10.5),
        c(8, brx + 26, by + 40, brx - 10, by + 40, r=10.5),
    ])
    frame = f'</g><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', clip + sky + rain, img, arrows + frame + calls]


def plate():
    return {
        "id": "fig-15-02-microburst",
        "replaces": "fig-15-02-microburst.svg",
        "book_file": "plate-15-02-microburst.jpg",
        "caption": "Figure 15-2. Flying an approach through a microburst",
        "desc": ("Figure 15-2. Flying an approach through a microburst. A 3D view from behind the approach: the intended glide path, and the path flown, which rises above it "
                 "in the increasing headwind, is pushed down in the downdraft, sinks fast in the increasing tailwind and touches the ground short of the runway, under the "
                 "base of a thunderstorm with virga and a rain shaft, and a ring of dust raised by the outflow."),
        "legend": [
            "Increasing headwind: airspeed and lift rise, and the aeroplane floats above the glide path.",
            "Downdraft: the aeroplane is pushed down.",
            "Increasing tailwind: airspeed falls and the aeroplane sinks fast.",
            "Ground contact short of the runway.",
            "Intended glide path.",
            "Outflow raising a ring of dust.",
            "Runway.",
            "Virga and the rain shaft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
