"""Figure 14-5. A lifted parcel in stable and in conditionally unstable air. The diagram of the book's figure (the temperature profiles, the parcel, the inversion, the numbered callouts)
with the clouds of the model of the sky in place of the cartoon ones (reskin.py, figs/clouds.py): the layer cloud a forced parcel makes in the stable air, and the tower it builds
by itself in the unstable air."""

LAYER = '<path d="M 64.8 266.7'
AFTER_LAYER = '<circle cx="198.6" cy="266.7" r="4.2"'
TOWER = '<path d="M 553.7 266.7'
AFTER_TOWER = '<polyline points="595.1,380 403.9,40" fill="none" stroke="#ffffff"'


def plate():
    return {
        "id": "fig-14-05-stability",
        "replaces": "fig-14-05-stability.svg",
        "book_file": "plate-14-05-stability.jpg",
        "caption": "Figure 14-5. A lifted parcel in stable and in conditionally unstable air",
        "desc": "Figure 14-5. A lifted parcel in stable and in conditionally unstable air",
        "legend": [
            "Stable day: the surrounding air cools 1 °C per 1 000 ft.",
            "The lifted parcel.",
            "Its dew point, meeting the parcel temperature at the cloud base, 4 000 ft.",
            "An inversion.",
            "Colder than its surroundings, the parcel sinks back; forced up, it forms layer cloud.",
            "Conditionally unstable day: the surrounding air cools 2.5 °C per 1 000 ft.",
            "Below 6 000 ft the parcel is colder and needs lifting.",
            "At 6 000 ft it is as warm as its surroundings.",
            "Above, it is warmer and rises by itself, building towering cloud.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-05-stability.svg",
            "drop": [
                [LAYER, AFTER_LAYER, {"sprites": [{"name": "cloud-stratus", "at": [123, 256], "width": 120, "height": 22}]}],
                [TOWER, AFTER_TOWER, {"sprites": [{"name": "cloud-tcu", "at": [585, 158], "width": 88, "height": 218}]}],
            ],
        },
    }
