"""Figure 11-4 (new). The two worked examples of Chapter 11 drawn to scale: the runway, the takeoff distance from the table, its corrections and the 1.5 margin, and the rate of climb.

Example 1 (1 700 ft, 36 °C, runway 1 200 m): 726 m, with the margin 1 089 m (inside, 111 m to spare); with a 4 kt tailwind 871 m and with the margin 1 307 m (longer than the runway). Example 2 (5 850 ft, 28 °C, runway 1 600 m, 1% upslope, 10 kt headwind):
1 062 m from the table, 1 115 m with the slope, 1 004 m into the wind, with the margin 1 506 m (inside); without the headwind 1 115 × 1.5 = 1 673 m (not inside). Rate of climb: 469 and 272 ft/min, against 720 ft/min on a standard day at sea level.
All numbers are the chapter's own; the bars are to one scale in metres (and in ft/min on the right)."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 352
U = "ar1104"
INK, BLUE, GREEN, AMBER, RED, SLATE = "#1E293B", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#475569"
X0, PXM = 56.0, 0.185                                       # metres to pixels
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


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


def runway(y, m, label):
    w = m * PXM
    return (f'<rect x="{n(X0)}" y="{n(y)}" width="{n(w)}" height="20" rx="2" fill="#5B6577"/><line x1="{n(X0 + 6)}" y1="{n(y + 10)}" x2="{n(X0 + w - 6)}" y2="{n(y + 10)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="8 6"/>'
            f'<line x1="{n(X0 + w)}" y1="{n(y - 6)}" x2="{n(X0 + w)}" y2="{n(y + 118)}" stroke="#5B6577" stroke-width="1.6" stroke-dasharray="4 4"/>' + pill(X0 + w + 6, y + 10, label, SLATE, anchor="start"))


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


def example1():
    y = 18.0
    out = card(f"{U}c1", 10, 10, 470, 158) + pill(470, 26, "1 700 FT  36 °C", INK, anchor="end")
    out += runway(y + 30, 1200, "1 200 M")
    out += bar(y + 62, 726, AMBER, "726 M") + bar(y + 82, 1089, GREEN, "1 089 M", outline=True, mark="ok")
    out += bar(y + 114, 1307, RED, "1 307 M", outline=True, mark="no") + pill(X0, y + 136, "4 KT", RED, anchor="start")
    return out


def example2():
    y = 186.0
    out = card(f"{U}c2", 10, 178, 470, 164) + pill(470, 194, "5 850 FT  28 °C", INK, anchor="end")
    out += runway(y + 26, 1600, "1 600 M")
    out += bar(y + 54, 1062, AMBER, "1 062 M") + bar(y + 72, 1115, AMBER, "1 115 M") + bar(y + 90, 1004, BLUE, "1 004 M")
    out += bar(y + 110, 1506, GREEN, "1 506 M", outline=True, mark="ok") + bar(y + 132, 1673, RED, "1 673 M", outline=True, mark="no")
    return out


def climb():
    out = card(f"{U}c3", 490, 10, 140, 332)
    base, k = 318.0, 0.36                                    # ft/min to pixels
    for i, (v, col) in enumerate(((720, SLATE), (469, AMBER), (272, RED))):
        x = 506 + i * 40
        out += f'<rect x="{n(x)}" y="{n(base - v * k)}" width="26" height="{n(v * k)}" rx="3" fill="{col}"/>' + pill(x + 13, base - v * k - 12, str(v), col, size=7.5)
    out += f'<line x1="498" y1="{n(base)}" x2="622" y2="{n(base)}" stroke="#94A3B8" stroke-width="1.6"/>' + H.glyph_text("FT/MIN", 560, base + 12, 7.5, INK, spacing=0.4)
    return out


def callouts():
    c = S.callout
    return "".join((c(1, 27, 27, r=10.5), c(2, 27, 138, r=10.5), c(3, 27, 195, r=10.5), c(4, 27, 324, r=10.5), c(5, 507, 27, r=10.5)))


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', example1(), example2(), climb(), callouts()]


def plate():
    return {
        "id": "fig-11-04-worked-examples",
        "replaces": "fig-11-04-worked-examples.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-11-04-worked-examples.jpg",
        "caption": "Figure 11-4. The two worked examples to scale: the runway, the takeoff distance with its corrections and margin, and the rate of climb",
        "desc": ("Figure 11-4. The chapter's two worked examples drawn to one scale. Example 1, 1 700 ft and 36 °C, runway 1 200 m: 726 m, with the margin 1 089 m, inside; with a 4 kt tailwind, 1 307 m, longer than the runway. "
                 "Example 2, 5 850 ft and 28 °C, runway 1 600 m: 1 062 m, 1 115 m with the upslope, 1 004 m into the 10 kt headwind, with the margin 1 506 m, inside; without the headwind 1 673 m, not inside. "
                 "Rate of climb: 469 and 272 ft/min, against 720 ft/min on a standard day at sea level."),
        "legend": [
            "Example 1, 1 700 ft and 36 °C: the takeoff distance is 726 m; with the margin, 726 × 1.5 = 1 089 m, inside the 1 200 m runway with 111 m to spare.",
            "With a 4 kt tailwind: 726 × 1.20 = 871 m; with the margin, 1 307 m, longer than the runway. Take off in the other direction, into wind, or wait.",
            "Example 2, 5 850 ft and 28 °C: 1 062 m from the table, 1 115 m with the 1% upslope, 1 004 m into the 10 kt headwind; with the margin, 1 506 m, inside the 1 600 m runway.",
            "Without the headwind, 1 115 × 1.5 = 1 673 m, which is not inside the runway.",
            "Rate of climb: 469 ft/min in Example 1 and 272 ft/min in Example 2, against 720 ft/min on a standard day at sea level.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
