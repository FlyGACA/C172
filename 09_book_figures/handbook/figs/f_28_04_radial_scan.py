"""Figure 28-4 of the handbook: the six flight instruments and the radial scan, centred on the attitude indicator.
Each instrument is a render of the model's own, laid out round the attitude indicator, with the scan as out-and-back arrows."""
from figs.kit import dial_layer, ring

BLUE = "#1D4ED8"


def plate():
    D, DAI, DT = 128, 148, 62                      # bezel diameters in the canvas: the instruments, the attitude indicator, the tachometer
    centres = {"ai": (320, 104), "asi": (96, 104), "alt": (544, 104), "tc": (96, 292), "dg": (320, 298), "vsi": (544, 292), "tach": (96, 402)}
    layers = [
        dial_layer("ai", "AI", centres["ai"], DAI),
        dial_layer("asi", "ASI", centres["asi"], D, {"ASI": 105}),
        dial_layer("alt", "ALT", centres["alt"], D, {"ALT": 3500}),
        dial_layer("tc", "TC", centres["tc"], D, {"turn": 0}),
        dial_layer("dg", "DG", centres["dg"], D, {"heading": 120}),
        dial_layer("vsi", "VSI", centres["vsi"], D, {"VSI": 0}),
        dial_layer("tach", "TACH", centres["tach"], DT, {"TACH": 2300}),
    ]
    r_ai, r = DAI / 2 + 8, D / 2 + 6
    overlays = [{"type": "svg", "markup": ring(*centres["ai"], r_ai + 4)}]
    for name in ("asi", "alt", "tc", "dg", "vsi"):
        overlays.append({"type": "pair", "from": "ai.c", "to": f"{name}.c", "gap": [r_ai + 8, r + 3], "offset": 5.2, "colour": BLUE, "width": 3.0, "head": 10})
    leaders = [(1, "ai", "rim_nw", [236, 22]), (2, "asi", "rim_nw", [32, 26]), (3, "alt", "rim_ne", [608, 26]),
               (4, "tc", "rim_sw", [32, 352]), (5, "dg", "rim_sw", [238, 360]), (6, "vsi", "rim_se", [608, 352]), (7, "tach", "rim_ne", [170, 380])]
    for n, name, rim, pos in leaders:
        overlays.append({"type": "marker", "n": n, "at": f"{name}.{rim}", "pos": pos, "leader": True, "gap": 0})
    overlays.append({"type": "marker", "n": 8, "at": "dg.rim_n", "pos": [418, 218], "leader": False})
    return {
        "id": "fig-28-04-radial-scan",
        "replaces": "fig-28-04-radial-scan.svg",
        "book_file": "plate-28-04-radial-scan.jpg",
        "caption": "Figure 28-4. The six flight instruments and the radial scan, centred on the attitude indicator",
        "desc": "The six flight instruments and the tachometer of the training aeroplane: the attitude indicator in the middle of the top row with arrows going out to each of the other five and back.",
        "legend": [
            "Attitude indicator: the centre of the scan.",
            "Airspeed indicator.",
            "Altimeter.",
            "Turn coordinator.",
            "Heading indicator.",
            "Vertical speed indicator.",
            "Tachometer: check after each power change.",
            "The scan: out and back.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "layers": layers,
        "overlays": overlays,
    }
