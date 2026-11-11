"""Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-25-07-run-up",
        "replaces": "fig-25-07-run-up.svg",
        "book_file": "plate-25-07-run-up.jpg",
        "caption": "Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast",
        "desc": "Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast",
        "legend": [
            "Wind.",
            "Nose into wind, nosewheel straight.",
            "Propeller blast: nothing behind you.",
            "Firm, clean surface, clear of the taxiway.",
            "Loose sand: it nicks the propeller.",
            "Runway-holding position: run up before it.",
            "The next aircraft, out of your blast.",
            "Traffic on final: look before you enter the runway.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-25-07-run-up.svg"},
    }
