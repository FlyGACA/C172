"""Figure 18-2 (new in the open-data round: the book had no such figure). The declared distances of runway 17/35 at Thumamah (OETH).

The aerodrome lies along the page to scale, north to the left (figs/h_b4.py draws the runway, the stopways, the pavements, the roofs and the road from data/oeth_plan.json, as figure 18-1
does). Above it four bars for runway 35, used for taking off and landing towards the north (to the left); below it four bars for runway 17. Each bar runs from where the distance starts (a dark
end plate) to where it ends (the tip of the arrowhead, which points the way the aeroplane goes), so their lengths can be compared with the runway and with each other.

The numbers are the AIP's (AD 2.13, AMDT 11/26): TORA, TODA and LDA 4 000 m in both directions; ASDA 4 300 m for runway 35 and 4 060 m for runway 17, that is the runway and the stopway
that lies ahead (AD 2.12: 300 m beyond the north end, 60 m beyond the south end; no clearway). The stopway part of each ASDA bar is striped in the yellow of the stopway outline.
The bars span the thresholds of the plan, which lie 4 004.6 m apart by the AIP's coordinates; the labels give the declared 4 000 m (a difference of a twentieth of a unit on the page).
The letters in the picture are the AIP's own codes and the metre; everything else is a numbered callout. The two aeroplanes beside the designators only show the direction."""
from figs import h_a2 as H2
from figs import h_b4 as B
from figs import scene as S
from figs import terrain

W, HT = 640, 380
terrain.ensure("terrain-18-02-thumamah", size=(W * 4, HT * 4), seed=1802, kind="plain", features=("wadis",), veil=0.36, soft=2.8)

PX, PY, PW, PH = 8, 8, 624, 364
K = 0.1305                                         # units to the metre: the 4 364.6 m from the end of one stopway to the end of the other across 570 units
Y0 = 190.0                                         # the runway centreline on the page
P = B.Plan(40.0 + B.STOP_N * K, Y0, K)
SPR = {"shadow": {"dx": 0.9, "dy": 1.5, "blur": 1.1, "opacity": 0.34}, "outline": {"width": 0.35, "colour": "#2B3648", "opacity": 0.8}}

THR17, THR35 = B.S_N, B.S_S                        # the two thresholds in the frame (metres from the threshold of runway 17)
END_N, END_S = THR17 - B.STOP_N, THR35 + B.STOP_S   # the far ends of the two stopways

# the AIP's table (AD 2.13), metres
DECLARED = {"35": {"TORA": 4000, "TODA": 4000, "ASDA": 4300, "LDA": 4000}, "17": {"TORA": 4000, "TODA": 4000, "ASDA": 4060, "LDA": 4000}}
assert DECLARED["35"]["ASDA"] == DECLARED["35"]["TORA"] + B.STOP_N and DECLARED["17"]["ASDA"] == DECLARED["17"]["TORA"] + B.STOP_S

ROWS = {"35": {"TORA": 68.0, "TODA": 90.0, "ASDA": 112.0, "LDA": 134.0}, "17": {"TORA": 250.0, "TODA": 272.0, "ASDA": 294.0, "LDA": 316.0}}
COLOURS = {"TORA": ("#1D4ED8", "#3B73EE", "#A9C4FF"), "TODA": ("#6B4FB8", "#8A70D8", "#D9CEF8"), "ASDA": ("#C2410C", "#E8662B", "#FFD0B0"), "LDA": ("#047857", "#12A37B", "#A7F3D0")}
LX = 320.0                                         # the column of the labels
GUIDE = (57, 327)                                  # the guide lines at the thresholds, from and to (page y)
BAR_H, HEAD_L, HEAD_W = 8.0, 11.0, 15.0


def X(s):
    return P.xy(s, 0.0)[0]


def span(rwy, code):
    """Where a declared distance starts and ends in the frame (metres): the takeoff and the landing of runway 35 start at its threshold (the south end) and run north."""
    start, far, beyond = (THR35, THR17, END_N) if rwy == "35" else (THR17, THR35, END_S)
    return (start, beyond if code == "ASDA" else far)


def bar_outline(x0, x1, y):
    d = 1.0 if x1 > x0 else -1.0
    xb = x1 - d * HEAD_L
    return [(x0, y - BAR_H / 2), (xb, y - BAR_H / 2), (xb, y - HEAD_W / 2), (x1, y), (xb, y + HEAD_W / 2), (xb, y + BAR_H / 2), (x0, y + BAR_H / 2)]


def bar(uid, rwy, code):
    """One declared distance: a lit bar with a white casing and a soft shadow, a dark end plate where it starts, an arrowhead whose tip is where it ends; over a stopway it is striped."""
    base, mid, hi = COLOURS[code]
    s0, s1 = span(rwy, code)
    x0, x1, y = X(s0), X(s1), ROWS[rwy][code]
    d = 1.0 if x1 > x0 else -1.0
    poly = S.pts(bar_outline(x0, x1, y))
    xb = x1 - d * HEAD_L
    out = [f'<polygon points="{poly}" fill="#10233F" fill-opacity="0.32" transform="translate(0.9 1.8)" filter="url(#b4rs)"/>',
           f'<polygon points="{poly}" fill="#FFFFFF" fill-opacity="0.95" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="2.4" stroke-linejoin="round"/>',
           f'<polygon points="{poly}" fill="{base}" stroke="{base}" stroke-width="0.4" stroke-linejoin="round"/>',
           f'<rect x="{min(x0, xb):.2f}" y="{y - BAR_H / 2 + 0.9:.2f}" width="{abs(xb - x0):.2f}" height="{BAR_H * 0.5:.2f}" fill="{mid}"/>',
           f'<line x1="{x0:.2f}" y1="{y - BAR_H / 2 + 1.5:.2f}" x2="{xb:.2f}" y2="{y - BAR_H / 2 + 1.5:.2f}" stroke="{hi}" stroke-opacity="0.8" stroke-width="0.8"/>']
    if code == "ASDA":                                   # the stopway part: striped in the stopway's yellow, inside the outline of the bar
        xa = X(THR17 if rwy == "35" else THR35)
        out.append(f'<clipPath id="{uid}c"><polygon points="{poly}"/></clipPath>'
                   f'<rect x="{min(xa, x1):.2f}" y="{y - HEAD_W / 2 - 1:.2f}" width="{abs(x1 - xa):.2f}" height="{HEAD_W + 2:.2f}" fill="url(#dd-stripes)" clip-path="url(#{uid}c)"/>'
                   f'<line x1="{xa:.2f}" y1="{y - BAR_H / 2 - 0.2:.2f}" x2="{xa:.2f}" y2="{y + BAR_H / 2 + 0.2:.2f}" stroke="#FFFFFF" stroke-width="1.0"/>')
    # the end plate at the start
    out.append(f'<rect x="{x0 - 2.3:.2f}" y="{y - BAR_H / 2 - 4.3:.2f}" width="4.6" height="{BAR_H + 8.6:.2f}" rx="1.3" fill="#FFFFFF" fill-opacity="0.95"/>'
               f'<rect x="{x0 - 1.2:.2f}" y="{y - BAR_H / 2 - 3.2:.2f}" width="2.4" height="{BAR_H + 6.4:.2f}" rx="0.7" fill="{B.INK}"/>')
    return "".join(out)


def pill(rwy, code):
    """The label of a bar: the AIP's code and the declared length, on a pale plate in the column of the labels."""
    base = COLOURS[code][0]
    y = ROWS[rwy][code]
    metres = f"{DECLARED[rwy][code]:,}".replace(",", "\u2009") + " m"
    return (f'<rect x="{LX - 47:.1f}" y="{y - 8.2:.1f}" width="94" height="16.4" rx="8.2" fill="#FFFFFF" fill-opacity="0.96" stroke="{base}" stroke-width="1.2" filter="url(#b4ds)"/>'
            f'<text x="{LX - 38:.1f}" y="{y + 3.9:.1f}" font-family="monospace" font-size="11" font-weight="bold" fill="{base}" text-anchor="start">{code}</text>'
            f'<text x="{LX + 39:.1f}" y="{y + 3.9:.1f}" font-family="sans-serif" font-size="11" font-weight="bold" fill="{B.INK}" text-anchor="end">{metres}</text>')


def guides():
    """Thin dashed lines down the page that carry the ends of the runway and of the stopways to the bars: the two thresholds through both groups, the far end of each
    stopway only as far as the one bar that reaches it (the ASDA of the runway that has that stopway ahead)."""
    spans = ((END_N, ROWS["35"]["ASDA"] - 11.0, Y0 + 7.0), (THR17, GUIDE[0], GUIDE[1]), (THR35, GUIDE[0], GUIDE[1]), (END_S, Y0 - 28.0, ROWS["17"]["ASDA"] + 11.0))
    out = []
    for s, y0, y1 in spans:
        x = X(s)
        out.append(f'<line x1="{x:.2f}" y1="{y0}" x2="{x:.2f}" y2="{y1}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="2.0"/>'
                   f'<line x1="{x:.2f}" y1="{y0}" x2="{x:.2f}" y2="{y1}" stroke="#3B4558" stroke-width="0.75" stroke-dasharray="2.6 2.6"/>')
    return "".join(out)


def designators():
    """The two designators above the ends of the strip, upright and heavier than the ones of the small plans (figs/h_b4.py), which this figure leaves out."""
    return (H2.glyph_text("17", X(THR17) + 13.0, Y0 - 13.5, 8.0, "#FFFFFF", stroke=B.INK, stroke_width=1.0)
            + H2.glyph_text("35", X(THR35) - 13.0, Y0 - 13.5, 8.0, "#FFFFFF", stroke=B.INK, stroke_width=1.0))


def dimensions():
    """The lengths of the runway and of its stopways (AD 2.12), on a dimension line above the strip."""
    y = Y0 - 24.0
    xs = [X(s) for s in (END_N, THR17, THR35, END_S)]
    out = [f'<line x1="{xs[0]:.2f}" y1="{y}" x2="{xs[3]:.2f}" y2="{y}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.0" stroke-linecap="round"/>',
           f'<line x1="{xs[0]:.2f}" y1="{y}" x2="{xs[3]:.2f}" y2="{y}" stroke="{B.INK}" stroke-width="1.1"/>']
    for x in xs:
        out.append(f'<line x1="{x:.2f}" y1="{y - 3.6}" x2="{x:.2f}" y2="{y + 3.6}" stroke="{B.INK}" stroke-width="1.3"/>')
    out.append(B.label((xs[0] + xs[1]) / 2, y - 4.6, "300 m", 10.0))
    out.append(B.label(X(1150.0), y - 4.6, "4\u2009000 m", 10.0))
    out.append(B.label(xs[3] + 19.0, y - 4.6, "60 m", 10.0, "end"))
    return "".join(out)


def direction(rwy):
    """Beside each group of bars: the designator on a dark plate and a thin arrow the way aeroplanes take off and land on that runway (an aeroplane of the model rides on it: see sprites())."""
    if rwy == "35":
        tx, y, x0, x1 = 600.0, 34.0, 578.0, 452.0
    else:
        tx, y, x0, x1 = 40.0, 348.0, 62.0, 188.0
    d = 1.0 if x1 > x0 else -1.0
    return (f'<line x1="{x0}" y1="{y}" x2="{x1 - d * 6}" y2="{y}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.4" stroke-linecap="round"/>'
            f'<line x1="{x0}" y1="{y}" x2="{x1 - d * 6}" y2="{y}" stroke="{B.INK}" stroke-width="1.8" stroke-linecap="round"/>'
            + B.head(x1, y, d, 0.0, 9.0, 9.4, B.INK)
            + f'<rect x="{tx - 17}" y="{y - 11.5}" width="34" height="23" rx="4.5" fill="#262E3C" stroke="#FFFFFF" stroke-width="1.5" filter="url(#b4ds)"/>'
            + H2.glyph_text(rwy, tx, y, 11.0, "#F4F1E6"))


def markup():
    out = [f'<defs><clipPath id="ddc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9"/></clipPath>'
           f'<pattern id="dd-stripes" width="4.2" height="4.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2.0" height="4.2" fill="{B.YEL}"/></pattern></defs>',
           '<g clip-path="url(#ddc)">', B.ground_card(PX, PY, PW, PH, 0.2), B.aerodrome(P, runway_text=False), guides(), dimensions(), designators()]
    for rwy in ("35", "17"):
        for code in ("TORA", "TODA", "ASDA", "LDA"):
            out.append(bar(f"dd{rwy}{code}", rwy, code))
        for code in ("TORA", "TODA", "ASDA", "LDA"):
            out.append(pill(rwy, code))
        out.append(direction(rwy))
    out.append("</g>")
    return "".join(out)


def sprites():
    return [{"name": "sprite-top", "at": [520.0, 34.0], "width": 25.0, "angle": 270, **SPR},      # runway 35: towards the north, to the left
            {"name": "sprite-top", "at": [120.0, 348.0], "width": 25.0, "angle": 90, **SPR}]       # runway 17: towards the south, to the right


def callouts():
    c = S.callout
    out = [c(1, 512.0, Y0 + 28.0, 512.0, Y0 + 3.0),                                   # the runway
           c(2, 26.0, Y0 + 28.0, X(END_N) + 16.0, Y0 + 4.0),                          # the stopway beyond the north end
           c(3, 620.0, Y0 + 32.0, X(THR35) + 4.0, Y0 + 4.0),                          # the stopway beyond the south end
           c(4, LX + 66.0, ROWS["35"]["TORA"], r=9.5),
           c(5, LX + 66.0, ROWS["35"]["TODA"], r=9.5),
           c(6, 58.0, ROWS["35"]["TODA"], 58.0, ROWS["35"]["ASDA"] - 3.0),                      # the ASDA of runway 35, over the north stopway
           c(7, LX + 66.0, ROWS["35"]["LDA"], r=9.5),
           c(8, 620.0, ROWS["17"]["TODA"] - 2.0, X(END_S) - 2.5, ROWS["17"]["ASDA"] - 3.0)]          # the ASDA of runway 17, over the south stopway
    return "".join(out)


def layers():
    return [{"name": "terrain-18-02-thumamah", "at": [W / 2, HT / 2], "width": W}, B.defs(), markup(), *sprites(), B.frame(PX, PY, PW, PH),
            B.north_arrow(PX + 36, PY + 32), B.scale_bar(PX + PW - 30 - 1000 * K, PY + PH - 16, 1000 * K, "1 km"), callouts()]


def plate():
    return {
        "id": "fig-18-02-declared-distances",
        "replaces": "fig-18-02-declared-distances.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-18-02-declared-distances.jpg",
        "caption": "Figure 18-2. The declared distances of runway 17/35 at Thumamah",
        "desc": ("Figure 18-2. The declared distances of runway 17/35 at Thumamah. The aerodrome lies along the page to scale, north to the left; the upper bars are for runway 35 and the lower "
                 "bars for runway 17, each from where the distance starts to where it ends. The numbers are the AIP's (AD 2.12 and AD 2.13, AMDT 11/26); the ground plan is that of Figure 18-1 "
                 "(contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "Runway 17/35: 4 000 m between its thresholds.",
            "The stopway beyond the north end, 300 m: it lies ahead of a takeoff on runway 35.",
            "The stopway beyond the south end, 60 m: it lies ahead of a takeoff on runway 17.",
            "`TORA`, the takeoff run available: 4 000 m in either direction.",
            "`TODA`, the takeoff distance available: also 4 000 m, because Thumamah has no clearway.",
            "`ASDA`, the accelerate-stop distance available, for runway 35: the runway and the stopway ahead, 4 300 m.",
            "`LDA`, the landing distance available: 4 000 m in either direction; a stopway adds nothing to it.",
            "`ASDA` for runway 17: 4 060 m.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
