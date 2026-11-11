"""Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-25-06-taxi-wind",
        "replaces": "fig-25-06-taxi-wind.svg",
        "book_file": "plate-25-06-taxi-wind.jpg",
        "caption": "Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind",
        "desc": "Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind",
        "legend": [
            "Quartering headwind from the left: wheel turned left, into the wind (left aileron up); elevator neutral.",
            "Quartering headwind from the right: wheel turned right; elevator neutral.",
            "Quartering tailwind from the left: wheel turned right, away from the wind (left aileron down), and forward (elevator down).",
            "Quartering tailwind from the right: wheel turned left and forward.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-25-06-taxi-wind.svg"},
    }
