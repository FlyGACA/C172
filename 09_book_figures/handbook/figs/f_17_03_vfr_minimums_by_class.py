"""Figure 17-3. VFR visibility and distance from cloud in Classes B to E. Three scenes in cards, one for each group of classes: a desert horizon under a cumulus of the model of the sky
(figs/clouds.py) in place of the white blob, the model seen from the right close to it (Class B, clear of clouds) and, in Classes C, D, E and in Class E high up, 500 or 1 000 ft below
it, 1 000 ft above it and 2 000 ft (1 500 m) beside it, with the visibility as a dashed arrow along the foot of each card. Every distance, dimension line and letter of the old figure
is kept, with its nine numbered callouts (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

CARDS = [(12, 12, 196, 368), (222, 12, 196, 368), (432, 12, 196, 368)]
GY = 336.0
INK, GREEN, AMBER = "#1F2937", "#047857", "#B45309"
SKY_E = [(0.0, "#2F66B4"), (0.45, "#6FA2DB"), (0.86, "#C9DDF3"), (1.0, "#F4EFD9")]
W = 56.0


def cloud_at(cx, base, w=82, h=56):
    return {"name": "cloud-cumulus-c", "at": [cx, base - h / 2], "width": w, "height": h, "haze": {"colour": "#CFE0F3", "amount": 0.05}}


def world(i, box, letters, sky, seed):
    x = box[0]
    return H.profile(f"a1c{i}", box, GY, seed=seed, sun=(50, 50), far=22, mid=10, base=13, sky=sky or H.SKY, scrub_count=7, grain=False,
                     clouds=[cloud_at(x + 73, 214)], palms=[(x + 20, GY - 5, 0.5)], acacias=[(x + 176, GY - 4, 0.45)])


def tab(x, y, text):
    return (f'<rect x="{x - 8}" y="{y - 17}" width="{14 + 11.5 * len(text)}" height="26" rx="6" fill="#FFFFFF" fill-opacity="0.9"/>'
            f'<text x="{x}" y="{y}" font-family="monospace" font-size="17" font-weight="bold" fill="#1D4ED8" text-anchor="start">{text}</text>')


def visibility(x0, x1, label_x, label):
    return (H.path_line(f"M {x0} 364 L {x1 - 7.2} 364", GREEN, 2.5, dash="7 4", casing=2.4, glow=False) + H.arrow_head(x1, 364, 0, 10, GREEN) + H.pill(label_x, 346, 32, 20, label, GREEN, 13))


def layers():
    out = [H.page("a1page", 640, 392), H.defs()]
    out += world(0, CARDS[0], "B", None, 111) + world(1, CARDS[1], "CDE", None, 113) + world(2, CARDS[2], "E", SKY_E, 117)
    # card B: clear of cloud, the aeroplanes right beside it
    out.append({"name": "sprite-side", "at": [88, 226.5], "width": W, **H.LOOK})
    out.append({"name": "sprite-side-left", "at": [161, 186.5], "width": W, **H.LOOK})
    # cards C D E and E: above, below and to the side
    for dx in (210, 420):
        out.append({"name": "sprite-side", "at": [90 + dx, 68.5], "width": W, **H.LOOK})
        out.append({"name": "sprite-side", "at": [90 + dx, 304.5], "width": W, **H.LOOK})
        out.append({"name": "sprite-side-left", "at": [174 + dx, 186.5], "width": W, **H.LOOK})
    out.append(H.dim_line(295, 82, 295, 152, INK, 2.0, head=6.5) + H.pill(295, 117, 50, 20, "1 000", INK, 13))
    out.append(H.dim_line(295, 217, 295, 297, INK, 2.0, head=6.5) + H.pill(295, 257, 50, 20, "500", INK, 13))
    out.append(H.dim_line(337, 168, 386, 168, INK, 2.0, head=6.5) + H.pill(362, 146, 50, 20, "2 000", INK, 13))
    out.append(H.dim_line(505, 82, 505, 152, INK, 2.0, head=6.5) + H.pill(505, 117, 50, 20, "1 000", INK, 13))
    out.append(H.dim_line(505, 217, 505, 297, INK, 2.0, head=6.5) + H.pill(505, 257, 50, 20, "1 000", INK, 13))
    out.append(H.dim_line(547, 168, 596, 168, AMBER, 2.0, head=6.5) + H.pill(572, 146, 50, 20, "1 500", AMBER, 13, border="#E5B06A"))
    out.append(visibility(28, 192, 110, "5") + visibility(238, 402, 320, "5") + visibility(448, 612, 530, "8"))
    out.append(tab(38, 40, "B") + tab(248, 40, "C D E") + tab(458, 40, "E"))
    c = S.callout
    out.append("".join([c(1, 40, 232), c(2, 261, 261), c(3, 261, 117), c(4, 362, 214, 362, 170), c(5, 396, 34), c(6, 471, 261),
                         c(7, 471, 117), c(8, 572, 214, 572, 170), c(9, 606, 34)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-17-03-vfr-minimums-by-class",
        "replaces": "fig-17-03-vfr-minimums-by-class.svg",
        "book_file": "plate-17-03-vfr-minimums-by-class.jpg",
        "caption": "Figure 17-3. VFR visibility and distance from cloud in Classes B to E",
        "desc": "Figure 17-3. VFR visibility and distance from cloud in Classes B to E",
        "legend": [
            "Class B: clear of clouds.",
            "500 ft below cloud.",
            "1 000 ft above.",
            "2 000 ft horizontally.",
            "Classes C and D, and Class E below 10 000 ft MSL.",
            "1 000 ft below.",
            "1 000 ft above.",
            "1 500 m horizontally (amber: metres).",
            "Class E at or above 10 000 ft MSL.",
        ],
        "canvas": [640, 392],
        "background": "pale",
        "reskin": {"svg": "fig-17-03-vfr-minimums-by-class.svg", "blank": True, "layers": layers()},
    }
