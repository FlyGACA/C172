"""Figure 14-8. Radiation fog: the temperature falls to the dew point overnight. The chart of the book's figure (the temperature and dew point curves, the shaded night, the sunrise, its
callouts 1 to 4) over three scenes of the same hollow in the hills of the Arabian Peninsula: the evening, clear and calm, the ground radiating its heat to the sky; the dawn, with the
fog lying in the hollow and thickest in its middle; the mid-morning, with the fog lifted into low cloud as the ground heats (figs/scene.py makes the sky, the land, the fog and the arrows;
reskin.py lays them with the clouds of figs/clouds.py)."""
import os
import re

from figs import scene as S

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(HERE, "old", "fig-14-08-radiation-fog.svg"), encoding="utf-8") as f:
    OLD = f.read()
CHART = OLD[OLD.index('<rect x="415.6"'):OLD.index('<path d="M 12 390 L 62 390')]                     # the night, the grid, the axes, the two curves, the sunrise
CHART += "".join(m.group(0) for m in re.finditer(r'<circle[^>]*r="10\.5"[^>]*/>\s*<text[^>]*>[1-4]</text>', OLD))      # and the callouts 1 to 4

PANELS = [(12, 196), (222, 196), (432, 196)]
TOP, BOTTOM = 232, 410


def panel(i, sky_stops, body):
    """One scene in its card: a rounded frame with a soft shadow, the picture clipped to it."""
    x, w = PANELS[i]
    h = BOTTOM - TOP
    uid = f"f1408p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, TOP, w, h, sky_stops) + body + f'</g><rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def hollow(i, seed=4):
    x, w = PANELS[i]
    return S.valley(f"f1408v{i}", x, x + w, TOP + 62, BOTTOM, seed=seed, depth=34)


def village(i, lit=False):
    x, w = PANELS[i]
    base = 352
    out = [S.house(x + 78, base + 6, 13, 8, 3), S.house(x + 102, base + 3, 11, 7, 4), S.house(x + 60, base + 12, 10, 6, 5)]
    out += [S.palm(x + 52, base + 16, 20, 0.1, 6), S.palm(x + 128, base + 8, 17, -0.08, 7), S.acacia(x + 150, base + 14, 11, 8), S.palm(x + 34, base + 26, 24, 0.12, 9)]
    if lit:
        out += [f'<rect x="{S.n(x + 84)}" y="{base - 1.5}" width="1.8" height="2.4" fill="#FFE08A"/><rect x="{S.n(x + 106)}" y="{base - 3.5}" width="1.6" height="2.2" fill="#FFE08A"/>']
    return "".join(out)


def heat_waves(i, colour1="#E8782E", colour2="#F8BE73", n_arrows=3, wavy=True):
    x, w = PANELS[i]
    out = []
    for k in range(n_arrows):
        cx = x + 40 + k * 56
        if wavy:
            pts = [(cx, 392), (cx + 5, 380), (cx - 3, 368), (cx + 5, 356), (cx - 2, 344)]
        else:
            pts = [(cx, 394), (cx, 380), (cx, 366), (cx, 352)]
        out.append(S.ribbon(f"f1408h{i}{k}", pts, 5.2, colour1, colour2, opacity=0.88, head=2.2, tail=0.4, per=8))
    return "".join(out)


def evening():
    x, w = PANELS[0]
    stars = "".join(f'<circle cx="{S.n(x + sx)}" cy="{S.n(TOP + sy)}" r="{r}" fill="#FFFFFF" opacity="{o}"/>' for sx, sy, r, o in
                    [(22, 16, 0.9, 0.9), (50, 30, 0.7, 0.7), (80, 12, 1.1, 0.95), (112, 26, 0.7, 0.7), (140, 10, 0.9, 0.9), (170, 24, 0.8, 0.8), (36, 44, 0.7, 0.6), (96, 46, 0.8, 0.7), (178, 46, 0.7, 0.6), (150, 40, 0.6, 0.5)])
    moon = (S.glow("f1408mg", x + 160, TOP + 24, 26, "#FFF1C8", 0.55) + f'<circle cx="{S.n(x + 160)}" cy="{S.n(TOP + 24)}" r="8.5" fill="#F7EBC2"/>'
            f'<circle cx="{S.n(x + 164.5)}" cy="{S.n(TOP + 21.5)}" r="7.6" fill="#4B5C8E"/>')
    return panel(0, [(0.0, "#2B3A6B"), (0.45, "#5E6F9F"), (0.8, "#C79DA0"), (1.0, "#F2B98A")],
                 stars + moon + hollow(0, 4) + village(0, lit=True) + heat_waves(0, wavy=True))


def dawn():
    x, w = PANELS[1]
    sun = S.glow("f1408sg", x + 150, TOP + 96, 52, "#FFE3A8", 0.9) + f'<circle cx="{S.n(x + 150)}" cy="{S.n(TOP + 99)}" r="8" fill="#FFF3CF"/>'
    fogs = (S.fog("f1408fa", x - 30, x + w + 30, 372, 96, seed=3, opacity=1.0, middle=True, foot=0.1) + S.fog("f1408fb", x - 20, x + w + 20, 376, 62, seed=9, opacity=1.0, wisp=1.1, middle=True, foot=0.1)
            + S.fog("f1408fc", x, x + w, 372, 38, seed=21, opacity=0.9, wisp=1.0, middle=True, foot=0.1))
    return panel(1, [(0.0, "#5C74B0"), (0.5, "#A8B7D8"), (0.82, "#F3D3B2"), (1.0, "#FBE6C4")], sun + hollow(1, 4) + village(1) + fogs)


def morning():
    x, w = PANELS[2]
    sun = S.glow("f1408tg", x + 150, TOP + 38, 40, "#FFF2C4", 0.9) + f'<circle cx="{S.n(x + 150)}" cy="{S.n(TOP + 38)}" r="8.5" fill="#FFF7DC"/>'
    return panel(2, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 sun + hollow(2, 4) + village(2) + S.fog("f1408ma", x, x + w, 362, 22, seed=5, opacity=0.5, wisp=0.8) + heat_waves(2, "#D9731F", "#F2B15F", 2, wavy=False))


LOW_CLOUDS = [{"name": "cloud-cumulus-b", "at": [476, 276], "width": 54, "height": 18}, {"name": "cloud-cumulus-b", "at": [530, 270], "width": 50, "height": 16},
              {"name": "cloud-cumulus-b", "at": [585, 278], "width": 52, "height": 17}]


def callouts():
    return S.callout(5, 30, 250, r=10.5) + S.callout(6, 240, 250, r=10.5) + S.callout(7, 450, 250, r=10.5)


def plate():
    return {
        "id": "fig-14-08-radiation-fog",
        "replaces": "fig-14-08-radiation-fog.svg",
        "book_file": "plate-14-08-radiation-fog.jpg",
        "caption": "Figure 14-8. Radiation fog: the temperature falls to the dew point overnight",
        "desc": "Figure 14-8. Radiation fog: the temperature falls to the dew point overnight",
        "legend": [
            "Temperature, falling through a clear night.",
            "Dew point, almost steady.",
            "The spread closes and fog forms.",
            "Sunrise.",
            "Evening: clear and calm, the ground radiating heat.",
            "Dawn: fog in the low ground, thickest in the hollow.",
            "Mid-morning: the ground heats and the fog lifts and breaks up.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-08-radiation-fog.svg",
            "blank": True,
            "layers": ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', CHART, evening(), dawn(), morning(), *LOW_CLOUDS, callouts()],
        },
    }
