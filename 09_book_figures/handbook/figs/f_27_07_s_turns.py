"""Figure 27-7. S-turns across a road: the bank changes in each half circle. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-27-07-s-turns",
        "replaces": "fig-27-07-s-turns.svg",
        "book_file": "plate-27-07-s-turns.jpg",
        "caption": "Figure 27-7. S-turns across a road: the bank changes in each half circle",
        "desc": "Figure 27-7. S-turns across a road: the bank changes in each half circle",
        "legend": [
            "Wind, 15 kt, at right angles to the road.",
            "Crossing downwind, wings level.",
            "Steepest bank, 40°.",
            "Crosswind point: about 32°, nose about 10° into the wind.",
            "Shallowest bank, 23°, coming round to upwind.",
            "Crossing upwind, wings level: reverse the turn.",
            "Upwind half circle: the bank steepens from 23° through 32° to 40°, nose again into the wind.",
            "A vehicle on the road: keep your distance (§91.67).",
        ],
        "canvas": [640, 420 + 260],
        # above the drawing, the same in 3D (figs/oeth3d.s_turns_27_07): the half circles at 1 000 ft over the road, the shadow the ground track, the aeroplanes enlarged and banked
        "top3d": {"render": "farm-27-07-s-turns", "height": 260, "v_mid": 0.42, "uid": "s277", "callouts": [
            (1, "wind", 150.0, 32.0), (2, "cross_dn", 56.0, 96.0), (3, "steep", 48.0, 172.0), (4, "xw", 150.0, 232.0), (5, "shallow", 316.0, 222.0),
            (6, "cross_up", 254.0, 52.0), (7, "up_half", 426.0, 40.0), (8, "vehicle", 228.0, 236.0)]},
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-27-07-s-turns.svg"}, "terrain-27-07", seed=27, kind='farm', veil=0.26, fields=[(0.2, 0.2, 0.07), (0.82, 0.8, 0.07)]),
    }
