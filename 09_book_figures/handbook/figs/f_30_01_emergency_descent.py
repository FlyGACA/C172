"""Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK, look              # noqa: E402
from figs.kit import side_plane             # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-30-01-emergency-descent",
        "replaces": "fig-30-01-emergency-descent.svg",
        "book_file": "plate-30-01-emergency-descent.jpg",
        "caption": "Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery",
        "desc": "Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery",
        "legend": [
            "Clear the area and call.",
            "Throttle closed, bank, nose down.",
            "Descending turns over the checked area.",
            "About 30° to 45° of bank, seen from behind.",
            "The example aeroplane's limits: `VFE` 90 kt with any flap; `VA` 100 kt in turbulence; above `VNO` 125 kt (the yellow arc) only in smooth air; never above `VNE` 160 kt.",
            "Level off above the height your school sets.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {
            "svg": "fig-30-01-emergency-descent.svg",
            "drop": [
                # the three aeroplanes on the path (entry, in the turn, level at the end), flat silhouettes in the old figure, are the model
                [START, '<path d="M 112 70 C 113.7 71.3 119 74.3 122 78', {"sprites": [side_plane(62, 66, 0, 1.2, SILHOUETTE, grow=1.2, look=LOOK)]}],
                [START, '<path d="M 130 243.1 C 132.1 245.4', {"sprites": [side_plane(320.2, 123.5, 24, 1.1, SILHOUETTE, grow=1.2, look=LOOK)]}],
                [START, '<line x1="10" y1="310" x2="425" y2="310"', {"sprites": [side_plane(396, 292, 0, 1.2, SILHOUETTE, grow=1.2, look=LOOK)]}],
                # the aeroplane from behind in the turn, a line drawing in the old figure, is the model from behind, banked 38 degrees to the left
                ['<g transform="rotate(-38 532 99)">', '<text x="597" y="130"', {"sprites": [{"name": "sprite-rear", "at": [537.1, 105.5], "width": 136, "angle": -38, **LOOK}]}],
            ],
        },
    }
