"""Figure 15-7. Where structural ice forms: temperature, height and visible moisture. The diagram of the book's figure (the temperature line, the icing band, the aerodrome, the
numbered callouts) with the cloud of the model of the sky in place of the outlined tower, on a sky, and with the model for the three aeroplanes, painted dark where they
fly in the cloud (reskin.py, figs/clouds.py, figs/kit.py)."""
from reskin import LOOK                    # noqa: E402
from figs.kit import side_plane            # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'
DARK = {"tint": "#2A3347", "tint_strength": 0.92, "outline": {"width": 0.5, "colour": "#FFFFFF", "opacity": 0.7}, "shadow": {"dx": 1.0, "dy": 1.6, "blur": 1.2, "opacity": 0.3}}
GREEN = {**LOOK, "tint": "#047857", "tint_strength": 0.62}
BACKGROUND = '<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>'
SKY = ('<defs><linearGradient id="f1507-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E9F1FA"/></linearGradient></defs>'
       '<rect x="360" y="36" width="280" height="258" fill="url(#f1507-sky)"/>')
BAND = '<rect x="74" y="91" width="556" height="105" fill="#e8eefc"/>'
FIRST_DROPLET = '<circle cx="432" cy="224" r="2.6" fill="#1d4ed8"/>'
REMOVE = [
    r'<circle [^>]*fill="#9ca3af" stroke="#9ca3af" stroke-width="3"/>',                          # the outlined tower ...
    r'<rect x="408" y="225\.4" width="128" height="12\.6" fill="#(?:9ca3af|ffffff)"[^>]*/>',
    r'<circle cx="[\d.]+" cy="[\d.]+" r="(?:2\d|3[0-2])" fill="#ffffff"/>',                      # ... and its fill
]


def plate():
    return {
        "id": "fig-15-07-icing-band",
        "replaces": "fig-15-07-icing-band.svg",
        "book_file": "plate-15-07-icing-band.jpg",
        "caption": "Figure 15-7. Where structural ice forms: temperature, height and visible moisture",
        "desc": "Figure 15-7. Where structural ice forms: temperature, height and visible moisture",
        "legend": [
            "Temperature falling about 2 °C per 1 000 ft.",
            "Freezing level (0 °C), here about 9 000 ft.",
            "0 °C to −15 °C: clear ice builds fastest here in convective cloud.",
            "Cloud below the freezing level: liquid droplets, no structural ice.",
            "Cloud above the freezing level: supercooled droplets freeze on the leading edges.",
            "Clear air above the freezing level: no visible moisture, no structural ice.",
            "The aerodrome: 14 °C at 2 000 ft.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-07-icing-band.svg",
            "remove": REMOVE,
            "replace": [[BACKGROUND, BACKGROUND + SKY], [BAND, '<rect x="74" y="91" width="556" height="105" fill="#1d4ed8" fill-opacity="0.12"/>']],
            "drop": [
                [FIRST_DROPLET, FIRST_DROPLET, {"sprites": [{"name": "cloud-congestus", "at": [470, 147], "width": 138, "height": 211}]}],
                [START, '<path d="M 492 142.4 Q 501 149.4 492 155.4"', {"sprites": [side_plane(476, 148.4, 0, 0.95, SILHOUETTE, grow=1.2, look=DARK)]}],
                [START, '<line x1="206.8" y1="251.8"', {"sprites": [side_plane(586, 148.4, 0, 0.95, SILHOUETTE, grow=1.2, look=GREEN), side_plane(474, 212.8, 0, 0.95, SILHOUETTE, grow=1.2, look=DARK)]}],
            ],
        },
    }
