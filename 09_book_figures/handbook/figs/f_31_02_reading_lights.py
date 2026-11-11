"""Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-31-02-reading-lights",
        "replaces": "fig-31-02-reading-lights.svg",
        "book_file": "plate-31-02-reading-lights.jpg",
        "caption": "Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing",
        "desc": "Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing",
        "legend": [
            "Converging from your right: its red light.",
            "Crossing from your left, passing behind: its green light.",
            "Head-on: green and red, red on your right.",
            "Ahead, same direction: white tail light alone.",
            "Your aeroplane.",
            "A light fixed in the windscreen that grows: a collision course.",
            "A light drifting across the windscreen is passing; keep it in sight.",
            "The anticollision light flashes; stars do not.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-31-02-reading-lights.svg", "sprite_top": "sprite-top-night", "outline": False},
    }
