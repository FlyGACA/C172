"""Figure 27-4. A 360° steep turn to the left: plan view, and the bank, back pressure and power around the turn. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-27-04-steep-turn-sequence",
        "replaces": "fig-27-04-steep-turn-sequence.svg",
        "book_file": "plate-27-04-steep-turn-sequence.jpg",
        "caption": "Figure 27-4. A 360° steep turn to the left: plan view, and the bank, back pressure and power around the turn",
        "desc": "Figure 27-4. A 360° steep turn to the left: plan view, and the bank, back pressure and power around the turn",
        "legend": [
            "The reference point on the entry heading.",
            "The roll-out begins about 22° before the entry heading.",
            "Bank angle.",
            "Elevator back pressure.",
            "Power.",
            "Roll-in: back pressure and power come in before 30° of bank.",
            "Steady turn at 45°.",
            "Roll-out: bank, back pressure and power come off together.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-27-04-steep-turn-sequence.svg"},
    }
