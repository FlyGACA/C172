"""Figure 26-8. A forward slip from behind and from above, and its steeper approach path. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-26-08-forward-slip",
        "replaces": "fig-26-08-forward-slip.svg",
        "book_file": "plate-26-08-forward-slip.jpg",
        "caption": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "desc": "Figure 26-8. A forward slip from behind and from above, and its steeper approach path",
        "legend": [
            "Upwind wing lowered with aileron: the bank is into the wind.",
            "Opposite rudder, here right, stops the turn.",
            "Lift tilts towards the low wing; the aeroplane moves sideways towards it, offsetting the drift.",
            "Wind from the left in both views.",
            "The nose points away from the wind.",
            "The track stays on the extended centreline.",
            "The airflow strikes the side of the aeroplane: drag rises sharply.",
            "At the same airspeed, the slip gives a much steeper path to the aiming point.",
            "Without the slip, the aeroplane lands well beyond it.",
            "Slip taken out before the round out; the landing is straight.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {
            "svg": "fig-26-08-forward-slip.svg",
            # the aeroplane seen from behind with the upwind wing down (a drawing in the old figure) is the model from behind, banked 18 degrees to the left; the aileron
            # up on the low wing, down on the high one, and the right rudder are marked on it as before (the old marks, drawn on the old drawing's proportions, redrawn on this one)
            "drop": [['<g transform="rotate(-18 170 124)">', '<line x1="170" y1="104" x2="149.1" y2="39.7"', {
                "sprites": [{"name": "sprite-rear", "at": [169.1, 121.2], "width": 210, "angle": -18, **LOOK}],
                "markup": '<g transform="rotate(-18 170 124)">'
                          '<rect x="68" y="101.6" width="30" height="3" rx="1" fill="#1d4ed8"/><rect x="212" y="112.6" width="30" height="3" rx="1" fill="#1d4ed8"/>'
                          '<polygon points="170.5,98.6 176.5,99.6 176.5,106.4 170.5,106.8" fill="#1d4ed8"/></g>'}]],
        },
    }
