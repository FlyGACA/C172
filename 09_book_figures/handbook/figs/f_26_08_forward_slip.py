"""Figure 26-8. A forward slip from behind and from above, and its steeper approach path. Three scenes in cards: the model from behind, banked into the wind over the desert (the aileron
and rudder marks, the lift tilted towards the low wing, the wind as ribbon arrows); the same slip from above on an aerial view of the country (figs/terrain.py) with the runway and its extended
centreline, the track, the airflow on the side of the aeroplane; and the approach in profile, the steeper path of the slip against the shallower path without it. The ten numbered callouts
of the old figure are kept in their places (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-26-08", size=(2560, 1600), seed=26, kind="plain", features=("scrub", "wadis"), veil=0.3, soft=2.6)

TL = (8, 8, 306, 242)
TR = (326, 8, 306, 242)
BT = (8, 262, 624, 172)
GYB = 410.0
GYT = 214.0
ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")
GREEN = ("#0A7D5A", "#7ED6AF")
INK = ("#1F2937", "#667489")
LOOK_TOP = {"outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.9}, "shadow": {"dx": 3.5, "dy": 5.0, "blur": 2.6, "opacity": 0.32}}


def top_left():
    marks = ('<g transform="rotate(-18 170 124)">'
             '<rect x="68" y="101.6" width="30" height="3" rx="1" fill="#1D4ED8"/><rect x="212" y="112.6" width="30" height="3" rx="1" fill="#1D4ED8"/>'
             '<polygon points="170.2,91 178,92.4 178,111 170.2,111.6" fill="#1D4ED8"/></g>')
    out = H.profile("a1tl", TL, GYT, seed=31, sun=(70, 60), far=22, mid=10, base=14, clouds=[H.cloud("cloud-cumulus-b", 270, 150, 40, 0.9)],
                    palms=[(262, GYT + 14, 0.5)], acacias=[(40, GYT + 18, 0.5)], scrub_count=14)
    out.append(S.ribbon("a1lift", [(168, 118), (159, 78), (149, 40)], 6.5, *BLUE))
    out.append({"name": "sprite-rear", "at": [169.1, 121.2], "width": 210, "angle": -18, **H.LOOK})
    out.append(marks)
    for k, y in enumerate((94, 124, 154)):
        out.append(S.ribbon(f"a1wl{k}", [(16, y), (34, y), (52, y)], 7.0, *ORANGE))
    return out


def top_right():
    x, y, w, h = TR
    out = [S.card("a1tr", x, y, w, h, H.SKY, "", radius=10)]
    inner = [{"name": "terrain-26-08", "at": [x + w / 2 + 30, y + h / 2 + 30], "width": 640}]
    runway = (f'<rect x="450" y="{y}" width="40" height="92" fill="#D9C79A" opacity="0.75"/>'
              f'<defs>{S.gradient("a1rwt", [(0, "#454E5E"), (1, "#323A48")])}</defs><rect x="454" y="{y}" width="32" height="88" fill="url(#a1rwt)"/>'
              f'<rect x="454" y="{y}" width="1.2" height="88" fill="#F4F6FA" opacity="0.85"/><rect x="484.8" y="{y}" width="1.2" height="88" fill="#F4F6FA" opacity="0.85"/>')
    runway += "".join(f'<rect x="469.4" y="{yy}" width="1.6" height="11" fill="#F4F6FA" opacity="0.92"/>' for yy in (26, 46, 66))
    runway += "".join(f'<rect x="{xx}" y="76" width="2.6" height="12" fill="#FAFBFD" opacity="0.97"/>' for xx in (457, 462.2, 467.4, 472.6, 477.8, 483))
    runway += '<line x1="470" y1="96" x2="470" y2="246" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="6 5" opacity="0.9"/>'
    runway += '<line x1="470" y1="96" x2="470" y2="246" stroke="#4B5870" stroke-width="0.8" stroke-dasharray="6 5" opacity="0.8"/>'
    inner.append(runway)
    out += H.clipped("a1trclip", TR, 10, inner)
    out.append(S.card_front("a1trb", x, y, w, h, "", radius=10))
    for k, yy in enumerate((160, 186, 212)):
        out.append(S.ribbon(f"a1wr{k}", [(344, yy), (362, yy), (380, yy)], 7.0, *ORANGE))
    out.append(S.ribbon("a1trk", [(470, 238), (470, 186), (470, 130)], 7.0, *GREEN))
    out.append({"name": "sprite-top", "at": [470, 186], "width": 58, "angle": 28, **LOOK_TOP})
    out.append(S.ribbon("a1flow", [(396, 118), (420, 140), (444, 164)], 6.5, *BLUE))
    return out


def bottom():
    objects = H.windsock(598, GYB - 6.5, 24, wind=1)
    out = H.profile("a1bt", BT, GYB, seed=37, sun=(80, 60), runway_args={"x0": 330, "x1": 632, "threshold": True, "aim": 380, "dash_from": 356, "half": 4.2},
                    clouds=[H.cloud("cloud-cumulus-a", 470, 288, 80), H.cloud("cloud-cumulus-b", 590, 296, 56)],
                    palms=[(246, GYB - 6, 0.55), (264, GYB - 4, 0.45)], acacias=[(48, GYB - 5, 0.5)], objects=objects, far=22, mid=10)
    out.append(H.line_cased(30, 290, 628, 376.1, "#8391A6", 1.8, dash="5 4", casing=2.0))
    out.append(H.path_line("M 30 290 L 336 394.9 C 342.7 396.1 362 399.7 376 402 C 390 404.3 407.7 407.7 420 409 C 432.3 410.3 445 409.8 450 410", "#047857", 2.6, casing=2.2))
    out.append(H.line_cased(336, 394.9, 380, 410, "#7B8799", 1.2, dash="3 3", casing=1.8))
    out.append(H.drop_shadow(332 + 10, GYB + 1.6, 50, 2.0, 0.16))
    ghost = H.plane_mid(330, 333.2, 2, 80, tint="#8B97AA", tint_strength=0.55, opacity=0.55)
    out.append(ghost)
    out.append(H.plane_mid(150, 331.1, 6, 80))
    out.append(H.foreground("a1bt", BT, GYB, seed=37, lights=(330, 632), scrub=9, scale=1.15))
    return out


def callouts():
    c = S.callout
    return "".join([c(1, 76, 206, 97, 132), c(2, 250, 40, 172, 100), c(3, 100, 40, 146, 52), c(4, 34, 66, 34, 91),
                    c(5, 544, 196, 492, 176), c(6, 520, 124, 474, 136), c(7, 370, 106, 394, 114),
                    c(8, 196, 312, 168, 317), c(9, 560, 312, 560, 365), c(10, 400, 352, 388, 402)])


def layers():
    out = [H.page("a1page", 640, 440), H.defs()]
    out += top_left()
    out += top_right()
    out += bottom()
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-26-08-forward-slip",
        "replaces": "fig-26-08-forward-slip.svg",
        "book_file": "plate-26-08-forward-slip.jpg",
        "caption": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "desc": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "legend": [
            "Upwind wing lowered with aileron: the bank is into the wind.",
            "Opposite rudder, here right, stops the turn.",
            "Lift tilts towards the low wing; the aeroplane moves sideways towards it, offsetting the drift.",
            "Wind from the left in both views.",
            "The nose points away from the wind.",
            "The track stays on the extended centreline.",
            "The airflow strikes the side of the aeroplane: drag rises sharply.",
            "At the same airspeed, the slip gives a much steeper path to the aiming point.",
            "Without the slip, the aeroplane lands well beyond it.",
            "Slip taken out before the round out; the landing is straight.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-08-forward-slip.svg", "blank": True, "layers": layers()},
    }
