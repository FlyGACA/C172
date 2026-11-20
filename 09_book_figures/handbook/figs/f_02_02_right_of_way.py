"""Figure 2-2 (new). Right of way, from that section of Chapter 2 (GACAR 91.61): six scenes.

1 distress (an aircraft in distress, ringed in red, and two others turning away), 2 converging (the aircraft on the other's right has right of way; the other gives way and passes behind it), 3 head-on (both alter course to the right),
4 overtaking (the aircraft being overtaken has right of way; the overtaking one alters course to the right and passes well clear), 5 landing (of two approaching to land, the lower has right of way), 6 taxiing head-on (both stop or alter course to the right).
Seen from above except scene 5. A green tick marks the aircraft with right of way, an orange ribbon the path of the one that gives way. Shapes, colours and the numbers of the callouts; no words. The drawings are generic."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar0202"
INK, RED, GREEN = "#1E293B", "#B91C1C", "#15803D"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 200.0, 150.0), (220.0, 170.0, 200.0, 150.0), (430.0, 170.0, 200.0, 150.0))
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]


def panel(i, body, sky=None):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    bg = S.sky(uid + "k", x, y, w, h, sky) if sky else f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#CFE3F7"/><stop offset="1" stop-color="#EEF5FC"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid}g)"/>'
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + bg + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def tick(cx, cy):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="10" fill="#FFFFFF" stroke="{GREEN}" stroke-width="2.4"/><path d="M{n(cx - 4.6)} {n(cy)} l3.4 3.8 l6.4 -7.6" fill="none" stroke="{GREEN}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'


def path(uid, pts):
    return S.ribbon(uid, pts, 4.4, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)


def straight(x1, y1, x2, y2):
    return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="#FFFFFF" stroke-width="2.2" stroke-dasharray="5 5" stroke-opacity="0.95"/>'


def scenes():
    out = []
    x, y = CELLS[0][:2]                                        # distress
    out.append(panel(0, f'<circle cx="{n(x + 100)}" cy="{n(y + 78)}" r="30" fill="#FEE2E2" fill-opacity="0.6" stroke="{RED}" stroke-width="3" stroke-dasharray="6 4"/>'
                     + path(f"{U}a", [(x + 48, y + 104), (x + 56, y + 84), (x + 46, y + 56), (x + 30, y + 40)]) + path(f"{U}b", [(x + 156, y + 50), (x + 146, y + 72), (x + 158, y + 100), (x + 176, y + 116)]) + tick(x + 136, y + 60)))
    x, y = CELLS[1][:2]                                        # converging
    out.append(panel(1, straight(x + 150, y + 62, x + 30, y + 62) + path(f"{U}c", [(x + 70, y + 108), (x + 96, y + 100), (x + 160, y + 96), (x + 186, y + 72), (x + 188, y + 40)]) + tick(x + 160, y + 36)))
    x, y = CELLS[2][:2]                                        # head-on
    out.append(panel(2, path(f"{U}d", [(x + 64, y + 76), (x + 86, y + 92), (x + 112, y + 104), (x + 140, y + 108)]) + path(f"{U}e", [(x + 136, y + 70), (x + 114, y + 54), (x + 88, y + 42), (x + 60, y + 38)])))
    x, y = CELLS[3][:2]                                        # overtaking
    out.append(panel(3, straight(x + 158, y + 64, x + 192, y + 64) + path(f"{U}f", [(x + 56, y + 70), (x + 84, y + 98), (x + 140, y + 108), (x + 186, y + 98)]) + tick(x + 140, y + 38)))
    x, y = CELLS[4][:2]                                        # landing: the lower aircraft has right of way
    ground = f'<rect x="{n(x)}" y="{n(y + 122)}" width="200" height="28" fill="#E3D2A8"/><rect x="{n(x + 120)}" y="{n(y + 124)}" width="76" height="8" rx="1.5" fill="#5B6577"/>'
    out.append(panel(4, ground + straight(x + 14, y + 40, x + 128, y + 124) + tick(x + 126, y + 80), sky=DAY))
    x, y = CELLS[5][:2]                                        # taxiing head-on
    out.append(panel(5, f'<defs><linearGradient id="{U}sd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="200" height="150" fill="url(#{U}sd)"/>'
                     + f'<rect x="{n(x)}" y="{n(y + 50)}" width="200" height="54" fill="#8B93A5"/><line x1="{n(x)}" y1="{n(y + 77)}" x2="{n(x + 200)}" y2="{n(y + 77)}" stroke="#FACC15" stroke-width="2.2"/>'
                     + path(f"{U}g", [(x + 66, y + 80), (x + 84, y + 90), (x + 100, y + 94)]) + path(f"{U}h", [(x + 134, y + 74), (x + 116, y + 64), (x + 100, y + 60)])))
    return "".join(out)


def sprites():
    t = lambda x, y, w, a: {"name": "sprite-top", "at": [x, y], "width": w, "angle": a, "outline": OUT, "shadow": SHADOW}
    s = lambda x, y, w, a=0.0: {"name": "sprite-side", "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": a} if a else {})}
    c = lambda i: CELLS[i][:2]
    x0, y0 = c(0); x1, y1 = c(1); x2, y2 = c(2); x3, y3 = c(3); x4, y4 = c(4); x5, y5 = c(5)
    return [t(x0 + 100, y0 + 78, 36, 20.0), t(x0 + 48, y0 + 118, 30, 30.0), t(x0 + 156, y0 + 38, 30, 210.0),
            t(x1 + 70, y1 + 124, 34, 0.0), t(x1 + 160, y1 + 62, 34, 270.0),
            t(x2 + 46, y2 + 74, 34, 90.0), t(x2 + 154, y2 + 74, 34, 270.0),
            t(x3 + 40, y3 + 66, 32, 90.0), t(x3 + 140, y3 + 64, 32, 90.0),
            s(x4 + 52, y4 + 64, 44, 12.0), s(x4 + 102, y4 + 96, 44, 12.0),
            t(x5 + 48, y5 + 77, 32, 90.0), t(x5 + 152, y5 + 77, 32, 270.0)]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(6))


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', scenes(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-02-02-right-of-way",
        "replaces": "fig-02-02-right-of-way.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-02-right-of-way.jpg",
        "caption": "Figure 2-2. Right of way: distress, converging, head-on, overtaking, landing and taxiing",
        "desc": ("Figure 2-2. Right of way in six scenes: an aircraft in distress has right of way over all other traffic; converging, the aircraft on the other's right has right of way; head-on, both alter course to the right; "
                 "overtaking, the aircraft being overtaken has right of way and the overtaking one alters course to the right; of two aircraft approaching to land, the lower has right of way; taxiing head-on, both stop or alter course to the right."),
        "legend": [
            "Distress: an aircraft in distress has right of way over all other traffic.",
            "Converging, same category: the aircraft on the other's right has right of way. The aircraft that gives way must not pass over, under or ahead of the other unless well clear.",
            "Head-on: both alter course to the right.",
            "Overtaking: the aircraft being overtaken has right of way; the overtaking aircraft alters course to the right and passes well clear.",
            "Landing: of two aircraft approaching to land, the lower has right of way, but it must not cut in front of one already on final.",
            "Taxiing head-on: both stop or, where practicable, alter course to the right.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
