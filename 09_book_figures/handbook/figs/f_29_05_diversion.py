"""Figure 29-5. A diversion from the midpoint of leg A to B to alternate C. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-29-05-diversion",
        "replaces": "fig-29-05-diversion.svg",
        "book_file": "plate-29-05-diversion.jpg",
        "caption": "Figure 29-5. A diversion from the midpoint of leg A to B to alternate C",
        "desc": "Figure 29-5. A diversion from the midpoint of leg A to B to alternate C",
        "legend": [
            "Leg A to B as flown.",
            "Checkpoint 2, 09:28: decide and turn.",
            "The pencil estimate.",
            "The measured course, 217°, with 10 NM ticks.",
            "Heading 230° true, crabbed into the wind.",
            "Wind 340° at 28 kt.",
            "The pipeline, 09:33: first check.",
            "Top of descent, 09:38.",
            "Alternate C, 09:46.",
            "The abandoned leg.",
            "The estimate, in amber.",
            "The refined figures, in blue.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-29-05-diversion.svg"},
    }
