"""Figure 18-1. The parts of an aerodrome seen from above. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-18-01-aerodrome-plan",
        "replaces": "fig-18-01-aerodrome-plan.svg",
        "book_file": "plate-18-01-aerodrome-plan.jpg",
        "caption": "Figure 18-1. The parts of an aerodrome seen from above",
        "desc": "Figure 18-1. The parts of an aerodrome seen from above",
        "legend": [
            "Runway 09/27.",
            "Runway designator: `09` at the west end, `27` at the east end.",
            "Parallel taxiway `A`, joined to the runway by taxiways `B`, `C` and `D`.",
            "Runway-holding position, the holding point where an aircraft stops before entering the runway.",
            "Apron.",
            "Manoeuvring area: runway and taxiways.",
            "Movement area: the manoeuvring area and the apron.",
            "Windsock.",
            "Signal area.",
            "Aerodrome control tower.",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-18-01-aerodrome-plan.svg"},
    }
