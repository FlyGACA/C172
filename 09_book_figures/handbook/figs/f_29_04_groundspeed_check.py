"""Figure 29-4. A groundspeed check between two fixes, and the revised estimate for B. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-29-04-groundspeed-check",
        "replaces": "fig-29-04-groundspeed-check.svg",
        "book_file": "plate-29-04-groundspeed-check.jpg",
        "caption": "Figure 29-4. A groundspeed check between two fixes, and the revised estimate for B",
        "desc": "Figure 29-4. A groundspeed check between two fixes, and the revised estimate for B",
        "legend": [
            "Checkpoint 1: planned (grey) and actual (blue).",
            "Checkpoint 2.",
            "B: planned and revised.",
            "20 NM in 15 minutes.",
            "Groundspeed.",
            "Time to B.",
            "Minutes late.",
        ],
        "canvas": [640, 305],
        "background": "pale",
        "reskin": {"svg": "fig-29-04-groundspeed-check.svg"},
    }
