"""Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front. Three glass blocks of the atmosphere, one over the other: the front face of each is the
cross-section (the cold, warm and cool air, the sloping frontal surface, the clouds of the model of the sky (figs/clouds.py) lying along it, the rain), the top face is the ground
with the front as it is drawn on a map (triangles, half-circles), and the ribbon arrows show the air and the way the front moves (the black ones). The ten numbered callouts of the
old figure are kept, in the same order and meaning (figs/scene.py makes the pieces; reskin.py lays them with the clouds)."""
from figs import scene as S

W, H = 640, 548
FX, FW, FH = 52, 440, 104            # the front face of a block: left edge, width, height
DX, DY = 66, 34                      # the depth of a block, as it runs up and to the right
TOPS = [60, 230, 400]                # the top edge of the front face of the three blocks
GROUND = 20                          # the thickness of the ground at the foot of a face


def X(u):
    return FX + u


def pt(y0, u, v):
    return (FX + u, y0 + v)


def face_polygon(y0):
    return [(FX, y0), (FX + FW, y0), (FX + FW, y0 + FH), (FX, y0 + FH)]


def poly(y0, uv):
    return [pt(y0, u, v) for u, v in uv]


def block_base(k, y0, regions, surfaces):
    """Everything of a block that lies behind the clouds: the shadow, the ground seen from above, the sky of the face, the air (`regions`: [(points in face units, colours, opacity)]) and
    the frontal surfaces (`surfaces`: lists of points in face units)."""
    uid = f"f1409b{k}"
    y0 = y0_of(k)
    top = [(FX, y0), (FX + FW, y0), (FX + FW + DX, y0 - DY), (FX + DX, y0 - DY)]
    out = [f'<defs><filter id="{uid}sh" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="6"/></filter></defs>'
           f'<ellipse cx="{S.n(FX + (FW + DX) / 2)}" cy="{S.n(y0 + FH + 9)}" rx="{S.n(FW * 0.56)}" ry="8" fill="#16335F" opacity="0.26" filter="url(#{uid}sh)"/>']
    # the ground, from above
    out.append(f'<defs>{S.gradient(uid + "t", [(0, "#C9DCAE"), (0.55, "#DCCB9B"), (1, "#D2B988")])}</defs>' + S.face(top, f"url(#{uid}t)", 1.0, "#FFFFFF", 0.85, 1.2))
    out.append(f'<defs><filter id="{uid}g" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="{k + 3}"/>'
               f'<feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.2  0 0 0 0.6 -0.15"/></filter>{S.clip(uid + "tc", top)}</defs>'
               f'<rect x="{FX}" y="{y0 - DY}" width="{FW + DX}" height="{DY}" filter="url(#{uid}g)" opacity="0.5" clip-path="url(#{uid}tc)"/>')
    out.append(terrain(uid, y0, k))
    # the face: its own sky, then the air
    out.append(f'<defs>{S.gradient(uid + "s", [(0, "#F4F9FE"), (1, "#D5E6F6")])}</defs>' + S.face(face_polygon(y0), f"url(#{uid}s)", 1.0, "#FFFFFF", 0.0, 0))
    for i, (uv, (c1, c2), op) in enumerate(regions):
        out.append(S.air(f"{uid}a{i}", poly(y0, uv), c1, c2, op))
    for uv in surfaces:
        pts_ = poly(y0, uv)
        d = "M " + " L ".join(f"{S.n(a)},{S.n(b)}" for a, b in pts_)
        out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="4.2" stroke-opacity="0.45" stroke-linejoin="round" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="#3A4B66" stroke-width="1.6" stroke-opacity="0.75" stroke-dasharray="5 3" stroke-linejoin="round" stroke-linecap="round"/>')
    return "".join(out)


def top_point(y0, a, b):
    """A point of the top face from its own coordinates: a along the front edge (0 to 1), b into the depth (0 to 1)."""
    return (FX + a * FW + b * DX, y0 - b * DY)


def terrain(uid, y0, k):
    """Fields, a road and a few palms on the ground seen from above (the top face), in its slanting coordinates."""
    import random
    rnd = random.Random(40 + k)
    out = []
    greens = ["#A9C48A", "#B9CE95", "#C7D59F", "#9DB87F"]
    tans = ["#D9C493", "#CDB683", "#E0CD9E"]
    a = 0.0
    while a < 1.0:
        width = rnd.uniform(0.08, 0.16)
        b = 0.0
        while b < 0.98:
            depth = rnd.uniform(0.18, 0.36)
            if rnd.random() < 0.62:
                c = rnd.choice(greens if rnd.random() < 0.55 else tans)
                q = [top_point(y0, a + 0.004, b + 0.01), top_point(y0, min(1.0, a + width) - 0.004, b + 0.01), top_point(y0, min(1.0, a + width) - 0.004, min(1.0, b + depth) - 0.01), top_point(y0, a + 0.004, min(1.0, b + depth) - 0.01)]
                out.append(f'<polygon points="{S.pts(q)}" fill="{c}" opacity="0.55"/>')
            b += depth
        a += width
    road = [top_point(y0, 0.0, 0.52), top_point(y0, 1.0, 0.52), top_point(y0, 1.0, 0.57), top_point(y0, 0.0, 0.57)]
    out.append(f'<polygon points="{S.pts(road)}" fill="#8A8574" opacity="0.55"/>')
    for a in (0.06, 0.13, 0.42, 0.55, 0.78, 0.9):
        x, y = top_point(y0, a, 0.8 + 0.12 * ((a * 37) % 1))
        out.append(S.palm(x, y, 10.5, 0.1, int(a * 100)) if int(a * 10) % 2 == 0 else S.acacia(x, y, 6.5, int(a * 100)))
    return "".join(out)


def y0_of(k):
    return TOPS[k]


def block_front(k, end):
    """What lies in front of the clouds: the ground at the foot of the face, the glass (a gloss and the edges), the right face (the air that the face ends in, and the ground);
    `end` is the colours of the air at the right-hand end of the face."""
    y0 = y0_of(k)
    uid = f"f1409f{k}"
    out = []
    ground = [(FX, y0 + FH - GROUND), (FX + FW, y0 + FH - GROUND), (FX + FW, y0 + FH), (FX, y0 + FH)]
    out.append(f'<defs>{S.gradient(uid + "g", [(0, "#D8BF8A"), (1, "#A98A58")])}</defs><polygon points="{S.pts(ground)}" fill="url(#{uid}g)"/>'
               f'<line x1="{FX}" y1="{y0 + FH - GROUND}" x2="{FX + FW}" y2="{y0 + FH - GROUND}" stroke="#8FA85F" stroke-width="2.4"/>')
    for i in range(14):                                                                          # a little grit in the soil
        gx = FX + 12 + i * 31.5 + (i % 3) * 5
        out.append(f'<ellipse cx="{S.n(gx)}" cy="{S.n(y0 + FH - GROUND * 0.45 + (i % 2) * 4)}" rx="{3 + (i % 3)}" ry="1.4" fill="#8E7347" opacity="0.5"/>')
    x1, x2 = FX + FW, FX + FW + DX
    right = [(x1, y0), (x2, y0 - DY), (x2, y0 - DY + FH), (x1, y0 + FH)]
    right_air = [(x1, y0), (x2, y0 - DY), (x2, y0 - DY + FH - GROUND), (x1, y0 + FH - GROUND)]
    right_ground = [(x1, y0 + FH - GROUND), (x2, y0 - DY + FH - GROUND), (x2, y0 - DY + FH), (x1, y0 + FH)]
    out.append(f'<defs>{S.gradient(uid + "r", [(0, "#EEF5FC"), (1, "#C9DCF1")])}</defs>' + S.face(right, f"url(#{uid}r)", 1.0, "#FFFFFF", 0.0, 0))
    out.append(S.air(uid + "e", right_air, end[0], end[1], 0.55))
    out.append(f'<polygon points="{S.pts(right_ground)}" fill="#B99A68"/>')
    out.append(f'<defs>{S.gradient(uid + "d", [(0, "#0B2A55", 0.0), (1, "#0B2A55", 0.22)], 0, 0, 1, 0)}</defs><polygon points="{S.pts(right)}" fill="url(#{uid}d)"/>')
    out.append(S.face(right, "none", 1.0, "#FFFFFF", 0.85, 1.2))
    out.append(f'<defs>{S.gradient(uid + "k", [(0, "#FFFFFF", 0.5), (0.5, "#FFFFFF", 0.0), (1, "#FFFFFF", 0.0)], 0, 0, 0.3, 1)}</defs><polygon points="{S.pts(face_polygon(y0))}" fill="url(#{uid}k)"/>')
    out.append(f'<polygon points="{S.pts([(FX + 60, y0), (FX + 130, y0), (FX + 60, y0 + FH), (FX - 10, y0 + FH)])}" fill="#FFFFFF" opacity="0.07"/>')
    out.append(f'<polygon points="{S.pts(face_polygon(y0))}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-opacity="0.9"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the three blocks
COLD = ("#6F9BE8", "#4D7BD0")
WARM = ("#FFD9A6", "#F7B468")
COOL = ("#8DD6C6", "#58B3A2")


def cold_front():
    k, y0 = 0, TOPS[0]
    surf = [(252, 84), (240, 66), (226, 44), (212, 22), (203, 0)]
    regions = [([(0, 84), (0, 0), (203, 0), (212, 22), (226, 44), (240, 66), (252, 84)], COLD, 0.62),
               ([(203, 0), (FW, 0), (FW, 84), (252, 84), (240, 66), (226, 44), (212, 22)], WARM, 0.5)]
    base = block_base(k, y0, regions, [surf])
    clouds = [
        {"name": "cloud-tcu", "at": [X(266), y0 + 47], "width": 30, "height": 70},
        {"name": "cloud-cb-wide", "at": [X(322), y0 + 42], "width": 134},
        {"name": "cloud-cumulus-b", "at": [X(412), y0 + 66], "width": 56},
    ]
    rain = S.rain("f1409r0", X(262), X(330), y0 + 50, y0 + FH - GROUND, slant=-6, count=30, seed=3, colour="#2F55A8", veil=0.24)
    bolt = S.lightning("f1409l0", X(284), y0 + 44, y0 + FH - GROUND - 2, seed=8, forks=1)
    arrows = (S.ribbon("f1409c0", [(X(18), y0 + 70), (X(90), y0 + 64), (X(170), y0 + 68), (X(238), y0 + 72)], 9, "#2F63C8", "#8DB3F2")
              + S.ribbon("f1409w0", [(X(430), y0 + 76), (X(392), y0 + 52), (X(340), y0 + 30), (X(300), y0 + 12)], 8, "#E8782E", "#F8BE73")
              + S.ribbon("f1409m0", [(X(24), y0 + 12), (X(110), y0 + 12), (X(178), y0 + 12)], 7, "#1F2937", "#667489", opacity=0.95))
    symbols = S.front_symbols("cold", (FX + 252, y0), (FX + 252 + DX, y0 - DY), 6.5, 17.0)
    return [base, *clouds, rain, bolt, block_front(k, WARM), arrows, symbols]


def warm_front():
    k, y0 = 1, TOPS[1]
    surf = [(112, 84), (200, 70), (290, 50), (370, 26), (FW, 4)]
    regions = [([(0, 0), (FW, 0), (FW, 4), (370, 26), (290, 50), (200, 70), (112, 84), (0, 84)], WARM, 0.5),
               ([(112, 84), (200, 70), (290, 50), (370, 26), (FW, 4), (FW, 84)], COLD, 0.62)]
    base = block_base(k, y0, regions, [surf])
    clouds = [
        {"name": "cloud-cirrus-b", "at": [X(396), y0 + 11], "width": 160, "height": 40, "angle": -4},
        {"name": "cloud-veil", "at": [X(364), y0 + 28], "width": 190, "height": 22, "angle": -10},
        {"name": "cloud-altostratus", "at": [X(288), y0 + 42], "width": 190, "height": 46, "angle": -9},
        {"name": "cloud-nimbostratus", "at": [X(190), y0 + 63], "width": 220, "height": 48, "angle": -5},
        {"name": "cloud-stratus", "at": [X(300), y0 + FH - GROUND - 8], "width": 150, "height": 16},
    ]
    rain = S.rain("f1409r1", X(120), X(252), y0 + 74, y0 + FH - GROUND, slant=-4, count=26, seed=6, colour="#2F55A8", veil=0.16)
    arrows = (S.ribbon("f1409w1", [(X(24), y0 + 62), (X(120), y0 + 52), (X(230), y0 + 30), (X(318), y0 + 8)], 9, "#E8782E", "#F8BE73")
              + S.ribbon("f1409c1", [(X(430), y0 + 88), (X(380), y0 + 87), (X(330), y0 + 86)], 6, "#2F63C8", "#8DB3F2", head=2.0)
              + S.ribbon("f1409m1", [(X(24), y0 + 12), (X(110), y0 + 12), (X(178), y0 + 12)], 7, "#1F2937", "#667489", opacity=0.95))
    symbols = S.front_symbols("warm", (FX + 112, y0), (FX + 112 + DX, y0 - DY), 6.5, 17.0)
    return [base, *clouds, rain, block_front(k, COLD), arrows, symbols]


def occluded_front():
    k, y0 = 2, TOPS[2]
    regions = [([(0, 84), (0, 0), (170, 0), (190, 40), (250, 84)], COLD, 0.62),
               ([(170, 0), (FW, 0), (FW, 6), (190, 40)], WARM, 0.5),
               ([(190, 40), (FW, 6), (FW, 84), (250, 84)], COOL, 0.62)]
    surf = [[(250, 84), (190, 40), (170, 0)], [(190, 40), (330, 24), (FW, 6)]]
    base = block_base(k, y0, regions, surf)
    clouds = [
        {"name": "cloud-nimbostratus", "at": [X(306), y0 + 32], "width": 260, "height": 46, "angle": -4},
        {"name": "cloud-tcu", "at": [X(226), y0 + 26], "width": 36, "height": 78},
        {"name": "cloud-stratus", "at": [X(384), y0 + 62], "width": 110, "height": 16},
    ]
    rain = S.rain("f1409r2", X(214), X(330), y0 + 50, y0 + FH - GROUND, slant=-5, count=26, seed=11, colour="#2F55A8", veil=0.2)
    arrows = (S.ribbon("f1409c2", [(X(16), y0 + 74), (X(96), y0 + 70), (X(170), y0 + 72), (X(236), y0 + 76)], 9, "#2F63C8", "#8DB3F2")
              + S.ribbon("f1409w2", [(X(300), y0 + 78), (X(280), y0 + 56), (X(250), y0 + 36), (X(222), y0 + 18)], 8, "#E8782E", "#F8BE73")
              + S.ribbon("f1409m2", [(X(24), y0 + 12), (X(110), y0 + 12), (X(178), y0 + 12)], 7, "#1F2937", "#667489", opacity=0.95))
    symbols = S.front_symbols("occluded", (FX + 250, y0), (FX + 250 + DX, y0 - DY), 6.5, 17.0)
    return [base, *clouds, rain, block_front(k, COOL), arrows, symbols]


def callouts():
    c = S.callout
    return "".join([
        c(1, 24, 160, X(110), TOPS[0] + 70), c(2, 590, 100, X(210), TOPS[0] + 34), c(3, 590, 36, X(330), TOPS[0] + 20),
        c(4, 24, 292, X(70), TOPS[1] + 58), c(5, 590, 232, X(410), TOPS[1] + 14), c(6, 590, 290, X(300), TOPS[1] + 44), c(7, 24, 336, X(180), TOPS[1] + 80),
        c(8, 590, 410, X(260), TOPS[2] + 24), c(9, 24, 500, X(110), TOPS[2] + 74), c(10, 590, 470, X(300), TOPS[2] + 34),
    ])


def layers():
    out = [f'<defs>{S.gradient("f1409bg", [(0, "#F7FAFE"), (1, "#E4EDF7")])}</defs><rect x="0" y="0" width="{W}" height="{H}" fill="url(#f1409bg)"/>']
    for blk in (cold_front(), warm_front(), occluded_front()):
        out += blk
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-14-09-fronts",
        "replaces": "fig-14-09-fronts.svg",
        "book_file": "plate-14-09-fronts.jpg",
        "caption": "Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front",
        "desc": "Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front",
        "legend": [
            "Cold front: cold air pushing under warm air.",
            "The steep frontal surface.",
            "Cumulonimbus in a narrow band of showers and gusts.",
            "Warm front: warm air gliding up a shallow frontal surface.",
            "Cirrus and cirrostratus far ahead.",
            "Altostratus and nimbostratus, thickening and lowering toward the surface front.",
            "Wide band of steady rain, with low stratus in the cold air.",
            "Occluded front: warm air lifted off the ground.",
            "Cold air overtaking and undercutting cooler air ahead.",
            "Layer cloud and rain, possibly with embedded cumulonimbus.",
        ],
        "canvas": [W, H],
        "background": "pale",
        "reskin": {"svg": "fig-14-09-fronts.svg", "blank": True, "layers": layers()},
    }
