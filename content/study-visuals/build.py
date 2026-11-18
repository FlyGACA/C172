#!/usr/bin/env python3
"""Deterministic builder for the study-visual pack: python3 content/study-visuals/build.py [--out DIR]

Every number is read from the repository's cited data (shared/js/sim.js and the POH reference
table); nothing here is typed from memory. The output is byte-identical on every run.

Both editions are real layouts, not mirrored markup: in the Arabic edition the panels, cards and
line starts swap sides, every text anchor is chosen from the writing direction, and numbers/ranges
are isolated (U+2066 ... U+2069) so "41–85" and "85 / 110" keep their order inside Arabic text.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from lib_svg import W, PALETTE, circle, document, fmt, group, line, path, rect, scale, text, wrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIM_JS = ROOT / "shared" / "js" / "sim.js"
POH_REFS = ROOT / "08_realistic_digital_twin" / "data" / "poh_references.json"

# A number, or several numbers joined by a range/speed separator, each with an optional unit.
# "41–85", "85 / 110", "2100–2450 RPM", "10° / 10–40°" and "5,000 ft" all match as one run.
_ATOM = r"\d+(?:[.,]\d+)?°?(?:\s(?:US\s)?(?:gal|KIAS|RPM|BHP|lbf|ft|in))?"
NUM_RUN = re.compile(
    r"(?<![\w./-])" + _ATOM + r"(?:\s*(?:–|—|→|/|×|-)\s*" + _ATOM + r")*(?![\w])"
)


def isolate_numbers(value):
    return NUM_RUN.sub(lambda match: "\u2066" + match.group(0) + "\u2069", str(value))


def align(direction, visual):
    """Map a visual alignment to the logical text-anchor for the document direction."""
    if visual == "center":
        return "middle"
    left = visual == "left"
    return "start" if (direction == "ltr") == left else "end"


def load_sim():
    text = SIM_JS.read_text(encoding="utf-8")
    numbers = {}
    for key in (
        "vne",
        "vno",
        "vfe",
        "va2300",
        "maxRpm",
        "fuelPerTankTotal",
        "fuelPerTankUsable",
        "fuelUnusablePerTank",
    ):
        match = re.search(r"\b%s\s*:\s*([0-9.]+)" % key, text)
        if not match:
            raise SystemExit("shared/js/sim.js: constant %s not found" % key)
        numbers[key] = float(match.group(1))
    for key in ("asiWhite", "asiGreen", "asiYellow"):
        match = re.search(r"\b%s\s*:\s*\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\]" % key, text)
        if not match:
            raise SystemExit("shared/js/sim.js: arc %s not found" % key)
        numbers[key] = [float(match.group(1)), float(match.group(2))]
    match = re.search(r"ALT_STATIC_TABLE\s*=\s*(\[\[.*?\]\])", text, re.S)
    if not match:
        raise SystemExit("shared/js/sim.js: ALT_STATIC_TABLE not found")
    numbers["altStatic"] = json.loads(match.group(1))
    return numbers


def load_poh():
    data = json.loads(POH_REFS.read_text(encoding="utf-8"))
    return {entry["key"]: str(entry["value"]) for entry in data["values"]}


def verify_poh(sim):
    """Fail the build when a drawn value no longer matches the printed POH text it cites.

    The figures are drawn from sim.js; this binding re-reads the POH table and refuses to build
    if the two disagree, so a changed number cannot ship behind a citation to the old page.
    """
    poh = load_poh()
    limits = re.search(r"VNE (\d+), VNO (\d+), VA (\d+) at 2300 lb, VFE (\d+) \(10 deg\) / (\d+)", poh["airspeed.limits_KIAS"])
    markings = re.search(r"white (\d+)-(\d+), green (\d+)-(\d+), yellow (\d+)-(\d+), red line (\d+)", poh["airspeed.markings_KIAS"])
    fuel = re.search(r"([\d.]+) gal each, (\d+) total, (\d+) usable", poh["fuel.standard_tanks"])
    rpm = re.search(r"(\d+)", poh["engine.max_rpm"])
    unusable = re.search(r"([\d.]+) gal unusable each standard tank \(([\d.]+) long range\)", poh["fuel.unusable_marking"])
    if not (limits and markings and fuel and rpm and unusable):
        raise SystemExit("poh_references.json: the airspeed, fuel or rpm wording changed; update verify_poh()")
    checks = [
        ("VNE", sim["vne"], limits.group(1), "airspeed.limits_KIAS"),
        ("VNO", sim["vno"], limits.group(2), "airspeed.limits_KIAS"),
        ("VA at 2300 lb", sim["va2300"], limits.group(3), "airspeed.limits_KIAS"),
        ("VFE full flap", sim["vfe"], limits.group(5), "airspeed.limits_KIAS"),
        ("white arc start", sim["asiWhite"][0], markings.group(1), "airspeed.markings_KIAS"),
        ("white arc end", sim["asiWhite"][1], markings.group(2), "airspeed.markings_KIAS"),
        ("green arc start", sim["asiGreen"][0], markings.group(3), "airspeed.markings_KIAS"),
        ("green arc end", sim["asiGreen"][1], markings.group(4), "airspeed.markings_KIAS"),
        ("yellow arc start", sim["asiYellow"][0], markings.group(5), "airspeed.markings_KIAS"),
        ("yellow arc end", sim["asiYellow"][1], markings.group(6), "airspeed.markings_KIAS"),
        ("red line", sim["vne"], markings.group(7), "airspeed.markings_KIAS"),
        ("fuel per tank total", sim["fuelPerTankTotal"], fuel.group(1), "fuel.standard_tanks"),
        ("fuel per tank usable", sim["fuelPerTankUsable"], float(fuel.group(3)) / 2, "fuel.standard_tanks"),
        ("unusable fuel per tank", sim["fuelUnusablePerTank"], unusable.group(1), "fuel.unusable_marking"),
        ("maximum rpm", sim["maxRpm"], rpm.group(1), "engine.max_rpm"),
    ]
    for name, drawn, printed, key in checks:
        if float(drawn) != float(printed):
            raise SystemExit("POH binding: %s is %s in sim.js but %s in %s" % (name, drawn, printed, key))


# Drawn engine rows are tied to the POH entry that prints the same numbers; wording (dash style,
# word order) may differ, the numbers may not.
ENGINE_ROWS = {
    "row_engine": "engine.model",
    "row_type": "engine.type",
    "row_rating": "engine.rating",
    "row_max_rpm": "engine.max_rpm",
    "row_static_rpm": "engine.static_rpm_full_throttle",
    "row_propeller": "propeller",
    "row_fuel": "fuel.grade",
}
# Rows whose text is drawn verbatim from the POH must stay verbatim (case and whitespace aside),
# so a digit-free rewrite such as a different propeller manufacturer cannot slip through.
ENGINE_TEXT_ROWS = ("row_engine", "row_type", "row_rating", "row_propeller", "row_fuel")
TANK_ROWS = {"standard": "fuel.standard_tanks", "long_range": "fuel.long_range_tanks"}


def _numbers(value):
    return [float(token.replace(",", "")) for token in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", str(value))]


def _text(value):
    return " ".join(str(value).casefold().split())


def verify_figure_poh(figure_id, data, poh=None):
    """Bind the numbers drawn from a visual's JSON to the POH text, not only to sim.js.

    Covers what verify_poh() cannot see: the long-range tank, the unusable markings and the
    engine/propeller rows and tach bands, which the figures draw straight from their JSON.
    """
    poh = poh or load_poh()
    if figure_id == "fuel-capacity":
        unusable = re.search(r"([\d.]+) gal unusable each standard tank \(([\d.]+) long range\)", poh["fuel.unusable_marking"])
        if not unusable:
            raise SystemExit("poh_references.json: fuel.unusable_marking wording changed; update verify_figure_poh()")
        printed_unusable = {"standard": float(unusable.group(1)), "long_range": float(unusable.group(2))}
        for tank in data["tanks"]:
            printed = _numbers(poh[TANK_ROWS[tank["id"]]])
            for field in ("total_per_tank_gal", "total_gal", "usable_gal"):
                if float(tank[field]) not in printed:
                    raise SystemExit("POH binding: %s %s is %s but %s prints %s" % (tank["id"], field, tank[field], TANK_ROWS[tank["id"]], printed))
            if float(tank["unusable_per_tank_gal"]) != printed_unusable[tank["id"]]:
                raise SystemExit("POH binding: %s unusable is %s but fuel.unusable_marking prints %s" % (tank["id"], tank["unusable_per_tank_gal"], printed_unusable[tank["id"]]))
            if tank["total_gal"] != 2 * tank["total_per_tank_gal"] or tank["usable_gal"] != 2 * tank["usable_per_tank_gal"]:
                raise SystemExit("POH binding: %s tank totals are not twice the per-tank figures" % tank["id"])
    if figure_id == "engine-propeller":
        for row in data["rows"]:
            key = ENGINE_ROWS.get(row["label"])
            if key is None:
                raise SystemExit("POH binding: engine row %s has no POH key" % row["label"])
            if _numbers(row["value"]) != _numbers(poh[key]):
                raise SystemExit("POH binding: %s draws %r but %s prints %r" % (row["label"], row["value"], key, poh[key]))
            if row["label"] in ENGINE_TEXT_ROWS and _text(row["value"]) != _text(poh[key]):
                raise SystemExit("POH binding: %s draws %r but %s prints %r" % (row["label"], row["value"], key, poh[key]))
        bands = [(int(low), int(high)) for low, high in re.findall(r"(\d+)-(\d+)", poh["tach.green"])]
        drawn = [(band["from"], band["to"]) for band in data["tach_bands"]]
        if drawn != bands:
            raise SystemExit("POH binding: tach bands %s do not match tach.green %s" % (drawn, bands))


def v_speeds(data, t, direction, sim):
    right = direction == "rtl"
    lx = W - 90 if right else 90
    cx = lambda kias: scale(kias, [0, 200], [160, 1440])
    parts = []

    parts.append(text(lx, 226, t["scale_label"], anchor="start", size=24, fill=PALETTE["muted"]))
    parts.append(line(160, 250, 1440, 250, stroke=PALETTE["rule"], stroke_width=2))
    for kias in range(0, 201, 20):
        x = cx(kias)
        parts.append(line(x, 244, x, 256, stroke=PALETTE["muted"], stroke_width=2))
        parts.append(text(x, 282, str(kias), anchor="middle", size=18, fill=PALETTE["muted"]))

    colors = {"white": PALETTE["white"], "green": PALETTE["green"], "yellow": PALETTE["yellow"]}
    for index, arc in enumerate(data["arcs"]):
        y = 330 + index * 70
        parts.append(rect(160, y, 1280, 16, fill=PALETTE["track"]))
        band = dict(fill=colors[arc["id"]])
        if arc["id"] == "white":
            band.update(stroke=PALETTE["muted"], stroke_width=1.5)
        parts.append(rect(cx(arc["from"]), y, cx(arc["to"]) - cx(arc["from"]), 16, **band))
        label = "%s · %s" % (t[arc["label"]], "\u2066" + "%d–%d" % (arc["from"], arc["to"]) + "\u2069")
        parts.append(text(lx, y - 10, label, anchor="start", size=21))
        parts.append(
            text(
                (cx(arc["from"]) + cx(arc["to"])) / 2,
                y + 34,
                "\u2066%d–%d\u2069" % (arc["from"], arc["to"]),
                anchor="middle",
                size=16,
                fill=PALETTE["muted"],
            )
        )

    red_x = cx(data["redline"]["value"])
    parts.append(line(red_x, 316, red_x, 486, stroke=PALETTE["red"], stroke_width=4))
    label_x = red_x - 10 if right else red_x + 10
    parts.append(
        text(
            label_x,
            310,
            "%s %s" % (t[data["redline"]["label"]], "\u2066%d\u2069" % data["redline"]["value"]),
            anchor="start",
            size=19,
            fill=PALETTE["red"],
            weight=600,
        )
    )

    card_w = 335
    count = len(data["v_speeds"])
    for index, speed in enumerate(data["v_speeds"]):
        slot = (count - 1 - index) if right else index
        x = 90 + slot * (card_w + 20)
        parts.append(rect(x, 540, card_w, 170, fill=PALETTE["panel"], stroke=PALETTE["rule"], stroke_width=1.5, rx=8))
        parts.append(text(x + card_w / 2, 590, speed["code"], anchor="middle", size=30, weight=700, fill=PALETTE["accent"], letter_spacing=1))
        parts.append(text(x + card_w / 2, 640, "\u2066%s\u2069" % speed["value"], anchor="middle", size=34, weight=600))
        parts.append(text(x + card_w / 2, 668, t["unit"], anchor="middle", size=17, fill=PALETTE["muted"]))
        parts.append(text(x + card_w / 2, 694, t[speed["label"]], anchor="middle", size=17))

    parts.append(text(lx, 780, t["note"], anchor="start", size=19, fill=PALETTE["muted"]))
    return group("".join(parts))


def fuel_capacity(data, t, direction):
    right = direction == "rtl"
    panel_y, panel_h = 180, 480
    base_y = panel_y + panel_h - 60
    max_gal = 27.0
    parts = []

    placements = ((810, data["tanks"][0]), (90, data["tanks"][1])) if right else ((90, data["tanks"][0]), (810, data["tanks"][1]))
    for panel_x, tank in placements:
        parts.append(rect(panel_x, panel_y, 700, panel_h, fill=PALETTE["panel"], stroke=PALETTE["rule"], stroke_width=1.5, rx=10))
        hx = panel_x + (670 if right else 30)
        parts.append(text(hx, panel_y + 46, t[tank["title"]], anchor="start", size=26, weight=600))
        parts.append(text(hx, panel_y + 74, t["per_tank"], anchor="start", size=18, fill=PALETTE["muted"]))

        def gpx(gal):
            return gal / max_gal * 300

        for index, side in enumerate(("left", "right")):
            tx = panel_x + 60 + index * 175
            total_h = gpx(tank["total_per_tank_gal"])
            unusable_h = gpx(tank["unusable_per_tank_gal"])
            top = base_y - total_h
            parts.append(rect(tx, top, 130, total_h, fill=PALETTE["white"], stroke=PALETTE["muted"], stroke_width=2, rx=6))
            parts.append(rect(tx, base_y - unusable_h, 130, unusable_h, fill=PALETTE["red"], opacity=0.85))
            parts.append(rect(tx, top + 1.5, 130, total_h - unusable_h - 3, fill=PALETTE["green"], opacity=0.85, rx=4))
            parts.append(text(tx + 65, base_y + 28, t[side], anchor="middle", size=18, fill=PALETTE["muted"]))
            parts.append(text(tx + 65, top - 12, "%s %s" % (fmt(tank["total_per_tank_gal"], 1), t["gallon"]), anchor="middle", size=17, weight=600))
            parts.append(
                text(
                    tx + 65,
                    top + max(24.0, gpx(tank["usable_per_tank_gal"]) / 2),
                    "%s %s" % (fmt(tank["usable_per_tank_gal"], 0), t["usable"]),
                    anchor="middle",
                    size=16,
                    fill=PALETTE["white"],
                    weight=600,
                )
            )
            parts.append(text(tx + 65, base_y - unusable_h / 2 + 5, fmt(tank["unusable_per_tank_gal"], 1), anchor="middle", size=15, fill=PALETTE["white"], weight=600))

        # Totals column: to the right of the bars in both editions, aligned to the reading start.
        sx = panel_x + (670 if right else 430)
        a = "start"
        parts.append(text(sx, panel_y + 130, t["total"], anchor=a, size=19, fill=PALETTE["muted"]))
        parts.append(text(sx, panel_y + 168, "%d %s" % (tank["total_gal"], t["gallon"]), anchor=a, size=30, weight=600))
        parts.append(text(sx, panel_y + 232, t["usable_total"], anchor=a, size=19, fill=PALETTE["muted"]))
        parts.append(text(sx, panel_y + 270, "%d %s" % (tank["usable_gal"], t["gallon"]), anchor=a, size=30, weight=600, fill=PALETTE["green"]))
        y = panel_y + 330
        for entry in wrap(t["derived"], 30):
            parts.append(text(sx, y, entry, anchor=a, size=15, fill=PALETTE["muted"]))
            y += 20
        y += 6
        for entry in wrap(t["unusable"], 30):
            parts.append(text(sx, y, entry, anchor=a, size=15, fill=PALETTE["red"]))
            y += 20

    parts.append(line(90, 710, 1510, 710, stroke=PALETTE["rule"], stroke_width=1.5))
    parts.append(text(W - 90 if right else 90, 758, t["note"], anchor="start", size=19, fill=PALETTE["muted"]))
    return group("".join(parts))


def alternate_static(data, t, direction, sim):
    right = direction == "rtl"
    x0, x1, y0, y1 = 250, 1440, 200, 620
    domain = [30, 150]
    px = lambda value: scale(value, domain, [x0, x1])
    py = lambda value: scale(value, domain, [y1, y0])
    parts = []

    parts.append(rect(x0, y0, x1 - x0, y1 - y0, fill=PALETTE["white"], stroke=PALETTE["rule"], stroke_width=1.5))
    for value in range(40, 141, 10):
        parts.append(line(px(value), y0, px(value), y1, stroke=PALETTE["track"], stroke_width=1))
        parts.append(line(x0, py(value), x1, py(value), stroke=PALETTE["track"], stroke_width=1))
        parts.append(text(px(value), y1 + 28, str(value), anchor="middle", size=17, fill=PALETTE["muted"]))
        parts.append(text(x0 - 14, py(value) + 5, str(value), anchor="end", size=17, fill=PALETTE["muted"]))

    parts.append(text((x0 + x1) / 2, y1 + 64, t["x_label"], anchor="middle", size=22, direction="ltr"))
    # Axis titles sit in the gap between the header rule (y=168) and the plot frame (y=200).
    parts.append(
        text(
            x1 if right else x0,
            y0 - 8,
            t["y_label"],
            anchor="end" if right else "start",
            size=18,
            fill=PALETTE["muted"],
            direction="ltr",
        )
    )

    parts.append(line(px(domain[0]), py(domain[0]), px(domain[1]), py(domain[1]), stroke=PALETTE["muted"], stroke_width=2, stroke_dasharray="10 8"))
    parts.append(text(px(122) + 12, py(122) - 12, t["series_identity"], size=18, fill=PALETTE["muted"], direction="ltr"))

    points = [(px(indicated), py(corrected)) for indicated, corrected in sim["altStatic"]]
    d = " ".join(("%s%s %s" % ("M" if index == 0 else "L", fmt(x), fmt(y))) for index, (x, y) in enumerate(points))
    parts.append(path(d, fill="none", stroke=PALETTE["accent"], stroke_width=4, stroke_linejoin="round"))
    for indicated, corrected in sim["altStatic"]:
        parts.append(circle(px(indicated), py(corrected), 6, fill=PALETTE["white"], stroke=PALETTE["accent"], stroke_width=3))

    for value in (40, 100, 140):
        pair = next((entry for entry in sim["altStatic"] if entry[0] == value), None)
        if pair:
            if value >= 140:
                parts.append(text(px(value) - 14, py(pair[1]) - 16, "%d → %d" % (value, pair[1]), anchor="end", size=18, fill=PALETTE["accent"], weight=600, direction="ltr"))
            else:
                parts.append(text(px(value) + 10, py(pair[1]) - 16, "%d → %d" % (value, pair[1]), size=18, fill=PALETTE["accent"], weight=600, direction="ltr"))

    parts.append(text(px(45), y0 + 36, t["series_table"], size=19, fill=PALETTE["accent"], weight=600, direction="ltr"))
    parts.append(rect(x0 + 20, y1 + 74, 16, 16, fill=PALETTE["accent"]))
    parts.append(text(x0 + 46, y1 + 88, t["series_table"], size=18, direction="ltr"))
    parts.append(line(x0 + 300, y1 + 82, x0 + 350, y1 + 82, stroke=PALETTE["muted"], stroke_width=2, stroke_dasharray="10 8"))
    parts.append(text(x0 + 362, y1 + 88, t["series_identity"], size=18, direction="ltr"))
    parts.append(text(W - 90 if right else 90, y1 + 128, t["conditions"], anchor="start", size=20, weight=600))
    parts.append(text(W - 90 if right else 90, y1 + 156, t["note"], anchor="start", size=17, fill=PALETTE["muted"]))
    return group("".join(parts))


def engine_propeller(data, t, direction):
    right = direction == "rtl"
    engine_x = 790 if right else 90
    tach_x = 90 if right else 790
    inner = lambda panel_x: panel_x + (670 if right else 30)
    parts = []
    parts.append(rect(engine_x, 200, 700, 600, fill=PALETTE["panel"], stroke=PALETTE["rule"], stroke_width=1.5, rx=10))
    parts.append(text(inner(engine_x), 246, t["row_engine"], anchor="start", size=26, weight=600))

    y = 292
    for row in data["rows"][1:]:
        parts.append(text(inner(engine_x), y, t[row["label"]], anchor="start", size=17, fill=PALETTE["muted"]))
        lines = wrap(row["value"], 62)
        for index, entry in enumerate(lines):
            parts.append(text(inner(engine_x), y + 28 + index * 26, "\u2066%s\u2069" % entry, anchor="start", size=20))
        y += 28 + len(lines) * 26 + 18

    parts.append(rect(tach_x, 200, 700, 600, fill=PALETTE["white"], stroke=PALETTE["rule"], stroke_width=1.5, rx=10))
    parts.append(text(inner(tach_x), 246, t["tach_title"], anchor="start", size=23, weight=600))
    # In the Arabic edition the bars sit on the left of the panel and their labels on the right.
    bx0, bx1 = (tach_x + 40, tach_x + 470) if right else (tach_x + 230, tach_x + 660)
    rpm = lambda value: scale(value, [2000, 2800], [bx0, bx1])
    for index, band in enumerate(data["tach_bands"]):
        by = 330 + index * 110
        parts.append(text(inner(tach_x), by + 5, t[band["label"]], anchor="start", size=19))
        parts.append(rect(bx0, by - 14, bx1 - bx0, 22, fill=PALETTE["track"]))
        parts.append(rect(rpm(band["from"]), by - 14, rpm(band["to"]) - rpm(band["from"]), 22, fill=PALETTE["green"], opacity=0.85))
        parts.append(
            text(
                (rpm(band["from"]) + rpm(band["to"])) / 2,
                by + 32,
                "\u2066%d–%d\u2069 %s" % (band["from"], band["to"], t["rpm"]),
                anchor="middle",
                size=16,
                fill=PALETTE["muted"],
            )
        )
    for value in (2000, 2400, 2800):
        parts.append(line(rpm(value), 300, rpm(value), 640, stroke=PALETTE["rule"], stroke_width=1))
        parts.append(text(rpm(value), 668, str(value), anchor="middle", size=15, fill=PALETTE["muted"]))

    for index, entry in enumerate(wrap(t["note"], 72)):
        parts.append(text(inner(tach_x), 712 + index * 24, entry, anchor="start", size=17, fill=PALETTE["muted"]))
    return group("".join(parts))


DRAW = {
    "v-speeds": lambda data, t, direction, sim: v_speeds(data, t, direction, sim),
    "fuel-capacity": lambda data, t, direction, sim: fuel_capacity(data, t, direction),
    "alternate-static": alternate_static,
    "engine-propeller": lambda data, t, direction, sim: engine_propeller(data, t, direction),
}


def header(figure, t, lang, direction):
    right = direction == "rtl"
    aircraft_x = W - 90 if right else 90
    tag_x = 90 if right else W - 90
    text_dir = "rtl" if right else "ltr"
    title = figure["title"][lang]
    if right:
        title = isolate_numbers(title)
    # Disclosure band above the plot, in the edition's language: study-only and independence from
    # GACA come before any operational claim, not only in the footer.
    parts = [
        rect(90, 16, W - 180, 34, fill="#FEF3F2", stroke="#EFC5C0", stroke_width=1, rx=6),
        text(aircraft_x, 39, t["band"], anchor="start", size=14, fill=PALETTE["red"], weight=600, direction=text_dir),
        text(aircraft_x, 80, t["aircraft"], anchor="start", size=18, fill=PALETTE["muted"]),
        text(tag_x, 80, t["tier_free"] if figure["tier"] == "free" else t["tier_premium"], anchor="end", size=16, fill=PALETTE["accent"], weight=600),
        text(aircraft_x, 146, title, anchor="start", size=40, weight=600),
        line(90, 176, W - 90, 176, stroke=PALETTE["rule"], stroke_width=2),
    ]
    return "".join(parts)


def footer(figure, t, lang, direction, manifest):
    parts = [line(90, 818, W - 90, 818, stroke=PALETTE["rule"], stroke_width=1.5)]

    # English block on the left, Arabic block on the right, in both editions.
    y = 843
    for entry in wrap(manifest["non_affiliation"]["en"], 140):
        parts.append(text(90, y, entry, anchor="start", size=14, fill=PALETTE["muted"], direction="ltr"))
        y += 18
    y += 6
    for entry in wrap(manifest["non_affiliation"]["ar"], 130):
        parts.append(text(W - 90, y, entry, anchor="start", size=14, fill=PALETTE["muted"], direction="rtl"))
        y += 18
    y += 6

    sources = "; ".join("POH p.%s — %s" % (source["page"], source["what_" + lang]) for source in figure["sources"])
    if direction == "rtl":
        sources = isolate_numbers(sources)
        x, text_dir = W - 90, "rtl"
    else:
        x, text_dir = 90, "ltr"
    for entry in wrap("%s: %s" % (t["sources"], sources), 150):
        parts.append(text(x, y, entry, anchor="start", size=14, fill=PALETTE["muted"], direction=text_dir))
        y += 18
    y += 8

    parts.append(text((90 + W - 90) / 2, y, "%s · %s" % (t["disclaimer"], t["status"]), anchor="middle", size=15))
    return "".join(parts)


def build(out_root):
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    sim = load_sim()
    verify_poh(sim)
    poh = load_poh()
    written = []
    for figure in manifest["visuals"]:
        data = json.loads((HERE / "visuals" / figure["data"]).read_text(encoding="utf-8"))
        verify_figure_poh(figure["id"], data, poh)
        draw = DRAW[figure["id"]]
        for lang in manifest["languages"]:
            direction = "rtl" if lang == "ar" else "ltr"
            t = dict(manifest["strings"][lang])
            t.update(data["strings"][lang])
            if direction == "rtl":
                t = {key: isolate_numbers(value) for key, value in t.items()}
            body = header(figure, t, lang, direction) + draw(data, t, direction, sim) + footer(figure, t, lang, direction, manifest)
            svg = document(lang, direction, figure["title"][lang], body)
            target = out_root / lang / ("%s.svg" % figure["id"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8")
            written.append(str(target.relative_to(out_root)))
    return sorted(written)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "out")
    args = parser.parse_args(argv)
    for entry in build(args.out.resolve()):
        print(entry)


if __name__ == "__main__":
    sys.exit(main())
