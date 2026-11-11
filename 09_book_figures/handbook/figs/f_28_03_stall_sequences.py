"""Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-28-03-stall-sequences",
        "replaces": "fig-28-03-stall-sequences.svg",
        "book_file": "plate-28-03-stall-sequences.jpg",
        "caption": "Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery",
        "desc": "Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery",
        "legend": [
            "Set-up. Top: descending at 65 kt, full flap. Bottom: 55 kt (`VR`), takeoff configuration, drawn clean.",
            "Entry. Top: throttle closed, nose raised. Bottom: takeoff power, nose raised past the climb attitude.",
            "The stall: buffet (red), the nose drops. Top: about 45 kt.",
            "Angle of attack reduced first (blue).",
            "Wings level, full power.",
            "Climb at `VY`, 75 kt.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-28-03-stall-sequences.svg"},
    }
