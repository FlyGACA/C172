"""Figure 27-1 of the handbook: sight pictures of the four fundamentals (straight and level, climb, descent, a level turn to the left at 30 degrees
of bank), each as the pilot sees it through the windscreen of the model, with the attitude indicator and the ball beside it."""
from figs.kit import dial_layer

# the pilot's eye: where the occupant of the left seat looks from, found from the attitude indicator (metres, in the aeroplane's own frame)
EYE = {"part": "PANEL.AI.bezel", "at": [0.5, 0.5, 0.5], "add": [-0.0075, 0.62, 0.31]}
SKY = {"zenith": [0.02, 0.16, 0.95], "horizon": [0.58, 0.80, 1.00], "ground_near": [0.92, 0.78, 0.52], "ground_far": [0.56, 0.45, 0.26]}
BASE_PITCH = 3.0                  # the model's level flight, as in the side views

VIEW_W, VIEW_H = 190, 142


def view(name, box, pitch, bank=0.0):
    return {
        "name": name, "box": [*box, VIEW_W, VIEW_H], "round": 9,
        "render": {
            "camera": {"view": "eye", "eye": EYE, "look": [0.0, -1.0, 0.0], "fov": 58},
            "size": [1140, 852],
            "light": "cockpit", "sky": SKY, "opaque": True,
            "pitch": {"deg": pitch, "bank": bank, "about": [0.28, 0.12, 2.0]},
            "propeller": "none",
            "hide": ["ELECTRICAL.adf_sense_wire", "AIRFRAME.windshield", "AIRFRAME.door_window_L", "AIRFRAME.door_window_R", "AIRFRAME.window_rear_L", "AIRFRAME.window_rear_R", "AIRFRAME.rear_window"],     # clear glass: the eye looks through it
            "samples": 96,
            "anchors": {},
        },
    }


def plate():
    cells = [(0, 0), (320, 0), (0, 210), (320, 210)]
    poses = [(BASE_PITCH, 0.0, {"pitch": 0, "bank": 0}), (BASE_PITCH + 9.0, 0.0, {"pitch": 10, "bank": 0}),
             (BASE_PITCH - 7.0, 0.0, {"pitch": -8, "bank": 0}), (BASE_PITCH, -30.0, {"pitch": 0, "bank": -30})]
    layers = []
    for i, ((cx, cy), (pitch, bank, ai)) in enumerate(zip(cells, poses), 1):
        layers.append(view(f"v{i}", (cx + 12, cy + 14), pitch, bank))
        layers.append(dial_layer(f"ai{i}", "AI", (cx + 258, cy + 56), 78, ai))
        layers.append(dial_layer(f"tc{i}", "TC", (cx + 258, cy + 132), 58, {"turn": 0.0 if bank == 0 else -1.0}))
    overlays = []
    for i, (cx, cy) in enumerate(cells, 1):
        overlays.append({"type": "svg", "markup": f'<rect x="{cx + 12}" y="{cy + 14}" width="{VIEW_W}" height="{VIEW_H}" rx="9" fill="none" stroke="#1F2A44" stroke-width="2.4"/>'})
        overlays.append({"type": "marker", "n": i, "pos": [cx + 12, cy + 14], "leader": False})
    overlays += [
        {"type": "marker", "n": 5, "pos": [150, 178], "leader": True, "target": [143, 114]},
        {"type": "marker", "n": 6, "pos": [58, 52], "leader": True, "target": [70, 94]},
        {"type": "marker", "n": 7, "at": "ai1.rim_ne", "pos": [286, 22], "leader": True},
        {"type": "marker", "n": 8, "at": "tc1.rim_se", "pos": [290, 172], "leader": True},
    ]
    return {
        "id": "fig-27-01-attitude-pictures",
        "replaces": "fig-27-01-attitude-pictures.svg",
        "book_file": "plate-27-01-attitude-pictures.jpg",
        "caption": "Figure 27-1. Sight pictures of the four fundamentals, with the attitude indicator and the ball",
        "desc": "Four views through the windscreen of the training aeroplane, each with its attitude indicator and ball: straight and level, climb, descent, and a level turn to the left at 30 degrees of bank.",
        "legend": [
            "Straight and level.",
            "Climb: the horizon sits lower in the windscreen.",
            "Descent: the horizon sits higher.",
            "Level turn to the left at 30° of bank: the horizon tilts against the top of the cowl.",
            "Your reference point on the cowl.",
            "The natural horizon, your primary reference.",
            "The attitude indicator, for a cross-check.",
            "The ball, centred in coordinated flight.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "layers": layers,
        "overlays": overlays,
    }
