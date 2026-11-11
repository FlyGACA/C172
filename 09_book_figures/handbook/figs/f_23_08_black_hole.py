"""Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK, look              # noqa: E402
from figs.kit import side_plane             # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-23-08-black-hole",
        "replaces": "fig-23-08-black-hole.svg",
        "book_file": "plate-23-08-black-hole.jpg",
        "caption": "Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant",
        "desc": "Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant",
        "legend": [
            "Dark water or desert before the runway: no lights, no texture.",
            "Runway edge lights.",
            "Town lights beyond the runway.",
            "Green: the correct approach path.",
            "Red: the path flown by keeping the runway's picture unchanged; it sags well below the correct path.",
            "Unlit rising ground short of the runway, which the sagging path meets.",
            "The PAPI: two white and two red on the correct path, more red below it (Chapter 18).",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {
            "svg": "fig-23-08-black-hole.svg",
            # the aeroplane on the approach, a flat silhouette in the old figure, is the model, nose down along the path
            "drop": [[START, '<circle cx="150" cy="292" r="12.5" fill="#ffffff"/>', {"sprites": [side_plane(50, 108.4, 16, 1.0, SILHOUETTE, grow=1.7, look=LOOK)]}]],
        },
    }
