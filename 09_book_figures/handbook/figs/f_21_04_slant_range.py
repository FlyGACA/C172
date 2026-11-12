"""Figure 21-4. DME slant range and ground distance at 6 000 ft above the station. A scene in a card: the desert horizon with its hills and plain, a VOR/DME station (white round building,
radome, antenna), the model seen from the right at 6 000 ft overhead, 1.7 NM out and 30 NM out, the slant range as a beam of light from the station, the ground distance as a green
dimension line with the break of the old figure, the height as a dimension line, the readings in small labels; every number and the five numbered callouts of the old figure kept
(figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

CARD = (10, 8, 620, 312)
GY = 270.0
BLUE, GREEN, INK = "#1D4ED8", "#047857", "#1F2937"


def world():
    objects = H.vor_station(128, GY, 1.4)
    return H.profile("a1w", CARD, GY + 1, seed=91, sun=(70, 50), far=22, mid=10, base=13, scrub_count=14, grain=False,
                     clouds=[H.cloud("cloud-cumulus-b", 250, 52, 66), H.cloud("cloud-cumulus-a", 440, 40, 72, 0.9), H.cloud("cloud-cumulus-b", 40, 36, 46, 0.85)],
                     palms=[(60, GY + 6, 0.5)], acacias=[(300, GY + 8, 0.5), (520, GY + 6, 0.45)], objects=objects)


def drop_line(x, y0, y1):
    return H.line_cased(x, y0, x, y1, "#3B4A63", 1.3, dash="5 4", casing=2.2)


def ground_break():
    """The break of the old figure in the ground line: the ground goes on to 30 NM."""
    return (f'<path d="M420,270 l6,-9 l8,18 l8,-18 l6,9" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" stroke-opacity="0.9"/>'
            f'<path d="M420,270 l6,-9 l8,18 l8,-18 l6,9" fill="none" stroke="#B45309" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')


def layers():
    out = [H.page("a1page", 640, 330), H.defs(), H.glow_defs(640, 330)]
    out += world()
    out.append(ground_break())
    # the three aeroplanes at 6 000 ft and their drop lines
    out.append(drop_line(130, 246, 130) + drop_line(390.9, 131.9, 270) + drop_line(572, 131.9, 270))
    out.append('<path d="M378.9,270 L378.9,258 L390.9,258" fill="none" stroke="#3B4A63" stroke-width="1.3"/>')
    out.append(H.beam(138, 254, 384.9, 127.9, "#3F8FF5", width=3.4))
    out.append('<defs><linearGradient id="a1fade" gradientUnits="userSpaceOnUse" x1="470" y1="0" x2="562" y2="0"><stop offset="0" stop-color="#58A6FF" stop-opacity="0"/><stop offset="1" stop-color="#58A6FF" stop-opacity="1"/></linearGradient></defs>'
               '<line x1="470" y1="177.9" x2="562" y2="127.9" stroke="url(#a1fade)" stroke-width="8" stroke-opacity="0.5" stroke-linecap="round" filter="url(#a1glow)"/>'
               '<line x1="470" y1="177.9" x2="562" y2="127.9" stroke="url(#a1fade)" stroke-width="3" stroke-dasharray="8 5" stroke-linecap="round"/>')
    for cx in (129, 390, 571):
        out.append({"name": "sprite-side", "at": [cx, 118.5], "width": 62, **H.LOOK})
    # the height, the ground distance
    out.append(H.dim_line(86, 124, 86, 268, INK, 1.5, head=6.5))
    out.append(H.pill(52, 190, 46, 18, "6 000", INK, 12, border="#8793A8"))
    out.append(H.dim_line(138.4, 286, 390.9, 286, GREEN, 1.8, head=7))
    out.append(H.pill(130, 80, 42, 20, "1.0", INK, 13))
    out.append(H.pill(229.4, 171.9, 42, 20, "2.0", BLUE, 13))
    out.append(H.pill(526, 85.9, 48, 20, "30.0", BLUE, 13))
    out.append(H.pill(260.4, 286, 42, 20, "1.7", GREEN, 13))
    out.append(H.pill(572, 286, 48, 20, "30.0", GREEN, 13))
    c = S.callout
    out.append("".join([c(1, 94, 82, r=10), c(2, 52, 214, r=10), c(3, 194.4, 171.9, r=10), c(4, 296.4, 286, r=10), c(5, 606, 85.9, r=10)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-21-04-slant-range",
        "replaces": "fig-21-04-slant-range.svg",
        "book_file": "plate-21-04-slant-range.jpg",
        "caption": "Figure 21-4. DME slant range and ground distance at 6 000 ft above the station",
        "desc": "Figure 21-4. DME slant range and ground distance at 6 000 ft above the station",
        "legend": [
            "Overhead: the DME shows 1.0 NM; the ground distance is zero.",
            "Height above the station: 6 000 ft, about 0.99 NM.",
            "Slant range on the DME: 2.0 NM.",
            "Ground distance: 1.7 NM.",
            "Far out, 30.0 NM on the DME is 30.0 NM over the ground.",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-21-04-slant-range.svg", "blank": True, "layers": layers()},
    }
