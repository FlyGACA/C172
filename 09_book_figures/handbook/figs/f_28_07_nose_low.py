"""Figure 28-7 of the handbook: a nose-low unusual attitude and the recovery in order, on the model's instruments."""
from figs.upset import upset_plate


def plate():
    return upset_plate(
        "fig-28-07-nose-low", "plate-28-07-nose-low.jpg",
        "Figure 28-7. A nose-low unusual attitude and the recovery in order",
        "The attitude indicator, airspeed indicator, altimeter, vertical speed indicator and turn coordinator of the training aeroplane in a nose-low, steeply banked attitude, and below them four pictures of the attitude indicator for the recovery, power to idle first, then wings level, then the nose raised.",
        [
            "Nose about 20° down, banked 45° right.",
            "Airspeed high, in the caution range, rising.",
            "Altitude falling.",
            "Descending fast.",
            "Turning right, beyond standard rate.",
            "First, power to idle and unload: stop pulling.",
            "Then wings level, before any pull.",
            "Then raise the nose gently to the horizon.",
            "Cruise power; retrim.",
        ],
        top={"AI": {"pitch": -20, "bank": 45}, "ASI": 140, "ALT": 3800, "VSI": -2000, "turn": 1.5},
        trends=[("asi", 232, 286), ("alt", 112, 62)],
        sequence=[{"pitch": -20, "bank": 45}, {"pitch": -20, "bank": 45}, {"pitch": -15, "bank": 0}, {"pitch": 0, "bank": 0}],
        bars=[(0, 0.55), (1, 0.0), (3, 0.55)],
    )
