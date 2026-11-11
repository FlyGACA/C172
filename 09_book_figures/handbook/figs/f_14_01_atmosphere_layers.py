"""Figure 14-1. The layers of the atmosphere and the ISA temperature profile. The diagram of the book's figure (the layers, the temperature line, the pressure bar, the numbered callouts)
with the cumulonimbus of the model of the sky in place of the cartoon one (reskin.py, figs/clouds.py): the anvil spreads under the tropopause as before."""

CLOUD = '<path d="M 433 334.3 A'
BOLT = '<path d="M 466 262 L 457 285'


def plate():
    return {
        "id": "fig-14-01-atmosphere-layers",
        "replaces": "fig-14-01-atmosphere-layers.svg",
        "book_file": "plate-14-01-atmosphere-layers.jpg",
        "caption": "Figure 14-1. The layers of the atmosphere and the ISA temperature profile",
        "desc": "Figure 14-1. The layers of the atmosphere and the ISA temperature profile",
        "legend": [
            "Troposphere.",
            "ISA temperature, falling about 2 °C per 1 000 ft.",
            "Sea level: 15 °C and 1 013 hPa.",
            "Tropopause, about 36 000 ft in the ISA.",
            "Stratosphere.",
            "A cumulonimbus whose top spreads into an anvil under the tropopause.",
            "ISA pressure in hPa; at 18 000 ft it is about half the sea-level value.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-01-atmosphere-layers.svg",
            "drop": [[CLOUD, BOLT, {"sprites": [{"name": "cloud-cb", "at": [466, 252], "width": 130, "height": 162}]}]],
        },
    }
