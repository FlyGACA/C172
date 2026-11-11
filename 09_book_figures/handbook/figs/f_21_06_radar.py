"""Figure 21-6. Primary radar, secondary radar and ADS-B. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-06-radar",
        "replaces": "fig-21-06-radar.svg",
        "book_file": "plate-21-06-radar.jpg",
        "caption": "Figure 21-6. Primary radar, secondary radar and ADS-B",
        "desc": "Figure 21-6. Primary radar, secondary radar and ADS-B",
        "legend": [
            "Primary radar: a pulse out and a faint echo back, transponder or not.",
            "Secondary radar: interrogation and reply.",
            "The reply: the code, here 4521, and the pressure altitude in hundreds of feet, here 045 for 4 500 ft.",
            "High ground hides aircraft behind it.",
            "ADS-B Out: the aircraft broadcasts its own position.",
            "On the display, a primary target: position only.",
            "A secondary target with its label: code and altitude.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-21-06-radar.svg"},
    }
