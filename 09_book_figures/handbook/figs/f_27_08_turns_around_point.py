"""Figure 27-8. Turns around a point: bank and groundspeed around the circle. The diagram of the book's figure with the aeroplane of the model (reskin.py), on an aerial view of
the country (figs/terrain.py) in which the point is the centre of a field of irrigated crop, as the legend says."""
from figs import terrain

terrain.ensure("terrain-27-08", size=(2560, 1800), seed=27, kind="farm", features=("scrub", "wadis", "tracks"), fields=[(0.5, 0.5, 34 / 640.0)], veil=0.18)


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
                "canvas": [640, 450 + 260],
        # above the drawing, the same in 3D (figs/oeth3d.point_27_08): the circle at 1 000 ft round the field, its shadow the ground track, the aeroplanes enlarged and banked
        "top3d": {"render": "farm-27-08-point", "height": 260, "v_mid": 0.42, "uid": "p278", "callouts": [
            (1, "point", 384.0, 232.0), (2, "wind", 132.0, 44.0), (3, "entry", 60.0, 216.0), (4, "down", 296.0, 236.0), (5, "east", 484.0, 152.0),
            (6, "up", 384.0, 38.0), (7, "west", 160.0, 100.0)]},
        "background": "pale",
        "reskin": {"svg": "fig-27-08-turns-around-point.svg", "sprites": [{"name": "terrain-27-08", "at": [320, 225], "width": 640}], "replace": [['fill="#e3f1ec"', 'fill="none"']], "halo": True},
    }
