"""Figure 7-1 of the handbook: the three axes of an aeroplane and the control surfaces that rotate it about each one.
The model in level flight seen from the front left and above, the three axes through the centre of gravity as dashed lines
with a turning arrow at the end of each, the primary controls amber and the flaps blue."""


def plate():
    cg = [0, 0.0, 1.3]
    axes = {"roll": ([0, -3.4, 1.3], [0, 6.6, 1.3]), "pitch": ([-6.1, 0, 1.3], [6.1, 0, 1.3]), "yaw": ([0, 0, 0.1], [0, 0, 3.9])}
    return {
        "id": "fig-07-01-three-axes",
        "replaces": "fig-07-01-three-axes.svg",
        "book_file": "plate-07-01-three-axes.jpg",
        "caption": "Figure 7-1. The three axes of an aeroplane and the control surfaces that rotate it about each one",
        "desc": "The aeroplane from the front left and above with its three axes through the centre of gravity and a turning arrow on each, the ailerons, elevator and rudder in amber and the flaps in blue.",
        "legend": [
            "Longitudinal axis: roll, controlled by the ailerons.",
            "Lateral axis: pitch, controlled by the elevator.",
            "Vertical axis: yaw, controlled by the rudder.",
            "Aileron. The two ailerons move in opposite directions.",
            "Elevator.",
            "Rudder.",
            "Flap, a secondary control. Both flaps move together.",
            "Centre of gravity, where the three axes meet.",
        ],
        "canvas": [640, 360],
        "background": "sky",
        "render": {
            "camera": {"view": "side", "target": [0, 1.6, 1.5], "width": 14.6, "azimuth": 143, "elevation": 22},
            "size": [2560, 1440],
            "light": "outdoor",
            "pitch": {"deg": 3.0, "about": [0, 0, 1.3]},
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "tint": [
                {"parts": ["WING_L.aileron", "WING_R.aileron", "EMPENNAGE.elevator", "EMPENNAGE.rudder"], "colour": "#2A1200", "glow": "#E87A00", "emission": 0.62},
                {"parts": ["WING_L.flap", "WING_R.flap"], "colour": "#041238", "glow": "#2E6CF4", "emission": 0.62},
            ],
            "samples": 96,
            "anchors": {
                "cg": cg,
                "roll_end": axes["roll"][0], "roll_tail": axes["roll"][1],
                "pitch_end": axes["pitch"][0], "pitch_far": axes["pitch"][1],
                "yaw_end": axes["yaw"][1], "yaw_low": axes["yaw"][0],
                "aileron": {"visible": "WING_L.aileron", "at": [0.5, 0.5]},
                "elevator": {"visible": "EMPENNAGE.elevator", "at": [0.85, 0.75]},
                "rudder": {"visible": "EMPENNAGE.rudder", "at": [0.5, 0.35]},
                "flap": {"visible": "WING_L.flap", "at": [0.5, 0.5]},
            },
            "curves": {
                "roll_axis": {"line": axes["roll"]},
                "pitch_axis": {"line": axes["pitch"]},
                "yaw_axis": {"line": axes["yaw"]},
                "roll_turn": {"arc": {"centre": [0, -3.4, 1.3], "axis": [0, 1, 0], "ref": [0, 0, 1], "radius": 0.95, "from": 40, "to": 330, "n": 48}},
                "pitch_turn": {"arc": {"centre": [6.1, 0, 1.3], "axis": [1, 0, 0], "ref": [0, 0, 1], "radius": 0.95, "from": 40, "to": 330, "n": 48}},
                "yaw_turn": {"arc": {"centre": [0, 0, 3.9], "axis": [0, 0, 1], "ref": [1, 0, 0], "radius": 1.05, "from": 30, "to": 320, "n": 48}},
            },
        },
        "overlays": [
            {"type": "path", "curve": "roll_axis", "colour": "#3B54C4", "width": 1.8, "dash": "7 5"},
            {"type": "path", "curve": "pitch_axis", "colour": "#3B54C4", "width": 1.8, "dash": "7 5"},
            {"type": "path", "curve": "yaw_axis", "colour": "#3B54C4", "width": 1.8, "dash": "7 5"},
            {"type": "path", "curve": "roll_turn", "colour": "#1F8A5B", "width": 3, "arrow": "end"},
            {"type": "path", "curve": "pitch_turn", "colour": "#1F8A5B", "width": 3, "arrow": "end"},
            {"type": "path", "curve": "yaw_turn", "colour": "#1F8A5B", "width": 3, "arrow": "end"},
            {"type": "cg", "at": "cg"},
            {"type": "marker", "n": 1, "at": "roll_end", "pos": [60, 150], "leader": True},
            {"type": "marker", "n": 2, "at": "pitch_far", "pos": [470, 322], "leader": True},
            {"type": "marker", "n": 3, "at": "yaw_end", "pos": [380, 30], "leader": True},
            {"type": "marker", "n": 4, "at": "aileron", "pos": [525, 265], "leader": True},
            {"type": "marker", "n": 5, "at": "elevator", "pos": [590, 212], "leader": True},
            {"type": "marker", "n": 6, "at": "rudder", "pos": [585, 60], "leader": True},
            {"type": "marker", "n": 7, "at": "flap", "pos": [345, 332], "leader": True},
            {"type": "marker", "n": 8, "at": "cg", "pos": [232, 332], "leader": True, "gap": 11},
        ],
    }
