"""Figure 30-4. A forced-landing pattern with its key points, in plan and in profile. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-30-04-forced-landing-pattern",
        "replaces": "fig-30-04-forced-landing-pattern.svg",
        "book_file": "plate-30-04-forced-landing-pattern.jpg",
        "caption": "Figure 30-4. A forced-landing pattern with its key points, in plan and in profile",
        "desc": "Figure 30-4. A forced-landing pattern with its key points, in plan and in profile",
        "legend": [
            "Engine failure: best glide, turn toward the field.",
            "The wind.",
            "Aim point, about a third of the way into the field.",
            "High key: over the field near the aim point, heading in the landing direction.",
            "Turns over the field to lose surplus height, keeping it in sight.",
            "Low key: abeam the aim point, at about normal circuit height.",
            "Base key: judge the height; flap only when the field is made.",
            "The field, landing into wind.",
            "Too low: turn base early and shorten the path.",
            "Too high: extend downwind, then flap or a slip.",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": {"svg": "fig-30-04-forced-landing-pattern.svg"},
    }
