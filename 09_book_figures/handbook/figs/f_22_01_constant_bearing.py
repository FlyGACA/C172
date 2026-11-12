"""Figure 22-1. A collision course: constant bearing, no relative motion. At the left, an aerial view of the desert (figs/terrain.py) with the two tracks and the aeroplanes of the model at
the three moments (the earlier two ghosted, the third solid), the lines of sight as soft cones with dotted centres, the angle to the nose at each moment as an orange sector, the collision
point; at the right, the same three moments through the windscreen (sky, hills, plain, the dark hump of the glareshield, a rubber-edged frame with the sheen of glass): the other aircraft
stays at one spot on the horizon and only grows, and the traffic that is not on a collision course moves across. The seven numbered callouts of the old figure are kept, in the same order
and meaning (figs/scene.py makes the callouts and the ribbons)."""
import math

from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 360
terrain.ensure("terrain-22-01", size=(W * 4, HT * 4), seed=221, kind="plain", features=("wadis", "tracks"), veil=0.30, soft=2.8)

U = "a221"
BLUE, INK = "#1D4ED8", "#1F2937"
n = S.n
FRAMES = [24, 132, 240]            # the tops of the three windscreens
FX, FW, FH = 356, 268, 82
SHADOW = {"dx": 1.4, "dy": 2.2, "blur": 1.6, "opacity": 0.30}


def defs():
    return ("<defs>" + H.blur_filter(U + "bl", 2.2) + H.blur_filter(U + "b1", 1.0) + H.shadow_filter(U + "cs", 0, 2.4, 3.2, 0.30, "#10233F") + S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E4EDF7")])
            + S.gradient(U + "gs", [(0, "#EAF4FD"), (0.7, "#F6F2E2"), (1, "#F8E9C8")]) + S.gradient(U + "pl", [(0, "#E8D6A8"), (1, "#C9AE7C")])
            + S.gradient(U + "hp", [(0, "#3A4458"), (1, "#0F131B")]) + '<clipPath id="' + U + 'lc"><rect x="6" y="10" width="320" height="340" rx="10"/></clipPath>' + "</defs>")


def left_card():
    return [f'<rect x="6" y="10" width="320" height="340" rx="10" fill="#FFFFFF" filter="url(#{U}cs)"/>', f'<g clip-path="url(#{U}lc)">',
            {"name": "terrain-22-01", "at": [W / 2, HT / 2], "width": W}, S.scrub(81, 8, 70, 20, 60, 2, scale=0.85) + S.scrub(82, 150, 320, 250, 346, 4, scale=0.85) + S.scrub(83, 200, 322, 20, 56, 2, scale=0.85), "</g>",
            f'<rect x="6" y="10" width="320" height="340" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>']


def cones():
    """The lines of sight: a soft narrow cone from each of our positions to the other aircraft, with a dotted centre."""
    out = []
    for (x0, y0, x1, y1) in ((95, 276, 305, 66), (95, 206, 235, 66), (95, 136, 165, 66)):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln, dx / ln
        w = 6.5
        poly = [(x0, y0), (x1 + nx * w, y1 + ny * w), (x1 - nx * w, y1 - ny * w)]
        out.append(f'<polygon points="{S.pts(poly)}" fill="#2F66E8" fill-opacity="0.20" filter="url(#{U}b1)"/>')
        out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="4.2" stroke-linecap="round"/><line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="3 4" stroke-linecap="round"/>')
    return "".join(out)


def tracks():
    return (f'<line x1="95" y1="338" x2="95" y2="66" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4.2"/><line x1="95" y1="338" x2="95" y2="66" stroke="#6B7280" stroke-width="1.7" stroke-dasharray="6 5"/>'
            f'<line x1="322" y1="66" x2="95" y2="66" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4.2"/><line x1="322" y1="66" x2="95" y2="66" stroke="#6B7280" stroke-width="1.7" stroke-dasharray="6 5"/>')


def bearings():
    """The angle between the nose and the other aircraft at each of our positions: the heading (a thin orange line), the sector to the line of sight and its arc."""
    out = []
    for y in (276, 206, 136):
        arc_end = (95 + 24 * math.sin(math.radians(45)), y - 24 * math.cos(math.radians(45)))
        out.append(f'<path d="M 95,{y} L 95,{y - 24} A 24,24 0 0 1 {n(arc_end[0])},{n(arc_end[1])} Z" fill="#F59A2B" fill-opacity="0.34"/>')
        out.append(f'<path d="M 95,{y - 24} A 24,24 0 0 1 {n(arc_end[0])},{n(arc_end[1])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.6"/><path d="M 95,{y - 24} A 24,24 0 0 1 {n(arc_end[0])},{n(arc_end[1])}" fill="none" stroke="#B45309" stroke-width="2.2"/>')
        out.append(f'<line x1="95" y1="{y}" x2="95" y2="{y - 31}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.4"/><line x1="95" y1="{y}" x2="95" y2="{y - 31}" stroke="#B45309" stroke-width="1.3"/>')
    return "".join(out)


def aeroplanes_plan():
    ours = {"tint": "#2F66D6", "tint_strength": 0.64, "shadow": SHADOW}
    other = {"tint": "#2A3446", "tint_strength": 0.78, "shadow": SHADOW}
    out = []
    for y, op in ((276, 0.62), (206, 0.62), (136, 1.0)):
        out.append({"name": "sprite-top", "at": [95, y], "width": 40, "angle": 0, "opacity": op, **ours})
    for x, op in ((305, 0.62), (235, 0.62), (165, 1.0)):
        out.append({"name": "sprite-top", "at": [x, 66], "width": 40, "angle": 270, "opacity": op, **other})
    return out


def plan_marks():
    out = []
    # the collision point
    out.append(f'<circle cx="95" cy="66" r="9" fill="#FFFFFF" fill-opacity="0.35" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.9"/><circle cx="95" cy="66" r="9" fill="none" stroke="#B91C1C" stroke-width="2.4"/>'
               f'<g stroke-linecap="round"><line x1="90" y1="61" x2="100" y2="71" stroke="#FFFFFF" stroke-width="5"/><line x1="90" y1="71" x2="100" y2="61" stroke="#FFFFFF" stroke-width="5"/>'
               f'<line x1="90" y1="61" x2="100" y2="71" stroke="#B91C1C" stroke-width="2.4"/><line x1="90" y1="71" x2="100" y2="61" stroke="#B91C1C" stroke-width="2.4"/></g>')
    # where each of the two will be: rings at the earlier positions
    for (x, y, c) in ((95, 276, BLUE), (95, 206, BLUE), (305, 66, INK), (235, 66, INK)):
        out.append(f'<circle cx="{x}" cy="{y}" r="4.6" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.9"/><circle cx="{x}" cy="{y}" r="4.6" fill="#FFFFFF" stroke="{c}" stroke-width="2"/>')
    # which way each is going
    out.append(S.ribbon(U + "oa", [(95, 117), (95, 108), (95, 94)], 5.6, "#1D4ED8", "#6FA0FF", head=2.0, tail=0.8))
    out.append(S.ribbon(U + "ob", [(146, 66), (136, 66), (123, 66)], 5.6, "#1F2937", "#566178", head=2.0, tail=0.8))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the windscreens
def frame(i, y0, size, crossing_x):
    """One windscreen: the sky, far hills, the plain, the other aircraft on the horizon (its width `size`), the crossing traffic (grey), the hump of the glareshield, the frame."""
    uid = f"{U}f{i}"
    hz = y0 + 45.1
    rr = f'<rect x="{FX}" y="{y0}" width="{FW}" height="{FH}" rx="10"/>'
    out = [f'<defs><clipPath id="{uid}c">{rr}</clipPath></defs><g clip-path="url(#{uid}c)">',
           f'<rect x="{FX}" y="{y0}" width="{FW}" height="{hz - y0 + 1}" fill="url(#{U}gs)"/>',
           S.land_layer(uid + "h", S.ridge(i * 7 + 3, FX, FX + FW, hz + 1, 8, step=3.0, peaks=0.45), hz + 3, ("#A7B6D3", "#C9D5E8"), rim=False, haze=0.35, haze_colour="#F4EDDC"),
           f'<rect x="{FX}" y="{hz}" width="{FW}" height="{y0 + FH - hz}" fill="url(#{U}pl)"/>',
           f'<line x1="{FX}" y1="{n(hz)}" x2="{FX + FW}" y2="{n(hz)}" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="0.9"/>',
           S.scrub(90 + i, FX + 4, FX + FW - 4, hz + 3, y0 + FH - 6, 7, scale=0.55), "</g>"]
    return out, hz


def frame_front(i, y0):
    uid = f"{U}f{i}"
    hump = f"M 444,{y0 + FH} Q 490,{y0 + FH - 26} 536,{y0 + FH} Z"
    return (f'<defs><clipPath id="{uid}c2"><rect x="{FX}" y="{y0}" width="{FW}" height="{FH}" rx="10"/></clipPath></defs><g clip-path="url(#{uid}c2)">'
            f'<path d="{hump}" fill="url(#{U}hp)"/><path d="M 452,{y0 + FH - 2} Q 490,{y0 + FH - 24} 528,{y0 + FH - 2}" fill="none" stroke="#9DB0D0" stroke-opacity="0.4" stroke-width="0.9"/>'
            f'<polygon points="{S.pts([(FX + 20, y0), (FX + 70, y0), (FX + 24, y0 + FH), (FX - 26, y0 + FH)])}" fill="#FFFFFF" fill-opacity="0.10"/>'
            f'<polygon points="{S.pts([(FX + 96, y0), (FX + 104, y0), (FX + 58, y0 + FH), (FX + 50, y0 + FH)])}" fill="#FFFFFF" fill-opacity="0.07"/></g>'
            f'<rect x="{FX}" y="{y0}" width="{FW}" height="{FH}" rx="10" fill="none" stroke="#0F131B" stroke-width="5.6"/><rect x="{FX + 2.4}" y="{y0 + 2.4}" width="{FW - 4.8}" height="{FH - 4.8}" rx="8" fill="none" stroke="#5B667E" stroke-opacity="0.55" stroke-width="0.8"/>')


def windscreens():
    layers_ = []
    for i, y0 in enumerate(FRAMES):
        parts, hz = frame(i, y0, 0, 0)
        layers_ += parts
        size = (14, 21, 42)[i]
        # the other aircraft: dead ahead on the horizon, at one spot, bigger each time
        layers_.append({"name": "sprite-front", "at": [590.5, hz - size * 0.21 + 0.6], "width": size, "tint": "#1C2535", "tint_strength": 0.86, "outline": {"width": 0.35, "colour": "#0B1220", "opacity": 0.6}})
        # the crossing traffic: a little above the horizon, moving to the left
        cx = (445.3, 418.5, 387.3)[i]
        layers_.append({"name": "sprite-side-left", "at": [cx, hz - 9.5], "width": 13, "tint": "#6B7280", "tint_strength": 0.55, "opacity": 0.95})
        if i == 2:
            for gx in (445.3, 418.5):
                layers_.append(f'<circle cx="{gx}" cy="{n(hz - 9.5)}" r="2.6" fill="none" stroke="#6B7280" stroke-opacity="0.75" stroke-width="0.9" stroke-dasharray="1.2 1.2"/>')
            layers_.append(S.ribbon(U + "mv", [(441, hz - 17), (418, hz - 17), (395, hz - 17)], 3.4, "#6B7280", "#A8B0BF", head=2.0, tail=0.6))
        layers_.append(frame_front(i, y0))
    return layers_


def callouts():
    c = S.callout
    return "".join([c(1, 220, 191, 202, 173), c(2, 185, 156, 167, 138), c(3, 150, 121, 132, 103), c(4, 130, 34, 105, 60), c(5, 52, 262, 100, 254),
                    c(1, 354, 26, r=10), c(2, 354, 134, r=10), c(3, 354, 242, r=10), c(6, 612, 336, 598, 280), c(7, 372, 336, 386, 276)])


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>']
    out.insert(0, defs())
    out += left_card()
    out += [cones(), tracks(), bearings(), plan_marks()]
    out += aeroplanes_plan()
    out += windscreens()
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-22-01-constant-bearing",
        "replaces": "fig-22-01-constant-bearing.svg",
        "book_file": "plate-22-01-constant-bearing.jpg",
        "caption": "Figure 22-1. A collision course: constant bearing, no relative motion",
        "desc": "Figure 22-1. A collision course: constant bearing, no relative motion",
        "legend": [
            "First moment.",
            "Second moment, 20 seconds later.",
            "Third moment, 20 seconds before impact. The same moments appear in the plan view (left) and through your windscreen (right).",
            "Collision point.",
            "The angle between your nose and the other aircraft stays the same: a constant bearing.",
            "In the windscreen the other aircraft stays at one spot and only grows.",
            "Traffic that moves across the windscreen is not on a collision course while it keeps moving; keep it in sight.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-22-01-constant-bearing.svg", "blank": True, "layers": layers()},
    }
