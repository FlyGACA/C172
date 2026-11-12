"""Figure 14-8. Radiation fog: the temperature falls to the dew point overnight. The diagram of the book's figure (the temperature and dew point curves, the three scenes, the numbered
callouts) with a sky behind each scene and the clouds of the model of the sky in place of the outlines (reskin.py, figs/clouds.py): the fog filling the hollow at dawn, and the low
stratus it lifts into by mid-morning."""

BACKGROUND = '<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>'
SKIES = ('<defs><linearGradient id="f1408-eve" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6F86B0"/><stop offset="1" stop-color="#C9D3E6"/></linearGradient>'
         '<linearGradient id="f1408-dawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9BEE0"/><stop offset="1" stop-color="#F3E6D3"/></linearGradient>'
         '<linearGradient id="f1408-day" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FB4E3"/><stop offset="1" stop-color="#E4EEF9"/></linearGradient></defs>'
         '<rect x="12" y="230" width="196" height="160" fill="url(#f1408-eve)"/><rect x="222" y="230" width="196" height="160" fill="url(#f1408-dawn)"/>'
         '<rect x="432" y="230" width="196" height="160" fill="url(#f1408-day)"/>')
STARS = [(148, 264), (188, 272), (160, 248), (198, 250)]
SWAPS = [[BACKGROUND, BACKGROUND + SKIES],
         ['<circle cx="172" cy="258" r="9" fill="#9ca3af"/>', '<circle cx="172" cy="258" r="9" fill="#F4EDC8"/>'],
         ['<circle cx="176.9" cy="255.3" r="8.1" fill="#ffffff"/>', '<circle cx="176.9" cy="255.3" r="8.1" fill="#8296BA"/>']
         ] + [[f'<circle cx="{x}" cy="{y}" r="1.3" fill="#9ca3af"/>', f'<circle cx="{x}" cy="{y}" r="1.3" fill="#ffffff"/>'] for x, y in STARS]


def plate():
    return {
        "id": "fig-14-08-radiation-fog",
        "replaces": "fig-14-08-radiation-fog.svg",
        "book_file": "plate-14-08-radiation-fog.jpg",
        "caption": "Figure 14-8. Radiation fog: the temperature falls to the dew point overnight",
        "desc": "Figure 14-8. Radiation fog: the temperature falls to the dew point overnight",
        "legend": [
            "Temperature, falling through a clear night.",
            "Dew point, almost steady.",
            "The spread closes and fog forms.",
            "Sunrise.",
            "Evening: clear and calm, the ground radiating heat.",
            "Dawn: fog in the low ground, thickest in the hollow.",
            "Mid-morning: the ground heats and the fog lifts and breaks up.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-08-radiation-fog.svg",
            "replace": SWAPS,
            "drop": [
                ['<path d="M 222 390 L 222 372', '<circle cx="392" cy="270" r="8"', {"sprites": [{"name": "cloud-veil", "at": [320, 380], "width": 196, "height": 34}]}],
                ['<path d="M 454 310 L 454 302', '<line x1="472" y1="386" x2="472" y2="350"', {"sprites": [
                    {"name": "cloud-cumulus-b", "at": [476, 303], "width": 50, "height": 17}, {"name": "cloud-cumulus-b", "at": [529, 304], "width": 46, "height": 15},
                    {"name": "cloud-cumulus-b", "at": [580, 303], "width": 50, "height": 17}]}],               # (low lumps of stratocumulus: flat-bottomed cumulus, pressed down)
            ],
        },
    }
