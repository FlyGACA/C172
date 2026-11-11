"""Figure 14-3. Sea and land breezes, valley and mountain winds. The diagram of the book's figure (the four panels, the sun and the moon, the arrows, the numbered callouts) on a
sky by day and by dusk, with the sea, the land and the ridges shaded, and with the clouds of the model of the sky (reskin.py, figs/clouds.py): the cumulus over the land and over
the ridges, the fog in the valley."""

DAY = '<stop offset="0" stop-color="#8FB4E3"/><stop offset="1" stop-color="#E4EEF9"/>'
NIGHT = '<stop offset="0" stop-color="#7088B3"/><stop offset="1" stop-color="#BFCBE0"/>'
SKIES = ('<defs><linearGradient id="f1403-day" x1="0" y1="0" x2="0" y2="1">' + DAY + '</linearGradient><linearGradient id="f1403-night" x1="0" y1="0" x2="0" y2="1">' + NIGHT + '</linearGradient>'
         '<linearGradient id="f1403-rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D5D9DF"/><stop offset="1" stop-color="#8E97A5"/></linearGradient></defs>'
         '<rect x="8" y="6" width="304" height="162" fill="url(#f1403-day)"/><rect x="328" y="6" width="304" height="162" fill="url(#f1403-night)"/>'
         '<rect x="8" y="218" width="304" height="192" fill="url(#f1403-day)"/><rect x="328" y="218" width="304" height="192" fill="url(#f1403-night)"/>')
BACKGROUND = '<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>'
FIRST_ARROW = '<line x1="60" y1="156" x2="205" y2="156" stroke="#1f2937" stroke-width="3" marker-end="url(#aink)"/>'
MOON4 = '<circle cx="480" cy="244" r="10" fill="#F4EDC8"/>'                        # (the fog of the valley goes in before the moon: after the pool it lies in)
OLD_FOG = '<path d="M 441 368 q 9.75 -7 19.5 0 q 9.75 -7 19.5 0 q 9.75 -7 19.5 0 q 9.75 -7 19.5 0 L 495 391 L 465 391 Z" fill="#ffffff" stroke="#9ca3af" stroke-width="1.4"/>'
STARS = [(566, 36), (606, 44), (578, 20), (616, 22), (456, 250), (496, 258), (468, 234), (506, 236)]
SWAPS = [
    [BACKGROUND, BACKGROUND + SKIES],
    ['<rect x="8" y="168" width="132" height="34" fill="#e8eefc"/>', '<rect x="8" y="168" width="132" height="34" fill="#9DBEE3"/>'],
    ['<path d="M 140 168 L 312 168 L 312 202 L 140 202 Z" fill="#fdf0e1"/>', '<path d="M 140 168 L 312 168 L 312 202 L 140 202 Z" fill="#E6D5B2"/>'],
    ['<rect x="328" y="168" width="132" height="34" fill="#e8eefc"/>', '<rect x="328" y="168" width="132" height="34" fill="#6F89B4"/>'],
    ['<path d="M 460 168 L 632 168 L 632 202 L 460 202 Z" fill="#fdf0e1"/>', '<path d="M 460 168 L 632 168 L 632 202 L 460 202 Z" fill="#A9A08E"/>'],
    ['<polygon points="8,314 52,302 145,392 175,392 268,302 312,314 312,410 8,410" fill="#f3f4f6"', '<polygon points="8,314 52,302 145,392 175,392 268,302 312,314 312,410 8,410" fill="url(#f1403-rock)"'],
    ['<polygon points="328,314 372,302 465,392 495,392 588,302 632,314 632,410 328,410" fill="#f3f4f6"', '<polygon points="328,314 372,302 465,392 495,392 588,302 632,314 632,410 328,410" fill="url(#f1403-rock)"'],
    ['<circle cx="590" cy="30" r="10" fill="#9ca3af"/>', '<circle cx="590" cy="30" r="10" fill="#F4EDC8"/>'],
    ['<circle cx="595.5" cy="27" r="9" fill="#ffffff"/>', '<circle cx="595.5" cy="27" r="9" fill="#7A92B8"/>'],
    ['<circle cx="480" cy="244" r="10" fill="#9ca3af"/>', '<circle cx="480" cy="244" r="10" fill="#F4EDC8"/>'],
    ['<circle cx="485.5" cy="241" r="9" fill="#ffffff"/>', '<circle cx="485.5" cy="241" r="9" fill="#7A92B8"/>'],
] + [[f'<circle cx="{x}" cy="{y}" r="1.3" fill="#9ca3af"/>', f'<circle cx="{x}" cy="{y}" r="1.3" fill="#ffffff"/>'] for x, y in STARS]


def plate():
    return {
        "id": "fig-14-03-local-winds",
        "replaces": "fig-14-03-local-winds.svg",
        "book_file": "plate-14-03-local-winds.jpg",
        "caption": "Figure 14-3. Sea and land breezes, valley and mountain winds",
        "desc": "Figure 14-3. Sea and land breezes, valley and mountain winds",
        "legend": [
            "By day the land heats faster than the sea.",
            "Sea breeze at the surface.",
            "Air rising over the land, building cumulus.",
            "Return flow aloft.",
            "Air sinking over the sea.",
            "At night the land cools faster than the sea.",
            "Land breeze, usually weaker.",
            "Valley wind: air rises up the heated slopes and builds cumulus over the ridges.",
            "Mountain wind: cold air drains down and pools in the valley, where fog can form.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-03-local-winds.svg",
            "remove": [r'<path d="M [\d.]+ [\d.]+ A [^"]*" fill="#ffffff" stroke="#9ca3af" stroke-width="1\.4"/>', r'<path d="M 441 368 q [^"]*" fill="#ffffff" stroke="#9ca3af" stroke-width="1\.4"/>'],
            "replace": SWAPS,
            "drop": [
                [FIRST_ARROW, FIRST_ARROW, {"sprites": [{"name": "cloud-cumulus-b", "at": [237, 42], "width": 64}, {"name": "cloud-cumulus-b", "at": [53, 271], "width": 58}, {"name": "cloud-cumulus-b", "at": [269, 271], "width": 58}]}],
                [MOON4, MOON4, {"sprites": [{"name": "cloud-stratus", "at": [480, 379], "width": 92, "height": 24}]}],
            ],
        },
    }
