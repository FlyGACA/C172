"""The two figures about unusual attitudes (28-6 and 28-7): what the instruments show, and the recovery in four pictures of the attitude
indicator. Not a figure itself: f_28_06_nose_high.py and f_28_07_nose_low.py give it their numbers."""
from figs.kit import arc_arrow, dial_layer, power_bar

ORANGE, INK = "#C2570C", "#1F2A44"


def upset_plate(fid, book_file, caption, desc, legend, *, top, trends, sequence, bars):
    """top: readings of the instruments {"AI": pose, "ASI": kt, "ALT": ft, "VSI": fpm, "turn": x}; trends: arrows on the dials, [(instrument, from deg, to deg)];
    sequence: poses of the attitude indicator in the four pictures of the recovery; bars: [(picture index, fraction of power)]."""
    D, DAI, DS = 92, 150, 96
    top_row = {"ai": (218, 108, DAI), "asi": (76, 108, DS), "alt": (360, 108, DS), "vsi": (474, 108, DS), "tc": (580, 108, DS)}
    layers = [
        dial_layer("ai", "AI", top_row["ai"][:2], DAI, top["AI"]),
        dial_layer("asi", "ASI", top_row["asi"][:2], DS, {"ASI": top["ASI"]}),
        dial_layer("alt", "ALT", top_row["alt"][:2], DS, {"ALT": top["ALT"]}),
        dial_layer("vsi", "VSI", top_row["vsi"][:2], DS, {"VSI": top["VSI"]}),
        dial_layer("tc", "TC", top_row["tc"][:2], DS, {"turn": top["turn"]}),
    ]
    # the four pictures in a row: each attitude indicator, its power bar if it has one, and room for an arrow to the next
    has_bar = {i for i, _ in bars}
    gap, bar_room = 54, 24
    total = 4 * D + 3 * gap + len(has_bar) * bar_room
    x, xs, ends = (640 - total) / 2, [], []
    for i in range(4):
        xs.append(x + D / 2)
        x += D + (bar_room if i in has_bar else 0)
        ends.append(x)
        x += gap
    for i, (cx, pose) in enumerate(zip(xs, sequence)):
        layers.append(dial_layer(f"s{i + 1}", "AI", (cx, 304), D, pose))
    markup = ['<line x1="24" y1="204" x2="616" y2="204" stroke="#DCE1EA" stroke-width="2"/>']
    for name, a0, a1 in trends:
        cx, cy, d = top_row[name]
        markup.append(arc_arrow(cx, cy, d / 2 + 9, a0, a1, ORANGE))
    for i, fraction in bars:
        markup.append(power_bar(xs[i] + D / 2 + 8, 304 - 31, 16, 62, fraction))
    overlays = [{"type": "svg", "markup": "".join(markup)}]
    for i in range(3):                                       # the arrows between the four pictures
        overlays.append({"type": "arrow", "from": [ends[i] + 6, 304], "to": [xs[i + 1] - D / 2 - 7, 304], "colour": INK, "width": 3.4, "head": 11})
    for n, name in zip((1, 2, 3, 4, 5), ("ai", "asi", "alt", "vsi", "tc")):
        cx, cy, d = top_row[name]
        off = 0.707 * (d / 2 + 17)
        overlays.append({"type": "marker", "n": n, "pos": [cx - off, cy - off], "leader": False})
    for n, i in zip((6, 7, 8), range(3)):
        overlays.append({"type": "marker", "n": n, "pos": [(ends[i] + 6 + xs[i + 1] - D / 2 - 7) / 2, 258], "leader": False})
    overlays.append({"type": "marker", "n": 9, "at": "s4.rim_s", "pos": [xs[3] + 6, 378], "leader": True})
    return {
        "id": fid, "replaces": fid + ".svg", "book_file": book_file, "caption": caption, "desc": desc, "legend": legend,
        "canvas": [640, 400], "background": "pale", "layers": layers, "overlays": overlays,
    }
