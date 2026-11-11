"""Figure 31-7. Judging the flare at night, with the landing light and without it. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK                    # noqa: E402
from figs.kit import NIGHT, side_plane      # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-31-07-night-flare",
        "replaces": "fig-31-07-night-flare.svg",
        "book_file": "plate-31-07-night-flare.jpg",
        "caption": "Figure 31-7. Judging the flare at night, with the landing light and without it",
        "desc": "Figure 31-7. Judging the flare at night, with the landing light and without it",
        "legend": [
            "Higher on final: the beam does not reach the ground.",
            "The beam shows the surface and tyre marks: round out.",
            "Hold the approach descent until this point.",
            "Throttle closed gradually as the wheels touch.",
            "Nose reference, the top of the cowling.",
            "Far-end lights rise above the nose: round out.",
            "Hold the landing attitude; feel for the runway with small power and pitch changes.",
            "Runway edge lights.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {
            "svg": "fig-31-07-night-flare.svg",
            # the three aeroplanes on final and in the flare, flat silhouettes in the old figure, are the model by moonlight
            "drop": [
                [START, '<polygon points="166,111 260,140 254,154 164,114"', {"sprites": [side_plane(300, 146, 4, 1.1, SILHOUETTE, look=NIGHT)]}],
                [START, '<circle cx="450" cy="170" r="5" fill="none"', {"sprites": [side_plane(150, 110, 7, 1.1, SILHOUETTE, look=NIGHT)]}],
                [START, '<line x1="156" y1="342" x2="405" y2="363.8"', {"sprites": [side_plane(150, 347, 4, 1.1, SILHOUETTE, look=NIGHT)]}],
            ],
        },
    }
