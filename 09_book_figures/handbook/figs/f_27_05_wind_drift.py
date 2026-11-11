"""Figure 27-5. Drift and crab: following a road in a crosswind, and the wind triangles at 90 kt in a 15 kt wind. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-27-05-wind-drift",
        "replaces": "fig-27-05-wind-drift.svg",
        "book_file": "plate-27-05-wind-drift.jpg",
        "caption": "Figure 27-5. Drift and crab: following a road in a crosswind, and the wind triangles at 90 kt in a 15 kt wind",
        "desc": "Figure 27-5. Drift and crab: following a road in a crosswind, and the wind triangles at 90 kt in a 15 kt wind",
        "legend": [
            "Heading along the road: the wind drifts the aeroplane off it.",
            "Heading about 10° into the wind: the track stays on the road.",
            "Downwind: groundspeed 105 kt.",
            "Upwind: groundspeed 75 kt.",
            "Crosswind: heading about 10° into the wind.",
            "Track along the road at 89 kt.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-27-05-wind-drift.svg"},
    }
