"""Figure 30-2. Engine failure after takeoff: the cone ahead, and why the turn back fails. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-30-02-engine-failure-after-takeoff",
        "replaces": "fig-30-02-engine-failure-after-takeoff.svg",
        "book_file": "plate-30-02-engine-failure-after-takeoff.jpg",
        "caption": "Figure 30-2. Engine failure after takeoff: the cone ahead, and why the turn back fails",
        "desc": "Figure 30-2. Engine failure after takeoff: the cone ahead, and why the turn back fails",
        "legend": [
            "The wind: you took off into it.",
            "Runway ahead: close the throttle and land on it.",
            "Failure with the runway behind: nose down to best glide.",
            "The cone ahead, within gentle turns.",
            "Open fields.",
            "Buildings and wires: steer between them. Hitting one at the end of a slide is far less dangerous than at flying speed [[FAA-H-8083-3C ch. 18]].",
            "The turn back: more than 180° of steep gliding turn near the ground.",
            "Where it ends: beside the runway, low, and downwind.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-30-02-engine-failure-after-takeoff.svg"}, "terrain-30-02", seed=302, kind="farm", veil=0.26, fields=[(0.84, 0.74, 0.06)], village=(0.72, 0.30)),
    }
