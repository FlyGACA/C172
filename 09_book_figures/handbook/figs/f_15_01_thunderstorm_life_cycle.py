"""Figure 15-1. The three stages of a thunderstorm cell. Three scenes in cards over a plain of the Peninsula: a towering cumulus with its updrafts (cumulus stage), a mature
cumulonimbus with updrafts and downdrafts side by side, rain, hail, a bolt and the gust front (mature stage), and a spent anvil over a fading tower with light rain
(dissipating stage); one dashed line across all three marks the freezing level. The clouds are the sprites of figs/clouds.py, the ribbon arrows, the rain and the land come
from figs/scene.py; the nine numbered callouts of the old figure and their places are kept."""
from figs import scene as S

CARDS = {1: (6, 6, 200, 330), 2: (220, 6, 200, 330), 3: (434, 6, 200, 330)}
HZ = 270                                         # the horizon of every card
ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")
DAY = [(0.0, "#3A74C0"), (0.55, "#7FB0E4"), (0.92, "#D6E7F7"), (1.0, "#F4F1DF")]
STORM = [(0.0, "#2F3F66"), (0.45, "#5D7099"), (0.9, "#A9B6CC"), (1.0, "#C9D0DA")]
FADE = [(0.0, "#5E86BE"), (0.5, "#9DBFE6"), (0.92, "#E3EDF7"), (1.0, "#F6EEDA")]


def backs():
    out = []
    for k, stops in ((1, DAY), (2, STORM), (3, FADE)):
        x, y, w, h = CARDS[k]
        extra = ""
        if k == 1:
            extra = S.sun("f1501s1", x + 168, y + 36, 8)
        if k == 3:
            extra = S.sun("f1501s3", x + 36, y + 40, 8)
        out.append(S.card(f"f1501b{k}", x, y, w, h, stops, extra))
    return "".join(out)


def fronts():
    out = []
    for k, tone, houses, palms, acacias in ((1, "day", [(30, 306, 1.0), (150, 300, 0.8)], [(56, 316, 1.1), (176, 314, 1.0)], [(112, 322, 1.0)]),
                                           (2, "storm", [(236, 304, 0.9)], [(250, 318, 1.0), (404, 314, 1.0)], [(300, 322, 1.1), (352, 328, 1.0)]),
                                           (3, "dusk", [(450, 302, 0.9), (572, 310, 1.0)], [(470, 316, 1.0), (606, 318, 0.9)], [(530, 324, 1.1)])):
        x, y, w, h = CARDS[k]
        body = S.plain(f"f1501g{k}", x, x + w, HZ, y + h, seed=2 + k, tone=tone, houses=houses, palms=palms, acacias=acacias)
        body += S.altitude_line(x, x + w, 196, "#FFFFFF", 0.85, dash="6 5", width=1.4) + S.snowflake(x + 12, 196)
        if k == 2:
            body += (S.rain("f1501r2", 334, 392, 232, 300, slant=-6, count=44, seed=4, colour="#3A63B4", veil=0.26) + S.lightning("f1501l", 266, 238, 292, seed=3)
                     + S.hailstones([(397, 142), (405, 158), (395, 173), (404, 189), (398, 204), (406, 219)]))
        if k == 3:
            body += S.rain("f1501r3", 492, 576, 214, 296, slant=-4, count=24, seed=6, colour="#4F73B8", veil=0.10)
        out.append(S.card_front(f"f1501f{k}", x, y, w, h, body))
    return "".join(out)


def arrows():
    r = S.ribbon
    a = []
    # cumulus stage: updrafts only
    a += [r("f1501u1", [(88, 318), (88, 270), (88, 214)], 6.0, *ORANGE), r("f1501u2", [(106, 322), (106, 250), (106, 156)], 6.5, *ORANGE), r("f1501u3", [(124, 318), (124, 270), (124, 214)], 6.0, *ORANGE)]
    # mature stage: updrafts on the left of the tower, downdrafts and rain on the right, the gust front on the ground
    a += [r("f1501u4", [(287, 322), (286, 240), (286, 140)], 6.0, *ORANGE), r("f1501u5", [(303, 322), (303, 240), (302, 166)], 6.0, *ORANGE),
          r("f1501d1", [(335, 128), (335, 200), (335, 292)], 6.0, *BLUE), r("f1501d2", [(351, 152), (351, 214), (352, 292)], 6.0, *BLUE),
          r("f1501g", [(352, 316), (380, 318), (416, 316)], 5.5, *BLUE)]
    # dissipating stage: downdrafts only
    a += [r("f1501d3", [(506, 150), (506, 230), (506, 308)], 5.5, *BLUE), r("f1501d4", [(530, 142), (530, 226), (530, 316)], 5.5, *BLUE), r("f1501d5", [(554, 150), (554, 230), (554, 308)], 5.5, *BLUE)]
    return "".join(a)


def callouts():
    c = S.callout
    strip = ('<defs><linearGradient id="f1501strip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDF2F9"/><stop offset="1" stop-color="#DCE5F1"/></linearGradient></defs>'
             '<rect x="0" y="344" width="640" height="40" fill="url(#f1501strip)"/><line x1="0" y1="344" x2="640" y2="344" stroke="#B7C3D6" stroke-width="1"/>')
    return strip + "".join([c(1, 107, 364), c(2, 320, 364), c(3, 533, 364),
                            c(4, 166, 296, 128, 296), c(4, 250, 296, 284, 296), c(6, 236, 30, 258, 122), c(5, 402, 214, 356, 214), c(8, 372, 196, 395, 176), c(7, 404, 292, 392, 314),
                            c(5, 596, 268, 560, 268), c(9, 190, 196)])


CLOUDS = [
    {"name": "cloud-congestus", "at": [106, 186], "width": 140},
    {"name": "cloud-cb", "at": [320, 172], "width": 200, "height": 190},
    {"name": "cloud-anvil", "at": [534, 84], "width": 196},
    {"name": "cloud-congestus", "at": [534, 178], "width": 96, "opacity": 0.5},
]


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
        "reskin": {"svg": "fig-15-01-thunderstorm-life-cycle.svg", "blank": True,
                   "layers": ['<rect x="0" y="0" width="640" height="384" fill="#ffffff"/>', backs(), *CLOUDS, fronts(), arrows(), callouts()]},
    }
