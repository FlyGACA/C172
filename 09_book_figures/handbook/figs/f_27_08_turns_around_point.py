"""Figure 27-8. Turns around a point: bank and groundspeed around the circle. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-27-08-turns-around-point",
        "replaces": "fig-27-08-turns-around-point.svg",
        "book_file": "plate-27-08-turns-around-point.jpg",
        "caption": "Figure 27-8. Turns around a point: bank and groundspeed around the circle",
        "desc": "Figure 27-8. Turns around a point: bank and groundspeed around the circle",
        "legend": [
            "The point, here the centre of a circular field.",
            "Wind, 15 kt.",
            "Entry downwind.",
            "Downwind: steepest bank, 40°.",
            "Turning toward upwind: about 32°, nose inside the circle.",
            "Upwind: shallowest bank, 23°.",
            "Turning toward downwind: about 32°, nose outside the circle.",
            "Groundspeed in knots (grey).",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": {"svg": "fig-27-08-turns-around-point.svg"},
    }
