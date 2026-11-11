"""Figure 28-5 of the handbook: a standard-rate turn to the right from 360 to 090, as three of the model's instruments (attitude
indicator, turn coordinator, heading indicator) and the headings against the seconds of the turn."""
from figs.kit import arc_arrow, dial_layer

BLUE, ORANGE, INK = "#1D4ED8", "#C2570C", "#1F2A44"


def plate():
    D = 150
    centres = {"ai": (112, 112), "tc": (320, 112), "dg": (528, 112)}
    layers = [
        dial_layer("ai", "AI", centres["ai"], D, {"pitch": 3, "bank": 16}),
        dial_layer("tc", "TC", centres["tc"], D, {"turn": 1.0}),
        dial_layer("dg", "DG", centres["dg"], D, {"heading": 60}),
    ]
    layers[2]["render"]["anchors"]["bug"] = {"dial": "DG", "angle": 30, "radius": 1.0}
    layers[1]["render"]["anchors"]["wing"] = {"dial": "TC", "angle": 108, "radius": 0.62}
    layers[1]["render"]["anchors"]["ball"] = {"dial": "TC", "angle": 180, "radius": 0.6}

    # the timeline: seconds along the axis, headings above it
    x0, x1, y = 72, 568, 322
    per = (x1 - x0) / 30.0
    X = lambda t: x0 + per * t
    marks = [f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" opacity=".9"/>',
             f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>']
    for t in range(0, 31, 5):
        long = t % 10 == 0
        marks.append(f'<line x1="{X(t):.1f}" y1="{y - (9 if long else 5)}" x2="{X(t):.1f}" y2="{y + (9 if long else 5)}" stroke="{INK}" stroke-width="{3 if long else 2.2}" stroke-linecap="round"/>')
    marks.append(f'<rect x="{X(27.33):.1f}" y="{y - 11}" width="{X(30) - X(27.33):.1f}" height="22" rx="3" fill="#F2B27A" opacity=".85"/>')
    marks.append(f'<line x1="{X(27.33):.1f}" y1="{y - 11}" x2="{X(27.33):.1f}" y2="{y + 11}" stroke="{ORANGE}" stroke-width="2.4"/>')
    marks.append(f'<polygon points="{X(27.33):.1f},{y + 13} {X(27.33) - 7:.1f},{y + 27} {X(27.33) + 7:.1f},{y + 27}" fill="{ORANGE}" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round"/>')
    marks.append(f'<circle cx="{X(20):.1f}" cy="{y}" r="9.5" fill="{BLUE}" stroke="#FFFFFF" stroke-width="3"/>')
    # the heading bug (orange tab) on the rim of the heading indicator at 090, 30 degrees round from the top, and an arrow round the dial toward it
    cx, cy = centres["dg"]
    r = D / 2 * 0.86
    bug = (f'<g transform="translate({cx},{cy}) rotate(30)"><path d="M-6.5,{-r - 3} h13 v11 h-13 z" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round"/></g>')
    arc = arc_arrow(cx, cy, D / 2 + 17, -24, 22, BLUE)
    overlays = [{"type": "svg", "markup": "".join(marks) + bug + arc}]
    for t, s in ((0, "360"), (10, "030"), (20, "060"), (30, "090")):
        overlays.append({"type": "text", "pos": [X(t), y - 28], "s": s, "size": 15, "colour": INK})
    for t in (0, 10, 20, 30):
        overlays.append({"type": "text", "pos": [X(t), y + 40], "s": str(t), "size": 13, "colour": "#5B6475"})
    overlays.append({"type": "text", "pos": [X(27.33) - 13, y + 34], "s": "082", "size": 14, "colour": ORANGE, "anchor": "end"})
    overlays += [
        {"type": "marker", "n": 1, "at": "ai.rim_nw", "pos": [30, 28], "leader": True},
        {"type": "marker", "n": 2, "at": "tc.wing", "pos": [404, 30], "leader": True},
        {"type": "marker", "n": 3, "at": "tc.ball", "pos": [404, 196], "leader": True},
        {"type": "marker", "n": 4, "at": "dg.rim_nw", "pos": [440, 28], "leader": True},
        {"type": "marker", "n": 5, "at": "dg.bug", "pos": [612, 34], "leader": True},
        {"type": "marker", "n": 6, "pos": [30, y], "leader": False},
        {"type": "marker", "n": 7, "pos": [X(27.33), y + 76], "leader": True, "target": [X(27.33), y + 29]},
    ]
    return {
        "id": "fig-28-05-standard-rate-turn",
        "replaces": "fig-28-05-standard-rate-turn.svg",
        "book_file": "plate-28-05-standard-rate-turn.jpg",
        "caption": "Figure 28-5. A standard-rate turn to the right from 360 to 090",
        "desc": "The attitude indicator, turn coordinator and heading indicator of the training aeroplane in a right turn at standard rate, and below them the heading against the seconds of the turn with the point where the roll-out starts.",
        "legend": [
            "Attitude indicator: about 16° of right bank, nose slightly up.",
            "Turn coordinator: wing on the standard-rate mark.",
            "Ball centred: coordinated.",
            "Heading indicator passing 060, turning toward the bug.",
            "Heading bug on 090.",
            "Headings above, seconds below; the blue point is the moment shown.",
            "Roll-out begins at about 082.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "layers": layers,
        "overlays": overlays,
    }
