"""Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402

BOLD = {**LOOK, "outline": {"width": 1.0, "colour": "#1F2937", "opacity": 1.0}}        # small on a white ground: a firmer edge


def plate():
    return {
        "id": "fig-28-08-cloud-escape",
        "replaces": "fig-28-08-cloud-escape.svg",
        "book_file": "plate-28-08-cloud-escape.jpg",
        "caption": "Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation",
        "desc": "Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation",
        "legend": [
            "Planned route from aerodrome A.",
            "Dust or cloud: no horizon.",
            "Wings level, then a 180° turn: one minute at standard rate.",
            "Clear air on the reciprocal heading.",
            "ATC and radar.",
            "GNSS or VOR guidance toward A.",
            "High ground: stay above the safe altitude.",
            "Aerodrome A.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-28-08-cloud-escape.svg",
            # the two aeroplanes on the track, flat silhouettes in the old figure, are the model seen from above: outbound to the east, then back to the west
            "drop": [['<path d="M 0 -12 L 1.6 -9 L 1.6 -3 L 13 1', '<path d="M 318 282 C 308.7 281.3', {"sprites": [
                {"name": "sprite-top", "at": [300, 190], "width": 40, "angle": 90, **BOLD},
                {"name": "sprite-top", "at": [366, 282], "width": 40, "angle": 270, **BOLD}]}]],
        },
    }
