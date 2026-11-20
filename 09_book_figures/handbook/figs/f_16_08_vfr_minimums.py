"""Figure 16-8. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome (redrawn in the second design pass as two 3D views).

Two renders (figs/oeth3d.py; blender/render_oeth.py), the ground the open picture of the desert east of Thumamah on its relief:
- above: the same view as Figure 2-4's (vfr-2-04-cloud): a cumulus of the cloud library inside a glass box of the distances to keep from it (500 ft below,
  1 000 ft above, 2 000 ft all round), the aeroplane flying past; callouts 1 to 5 are the three distances, the flight visibility and the cloud.
- below (vfr-16-08-ceiling): the generic aerodrome of 2-4 under a layer of stratus whose base, the ceiling, is a little over 1 000 ft above the ground,
  with the surface area of the controlled airspace round it as a see-through drum; callouts 6 to 8 are the ceiling, the ground visibility and the drum.
The text is the distances, from the chapter. The aerodrome is generic; the aeroplanes are enlarged and the drum is not to scale."""
from figs import h_b2 as H
from figs import scene as S
from figs import f_02_04_vfr_minimums as V

n = S.n
W = V.W
U = "f1608"
TOP, BOT = "vfr-2-04-cloud", "vfr-16-08-ceiling"
PX, PW, PH = V.PX, V.PW, V.PH
PY1, PY2, HT = V.PY1, V.PY2, V.HT


def top_over(at, ph):
    (tx, ty), (bx, by), (lx, ly) = at("top"), at("bottom"), at("left")
    (ctx, cty), (cbx, cby), (clx, cly) = at("cloud_top"), at("cloud_base"), at("cloud_left")
    (ax, ay) = at("ac")
    return (V.dim(ctx + 30, cty, ctx + 30, ty) + V.pill(ctx + 30, (cty + ty) / 2, "1 000 FT", V.BLUE)
            + V.dim(cbx + 30, cby, cbx + 30, by) + V.pill(cbx + 30, (cby + by) / 2 + 1, "500 FT", V.BLUE)
            + V.dim(lx, cly, clx, cly) + V.pill((lx + clx) / 2, cly - 14, "2 000 FT", V.BLUE)
            + V.pill(ax, ay + 26, "5 KM", V.INK))


def top_calls(at):
    (tx, ty), (bx, by) = at("top"), at("bottom")
    (ctx, cty), (cbx, cby), (clx, cly), (lx, ly) = at("cloud_top"), at("cloud_base"), at("cloud_left"), at("left")
    (ax, ay), (cx, cy) = at("ac"), at("cloud")
    c = S.callout
    return (c(1, cbx + 92, (cby + by) / 2 + 1, cbx + 56, (cby + by) / 2 + 1, r=10.5) + c(2, ctx + 96, (cty + ty) / 2, ctx + 64, (cty + ty) / 2, r=10.5)
            + c(3, (lx + clx) / 2 - 58, cly - 14, (lx + clx) / 2 - 36, cly - 14, r=10.5) + c(4, ax - 4, ay + 52, ax, ay + 36, r=10.5)
            + c(5, cx - 40, cy + 62, cx - 20, cy + 14, r=10.5))


def bot_over(at, ph):
    (dx, dy), (gx, gy), (rx, ry) = at("deck"), at("deck_ground"), at("rwy")
    return (V.dim(dx, dy + 2, gx, gy - 2) + V.pill(dx + 34, (dy + gy) / 2, "1 000 FT", V.BLUE)
            + V.pill(rx + 70, ry + 30, "5 KM", V.INK))


def bot_calls(at):
    (dx, dy), (gx, gy), (rx, ry), (cl, cly) = at("deck"), at("deck_ground"), at("rwy"), at("ctr_left")
    c = S.callout
    return (c(6, dx + 92, (dy + gy) / 2, dx + 66, (dy + gy) / 2, r=10.5) + c(7, rx + 128, ry + 30, rx + 104, ry + 30, r=10.5)
            + c(8, PX + 40, PY2 + PH - 30, PX + 80, (cly + PY2 + PH) / 2 - 10, r=10.5))


def layers():
    top = V.panel(TOP, PY1, U + "c1", lambda at, ph: V.sky(PY1, ph), top_over, top_calls)
    bot = V.panel(BOT, PY2, U + "c2", lambda at, ph: "", bot_over, bot_calls)
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', *top, *bot]


def plate():
    return {
        "id": "fig-16-08-vfr-minimums",
        "replaces": "fig-16-08-vfr-minimums.svg",
        "book_file": "plate-16-08-vfr-minimums.jpg",
        "caption": "Figure 16-8. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome",
        "desc": ("Figure 16-8. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome. Above, a cumulus inside a see-through box of the distances to "
                 "keep from it: 500 ft below, 1 000 ft above and 2 000 ft horizontally, with a flight visibility of 5 km. Below, an aerodrome under a cloud layer whose base, "
                 "the ceiling, is at least 1 000 ft above the ground, a ground visibility of 5 km, and the surface area of the controlled airspace round it."),
        "legend": [
            "500 ft below cloud.",
            "1 000 ft above cloud.",
            "2 000 ft horizontally from cloud.",
            "Flight visibility 5 km.",
            "The cloud.",
            "Ceiling at least 1 000 ft to fly beneath it within controlled airspace designated to the surface for an aerodrome [[§91.165(d)]].",
            "Ground visibility at least 5 km to take off, land or enter the circuit in the surface area of Class B, C, D or E airspace; flight visibility if none is reported [[§91.165(e)]].",
            "The surface area of controlled airspace.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
