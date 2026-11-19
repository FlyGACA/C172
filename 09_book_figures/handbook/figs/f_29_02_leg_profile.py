"""Figure 29-2. The leg from A to B in profile, drawn again as a scene (the old figure was a flat chart). The geometry and the numbers of the old figure are kept exactly
(its ground profile, its path, its 3 000 ft above-ground line, its scales: 7.72 units a nautical mile, 0.03625 a foot), and so are its eleven callouts:

the sky of a clear day over the land, the ground profile as a band of desert with its crest lit and scrub on it, the escarpment beyond B as rock; the runways of A and B edge-on;
the path as a line with a casing (dashed for the join); the model at three places (climbing, in the cruise, descending); the checkpoints' times on dotted lines from the top; the
heights and distances as quiet scales at the left and the foot (a grid of thin white lines in the sky). Digits only; the words are in the legend (figs/marks.py)."""
from figs import h_a1 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 380
X0, PX_NM = 62.0, 7.72                                      # 0 NM (A), units per nautical mile
Y0, PX_FT = 318.0, 0.03625                                  # sea level, units per foot
BLUE, INK, AMBER = "#1D4ED8", "#1E293B", "#B45309"
GROUND = [(62, 245.5), (92.9, 241.8), (131.5, 232.8), (177.8, 225.5), (224.2, 229.1), (270.5, 236.4), (309.1, 240), (355.4, 247.3), (401.8, 250.9), (424.9, 260),
          (432.7, 265.4), (440.4, 260), (471.3, 254.5), (509.9, 256.3), (556.2, 260), (579.4, 258.2)]
SCARP = [(579.4, 258.2), (591, 212.8), (602.6, 205.6), (618, 203.8), (632, 203.0)]
AGL = ("M 62 136.7 C 67.1 136.1 81.3 135.2 92.9 133 C 104.5 130.9 117.3 126.7 131.5 124 C 145.7 121.3 162.4 117.3 177.8 116.7 C 193.3 116.1 208.7 118.5 224.2 120.3 "
       "C 239.6 122.2 256.3 125.8 270.5 127.6 C 284.7 129.4 295 129.4 309.1 131.2 C 323.3 133 340 136.7 355.4 138.5 C 370.9 140.3 390.2 140 401.8 142.1 C 413.4 144.2 419.8 148.8 "
       "424.9 151.2 C 430.1 153.6 430.1 156.6 432.7 156.6 C 435.2 156.6 434 153 440.4 151.2 C 446.8 149.4 459.7 146.3 471.3 145.7 C 482.9 145.1 495.7 146.6 509.9 147.5 "
       "C 524 148.5 544.6 150.9 556.2 151.2 C 567.8 151.5 573.6 157.2 579.4 149.4 C 585.2 141.5 587.1 112.8 591 104 C 594.8 95.3 598.1 98.3 602.6 96.8 C 607.1 95.3 615.4 95.3 618 95")
PATH = "M 62 245.5 L 154.7 82.3 L 432.7 82.3 L 523 223.7 L 542.3 223.7"
JOIN = "M 542.3 223.7 Q 552.3 223.7 556.2 260"
TIMES = [(154.7, "09:12"), (309.1, "09:25"), (432.7, "09:36"), (556.2, "09:47")]
BOX = (8, 14, 624, 312)


def land():
    x, y, w, h = BOX
    bottom = y + h
    ground = [(x, GROUND[0][1])] + GROUND + SCARP
    out = [S.land_layer("lp29g", ground, bottom, ("#E8D3A4", "#C9A974"))]
    out.append(S.land_layer("lp29r", SCARP + [(632, 260)], bottom, S.SAND["rock"], rim=True))
    out.append(S.scrub(29, x + 8, 575, 262, bottom - 4, 34, scale=0.9))
    out.append(H.runway("lp29ra", 52, 74, 245.5, half=2.6, centre=False, lights=False, shoulder=False))
    out.append(H.runway("lp29rb", 546, 568, 260, half=2.6, centre=False, lights=False, shoulder=False))
    return "".join(out)


def grid():
    out = []
    for ft in (2000, 4000, 6000):
        y = Y0 - ft * PX_FT
        out.append(f'<line x1="{n(X0)}" y1="{n(y)}" x2="624" y2="{n(y)}" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8"/>')
    for nm in range(0, 80, 10):
        x = X0 + nm * PX_NM
        out.append(f'<line x1="{n(x)}" y1="{n(BOX[1] + BOX[3] - 6)}" x2="{n(x)}" y2="{n(BOX[1] + BOX[3])}" stroke="#5B4A2E" stroke-opacity="0.55" stroke-width="1"/>')
    for x, _ in TIMES:
        out.append(f'<line x1="{n(x)}" y1="40" x2="{n(x)}" y2="300" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="1" stroke-dasharray="2 3"/>')
    return "".join(out)


def labels():
    out = []
    for ft in (0, 2000, 4000, 6000):
        out.append(M.chip(34, Y0 - ft * PX_FT, f"{ft:,}".replace(",", " "), INK, size=7.0))
    for nm in range(0, 80, 10):
        out.append(M.chip(X0 + nm * PX_NM, 338, str(nm), INK, size=7.0))
    out.append(M.chip(34, 338, "NM", INK, size=7.0) + M.chip(34, 30, "FT", INK, size=7.0))
    for x, t in TIMES:
        out.append(M.chip(x, 30, t, AMBER, size=8.2, kind="clock"))
    return "".join(out)


def layers():
    x, y, w, h = BOX
    out = [H.page("lp29p", W, HT), H.defs()]
    out.append(S.card("lp29c", x, y, w, h, H.SKY, S.glow("lp29s", 520, 60, 160, "#FFF1CC", 0.45) + grid()))
    out.append(H.cloud("cloud-cumulus-a", 330, 168, 74, 0.8))
    out.append(H.cloud("cloud-cumulus-b", 100, 82, 46, 0.75))
    out.append(S.card_front("lp29l", x, y, w, h, land()))
    # the 3 000 ft above-ground line, the path, the join
    out.append(f'<path d="{AGL}" fill="none" stroke="#10233F" stroke-opacity="0.35" stroke-width="2.6" stroke-dasharray="5 4"/>'
               f'<path d="{AGL}" fill="none" stroke="#FFFFFF" stroke-width="1.4" stroke-dasharray="5 4"/>')
    out.append(H.path_line(PATH, BLUE, 2.8, casing=2.4))
    out.append(H.path_line(JOIN, BLUE, 2.0, dash="5 3", casing=2.0))
    # the model: climbing, in the cruise, descending
    out.append(H.plane_mid(112, 161, -12, 44))
    out.append(H.plane_mid(232, 84, 0, 46))
    out.append(H.plane_mid(488, 166, 8, 44))
    out.append(labels())
    c = S.callout
    out.append(c(1, 80, 277.5, 64, 249.5) + c(2, 142.1, 172.4, 122.1, 160.4) + c(3, 150.7, 56, 154.7, 79) + c(4, 293.7, 58.3, 293.7, 78.3)
               + c(5, 262.8, 101.6, 262.8, 124.6) + c(6, 331.1, 104.3, 312.1, 85.3) + c(7, 444, 56, 433.7, 79) + c(8, 455.8, 183.8, 475.9, 151.2)
               + c(9, 509.2, 193.7, 527.2, 218.7) + c(10, 552.2, 294, 556.2, 265) + c(11, 600, 177.4, 597.7, 207))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-29-02-leg-profile",
        "replaces": "fig-29-02-leg-profile.svg",
        "book_file": "plate-29-02-leg-profile.jpg",
        "caption": "Figure 29-2. The leg from A to B in profile",
        "desc": "Figure 29-2. The leg from A to B in profile",
        "legend": [
            "Takeoff from A at 09:00.",
            "Climb at 75 kt: 12 minutes, 8 L.",
            "Top of climb at checkpoint 1, 09:12.",
            "Cruise at 6 500 ft.",
            "3 000 ft above the ground: above it the cruising-altitude rule applies.",
            "Checkpoint 2, 09:25.",
            "Checkpoint 3, 09:36: top of descent, 16 NM out.",
            "Descent at 500 ft/min: about 8 minutes, 12 NM.",
            "Level at circuit height, here 1 000 ft above B; join.",
            "Aerodrome B, elevation 1 600 ft, 09:47.",
            "The escarpment.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-29-02-leg-profile.svg", "blank": True, "layers": layers()},
    }
