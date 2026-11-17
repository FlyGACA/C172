"""Check the projection note of the AIP's 1:500 000 chart against the sheets themselves, and write data/chart_cone_check.json.

Every sheet of the AIP's two visual chart series prints "Lambert Conformal Conic Projection / Standard Paralleles 25°20' and 30°40'" in its margin (AIP ENR 6; GEN 3.2 says the
standard parallels are "indicated on chart"). On a conformal conic the meridians are straight lines that close by n degrees for each degree of longitude, n being fixed by the two
standard parallels: 0.4696 for these two. This script measures that on the sheets: it renders a sheet at 200 dpi, follows the thin black lines of its graticule down and across the
map, and takes
    the lean of each meridian against the page, and from the change of lean with longitude the constant n of the sheet;
    the spacing of the parallels down the middle of the map, which is the sheet's scale along the meridian (pixels to the degree of latitude).
Six sheets, from 16 N to 32 N and from 36 E to 57 E. What it found on 2026-11-17 (the PDFs of AMDT 10/26 and 11/26): n between 0.464 and 0.473 on all six, so the whole series is
drawn on one cone, the one the margin names. The scale of the six sheets differs by up to 0.8 % (least on the Riyadh sheet), which the cone alone does not explain: on one cone at
one stated scale the sheets from 16 to 18 N would be 1.7 % larger than the Riyadh sheet, and those from 30 to 32 N the same as it. So the book says nothing about how the scale of
the printed sheets changes over the Kingdom, only what holds on any sheet: measure a distance against the minutes of latitude beside it.

Needs numpy, pillow, pdftoppm (poppler) and the chart PDFs of the saudi-airspace repository (data/raw/charts/icao-500k, not in git there).
    python3 check_chart_cone.py [/path/to/saudi-airspace] [folder for the rendered pages]
"""
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/saudi-airspace"
WORK = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="chart-cone-")
SHEETS = (("2446-A", 36, 30), ("2547-A", 48, 26), ("2546-C", 45, 24), ("2563-A", 54, 22), ("2566-C", 39, 20), ("2668-C", 45, 16))      # sheet, its west meridian, its south parallel (3 degrees by 2)
PRINTED = (25 + 20 / 60, 30 + 40 / 60)
STRIP = 16
F_WGS = 1 / 298.257223563                              # the flattening of the WGS 84 ellipsoid
E_WGS = math.sqrt(F_WGS * (2 - F_WGS))


def cone_constant(lat1, lat2):
    m = lambda p: math.cos(p) / math.sqrt(1 - (E_WGS * math.sin(p)) ** 2)
    t = lambda p: math.tan(math.pi / 4 - p / 2) / ((1 - E_WGS * math.sin(p)) / (1 + E_WGS * math.sin(p))) ** (E_WGS / 2)
    p1, p2 = math.radians(lat1), math.radians(lat2)
    return (math.log(m(p1)) - math.log(m(p2))) / (math.log(t(p1)) - math.log(t(p2)))


def cone_scale(lat, lat1=PRINTED[0], lat2=PRINTED[1]):
    m = lambda p: math.cos(p) / math.sqrt(1 - (E_WGS * math.sin(p)) ** 2)
    t = lambda p: math.tan(math.pi / 4 - p / 2) / ((1 - E_WGS * math.sin(p)) / (1 + E_WGS * math.sin(p))) ** (E_WGS / 2)
    n = cone_constant(lat1, lat2)
    big_f = m(math.radians(lat1)) / (n * t(math.radians(lat1)) ** n)
    return big_f * t(math.radians(lat)) ** n * n / m(math.radians(lat))


def follow(dark, y_start, direction):
    """Every thin dark line that runs down the page through the strip at y_start, followed up (-1) or down (+1): arrays of (y, x)."""
    height, width = dark.shape
    strip = dark[y_start:y_start + STRIP]
    frac = strip.mean(axis=0)
    cols = [x for x in range(3, width - 3) if frac[x] >= 0.85 and frac[x] >= frac[x - 1] and frac[x] > frac[x + 1]]
    cols = [x for x in cols if dark[y_start:y_start + STRIP, x - 4:x + 5].mean() < 0.6]              # thin: not a thick frame line or a filled area
    found = []
    for x0 in cols:
        pts, x, slope, miss, y = [(y_start + STRIP / 2, float(x0))], float(x0), 0.0, 0, y_start
        while 0 < y + direction * STRIP < height - STRIP and miss < 12:
            y += direction * STRIP
            px = x + slope * direction * STRIP
            lo = int(round(px)) - 4
            win = dark[y:y + STRIP, lo:lo + 9].mean(axis=0)
            k = int(np.argmax(win))
            if win[k] < 0.8:
                miss, x = miss + 1, px
                continue
            w = win[max(0, k - 1):k + 2]
            x = lo + max(0, k - 1) + float((w * np.arange(len(w))).sum() / w.sum())
            pts.append((y + STRIP / 2, x))
            miss = 0
            if len(pts) >= 6:
                p = np.array(pts[-12:])
                slope = float(np.polyfit(p[:, 0], p[:, 1], 1)[0])
        found.append(np.array(pts))
    return found


def long_lines(dark, lo=0.30, hi=0.72, least=0.55):
    """The lines that run through most of the page: the start strip that finds the most of them wins."""
    height = dark.shape[0]
    best = []
    for y_start in range(int(height * lo), int(height * hi), 97):
        tracks = [np.vstack([u[::-1], d[1:]]) for u, d in zip(follow(dark, y_start, -1), follow(dark, y_start, +1))]
        tracks = [t for t in tracks if t[:, 0].max() - t[:, 0].min() > least * height]
        if len(tracks) > len(best):
            best = tracks
    return best


def fitted(track, degree):
    for _ in range(3):
        c = np.polyfit(track[:, 0], track[:, 1], degree)
        r = track[:, 1] - np.polyval(c, track[:, 0])
        track = track[np.abs(r) < max(0.7, 2.5 * r.std())]
    c = np.polyfit(track[:, 0], track[:, 1], degree)
    return c, float((track[:, 1] - np.polyval(c, track[:, 0])).std())


def meridians(dark, lon_w):
    height = dark.shape[0]
    rows = []
    for t in long_lines(dark):
        (b, c), res = fitted(t, 1)
        rows.append((b * height / 2 + c, math.degrees(math.atan(b)), res))
    rows.sort()
    grat = [r for r in rows if not (abs(r[1]) < 0.004 and r[2] < 0.12)]                               # the frame lines of the page stand exactly upright and are ruler-straight
    xs, lean = np.array([r[0] for r in grat]), np.array([r[1] for r in grat])
    best = None
    for first in (lon_w, lon_w + 0.25, lon_w + 0.5):                                                  # the outermost lines found are the sheet's edge meridians, or a quarter or a half inside them
        for last in (lon_w + 3, lon_w + 2.75, lon_w + 2.5):
            unit = (xs[-1] - xs[0]) / (last - first)
            lon = first + (xs - xs[0]) / unit
            off = float((np.abs(lon / 0.25 - np.round(lon / 0.25)) * 0.25).max())
            if best is None or off < best[0] - 1e-6:
                best = (off, unit, lon)
    off, unit, lon = best
    assert off < 0.02, f"the lines found do not sit on quarters of a degree (worst {off:.3f})"
    slope, icpt = np.polyfit(lon, lean, 1)
    return {"meridians_found": len(grat), "n_measured": round(abs(float(slope)), 4), "worst_misfit_deg": round(float(np.abs(lean - (slope * lon + icpt)).max()), 4),
            "upright_meridian_e": round(float(-icpt / slope), 2), "px_per_degree_of_longitude_mid_page": round(float(unit), 1)}


def parallels(dark):
    turned = dark.T                                                                                   # a parallel now runs "down" the page
    mid = turned.shape[0] / 2 + 475.0                                                                 # the middle of the map frame, which lies right of the middle of the page
    rows = []
    for t in long_lines(turned, 0.35, 0.70, 0.5):
        c, res = fitted(t, 2)
        rows.append((float(np.polyval(c, mid)), abs(float(c[0])) * 2387.0 ** 2))
    rows.sort()
    ys = np.array([r[0] for r in rows if r[1] > 3.0])                                                 # the frame lines are straight; a parallel bows by several pixels over the frame
    ys = ys[np.concatenate([[True], np.diff(ys) > 5.0])]
    gaps = np.diff(ys)
    base = float(np.median(gaps[gaps < 1.3 * gaps.min()]))                                            # one step of the graticule: a quarter or a half of a degree
    mult = np.round(gaps / base)
    good = (mult >= 1) & (np.abs(gaps - mult * base) < 0.012 * base * np.maximum(mult, 1))            # a gap that is not a whole number of steps has a line in it that is not a parallel
    step = float(gaps[good].sum() / mult[good].sum())
    per_degree = step / 0.25 if step < 600 else step / 0.5
    return {"parallel_gaps_used": int(good.sum()), "px_per_degree_of_latitude": round(per_degree, 1)}


def main():
    n_printed = cone_constant(*PRINTED)
    out = {"what": "the convergence of the meridians and the spacing of the parallels measured on six sheets of the AIP's 1:500 000 chart, rendered at 200 dpi (data/check_chart_cone.py)",
           "measured": "2026-11-17", "printed_standard_parallels": ["25°20'", "30°40'"], "n_of_the_printed_parallels": round(n_printed, 4), "sheets": []}
    for sheet, lon_w, lat_s in SHEETS:
        pdf = os.path.join(SRC, "data", "raw", "charts", "icao-500k", f"icao-500k_{sheet}.pdf")
        page = os.path.join(WORK, f"sheet_{sheet}")
        if not os.path.exists(page + "-1.pgm"):
            subprocess.run(["pdftoppm", "-r", "200", "-gray", pdf, page], check=True)
        dark = np.asarray(Image.open(page + "-1.pgm").convert("L")) < 110
        row = {"sheet": sheet, "west_e": lon_w, "south_n": lat_s, **meridians(dark, lon_w), **parallels(dark)}
        out["sheets"].append(row)
        print(row, flush=True)
    ref = next(s for s in out["sheets"] if s["sheet"] == "2546-C")
    for s in out["sheets"]:
        mid = s["south_n"] + 1.0
        s["scale_against_2546_C_measured"] = round(s["px_per_degree_of_latitude"] / ref["px_per_degree_of_latitude"], 4)
        s["scale_against_2546_C_on_the_printed_cone"] = round(cone_scale(mid) / cone_scale(25.0), 4)
    ns = [s["n_measured"] for s in out["sheets"]]
    out["result"] = (f"n measured on the six sheets: {min(ns):.3f} to {max(ns):.3f}; the printed standard parallels give {n_printed:.4f}. "
                     "The sheets' scales differ from sheet to sheet in a way the cone alone does not explain (compare the two scale columns), so nothing is said about the scale of the printed sheets.")
    with open(os.path.join(HERE, "chart_cone_check.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(out["result"])


if __name__ == "__main__":
    main()
