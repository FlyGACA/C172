"""Figure 21-4. DME slant range and ground distance at 6 000 ft above the station. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-04-slant-range",
        "replaces": "fig-21-04-slant-range.svg",
        "book_file": "plate-21-04-slant-range.jpg",
        "caption": "Figure 21-4. DME slant range and ground distance at 6 000 ft above the station",
        "desc": "Figure 21-4. DME slant range and ground distance at 6 000 ft above the station",
        "legend": [
            "Overhead: the DME shows 1.0 NM; the ground distance is zero.",
            "Height above the station: 6 000 ft, about 0.99 NM.",
            "Slant range on the DME: 2.0 NM.",
            "Ground distance: 1.7 NM.",
            "Far out, 30.0 NM on the DME is 30.0 NM over the ground.",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-21-04-slant-range.svg"},
    }
