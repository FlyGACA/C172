"""Figure 30-7. Survival after a desert landing: priorities around the aeroplane. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-30-07-survival",
        "replaces": "fig-30-07-survival.svg",
        "book_file": "plate-30-07-survival.jpg",
        "caption": "Figure 30-7. Survival after a desert landing: priorities around the aeroplane",
        "desc": "Figure 30-7. Survival after a desert landing: priorities around the aeroplane",
        "legend": [
            "Safety and first aid: everyone clear until the fire risk has passed.",
            "Stay with the aeroplane: it is far easier to see than people, and the search follows your route.",
            "Shade under the wing, off the hot ground, extended with a sheet.",
            "Water, kept in the shade.",
            "The ELT, and the radio if it works.",
            "A ground signal: a bright sheet, or panels laid out from the code card.",
            "A signal mirror, flashed at aircraft or vehicles.",
            "A fire ready to light, well away from the aeroplane and its fuel.",
            "Do not walk away in the heat.",
            "The midday sun.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {
            "svg": "fig-30-07-survival.svg",
            # the aeroplane, a line drawing in the old figure, is the model seen from the left, on the same ground line and as long as the old drawing was (the nose at the left);
            # the sheet that gives shade hangs from its wing behind it
            "drop": [['<g transform="translate(0 25.1)">', '<circle cx="88" cy="294.6" r="4.5"', {
                "before": '<polygon points="228,247 72,318 118,318" fill="#fdf0e1" stroke="#b45309" stroke-width="2" stroke-linejoin="round"/>',
                "sprites": [{"name": "sprite-side-left", "at": [308.5, 272.4], "width": 317, **LOOK}]}],
                # the search aircraft far off, a flat silhouette in the old figure, is the same aeroplane
                ['<path d="M -19 -1 L 10 -3 Q 17 -2 18 1', '<line x1="508" y1="272" x2="378" y2="76"', {"sprites": [{"name": "sprite-side", "at": [360, 64], "width": 62, **LOOK}]}]],
        },
    }
