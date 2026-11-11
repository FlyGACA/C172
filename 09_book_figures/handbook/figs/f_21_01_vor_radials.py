"""Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-01-vor-radials",
        "replaces": "fig-21-01-vor-radials.svg",
        "book_file": "plate-21-01-vor-radials.jpg",
        "caption": "Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range",
        "desc": "Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range",
        "legend": [
            "Magnetic north, the reference for every radial.",
            "True north on a chart; the angle between them, exaggerated here, is the variation (Chapter 10). A chart's compass rose around a VOR is aligned with magnetic north.",
            "The station, a fictional VOR/DME.",
            "On the 240 radial, flying to the station: course 060.",
            "On the 060 radial, flying away from the station: also course 060.",
            "The identifier, `NKL`, in Morse code.",
            "In line of sight: a usable signal.",
            "Hidden by terrain or the earth's curve: no signal, and the warning flag appears.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-21-01-vor-radials.svg"},
    }
