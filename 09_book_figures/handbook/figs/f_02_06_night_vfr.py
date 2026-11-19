"""Figure 2-6 (new). VFR at night in the Kingdom and the VFR fuel reserve, from the last two sections of Chapter 2: four scenes.

1 the night: a band of sky from day through sunset, civil twilight, night, morning twilight and sunrise, with the period in which VFR is prohibited (sunset to sunrise, §91.171) and the GACAR night (the end of evening civil twilight to the beginning of morning civil twilight)
under it; 2 the exception (a local flight round an aerodrome, under conditions prescribed by the ATC facility, or an authorization: a green tick); 3 position lights lit from sunset to sunrise (the aeroplane from above with its red, green and white lights); 4 the VFR fuel
(30 minutes by day and 45 minutes at night after the first point of intended landing, as two bars to scale). Shapes, colours and the numbers of the callouts; the only text is 30 MIN and 45 MIN. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import photo_ground as PG
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 404
U = "ar02n"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
TOP = (12.0, 12.0, 616.0, 150.0)
BOT = ((12.0, 172.0, 197.0, 220.0), (221.0, 172.0, 197.0, 220.0), (430.0, 172.0, 197.0, 220.0))
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
NIGHT = [(0.0, "#0F1E3E"), (0.55, "#2B3A6B"), (0.9, "#4C5F95"), (1.0, "#5E6F9F")]


def frame(uid, r, body):
    x, y, w, h = r
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-5%" y="-10%" width="110%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def pill(cx, cy, w, text, fill="#1F2937", h=11.0):
    return M.chip(cx, cy, text, fill, size=h * 0.8, min_w=w)


def stars(r, seed):
    import random
    rnd = random.Random(seed)
    x, y, w, h = r
    return "".join(f'<circle cx="{n(rnd.uniform(x + 8, x + w - 8))}" cy="{n(rnd.uniform(y + 6, y + h * 0.55))}" r="{n(rnd.uniform(0.6, 1.2))}" fill="#FFFFFF" opacity="{n(rnd.uniform(0.5, 0.95))}"/>' for _ in range(int(w / 9)))


def timeline():
    x, y, w, h = TOP
    g = (f'<defs><linearGradient id="{U}tl" x1="0" y1="0" x2="1" y2="0">'
         '<stop offset="0" stop-color="#7FB2E5"/><stop offset="0.12" stop-color="#9FC3E8"/><stop offset="0.17" stop-color="#F6C27A"/><stop offset="0.24" stop-color="#9A6FA8"/>'
         '<stop offset="0.33" stop-color="#1B2A55"/><stop offset="0.5" stop-color="#0F1E3E"/><stop offset="0.67" stop-color="#1B2A55"/><stop offset="0.76" stop-color="#9A6FA8"/>'
         '<stop offset="0.83" stop-color="#F6C27A"/><stop offset="0.88" stop-color="#9FC3E8"/><stop offset="1" stop-color="#7FB2E5"/></linearGradient></defs>')
    sx0, sx1 = x + w * 0.17, x + w * 0.83
    nx0, nx1 = x + w * 0.30, x + w * 0.70
    ground = f'<path d="M{n(x)} {n(y + 98)} Q{n(x + w * 0.25)} {n(y + 90)} {n(x + w * 0.5)} {n(y + 96)} T{n(x + w)} {n(y + 94)} L{n(x + w)} {n(y + h)} L{n(x)} {n(y + h)} Z" fill="#6B5B45" fill-opacity="0.85"/>'
    sun1 = S.glow(f"{U}s1", sx0, y + 96, 30, "#FFE3A8", 0.95) + f'<circle cx="{n(sx0)}" cy="{n(y + 94)}" r="9" fill="#FFF3CF"/>'
    sun2 = S.glow(f"{U}s2", sx1, y + 96, 30, "#FFE3A8", 0.95) + f'<circle cx="{n(sx1)}" cy="{n(y + 94)}" r="9" fill="#FFF3CF"/>'
    moon = S.glow(f"{U}mg", x + w / 2, y + 44, 34, "#FFF1C8", 0.55) + f'<circle cx="{n(x + w / 2)}" cy="{n(y + 44)}" r="11" fill="#F7EBC2"/>'
    br_red = (f'<path d="M{n(sx0)} {n(y + 108)} L{n(sx0)} {n(y + 118)} L{n(sx1)} {n(y + 118)} L{n(sx1)} {n(y + 108)}" fill="none" stroke="{RED}" stroke-width="3.2"/>'
              f'<circle cx="{n(x + w / 2)}" cy="{n(y + 128)}" r="14" fill="#FFFFFF" fill-opacity="0.92" stroke="{RED}" stroke-width="3.4"/><line x1="{n(x + w / 2 - 10)}" y1="{n(y + 138)}" x2="{n(x + w / 2 + 10)}" y2="{n(y + 118)}" stroke="{RED}" stroke-width="3.4" stroke-linecap="round"/>')
    br_blue = f'<path d="M{n(nx0)} {n(y + 20)} L{n(nx0)} {n(y + 10)} L{n(nx1)} {n(y + 10)} L{n(nx1)} {n(y + 20)}" fill="none" stroke="#BFDBFE" stroke-width="3"/>'
    return frame(f"{U}t", TOP, g + f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}tl)"/>' + stars(TOP, 5) + moon + ground + sun1 + sun2 + br_blue + br_red)


def plane_top(cx, cy, w, angle=90.0):
    return {"name": "sprite-top", "at": [cx, cy], "width": w, "angle": angle, "outline": OUT, "shadow": SHADOW}


def light(cx, cy, col, r=14.0):
    return S.glow(f"{U}l{int(cx)}{int(cy)}", cx, cy, r, col, 0.95) + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="2.6" fill="#FFFFFF"/>'


def panel_exception():                                       # a local flight round an aerodrome, a tick
    x, y, w, h = BOT[0]
    rw = f'<rect x="{n(x + 34)}" y="{n(y + 176)}" width="130" height="10" rx="2" fill="#5B6577"/><line x1="{n(x + 40)}" y1="{n(y + 181)}" x2="{n(x + 158)}" y2="{n(y + 181)}" stroke="#F1F5F9" stroke-width="1.2" stroke-dasharray="7 5"/>'
    loop = S.ribbon(f"{U}lp", [(x + 40, y + 110), (x + 100, y + 84), (x + 162, y + 104), (x + 150, y + 150), (x + 70, y + 152), (x + 36, y + 124)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.9, head=2.0, tail=0.5, per=8)
    tick = (f'<circle cx="{n(x + 168)}" cy="{n(y + 36)}" r="17" fill="{GREEN}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<path d="M{n(x + 160)} {n(y + 37)} L{n(x + 166)} {n(y + 43)} L{n(x + 177)} {n(y + 30)}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    return frame(f"{U}e", BOT[0], S.sky(f"{U}ek", x, y, w, h, NIGHT) + stars(BOT[0], 8) + PG.side(x, x + w, y + 168, y + h, tone="night", offset=0.2) + rw + loop + tick)


def panel_lights():
    x, y, w, h = BOT[1]
    return frame(f"{U}g", BOT[1], S.sky(f"{U}gk", x, y, w, h, NIGHT) + stars(BOT[1], 11) + PG.side(x, x + w, y + 168, y + h, tone="night", offset=0.2))


def panel_lights_over():
    x, y, w, h = BOT[1]
    cx, cy = x + w / 2, y + 100
    return light(cx + 2, cy - 54, "#FF5A4A") + light(cx + 2, cy + 54, "#5AE08A") + light(cx - 52, cy, "#FFFFFF")


def panel_fuel():
    x, y, w, h = BOT[2]
    k = 2.6                                                    # units per minute
    bx = x + 24
    out = [S.sky(f"{U}fk", x, y, w, h, [(0.0, "#EAF1FA"), (1.0, "#F6EFE0")])]
    rw = f'<rect x="{n(bx - 4)}" y="{n(y + 48)}" width="46" height="10" rx="2" fill="#5B6577"/><line x1="{n(bx)}" y1="{n(y + 53)}" x2="{n(bx + 38)}" y2="{n(y + 53)}" stroke="#F1F5F9" stroke-width="1.2" stroke-dasharray="6 4"/><line x1="{n(bx)}" y1="{n(y + 62)}" x2="{n(bx)}" y2="{n(y + 196)}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>'
    out.append(rw)
    for i, (mins, col, label, icon_y) in enumerate(((30, "#F59E0B", "30 MIN", y + 80), (45, "#2563EB", "45 MIN", y + 150))):
        bw = mins * k
        out.append(f'<rect x="{n(bx)}" y="{n(icon_y)}" width="{n(bw)}" height="26" rx="8" fill="{col}" stroke="#FFFFFF" stroke-width="1.8"/><rect x="{n(bx)}" y="{n(icon_y)}" width="{n(bw)}" height="9" rx="8" fill="#FFFFFF" fill-opacity="0.22"/>')
        out.append(H.glyph_text(label, bx + bw / 2, icon_y + 14, 11.0, fill="#FFFFFF"))
    sun = S.glow(f"{U}fs", bx + 96, y + 93, 20, "#FFF2C4", 0.95) + f'<circle cx="{n(bx + 96)}" cy="{n(y + 93)}" r="8" fill="#FDE68A" stroke="#F59E0B" stroke-width="1.4"/>'
    moon = f'<circle cx="{n(bx + 141)}" cy="{n(y + 163)}" r="8" fill="#F7EBC2" stroke="{INK}" stroke-width="1.4"/>'
    return frame(f"{U}f", BOT[2], "".join(out) + sun + moon)


def sprites():
    x, y, w, h = BOT[0]
    return [plane_top(x + 100, y + 88, 36, 0.0), plane_top(BOT[1][0] + BOT[1][2] / 2, BOT[1][1] + 100, 80, 90.0)]


def callouts():
    c = S.callout
    return c(1, TOP[0] + 17, TOP[1] + 17, r=10.5) + c(2, BOT[0][0] + 17, BOT[0][1] + 17, r=10.5) + c(3, BOT[1][0] + 17, BOT[1][1] + 17, r=10.5) + c(4, BOT[2][0] + 17, BOT[2][1] + 17, r=10.5)


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', timeline(), panel_exception(), panel_lights(), panel_fuel(), *sprites(), panel_lights_over(), callouts()]


def plate():
    return {
        "id": "fig-02-06-night-vfr",
        "replaces": "fig-02-06-night-vfr.svg",                # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-06-night-vfr.jpg",
        "caption": "Figure 2-6. VFR at night in the Kingdom: no VFR from sunset to sunrise without an authorization, lights lit, and 45 minutes of fuel",
        "desc": ("Figure 2-6. VFR at night in the Kingdom in four scenes: no VFR from sunset to sunrise, with the GACAR night (evening to morning civil twilight) inside that period; the exception of an authorization or a local flight under ATC conditions; "
                 "position lights lit from sunset to sunrise; and the VFR fuel, 30 minutes by day or 45 minutes at night after the first point of intended landing."),
        "legend": [
            "No person may operate an aircraft under VFR from sunset to sunrise in KSA airspace. The GACAR definition of night is the period between the end of evening civil twilight and the beginning of morning civil twilight; the prohibition is stated from sunset to sunrise.",
            "The exception: unless the President has authorized it, or the flight is a local flight under conditions prescribed by the appropriate ATC facility. The night lessons of the private pilot course are flown under such an authorization or such local conditions, which your school arranges.",
            "From sunset to sunrise an aircraft must show lighted position lights, and an aircraft parked or moving on or near an aerodrome movement area must be illuminated, show position lights, or be in an area marked by obstruction lights.",
            "VFR fuel: enough fuel to fly to the first point of intended landing and then, at normal cruising speed, for at least 30 minutes by day or 45 minutes at night.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
