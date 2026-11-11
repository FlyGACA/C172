"""Figure 15-5. Looking down and looking ahead through a dust layer. The diagram of the book's figure (the layer, the two lines of sight, the runway, the numbered callouts) on a sky,
with the dust layer and the ground coloured, and with the model for the two aeroplanes (reskin.py, figs/kit.py)."""
from figs.kit import side_plane            # noqa: E402

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
START = '<path d="M-24.8 -9.3'
BACKGROUND = '<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>'
SKY = ('<defs><linearGradient id="f1505-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FB4E3"/><stop offset="1" stop-color="#D4E3F3"/></linearGradient>'
       '<linearGradient id="f1505-dust" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E4D3B2"/><stop offset="1" stop-color="#D8C39B"/></linearGradient></defs>'
       '<rect x="0" y="0" width="640" height="150" fill="url(#f1505-sky)"/>')
DUST = '<rect x="0" y="150" width="640" height="150" fill="#fdf0e1"/>'
GROUND = '<rect x="0" y="300" width="640" height="60" fill="#f3f4f6"/>'


def plate():
    return {
        "id": "fig-15-05-slant-visibility",
        "replaces": "fig-15-05-slant-visibility.svg",
        "book_file": "plate-15-05-slant-visibility.jpg",
        "caption": "Figure 15-5. Looking down and looking ahead through a dust layer",
        "desc": "Figure 15-5. Looking down and looking ahead through a dust layer",
        "legend": [
            "Dust or haze layer.",
            "Looking straight down: a short path through the dust, ground in sight.",
            "Looking ahead along the approach: a long path through the dust, runway not in sight.",
            "Runway.",
            "Reported visibility, measured horizontally near the surface.",
            "Lower and closer, the runway appears: late, perhaps too late for a stable approach.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-05-slant-visibility.svg",
            "replace": [[BACKGROUND, BACKGROUND + SKY], [DUST, '<rect x="0" y="150" width="640" height="150" fill="url(#f1505-dust)"/>'], [GROUND, GROUND.replace("#f3f4f6", "#E7DCC3")]],
            "drop": [
                [START, '<line x1="104" y1="82" x2="104" y2="300"', {"sprites": [side_plane(104, 74, 16, 1.0, SILHOUETTE, grow=1.3)]}],
                [START, '<line x1="469" y1="275" x2="540" y2="297"', {"sprites": [side_plane(452, 270, 12, 1.0, SILHOUETTE, grow=1.3)]}],
            ],
        },
    }
