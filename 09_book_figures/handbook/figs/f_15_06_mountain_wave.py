"""Figure 15-6. Mechanical turbulence, mountain wave and rotor. A ridge of rock with its lit and shaded faces on a plain of the Peninsula, the airstream over it drawn as soft white
lines (the streamlines of the old figure, kept: smooth over the windward slope, a wave on the lee side), the lens cloud on the crest of the wave, a roll cloud in each rotor, and
the aerodrome with its eddies at the foot of the windward slope. The clouds are the sprites of figs/clouds.py, the land and the arrows come from figs/scene.py; the eight
numbered callouts of the old figure and their places are kept."""
import math

from figs import scene as S

ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")
RED = ("#B3261E", "#F08A7A")
INK = ("#1F2937", "#667489")
GROUND = 330

STREAMS = [
    [(0.0, 172.0), (64.0, 172.0), (128.0, 172.0), (192.0, 172.0), (224.0, 170.5), (256.0, 159.2), (288.0, 150.5), (320.0, 146.3), (352.0, 158.3), (384.0, 199.3), (416.0, 214.2), (448.0, 160.4), (480.0, 129.3),
     (512.0, 181.5), (544.0, 215.2), (576.0, 164.6), (608.0, 128.5), (640.0, 177.3)],
    [(0.0, 124.0), (64.0, 124.0), (128.0, 124.0), (192.0, 124.0), (224.0, 123.1), (256.0, 116.1), (288.0, 110.8), (320.0, 108.2), (352.0, 116.1), (384.0, 143.0), (416.0, 152.7), (448.0, 116.1), (480.0, 94.9),
     (512.0, 130.5), (544.0, 153.4), (576.0, 118.9), (608.0, 94.3), (640.0, 127.6)],
    [(0.0, 76.0), (64.0, 76.0), (128.0, 76.0), (192.0, 76.0), (224.0, 75.5), (256.0, 72.1), (288.0, 69.4), (320.0, 68.1), (352.0, 72.0), (384.0, 85.5), (416.0, 90.4), (448.0, 72.1), (480.0, 61.4),
     (512.0, 79.2), (544.0, 90.7), (576.0, 73.5), (608.0, 61.2), (640.0, 77.8)],
]


def curl(uid, cx, cy, r, colours, width=4.5, a0=140.0, a1=430.0):
    """A turning arrow: a ribbon round a circle that tightens as it goes (clockwise on the page: the top goes with the wind, the foot against it)."""
    pts_ = []
    steps = 14
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        rr = r * (1.0 - 0.28 * i / steps)
        pts_.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return S.ribbon(uid, pts_, width, *colours)


def sky_and_streams():
    out = [S.sky("f1506sky", 0, 0, 640, GROUND + 2, [(0.0, "#3A74C0"), (0.5, "#7DAEE3"), (0.9, "#D7E7F7"), (1.0, "#F4F1DF")])]
    for k, line in enumerate(STREAMS):
        d = "M " + " L ".join(f"{S.n(x)},{S.n(y)}" for x, y in S.catmull(line, per=6))
        out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="{S.n(3.6 - 0.5 * k)}" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<path d="{d}" fill="none" stroke="#9DB9DD" stroke-opacity="0.45" stroke-width="1" transform="translate(0 2.2)"/>')
    return "".join(out)


def land():
    far = (S.land_layer("f1506f1", S.ridge(4, 0, 640, GROUND + 1, 78, peaks=0.7), GROUND + 4, ("#7587AE", "#B0BDD6"), rim=False, haze=0.30)
           + S.land_layer("f1506f2", S.ridge(8, 0, 640, GROUND + 2, 40, peaks=0.45), GROUND + 4, ("#8C9AB8", "#C2CCDD"), rim=False, haze=0.2))
    outline = S.jag([(120, 330), (176, 324), (226, 306), (262, 284), (300, 222), (330, 186), (356, 214), (392, 272), (430, 306), (476, 322), (520, 330)], 2.4, 5)
    mountain = S.rock("f1506m", outline, GROUND + 2, 100, 540, 6, spine=[(330, 186), (322, 232), (338, 272), (326, 332)])
    plain = (f'<defs>{S.gradient("f1506p", [(0, "#E7D5AA"), (1, "#C9AC78")])}</defs><rect x="0" y="{GROUND}" width="640" height="{380 - GROUND}" fill="url(#f1506p)"/>'
             + S.scrub(3, 0, 640, GROUND + 4, 378, 34, colour=("#8A8A55", "#5E603E"), scale=0.8) + f'<line x1="0" y1="{GROUND}" x2="640" y2="{GROUND}" stroke="#FFF6DA" stroke-opacity="0.6" stroke-width="1"/>')
    return far, mountain, plain


def airfield():
    out = [f'<rect x="136" y="{GROUND + 1}" width="84" height="8" fill="#4A4F5A"/><rect x="136" y="{GROUND + 1}" width="84" height="1.4" fill="#8C93A0"/>']
    out += [f'<rect x="{143 + 13 * i}" y="{GROUND + 4.6}" width="7" height="1.3" fill="#F3F4F6"/>' for i in range(6)]
    out.append(S.house(24, GROUND, 40, 46, 4))
    out.append(f'<path d="M 74 {GROUND} L 74 {GROUND - 30} Q 104 {GROUND - 54} 134 {GROUND - 30} L 134 {GROUND} Z" fill="#D5DCE8"/><path d="M 74 {GROUND - 30} Q 104 {GROUND - 54} 134 {GROUND - 30}" fill="none" stroke="#FFFFFF" stroke-width="1.2"/>'
               f'<rect x="92" y="{GROUND - 20}" width="24" height="20" fill="#8E9BB4"/><rect x="92" y="{GROUND - 20}" width="24" height="2" fill="#6B7890"/>')
    out.append(f'<g><line x1="224" y1="{GROUND}" x2="224" y2="{GROUND - 18}" stroke="#6B7280" stroke-width="1.3"/><path d="M 224,{GROUND - 18} L 238,{GROUND - 15} L 224,{GROUND - 11} Z" fill="#F36F21"/></g>')
    out.append(S.palm(50, GROUND + 14, 22, 0.1, 6) + S.acacia(224, GROUND + 22, 10, 3))
    return "".join(out)


def arrows():
    r = S.ribbon
    a = [r("f1506w", [(22, 30), (62, 30), (118, 30)], 7.0, *INK),
         r("f1506u", [(252, 288), (270, 258), (288, 230), (306, 204)], 7.0, *ORANGE),
         r("f1506d", [(352, 194), (372, 224), (392, 256), (406, 274)], 7.0, *BLUE),
         curl("f1506c1", 463, 280, 17, RED), curl("f1506c2", 598, 294, 13, RED, width=4.0),
         curl("f1506e1", 150, 306, 10, RED, width=3.4, a0=150, a1=420), curl("f1506e2", 193, 318, 8, RED, width=3.0, a0=150, a1=420)]
    return "".join(a)


def callouts():
    c = S.callout
    return "".join([c(1, 140, 30), c(2, 176, 268, 166, 292), c(3, 250, 224, 272, 248), c(4, 432, 226, 388, 244), c(5, 548, 176, 482, 130), c(6, 399, 52, 436, 78), c(7, 525, 252, 494, 270), c(8, 330, 300)])


CLOUDS = [
    {"name": "cloud-lenticular", "at": [475, 82], "width": 116},
    {"name": "cloud-lenticular", "at": [607, 78], "width": 70, "opacity": 0.9},
    {"name": "cloud-roll", "at": [470, 262], "width": 84},
    {"name": "cloud-roll", "at": [598, 274], "width": 64},
]


def plate():
    far, mountain, plain = land()
    return {
        "id": "fig-15-06-mountain-wave",
        "replaces": "fig-15-06-mountain-wave.svg",
        "book_file": "plate-15-06-mountain-wave.jpg",
        "caption": "Figure 15-6. Mechanical turbulence, mountain wave and rotor",
        "desc": "Figure 15-6. Mechanical turbulence, mountain wave and rotor",
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
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-15-06-mountain-wave.svg", "blank": True,
                   "layers": ['<rect x="0" y="0" width="640" height="380" fill="#ffffff"/>', sky_and_streams(), far, *CLOUDS, mountain, plain, airfield(), arrows(), callouts()]},
    }
