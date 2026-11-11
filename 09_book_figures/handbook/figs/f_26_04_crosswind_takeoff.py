"""Figure 26-4. A crosswind takeoff from above, with the control positions at each stage. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-26-04-crosswind-takeoff",
        "replaces": "fig-26-04-crosswind-takeoff.svg",
        "book_file": "plate-26-04-crosswind-takeoff.jpg",
        "caption": "Figure 26-4. A crosswind takeoff from above, with the control positions at each stage",
        "desc": "Figure 26-4. A crosswind takeoff from above, with the control positions at each stage",
        "legend": [
            "Wind from the left.",
            "Start of the roll: control wheel fully into the wind. The aeroplane weathervanes into the wind (amber arrow) and the propeller pulls left, so right rudder keeps it straight.",
            "As the ailerons bite: less aileron, wings level.",
            "Lift-off: held on a little longer, then lifted off positively, upwind wing slightly low.",
            "Once clear: crab into the wind, wings level, on the extended centreline.",
            "The control wheel as you see it; dashed grey: neutral.",
            "The rudder pedals; blue: the pedal pushed.",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-26-04-crosswind-takeoff.svg"},
    }
