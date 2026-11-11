"""Figure 16-4. Cloud base and ceiling with three layers of cloud. The diagram of the book's figure (the height scale, the 1 000 ft line, the aerodrome, the numbered callouts) on a sky
with the clouds of the model of the sky in place of the outlines (reskin.py, figs/clouds.py), each standing on the height of its base: two few, four scattered (cumulus), and
the broken layer, three stretches of stratocumulus whose base is the ceiling."""

SKY = ('<defs><linearGradient id="f1604-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E9F1FA"/></linearGradient></defs>'
       '<rect x="70" y="20" width="560" height="310" fill="url(#f1604-sky)"/>')
OLD_TINT = '<rect x="70" y="20" width="560" height="310" fill="#e8eefc" fill-opacity="0.5"/>'
FIRST_CALLOUT = '<circle cx="138.0" cy="200.0" r="11" fill="#1f2937"/>'


def on_base(name, cx, base, width, aspect, height=None):
    h = height or width / aspect
    return {"name": name, "at": [cx, round(base - h / 2, 1)], "width": width, **({"height": height} if height else {})}


SPRITES = [
    on_base("cloud-cumulus-b", 185, 214, 72, 2.37), on_base("cloud-cumulus-a", 408, 214, 58, 2.53),                                   # FEW020
    on_base("cloud-cumulus-b", 140, 156, 80, 2.37), on_base("cloud-cumulus-a", 250, 156, 70, 2.53), on_base("cloud-cumulus-b", 372, 156, 84, 2.37),
    on_base("cloud-cumulus-a", 487, 156, 64, 2.53),                                                                                   # SCT030
    on_base("cloud-stratocumulus", 163, 69, 174, 7.33, 32), on_base("cloud-stratocumulus", 374, 69, 192, 7.33, 34), on_base("cloud-stratocumulus", 558, 69, 132, 7.33, 28),     # BKN045
]


def plate():
    return {
        "id": "fig-16-04-ceiling",
        "replaces": "fig-16-04-ceiling.svg",
        "book_file": "plate-16-04-ceiling.jpg",
        "caption": "Figure 16-4. Cloud base and ceiling with three layers of cloud",
        "desc": "Figure 16-4. Cloud base and ceiling with three layers of cloud",
        "legend": [
            "`FEW020`: the lowest cloud base, 2 000 ft, but not a ceiling.",
            "`SCT030`: scattered, not a ceiling.",
            "`BKN045`: the lowest broken layer, so the ceiling is 4 500 ft.",
            "The aerodrome: report heights are measured from its elevation.",
            "1 000 ft: under a lower ceiling you may not fly VFR beneath it within controlled airspace designated to the surface for an aerodrome [[§91.165(d)]].",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {
            "svg": "fig-16-04-ceiling.svg",
            "remove": [r'<path d="M[\d.]+,[\d.]+ L[^"]*"[^>]*/>'],
            "replace": [[OLD_TINT, SKY]],
            "drop": [[FIRST_CALLOUT, FIRST_CALLOUT, {"sprites": SPRITES}]],
        },
    }
