"""Figure 26-7. Soft-field takeoff and soft-field landing. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-26-07-soft-field",
        "replaces": "fig-26-07-soft-field.svg",
        "book_file": "plate-26-07-soft-field.jpg",
        "caption": "Figure 26-7. Soft-field takeoff and soft-field landing",
        "desc": "Figure 26-7. Soft-field takeoff and soft-field landing",
        "legend": [
            "Rolling onto the runway without stopping, control wheel fully back, flaps as the AFM recommends.",
            "Full power; once the nosewheel lifts, a nose-high attitude held.",
            "Lift-off at a low speed.",
            "Nose lowered at once: level just above the surface, accelerating.",
            "The ground effect zone, within about one wingspan of the surface.",
            "Climb only at `VX` 62 kt with an obstacle, or at `VY` 75 kt.",
            "Final at 60 kt, flaps 30°.",
            "Flare with some power on.",
            "Touchdown at the lowest possible speed, nose high, nosewheel held off.",
            "Nosewheel lowered gently, no brakes, power to keep moving.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-07-soft-field.svg"},
    }
