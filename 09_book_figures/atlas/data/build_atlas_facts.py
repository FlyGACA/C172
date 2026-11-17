"""Build atlas_facts.json: what the cards of the aerodrome atlas print, for the civil aerodromes of AIP-KSA (those AD 1.3 lists with scheduled traffic, and Thumamah).

Sources, in this order of trust:
  1. the official AD 2 page of each aerodrome, AIRAC AIP AMDT 11/26 (effective 2026-10-29), saved as <pages>/<ICAO>.html: AD 2.2 (reference point, elevation, reference temperature,
     magnetic variation) is read from it here, and every other value a card prints is looked for in its text (the count of values found and not found is kept for each aerodrome);
  2. the saudi-airspace repository (data/structured/aerodromes.json and airport_airspace.geojson) for the structure: runways with thresholds and declared distances and the ATS
     airspace of AD 2.17 with its outline. The frequencies of AD 2.18 are read from the page's own table (ad_table.py). That repository was built from the AMDT 12/26 pages, so a value of its that the AMDT 11/26 page does not
     print is flagged "not_in_amdt_11_26" and the card does not print it.
Values are kept as printed. Not for navigation.
    python3 build_atlas_facts.py /path/to/saudi-airspace /path/to/pages
"""
import hashlib
import html
import json
import os
import re
import sys

SRC, PAGES = sys.argv[1:3]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ad_table import table  # noqa: E402


def comms_of(path):
    """AD 2.18 as the page prints it: one record for each frequency, with the service designation and the call sign carried down the rows they span."""
    rows = table(path, "AD2_18_TABLE")[2:]
    hold = {}                                            # column -> [rows left, lines]
    out = []
    for row in rows:
        cells, k = {}, 0
        it = iter(row)
        for col in range(7):
            if col in hold and hold[col][0] > 0:
                hold[col][0] -= 1
                cells[col] = hold[col][1]
                continue
            try:
                span, lines = next(it)
            except StopIteration:
                break
            cells[col] = lines
            if span > 1:
                hold[col] = [span - 1, lines]
        m = re.match(r"(\d{3}\.\d{1,3}) ?MHZ", " ".join(cells.get(2, [])))
        if not m:
            continue
        out.append({"service": " ".join(cells.get(0, [])), "callsign": " ".join(cells.get(1, [])), "mhz": float(m.group(1)), "printed": cells[2][0],
                    "hours": " ".join(cells.get(3, [])), "remarks": " ".join(cells.get(6, []))})
    return out

CIVIL = "OEAB OEAH OEAO OEBA OEBH OEDF OEGN OEGS OEGT OEHL OEJN OEMA OENG OEOM OEPA OERB OERF OERK OERR OERS OESH OESK OETB OETF OETH OETR OEWD OEWJ OEYN".split()


def text_of(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r'(?is)<span class="deletedAIRAC"[^>]*>(?:\s*<span[^>]*>.*?</span>\s*|[^<]*)*</span>', " ", t)          # what the amendment took out is still in the page, marked as deleted
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|td|th|li|h\d)>", "\n", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    return [l for l in (re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")) if l]


def section(lines, icao, a, b):
    i = next(k for k, l in enumerate(lines) if l.startswith(f"{icao} AD {a} "))
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith(f"{icao} AD {b} "))
    return lines[i:j]


def after(sec, label):
    """What stands after a label of AD 2.2, up to the number of the next item (a value may be broken over lines)."""
    k = next(i for i, l in enumerate(sec) if label.lower() in l.lower())
    got = []
    for l in sec[k + 1:]:
        if re.fullmatch(r"\d", l):
            break
        got.append(l)
    return " ".join(got)


def dms(s):
    m = re.search(r"([NS]) ?(\d{2})(\d{2})(\d{2}(?:\.\d+)?) ?([EW]) ?(\d{3})(\d{2})(\d{2}(?:\.\d+)?)", s)
    assert m, s
    la = (int(m.group(2)) + int(m.group(3)) / 60 + float(m.group(4)) / 3600) * (1 if m.group(1) == "N" else -1)
    lo = (int(m.group(6)) + int(m.group(7)) / 60 + float(m.group(8)) / 3600) * (1 if m.group(5) == "E" else -1)
    return round(la, 7), round(lo, 7)


airports = {a["icao"]: a for a in json.load(open(os.path.join(SRC, "data/structured/aerodromes.json"), encoding="utf-8"))["airports"]}
space = {}
for f in json.load(open(os.path.join(SRC, "data/structured/airport_airspace.geojson"), encoding="utf-8"))["features"]:
    space.setdefault(f["properties"]["icao"], []).append(f)

out = {"edition": "AIRAC AIP AMDT 11/26, effective 2026-10-29", "retrieved": "2026-11-17", "aerodromes": []}
for icao in CIVIL:
    path = os.path.join(PAGES, icao + ".html")
    lines = text_of(path)
    flat = " ".join(lines)
    s22 = section(lines, icao, "2.2", "2.3")
    arp_printed = after(s22, "ARP coordinates")
    lat, lon = dms(arp_printed)
    er = after(s22, "Elevation/Reference temperature")
    m = re.match(r"(\d+(?:\.\d+)?) ?FT", er)
    assert m, (icao, er)
    mt = re.search(r"/ ?(\d+(?:\.\d+)?) ?° ?C", er)                 # (a page may print NIL for the reference temperature: kept as None)
    var = after(s22, "MAG VAR")
    name = next(l for l in lines if l.startswith(f"{icao} - "))[7:]
    a = airports[icao]
    found, missing = 0, []

    def seen(v, what):
        global found
        ok = str(v) in flat
        found += ok
        if not ok:
            missing.append(f"{what}: {v}")
        return ok

    runways = []
    for r in a["runways"]:
        rw = {"id": r["designator"], "true_deg": r.get("true_brg"), "length_m": r.get("length_m"), "width_m": r.get("width_m"), "surface": r.get("surface"),
              "threshold": r.get("threshold"), "thr_elev_ft": r.get("thr_elev_ft"), "declared_m": r.get("declared_m"), "lighting": r.get("lighting")}
        rw["dims_in_amdt_11_26"] = seen(f"{r.get('length_m')} x {r.get('width_m')}", f"RWY {r['designator']} dimensions")
        for k, v in (r.get("declared_m") or {}).items():
            seen(v, f"RWY {r['designator']} {k}")
        runways.append(rw)
    zones = []
    for f in space.get(icao, []):
        p = f["properties"]
        z = {"name": p["name"], "kind": p["kind"], "class": p["class"], "lower": p["lower"]["raw"], "upper": p["upper"]["raw"], "hours": p["hours"], "units": p["units"],
             "transition_altitude": p["transition_altitude"], "geometry": f["geometry"]}
        z["in_amdt_11_26"] = seen(p["name"], "airspace name") and seen(p["upper"]["raw"], "airspace upper limit")
        zones.append(z)
    comms = comms_of(path)                               # read from the page itself: the repository's list breaks call signs and services over lines
    out["aerodromes"].append({
        "icao": icao, "name": name, "page_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
        "arp_printed": arp_printed, "lat": lat, "lon": lon, "elev_ref_printed": er, "elev_ft": float(m.group(1)), "ref_temp_c": float(mt.group(1)) if mt else None, "mag_var_printed": var,
        "traffic": after(s22, "Types of traffic permitted"), "runways": runways, "airspace": zones, "comms": comms, "sheet_500k": a.get("sheet_500k"),
        "checked_against_amdt_11_26": {"found": found, "not_found": missing}})
    print(icao, name[:34].ljust(34), er.ljust(18), "found", found, "missing", len(missing), missing[:3])
json.dump(out, open(os.path.join(HERE, "atlas_facts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote atlas_facts.json", len(out["aerodromes"]))
