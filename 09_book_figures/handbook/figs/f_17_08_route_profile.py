"""Figure 17-8. The worked example in profile along the route. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-17-08-route-profile",
        "replaces": "fig-17-08-route-profile.svg",
        "book_file": "plate-17-08-route-profile.jpg",
        "caption": "Figure 17-8. The worked example in profile along the route",
        "desc": "Figure 17-8. The worked example in profile along the route",
        "legend": [
            "Control zone, Class D, to 3 500 ft: in contact with the tower.",
            "TMA, Class C, floors 3 500 ft and 4 500 ft; no clearance, so stay below.",
            "Point WADI, 8 NM.",
            "500 ft margins below the floors.",
            "Cruise at 5 500 ft.",
            "Base of Class E, 1 000 ft above the ground (dashed); Class G beneath.",
            "Descent into Class G and the circuit at B.",
            "Turning point T, 33 NM.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-17-08-route-profile.svg"},
    }
