"""Figure 2-4 (new; redrawn in the second design pass as two views). VFR weather minimums, from that section of Chapter 2 (GACAR 91.165).

Two renders (figs/oeth3d.py; blender/render_oeth.py), the ground the open picture of the desert east of Thumamah on its relief:
- above (vfr-2-04-cloud): a cumulus of the cloud library, its base about 5 000 ft above the ground, inside a glass box of the distances to keep from it in
  Classes C and D and in Class E below 10 000 ft MSL (500 ft below, 1 000 ft above, 2 000 ft all round); the aeroplane (enlarged) flies past outside it.
  Callout 1 is the box, with the distances drawn on it and the flight visibility (5 km); callout 2 is a small drawing of the same box at or above
  10 000 ft MSL in Class E (1 000 ft below and above, 1 500 m all round, 8 km). The sky is drawn (the render leaves it clear).
- below (vfr-2-04-ceiling): a generic aerodrome (a graded runway with its markings, an apron, a tower; not any real one) under a layer of stratus whose
  base is below 1 000 ft above the ground (callout 4, with the ground visibility of 5 km to take off, land or enter the circuit), and the aeroplane low
  and clear of the cloud away from it (callout 3: Classes G and F at 1 200 ft or less above the surface, by day, 3 km).
The text is the distances, from the chapter. The boxes are to scale with the cloud; the aeroplanes are enlarged."""
import json
import os

from figs import h_b2 as H
from figs import scene as S

n = S.n
W = 640
U = "ar0204"
INK, BLUE, RED, AMBER, GREEN = "#1E293B", "#1D4ED8", "#B91C1C", "#B45309", "#15803D"
PX, PW = 8.0, 624.0
TOP, BOT = "vfr-2-04-cloud", "vfr-2-04-ceiling"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def info(rid, py):
    with open(os.path.join(HERE, "renders", rid + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ph = PW * h / w
    return (lambda k: (PX + d["anchors"][k][0] * PW, py + d["anchors"][k][1] * ph)), ph


PH = PW * 1000 / 2400
PY1, PY2 = 8.0, 8.0 + PH + 10.0
HT = int(PY2 + PH + 8.0)


def pill(cx, cy, text, fill=INK, size=8.5):
    g = H._GLYPHS
    w = sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * size / g["cap_height"]) + 0.4 for c in text) + 12.0
    h = size + 7.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def dim(x1, y1, x2, y2, col="#FFFFFF"):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    def head(x, y, s):
        hx, hy = x - s * 7 * math.cos(a), y - s * 7 * math.sin(a)
        px, py = -math.sin(a) * 4.5, math.cos(a) * 4.5
        return f'<path d="M{n(x)} {n(y)} L{n(hx + px)} {n(hy + py)} L{n(hx - px)} {n(hy - py)} Z" fill="{col}"/>'
    return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{col}" stroke-width="2.2"/>' + head(x2, y2, 1) + head(x1, y1, -1)




def inset(x, y):
    """Class E at or above 10 000 ft MSL: the same box, drawn small, with its distances."""
    w, h = 150.0, 86.0
    cx, cy = x + w / 2, y + h / 2 + 4
    bx, by, bw, bh = cx - 58, cy - 22, 92, 44
    cloud = (f'<ellipse cx="{n(cx - 8)}" cy="{n(cy + 2)}" rx="16" ry="9" fill="#FFFFFF"/><ellipse cx="{n(cx + 6)}" cy="{n(cy - 3)}" rx="14" ry="11" fill="#FFFFFF"/>'
             f'<ellipse cx="{n(cx + 16)}" cy="{n(cy + 4)}" rx="11" ry="7" fill="#FFFFFF"/>')
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h + 24)}" rx="10" fill="#0F172A" fill-opacity="0.55" stroke="#FFFFFF" stroke-width="1.4"/>'
            f'<rect x="{n(bx)}" y="{n(by)}" width="{n(bw)}" height="{n(bh)}" rx="3" fill="#2563EB" fill-opacity="0.22" stroke="#93C5FD" stroke-width="1.6"/>' + cloud
            + pill(cx, by - 9, "1 000 FT", BLUE, 7.0) + pill(cx, by + bh + 9, "1 000 FT", BLUE, 7.0) + pill(bx + bw + 6, cy, "1 500 M", BLUE, 7.0)
            + pill(cx, y + h + 12, "8 KM", INK, 7.0))


def sky(py, ph):
    return (f'<defs><linearGradient id="{U}sk" x1="0" y1="{n(py)}" x2="0" y2="{n(py + ph)}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#3F78C2"/>'
            f'<stop offset="0.38" stop-color="#86B4E6"/><stop offset="0.52" stop-color="#D8E5F1"/><stop offset="1" stop-color="#E9E5DC"/></linearGradient></defs>'
            f'<rect x="{n(PX)}" y="{n(py)}" width="{n(PW)}" height="{n(ph)}" fill="url(#{U}sk)"/>')


def panel(rid, py, uid, under, over, calls):
    at, ph = info(rid, py)
    clip = f'<defs><clipPath id="{uid}"><rect x="{n(PX)}" y="{n(py)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{uid})">'
    img = {"name": rid, "at": [PX + PW / 2, py + ph / 2], "width": PW, "whole": True}
    frame = f'</g><rect x="{n(PX)}" y="{n(py)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [clip + under(at, ph), img, over(at, ph) + frame + calls(at)]


def top_over(at, ph):
    (tx, ty), (bx, by), (lx, ly) = at("top"), at("bottom"), at("left")
    (ctx, cty), (cbx, cby), (clx, cly) = at("cloud_top"), at("cloud_base"), at("cloud_left")
    (ax, ay) = at("ac")
    return (dim(ctx + 30, cty, ctx + 30, ty) + pill(ctx + 30, (cty + ty) / 2, "1 000 FT", BLUE)
            + dim(cbx + 30, cby, cbx + 30, by) + pill(cbx + 30, (cby + by) / 2 + 1, "500 FT", BLUE)
            + dim(lx, cly, clx, cly) + pill((lx + clx) / 2, cly - 14, "2 000 FT", BLUE)
            + pill(ax, ay + 26, "5 KM", INK) + inset(PX + PW - 166, PY1 + 12))


def bot_over(at, ph):
    (ax, ay), (rx, ry), (dx, dy) = at("ac"), at("thr"), at("deck")
    return (pill(ax + 4, ay + 26, "3 KM", INK) + pill(PX + PW / 2 + 40, PY2 + 30, "< 1 000 FT", RED) + pill(rx + 46, ry + 40, "5 KM", INK))


def layers():
    top = panel(TOP, PY1, U + "c1", lambda at, ph: sky(PY1, ph), top_over,
                lambda at: S.callout(1, at("front_left_top")[0] - 26, at("front_left_top")[1] - 22, *at("front_left_top"), r=10.5)
                + S.callout(2, PX + PW - 180, PY1 + 22, PX + PW - 166, PY1 + 30, r=10.5))
    bot = panel(BOT, PY2, U + "c2", lambda at, ph: "", bot_over,
                lambda at: S.callout(3, at("ac")[0] - 30, at("ac")[1] - 20, *at("ac"), r=10.5)
                + S.callout(4, PX + PW / 2 - 30, PY2 + 30, PX + PW / 2 - 2, PY2 + 30, r=10.5))
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', *top, *bot]


def plate():
    return {
        "id": "fig-02-04-vfr-minimums",
        "replaces": "fig-02-04-vfr-minimums.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-04-vfr-minimums.jpg",
        "caption": "Figure 2-4. VFR weather minimums: distance from cloud and flight visibility, low down by day, and near a controlled aerodrome",
        "desc": ("Figure 2-4. VFR weather minimums in two views: above, a cumulus inside a glass box of the distances to keep from it, the aeroplane outside the box; below, a generic aerodrome under a low layer of cloud, the aeroplane low and clear of it. The minimums: in Classes C and D, and in Class E below 10 000 ft MSL, 5 km and 500 ft below, 1 000 ft above and 2 000 ft horizontally from cloud; in Class E at or above 10 000 ft MSL, 8 km and 1 000 ft below and above, 1 500 m horizontally; "
                 "in Classes G and F at 1 200 ft or less above the surface, aeroplanes by day, 3 km and clear of clouds; and near a controlled aerodrome, no VFR beneath a ceiling of less than 1 000 ft and a ground visibility of 5 km to take off, land or enter the circuit. Not to scale."),
        "legend": [
            "Classes C and D, and Class E below 10 000 ft MSL: flight visibility 5 km; 500 ft below, 1 000 ft above and 2 000 ft horizontally from cloud.",
            "Class E at or above 10 000 ft MSL: 8 km; 1 000 ft below, 1 000 ft above and 1 500 m horizontally from cloud.",
            "Classes G and F, 1 200 ft or less above the surface, aircraft other than helicopters, by day: 3 km and clear of clouds.",
            "Near a controlled aerodrome: no VFR beneath a ceiling of less than 1 000 ft within the controlled airspace designated to the surface; to take off, land or enter the circuit, a ground visibility of at least 5 km. The AIP's own table is more demanding: plan to the more demanding figure.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
