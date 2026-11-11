"""Figure 26-5. Crab and wing-low crosswind landings, from above and from behind at touchdown. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-26-05-crab-wing-low",
        "replaces": "fig-26-05-crab-wing-low.svg",
        "book_file": "plate-26-05-crab-wing-low.jpg",
        "caption": "Figure 26-5. Crab and wing-low crosswind landings, from above and from behind at touchdown",
        "desc": "Figure 26-5. Crab and wing-low crosswind landings, from above and from behind at touchdown",
        "legend": [
            "Wind from the left in both panels.",
            "Crab: nose into the wind, track on the centreline.",
            "Just before touchdown, right rudder aligns the nose and a little left aileron stops the drift.",
            "Wing-low: a crab on a long final…",
            "…changed before the round out: rudder aligns the nose, aileron lowers the upwind wing.",
            "Touchdown aligned, on the centreline.",
            "Crab at touchdown, from behind: wings nearly level, right rudder.",
            "Wing-low from behind: left wing low, left aileron up, right rudder.",
            "The upwind main wheel touches first.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {
            "svg": "fig-26-05-crab-wing-low.svg",
            # the two aeroplanes seen from behind at the bottom (level, and with the wing low) are the model; the blue marks of the controls stay on them
            "drop": [
                ['<g transform="translate(22.5 324.6)">', '<polygon points="122.0,358.7', {"sprites": [{"name": "sprite-rear", "at": [122, 360.0], "width": 199, **LOOK}]}],
                ['<g transform="translate(348.5 321.7)">', '<polygon points="448.0,355.8', {"sprites": [{"name": "sprite-rear", "at": [448, 357.7], "width": 199, **LOOK}]}],
            ],
        },
    }
