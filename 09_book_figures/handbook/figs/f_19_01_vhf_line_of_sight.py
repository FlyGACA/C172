"""Figure 19-1. VHF radio reaches only as far as the line of sight. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-19-01-vhf-line-of-sight",
        "replaces": "fig-19-01-vhf-line-of-sight.svg",
        "book_file": "plate-19-01-vhf-line-of-sight.jpg",
        "caption": "Figure 19-1. VHF radio reaches only as far as the line of sight",
        "desc": "Figure 19-1. VHF radio reaches only as far as the line of sight",
        "legend": [
            "A ground station, antenna height ignored.",
            "The line of sight from the station.",
            "The radio shadow below it.",
            "An aircraft above the line: two-way contact.",
            "An aircraft at the same distance, lower: the bulge of the earth blocks the path.",
            "A ridge casts its own shadow.",
            "An aircraft behind the ridge: no contact, even close to the station.",
            "Height of the line of sight above the ground, in feet, at 48, 72 and 96 NM.",
        ],
        "canvas": [640, 370],
        "background": "pale",
        "reskin": {"svg": "fig-19-01-vhf-line-of-sight.svg"},
    }
