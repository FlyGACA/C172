"""Figure 15-7. Mechanical turbulence, mountain wave and rotor (redrawn in the second design pass as one 3D view).

One render (figs/oeth3d.wave_15_06; blender/render_oeth.py): the open picture of the desert east of Thumamah on its relief, seen from the south-east, with a
ridge laid on it (the scene has no mountain; 1 500 m high and 7 km wide at its foot), two piles of lens-shaped clouds of the cloud library over the crests of
the standing wave downwind of it, roll clouds under the crests where the rotors are, and the generic aerodrome of 2-4's lower view. Drawn on the plate: the
sky, the wind, the rising and sinking air on the two slopes, the airstream as a wave, and the eddies by the buildings. The eight callouts are kept."""
import json
import os

from figs import h_b2 as H
from figs import scene as S

n = S.n
W = 640
U = "f1506"
R3D = "wave-15-06"
PX, PY, PW = 8.0, 8.0, 624.0
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")
INK = ("#1F2937", "#667489")


def info():
    with open(os.path.join(HERE, "renders", R3D + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ph = PW * h / w
    return (lambda k: (PX + d["anchors"][k][0] * PW, PY + d["anchors"][k][1] * ph)), ph


PH = PW * 1125 / 2000
HT = int(PY + PH + 8)


def stream(pts, dy, op):
    d = "M" + " L".join(f"{n(x)} {n(y + dy)}" for x, y in S.catmull(pts, 12))
    return f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'


def eddy(cx, cy, r):
    return (f'<path d="M{n(cx - r)} {n(cy)} a{n(r)} {n(r * 0.7)} 0 1 1 {n(r * 1.4)} {n(-r * 0.5)}" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>'
            f'<path d="M{n(cx + r * 0.4)} {n(cy - r * 0.5)} l3 -4 l1 5 z" fill="#FFFFFF"/>')


def layers():
    at, ph = info()
    hx, hy = at("hz")
    sky = (f'<defs>{S.gradient(U + "sk", [(0, "#3A70BC"), (0.6, "#86B4E6"), (1, "#D8E5F1")])}</defs>'
           f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(hy - PY + 20)}" fill="url(#{U}sk)"/>')
    clip = f'<defs><clipPath id="{U}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{U}c)">'
    img = {"name": R3D, "at": [PX + PW / 2, PY + ph / 2], "width": PW, "whole": True}
    wave = [at(f"wave{j}") for j in range(14)]
    (cx, cy), (l0x, l0y), (r0x, r0y), (r1x, r1y) = at("crest"), at("lens0"), at("roll0"), at("roll1")
    (rx, ry), (tx, ty) = at("rwy"), at("tower")
    (ua, uay), (ub, uby), (da, day), (db, dby) = at("up_a"), at("up_b"), at("down_a"), at("down_b")
    r = S.ribbon
    over = (stream(wave, 0, 0.9) + stream(wave, -22, 0.6) + stream(wave, 22, 0.6)
            + r(U + "w", [(PX + 18, PY + 70), (PX + 70, PY + 70), (PX + 124, PY + 70)], 6.5, *INK)
            + r(U + "up", [(max(ua, PX + 14), uay), ((max(ua, PX + 14) + ub) / 2, (uay + uby) / 2 - 4), (ub, uby)], 6.0, *ORANGE)
            + r(U + "dn", [(da, day), ((da + db) / 2, (day + dby) / 2 - 2), (db, dby)], 6.5, *BLUE)
            + eddy(r0x - 6, r0y + 2, 12) + eddy(r1x - 6, r1y + 2, 12) + eddy(tx + 10, ty - 6, 6) + eddy(tx + 26, ty - 4, 5))
    c = S.callout
    calls = "".join([
        c(1, PX + 140, PY + 70, PX + 128, PY + 70, r=10.5),
        c(2, tx - 20, ty + 30, tx + 8, ty - 2, r=10.5),
        c(3, (max(ua, PX + 14) + ub) / 2 - 30, (uay + uby) / 2 + 26, (max(ua, PX + 14) + ub) / 2, (uay + uby) / 2, r=10.5),
        c(4, (da + db) / 2 + 30, (day + dby) / 2 + 26, (da + db) / 2 + 4, (day + dby) / 2 + 2, r=10.5),
        c(5, wave[10][0] + 50, wave[10][1] + 6, wave[10][0] + 20, wave[10][1] + 2, r=10.5),
        c(6, l0x + 52, l0y - 28, l0x + 20, l0y - 6, r=10.5),
        c(7, r0x + 40, r0y + 34, r0x + 10, r0y + 6, r=10.5),
        c(8, cx - 20, cy - 50, cx + 34, cy + 14, r=10.5),
    ])
    frame = f'</g><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', clip + sky, img, over + frame + calls]


def plate():
    return {
        "id": "fig-15-07-mountain-wave",
        "replaces": "fig-15-07-mountain-wave.svg",
        "book_file": "plate-15-07-mountain-wave.jpg",
        "caption": "Figure 15-7. Mechanical turbulence, mountain wave and rotor",
        "desc": ("Figure 15-7. Mechanical turbulence, mountain wave and rotor, in one 3D view over the desert: the wind across a ridge, smooth rising air on the windward "
                 "slope and strong sinking air on the lee slope, the standing wave downwind with lens-shaped clouds on its crests and roll clouds below them where the "
                 "rotors are, and eddies by the buildings of an aerodrome."),
        "legend": [
            "Wind.",
            "Eddies and gusts downwind of buildings near the runway.",
            "Smooth rising air on the windward slope.",
            "Strong sinking air on the lee slope, which can exceed a light aeroplane's climb.",
            "Standing wave crests.",
            "Lens-shaped cloud marking a crest.",
            "Rotors: violent turbulence below the crests.",
            "The ridge.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
