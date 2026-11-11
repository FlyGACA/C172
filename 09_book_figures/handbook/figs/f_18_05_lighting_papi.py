"""Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-18-05-lighting-papi",
        "replaces": "fig-18-05-lighting-papi.svg",
        "book_file": "plate-18-05-lighting-papi.jpg",
        "caption": "Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI",
        "desc": "Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI",
        "legend": [
            "Approach lights, white, along the extended centreline, here with one crossbar.",
            "Threshold lights, green.",
            "Runway edge lights, white.",
            "Runway end lights, red.",
            "PAPI: four units in a row on the left of the runway, near the touchdown point.",
            "Taxiway edge lights, blue.",
            "Taxiway centreline lights, green.",
            "Stop bar, red, across the taxiway at the runway-holding position.",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": {"svg": "fig-18-05-lighting-papi.svg"},
    }
