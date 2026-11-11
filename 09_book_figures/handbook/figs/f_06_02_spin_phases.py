"""Figure 6-2. The phases of a spin. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-06-02-spin-phases",
        "replaces": "fig-06-02-spin-phases.svg",
        "book_file": "plate-06-02-spin-phases.jpg",
        "caption": "Figure 6-2. The phases of a spin",
        "desc": "Figure 6-2. The phases of a spin",
        "legend": [
            "Entry: the aeroplane is stalled while yaw is applied or allowed.",
            "Incipient phase: rotation starts and builds while the path steepens; in most light aeroplanes it lasts two to four turns.",
            "Developed phase: rotation, airspeed and descent rate are steady and the path is nearly vertical. Some training aeroplanes turn into a spiral dive instead.",
            "Recovery phase: the rotation stops, the wing is unstalled and the aeroplane is eased out of the dive.",
            "Direction of rotation about the spin axis.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-06-02-spin-phases.svg",
            # the four small plan symbols of the old figure are the model on the flight path: level at the entry, nose high at the stall, nose down and rolled in the spin
            # (rendered in that attitude), levelling out in the recovery
            "remove": [r'<g transform="translate\(44,104\) scale\(0\.7\)" filter="url\(#sh\)">.*?</g>',
                       r'<g transform="translate\(190,78\) rotate\(-25\) scale\(0\.7\)" filter="url\(#sh\)">.*?</g>',
                       r'<g transform="translate\(250,185\) rotate\(-40\) scale\(0\.55\)" filter="url\(#sh\)">.*?</g>',
                       r'<g transform="translate\(510,340\) scale\(0\.6\)" filter="url\(#sh\)">.*?</g>'],
            "sprites": [{"name": "sprite-side", "at": [48, 102], "width": 54, **LOOK},
                        {"name": "sprite-side", "at": [188, 80], "width": 54, "angle": -25, **LOOK},
                        {"name": "sprite-spin", "at": [252, 186], "width": 36, **LOOK},
                        {"name": "sprite-side", "at": [510, 338], "width": 60, "angle": 5, **LOOK}],
        },
    }
