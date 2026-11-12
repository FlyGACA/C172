"""Figure 27-7. S-turns across a road: the bank changes in each half circle. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-27-07-s-turns",
        "replaces": "fig-27-07-s-turns.svg",
        "book_file": "plate-27-07-s-turns.jpg",
        "caption": "Figure 27-7. S-turns across a road: the bank changes in each half circle",
        "desc": "Figure 27-7. S-turns across a road: the bank changes in each half circle",
        "legend": [
            "Wind, 15 kt, at right angles to the road.",
            "Crossing downwind, wings level.",
            "Steepest bank, 40°.",
            "Crosswind point: about 32°, nose about 10° into the wind.",
            "Shallowest bank, 23°, coming round to upwind.",
            "Crossing upwind, wings level: reverse the turn.",
            "Upwind half circle: the bank steepens from 23° through 32° to 40°, nose again into the wind.",
            "A vehicle on the road: keep your distance (§91.67).",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-27-07-s-turns.svg"}, "terrain-27-07", seed=27, kind='farm', veil=0.26, fields=[(0.2, 0.2, 0.07), (0.82, 0.8, 0.07)]),
    }
