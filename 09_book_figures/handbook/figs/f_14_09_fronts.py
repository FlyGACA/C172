"""Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front. The diagram of the book's figure (the warm and cold air, the frontal surfaces, the rain, the arrows, the
numbered callouts) with the clouds of the model of the sky in place of the cartoon clouds (reskin.py, figs/clouds.py): the cumulonimbus of the cold front, the layers of the warm front
lying along its slope (nimbostratus, altostratus, cirrostratus, a wisp of cirrus) and the layer cloud and the cumulus of the occluded front."""

REMOVE = [
    r'<path d="M (?!184 298)[\d.]+ [\d.]+ [AL][^"]*" fill="url\(#f1409-(?:cld|ns)\)"[^>]*/>',          # the cartoon clouds (not the low stratus: its own drop below)
    r'<circle cx="[\d.]+" cy="[\d.]+" r="[\d.]+" fill="#ffffff" opacity="0\.55"/>',                    # their puffs
    r'<path d="M 572 184 q [^"]*"[^>]*/>',                                                              # the wisp of cirrus
]
BOLT = '<path d="M 330 52 L 324 68 L 331 68 L 325 84'
FIRST_RAIN_WARM = '<line x1="166" y1="294.7" x2="162" y2="304"'
LOW_STRATUS = '<path d="M 184 298 L 184 292'
AFTER_STRATUS = '<line x1="24" y1="296" x2="150" y2="277.6"'
FIRST_ARROW_OCCLUDED = '<line x1="70" y1="436" x2="170" y2="436"'


def plate():
    return {
        "id": "fig-14-09-fronts",
        "replaces": "fig-14-09-fronts.svg",
        "book_file": "plate-14-09-fronts.jpg",
        "caption": "Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front",
        "desc": "Figure 14-9. Cross-sections of a cold front, a warm front and an occluded front",
        "legend": [
            "Cold front: cold air pushing under warm air.",
            "The steep frontal surface.",
            "Cumulonimbus in a narrow band of showers and gusts.",
            "Warm front: warm air gliding up a shallow frontal surface.",
            "Cirrus and cirrostratus far ahead.",
            "Altostratus and nimbostratus, thickening and lowering toward the surface front.",
            "Wide band of steady rain, with low stratus in the cold air.",
            "Occluded front: warm air lifted off the ground.",
            "Cold air overtaking and undercutting cooler air ahead.",
            "Layer cloud and rain, possibly with embedded cumulonimbus.",
        ],
        "canvas": [640, 480],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-09-fronts.svg",
            "remove": REMOVE,
            "drop": [
                [BOLT, BOLT, {"sprites": [{"name": "cloud-cb-wide", "at": [345, 56], "width": 140}, {"name": "cloud-cumulus-b", "at": [490, 75], "width": 44}]}],
                [FIRST_RAIN_WARM, FIRST_RAIN_WARM, {"sprites": [
                    {"name": "cloud-nimbostratus", "at": [240, 240], "width": 190, "height": 62, "angle": -13.7},
                    {"name": "cloud-stratus", "at": [403, 220], "width": 140, "height": 34, "angle": -15},
                    {"name": "cloud-veil", "at": [521, 190], "width": 94, "height": 20, "angle": -19},
                    {"name": "cloud-cirrus", "at": [588, 177], "width": 40, "angle": -19}]}],
                [LOW_STRATUS, AFTER_STRATUS, {"sprites": [{"name": "cloud-stratus", "at": [226, 292], "width": 84, "height": 14}]}],
                [FIRST_ARROW_OCCLUDED, FIRST_ARROW_OCCLUDED, {"sprites": [
                    {"name": "cloud-nimbostratus", "at": [380, 366], "width": 160, "height": 38}, {"name": "cloud-congestus", "at": [308, 355], "width": 36}]}],
            ],
        },
    }
