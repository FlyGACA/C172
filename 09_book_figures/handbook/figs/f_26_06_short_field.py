"""Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-26-06-short-field",
        "replaces": "fig-26-06-short-field.svg",
        "book_file": "plate-26-06-short-field.jpg",
        "caption": "Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing",
        "desc": "Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing",
        "legend": [
            "Line up at the very start of the runway, flaps as the AFM gives (drawn partly extended); full power.",
            "As `VX` approaches, rotate to the `VX` attitude.",
            "Climb at `VX` 62 kt, eyes outside.",
            "The obstacle; the example takeoff table measures to 15 m (Chapter 11).",
            "Once clear, `VY` 75 kt, then flaps up in stages.",
            "`VY` from lift-off gains more height per minute but less per metre: here it would not clear the obstacle.",
            "Final at 60 kt, flaps 30°, on a steady path over the obstacle.",
            "The aiming point, just beyond the threshold.",
            "Touchdown at minimum speed, nose high, power off, with little float.",
            "Firm braking once the nosewheel is down, control wheel held back.",
            "A normal 65 kt approach over the same obstacle lands much further along.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-06-short-field.svg"},
    }
