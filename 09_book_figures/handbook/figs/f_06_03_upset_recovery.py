"""Figure 6-3 of the handbook: nose-high and nose-low upsets on the attitude indicator, two renders of the model's own instrument."""
from figs.kit import arc_arrow, dial_layer

BLUE = "#1D4ED8"


def plate():
    D = 236
    left, right = (170, 182), (470, 182)
    layers = [
        dial_layer("high", "AI", left, D, {"pitch": 30, "bank": 30}),
        dial_layer("low", "AI", right, D, {"pitch": -20, "bank": 60}),
    ]
    R = D / 2
    markup = arc_arrow(*left, R + 14, 62, -24, BLUE, 3.6) + arc_arrow(*right, R + 14, 84, -14, BLUE, 3.6)
    overlays = [{"type": "svg", "markup": markup}]
    overlays += [
        {"type": "marker", "n": 1, "at": "high.rim_sw", "pos": [38, 324], "leader": True},
        {"type": "marker", "n": 2, "at": "high.rim_w", "pos": [30, 150], "leader": True},
        {"type": "marker", "n": 3, "pos": [84, 54], "leader": False},
        {"type": "marker", "n": 4, "at": "low.rim_se", "pos": [602, 324], "leader": True},
        {"type": "marker", "n": 5, "pos": [588, 62], "leader": False},
        {"type": "marker", "n": 6, "at": "low.rim_w", "pos": [334, 270], "leader": True},
    ]
    return {
        "id": "fig-06-03-upset-recovery",
        "replaces": "fig-06-03-upset-recovery.svg",
        "book_file": "plate-06-03-upset-recovery.jpg",
        "caption": "Figure 6-3. Nose-high and nose-low upsets on the attitude indicator",
        "desc": "Two pictures of the attitude indicator of the training aeroplane: one nose high and banked right, one nose low and banked steeply right, each with an arrow for the roll to wings level.",
        "legend": [
            "Nose high: the horizon is far below the aeroplane symbol, about 30° nose up, in a right bank.",
            "First, forward pressure to unload; the nose comes down towards the horizon.",
            "Then roll wings level and set power for the airspeed.",
            "Nose low: the horizon is far above the symbol, about 20° nose down, in a steep right bank.",
            "First, power idle and unload, then roll wings level.",
            "Only then raise the nose to the horizon.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "layers": layers,
        "overlays": overlays,
    }
