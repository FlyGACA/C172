"""Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow. A dusty sky over a desert plain: the dark base of a thunderstorm and its rain at the right, the cold outflow
running along the ground under it as a blue wedge with a rolled nose, the wall of dust standing at the nose (billows painted the colour of the sand, with the warm air rising
inside), and an aerodrome in the path. The clouds are the sprites of figs/clouds.py; the land, the arrows and the rain come from figs/scene.py; the eight numbered callouts of the
old figure and their places are kept."""
from figs import scene as S

ORANGE = ("#D2691E", "#F3B676")
BLUE = ("#2F63C8", "#8DB3F2")
INK = ("#1F2937", "#667489")
HORIZON = 312
SKY = S.sky("f1504sky", 0, 0, 640, 330, [(0.0, "#6E96C8"), (0.45, "#A9C0DA"), (0.8, "#E2D9C2"), (1.0, "#EAD6AE")])
HILLS = (S.land_layer("f1504h1", S.ridge(5, 0, 640, HORIZON + 2, 40, peaks=0.55), HORIZON + 6, ("#9A8A86", "#C9B79C"), rim=False, haze=0.35, haze_colour="#E8D8B8")
         + S.land_layer("f1504h2", S.ridge(9, 0, 640, HORIZON + 3, 20, peaks=0.3), HORIZON + 6, ("#B5A48A", "#D8C49D"), rim=False, haze=0.25, haze_colour="#E8D8B8"))
RAIN = S.rain("f1504rain", 456, 580, 96, 262, slant=-8, count=60, seed=3, colour="#33508F", veil=0.30, bottom=0.0)

# the cold outflow: a wedge along the ground from the right with a rolled nose at the gust front
WEDGE = [(640, 322), (640, 268), (560, 258), (470, 254), (380, 252), (310, 254), (262, 262), (240, 276), (232, 296), (234, 322)]
OUTFLOW = (S.air("f1504air", WEDGE, "#6D93D8", "#C6D8F4", 0.55)
           + f'<path d="M 640,268 C 560,258 470,254 380,252 C 320,252 270,256 248,270 C 238,278 233,292 233,322" fill="none" stroke="#2F5DB5" stroke-width="1.8" stroke-opacity="0.9"/>')

GROUND = (f'<defs>{S.gradient("f1504gr", [(0, "#E8D4A4"), (1, "#C9AC78")])}</defs><rect x="0" y="{HORIZON}" width="640" height="{360 - HORIZON}" fill="url(#f1504gr)"/>'
          + S.dune("f1504d1", 0, 640, HORIZON + 8, 7, 4, colours=("#F0DDB0", "#D5B982"), crest="#FFF4D4")
          + S.dune("f1504d2", 0, 640, HORIZON + 30, 6, 11, colours=("#E9D3A0", "#C9AA74"), crest="#FFF0CC")
          + S.scrub(6, 0, 640, HORIZON + 6, 356, 46, scale=0.8))
AERODROME = (f'<rect x="12" y="320" width="112" height="9" fill="#4A4F5A"/><rect x="12" y="320" width="112" height="1.3" fill="#8C93A0"/>'
             + "".join(f'<rect x="{20 + 14 * i}" y="324" width="8" height="1.3" fill="#F3F4F6"/>' for i in range(7))
             + S.house(34, 318, 20, 11, 3) + S.house(60, 316, 14, 9, 5)
             + '<g><rect x="96" y="304" width="3" height="14" fill="#6B7280"/><rect x="92" y="298" width="11" height="7" fill="#9AA3B2"/><rect x="93.5" y="299.5" width="8" height="3" fill="#7FB0D8"/></g>'
             + '<g><line x1="116" y1="320" x2="116" y2="306" stroke="#6B7280" stroke-width="1.2"/><path d="M 116,306 L 128,308 L 116,311 Z" fill="#F36F21"/></g>')
DUST_FLOOR = S.fog("f1504dust", 100, 400, HORIZON + 16, 70, seed=5, opacity=0.9, colour="#D4B27C", wisp=0.9, side_fade=0.22, foot=0.0)
DUST_TRAIL = S.fog("f1504dust2", 220, 520, HORIZON + 24, 40, seed=8, opacity=0.5, colour="#D8BC8C", wisp=1.0, side_fade=0.3, foot=0.0)

ARROWS = "".join([
    S.ribbon("f1504u1", [(222, 306), (212, 262), (212, 218), (218, 180)], 7.0, *ORANGE),
    S.ribbon("f1504u2", [(252, 296), (250, 252), (258, 206), (270, 160)], 7.0, *ORANGE),
    S.ribbon("f1504d1", [(498, 120), (498, 190), (498, 252)], 6.5, *BLUE),
    S.ribbon("f1504d2", [(532, 120), (532, 190), (532, 252)], 6.5, *BLUE),
    S.ribbon("f1504o1", [(566, 300), (470, 300), (370, 300), (272, 298)], 7.0, *BLUE),
    S.ribbon("f1504o2", [(618, 278), (560, 278), (510, 277), (472, 277)], 5.5, *BLUE),
    S.ribbon("f1504mv", [(332, 46), (290, 46), (240, 46), (192, 46)], 6.0, *INK),
])

c = S.callout
CALLOUTS = "".join([c(1, 608, 146, 600, 124), c(2, 566, 196, 538, 196), c(3, 400, 280), c(4, 232, 340, 234, 318), c(5, 110, 196, 160, 206), c(6, 352, 46, 336, 46), c(7, 66, 340, 66, 322), c(8, 166, 120, 212, 184)])

CLOUDS = [
    {"name": "cloud-stormbase", "at": [496, 66], "width": 262},
    {"name": "cloud-congestus", "at": [168, 238], "width": 128, "tint": "#C9A06B", "tint_strength": 0.78, "flip": True},
    {"name": "cloud-congestus", "at": [250, 204], "width": 190, "tint": "#C9A06B", "tint_strength": 0.75},
    {"name": "cloud-congestus", "at": [320, 252], "width": 120, "tint": "#CFAA74", "tint_strength": 0.78},
]


def plate():
    return {
        "id": "fig-15-04-haboob",
        "replaces": "fig-15-04-haboob.svg",
        "book_file": "plate-15-04-haboob.jpg",
        "caption": "Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow",
        "desc": "Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow",
        "legend": [
            "Thunderstorm.",
            "Cold downdraft with heavy rain.",
            "Cold, dense outflow spreading along the surface.",
            "Gust front: sudden wind shift and strong gusts.",
            "Wall of dust.",
            "Direction of movement.",
            "An aerodrome in its path.",
            "Warmer air forced up at the gust front, carrying dust aloft.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-15-04-haboob.svg", "blank": True,
                   "layers": ['<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', SKY, HILLS, *CLOUDS, RAIN, OUTFLOW, GROUND, DUST_FLOOR, DUST_TRAIL, AERODROME, ARROWS, CALLOUTS]},
    }
