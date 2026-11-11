"""Figure 26-3. The stabilized-approach gate and the go-around sequence. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-26-03-gate-go-around",
        "replaces": "fig-26-03-gate-go-around.svg",
        "book_file": "plate-26-03-gate-go-around.jpg",
        "caption": "Figure 26-3. The stabilized-approach gate and the go-around sequence",
        "desc": "Figure 26-3. The stabilized-approach gate and the go-around sequence",
        "legend": [
            "The gate, at 500 ft above the aerodrome in the FAA's guidance.",
            "The 300 ft line.",
            "Stable: continue to land.",
            "High and fast: not stable at the gate.",
            "Go around.",
            "Full power at once.",
            "Descent stopped, then flaps 20°.",
            "Positive climb at `VY` 75 kt; flaps 10° and then 0°.",
            "Moved to one side, runway in sight.",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": {"svg": "fig-26-03-gate-go-around.svg"},
    }
