"""Figure 25-8 of the handbook: a trainer secured on a summer ramp. The model from its left side, on the ground, with its chocks, the sun and the wind;
the tie-down ropes, the plugs and the cover are drawn over it (they are too small to see at this scale if they are drawn true)."""
import math

RED, AMBER, BLUE, ORANGE = "#D32F2F", "#E39A1B", "#1D4ED8", "#C2570C"


def plate():
    chock = {"kind": "wedge", "size": [0.20, 0.34, 0.14], "colour": AMBER}
    props = [
        {**chock, "at": [1.276, 0.085, -0.012]},                               # in front of the left main wheel, rising toward it
        {**chock, "at": [1.276, 0.841, -0.012], "rot": [0, 0, 180]},           # behind it
    ]
    anchors = {
        "chock": [1.276, 0.86, 0.07], "windscreen": [0.0, -0.39, 1.66],
        "plug": [0.222, -1.875, 1.36], "plug_a": [0.222, -1.95, 1.50], "plug_b": [0.222, -1.80, 1.50], "plug_c": [0.222, -1.80, 1.24], "plug_d": [0.222, -1.95, 1.24],
        "plug_flag_a": [0.222, -1.93, 1.20], "plug_flag_b": [0.222, -1.83, 1.20], "plug_flag_c": [0.222, -1.83, 0.92], "plug_flag_d": [0.222, -1.93, 0.92],
        "pitot": [1.75, -0.21, 1.747], "pitot_a": [1.75, -0.30, 1.78], "pitot_b": [1.75, -0.10, 1.78], "pitot_c": [1.75, -0.10, 1.71], "pitot_d": [1.75, -0.30, 1.71],
        "pitot_flag_a": [1.75, -0.28, 1.70], "pitot_flag_b": [1.75, -0.20, 1.70], "pitot_flag_c": [1.75, -0.20, 1.40], "pitot_flag_d": [1.75, -0.28, 1.40],
        "wing_rope": [3.04, 0.19, 0.9], "tail_rope": [0.0, 5.05, 0.3],
        "cabin": [0.30, 0.40, 1.60], "ground": [1.5, 1.96, -0.012],
    }
    curves = {
        "wing": {"line": [[2.65, 0.05, 1.82], [2.85, 0.12, 1.35], [3.05, 0.2, 0.9], [3.25, 0.28, 0.45], [3.44, 0.34, -0.005]]},
        "tail": {"line": [[0.0, 4.82, 0.62], [0.0, 4.92, 0.42], [0.0, 5.05, 0.25], [0.0, 5.18, 0.1], [0.0, 5.30, -0.005]]},
        "nose": {"line": [[0.0, -0.5, 0.34], [0.0, -0.66, 0.24], [0.0, -0.84, 0.12], [0.0, -1.06, -0.005]]},
    }
    sun = (586, 50)
    rays = "".join(f'<line x1="{sun[0] + 29 * math.cos(math.radians(a)):.1f}" y1="{sun[1] + 29 * math.sin(math.radians(a)):.1f}" x2="{sun[0] + 40 * math.cos(math.radians(a)):.1f}" y2="{sun[1] + 40 * math.sin(math.radians(a)):.1f}" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>' for a in range(0, 360, 30))
    sun_markup = (f'<circle cx="{sun[0]}" cy="{sun[1]}" r="22" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2.5"/>' + rays)
    overlays = [
        {"type": "svg", "markup": sun_markup},
        {"type": "line", "points": [[sun[0] - 22, sun[1] + 16], "cabin"], "colour": ORANGE, "width": 2.0, "dash": "7 5", "halo": True, "arrow": "end"},
        {"type": "line", "points": [[sun[0] - 8, sun[1] + 24], [470, 160]], "colour": ORANGE, "width": 2.0, "dash": "7 5", "halo": True},
        {"type": "path", "curve": "wing", "colour": ORANGE, "width": 3.0, "halo": True},
        {"type": "path", "curve": "tail", "colour": ORANGE, "width": 3.0, "halo": True},
        {"type": "path", "curve": "nose", "colour": ORANGE, "width": 3.0, "halo": True},
        {"type": "polygon", "points": ["plug_a", "plug_b", "plug_c", "plug_d"], "fill": RED, "stroke": "#FFFFFF", "width": 1.2},
        {"type": "polygon", "points": ["plug_flag_a", "plug_flag_b", "plug_flag_c", "plug_flag_d"], "fill": RED, "stroke": "#FFFFFF", "width": 1.0, "opacity": 0.92},
        {"type": "polygon", "points": ["pitot_a", "pitot_b", "pitot_c", "pitot_d"], "fill": RED, "stroke": "#FFFFFF", "width": 1.0},
        {"type": "polygon", "points": ["pitot_flag_a", "pitot_flag_b", "pitot_flag_c", "pitot_flag_d"], "fill": RED, "stroke": "#FFFFFF", "width": 1.0, "opacity": 0.92},
        {"type": "arrow", "from": [14, 196], "to": [64, 196], "colour": BLUE, "width": 3.6, "head": 14},
        {"type": "arrow", "from": [14, 222], "to": [64, 222], "colour": BLUE, "width": 3.6, "head": 14},
        {"type": "marker", "n": 1, "pos": [40, 168], "leader": False},
        {"type": "marker", "n": 2, "pos": [626, 22], "leader": False},
        {"type": "marker", "n": 3, "at": "windscreen", "pos": [196, 44], "leader": True},
        {"type": "marker", "n": 4, "at": "plug", "pos": [64, 314], "leader": True},
        {"type": "marker", "n": 5, "at": "pitot", "pos": [172, 330], "leader": True},
        {"type": "marker", "n": 6, "at": "wing_rope", "pos": [378, 330], "leader": True},
        {"type": "marker", "n": 7, "at": "tail_rope", "pos": [536, 330], "leader": True},
        {"type": "marker", "n": 8, "at": "chock", "pos": [276, 330], "leader": True},
    ]
    return {
        "id": "fig-25-08-securing",
        "replaces": "fig-25-08-securing.svg",
        "book_file": "plate-25-08-securing.jpg",
        "caption": "Figure 25-8. A trainer secured on a summer ramp",
        "desc": "The aeroplane from its left side on the ground, nose into the wind, tied down at the wings, nose and tail with its wheels chocked, plugs in the cowling inlets and a cover on the pitot tube, with the sun on the cabin.",
        "legend": [
            "Nose into the forecast wind where possible.",
            "Sun: an exposed cabin bakes instruments and avionics.",
            "Windscreen and window shades.",
            "Cowling inlet plugs with streamers.",
            "Pitot cover with streamer.",
            "Wing tie-down.",
            "Tail tie-down.",
            "Chocks.",
        ],
        "canvas": [640, 360],
        "background": "sky",
        "ground": [
            {"type": "band", "at": "ground", "colour": [222, 215, 200], "colour2": [196, 188, 170]},
            {"type": "contact", "at": "ground", "rx": 285, "ry": 4.5, "opacity": 0.38, "blur": 5},
        ],
        "render": {
            "camera": {"view": "side", "target": {"part": "WING_L.strut", "at": [0.5, 0.5, 0.5], "add": [0.0, 2.1, 0.625]}, "width": 10.0, "azimuth": 180, "elevation": 0},
            "size": [2240, 1260],
            "light": "outdoor", "mirror": True, "sun_elevation": 46,
            "parked": True,
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "propeller": {"turn": 18},
            "props": props,
            "samples": 96,
            "anchors": anchors,
            "curves": curves,
        },
        "overlays": overlays,
    }
