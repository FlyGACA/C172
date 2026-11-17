"""Build data/saudi_airspace.json, the facts the Saudi-example figures of the handbook (chapters 17, 18, 20 and 26) draw from.

Source: the saudi-airspace repository (data/structured/*), extracted from the GACA eAIP, AIRAC AIP AMDT 11/26 (effective 2026-10-29). Before it was used here, every value of AD 2 OETH
was compared with the official AMDT 11/26 page (54 values, all found verbatim), and the runway thresholds of OEJN and OERS with their AMDT 11/26 pages (largest difference 0.01 m).
Values printed in the AIP are kept as printed. Everything derived (magnetic directions, distances, bearings) is computed here and marked.

    python3 build_saudi_facts.py [/path/to/saudi-airspace]      # writes saudi_airspace.json next to this file
Not for navigation.
"""
import json
import math
import os
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/saudi-airspace"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saudi_airspace.json")
NM = 1852.0
R_EARTH = 6371008.8


def load(name):
    return json.load(open(os.path.join(SRC, "data/structured", name), encoding="utf-8"))


def dist_brg(lat1, lon1, lat2, lon2):
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    brg = (math.degrees(math.atan2(y, x)) + 360) % 360
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h)) / NM, brg


def ring(feature, nd=5):
    return [[round(lo, nd), round(la, nd)] for lo, la in feature["geometry"]["coordinates"][0]]


oeth, aer = load("oeth.json"), {a["icao"]: a for a in load("aerodromes.json")["airports"]}
atc = {f["properties"]["id"]: f for f in load("atc_airspace.geojson")["features"]}
apt = {(f["properties"].get("icao"), f["properties"].get("kind")): f for f in load("airport_airspace.geojson")["features"]}
prd = {f["properties"]["id"]: f for f in load("prd_areas.geojson")["features"]}

facts = {
    "provenance": {
        "edition": "AIRAC AIP AMDT 11/26, effective 2026-10-29 (AMDT 12/26 takes effect 2026-11-26)",
        "retrieved": "2026-11-12",
        "pages": ["AD 2 OETH", "AD 2 OEJN", "AD 2 OERS", "AD 2 OERK", "ENR 1.1", "ENR 1.2", "ENR 1.4", "ENR 2.1", "ENR 5.1", "GEN 3.3", "GEN 3.4"],
        "geometry": "saudi-airspace data/structured (AIP polygons; circles and arcs sampled); pavement and building outlines of Thumamah traced by the project from satellite imagery, +/-10 m; not for navigation",
        "derived": "magnetic_deg = true_deg - variation_E; distances and bearings are great-circle from the AIP coordinates",
    },
}

# ---------------------------------------------------------------- Thumamah (OETH)
o = oeth
mv = o["mag_var"]["deg"]
facts["oeth"] = {
    "name": "Thumamah", "icao": "OETH", "arp": {"lat": o["arp"]["lat"], "lon": o["arp"]["lon"], "dms": [o["arp"]["lat_dms"], o["arp"]["lon_dms"]]},
    "elev_ft": o["arp"]["elev_ft"], "ref_temp_c": o["arp"]["ref_temp_c"], "mag_var_e_deg": mv, "mag_var_epoch": o["mag_var"]["epoch"],
    "traffic": "VFR", "remarks": "PPR except aircraft based at OETH", "operator": o["operator"],
    "runways": [{"id": r["id"], "true_deg": r["true_brg"], "magnetic_deg_derived": round(r["true_brg"] - mv, 1), "length_m": r["length_m"], "width_m": r["width_m"], "surface": r["surface"],
                 "threshold": {"lat": r["threshold"]["lat"], "lon": r["threshold"]["lon"], "elev_ft": r["threshold"]["elev_ft"]}, "stopway_m": r["stopway_m"], "strip_m": r["strip_m"], "resa_m": r["resa_m"],
                 "declared_m": r["declared_m"], "lighting": r["lighting"], "circuit": r["circuit"]} for r in o["runways"]],
    "stopway_note": "AD 2.12 lists a stopway under the runway that departs towards it: 60 x 50 m under RWY 17 (south of THR 35), 300 x 50 m under RWY 35 (north of THR 17)",
    "markings": o["markings"], "taxiways": o["taxiways"], "aprons": o["aprons"], "obstacles": o["obstacles"],
    "atz": {"name": "THUMAMAH ATZ", "centre": {"lat": o["airspace"]["atz"]["centre"]["lat"], "lon": o["airspace"]["atz"]["centre"]["lon"]}, "radius_nm": 5, "lower": "SFC", "upper_ft_amsl": 3000, "class": "G", "transition_altitude_ft": 13000, "hours": "NIL (no ATS unit)"},
    "comms": {"unicom": {"callsign": "THUMAMAH UNICOM", "mhz": 124.4, "hours_utc": "0300-1500", "note": "applies only within the ATZ"}, "tiba_mhz": 122.8},
    "vrps": [{"name": v["name"], "lat": v["lat"], "lon": v["lon"], "note": v["note"]} for v in o["vrps"]],
    "circuit": {"rwy35": "left-hand", "rwy17": "right-hand", "airplane_ft_msl": 2900, "gyroplane_ft_msl": 2400, "airplane_ft_agl_derived": 2900 - o["arp"]["elev_ft"],
                "note": "both circuits lie on the west side of the runway; AD 2.22.3.2: arrivals from the west join a 45-degree entry to downwind west of the Thumamah highway"},
    "procedures": o["procedures"], "noise_abatement": o["noise_abatement"], "local_regulations": o["local_regulations"],
    "wildlife_reserve": "0.7 NM west of RWY 17/35 (AD 2.21: avoid overflying)",
    "escarpment": "AD 2.10: 70 m high escarpment on the RWY 17 centre line, about 3 km out (slope 2.26%); 200 m high escarpment at 3.3 km (slope 4.38%); the AIP words the distance as 'north of RWY 35'; water tower 34 m in the RWY 17 approach",
}
for v in facts["oeth"]["vrps"]:
    d, b = dist_brg(o["arp"]["lat"], o["arp"]["lon"], v["lat"], v["lon"])
    v["from_arp_nm_derived"], v["from_arp_true_deg_derived"] = round(d, 2), round(b, 1)
north, east = facts["oeth"]["vrps"][0], facts["oeth"]["vrps"][1]
legs, pts = [], [("OETH", o["arp"]["lat"], o["arp"]["lon"]), ("North VRP", north["lat"], north["lon"]), ("East VRP", east["lat"], east["lon"]), ("OETH", o["arp"]["lat"], o["arp"]["lon"])]
for (n1, a1, b1), (n2, a2, b2) in zip(pts, pts[1:]):
    d, b = dist_brg(a1, b1, a2, b2)
    legs.append({"from": n1, "to": n2, "nm": round(d, 1), "true_deg": round(b), "magnetic_deg": round(b - mv)})
facts["worked_example_route"] = {"legs": legs, "total_nm": round(sum(l["nm"] for l in legs), 1), "note": "OETH - North VRP - East VRP - OETH; derived from the AIP coordinates (AD 2.22.3); a plan, not a published route"}

# ---------------------------------------------------------------- Riyadh (OERK), Jeddah (OEJN), Red Sea (OERS)
def airport(icao, extra=None):
    a = aer[icao]
    out = {"icao": icao, "name": a["name"], "arp": {"lat": a["arp"]["lat"], "lon": a["arp"]["lon"]}, "elev_ft": a["elev_ft"], "ref_temp_c": a["ref_temp_c"], "mag_var_e_deg": a["mag_var_deg_e"], "traffic": a["traffic"],
           "runways": [{"id": r["designator"], "true_deg": r["true_brg"], "magnetic_deg_derived": round(r["true_brg"] - a["mag_var_deg_e"], 1), "length_m": r["length_m"], "width_m": r["width_m"],
                        "threshold": {"lat": r["threshold"]["lat"], "lon": r["threshold"]["lon"], "elev_ft": r.get("thr_elev_ft")}, "declared_m": r.get("declared_m"), "lighting": r.get("lighting")} for r in a["runways"]]}
    out.update(extra or {})
    return out


facts["oerk"] = airport("OERK", {"ctr": {"name": "RIYADH CTR", "radius_nm": 10, "lower": "SFC", "upper_ft_amsl": 4500, "class": "D", "hours": "H24", "units": ["KING KHALED TOWER", "RIYADH APPROACH"]}, "rff_category": 9})
facts["oejn"] = airport("OEJN", {"ctr": {"name": "JEDDAH CTR", "radius_nm": 10, "lower": "SFC", "upper_ft_amsl": 2500, "class": "D", "hours": "H24", "units": ["Jeddah Tower"]}, "rff_category": 10,
                                  "approach_lighting": {"16C/34C": "CAT II, 900 m", "16L/34R": "CALVERT CAT I, 900 m", "16R/34L": "CAT II, 900 m"}, "papi": "both sides, 3 degrees, all six runways"})
facts["oers"] = airport("OERS", {"ctr": {"name": "Red Sea (CTR)", "lateral": "arc of 10 NM centred on the ARP between two points on the west side (see the polygon)", "ring": ring(apt[("OERS", "CTR")]),
                                         "lower": "SFC", "upper_ft_amsl": 2500, "class": "D", "hours_utc": "07:00-15:00", "remarks": "CTR is considered ATZ outside hours of applicability with Airspace classification G", "units": ["Red Sea Tower"]},
                                  "rff_category": 8, "runway_status": {"15L/33R": "open, 3700 x 45, ALSF-2 900 m, PAPI 3 degrees", "15R/33L": "Closed (AD 2.12 and 2.13)"}, "tiba_mhz": 122.8,
                                  "vrps_note": "AD 2.22.12: entry and exit to and from the ATZ via the west, east, north and south VRPs (A, B, C, D, E, F, G)"})

# Red Sea, typed from the official page (AD 2 OERS, AMDT 11/26, read 2026-11-12 and again 2026-11-17): the reporting points of AD 2.22.12 and the frequencies of AD 2.18, as printed
def dms(lat, lon):
    """'254238N', '0365701E' -> degrees."""
    return round(int(lat[0:2]) + int(lat[2:4]) / 60 + int(lat[4:6]) / 3600, 6), round(int(lon[0:3]) + int(lon[3:5]) / 60 + int(lon[5:7]) / 3600, 6)


OERS_VRPS = (("A", "north", "East Coastal Road Pad", "RDL 134 from WEJ 37.6 DME", "254238N", "0365701E"),
             ("B", "west", "North of Abu Laheq Island", "RDL144 from WEJ42.5 DME", "253442N", "0365429E"),
             ("C", "west", "East Coastal Road Service Station", "RDL138 from WEJ44.6 DME", "253540N", "0365952E"),
             ("D", "south", "Turtle Bay Hotel", "RDL 141 from WEJ 49.0 DME", "253014N", "0370005E"),
             ("E", "east", "Hitteen School", "RDL 124 from WEJ 50.6 DME", "253921N", "0371324E"),
             ("F", "south", "Shuray Construction Village", "RDL 138 from WEJ 50.4 DME", "253049N", "0370335E"),
             ("G", "east", "Desert Rock", "RDL 121 from WEJ 49.2 DME", "254224N", "0371359E"))
facts["oers"]["vrps"] = []
for letter, side, name, radial, la, lo in OERS_VRPS:
    lat, lon = dms(la, lo)
    dist, brg = dist_brg(aer["OERS"]["arp"]["lat"], aer["OERS"]["arp"]["lon"], lat, lon)
    facts["oers"]["vrps"].append({"id": letter, "side": side, "name": name, "printed": radial, "dms": [la, lo], "lat": lat, "lon": lon, "from_arp_nm_derived": round(dist, 1), "from_arp_true_deg_derived": round(brg)})
facts["oers"]["comms"] = {"tower": {"callsign": "Red Sea Tower", "mhz": 118.2, "hours": "0700-1500", "remark": "Call Red Sea Tower 15 min before ARR time"},
                          "ground": {"callsign": "Red Sea Ground", "mhz": 121.95, "hours": "0700-1500"}, "atis": {"mhz": 126.55, "hours": "0700 - 1500"},
                          "tiba": {"mhz": 122.8, "hours": "H24", "remark": "TIBA procedure to be applied H24 outside Red Sea CTR/ATZ."},
                          "note": "AD 2.18. The hours are printed without a time system; AD 2.3 pairs UTC hours with local ones (05:00 - 13:00 is 0800-1600 LT), so they are read as UTC"}
facts["oers"]["ctr"]["lateral_printed"] = "252743N 0370421E - 254122N 0365503E then a clockwise arc 10NM centred on 253742N 0370520E 252743N 0370421E"
facts["oers"]["tiba_rule"] = "AD 2.22.1.2: TIBA on 122.8 MHZ in class G airspace: outside all CTAs, TMAs and CTRs; off AWYs below FL150; ...; within uncontrolled aerodrome in non-TWR operating hours; where there is no ATS unit to provide FIS"

# ---------------------------------------------------------------- areas
facts["areas"] = {
    "oeth_atz_ring": ring(apt[("OETH", "ATZ")]),
    "oerk_ctr_ring": ring(apt[("OERK", "CTR")]),
    "oejn_ctr_ring": ring(apt[("OEJN", "CTR")]),
    "riyadh_east_tma_part1": {"ring": ring(atc["riyadh-east-terminal-control-area-tma-part-1"]), "lower": "700 FT AGL", "upper": "FL195", "class": "C", "exclusions": "Excluding Riyadh CTR. KHASHM ALAN ATZ, THUMAMAH ATZ."},
    "riyadh_east_tma_part2": {"ring": ring(atc["riyadh-east-terminal-control-area-tma-part-2"]), "lower": "2500 FT AGL", "upper": "FL195", "class": "C"},
    "riyadh_final_director_east_15l": {"ring": ring(atc["riyadh-final-director-east-rwy15l"]), "lower": "700 FT AGL", "upper": "11000 FT AMSL", "class": "C", "exclusions": "Excluding Riyadh CTR",
                                       "note": "the Thumamah ATZ lies inside this polygon, whose west edge is 4.97 NM from the Thumamah reference point (the ATZ radius is 5 NM, so within about 55 m); the printed exclusion names only the Riyadh CTR"},
    "prd": {k: {"ring": ring(prd[k]), "type": prd[k]["properties"]["type"], "lower": prd[k]["properties"]["lower"]["raw"], "upper": prd[k]["properties"]["upper"]["raw"], "remarks": prd[k]["properties"]["remarks"]}
            for k in ("OED25", "OER212", "OED33")},
}
d, b = dist_brg(o["arp"]["lat"], o["arp"]["lon"], aer["OERK"]["arp"]["lat"], aer["OERK"]["arp"]["lon"])
facts["oeth_to_oerk"] = {"nm_derived": round(d, 1), "true_deg_derived": round(b), "note": "the ATZ edge (5 NM from OETH) and the Riyadh CTR edge (10 NM from OERK) are about %.1f NM apart on this line" % (d - 15.0)}
for k, a in facts["areas"]["prd"].items():
    cx = sum(p[0] for p in a["ring"][:-1]) / (len(a["ring"]) - 1)
    cy = sum(p[1] for p in a["ring"][:-1]) / (len(a["ring"]) - 1)
    dd, bb = dist_brg(o["arp"]["lat"], o["arp"]["lon"], cy, cx)
    a["centre_from_oeth_nm_derived"], a["centre_from_oeth_true_deg_derived"] = round(dd, 1), round(bb)
    near = min((dist_brg(o["arp"]["lat"], o["arp"]["lon"], p[1], p[0]) + (p,) for p in a["ring"][:-1]), key=lambda x: x[0])
    a["nearest_vertex_from_oeth_nm_derived"], a["nearest_vertex_from_oeth_true_deg_derived"] = round(near[0], 1), round(near[1])

# ---------------------------------------------------------------- the AIP's visual charts (GEN 3.2, ENR 6)
sheets = sorted(load("chart_sheets.geojson")["features"], key=lambda f: f["properties"]["sheet"])
check_path = os.path.join(os.path.dirname(OUT), "chart_cone_check.json")
facts["charts"] = {
    "source": "AIP GEN 3.2.4.2 (both series are 'constructed on Lambert Conformal Conic Projection (Standard Parallels indicated on chart)') and ENR 6 (the list of the sheets), AMDT 11/26, read 2026-11-17; "
              "the bounds of the sheets from saudi-airspace data/structured/chart_sheets.geojson (read off the frame of every sheet)",
    "projection": {"name": "Lambert Conformal Conic", "printed": "Lambert Conformal Conic Projection / Standard Paralleles 25\u00b020' and 30\u00b040'",
                   "standard_parallels_printed": ["25\u00b020'", "30\u00b040'"], "standard_parallels_deg": [round(25 + 20 / 60, 6), round(30 + 40 / 60, 6)],
                   "read_from": "the margin of all 53 sheets, read by eye from the PDFs (the same words on every one); sheet 2546-C is page ENR 6-73, dated 29 OCT 2026",
                   "check": json.load(open(check_path, encoding="utf-8")) if os.path.exists(check_path) else None},
    "sheets_500k": [{"sheet": f["properties"]["sheet"], "west": f["properties"]["bbox"][0], "south": f["properties"]["bbox"][1], "east": f["properties"]["bbox"][2], "north": f["properties"]["bbox"][3]}
                    for f in sheets if f["properties"]["series"].startswith("ICAO 1:500")],
    "sheets_wac": [{"sheet": f["properties"]["sheet"], "west": f["properties"]["bbox"][0], "south": f["properties"]["bbox"][1], "east": f["properties"]["bbox"][2], "north": f["properties"]["bbox"][3]}
                   for f in sheets if f["properties"]["series"].startswith("WAC")],
    "sheet_of_oeth": next(f["properties"]["sheet"] for f in sheets if f["properties"]["series"].startswith("ICAO 1:500")
                          and f["properties"]["bbox"][0] <= o["arp"]["lon"] < f["properties"]["bbox"][2] and f["properties"]["bbox"][1] <= o["arp"]["lat"] < f["properties"]["bbox"][3]),
}
assert len(facts["charts"]["sheets_500k"]) == 45 and len(facts["charts"]["sheets_wac"]) == 8 and facts["charts"]["sheet_of_oeth"] == "2546-C"      # the counts of ENR 6 (AMDT 11/26)
facts["provenance"]["pages"] += ["GEN 3.2", "ENR 6"]

json.dump(facts, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
print("route:", facts["worked_example_route"])
print("OETH-OERK:", facts["oeth_to_oerk"])
print({k: (v["nearest_vertex_from_oeth_nm_derived"], v["nearest_vertex_from_oeth_true_deg_derived"]) for k, v in facts["areas"]["prd"].items()})
