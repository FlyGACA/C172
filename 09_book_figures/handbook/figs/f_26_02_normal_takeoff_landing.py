"""Figure 26-2. Normal takeoff and normal landing seen from the side. The diagram of the book's figure with the aeroplane of the model (reskin.py): the nine
cartoon aeroplanes are replaced by the model seen from the right, each standing on the same point of the runway at the same attitude."""
import math

from reskin import LOOK        # noqa: E402

W = 88.0               # canvas units from tail to spinner (the old aeroplanes were 71 across, and chunkier)
ASPECT = 0.294         # the height of the picture over its width (sprite-side, cropped to the aeroplane)
CX = -6.8              # the middle of an old aeroplane lies this far behind the point of its group where its main wheels touch (canvas units)


def plane(tx, ty, angle, lowered=False):
    """The model where the old aeroplane stood: its wheels on the old one's ground point (the group's origin, 14.4 lower when the group was translated 18), turned
    about that point by the same angle (degrees clockwise)."""
    h = W * ASPECT
    lx, ly = CX, (14.4 if lowered else 0.0) - h / 2
    a = math.radians(angle)
    return {"name": "sprite-side", "at": [round(tx + lx * math.cos(a) - ly * math.sin(a), 1), round(ty + lx * math.sin(a) + ly * math.cos(a), 1)], "width": W, "angle": angle, **LOOK}


UPPER = [plane(70, 178, 0), plane(215, 178, -8), plane(330, 168, -9, True), plane(480, 94, -11, True)]
LOWER = [plane(110, 292.1, 2, True), plane(248, 359.6, -3, True), plane(372, 389, -6), plane(470, 395, -8), plane(590, 395, 0)]


def plate():
    return {
        "id": "fig-26-02-normal-takeoff-landing",
        "replaces": "fig-26-02-normal-takeoff-landing.svg",
        "book_file": "plate-26-02-normal-takeoff-landing.jpg",
        "caption": "Figure 26-2. Normal takeoff and normal landing seen from the side",
        "desc": "Figure 26-2. Normal takeoff and normal landing seen from the side",
        "legend": [
            "Takeoff roll at full power, rudder keeping the nose on the centreline.",
            "Rotation at `VR` 55 kt to the takeoff attitude.",
            "Lift-off, wings level, attitude held.",
            "Climb at `VY` 75 kt.",
            "Final at 65 kt, flaps 30°.",
            "The aiming point.",
            "Round out (flare): throttle closed, nose raised progressively.",
            "Hold-off just above the runway as the speed decays.",
            "Touchdown on the main wheels, nose high, near the stall speed.",
            "Nosewheel lowered; rollout on the centreline.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {
            "svg": "fig-26-02-normal-takeoff-landing.svg",
            "drop": [
                ['<g transform="translate(70 178) rotate(0) scale(0.8)" filter="url(#f2602-sh)">', '<rect x="14" y="117.8" width="24" height="4.4"', {"sprites": UPPER}],
                ['<g transform="translate(110 292.1) rotate(2) scale(0.8) translate(0 18)"', '<ellipse cx="466" cy="396" rx="9" ry="2.4"', {"sprites": LOWER}],
            ],
        },
    }
