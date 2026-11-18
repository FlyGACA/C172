"""Figure 13-2 (new). The chapter's trip from aerodrome A to aerodrome B and back, drawn to one scale: each runway against the distance needed, with the AFM corrections and the 1.5 margin.

A (2 000 ft, 30 °C, runway 1 200 m, 1% upslope, 10 kt headwind): 675 m from the table, 709 m with the slope, 638 m into the wind, with the margin 957 m (inside, 243 m to spare).
B (4 000 ft, 35 °C, runway 1 100 m): landing 533 m, with the margin 800 m (inside). Return takeoff at 40 °C: 960 m, with the margin 1 440 m (longer than the runway); at 10 °C, 680 m, with the margin 1 020 m (fits).
All numbers are the chapter's own; the bars are to one scale in metres."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 410
U = "ar1302"
INK, BLUE, GREEN, AMBER, RED, SLATE = "#1E293B", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#475569"
X0, PXM = 56.0, 0.32                                        # metres to pixels


RWYS = []
SPRITE_LOOK = {"outline": {"width": 0.4, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.0, "dy": 1.8, "blur": 1.4, "opacity": 0.35}}


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.0, anchor="middle"):
    w = gwidth(text, size) + 12.0
    h = size + 7.0
    if anchor == "start":
        cx = cx + w / 2
    elif anchor == "end":
        cx = cx - w / 2
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.3"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def card(uid, x, y, w, h):
    return (f'<defs><filter id="{uid}" x="-5%" y="-8%" width="110%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.24"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#FFFFFF" filter="url(#{uid})"/><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#E2E8F0" stroke-width="1.4"/>')


def runway(y, m, label, span=100):
    """A runway seen from above, to the scale of the bars: asphalt, edge lines, threshold stripes at both ends and a dashed centre line; the aeroplane
    of the model stands lined up on the threshold (a sprite, see layers)."""
    w = m * PXM
    h = 22.0
    RWYS.append((X0, y, w, h))
    out = (f'<defs><linearGradient id="{U}rw{len(RWYS)}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#596273"/><stop offset="1" stop-color="#454D5B"/></linearGradient></defs>'
           f'<rect x="{n(X0)}" y="{n(y - 1)}" width="{n(w)}" height="{n(h)}" rx="1.5" fill="url(#{U}rw{len(RWYS)})"/>'
           f'<line x1="{n(X0)}" y1="{n(y + 1.2)}" x2="{n(X0 + w)}" y2="{n(y + 1.2)}" stroke="#E5E7EB" stroke-width="0.9"/><line x1="{n(X0)}" y1="{n(y + h - 3.2)}" x2="{n(X0 + w)}" y2="{n(y + h - 3.2)}" stroke="#E5E7EB" stroke-width="0.9"/>')
    for x in (X0 + 2.5, X0 + w - 9.5):                       # threshold stripes
        out += "".join(f'<rect x="{n(x)}" y="{n(y + 3 + k * 2.6)}" width="7" height="1.5" fill="#F8FAFC"/>' for k in range(6))
    out += f'<line x1="{n(X0 + 16)}" y1="{n(y + h / 2 - 1)}" x2="{n(X0 + w - 16)}" y2="{n(y + h / 2 - 1)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="7 6"/>'
    out += f'<line x1="{n(X0 + w)}" y1="{n(y - 6)}" x2="{n(X0 + w)}" y2="{n(y + span)}" stroke="#5B6577" stroke-width="1.6" stroke-dasharray="4 4"/>' + pill(X0 + w + 6, y + 10, label, SLATE, anchor="start")
    return out


def bar(y, m, col, label, outline=False, mark=None):
    w = m * PXM
    body = (f'<rect x="{n(X0)}" y="{n(y)}" width="{n(w)}" height="13" rx="3" fill="#FFFFFF" stroke="{col}" stroke-width="2.4" stroke-dasharray="5 3"/>' if outline
            else f'<rect x="{n(X0)}" y="{n(y)}" width="{n(w)}" height="13" rx="3" fill="{col}"/>')
    out = body + pill(X0 + w + 6, y + 6.5, label, col, anchor="start")
    if mark == "ok":
        out += f'<circle cx="{n(X0 + w + gwidth(label, 8.0) + 34)}" cy="{n(y + 6.5)}" r="8" fill="#FFFFFF" stroke="{GREEN}" stroke-width="2"/><path d="M{n(X0 + w + gwidth(label, 8.0) + 30)} {n(y + 6.5)} l3 3.4 l5.6 -6.6" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    if mark == "no":
        cx = X0 + w + gwidth(label, 8.0) + 34
        out += f'<circle cx="{n(cx)}" cy="{n(y + 6.5)}" r="8" fill="#FFFFFF" stroke="{RED}" stroke-width="2"/><path d="M{n(cx - 3.6)} {n(y + 2.9)} l7.2 7.2 M{n(cx + 3.6)} {n(y + 2.9)} l-7.2 7.2" stroke="{RED}" stroke-width="2.4" stroke-linecap="round"/>'
    return out


def leg_a():
    y = 10.0
    out = card(f"{U}c1", 10, y, 620, 132) + pill(620, y + 16, "A  2 000 FT  30 °C", INK, anchor="end")
    out += runway(y + 26, 1200, "1 200 M", span=96)
    out += bar(y + 54, 675, AMBER, "675 M") + bar(y + 72, 709, AMBER, "709 M") + bar(y + 90, 638, BLUE, "638 M") + bar(y + 110, 957, GREEN, "957 M", outline=True, mark="ok")
    return out


def leg_b():
    y = 152.0
    out = card(f"{U}c2", 10, y, 620, 94) + pill(620, y + 16, "B  4 000 FT  35 °C", INK, anchor="end")
    out += runway(y + 26, 1100, "1 100 M", span=60)
    out += bar(y + 52, 533, AMBER, "533 M") + bar(y + 72, 800, GREEN, "800 M", outline=True, mark="ok")
    return out


def leg_back():
    y = 256.0
    out = card(f"{U}c3", 10, y, 620, 144) + pill(620, y + 16, "B  40 °C", RED, anchor="end")
    out += runway(y + 26, 1100, "1 100 M", span=110)
    out += bar(y + 52, 960, AMBER, "960 M") + bar(y + 72, 1440, RED, "1 440 M", outline=True, mark="no")
    out += pill(X0, y + 98, "10 °C", BLUE, anchor="start")
    out += bar(y + 108, 680, AMBER, "680 M") + bar(y + 126, 1020, GREEN, "1 020 M", outline=True, mark="ok")
    return out


def callouts():
    c = S.callout
    return "".join((c(1, 27, 27, r=10.5), c(2, 27, 169, r=10.5), c(3, 27, 273, r=10.5), c(4, 27, 370, r=10.5)))


def layers():
    RWYS.clear()
    out = [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', leg_a(), leg_b(), leg_back(), callouts()]
    planes = [{"name": "sprite-top", "at": [x + 24, y + h / 2 - 1], "width": 19, "angle": 90.0, **SPRITE_LOOK} for x, y, w, h in RWYS]
    return out[:-1] + planes + out[-1:]


def plate():
    return {
        "id": "fig-13-02-trip-distances",
        "replaces": "fig-13-02-trip-distances.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-13-02-trip-distances.jpg",
        "caption": "Figure 13-2. From A to B and back, to scale: each runway against the distance needed, with the corrections and the margin",
        "desc": ("Figure 13-2. The chapter's two examples drawn to one scale. Departure from A, 2 000 ft and 30 °C, runway 1 200 m: 675 m from the table, 709 m with the 1% upslope, 638 m into the 10 kt headwind, with the margin 957 m, inside with 243 m to spare. "
                 "Landing at B, 4 000 ft and 35 °C, runway 1 100 m: 533 m, with the margin 800 m, inside. The return takeoff at 40 °C: 960 m, with the margin 1 440 m, more than the runway; at 10 °C, 680 m, with the margin 1 020 m, which fits."),
        "legend": [
            "Departure from aerodrome A, 2 000 ft and 30 °C: 675 m from the table; 675 × 1.05 = 709 m with the 1% upslope; 638 m into the 10 kt headwind; with the margin, 638 × 1.5 = 957 m, inside the 1 200 m runway with 243 m to spare.",
            "Landing at aerodrome B, 4 000 ft and 35 °C: 533 m; with the margin, 533 × 1.5 = 800 m, inside the 1 100 m runway.",
            "The return takeoff, planned for 40 °C in the afternoon: 960 m; with the margin, 960 × 1.5 = 1 440 m, more than the runway. Even without the margin only 140 m would remain.",
            "Plan the return for a much cooler hour: at 10 °C, 680 × 1.5 = 1 020 m fits.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
