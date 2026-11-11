"""Figure 15-3. Windshear at the top of a surface inversion after a calm night. The diagram of the book's figure (the temperature curve, the inversion, the winds, the runway, the numbered
callouts) with a sky behind the scene, the ground coloured, and the model for the departing aeroplane (reskin.py, figs/kit.py)."""
from figs.kit import side_plane            # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'
BACKGROUND = '<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>'
SKY = ('<defs><linearGradient id="f1503-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E4EEF9"/></linearGradient></defs>'
       '<rect x="270" y="40" width="370" height="270" fill="url(#f1503-sky)"/>')
BAND = '<rect x="70" y="202" width="560" height="108" fill="#e8eefc"/>'
GROUND = '<rect x="270" y="310" width="370" height="50" fill="#f3f4f6"/>'


def plate():
    return {
        "id": "fig-15-03-inversion-windshear",
        "replaces": "fig-15-03-inversion-windshear.svg",
        "book_file": "plate-15-03-inversion-windshear.jpg",
        "caption": "Figure 15-3. Windshear at the top of a surface inversion after a calm night",
        "desc": "Figure 15-3. Windshear at the top of a surface inversion after a calm night",
        "legend": [
            "Temperature rising with height through the inversion.",
            "Top of the inversion.",
            "Calm or light wind in the cool surface layer.",
            "Strong wind above, here from behind a departing aeroplane.",
            "The aeroplane meets a sudden tailwind and loses airspeed.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-03-inversion-windshear.svg",
            "replace": [[BACKGROUND, BACKGROUND + SKY], [BAND, '<rect x="70" y="202" width="560" height="108" fill="#1d4ed8" fill-opacity="0.12"/>'], [GROUND, GROUND.replace("#f3f4f6", "#E7DCC3")]],
            "drop": [[START, '<line x1="129.8" y1="245.3" x2="145.6" y2="270.4"', {"sprites": [side_plane(519.8, 228.8, -42.2, 1.0, SILHOUETTE, grow=1.3)]}]],
        },
    }
