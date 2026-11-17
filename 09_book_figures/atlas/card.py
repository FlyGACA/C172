"""The cards of the aerodrome atlas: one picture for each aerodrome, with what its entry AD 2 in AIP-KSA prints.

A card has a head (the location indicator and the name as the AIP prints them), a map and four blocks. Every block carries the number of the section it is taken from:
    the map       an open satellite picture (Copernicus Sentinel-2, data/open/<icao>_s2.jpg), true north up and to scale, with the runways between the thresholds of AD 2.12,
                  their designators and the aerodrome reference point of AD 2.2
    AD 2.2        the elevation, the reference temperature and the magnetic variation, as printed
    AD 2.12/2.13  for each runway its dimensions and its declared distances TORA and LDA
    AD 2.17       the ATS airspace of the aerodrome: its outline to scale with the runways in it, its name, class, vertical limits and hours
    AD 2.18       the VHF frequencies of the tower, the approach, the ground control and the ATIS (those between 117.975 and 137 MHz)
The values are those of data/atlas_facts.json (AIRAC AIP AMDT 11/26; data/build_atlas_facts.py checks each against the official page); a value the page of that amendment does not
print is left out. Letters: location indicators, section numbers, ICAO abbreviations and numbers with their units. Not for navigation.

    python3 card.py ICAO [ICAO ...]     -> cache/<icao>.svg        then        node rasterize_cards.mjs        -> out/card-<icao>.jpg
"""
import base64
import io

import numpy as np
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "handbook"))
from figs import h_b2 as H          # noqa: E402
from figs import h_b4 as B          # noqa: E402
from figs import imagery_real as IR  # noqa: E402
from figs import scene as S         # noqa: E402
from PIL import Image               # noqa: E402

IR.OPEN = os.path.join(HERE, "data", "open")           # the atlas keeps its own pictures and its own cache
IR.RENDERS = os.path.join(HERE, "cache")
n = S.n
W, HT = 640, 400
U = "ac"
INK = H.INK
AD, AD_HI = "#BE185D", "#DB2777"                        # the colour of Part 3 of the AIP, as in Figure 4-1 of the handbook
SLATE = "#475569"
with open(os.path.join(HERE, "data", "atlas_facts.json"), encoding="utf-8") as _f:
    FACTS = json.load(_f)
BY = {a["icao"]: a for a in FACTS["aerodromes"]}
MX, MY, MW, MH = 10.0, 44.0, 388.0, 346.0              # the map
PX, PW = 408.0, 222.0                                  # the blocks beside it


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def tag(code, x, y, anchor="start", h=11.0, size=5.3):
    w = gwidth(code, size) + 10.0
    x0 = x if anchor == "start" else x - w if anchor == "end" else x - w / 2
    return (f'<rect x="{n(x0)}" y="{n(y - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{AD}" stroke="#FFFFFF" stroke-width="1.0" filter="url(#{U}ds)"/>'
            + H.glyph_text(code, x0 + w / 2, y, size, "#FFFFFF", spacing=0.3))


def txt(x, y, s, size=7.0, anchor="start", colour=INK, weight="bold"):
    return B.label(x, y, s, size, anchor, colour=colour, weight=weight, halo=False)


def num(v):
    """A number as the book writes one: 3350 -> 3 350, 6858.0 -> 6 858, 34.7 -> 34.7."""
    if v is None:
        return "NIL"
    if float(v) == int(v):
        s = f"{int(v):,}".replace(",", " ") if int(v) >= 10000 else (f"{int(v) // 1000} {int(v) % 1000:03d}" if int(v) >= 1000 else str(int(v)))
        return s
    return f"{v:g}"


def frame_for(a):
    """The map frame of an aerodrome: the middle of its thresholds in the middle of the window, as large as the runways and the picture allow."""
    th = [(r["threshold"]["lon"], r["threshold"]["lat"]) for r in a["runways"] if r.get("threshold")]
    lon0, lat0 = sum(p[0] for p in th) / len(th), sum(p[1] for p in th) / len(th)
    k = 60.0 * math.cos(math.radians(lat0))
    half_e = max(abs(p[0] - lon0) * k for p in th) + 0.9
    half_n = max(abs(p[1] - lat0) * 60.0 for p in th) + 0.9
    scale = min(MW / 2 / half_e, MH / 2 / half_n)
    scale = max(scale, MW / (15.4 / 1.852), MH / (10.4 / 1.852))           # the picture is 16 km by 11 km: the window may not show more than it has
    local = H.Frame(lat0, lon0, scale, MW / 2, MH / 2)
    return local, H.Frame(lat0, lon0, scale, MX + MW / 2, MY + MH / 2), scale


TONE_LO, TONE_HI, TONE_GAIN, TONE_CHROMA = 104.0, 224.0, (0.8, 3.2), 46.0


def tone(path):
    """The same range of lightness for the ground of every card. Each picture has its own stretch (see data/fetch_atlas_open.py), so pale sand comes out washed and dark lava heavy; here the lightness of
    the window (5th to 95th percentile) is brought to one range by one gain for the three bands, and where the colour is very strong (red dunes) it is drawn in until its mean is TONE_CHROMA."""
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    grey = rgb.mean(axis=2)
    lo, hi = np.percentile(grey, (5.0, 95.0))
    gain = min(max((TONE_HI - TONE_LO) / max(hi - lo, 1.0), TONE_GAIN[0]), TONE_GAIN[1])
    mid = (lo + hi) / 2.0
    rgb = (rgb - mid) * gain + (TONE_LO + TONE_HI) / 2.0
    grey = rgb.mean(axis=2, keepdims=True)
    chroma = float((rgb.max(axis=2) - rgb.min(axis=2)).mean())
    if chroma > TONE_CHROMA:
        rgb = grey + (rgb - grey) * (TONE_CHROMA / chroma)
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(path)


def ground(a, local):
    name = f"ground-{a['icao'].lower()}"
    path = os.path.join(IR.RENDERS, name + ".png")
    if os.path.exists(path):
        os.remove(path)
    picture = a["icao"].lower() + "_s2"
    assert IR.covers(local, (MW, MH), picture=picture), f"{a['icao']}: the picture does not cover the map"
    IR.ensure(name, local, (MW, MH), px_per_unit=4, veil=0.10, saturation=0.92, lift=1.0, picture=picture)
    tone(path)
    buf = io.BytesIO()
    Image.open(path).convert("RGB").save(buf, "JPEG", quality=90, subsampling=0)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return (f'<clipPath id="{U}map"><rect x="{n(MX)}" y="{n(MY)}" width="{n(MW)}" height="{n(MH)}" rx="8"/></clipPath>'
            f'<g clip-path="url(#{U}map)"><image x="{n(MX)}" y="{n(MY)}" width="{n(MW)}" height="{n(MH)}" preserveAspectRatio="none" href="data:image/jpeg;base64,{b64}"/>')


def pairs(a):
    """The runways as strips: [(designator, threshold, designator, threshold, record of the first)]."""
    out, used = [], set()
    rws = [r for r in a["runways"] if r.get("threshold")]
    for r in rws:
        if r["id"] in used:
            continue
        num_ = int(r["id"][:2])
        side = {"L": "R", "R": "L", "C": "C"}.get(r["id"][2:], "")
        other = next((q for q in rws if q["id"] == f"{(num_ + 17) % 36 + 1:02d}{side}"), None)
        if other:
            used.update((r["id"], other["id"]))
            out.append((r, other))
    return out


def runway_layer(a, F):
    out = []
    for r, q in pairs(a):
        p0, p1 = F.xy(r["threshold"]["lon"], r["threshold"]["lat"]), F.xy(q["threshold"]["lon"], q["threshold"]["lat"])
        out.append(f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="1.1" stroke-dasharray="5 3"/>')
        d = H.dist(p0, p1)
        ux, uy = (p1[0] - p0[0]) / d, (p1[1] - p0[1]) / d
        for (p, rec, sg) in ((p0, r, -1), (p1, q, 1)):
            c = (p[0] + sg * ux * 11.0, p[1] + sg * uy * 11.0)
            w = gwidth(rec["id"], 5.4) + 8.0
            out.append(f'<rect x="{n(c[0] - w / 2)}" y="{n(c[1] - 6.0)}" width="{n(w)}" height="12" rx="3" fill="{INK}" stroke="#FFFFFF" stroke-width="1.0" filter="url(#{U}ds)"/>' + H.glyph_text(rec["id"], c[0], c[1], 5.4, "#FFFFFF", spacing=0.3))
            out.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="2.0" fill="#FFFFFF" stroke="{INK}" stroke-width="0.9"/>')
    arp = F.xy(a["lon"], a["lat"])
    out.append(f'<circle cx="{n(arp[0])}" cy="{n(arp[1])}" r="4.2" fill="none" stroke="#FFFFFF" stroke-width="2.6"/><circle cx="{n(arp[0])}" cy="{n(arp[1])}" r="4.2" fill="none" stroke="{AD}" stroke-width="1.3"/>'
               f'<circle cx="{n(arp[0])}" cy="{n(arp[1])}" r="1.2" fill="{AD}"/>')
    return "".join(out)


def scale_bar(scale):
    nm = 1 if scale > 34 else 2
    length = nm * scale
    x, y = MX + 14.0, MY + MH - 14.0
    return (f'<rect x="{n(x - 6)}" y="{n(y - 12)}" width="{n(length + 12)}" height="18" rx="5" fill="#FFFFFF" fill-opacity="0.86"/>'
            f'<path d="M {n(x)},{n(y - 2.4)} L {n(x)},{n(y + 1.4)} L {n(x + length)},{n(y + 1.4)} L {n(x + length)},{n(y - 2.4)}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>'
            + H.glyph_text(f"{nm} NM", x + length / 2, y - 6.0, 4.8, INK, spacing=0.3))


def head(a):
    return (f'<rect x="0" y="0" width="{W}" height="34" fill="url(#{U}hd)"/>'
            + H.glyph_text(a["icao"], 14.0, 17.5, 12.5, "#FFFFFF", anchor="start", spacing=1.0)
            + H.glyph_text(a["name"].upper().replace(" - ", " / "), 78.0, 17.5, 6.6, "#FFFFFF", anchor="start", spacing=0.5, opacity=0.95)
            + H.glyph_text("AIP AD 2 · AMDT 11/26", W - 14.0, 17.5, 5.0, "#FFFFFF", anchor="end", spacing=0.4, opacity=0.9))


def block(y, h):
    return f'<rect x="{n(PX)}" y="{n(y)}" width="{n(PW)}" height="{n(h)}" rx="8" fill="#FFFCF5" stroke="{AD}" stroke-opacity="0.35" stroke-width="0.9" filter="url(#{U}cs)"/>'


def block_22(a, y):
    out = [block(y, 46.0), tag("AD 2.2", PX + 8.0, y + 12.0)]
    temp = f"{a['ref_temp_c']:g} °C" if a["ref_temp_c"] is not None else "NIL"
    out.append(txt(PX + 62.0, y + 15.0, f"{num(a['elev_ft'])} ft", 9.0) + txt(PX + PW - 10.0, y + 15.0, temp, 9.0, "end", colour="#B45309"))
    var = a["mag_var_printed"].split("/")[0].strip()
    out.append(txt(PX + 10.0, y + 35.0, f"VAR {var}", 6.6, colour=SLATE) + txt(PX + PW - 10.0, y + 35.0, a["traffic"], 6.6, "end", colour=SLATE))
    return "".join(out)


def block_runways(a, y):
    rws = [r for r in a["runways"] if r.get("dims_in_amdt_11_26")]
    h = 30.0 + 13.0 * len(rws)
    out = [block(y, h), tag("AD 2.12", PX + 8.0, y + 12.0), tag("AD 2.13", PX + 54.0, y + 12.0)]
    cols = (PX + 14.0, PX + 92.0, PX + 150.0, PX + PW - 12.0)
    out.append(H.glyph_text("TORA", cols[2], y + 12.0, 4.4, SLATE, anchor="end", spacing=0.3) + H.glyph_text("LDA", cols[3], y + 12.0, 4.4, SLATE, anchor="end", spacing=0.3))
    for i, r in enumerate(rws):
        yy = y + 30.0 + 13.0 * i
        d = r.get("declared_m") or {}
        out.append(txt(cols[0], yy, r["id"], 7.4) + txt(cols[1], yy, f"{num(r['length_m'])} × {r['width_m']} m", 6.8, "end", colour=SLATE)
                   + txt(cols[2], yy, num(d.get("TORA")) if d.get("TORA") else "–", 6.8, "end") + txt(cols[3], yy, num(d.get("LDA")) if d.get("LDA") else "–", 6.8, "end"))
    return "".join(out), h


def block_airspace(a, y, h):
    out = [block(y, h), tag("AD 2.17", PX + 8.0, y + 12.0)]
    zones = [z for z in a["airspace"] if z.get("in_amdt_11_26")]
    if not zones:
        return "".join(out) + txt(PX + 62.0, y + 15.0, "NIL", 8.0, colour=SLATE)
    z = zones[0]
    cls = z["class"] if z["class"] in H.COL else None
    colour = H.COL.get(z["class"], SLATE)
    ring = z["geometry"]["coordinates"][0] if z["geometry"]["type"] == "Polygon" else z["geometry"]["coordinates"][0][0]
    lon0, lat0 = a["lon"], a["lat"]
    k = 60.0 * math.cos(math.radians(lat0))
    pts = [((lo - lon0) * k, (la - lat0) * 60.0) for lo, la in ring]
    ext = max(max(abs(p[0]) for p in pts), max(abs(p[1]) for p in pts))
    box = min(h - 38.0, 74.0)
    s = box / 2 / ext
    cx, cy = PX + 12.0 + box / 2, y + 22.0 + box / 2
    poly = S.pts([(cx + e * s, cy - nn * s) for e, nn in pts])
    out.append(f'<polygon points="{poly}" fill="{colour}" fill-opacity="0.16" stroke="#FFFFFF" stroke-width="2.6" stroke-linejoin="round"/><polygon points="{poly}" fill="none" stroke="{colour}" stroke-width="1.2" stroke-dasharray="5 3" stroke-linejoin="round"/>')
    for r, q in pairs(a):
        p0 = (cx + (r["threshold"]["lon"] - lon0) * k * s, cy - (r["threshold"]["lat"] - lat0) * 60.0 * s)
        p1 = (cx + (q["threshold"]["lon"] - lon0) * k * s, cy - (q["threshold"]["lat"] - lat0) * 60.0 * s)
        out.append(f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{INK}" stroke-width="1.6"/>')
    bar = 5 * s                                                             # five nautical miles at the scale of the outline
    out.append(f'<path d="M {n(cx - bar / 2)},{n(y + h - 9.0)} L {n(cx - bar / 2)},{n(y + h - 6.5)} L {n(cx + bar / 2)},{n(y + h - 6.5)} L {n(cx + bar / 2)},{n(y + h - 9.0)}" fill="none" stroke="{SLATE}" stroke-width="0.9"/>'
               + H.glyph_text("5 NM", cx + bar / 2 + 4.0, y + h - 8.0, 4.0, SLATE, anchor="start", spacing=0.3))
    tx = PX + 12.0 + box + 12.0
    out.append(txt(tx, y + 34.0, z["name"], 6.6))
    if cls:
        out.append(H.class_disc(U, tx + 7.0, y + 49.0, cls, 6.6) + txt(tx + 18.0, y + 51.5, "CLASS " + cls, 6.2, colour=colour))
    else:
        out.append(txt(tx, y + 51.5, "CLASS " + str(z["class"]), 6.2, colour=SLATE))
    out.append(txt(tx, y + 66.0, f"{z['lower']} – {z['upper'].replace(' FT AMSL', ' ft')}", 6.4, colour=SLATE))
    out.append(txt(tx, y + 79.0, str(z["hours"])[:22], 6.2, colour=SLATE))
    return "".join(out)


ORDER = ["TWR", "AFIS", "ATS", "RADIO", "APP", "SMC", "SMGCS", "ATIS", "TIBA"]         # the service designations the pages print, in the order a pilot arriving needs them


def block_comms(a, y, h):
    """For each call sign of AD 2.18 its first VHF frequency (117.975 to 137 MHz, the emergency frequency left out), and how many more it has. Where the block has no room for every call sign, a service is shown as one row."""
    out = [block(y, h), tag("AD 2.18", PX + 8.0, y + 12.0)]
    groups = {}
    for c in a["comms"]:
        if c["service"] in ORDER and 117.975 <= c["mhz"] <= 137.0 and c["mhz"] != 121.5:
            groups.setdefault((ORDER.index(c["service"]), c["service"], c["callsign"]), []).append(c)
    fit = max(int((h - 26.0) / 9.6), 3)                 # rows the block has room for
    while len(groups) > fit:                            # too many call signs: the service with the most of them becomes one row, under the call sign printed first
        counts = {}
        for k in groups:
            counts[k[0]] = counts.get(k[0], 0) + 1
        worst = max(counts, key=lambda i: (counts[i], i))
        if counts[worst] == 1:
            break
        keys = [k for k in groups if k[0] == worst]     # dicts keep the order of the page
        groups[keys[0]] = [c for k in keys for c in groups[k]]
        for k in keys[1:]:
            del groups[k]
    rows = [groups[k] for k in sorted(groups, key=lambda k: k[0])][:fit]
    step = min(13.0, (h - 26.0) / max(len(rows), 1))
    for i, g in enumerate(rows):
        yy = y + 30.0 + step * i
        c = g[0]
        more = f"+{len(g) - 1}" if len(g) > 1 else ""
        out.append(txt(PX + 14.0, yy, c["service"], 6.8 if len(c["service"]) < 5 else 5.8, colour=AD) + txt(PX + 50.0, yy, c["callsign"][:24], 6.0, colour=SLATE, weight="normal")
                   + txt(PX + PW - 26.0, yy, f"{c['mhz']:.3f}", 7.4, "end") + txt(PX + PW - 10.0, yy, more, 5.6, "end", colour=SLATE))
    if not rows:
        out.append(txt(PX + 62.0, y + 15.0, "NIL", 8.0, colour=SLATE))
    return "".join(out)


def card(icao):
    a = BY[icao]
    local, F, scale = frame_for(a)
    defs = (H.defs(U, W, HT) + f'<defs>{S.gradient(U + "bg", [(0, "#F4EFE3"), (1, "#E9E0CB")])}'
            f'<linearGradient id="{U}hd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AD}"/><stop offset="1" stop-color="{AD_HI}"/></linearGradient>'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.2" flood-color="#3B2A12" flood-opacity="0.22"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>')
    body = [defs, head(a), ground(a, local), runway_layer(a, F), "</g>",
            f'<rect x="{n(MX)}" y="{n(MY)}" width="{n(MW)}" height="{n(MH)}" rx="8" fill="none" stroke="#FFFFFF" stroke-width="2.4"/><rect x="{n(MX)}" y="{n(MY)}" width="{n(MW)}" height="{n(MH)}" rx="8" fill="none" stroke="{AD}" stroke-width="1.0"/>',
            scale_bar(scale), H.north_arrow(U, MX + MW - 16.0, MY + 28.0, 22.0)]
    y = MY
    body.append(block_22(a, y)); y += 52.0
    rw, h = block_runways(a, y)
    body.append(rw); y += h + 6.0
    rest = MY + MH - y
    h_air = max(min(rest * 0.56, 112.0), 92.0)
    body.append(block_airspace(a, y, h_air)); y += h_air + 6.0
    body.append(block_comms(a, y, MY + MH - y))
    title = f"{a['icao']} {a['name']}: what AIP AD 2 prints, on an open satellite picture"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {HT}" width="{W}" height="{HT}" data-px-per-unit="3">'
            f"<title>{title}</title><desc>{title}. Values of AIRAC AIP AMDT 11/26. Contains modified Copernicus Sentinel data 2026. Not for navigation.</desc>" + "".join(body) + "</svg>")


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "cache"), exist_ok=True)
    for icao in sys.argv[1:] or sorted(BY):
        if not os.path.exists(os.path.join(IR.OPEN, icao.lower() + "_s2.json")):
            print("skipped", icao, "(no picture)")
            continue
        with open(os.path.join(HERE, "cache", icao.lower() + ".svg"), "w", encoding="utf-8") as f:
            f.write(card(icao))
        print("drew", icao)
