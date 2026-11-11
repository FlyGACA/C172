"""Figure 18-3. Runway markings at a normal runway end and at a displaced threshold. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-18-03-runway-markings",
        "replaces": "fig-18-03-runway-markings.svg",
        "book_file": "plate-18-03-runway-markings.jpg",
        "caption": "Figure 18-3. Runway markings at a normal runway end and at a displaced threshold",
        "desc": "Figure 18-3. Runway markings at a normal runway end and at a displaced threshold",
        "legend": [
            "Threshold stripes: the start of the part usable for landing; wider runways have more stripes.",
            "Designator, read from the approach.",
            "Centreline: keep the nose wheel on it.",
            "Touchdown zone marking: pairs of bars, with fewer bars further on.",
            "Aiming point: a target for the approach.",
            "Side stripe: the edge of the runway.",
            "Blast pad: yellow chevrons, not for use.",
            "Displaced part of the runway: white arrows lead to the threshold.",
            "Displaced threshold: a white bar across the runway, then the threshold stripes.",
            "Length available for takeoff, and for landing from the opposite direction.",
            "Length available for landing towards the displaced threshold.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-18-03-runway-markings.svg"},
    }
