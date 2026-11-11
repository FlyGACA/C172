"""Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-16-07-vfr-minimums",
        "replaces": "fig-16-07-vfr-minimums.svg",
        "book_file": "plate-16-07-vfr-minimums.jpg",
        "caption": "Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome",
        "desc": "Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome",
        "legend": [
            "500 ft below cloud.",
            "1 000 ft above cloud.",
            "2 000 ft horizontally from cloud.",
            "Flight visibility 5 km.",
            "The cloud.",
            "Ceiling at least 1 000 ft to fly beneath it within controlled airspace designated to the surface for an aerodrome [[§91.165(d)]].",
            "Ground visibility at least 5 km to take off, land or enter the circuit in the surface area of Class B, C, D or E airspace; flight visibility if none is reported [[§91.165(e)]].",
            "The surface area of controlled airspace.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-16-07-vfr-minimums.svg"},
    }
