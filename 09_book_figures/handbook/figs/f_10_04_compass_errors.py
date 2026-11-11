"""Figure 10-4. Compass turning and acceleration errors in the northern hemisphere. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-10-04-compass-errors",
        "replaces": "fig-10-04-compass-errors.svg",
        "book_file": "plate-10-04-compass-errors.jpg",
        "caption": "Figure 10-4. Compass turning and acceleration errors in the northern hemisphere",
        "desc": "Figure 10-4. Compass turning and acceleration errors in the northern hemisphere",
        "legend": [
            "Turning onto north, here a right turn from west: the compass lags, so roll out while it still reads short of 360°.",
            "Turning onto south, here a right turn from east: the compass leads, so roll out after it passes 180°.",
            "On east and west headings the turning error is small.",
            "Accelerating on an easterly heading: a false turn towards north (dashed arrow).",
            "Decelerating on an easterly heading: a false turn towards south.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-10-04-compass-errors.svg"},
    }
