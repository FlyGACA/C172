"""Figure 14-7. Cloud families by height. A sky in section from the ground to the top of the troposphere, with the clouds of the model of the sky (figs/clouds.py) lying at the
heights where each family is found: the swirling fibres of cirrus, the rows of cirrocumulus and the thin veil of cirrostratus above 20 000 ft, the grey sheet of altostratus and
the rows of altocumulus of the middle levels (the rows seen from below, as they are from the ground), the low layers (a dark nimbostratus with rain, a stratus, a field of
stratocumulus), the cumulus, and the two towers that cross all the heights; a plain of the Arabian Peninsula under them, with haze at the horizon. The two dashed lines of the old
figure and its twelve numbered callouts are kept (figs/scene.py makes the sky, the land and the callouts; reskin.py lays them with the clouds)."""
from figs import scene as S

W, H = 640, 440
HORIZON = 394


def callout_at(k, cx, cy, tx, ty):
    return S.callout(k, cx, cy, tx, ty, r=10.5)


SKY = S.sky("f1407sky", 0, 0, W, 412, [(0.0, "#2A62B0"), (0.28, "#4F89CC"), (0.60, "#8FBBE8"), (0.88, "#DDEBF8"), (1.0, "#FBF2D9")])
LAND = S.landscape("f1407land", 0, W, HORIZON, H, seed=7, mountains=22, hills=9,
                   palms=[(30, 430, 1.25), (44, 434, 1.0), (52, 428, 0.85), (232, 420, 0.7), (606, 432, 1.1)], acacias=[(124, 428, 1.1), (338, 418, 0.8), (418, 424, 1.0)],
                   houses=[(70, 424, 1.0), (268, 414, 0.8), (460, 420, 0.9)])
HAZE = (f'<defs>{S.gradient("f1407haze", [(0, "#F6EBD2", 0.0), (0.6, "#F6EBD2", 0.35), (1, "#F6EBD2", 0.7)])}</defs><rect x="0" y="318" width="{W}" height="{HORIZON - 318 + 4}" fill="url(#f1407haze)"/>')
LINES = (S.altitude_line(0, W, 300, "#FFFFFF", 0.7) + S.altitude_line(0, W, 160, "#FFFFFF", 0.7)
         + '<text x="6" y="295" font-family="sans-serif" font-size="11" font-weight="bold" fill="#FFFFFF" stroke="#2A4F86" stroke-width="2.4" stroke-opacity="0.45" paint-order="stroke">6 500</text>'
         + '<text x="6" y="155" font-family="sans-serif" font-size="11" font-weight="bold" fill="#FFFFFF" stroke="#2A4F86" stroke-width="2.4" stroke-opacity="0.45" paint-order="stroke">20 000</text>')
RAIN = S.rain("f1407rain", 52, 160, 356, 408, slant=-4, count=34, seed=2, colour="#2F55A8") + S.rain("f1407rain2", 548, 598, 370, 410, slant=-4, count=16, seed=5, colour="#2F55A8")
VIRGA = S.rain("f1407virga", 292, 396, 262, 322, slant=-9, count=24, seed=9, colour="#8AA2C6", veil=0.08, bottom=0.0)
LABELS = ('<text x="500" y="431" font-family="monospace" font-size="11" font-weight="bold" fill="#1f2937" text-anchor="middle">TCU</text>'
          '<text x="574" y="431" font-family="monospace" font-size="11" font-weight="bold" fill="#1f2937" text-anchor="middle">CB</text>')

HIGH = [
    {"name": "cloud-cirrus", "at": [140, 64], "width": 290},
    {"name": "cloud-cirrocumulus", "at": [410, 60], "width": 250},
    {"name": "cloud-veil", "at": [222, 132], "width": 440, "height": 26},
]
MID = [
    {"name": "cloud-altostratus", "at": [122, 214], "width": 250, "height": 74},
    {"name": "cloud-altocumulus-deck", "at": [346, 226], "width": 250},
]
LOW = [
    {"name": "cloud-nimbostratus", "at": [106, 336], "width": 210},
    {"name": "cloud-stratus", "at": [236, 380], "width": 132, "height": 26},
    {"name": "cloud-stratocumulus-deck", "at": [346, 340], "width": 190},
    {"name": "cloud-cumulus-c", "at": [444, 362], "width": 114},
    {"name": "cloud-cb-genera", "at": [572, 214], "width": 150, "height": 330},
    {"name": "cloud-tcu", "at": [510, 296], "width": 80, "height": 182},
]

CALLOUTS = (callout_at(1, 22, 96, 70, 74) + callout_at(2, 252, 36, 288, 62) + callout_at(3, 390, 112, 352, 126) + callout_at(4, 28, 222, 66, 246)
            + callout_at(5, 410, 186, 372, 204) + callout_at(6, 400, 262, 346, 262) + callout_at(7, 22, 318, 52, 332) + callout_at(8, 190, 352, 222, 378)
            + callout_at(9, 410, 316, 392, 330) + callout_at(10, 452, 338, 446, 358) + callout_at(11, 452, 232, 490, 260) + callout_at(12, 606, 40, 584, 76))


def plate():
    return {
        "id": "fig-14-07-cloud-families",
        "replaces": "fig-14-07-cloud-families.svg",
        "book_file": "plate-14-07-cloud-families.jpg",
        "caption": "Figure 14-7. Cloud families by height",
        "desc": "Figure 14-7. Cloud families by height",
        "legend": [
            "Cirrus.", "Cirrocumulus.", "Cirrostratus.", "Altostratus.", "Altocumulus.", "Virga.", "Nimbostratus.", "Stratus.", "Stratocumulus.", "Cumulus.",
            "Towering cumulus, `TCU` in a METAR.", "Cumulonimbus, `CB`.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {
            "svg": "fig-14-07-cloud-families.svg",
            "blank": True,
            "layers": [SKY, *HIGH, *MID[:1], VIRGA, *MID[1:], *LOW, RAIN, HAZE, LAND, LINES, LABELS, CALLOUTS],
        },
    }
