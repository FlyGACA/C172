"""Figure 31-4. A night takeoff: from the runway lights to the instruments. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from figs.kit import NIGHT, side_plane      # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-31-04-night-takeoff",
        "replaces": "fig-31-04-night-takeoff.svg",
        "book_file": "plate-31-04-night-takeoff.jpg",
        "caption": "Figure 31-4. A night takeoff: from the runway lights to the instruments",
        "desc": "Figure 31-4. A night takeoff: from the runway lights to the instruments",
        "legend": [
            "Lined up; heading indicator checked; landing and taxi lights on.",
            "Accelerate straight between the edge lights.",
            "Rotate at `VR`, 55 kt (example aeroplane).",
            "After liftoff nothing ahead: eyes to the attitude indicator.",
            "Climb at `VY`, 75 kt (example aeroplane); the landing light no longer reaches the ground.",
            "Dark ground: no horizon.",
            "Attitude: climb, wings level.",
            "Airspeed: 75 kt.",
            "Altimeter: increasing.",
            "Vertical speed: climbing.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-31-04-night-takeoff.svg",
            "drop": [
                # the three aeroplanes on the runway, at rotation and climbing, flat silhouettes in the old figure, are the model by moonlight
                [START, '<polygon points="267,216 376.9,210.9 376,230.7"', {"sprites": [side_plane(64, 218, 0, 1.1, SILHOUETTE, look=NIGHT)]}],
                [START, '<text x="248" y="195"', {"sprites": [side_plane(250, 217, -7, 1.1, SILHOUETTE, look=NIGHT)]}],
                [START, '<text x="466" y="162.2"', {"sprites": [side_plane(470, 184.2, -9, 1.1, SILHOUETTE, look=NIGHT)]}],
                # the four instruments are the model's own: nose 10 degrees up, 75 kt, climbing through 1,200 ft, 700 ft/min up
                ['<g transform="translate(110 345) scale(0.4035)">', '<line x1="57.3" y1="314.9"', {"sprites": [
                    {"name": "dial-31-04-ai", "at": [110, 345], "width": 92},
                    {"name": "dial-31-04-asi", "at": [250, 345], "width": 92},
                    {"name": "dial-31-04-alt", "at": [390, 345], "width": 92},
                    {"name": "dial-31-04-vsi", "at": [530, 345], "width": 92}]}],
            ],
        },
    }
