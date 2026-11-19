"""Figure 14-8. Radiation fog: the temperature falls to the dew point overnight. The chart of the book's figure (the temperature and dew point curves, the shaded night, the sunrise, its
callouts 1 to 4) over three renders of the same place at three times (redrawn in the second design pass; figs/oeth3d.fog_14_08, blender/render_oeth.py): the low plain
west of the escarpment at Thumamah seen from above the plateau, on the open picture of the ground on its relief. The evening, clear and calm under a low sun; the dawn, with
radiation fog lying in the low ground (a scattering volume densest at the ground) below the plateau; mid-morning, the sun higher and the fog lifted into broken low stratus.
The sky of each is drawn, and the heat leaving the ground in the evening and warming the air by mid-morning (orange arrows, as the old figure); callouts 5 to 7 are the three times."""
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


def heat_waves(i, colour1="#E8782E", colour2="#F8BE73", n_arrows=3, wavy=True):
    """The ground giving off its heat (wavy, in the evening) or heating the air above it (straight, by mid-morning), drawn over the render."""
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


def corners(i, r=9.0):
    """White over the corners of the render outside the card's rounded corners (the render is laid square)."""
    x, w = PANELS[i]
    x1, y0, y1 = x + w, TOP, BOTTOM
    k = 0.5523 * r
    paths = [f"M{x} {y0} L{x + r} {y0} C{x + r - k} {y0} {x} {y0 + r - k} {x} {y0 + r} Z", f"M{x1} {y0} L{x1} {y0 + r} C{x1} {y0 + r - k} {x1 - r + k} {y0} {x1 - r} {y0} Z",
             f"M{x} {y1} L{x} {y1 - r} C{x} {y1 - r + k} {x + r - k} {y1} {x + r} {y1} Z", f"M{x1} {y1} L{x1 - r} {y1} C{x1 - r + k} {y1} {x1} {y1 - r + k} {x1} {y1 - r} Z"]
    return "".join(f'<path d="{d}" fill="#ffffff"/>' for d in paths)


def scene(i, rid, stops, over=""):
    """One time of day: the drawn sky, then the render laid whole over it, in a card; `over` is drawn on the render."""
    x, w = PANELS[i]
    h = BOTTOM - TOP
    uid = f"f1408p{i}"
    under = (f'<defs><clipPath id="{uid}c"><rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9"/></clipPath>'
             f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
             f'<rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
             f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, TOP, w, h * 0.5, stops) + '</g>')
    img = {"name": rid, "at": [x + w / 2, TOP + h / 2], "width": w, "whole": True}
    frame = f'<rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>'
    return [under, img, over + corners(i) + frame]


EVENING = [(0.0, "#3E5E9A"), (0.55, "#C98E6B"), (1.0, "#F2C38F")]
DAWN = [(0.0, "#5C6E96"), (0.6, "#A8B4CA"), (1.0, "#E6D9CC")]
MORNING = [(0.0, "#3A70BC"), (0.6, "#86B4E6"), (1.0, "#D8E5F1")]


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
            "layers": ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', CHART, *scene(0, "fog-14-08-evening", EVENING, heat_waves(0, wavy=True)),
                       *scene(1, "fog-14-08-dawn", DAWN), *scene(2, "fog-14-08-morning", MORNING, heat_waves(2, "#D9731F", "#F2B15F", 2, wavy=False)), callouts()],
        },
    }
