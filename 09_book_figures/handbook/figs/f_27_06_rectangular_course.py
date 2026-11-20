"""Figure 27-6. The rectangular course: crab on the legs and the bank in each corner. The book's illustrated figure (its SVG kept in old/: the field, the course in blue, the crab and the
bank ranges at the corners, the tags) on an aerial view of the country (figs/terrain.py): fields of crop and ploughed plots round the field of the exercise (its rows kept), with the
aeroplane of the model at the four places where the old drawing had its own, same heading and place. The numbered callouts are the old figure's."""
from reskin import LOOK

from figs import h_plan

# the four aeroplanes of the old drawing: where, and which way (its rotate() turns the nose, which pointed east, clockwise; the picture of the model points north: 90 more)
PLANES = [(305, 352, 0), (502, 245, 260.4), (345, 98, 180), (148, 205, 99.6)]
SPRITES = [{"name": "sprite-top", "at": [x, y], "width": 47, "angle": a + 90, **LOOK} for x, y, a in PLANES]
ROWS = ('<defs><pattern id="hpRows" width="10.4" height="10" patternUnits="userSpaceOnUse"><rect width="10.4" height="10" fill="#5B9748"/><rect width="5.2" height="10" fill="#6CA857"/></pattern></defs>')


def plate():
    return {
        "id": "fig-27-06-rectangular-course",
        "replaces": "fig-27-06-rectangular-course.svg",
        "book_file": "plate-27-06-rectangular-course.jpg",
        "caption": "Figure 27-6. The rectangular course: crab on the legs and the bank in each corner",
        "desc": "Figure 27-6. The rectangular course: crab on the legs and the bank in each corner",
        "legend": [
            "Wind, 15 kt.",
            "The field: fly at an equal distance outside its edges.",
            "Entry on a 45° line to downwind.",
            "Downwind leg: tailwind, highest groundspeed, no crab.",
            "The steepest bank of the course, at the start of the turn onto base.",
            "Base leg: nose toward the inside.",
            "Upwind leg: headwind, lowest groundspeed, no crab.",
            "Crosswind leg: nose toward the outside.",
        ],
        "canvas": [640, 440 + 260],
        # above the drawing, the course in 3D (figs/oeth3d.rectangle_27_06): at 1 000 ft over the field, its shadow the ground track, the aeroplanes enlarged
        "top3d": {"render": "farm-27-06-rectangle", "height": 260, "v_mid": 0.45, "uid": "r276", "callouts": [
            (1, "wind", 60.0, 40.0), (2, "field", 236.0, 236.0), (3, "entry", 40.0, 236.0), (4, "down", 336.0, 236.0), (5, "corner", 522.0, 236.0),
            (6, "base", 566.0, 96.0), (7, "up", 404.0, 30.0), (8, "cross", 104.0, 140.0)]},
        "background": "pale",
        "reskin": h_plan.layer({
            "svg": "fig-27-06-rectangular-course.svg",
            "remove": [r'<path d="M \d+ \d+ q 20 -6 40 0 t 40 0 t 40 0" fill="none" stroke="#ffffff" stroke-width="1.6" opacity="0.6" stroke-linecap="round"/>'],       # the wave marks of the old ground
            "replace": [['<rect width="640" height="440" fill="#f4f8fc"/>', '<rect x="0" y="0" width="640" height="440" fill="#ffffff"/>'],
                        ['<rect x="8" y="6" width="624" height="428" rx="10" fill="url(#f2706-land)"/>', '<rect x="8" y="6" width="624" height="428" rx="10" fill="none"/>'],
                        ['fill="#d6e3c7" opacity="0.7"', 'fill="url(#hpCrop)" opacity="0.93"'], ['fill="#d1e0c1" opacity="0.7"', 'fill="url(#hpCrop)" opacity="0.93"'],
                        ['fill="#e4dcc0" opacity="0.7"', 'fill="url(#hpPlot)" opacity="0.93"'],
                        ['<rect x="200" y="150" width="250" height="150" rx="3" fill="url(#f2706-fld)"', '<rect x="200" y="150" width="250" height="150" rx="3" fill="url(#hpRows)"']],
            "drop": [['<g transform="translate(305 352) rotate(0) scale(1.05)"', '<rect x="30" y="37.7" width="72" height="4.6"', {"sprites": SPRITES}]],
        }, "terrain-27-06", seed=276, kind="farm", veil=0.28, markup=ROWS),
    }
