"""Figure 28-6 of the handbook: a nose-high unusual attitude and the recovery in order, on the model's instruments."""
from figs.upset import upset_plate


def plate():
    return upset_plate(
        "fig-28-06-nose-high", "plate-28-06-nose-high.jpg",
        "Figure 28-6. A nose-high unusual attitude and the recovery in order",
        "The attitude indicator, airspeed indicator, altimeter, vertical speed indicator and turn coordinator of the training aeroplane in a nose-high, banked attitude, and below them four pictures of the attitude indicator for the recovery, forward pressure first, then wings level, then power.",
        [
            "Nose about 20° up, banked 30° right.",
            "Airspeed low and falling.",
            "Altitude rising.",
            "Climbing.",
            "Turning right.",
            "First, forward pressure: the nose comes down to the horizon, reducing the angle of attack.",
            "Then wings level.",
            "Then power as needed (grey bar).",
            "Level off at the horizon; cruise power; retrim.",
        ],
        top={"AI": {"pitch": 20, "bank": 30}, "ASI": 52, "ALT": 4200, "VSI": 1500, "turn": 1.0},
        trends=[("asi", 112, 62), ("alt", 232, 286)],
        sequence=[{"pitch": 20, "bank": 30}, {"pitch": 0, "bank": 30}, {"pitch": 0, "bank": 0}, {"pitch": 0, "bank": 0}],
        bars=[(0, 0.55), (3, 0.8)],
    )
