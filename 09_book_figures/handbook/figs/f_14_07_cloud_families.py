"""Figure 14-7. Cloud families by height. The diagram of the book's figure (the altitude lines, the rain and the virga, the numbered callouts) with the clouds of the model
of the sky in place of the outlines (reskin.py, figs/clouds.py): cirrus, cirrocumulus, cirrostratus, altostratus, altocumulus, nimbostratus, stratus, stratocumulus,
cumulus, towering cumulus and cumulonimbus, each where the outline stood and as wide."""

SKY = ('<defs><linearGradient id="f1407-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E9F1FA"/></linearGradient></defs>'
       '<rect x="0" y="0" width="640" height="412" fill="url(#f1407-sky)"/>')
GROUND = '<rect x="0" y="412" width="640" height="28" fill="#fdf0e1"/>'
FIRST_CALLOUT = '<circle cx="26" cy="92" r="10.5" fill="#1f2937" stroke="#ffffff" stroke-width="1.5"/>'

REMOVE = [
    r'<path d="M [\d.]+ [\d.]+ q [^"]*" fill="none" stroke="#9ca3af" stroke-width="1\.[16]"/>',                         # the hooks of the cirrus
    r'<circle cx="[\d.]+" cy="(?:58|66|74)" r="3\.6" fill="#ffffff" stroke="#9ca3af" stroke-width="1"/>',               # the cirrocumulus, a grid of dots
    r'<path d="M (?:40 128|40 250|36 358|184 384) [^"]*"[^>]*/>',                                                      # the sheets: cirrostratus, altostratus, nimbostratus, stratus
    r'<path d="M [\d.]+ [\d.]+ A [^"]*" fill="#ffffff"[^>]*/>',                                                       # the lumps: altocumulus, stratocumulus, cumulus, towering cumulus, cumulonimbus
]

SPRITES = [
    {"name": "cloud-cirrus", "at": [106, 62], "width": 132},
    {"name": "cloud-altocumulus", "at": [242, 66], "width": 98},                  # (cirrocumulus: the same cloudlets, but high and small)
    {"name": "cloud-veil", "at": [210, 130], "width": 340},
    {"name": "cloud-stratus", "at": [115, 242], "width": 152},                    # (altostratus: a grey sheet in the middle levels)
    {"name": "cloud-altocumulus", "at": [294, 207], "width": 162},
    {"name": "cloud-nimbostratus", "at": [101, 338], "width": 130},
    {"name": "cloud-stratus", "at": [234, 378], "width": 100},
    {"name": "cloud-stratocumulus", "at": [350, 334], "width": 108},
    {"name": "cloud-cumulus-b", "at": [446, 367], "width": 46},
    {"name": "cloud-tcu", "at": [502, 304], "width": 50, "height": 152},
    {"name": "cloud-cb-tall", "at": [562, 208], "width": 150, "height": 344},
]


def plate():
    return {
        "id": "fig-14-07-cloud-families",
        "replaces": "fig-14-07-cloud-families.svg",
        "book_file": "plate-14-07-cloud-families.jpg",
        "caption": "Figure 14-7. Cloud families by height",
        "desc": "Figure 14-7. Cloud families by height",
        "legend": [
            "Cirrus.", "Cirrocumulus.", "Cirrostratus.", "Altostratus.", "Altocumulus.", "Virga.", "Nimbostratus.", "Stratus.", "Stratocumulus.", "Cumulus.",
            "Towering cumulus, `TCU` in a METAR.", "Cumulonimbus, `CB`.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-07-cloud-families.svg",
            "remove": REMOVE,
            "replace": [[GROUND, SKY + GROUND]],
            "drop": [[FIRST_CALLOUT, FIRST_CALLOUT, {"sprites": SPRITES}]],
        },
    }
