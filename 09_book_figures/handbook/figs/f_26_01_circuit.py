"""Figure 26-1. The circuit in the example aeroplane, with speed and flap setting at each point. The book's illustrated figure (its SVG kept in old/: the runway, the blue circuit, the tags
with the speed and flap of each point, the circuit unrolled below in a card of sky) on an aerial view of the country (figs/terrain.py) instead of the flat green ground, with the aeroplane
of the model (figs/sprites.py) at the five places where the old drawing had its own, same heading and place. The small aeroplanes in the tags and the numbered callouts are the old figure's."""
from reskin import LOOK

from figs import h_plan

# the five aeroplanes of the old drawing: where, and which way (its rotate() turns the nose, which pointed east, clockwise; the picture of the model points north: 90 more)
PLANES = [(140, 75, 180), (90, 178, 110), (230, 235, 0), (570, 178, 250), (515, 75, 180)]
SPRITES = [{"name": "sprite-top", "at": [x, y], "width": 43, "angle": a + 90, **LOOK} for x, y, a in PLANES]


def plate():
    return {
        "id": "fig-26-01-circuit",
        "replaces": "fig-26-01-circuit.svg",
        "book_file": "plate-26-01-circuit.jpg",
        "caption": "Figure 26-1. The circuit in the example aeroplane, with speed and flap setting at each point",
        "desc": "Figure 26-1. The circuit in the example aeroplane, with speed and flap setting at each point",
        "legend": [
            "Line up on runway 27, checks complete (Chapter 25), flaps up in this example.",
            "Full power; rotate at `VR` 55 kt.",
            "Climb at `VY` 75 kt; after-takeoff checks at a safe height.",
            "Crosswind turn beyond the runway end, no lower than your school's height.",
            "Downwind at circuit height: circuit power, before-landing checks.",
            "Abeam the threshold: power back, descent begins; below `VFE` 90 kt, flaps 10°.",
            "Base, with the threshold about 45° behind: flaps 20°. Look along final first.",
            "Final: flaps 30°, 65 kt, stable by the gate (Figure 26-3).",
            "The aiming point.",
            "Wind from the west.",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": h_plan.layer({
            "svg": "fig-26-01-circuit.svg",
            "remove": [r'<circle cx="[\d.]+" cy="[\d.]+" r="[\d.]+" fill="#9db38d" opacity="0.7"/>'],                  # the bushes of the old ground: the country has its own
            "replace": [['<rect width="640" height="450" fill="#f4f8fc"/>', '<rect x="0" y="0" width="640" height="450" fill="#ffffff"/>'],
                        ['<rect x="8" y="4" width="624" height="288" rx="10" fill="url(#f2601-land)"/>', '<rect x="8" y="4" width="624" height="288" rx="10" fill="none"/>'],
                        ['<rect x="230" y="66" width="180" height="18" rx="2" fill="url(#f2601-rwy)"/>', '<rect x="226.6" y="62.6" width="186.8" height="24.8" rx="3" fill="#B3A688" fill-opacity="0.55"/><rect x="230" y="66" width="180" height="18" rx="2" fill="url(#hpAsphalt)"/>']],
            "drop": [['<g transform="translate(140 75) rotate(180) scale(0.95)"', '<ellipse cx="330" cy="56" rx="7" ry="2.4"', {"sprites": SPRITES}]],
        }, "terrain-26-01", seed=261, kind="plain", veil=0.30),
    }
