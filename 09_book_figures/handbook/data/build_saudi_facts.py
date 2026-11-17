"""Build data/saudi_airspace.json, the facts the Saudi-example figures of the handbook (chapters 4, 11, 17, 18, 19, 20, 21 and 26) draw from.

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

# Jeddah, typed from the official page (AD 2 OEJN, AMDT 11/26, read 2026-11-12 and again 2026-11-17): the reporting points of AD 2.22.12, the route of AD 2.22.11, the DVOR/TACAN of
# AD 2.19 and the frequencies of AD 2.18 and of the Visual Approach Chart (page AD 2 OEJN - 205), as printed. Seconds are printed with one decimal for some points and none for others.
def dms1(lat, lon):
    """'215322.9N', '0391525.9E' -> degrees."""
    a, b = float(lat[:-1]), float(lon[:-1])
    return round(int(a // 10000) + int(a % 10000 // 100) / 60 + (a % 100) / 3600, 7), round(int(b // 10000) + int(b % 10000 // 100) / 60 + (b % 100) / 3600, 7)


OEJN_JDW = ("214244.3N", "0390723.2E")                     # DVOR/TACAN JDW 115.300 MHZ (CH100X), declination 04 E
OEJN_POINTS = (("VRP01", "University of Jeddah (North)", "RDL 032 from JDW 13.0NM", "215322.9N", "0391525.9E", "approach"),
               ("VRP02", "Highway junctions and intersection of King Abdullah Sports City (0.6 NM East of King Abdullah Sports City)", "RDL 032 from JDW 4.8 NM", "214643.0N", "0391019.0E", "tower_east"),
               ("VRP03", "Highway junctions and intersection of Airbase (3.2 NM East of King Abdulaziz international airport)", "RDL 103 from JDW 4.8 NM", "214123.0N", "0391223.0E", "tower_east"),
               ("VRP04", "Highway junctions and intersection of Tahliya Street (0.8 NM East of AlAhli club)", "RDL 142 from JDW 10.6 NM", "213405.0N", "0391354.0E", "tower_east"),
               ("VRP05", "Abruq Al-Rughamah (2.5 NM South East of Jeddah Central train station)", "RDL 142 from JDW 14.8 NM", "213026.2N", "0391625.9E", "approach"),
               ("VRP06", "Makkah - Jeddah Highway junctions East of Prince Abdullah Al Faisal Stadium (0.5 NM East of Prince Abdullah Al Faisal Stadium)", "RDL 151 from JDW 17.5 NM", "212655.0N", "0391532.0E", "approach"),
               ("VRP08", "King Abdul Aziz road junctions and intersection of Hira Street (Bank Al Jazira, the Head Office)", "RDL 175 from JDW 6.4 NM", "213622.3N", "0390714.2E", "tower_west"),
               ("VRP09", "Marine Sciences roundabout (Abhor)", "RDL 252 from JDW 1.1 NM", "214228.0N", "0390612.0E", "tower_west"),
               ("VRP10", "Prince Abdulmajeed Street West of King Abdullah Medical Complex", "RDL 317 from JDW 4.0 NM", "214548.0N", "0390438.0E", "tower_west"),
               ("VRP11", "Prince Abdulmajeed street North of King Abdullah Medical Complex", "RDL 336 from JDW 5.1 NM", "214727.0N", "0390529.0E", "tower_west"),
               ("VRP12", "Prince Abdulmajeed Street junctions and intersection of Madinah Road (East of King Abdullah Medical Complex)", "RDL 356 from JDW 5.0 NM", "214747.0N", "0390718.0E", "tower_east"),
               ("VRP13", "Lake City", "RDL 320 from JDW 8.7 NM", "214944.0N", "0390146.4E", "approach"),
               ("KHOAR", "-", "RDL 039 from JDW 39.4 NM", "221200.0N", "0393600.0E", None),
               ("GHARI", "-", "RDL 039 from JDW 59.1 NM", "222600.0N", "0395100.0E", None),
               ("AZIZI", "-", "RDL 143 from JDW 15.0 NM", "212757.0N", "0391827.0E", None))
jdw_lat, jdw_lon = dms1(*OEJN_JDW)
facts["oejn"]["jdw"] = {"type": "DVOR/TACAN", "id": "JDW", "mhz": 115.3, "declination_e_deg": 4, "dms": list(OEJN_JDW), "lat": jdw_lat, "lon": jdw_lon}
facts["oejn"]["points"] = []
for name, place, printed, la, lo, unit in OEJN_POINTS:
    lat, lon = dms1(la, lo)
    d_arp, b_arp = dist_brg(aer["OEJN"]["arp"]["lat"], aer["OEJN"]["arp"]["lon"], lat, lon)
    d_jdw, b_jdw = dist_brg(jdw_lat, jdw_lon, lat, lon)
    rdl, nm = int(printed.split()[1]), float(printed.split("JDW")[1].replace("NM", ""))
    row = {"id": name, "place": place, "printed": printed, "dms": [la, lo], "lat": lat, "lon": lon, "contact": unit, "from_arp_nm_derived": round(d_arp, 2), "from_arp_true_deg_derived": round(b_arp, 1),
           "inside_ctr_derived": bool(d_arp < 10), "from_jdw_nm_derived": round(d_jdw, 2), "from_jdw_magnetic_deg_derived": round((b_jdw - 4) % 360, 1)}
    if abs(d_jdw - nm) > 0.5 or abs(((b_jdw - 4 - rdl + 180) % 360) - 180) > 3:
        row["inconsistent"] = f"the printed coordinates lie {d_jdw:.1f} NM from JDW on radial {(b_jdw - 4) % 360:03.0f}; the printed bearing and distance say {nm:.1f} NM on radial {rdl:03d}. Kept as printed; drawn at the coordinates"
    facts["oejn"]["points"].append(row)
assert [r["id"] for r in facts["oejn"]["points"] if "inconsistent" in r] == ["AZIZI"]            # the only one: 3.0 NM
assert [r["id"] for r in facts["oejn"]["points"] if r["contact"] and not r["inside_ctr_derived"]] == ["VRP01", "VRP05", "VRP06", "VRP13"]      # the four gates lie outside the zone, the eight others inside
facts["oejn"]["comms"] = {"approach": {"callsign": "Jeddah Approach", "mhz": 124.0, "hours": "H24", "remark": "VHF APP"},
                          "tower_west": {"callsign": "Jeddah Tower", "mhz": 118.2, "hours": "H24", "remark": "TWR West; the Visual Approach Chart prints 118.2 (W)"},
                          "tower_east": {"callsign": "Jeddah Tower", "mhz": 118.5, "hours": "H24", "remark": "TWR EAST / East; AD 2.22.11: TWR-E on 118.500 MHz; the Visual Approach Chart prints 118.5 (E)"},
                          "note": "AD 2.18 and the Visual Approach Chart - ICAO (AD 2 OEJN - 205, 29 OCT 2026), which prints TWR: 118.2 (W) 118.3 (C) 118.5 (E) 124.3 (E) and APP: 124.0 123.8 124.675 125.850. The remarks of AD 2.18 run together in AMDT 11/26 (TWR West; TWR Center WEST SDBY; TWR EAST East; Backup TWR EAST SDBY); AMDT 12/26 prints them as TWR West, TWR Center, TWR East and Backup, with the same frequencies"}
facts["oejn"]["vfr"] = {"within_ctr": ["These VRPs not to be used as holding point.", "VFR flights operating via (VRP02, VRP03, VRP04 and VRP12) shall contact Jeddah TWR East.",
                                       "VFR flights operating via (VRP08, VRP09, VRP10 and VRP11) shall contact Jeddah TWR West.",
                                       "VFR flights operating via (VRP01, VRP05, VRP06 and VRP13) shall contact Jeddah Approach control 10NM prior the VRPs.",
                                       "Entry and exit to and from OEJN CTR shall be via VRP01, VRP05, VRP06 and VRP13.", "Pilots expect frequency change instructions as directed by ATC."],
                        "uvr": {"JDW1": ["VRP06", "AZIZI", "VRP01", "KHOAR", "GHARI", "DAFINAH", "MOLAQ"], "max_ft_agl": 500,
                                "printed": ["The maximum UVR altitude is 500 FT AGL, and any request for higher altitude is subject to ATC approval.",
                                            "Aircraft intending to utilize UVR from point AZIZI to VRP01 must first hold at AZIZI and request clearance to transition the CTR from TWR-E on 118.500 MHz.",
                                            "Aircraft intending to utilize UVR from point VRP01 to AZIZI must first hold at VRP01 and request clearance to transition the CTR from TWR-E on 118.500 MHz.",
                                            "No aircraft under any circumstances shall enter or exit OEJN CTR without clearance from Jeddah Aerodrome Control Tower."],
                                "note": "AD 2.22.11 and 2.22.12. DAFINAH and MOLAQ are in the path and not in the table of points. The table has no VRP07. 2.22.11 has aircraft hold at VRP01, and 2.22.12 says of the VRPs that they are not to be used as holding point: both kept as printed. 'UVR charts are published on SANS Website': not seen"}}

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

# ---------------------------------------------------------------- hot and high: the elevation and the reference temperature of twelve aerodromes (AD 2.2), and the density altitude they give
# Typed from item 1 (ARP) and item 3 (Elevation/Reference temperature) of AD 2.2 on the official AMDT 11/26 page of each aerodrome, and found again there word for word on 2026-11-17.
# The saudi-airspace index is not used for these two values: it was built from the pages of AMDT 12/26 and keeps only the whole degrees of a reference temperature.
HOT_AND_HIGH = (("OEAB", "N181425 E0423923", "6858 FT / 33° C"), ("OEBA", "N201754 E0413809", "5459 FT / 33° C"), ("OETF", "N212900 E0403240", "4848 FT / 34.7° C"),
                ("OENG", "N173641 E0442509", "3983 FT / 38.2° C"), ("OEHL", "N272623 E0414111", "3305 FT / 37.6° C"), ("OETB", "N282223 E0363717", "2551 FT / 37.6° C"),
                ("OEMA", "N243301 E0394221", "2134 FT / 42° C"), ("OERK", "N245746 E0464229", "2053 FT / 42.3° C"), ("OETH", "N251251 E0463827", "1870 FT / 42° C"),
                ("OEAH", "N251710 E0492910", "588 FT / 46° C"), ("OEDF", "N262816 E0494752", "75 FT / 45.2° C"), ("OEJN", "N214052 E0390922", "50 FT / 37.9° C"))
ISA_T0_K, ISA_LAPSE_K_M, ISA_G, ISA_R = 288.15, 0.0065, 9.80665, 287.05287          # the standard atmosphere below the tropopause (ICAO Doc 7488)
ISA_N = ISA_G / (ISA_R * ISA_LAPSE_K_M)


def density_altitude_ft(pressure_altitude_ft, oat_c):
    """The height in the standard atmosphere at which dry air has the density it has at this pressure altitude and temperature."""
    pressure = (1 - ISA_LAPSE_K_M * pressure_altitude_ft * 0.3048 / ISA_T0_K) ** ISA_N
    density = pressure * ISA_T0_K / (oat_c + 273.15)
    return ISA_T0_K / ISA_LAPSE_K_M * (1 - density ** (1 / (ISA_N - 1))) / 0.3048


def rule_of_thumb_ft(pressure_altitude_ft, oat_c):
    """The book's rule: ISA temperature = 15 - 2 for each 1 000 ft; density altitude = pressure altitude + 120 for each degree above it."""
    return pressure_altitude_ft + 120 * (oat_c - (15 - 2 * pressure_altitude_ft / 1000))


rows = []
for icao, arp, printed in HOT_AND_HIGH:
    a = aer[icao]
    lat = int(arp[1:3]) + int(arp[3:5]) / 60 + int(arp[5:7]) / 3600
    lon = int(arp[9:12]) + int(arp[12:14]) / 60 + int(arp[14:16]) / 3600
    elev, temp = int(printed.split(" FT / ")[0]), float(printed.split(" FT / ")[1].replace("° C", ""))
    assert abs(lat - a["arp"]["lat"]) < 1e-6 and abs(lon - a["arp"]["lon"]) < 1e-6 and int(temp) == a["ref_temp_c"], icao             # the index agrees on the place and on the whole degrees
    exact, rule = density_altitude_ft(elev, temp), rule_of_thumb_ft(elev, temp)
    row = {"icao": icao, "name": a["name"], "arp_printed": arp, "lat": round(lat, 7), "lon": round(lon, 7), "elev_ref_printed": printed, "elev_ft": elev, "ref_temp_c": temp,
           "isa_temp_c_derived": round(15 - ISA_LAPSE_K_M * elev * 0.3048, 1), "density_altitude_ft_derived": round(exact), "density_altitude_rounded_ft_derived": int(round(exact / 50.0) * 50),
           "rule_of_thumb_ft_derived": round(rule), "rule_minus_exact_ft_derived": round(rule - exact)}
    if a["elev_ft"] != elev:
        row["amdt_12_26"] = {"elev_ft": int(a["elev_ft"]), "note": "AMDT 12/26 (effective 2026-11-26) prints this elevation; the page of AMDT 12/26 marks the old one as deleted"}
    rows.append(row)
assert [r["icao"] for r in rows if "amdt_12_26" in r] == ["OEAH"] and rows[9]["amdt_12_26"]["elev_ft"] == 599                           # the only one of the twelve whose AD 2.2 changes with AMDT 12/26
assert all(150 <= r["rule_minus_exact_ft_derived"] <= 310 for r in rows), [r["rule_minus_exact_ft_derived"] for r in rows]                # the rule of thumb errs high by this much at these temperatures
assert rows[0]["density_altitude_ft_derived"] > 10000 and rows[8]["elev_ft"] == facts["oeth"]["elev_ft"] and rows[8]["ref_temp_c"] == facts["oeth"]["ref_temp_c"]
facts["hot_and_high"] = {
    "source": "AIP AD 2.2 of each aerodrome, items 1 and 3, AMDT 11/26; typed here and found again word for word on the official pages on 2026-11-17 (sha256 of each page in the book's sources/registry.json)",
    "assumptions": "the outside air temperature is the aerodrome reference temperature; QNH 1013.25 hPa, so that the pressure altitude is the elevation; dry air; the ICAO standard atmosphere (Doc 7488 constants)",
    "derived": "isa_temp_c, density_altitude_ft (the exact value), density_altitude_rounded_ft (to 50 ft, as the figure prints it), rule_of_thumb_ft (the book's rule) and rule_minus_exact_ft are worked out here, not printed in the AIP",
    "aerodromes": sorted(rows, key=lambda r: -r["density_altitude_ft_derived"]),
}
for key in ("oerk", "oejn"):                                                                # the printed reference temperatures, with their tenths (the index keeps whole degrees)
    facts[key]["ref_temp_c"] = next(r["ref_temp_c"] for r in rows if r["icao"] == key.upper())
facts["provenance"]["pages"] += ["AD 2 OEAB", "AD 2 OEBA", "AD 2 OETF", "AD 2 OENG", "AD 2 OEHL", "AD 2 OETB", "AD 2 OEMA", "AD 2 OEAH", "AD 2 OEDF"]

# ---------------------------------------------------------------- a fix from one station: the DVOR/DME of Riyadh and the two reporting points of Thumamah
# AD 2 OERK 2.19 (AMDT 11/26, the same text in AMDT 12/26): DVOR/DME (03° E) KSA 115.000 MHZ (CH97X) H24 245849.2N 0464008.1E, elevation of the DME antenna 2100 FT.
# AD 2 OETH 2.22.3 places the two reporting points by it: "RDL 358 from KSA 18.83 NM" and "RDL 025 from KSA 15.82 NM".
OERK_KSA = ("245849.2N", "0464008.1E")
ksa_lat, ksa_lon = dms1(*OERK_KSA)
facts["oerk"]["ksa"] = {"type": "DVOR/DME", "id": "KSA", "mhz": 115.0, "channel": "CH97X", "declination_e_deg": 3, "hours": "H24", "dms": list(OERK_KSA), "lat": ksa_lat, "lon": ksa_lon, "dme_antenna_elev_ft": 2100}
for v, (radial, nm) in zip(facts["oeth"]["vrps"], ((358, 18.83), (25, 15.82))):
    assert f"RDL {radial:03d} from KSA {nm} NM" in v["note"], v["note"]
    d, b = dist_brg(ksa_lat, ksa_lon, v["lat"], v["lon"])
    v["from_ksa_printed"] = {"radial": radial, "nm": nm}
    v["from_ksa_nm_derived"], v["from_ksa_true_deg_derived"], v["from_ksa_magnetic_deg_derived"] = round(d, 2), round(b, 1), round((b - 3) % 360, 1)
    assert abs(d - nm) < 0.1 and abs(((b - 3 - radial) + 180) % 360 - 180) < 0.6, (v["name"], d, b)          # the printed radial and distance agree with the printed coordinates

# ---------------------------------------------------------------- the AIP as a publication: its parts, its amendments and one supplement (Figures 4-1 and 4-2)
# Typed from the official eAIP on 2026-11-17 and found there word for word (the book's sources/registry.json has the hash of each page):
#   GEN 0.2, RECORD OF AIP AMENDMENTS      AIRAC AIP AMDT 10/26  20 Aug 2026  01 Oct 2026;  11/26  17 Sep 2026  29 Oct 2026  (the AMDT 11/26 package);
#                                          12/26  15 Oct 2026  26 Nov 2026  (added in the AMDT 12/26 package)
#   the table of contents (eAIP menu)      AD 2 has 62 aerodromes, each under the same subsections AD 2.1 to AD 2.25; AD 1.3 lists the same 62
#   the list of supplements                28 in force in the AMDT 11/26 package ("Published as of 17 SEP 2026"), among them AIP SUP 36/26, "from 17 SEP 2026"
#   AIP SUP 36/26                          dated 10 SEP 2026, EXPANSION OF URBAN VFR ROUTES (UVRs) IN RIYADH: "This supplement supersedes the current VFR route procedures published
#                                          under OERK AD 2.22."; "starting on17 September 2026 and remain current until the AIP is amended"; routes RYA 1 to RYA 11 and NAJD 1 to NAJD 7
#   AD 2 OERK 2.22.11 (AMDT 11/26 and 12/26)   still lists RYA 1 to RYA 10 and NAJD1 to NAJD4
import datetime as _dt


def _date(s):
    return _dt.date.fromisoformat(s)


AMENDMENTS = [("AIRAC AIP AMDT 10/26", "2026-08-20", "2026-10-01"), ("AIRAC AIP AMDT 11/26", "2026-09-17", "2026-10-29"), ("AIRAC AIP AMDT 12/26", "2026-10-15", "2026-11-26")]
for _name, _pub, _eff in AMENDMENTS:
    assert (_date(_eff) - _date(_pub)).days == 42 and _date(_eff).weekday() == 3, _name                     # published six weeks ahead; the effective date is a Thursday
assert all((_date(b[2]) - _date(a[2])).days == 28 for a, b in zip(AMENDMENTS, AMENDMENTS[1:]))               # 28 days from one effective date to the next
oeah = next(r for r in rows if r["icao"] == "OEAH")
assert (oeah["elev_ft"], oeah["amdt_12_26"]["elev_ft"]) == (588, 599)
facts["aip"] = {
    "source": "AIP-KSA, the eAIP on aimss.sans.com.sa: GEN 0.1, GEN 0.2, the table of contents, AD 1.3, the list of supplements and AIP SUP 36/26, as published with AMDT 11/26 and AMDT 12/26; typed here and found again word for word on 2026-11-17",
    "parts": ["GEN", "ENR", "AD"],
    "aerodromes_in_ad2": 62,
    "ad2_subsections": 25,
    "amendments": [{"name": n_, "published": p_, "effective": e_, "days_ahead_derived": 42} for n_, p_, e_ in AMENDMENTS],
    "cycle_days_derived": 28,
    "supplements_in_force": {"as_of": "2026-09-17", "count": 28, "airac": 12, "other": 16},
    "sup_36_26": {"name": "AIP SUP 36/26", "dated": "2026-09-10", "valid_from": "2026-09-17", "subject": "EXPANSION OF URBAN VFR ROUTES (UVRs) IN RIYADH",
                  "supersedes": "the current VFR route procedures published under OERK AD 2.22", "replaces": "AIP SUP 23/26", "until": "the AIP is amended with the relevant information",
                  "routes": {"RYA": 11, "NAJD": 7}, "ad2_oerk_2_22_11_routes": {"RYA": 10, "NAJD": 4}},
    "example_change": {"icao": "OEAH", "what": "aerodrome elevation, AD 2.2 item 3", "amdt_11_26_ft": 588, "amdt_12_26_ft": 599, "effective": "2026-11-26"},
}
facts["provenance"]["pages"] += ["GEN 0.1", "GEN 0.2", "AD 1.3", "AIP SUP 36/26"]

json.dump(facts, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
print("route:", facts["worked_example_route"])
print("OETH-OERK:", facts["oeth_to_oerk"])
print({k: (v["nearest_vertex_from_oeth_nm_derived"], v["nearest_vertex_from_oeth_true_deg_derived"]) for k, v in facts["areas"]["prd"].items()})
