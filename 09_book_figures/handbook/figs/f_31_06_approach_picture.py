"""Figure 31-6. The approach picture at night: too high, on the path and too low. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK                    # noqa: E402
from figs.kit import NIGHT, side_plane      # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-31-06-approach-picture",
        "replaces": "fig-31-06-approach-picture.svg",
        "book_file": "plate-31-06-approach-picture.jpg",
        "caption": "Figure 31-6. The approach picture at night: too high, on the path and too low",
        "desc": "Figure 31-6. The approach picture at night: too high, on the path and too low",
        "legend": [
            "Too high: runway long and steep; four white.",
            "On the path: two white, two red.",
            "Too low: runway flat and short; four red.",
            "Threshold lights, green.",
            "Edge lights, white.",
            "End lights, red.",
            "PAPI.",
            "Approach lights.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-31-06-approach-picture.svg",
            # the three aeroplanes on the profile (too high, on the path, too low), flat silhouettes in the old figure, are the model; they were drawn nose up on a descending
            # path, so here they point down the path at the old angles
            "drop": [
                [START, '<circle cx="84" cy="249.1" r="11" fill="#1f2937"/>', {"sprites": [side_plane(130, 253.1, 13.2, 1.0, SILHOUETTE, grow=1.35, look=LOOK)]}],
                [START, '<circle cx="84" cy="320.2" r="11" fill="#1f2937"/>', {"sprites": [side_plane(130, 324.2, 6.6, 1.0, SILHOUETTE, grow=1.35, look=LOOK)]}],
                [START, '<circle cx="84" cy="355.6" r="11" fill="#1f2937"/>', {"sprites": [side_plane(130, 359.6, 3.3, 1.0, SILHOUETTE, grow=1.35, look=LOOK)]}],
            ],
        },
    }
