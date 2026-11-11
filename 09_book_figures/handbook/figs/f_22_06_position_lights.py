"""Figure 22-6 of the handbook: position lights and what they tell you at night.
The model from above at night with its lights on and the three sectors in which each can be seen, and four views of what
another pilot sees: the same aeroplane from the front left, the front right, head on and from behind, with only the lights
that can be seen from there."""

RED, GREEN, WHITE = "#FF3B3B", "#22E07E", "#FFFFFF"

PANEL_W, PANEL_H = 132, 96
PANELS = {"v5": (338, 44), "v6": (490, 44), "v7": (338, 206), "v8": (490, 206)}

NAV = {
    "nav_left": {"part": "WING_L.nav_light", "at": [0.5, 0.5, 0.5]},
    "nav_right": {"part": "WING_R.nav_light", "at": [0.5, 0.5, 0.5]},
    "nav_tail": {"part": "ELECTRICAL.tail_nav_light", "at": [0.5, 0.5, 0.5]},
}
LAMP = {"red": ("WING_L.nav_light", RED), "green": ("WING_R.nav_light", GREEN), "white": ("ELECTRICAL.tail_nav_light", WHITE)}


def inset(name, azimuth, across, lights, width=14.6, elevation=7.0):
    """The aeroplane from another pilot's seat, small and dark, with the lights that show from there. `across` moves it
    along the picture (metres, positive to the right of the panel)."""
    import math
    az = math.radians(azimuth)
    right = (math.sin(az), -math.cos(az))                 # the camera's right on the ground: the aircraft moves right when the target moves left
    target = [0.0 - across * right[0], 1.6 - across * right[1], 1.15]
    x0, y0 = PANELS[name]
    return {
        "name": name, "box": [x0, y0, PANEL_W, PANEL_H],
        "render": {
            "camera": {"view": "side", "target": target, "width": width, "azimuth": azimuth, "elevation": elevation},
            "size": [1056, 768],
            "light": "night",
            "pitch": {"deg": 0.0, "about": [0, 0, 1.3]},
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "glow": [{"parts": [LAMP[c][0]], "colour": LAMP[c][1], "strength": 30} for c in lights],
            "samples": 96,
            "anchors": dict(NAV),
        },
    }


def plate():
    layers = [{
        "name": "top", "box": [8, 22, 320, 320],
        "render": {
            "camera": {"view": "side", "target": [0, 2.0, 0.8], "width": 18.4, "azimuth": 0, "elevation": 90, "up": [0, -1, 0]},
            "size": [1280, 1280],
            "light": "night",
            "pitch": {"deg": 0.0, "about": [0, 0, 1.3]},
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "glow": [
                {"parts": ["WING_L.nav_light"], "colour": RED, "strength": 30},
                {"parts": ["WING_R.nav_light"], "colour": GREEN, "strength": 30},
                {"parts": ["ELECTRICAL.tail_nav_light"], "colour": WHITE, "strength": 30},
                {"parts": ["ELECTRICAL.beacon"], "colour": RED, "strength": 30},
            ],
            "samples": 96,
            "anchors": {"centre": [0, 0.35, 1.3], **NAV, "beacon": {"part": "ELECTRICAL.beacon", "at": [0.5, 0.5, 0.5]}},
        },
    },
        inset("v5", 125, 2.1, ["red"]),                    # front left: the red light, and the aeroplane to the right of the middle
        inset("v6", 55, -2.1, ["green"]),                  # front right: the green light, to the left of the middle
        inset("v7", 90, 0.0, ["red", "green"], width=15.6),            # head on: both, red on the right
        inset("v8", -90, 0.0, ["white"], width=15.6),                  # from behind: the white light alone
    ]
    ground = [
        {"type": "wedge", "at": "top.centre", "r": 148, "from": -110, "to": 0, "colour": RED, "opacity": 0.42},
        {"type": "wedge", "at": "top.centre", "r": 148, "from": 0, "to": 110, "colour": GREEN, "opacity": 0.38},
        {"type": "wedge", "at": "top.centre", "r": 148, "from": 110, "to": 250, "colour": WHITE, "opacity": 0.26},
    ]
    overlays = [
        {"type": "glowdot", "at": "top.nav_left", "r": 15, "colour": RED},
        {"type": "glowdot", "at": "top.nav_right", "r": 15, "colour": GREEN},
        {"type": "glowdot", "at": "top.nav_tail", "r": 13, "colour": WHITE},
        {"type": "glowdot", "at": "top.beacon", "r": 15, "colour": RED},
    ]
    for name, (x0, y0) in PANELS.items():
        overlays.append({"type": "svg", "markup": f'<rect x="{x0}" y="{y0}" width="{PANEL_W}" height="{PANEL_H}" rx="9" fill="none" stroke="#FFFFFF" stroke-opacity=".26" stroke-width="1"/>'})
        ground.append({"type": "dots", "from": [x0 + PANEL_W / 2, y0 + 9], "to": [x0 + PANEL_W / 2, y0 + PANEL_H - 9], "step": 5.0, "r": 0.55, "colour": "#8FA0C4", "opacity": 0.42})
    for name, lights in (("v5", [("nav_left", RED)]), ("v6", [("nav_right", GREEN)]), ("v7", [("nav_left", RED), ("nav_right", GREEN)]), ("v8", [("nav_tail", WHITE)])):
        for anchor, c in lights:
            overlays.append({"type": "glowdot", "at": f"{name}.{anchor}", "r": 9, "colour": c})
    overlays += [
        {"type": "marker", "n": 1, "at": "top.nav_left", "pos": [52, 62], "leader": True, "gap": 7},
        {"type": "marker", "n": 2, "at": "top.nav_right", "pos": [286, 62], "leader": True, "gap": 7},
        {"type": "marker", "n": 3, "at": "top.nav_tail", "pos": [262, 322], "leader": True, "gap": 7},
        {"type": "marker", "n": 4, "at": "top.beacon", "pos": [70, 322], "leader": True, "gap": 7},
        {"type": "marker", "n": 5, "pos": [338, 44]}, {"type": "marker", "n": 6, "pos": [490, 44]},
        {"type": "marker", "n": 7, "pos": [338, 206]}, {"type": "marker", "n": 8, "pos": [490, 206]},
    ]
    return {
        "id": "fig-22-06-position-lights",
        "replaces": "fig-22-06-position-lights.svg",
        "book_file": "plate-22-06-position-lights.jpg",
        "caption": "Figure 22-6. Position lights and what they tell you at night",
        "desc": "The aeroplane seen from above at night with its red, green and white lights and the sectors where each shows, and four views of what another pilot sees.",
        "legend": [
            "Red light, left wingtip: seen from ahead and from the left.",
            "Green light, right wingtip: seen from ahead and from the right.",
            "White light, tail: seen from behind.",
            "Anticollision light, here a red beacon; many aeroplanes also have white strobes.",
            "A red light to your right.",
            "A green light to your left.",
            "Red and green together, red on your right.",
            "A white light alone.",
        ],
        "canvas": [640, 360],
        "background": "night",
        "layers": layers,
        "ground": ground,
        "overlays": overlays,
    }
