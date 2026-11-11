"""Figure 15-1. The three stages of a thunderstorm cell. The diagram of the book's figure with the clouds of the model of the sky (reskin.py, figs/clouds.py): the
outlined circles that stood for a cloud are towering cumulus, cumulonimbus and a dying anvil, on a sky; the arrows, the rain, the hail and the numbered
callouts are drawn again where the new clouds are."""

SKY = ('<defs><linearGradient id="f1501-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A5C3E6"/><stop offset="1" stop-color="#E6EFF9"/></linearGradient></defs>'
       '<rect x="0" y="0" width="640" height="340" fill="url(#f1501-sky)"/>')
FIRST_LINE = '<line x1="213" y1="14" x2="213" y2="340" stroke="#f3f4f6" stroke-width="2"/>'
START = '<circle cx="70" cy="244" r="22" fill="#9ca3af" stroke="#9ca3af" stroke-width="3"/>'          # the first circle of the first cloud ...
END = '<circle cx="107" cy="362" r="11" fill="#1f2937"/>'                                              # ... up to the number under the first panel
BROWN, BLUE = "#b45309", "#1d4ed8"


def up(x, tail, tip):
    return f'<line x1="{x}" y1="{tail}" x2="{x}" y2="{tip + 8}" stroke="{BROWN}" stroke-width="3"/><polygon points="{x},{tip} {x + 5.5},{tip + 10} {x - 5.5},{tip + 10}" fill="{BROWN}"/>'


def down(x, tail, tip):
    return f'<line x1="{x}" y1="{tail}" x2="{x}" y2="{tip - 8}" stroke="{BLUE}" stroke-width="3"/><polygon points="{x},{tip} {x - 5.5},{tip - 10} {x + 5.5},{tip - 10}" fill="{BLUE}"/>'


def rain(x0, y0, x1, y1, xs, width=1.3, dash="5 5", drift=-6):
    return "".join(f'<line x1="{x}" y1="{y0 + (6 if i % 2 else 0)}" x2="{x + drift}" y2="{y1}" stroke="{BLUE}" stroke-width="{width}" stroke-dasharray="{dash}"/>' for i, x in enumerate(xs))


def callout(n, cx, cy, tx, ty):
    return (f'<line x1="{tx}" y1="{ty}" x2="{cx}" y2="{cy}" stroke="#6b7280" stroke-width="1.2"/><circle cx="{cx}" cy="{cy}" r="11" fill="#1f2937"/>'
            f'<text x="{cx}" y="{cy + 4.6}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">{n}</text>')


def hail(points):
    return "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#ffffff" stroke="#1f2937" stroke-width="1.2"/>' for x, y in points)


MARKUP = (
    # first panel: updrafts only
    up(88, 330, 196) + up(107, 334, 150) + up(126, 330, 196) + callout(4, 166, 296, 129, 296)
    # second panel: updrafts on the left of the tower, downdrafts and rain on the right, the gust front on the ground, hail from under the anvil
    + rain(336, 238, 396, 330, [338, 347, 356, 365, 374, 383, 392]) + up(292, 334, 130) + up(310, 334, 156) + down(338, 126, 300) + down(356, 150, 300)
    + f'<path d="M 366 306 C 367.7 309.3 371 321.5 376 326 C 381 330.5 390 331.7 396 333 C 402 334.3 409.3 333.6 412 333.7" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    + f'<polygon points="420,334 409.8,339.1 410.2,328.1" fill="{BLUE}"/>' + hail([(398, 104), (406, 118), (394, 130), (404, 142), (398, 156), (407, 168)])
    + callout(6, 236, 30, 262, 70) + callout(5, 402, 214, 376, 214) + callout(8, 378, 190, 397, 158) + callout(7, 402, 306, 398, 330) + callout(4, 250, 296, 289, 296)
    # third panel: downdrafts only, light rain
    + rain(494, 198, 556, 300, [494, 506, 518, 530, 542, 554], width=1, dash="3 7", drift=-4) + down(506, 140, 318) + down(530, 132, 326) + down(554, 140, 318) + callout(5, 596, 268, 559, 268)
)


def plate():
    return {
        "id": "fig-15-01-thunderstorm-life-cycle",
        "replaces": "fig-15-01-thunderstorm-life-cycle.svg",
        "book_file": "plate-15-01-thunderstorm-life-cycle.jpg",
        "caption": "Figure 15-1. The three stages of a thunderstorm cell",
        "desc": "Figure 15-1. The three stages of a thunderstorm cell",
        "legend": [
            "Cumulus stage: updrafts only.",
            "Mature stage: updrafts and downdrafts side by side, heavy rain and hail.",
            "Dissipating stage: downdrafts only.",
            "Updraft.",
            "Downdraft with rain.",
            "Anvil.",
            "Gust front: cold outflow spreading along the surface.",
            "Hail falling from under the anvil into clear air.",
            "Freezing level (0 °C).",
        ],
        "canvas": [640, 384],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-01-thunderstorm-life-cycle.svg",
            "replace": [[FIRST_LINE, SKY + '<line x1="213" y1="14" x2="213" y2="340" stroke="#ffffff" stroke-opacity="0.7" stroke-width="2"/>'],
                        ['<line x1="427" y1="14" x2="427" y2="340" stroke="#f3f4f6" stroke-width="2"/>', '<line x1="427" y1="14" x2="427" y2="340" stroke="#ffffff" stroke-opacity="0.7" stroke-width="2"/>']],
            "drop": [[START, END, {"sprites": [
                {"name": "cloud-congestus", "at": [107, 183], "width": 111},
                {"name": "cloud-cb", "at": [320, 135], "width": 200},
                {"name": "cloud-anvil", "at": [538, 70], "width": 178},
                {"name": "cloud-congestus", "at": [527, 142], "width": 86, "opacity": 0.6},
            ], "markup": MARKUP}]],
        },
    }
