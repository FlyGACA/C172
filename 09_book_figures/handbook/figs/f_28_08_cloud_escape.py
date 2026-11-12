"""Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402

from figs import h_plan, terrain

BOLD = {**LOOK, "outline": {"width": 1.0, "colour": "#1F2937", "opacity": 1.0}}        # small on a white ground: a firmer edge


# the wall of dust or cloud on the right of the old drawing, cut to its wavy edge, and the high ground at the foot, as a hill of rock lit from the upper left
DUST_EDGE = h_plan.path_points("M 430 0 C 428 6.7 417 26.7 418 40 C 419 53.3 436.7 66.7 436 80 C 435.3 93.3 414.7 106.7 414 120 C 413.3 133.3 432.7 146.7 432 160 C 431.3 173.3 410.3 186.7 410 200 "
                               "C 409.7 213.3 429.7 226.7 430 240 C 430.3 253.3 411.3 266.7 412 280 C 412.7 293.3 432.7 306.7 434 320 C 435.3 333.3 422.3 353.3 420 360 L 640 360 L 640 0 Z")
DUST = terrain.piece("terrain-28-08-dust", ("poly", DUST_EDGE), seed=28, kind="dust", feather=4.0)
HILL = terrain.piece("terrain-28-08-hill", ("poly", [(250, 360), (300, 318), (340, 334), (390, 300), (440, 330), (480, 360)]), seed=3, kind="rock", features=("scrub",), veil=0.0, soft=1.0, raised=2.2, feather=0.8, darken=0.62)
DUST_PATH = '<path d="M 430 0 C 428 6.7 417 26.7 418 40 C 419 53.3 436.7 66.7 436 80 C 435.3 93.3 414.7 106.7 414 120 C 413.3 133.3 432.7 146.7 432 160 C 431.3 173.3 410.3 186.7 410 200 C 409.7 213.3 429.7 226.7 430 240 C 430.3 253.3 411.3 266.7 412 280 C 412.7 293.3 432.7 306.7 434 320 C 435.3 333.3 422.3 353.3 420 360 L 640 360 L 640 0 Z" fill="#fdf0e1"'


def plate():
    return {
        "id": "fig-28-08-cloud-escape",
        "replaces": "fig-28-08-cloud-escape.svg",
        "book_file": "plate-28-08-cloud-escape.jpg",
        "caption": "Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation",
        "desc": "Figure 28-8. Escaping dust or cloud entered by accident: control, a 180° turn, then radio, radar and navigation",
        "legend": [
            "Planned route from aerodrome A.",
            "Dust or cloud: no horizon.",
            "Wings level, then a 180° turn: one minute at standard rate.",
            "Clear air on the reciprocal heading.",
            "ATC and radar.",
            "GNSS or VOR guidance toward A.",
            "High ground: stay above the safe altitude.",
            "Aerodrome A.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": h_plan.layer({
            "svg": "fig-28-08-cloud-escape.svg",
            # the dust is a picture now, and the grains of it, the hatching of the hill and its outline go with the flat drawing of both
            "remove": [r'<circle cx="[\d.]+" cy="[\d.]+" r="(?:2\.2|1\.6)" fill="#b45309"/>', r'<line x1="\d+" y1="356" x2="\d+" y2="344" stroke="#9ca3af" stroke-width="1"/>',
                       r'<polygon points="250,360 300,318 340,334 390,300 440,330 480,360" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1.4"/>'],
            "replace": [[DUST_PATH, DUST_PATH.replace('fill="#fdf0e1"', 'fill="none"')]],
            # the two aeroplanes on the track, flat silhouettes in the old figure, are the model seen from above: outbound to the east, then back to the west
            "drop": [['<path d="M 0 -12 L 1.6 -9 L 1.6 -3 L 13 1', '<path d="M 318 282 C 308.7 281.3', {"sprites": [
                {"name": "sprite-top", "at": [300, 190], "width": 40, "angle": 90, **BOLD},
                {"name": "sprite-top", "at": [366, 282], "width": 40, "angle": 270, **BOLD}]}]],
        }, "terrain-28-08", seed=288, kind="plain", veil=0.32, extra_sprites=[DUST, {**HILL, "shadow": {"dx": 3, "dy": 4, "blur": 2.5, "opacity": 0.4}}]),
    }
