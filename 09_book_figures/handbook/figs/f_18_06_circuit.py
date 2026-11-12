"""Figure 18-6. The aerodrome traffic circuit from above and from the side. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-18-06-circuit",
        "replaces": "fig-18-06-circuit.svg",
        "book_file": "plate-18-06-circuit.jpg",
        "caption": "Figure 18-6. The aerodrome traffic circuit from above and from the side",
        "desc": "Figure 18-6. The aerodrome traffic circuit from above and from the side",
        "legend": [
            "Upwind leg: climb straight ahead after takeoff.",
            "Crosswind leg, at right angles to the runway beyond its end.",
            "Downwind leg, parallel to the runway, at circuit height.",
            "Base leg, descending.",
            "Final approach, lined up with the runway.",
            "Joining on a 45° line towards the middle of the downwind leg, at circuit height.",
            "Downwind checks.",
            "Abeam the threshold: reduce power and begin the descent.",
            "Turn on to base when the threshold is about 45° behind you.",
            "Leaving: straight out, or with a 45° turn in the direction of the circuit.",
        ],
        "canvas": [640, 610],
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-18-06-circuit.svg"}, "terrain-18-06", seed=186, kind="plain", veil=0.30, markup=h_plan.panel("hp186", 8, 394, 624, 208, ground_y=578)),
    }
