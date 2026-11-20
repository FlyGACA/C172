"""Figure 19-11. A transponder, an assigned code and the three emergency codes. Drawn again with the hardware of Figure 21-9 (figs/f_21_09_transponder.py: the bezel,
the lit display, the knurled knobs, the selector, the ident button, the reply lamp); the layout of the old flat figure and its eight callouts are kept: the head above, with the code
4521 and its four selectors, the mode selector (its positions differ between types, so only its detents are drawn), IDENT and the reply light; below, four cards, each a small lit
display of a code over a sign of what it means: 4521 assigned by ATC (a control tower), 7700 (a warning sign), 7600 (a headset crossed out), 7500 (a padlock)."""
from figs import f_21_09_transponder as T
from figs import scene as S

n = S.n
W, HT = 640, 350
BLUE, RED, AMBER, INK = "#1D4ED8", "#B91C1C", "#B45309", "#1F2937"
CARDS = [(20.0, "4521", BLUE, "#EEF3FE"), (172.0, "7700", RED, "#FDF0F0"), (324.0, "7600", AMBER, "#FDF5EA"), (476.0, "7500", INK, "#F4F5F7")]


def tower(cx, cy, col):
    return (f'<rect x="{n(cx - 4.5)}" y="{n(cy + 4)}" width="9" height="30" fill="{col}"/>'
            f'<polygon points="{n(cx - 13.5)},{n(cy - 10)} {n(cx + 13.5)},{n(cy - 10)} {n(cx + 9)},{n(cy + 4)} {n(cx - 9)},{n(cy + 4)}" fill="{col}"/>'
            f'<rect x="{n(cx - 10.8)}" y="{n(cy - 6.4)}" width="21.6" height="5.4" fill="#FFFFFF" opacity="0.85"/>'
            f'<rect x="{n(cx - 15.3)}" y="{n(cy - 13.6)}" width="30.6" height="3.6" fill="{col}"/><rect x="{n(cx - 10.8)}" y="{n(cy + 34)}" width="21.6" height="2.7" fill="{col}"/>')


def warning(cx, cy, col):
    return (f'<polygon points="{n(cx)},{n(cy - 18)} {n(cx + 21)},{n(cy + 18)} {n(cx - 21)},{n(cy + 18)}" fill="#FFFFFF" stroke="{col}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<rect x="{n(cx - 2.2)}" y="{n(cy - 6)}" width="4.5" height="14" rx="1" fill="{col}"/><circle cx="{n(cx)}" cy="{n(cy + 12.6)}" r="2.7" fill="{col}"/>')


def headset(cx, cy, col):
    return (f'<path d="M{n(cx - 15.4)},{n(cy - 4)} A15.4,15.4 0 0,1 {n(cx + 15.4)},{n(cy - 4)}" fill="none" stroke="{INK}" stroke-width="3.3"/>'
            f'<rect x="{n(cx - 19.8)}" y="{n(cy - 7.3)}" width="8.8" height="15.4" rx="3.3" fill="{INK}"/><rect x="{n(cx + 11)}" y="{n(cy - 7.3)}" width="8.8" height="15.4" rx="3.3" fill="{INK}"/>'
            f'<path d="M{n(cx - 15.4)},{n(cy + 8)} Q{n(cx - 13.2)},{n(cy + 18)} {n(cx - 2.2)},{n(cy + 18)}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy + 18)}" r="2.9" fill="{INK}"/>'
            f'<path d="M{n(cx - 10)},{n(cy + 7)} l20,20 M{n(cx + 10)},{n(cy + 7)} l-20,20" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>')


def lock(cx, cy, col):
    return (f'<path d="M{n(cx - 10.8)},{n(cy + 4)} L{n(cx - 10.8)},{n(cy - 6)} A10.8,10.8 0 0,1 {n(cx + 10.8)},{n(cy - 6)} L{n(cx + 10.8)},{n(cy + 4)}" fill="none" stroke="{col}" stroke-width="4.2"/>'
            f'<rect x="{n(cx - 16.8)}" y="{n(cy + 3)}" width="33.6" height="26.4" rx="3.6" fill="{col}"/><circle cx="{n(cx)}" cy="{n(cy + 14)}" r="3.6" fill="#FFFFFF"/>')


def card(x, code, col, bg, sign):
    out = [f'<rect x="{n(x + 2)}" y="190" width="140" height="140" rx="10" fill="#10233F" opacity="0.18"/>',
           f'<rect x="{n(x)}" y="186" width="140" height="140" rx="10" fill="{bg}" stroke="{col}" stroke-width="3"/>',
           T.display(f"c19{code}", x + 16, 208, 108, 40, code, "#FF6B5E" if col == RED else T.AMBER, 20.0)]
    out.append(sign(x + 70, 280, col))
    return "".join(out)


def disc(k, x, y, col, r=12.0):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 1.6)}" fill="#FFFFFF"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{col}"/>'
            f'<text x="{n(x)}" y="{n(y + 4.7)}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">{k}</text>')


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', T.unit(110.0, 18.0, 420.0, 120.0)]
    out.append(T.display("t19d", 134, 34, 190, 56, "4521", T.AMBER, 24.0))
    for x in (156.0, 204.0, 252.0, 300.0):
        out.append(T.knob(x, 114, 11, 18))
    out.append(T.selector(390, 80, pos=[300.0, 340.0, 20.0, 60.0], at=3, r=22))
    out.append(T.ident(469, 63) + T.lamp(469, 110))
    for x, code, col, bg in CARDS:
        out.append(card(x, code, col, bg, {"4521": tower, "7700": warning, "7600": headset, "7500": lock}[code]))
    c = S.callout
    out.append(c(1, 88, 66, 132, 66) + c(2, 390, 156, 390, 112) + c(3, 552, 63, 500, 63) + c(4, 552, 108, 479, 108))
    out.append(disc(5, 38, 204, BLUE) + disc(6, 190, 204, RED) + disc(7, 342, 204, AMBER) + disc(8, 494, 204, INK))
    return out


def plate():
    return {
        "id": "fig-19-11-transponder-codes",
        "replaces": "fig-19-11-transponder-codes.svg",
        "book_file": "plate-19-11-transponder-codes.jpg",
        "caption": "Figure 19-11. A transponder, an assigned code and the three emergency codes",
        "desc": "Figure 19-11. A transponder, an assigned code and the three emergency codes",
        "legend": [
            "The code window and its four selectors.",
            "The mode selector; its positions differ between types, so learn yours from the POH.",
            "IDENT: only when ATC asks [[§91.229(e)]].",
            "The reply light.",
            "A code ATC assigns, here 4521: read back the code and mode [[§91.229(b)]].",
            "7700: emergency.",
            "7600: loss of two-way communication [[§91.229(g)]].",
            "7500: unlawful interference.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-19-11-transponder-codes.svg", "blank": True, "layers": layers()},
    }
