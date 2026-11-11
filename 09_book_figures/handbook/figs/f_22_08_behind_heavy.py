"""Figure 22-8. Landing and taking off behind a heavy aeroplane. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK, look              # noqa: E402
from figs.kit import side_plane             # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'


def plate():
    return {
        "id": "fig-22-08-behind-heavy",
        "replaces": "fig-22-08-behind-heavy.svg",
        "book_file": "plate-22-08-behind-heavy.jpg",
        "caption": "Figure 22-8. Landing and taking off behind a heavy aeroplane",
        "desc": "Figure 22-8. Landing and taking off behind a heavy aeroplane",
        "legend": [
            "The heavy aeroplane's approach path.",
            "Its touchdown point: the wake ends there.",
            "The wake, below and behind its path.",
            "Your approach: at or above its path, touching down beyond its touchdown point.",
            "Below its path and landing short: into the wake.",
            "A departing heavy aeroplane's rotation point: the wake begins there.",
            "The wake below its climb path.",
            "Your takeoff: rotate before its rotation point and climb above its path until you can turn clear.",
            "Landing behind a departing heavy aeroplane: touch down before its rotation point.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {
            "svg": "fig-22-08-behind-heavy.svg",
            # the light aeroplanes (on the right path in green, in the wake in red, taking off in green) are the model, at the same places and angles; the heavy aeroplane,
            # which the model does not have, stays as it was
            "drop": [
                [START, '<line x1="420" y1="164" x2="420" y2="186"', {"sprites": [side_plane(150, 61.9, 22.2, 0.85, SILHOUETTE, grow=1.4, look=look("#047857"))]}],
                [START, '<line x1="209.8" y1="50.2" x2="186" y2="107.5"', {"sprites": [side_plane(150, 122.4, 23.9, 0.85, SILHOUETTE, grow=1.4, look=look("#b91c1c"))]}],
                [START, '<polygon points="520,228 513.8,237.6 508.6,227.9"', {"sprites": [side_plane(430, 274.5, -28.3, 0.85, SILHOUETTE, grow=1.4, look=look("#047857"))]}],
            ],
        },
    }
