"""Figure 26-8. A forward slip from behind and from above, and its steeper approach path. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-26-08-forward-slip",
        "replaces": "fig-26-08-forward-slip.svg",
        "book_file": "plate-26-08-forward-slip.jpg",
        "caption": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "desc": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "legend": [
            "Upwind wing lowered with aileron: the bank is into the wind.",
            "Opposite rudder, here right, stops the turn.",
            "Lift tilts towards the low wing; the aeroplane moves sideways towards it, offsetting the drift.",
            "Wind from the left in both views.",
            "The nose points away from the wind.",
            "The track stays on the extended centreline.",
            "The airflow strikes the side of the aeroplane: drag rises sharply.",
            "At the same airspeed, the slip gives a much steeper path to the aiming point.",
            "Without the slip, the aeroplane lands well beyond it.",
            "Slip taken out before the round out; the landing is straight.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-08-forward-slip.svg"},
    }
