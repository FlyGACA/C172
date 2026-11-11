"""Figure 27-3 of the handbook: a level steep turn to the left at 45 degrees, seen from behind (the model banked, with the lift, its two components and the
weight drawn from the centre of gravity), and the sight pictures through the windscreen in a left and in a right turn at 45 degrees (the pilot's eye in the
model, the horizon tilted against the cowl)."""
import math

EYE = {"part": "PANEL.AI.bezel", "at": [0.5, 0.5, 0.5], "add": [-0.0075, 0.62, 0.31]}              # the left seat, as in Figure 27-1
SKY = {"zenith": [0.02, 0.16, 0.95], "horizon": [0.58, 0.80, 1.00], "ground_near": [0.92, 0.78, 0.52], "ground_far": [0.56, 0.45, 0.26]}
BASE_PITCH = 3.0 + 3.0                 # the model's level attitude, and a little more nose up in a 45 degree turn (the lift is 1.41 times the weight)

# the aeroplane from behind: orthographic, a little above, the box centred on the middle of the banked wing so that both wingtips are in it
BOX = (0, 46, 350, 350)
WIDTH_M = 9.8                          # metres across the box
TARGET = [0.5, 0.0, 1.8]               # the wing root, 0.7 m above the centre of gravity along the aeroplane's own up, which leans 45 degrees to the left
CG_Z = 1.3
U = 2.3                                # the weight, in metres of arrow
R_ARC = 1.15                           # the radius of the arc of the bank angle, metres
S = math.sin(math.radians(45))

PANEL_W, PANEL_H = 250, 187            # the sight pictures, 4:3 like the windscreen of the model
PANELS = {"left": (374, 14), "right": (374, 212)}
REF = (0.689, 0.704)                   # the reference point on top of the cowl, as a fraction of a sight picture (the same place as in Figure 27-1)


def sight(name, bank):
    x, y = PANELS[name]
    return {
        "name": name, "box": [x, y, PANEL_W, PANEL_H], "round": 10,
        "render": {
            "camera": {"view": "eye", "eye": EYE, "look": [0.0, -1.0, 0.0], "fov": 58},
            "size": [1500, 1122],
            "light": "cockpit", "sky": SKY, "opaque": True,
            "pitch": {"deg": BASE_PITCH, "bank": bank, "about": [0.28, 0.12, 2.0]},
            "propeller": "none",
            "hide": ["ELECTRICAL.adf_sense_wire", "AIRFRAME.windshield", "AIRFRAME.door_window_L", "AIRFRAME.door_window_R", "AIRFRAME.window_rear_L", "AIRFRAME.window_rear_R", "AIRFRAME.rear_window"],
            "samples": 96,
            "anchors": {},
        },
    }


def plate():
    # (offsets from the centre of gravity, in the world's own directions: a plain point of a recipe would turn with the banked aeroplane)
    def about_cg(radius, degrees):
        return {"from": "cg", "add": [round(radius * math.sin(math.radians(degrees)), 4), 0, round(radius * math.cos(math.radians(degrees)), 4)]}
    arc = [about_cg(R_ARC, t) for t in range(0, 46, 3)]
    layers = [{
        "name": "rear", "box": list(BOX),
        "render": {
            "camera": {"view": "side", "target": TARGET, "width": WIDTH_M, "azimuth": -90, "elevation": 14},
            "size": [round(BOX[2] * 5), round(BOX[3] * 5)],
            "light": "outdoor",
            "pitch": {"deg": 0.0, "bank": -45.0, "about": [0, 0, CG_Z]},
            "propeller": {"turn": 30},
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "samples": 128,
            "anchors": {
                "cg": [0, 0, CG_Z],
                # the picture's right is the aeroplane's right; a left turn leans the lift to the left (+x)
                "lift_head": {"from": "cg", "add": [U, 0, U]},
                "up_head": {"from": "cg", "add": [0, 0, U]},
                "side_head": {"from": "cg", "add": [U, 0, 0]},
                "weight_head": {"from": "cg", "add": [0, 0, -U]},
                "weight_mid": {"from": "cg", "add": [0, 0, -U / 2]},
                "arc_mid": about_cg(R_ARC, 22.5),
                "angle_label": about_cg(1.75, 22.5),
            },
            "curves": {"arc": {"line": arc}},
        },
    }, sight("left", -45.0), sight("right", 45.0)]
    overlays = [
        {"type": "svg", "markup": f'<rect x="{x}" y="{y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="none" stroke="#1F2A44" stroke-width="2.4"/>'} for x, y in PANELS.values()
    ] + [
        # the dotted rectangle of the two components, then the arrows
        {"type": "line", "points": ["rear.up_head", "rear.lift_head"], "colour": "lift", "width": 1.6, "dash": "2.5 4", "halo": False},
        {"type": "line", "points": ["rear.side_head", "rear.lift_head"], "colour": "lift", "width": 1.6, "dash": "2.5 4", "halo": False},
        {"type": "line", "points": ["rear.cg", "rear.up_head"], "colour": "lift", "width": 2.6, "dash": "7 4", "arrow": "end"},
        {"type": "line", "points": ["rear.cg", "rear.side_head"], "colour": "lift", "width": 2.6, "dash": "7 4", "arrow": "end"},
        {"type": "arrow", "from": "rear.cg", "to": "rear.lift_head", "colour": "lift", "width": 3.6},
        {"type": "arrow", "from": "rear.cg", "to": "rear.weight_head", "colour": "weight", "width": 3.6},
        {"type": "path", "curve": "rear.arc", "colour": "weight", "width": 3.0},
        {"type": "cg", "at": "rear.cg", "r": 9},
        # the sizes: at the head of each arrow, on the side where the picture is free
        {"type": "text", "at": "rear.lift_head", "offset": [-27, 5], "s": "1.41", "size": 14, "colour": "lift"},
        {"type": "text", "at": "rear.up_head", "offset": [15, 5], "s": "1", "size": 14, "colour": "lift"},
        {"type": "text", "at": "rear.side_head", "offset": [0, 22], "s": "1", "size": 14, "colour": "lift"},
        {"type": "text", "at": "rear.weight_mid", "offset": [15, 5], "s": "1", "size": 14, "colour": "weight"},
        {"type": "text", "at": "rear.angle_label", "offset": [0, 4], "s": "45°", "size": 13, "colour": "weight"},
    ]
    for name, (x, y) in PANELS.items():
        overlays.append({"type": "svg", "markup": f'<circle cx="{x + PANEL_W * REF[0]:.1f}" cy="{y + PANEL_H * REF[1]:.1f}" r="4.6" fill="#FFFFFF" stroke="#1F2A44" stroke-width="1.8"/>'})
    overlays += [
        {"type": "marker", "n": 1, "at": "rear.lift_head", "offset": [10, -44], "leader": True, "gap": 7},
        {"type": "marker", "n": 2, "at": "rear.up_head", "offset": [34, -40], "leader": True, "gap": 7},
        {"type": "marker", "n": 3, "at": "rear.side_head", "offset": [-38, -22], "leader": True, "gap": 7},
        {"type": "marker", "n": 4, "at": "rear.weight_head", "offset": [58, 26], "leader": True, "gap": 7},
        {"type": "marker", "n": 5, "at": "rear.arc_mid", "offset": [72, -60], "leader": True, "gap": 7},
        {"type": "marker", "n": 6, "pos": list(PANELS["left"])},
        {"type": "marker", "n": 7, "pos": list(PANELS["right"])},
        {"type": "marker", "n": 8, "pos": [PANELS["left"][0] + PANEL_W - 22, PANELS["left"][1] + 22], "leader": True, "target": [PANELS["left"][0] + PANEL_W * REF[0], PANELS["left"][1] + PANEL_H * REF[1]], "gap": 5},
    ]
    return {
        "id": "fig-27-03-steep-turn",
        "replaces": "fig-27-03-steep-turn.svg",
        "book_file": "plate-27-03-steep-turn.jpg",
        "caption": "Figure 27-3. A level steep turn to the left at 45°, seen from behind, and the sight pictures in left and right turns",
        "desc": "The training aeroplane seen from behind in a level left turn at 45 degrees of bank, with the lift, its vertical and horizontal components and the weight drawn from the centre of gravity, and two views through the windscreen, in a 45 degree left turn and a 45 degree right turn.",
        "legend": [
            "Lift, perpendicular to the wings: 1.41 times the weight.",
            "Its vertical component balances the weight.",
            "Its horizontal component turns the aeroplane.",
            "Weight.",
            "The bank angle, 45°, equals the angle between the lift and the vertical.",
            "Sight picture in a 45° left turn.",
            "Sight picture in a 45° right turn.",
            "The reference point sits higher against the horizon in a left turn than in a right one, because you sit left of the centre line.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "layers": layers,
        "overlays": overlays,
    }
