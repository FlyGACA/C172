"""Figure 14-6. Four ways air is lifted. The diagram of the book's figure (the four panels, the arrows, the sun, the rain, the callouts) on a sky and with the clouds of the
model of the sky (reskin.py, figs/clouds.py) in place of the outlines: a cumulus over the warm ground, one building over the high ground, a thick rain cloud over the
cold wedge of a front and one over the meeting winds."""

SKY_STOPS = '<stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E9F1FA"/>'
SKIES = ('<defs><linearGradient id="f1406-sky" x1="0" y1="0" x2="0" y2="1">' + SKY_STOPS + '</linearGradient></defs>'
         '<rect x="8" y="6" width="304" height="170" fill="url(#f1406-sky)"/><rect x="328" y="6" width="304" height="194" fill="url(#f1406-sky)"/>'
         '<rect x="8" y="218" width="304" height="184" fill="url(#f1406-sky)"/><rect x="328" y="218" width="304" height="184" fill="url(#f1406-sky)"/>')
BACKGROUND = '<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>'
OLD_TINT = '<rect x="8" y="218" width="304" height="184" fill="#fdf0e1" opacity="0.6"/>'          # (the third panel's beige ground, under what is all air)
DIVIDER = '<line x1="320" y1="6" x2="320" y2="414" stroke="#9ca3af" stroke-width="1"/>'
REMOVE = [r'<path d="M [\d.]+ [\d.]+ A [^"]*" fill="#ffffff" stroke="#9ca3af" stroke-width="1\.4"/>']          # the four outlined clouds


def plate():
    return {
        "id": "fig-14-06-lifting",
        "replaces": "fig-14-06-lifting.svg",
        "book_file": "plate-14-06-lifting.jpg",
        "caption": "Figure 14-6. Four ways air is lifted",
        "desc": "Figure 14-6. Four ways air is lifted",
        "legend": [
            "Convection: heated ground sends up bubbles of warm air; air sinks over cooler water or vegetation.",
            "Orographic lift: wind forced up a slope, descending on the lee side.",
            "Sun-heated slopes add their own rising air, so cumulus builds over high ground in the afternoon.",
            "Frontal lift: colder air pushes under warmer air.",
            "Convergence: surface winds meet and the air goes up, as where a sea breeze meets another wind.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-06-lifting.svg",
            "remove": REMOVE,
            "replace": [[BACKGROUND, BACKGROUND + SKIES], [OLD_TINT, ""]],
            "drop": [[DIVIDER, DIVIDER, {"sprites": [
                {"name": "cloud-cumulus-a", "at": [122, 52], "width": 104},
                {"name": "cloud-congestus", "at": [534, 46], "width": 56},
                {"name": "cloud-nimbostratus", "at": [130, 279], "width": 120, "height": 44},
                {"name": "cloud-cumulus-a", "at": [480, 278], "width": 120},
            ]}]],
        },
    }
