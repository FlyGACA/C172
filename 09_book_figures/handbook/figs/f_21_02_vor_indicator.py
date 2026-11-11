"""Figure 21-2. The VOR indicator for four aircraft around a station, OBS set to 360. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-02-vor-indicator",
        "replaces": "fig-21-02-vor-indicator.svg",
        "book_file": "plate-21-02-vor-indicator.jpg",
        "caption": "Figure 21-2. The VOR indicator for four aircraft around a station, OBS set to 360",
        "desc": "Figure 21-2. The VOR indicator for four aircraft around a station, OBS set to 360",
        "legend": [
            "North-west of the station: `FR`, needle right.",
            "North-east: `FR`, needle left.",
            "South-east: `TO`, needle left.",
            "South-west: `TO`, needle right.",
            "The selected course, 360, through the station.",
            "The TO/FROM line, at right angles to the course; close to it neither shows.",
            "The OBS knob.",
        ],
        "canvas": [640, 460],
        "background": "pale",
        "reskin": {"svg": "fig-21-02-vor-indicator.svg"},
    }
