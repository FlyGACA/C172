"""Figure 31-10 (new; redrawn in the second design pass as one view). In flight at night over the Kingdom, from "In flight" of Chapter 31.

One render (figs/oeth3d.py, night-31-10; blender/render_oeth.py): the open picture of the desert east of Thumamah on its relief under a faint moon, about 2 000 ft
up behind the 3D model with its navigation lights lit, looking north-east. On it: 1 a near town whose lights are separate points at 2 000 ft, with a round inset of the same
town from 5 000 ft, one mass of light; 2 a straight road of sodium lights rising across the view, a false horizon (with a level attitude indicator, drawn, to trust, and a single
light with the dashes of autokinesis); 3 a small town under a patch of ground fog, its lights haloed and fading; 4 to the right, desert with no lights. The sky
and its stars are drawn (the render leaves it clear), down to the render's own colour at the horizon. The places and towns are generic."""
import json
import os
import random

from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 406
U = "ar31n"
R3D = "night-31-10"
PX, PY, PW = 8.0, 8.0, 624.0
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render_info():
    with open(os.path.join(HERE, "renders", R3D + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ph = PW * h / w
    at = lambda k: (PX + d["anchors"][k][0] * PW, PY + d["anchors"][k][1] * ph)
    return at, ph


def horizon_colour(v):
    """The colour of the render just under its horizon (the haze at the far ground), so that the drawn sky ends in it."""
    try:
        from PIL import Image
        im = Image.open(os.path.join(HERE, "renders", R3D + ".png")).convert("RGBA")
        y = min(im.height - 1, int(v * im.height) + 3)
        px = [im.getpixel((x, y)) for x in range(im.width // 10, im.width, im.width // 10)]
        px = [p for p in px if p[3] > 200] or [(46, 59, 102, 255)]
        r, g, b = (sum(p[c] for p in px) // len(px) for c in range(3))
        return f"#{r:02X}{g:02X}{b:02X}"
    except OSError:
        return "#2E3B66"


def sky(at, ph):
    hx, hy = at("hz")
    col = horizon_colour((hy - PY) / ph)
    grad = (f'<defs><linearGradient id="{U}sk" x1="0" y1="{n(PY)}" x2="0" y2="{n(hy)}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#040815"/>'
            f'<stop offset="0.55" stop-color="#0D1631"/><stop offset="1" stop-color="{col}"/></linearGradient></defs>'
            f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(hy - PY + 6)}" fill="url(#{U}sk)"/>')
    rnd = random.Random(31)
    stars = []
    for _ in range(170):
        x, y = rnd.uniform(PX + 4, PX + PW - 4), PY + (hy - PY - 14) * rnd.random() ** 1.35
        r = rnd.choice((0.45, 0.55, 0.7, 0.9, 1.2))
        stars.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#FFFFFF" opacity="{n(rnd.uniform(0.45, 0.95) * (1 - 0.5 * (y - PY) / (hy - PY)))}"/>')
    band = (f'<defs><linearGradient id="{U}hz" x1="0" y1="{n(hy - 9)}" x2="0" y2="{n(hy + 9)}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{col}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{col}" stop-opacity="0.9"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>')
    return grad + "".join(stars) + band


def horizon_band(at):
    """A soft band of the horizon's own colour over the meeting of the drawn sky and the render, so that no line shows there."""
    hx, hy = at("hz")
    return f'<rect x="{n(PX)}" y="{n(hy - 9)}" width="{n(PW)}" height="18" fill="url(#{U}hz)"/>'


def attitude(cx, cy, r=24.0):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + 3)}" fill="#0F172A" fill-opacity="0.55"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#7C4A21" stroke="#E2E8F0" stroke-width="2.6"/>'
            f'<path d="M{n(cx - r)} {n(cy)} A{n(r)} {n(r)} 0 0 1 {n(cx + r)} {n(cy)} Z" fill="#38BDF8"/><line x1="{n(cx - r)}" y1="{n(cy)}" x2="{n(cx + r)}" y2="{n(cy)}" stroke="#FFFFFF" stroke-width="1.2"/>'
            f'<path d="M{n(cx - 15)} {n(cy + 1)} H{n(cx - 5)} L{n(cx)} {n(cy + 5)} L{n(cx + 5)} {n(cy + 1)} H{n(cx + 15)}" fill="none" stroke="#FACC15" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy + 1)}" r="2.2" fill="#FACC15"/>')


def autokinesis(cx, cy):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="9" fill="#FFE9A8" fill-opacity="0.25"/><circle cx="{n(cx)}" cy="{n(cy)}" r="2.6" fill="#FFF6D6"/>'
            f'<path d="M{n(cx - 13)} {n(cy - 13)} q-6 -2 -8 -10 M{n(cx + 13)} {n(cy + 13)} q6 2 8 10 M{n(cx + 14)} {n(cy - 12)} q6 -4 9 -12" fill="none" stroke="#FFFFFF" '
            f'stroke-width="2" stroke-linecap="round" stroke-dasharray="3 3.5"/>')


def pill(cx, cy, w, text):
    return M.chip(cx, cy, text, "#1F2937", size=8.0, min_w=w)


def layers():
    at, ph = render_info()
    clip = f'<defs><clipPath id="{U}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10"/></clipPath></defs><g clip-path="url(#{U}c)">'
    img = {"name": R3D, "at": [PX + PW / 2, PY + ph / 2], "width": PW, "whole": True}
    (nx, ny), (fx, fy) = at("town_near"), at("town_far")
    (rx, ry), (gx, gy), (dx, dy) = at("road"), at("fog"), at("dark")
    hx, hy = at("hz")
    ix, iy = PX + 64, PY + 66                                # the same town from 5 000 ft: one mass of light (an inset, as a pilot higher up would see it)
    inset = (f'<defs><radialGradient id="{U}m"><stop offset="0" stop-color="#FFF4D6"/><stop offset="0.35" stop-color="#FFC46B" stop-opacity="0.9"/>'
             f'<stop offset="1" stop-color="#FFC46B" stop-opacity="0"/></radialGradient><clipPath id="{U}ic"><circle cx="{n(ix)}" cy="{n(iy)}" r="40"/></clipPath></defs>'
             f'<circle cx="{n(ix)}" cy="{n(iy)}" r="43" fill="#0F172A" fill-opacity="0.6"/><g clip-path="url(#{U}ic)"><rect x="{n(ix - 40)}" y="{n(iy - 40)}" width="80" height="80" fill="#141C34"/>'
             f'<ellipse cx="{n(ix)}" cy="{n(iy + 4)}" rx="30" ry="13" fill="url(#{U}m)"/></g><circle cx="{n(ix)}" cy="{n(iy)}" r="40" fill="none" stroke="#E2E8F0" stroke-width="2"/>'
             + pill(ix, iy + 54, 72, "5 000 FT") + f'<line x1="{n(ix + 38)}" y1="{n(iy + 14)}" x2="{n(nx - 30)}" y2="{n(ny - 8)}" stroke="#FFFFFF" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.7"/>')
    over = (horizon_band(at) + pill(nx, ny + 26, 72, "2 000 FT") + inset
            + attitude(rx - 14, hy - 62) + f'<line x1="{n(rx - 14)}" y1="{n(hy - 35)}" x2="{n(rx)}" y2="{n(ry - 6)}" stroke="#FFFFFF" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.8"/>'
            + autokinesis(gx - 70, hy - 70))
    frame = f'</g><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(ph)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    calls = (S.callout(1, nx - 52, ny - 34, nx - 8, ny - 4, r=10.5) + S.callout(2, rx + 40, ry + 54, rx + 2, ry + 3, r=10.5)
             + S.callout(3, gx + 6, gy + 62, gx, gy + 6, r=10.5) + S.callout(4, min(dx, PX + PW - 30), dy + 56, min(dx, PX + PW - 30), dy + 10, r=10.5))
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', clip + sky(at, ph), img, over + frame + calls]


def plate():
    return {
        "id": "fig-31-10-night-in-flight",
        "replaces": "fig-31-10-night-in-flight.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-31-10-night-in-flight.jpg",
        "caption": "Figure 31-10. In flight at night over the Kingdom: lights deceive, two illusions, weather in the lights, and the dark desert",
        "desc": ("Figure 31-10. In flight at night over the Kingdom, in one view from behind the aeroplane at about 2 000 ft: a near town whose lights are separate points, and a far one that is one mass of light (lights seen separately at 2 000 ft merge into one mass at 5 000 ft); a sloping road of lights that makes a false horizon, with a level attitude indicator to trust, and autokinesis; lights fading one by one and haloed, a sign of restricted visibility or ground fog, "
                 "so turn back while the lights behind are clear; and the dark desert with unlit high ground."),
        "legend": [
            "Lights deceive: lights seen separately at 2 000 ft may merge into one mass at 5 000 ft or higher, and a town appears long before you reach it.",
            "Two cruise illusions. A false horizon: ground lights mixed with stars, or a sloping cloud, suggest a horizon that is not level; trust the attitude indicator. Autokinesis: a single fixed light stared at for several seconds seems to move; keep your eyes moving and cross-check the instruments.",
            "Weather announces itself through the lights: lights fading one by one usually mean restricted visibility ahead, and a halo around them suggests ground fog. Turn back while lights behind you are still clear.",
            "Dark desert and unlit terrain: away from cities and highways there may be no lights at all, no checkpoints and no horizon; unlit high ground shows only where the stars or lights stop. Know each leg's safe altitude before takeoff.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
