"""Figure 14-8. Radiation fog: the temperature falls to the dew point overnight. The chart of the book's figure (the temperature and dew point curves, the shaded night, the sunrise, its
callouts 1 to 4) over three renders of the same place at three times (redrawn in the second design pass; figs/oeth3d.fog_14_08, blender/render_oeth.py): the low plain
west of the escarpment at Thumamah seen from above the plateau, on the open picture of the ground on its relief. The evening, clear and calm under a low sun; the dawn, with
radiation fog lying in the low ground (a scattering volume densest at the ground) below the plateau; mid-morning, the sun higher and the fog lifted into broken low stratus.
The sky of each is drawn; callouts 5 to 7 are the three times."""
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


def scene(i, rid, stops):
    """One time of day: the drawn sky, then the render laid whole over it, in a card."""
    x, w = PANELS[i]
    h = BOTTOM - TOP
    uid = f"f1408p{i}"
    under = (f'<defs><clipPath id="{uid}c"><rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9"/></clipPath>'
             f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
             f'<rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
             f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, TOP, w, h * 0.5, stops) + '</g>')
    img = {"name": rid, "at": [x + w / 2, TOP + h / 2], "width": w, "whole": True}
    frame = f'<rect x="{x}" y="{TOP}" width="{w}" height="{h}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>'
    return [under, img, frame]


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
            "layers": ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', CHART, *scene(0, "fog-14-08-evening", EVENING), *scene(1, "fog-14-08-dawn", DAWN),
                       *scene(2, "fog-14-08-morning", MORNING), callouts()],
        },
    }
