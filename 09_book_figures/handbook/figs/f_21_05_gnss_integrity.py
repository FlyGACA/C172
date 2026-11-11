"""Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-05-gnss-integrity",
        "replaces": "fig-21-05-gnss-integrity.svg",
        "book_file": "plate-21-05-gnss-integrity.jpg",
        "caption": "Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal",
        "desc": "Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal",
        "legend": [
            "Four satellites: a position in three dimensions and the time.",
            "A fifth, or four and the barometric altitude: a faulty satellite can be detected.",
            "A sixth, or five and the barometric altitude: it can be excluded.",
            "A low satellite hidden by the airframe or a bank.",
            "Interference: a stronger signal on the same frequency drowns the weak satellite signals.",
            "Positions from different sets of satellites agree: the position can be trusted.",
            "One set disagrees: a receiver with integrity monitoring warns you; one without may not.",
        ],
        "canvas": [640, 390],
        "background": "pale",
        "reskin": {"svg": "fig-21-05-gnss-integrity.svg"},
    }
