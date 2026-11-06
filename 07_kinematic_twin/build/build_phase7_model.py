#!/usr/bin/env python3
"""Build C172N_Phase7_Kinematic_Twin.glb — FlyGACA C172N digital twin, Phase 7.

Pure Python + numpy (no trimesh/Blender). Re-running produces the same file.

What changed versus Phase 6 (see ../README.md for the full list):
  * Every part is its own node with a meaningful pivot, so exploded views and
    animation work (Phase 6 baked all vertices in world space, translation 0).
  * Lycoming cylinder numbering: odd cylinders on the right bank, even on the
    left, No.1 right-front, firing order 1-3-2-4; flat-four crankshaft with
    throws 1/4 and 2/3 paired; camshaft at half speed.
  * One engine-driven DUAL magneto (POH p.7-18) wired to the POH plug map
    (right magneto -> lower right + upper left plugs, p.7-19), replacing the
    two separate magnetos drawn in Phase 6.
  * Systems are placed in a 1:1 airframe envelope sized from POH Figure 1-1
    (36 ft span, 26 ft 11 in length) with POH-located items: battery on the
    left forward firewall (p.7-25), oil cooler lower right firewall (p.7-18),
    pitot tube under the left wing and static port on the lower left forward
    fuselage (p.7-31), alternate static valve below the throttle (p.7-31).
  * PBR materials, colour-coded system plumbing and functional instrument
    needles whose dial markings come from data/instruments.json (POH Fig 2-2/2-3).

Geometry remains schematic: it is not derived from Cessna/Lycoming drawings or
an IPC and must not be used for maintenance, manufacturing or flight training
credit.

Coordinates: metres, glTF axes (+Y up, +Z forward toward the propeller,
+X toward the LEFT wing). Ground plane is y = 0.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from geometry import (  # noqa: E402
    Geom, align, arc_band, box, cyl_between, cylinder, disc, loft, merge, quat_from_matrix, rot,
    sphere, superellipse_ring, tick, tube, wing_panel,
)
from glb_writer import GLB  # noqa: E402

ROOT = HERE.parent
OUT = ROOT / "C172N_Phase7_Kinematic_Twin.glb"
INDEX = ROOT / "data" / "model_index.json"
INSTR = json.loads((ROOT / "data" / "instruments.json").read_text(encoding="utf-8"))["instruments"]

# ------------------------------------------------------------------ engine data
E = np.array([0.0, 1.20, 1.45])         # crank-axis centre of the engine, airframe coords
CRANK_R = 0.0492                        # half of 3.875 in stroke (O-320 type data, verify vs TCDS E-274)
ROD_L = 0.162                           # connecting-rod centre distance (illustrative)
BORE_R = 0.064                          # ~5.125 in bore / 2 (O-320 type data, verify)
# cylinder: bank direction (+1 = left/+X, -1 = right/-X), longitudinal station, crank-pin phase
CYL = {
    1: {"side": -1, "z": 0.110, "pin_deg": 180.0},
    2: {"side": +1, "z": 0.060, "pin_deg": 0.0},
    3: {"side": -1, "z": -0.070, "pin_deg": 0.0},
    4: {"side": +1, "z": -0.120, "pin_deg": 180.0},
}
FIRING_ORDER = [1, 3, 2, 4]
# POH p.7-19: right magneto fires lower-right and upper-left plugs; left magneto fires lower-left and upper-right.
def plug_magneto(cyl: int, position: str) -> str:
    right_bank = CYL[cyl]["side"] < 0
    if position == "lower":
        return "R" if right_bank else "L"
    return "L" if right_bank else "R"


# ---------------------------------------------------------------- the document
g = GLB("FlyGACA C172N Phase 7 builder (build_phase7_model.py)")
M = {}


def mat(name, rgba, **kw):
    M[name] = g.material(name, rgba, **kw)
    return M[name]


mat("ghost_airframe", (0.86, 0.90, 0.95, 0.14), metallic=0.1, roughness=0.35)
mat("ghost_surface", (0.80, 0.86, 0.93, 0.20), metallic=0.1, roughness=0.35)
mat("firewall", (0.74, 0.76, 0.80, 0.45), metallic=0.6, roughness=0.4)
mat("crankcase", (0.56, 0.58, 0.61, 1.0), metallic=0.55, roughness=0.45)
mat("cylinder_barrel", (0.30, 0.32, 0.34, 1.0), metallic=0.6, roughness=0.5)
mat("cylinder_head", (0.66, 0.68, 0.70, 1.0), metallic=0.6, roughness=0.4)
mat("rocker_cover", (0.78, 0.78, 0.80, 1.0), metallic=0.7, roughness=0.3)
mat("steel", (0.80, 0.81, 0.83, 1.0), metallic=0.9, roughness=0.28)
mat("piston", (0.88, 0.88, 0.90, 1.0), metallic=0.8, roughness=0.3)
mat("cam", (0.70, 0.62, 0.45, 1.0), metallic=0.8, roughness=0.35)
mat("exhaust", (0.50, 0.36, 0.27, 1.0), metallic=0.7, roughness=0.6)
mat("induction", (0.62, 0.64, 0.60, 1.0), metallic=0.5, roughness=0.45)
mat("carburetor", (0.74, 0.66, 0.42, 1.0), metallic=0.7, roughness=0.35)
mat("air_filter", (0.18, 0.18, 0.19, 1.0), roughness=0.8)
mat("spark_plug", (0.93, 0.93, 0.95, 1.0), roughness=0.3)
mat("magneto", (0.12, 0.12, 0.13, 1.0), metallic=0.3, roughness=0.5)
mat("ignition_lead", (0.96, 0.78, 0.20, 1.0), roughness=0.5)
mat("fuel_line", (0.18, 0.46, 0.96, 1.0), roughness=0.4)
mat("fuel_tank", (0.55, 0.70, 0.90, 0.30), metallic=0.2, roughness=0.3)
mat("avgas_100ll", (0.15, 0.42, 1.00, 0.70), roughness=0.15)
mat("fuel_valve", (0.20, 0.22, 0.26, 1.0), metallic=0.4, roughness=0.5)
mat("oil_line", (0.96, 0.62, 0.10, 1.0), roughness=0.4)
mat("oil_part", (0.44, 0.40, 0.33, 1.0), metallic=0.5, roughness=0.5)
mat("electric_cable", (0.88, 0.16, 0.16, 1.0), roughness=0.45)
mat("battery", (0.14, 0.14, 0.16, 1.0), roughness=0.6)
mat("terminal_pos", (0.85, 0.15, 0.15, 1.0), metallic=0.6, roughness=0.35)
mat("terminal_neg", (0.10, 0.10, 0.10, 1.0), metallic=0.6, roughness=0.35)
mat("electrical_part", (0.58, 0.60, 0.63, 1.0), metallic=0.7, roughness=0.35)
mat("vacuum_line", (0.64, 0.36, 0.88, 1.0), roughness=0.4)
mat("vacuum_part", (0.36, 0.30, 0.46, 1.0), metallic=0.4, roughness=0.5)
mat("pitot_line", (0.20, 0.78, 0.38, 1.0), roughness=0.4)
mat("static_line", (0.12, 0.78, 0.88, 1.0), roughness=0.4)
mat("pitot_tube", (0.82, 0.83, 0.86, 1.0), metallic=0.9, roughness=0.25)
mat("prop_blade", (0.56, 0.58, 0.62, 1.0), metallic=0.8, roughness=0.35)
mat("prop_tip", (0.95, 0.95, 0.95, 1.0), roughness=0.4)
mat("spinner", (0.93, 0.93, 0.95, 1.0), metallic=0.3, roughness=0.25)
mat("tire", (0.07, 0.07, 0.08, 1.0), roughness=0.9)
mat("gear", (0.86, 0.88, 0.90, 1.0), metallic=0.6, roughness=0.35)
mat("panel", (0.10, 0.10, 0.11, 1.0), roughness=0.7)
mat("bezel", (0.17, 0.17, 0.18, 1.0), metallic=0.3, roughness=0.5)
mat("dial_face", (0.035, 0.035, 0.04, 1.0), roughness=0.85)
mat("dial_white", (0.95, 0.95, 0.95, 1.0), roughness=0.5, emissive=(0.25, 0.25, 0.25))
mat("arc_white", (0.96, 0.96, 0.96, 1.0), roughness=0.5, emissive=(0.25, 0.25, 0.25))
mat("arc_green", (0.10, 0.78, 0.28, 1.0), roughness=0.5, emissive=(0.02, 0.18, 0.05))
mat("arc_yellow", (0.98, 0.80, 0.10, 1.0), roughness=0.5, emissive=(0.2, 0.15, 0.0))
mat("red_line", (0.92, 0.10, 0.10, 1.0), roughness=0.5, emissive=(0.25, 0.0, 0.0))
mat("needle", (0.98, 0.98, 0.98, 1.0), roughness=0.4, emissive=(0.35, 0.35, 0.35))
mat("ai_sky", (0.24, 0.55, 0.92, 1.0), roughness=0.6)
mat("ai_ground", (0.55, 0.34, 0.17, 1.0), roughness=0.7)
mat("ai_symbol", (1.0, 0.55, 0.0, 1.0), roughness=0.5, emissive=(0.3, 0.15, 0.0))
mat("knob_black", (0.06, 0.06, 0.07, 1.0), roughness=0.5)
mat("knob_red", (0.82, 0.10, 0.10, 1.0), roughness=0.45)
mat("knob_white", (0.90, 0.90, 0.88, 1.0), roughness=0.45)
mat("switch_white", (0.92, 0.92, 0.90, 1.0), roughness=0.4)
mat("lamp_low_voltage", (0.40, 0.06, 0.06, 1.0), roughness=0.3)
mat("radio", (0.12, 0.12, 0.13, 1.0), metallic=0.3, roughness=0.5)
mat("radio_display", (0.08, 0.30, 0.14, 1.0), roughness=0.3, emissive=(0.05, 0.35, 0.12))
mat("yoke", (0.12, 0.12, 0.13, 1.0), roughness=0.55)

GROUPS = ["AIRFRAME", "ENGINE", "IGNITION", "INDUCTION", "FUEL", "OIL", "ELECTRICAL", "VACUUM", "PITOT_STATIC", "PANEL"]
root = g.node("C172N_Phase7", extras={"project": "FlyGACA C172N digital twin", "phase": 7, "units": "m",
                                        "axes": "+Y up, +Z forward, +X left wing",
                                        "geometry_status": "schematic; not from Cessna/Lycoming drawings"})
GN = {}
for name in GROUPS:
    GN[name] = g.node(name, root, t=E if name == "ENGINE" else None, extras={"group": name, "kind": "group"})

INDEX_ROWS = []


def add_part(group, name, geom: Geom, material, pivot=None, parent=None, extras=None):
    """Create a mesh part whose node sits at ``pivot`` (default: bbox centre)."""
    if pivot is None:
        pivot = (geom.v.min(0) + geom.v.max(0)) / 2
    pivot = np.asarray(pivot, float)
    local = Geom(geom.v - pivot, geom.n, geom.f)
    full = f"{group}__{name}"
    mesh = g.mesh(full, local, M[material])
    ex = {"group": group, "part": name}
    if extras:
        ex.update(extras)
    node = g.node(full, GN[group] if parent is None else parent, t=pivot, mesh=mesh, extras=ex)
    INDEX_ROWS.append({"node": full, "group": group, "material": material, "vertices": int(len(geom.v)), **(extras or {})})
    return node


def eng(p):
    """Engine-local point -> airframe coordinates."""
    return np.asarray(p, float) + E


def axis_of(c):
    return np.array([CYL[c]["side"], 0.0, 0.0])


# =================================================================== ENGINE
def build_engine():
    G = "ENGINE"
    # crankcase halves (split vertically like a Lycoming case), nose and accessory housing
    add_part(G, "crankcase_left_half", box(0.115, 0.29, 0.46, (0.0575, -0.005, 0.01)), "crankcase", extras={"xray": True})
    add_part(G, "crankcase_right_half", box(0.115, 0.29, 0.46, (-0.0575, -0.005, 0.01)), "crankcase", extras={"xray": True})
    add_part(G, "nose_section", cylinder(0.085, 0.13, 32).transformed(rot((1, 0, 0), 90), (0, 0, 0.24)), "crankcase",
             extras={"xray": True})
    add_part(G, "accessory_housing", box(0.27, 0.25, 0.07, (0, 0.0, -0.255)), "crankcase", extras={"xray": True})

    # crankshaft node rotates about +Z (viewer sets rotation.z = crank angle)
    shaft = merge(
        cylinder(0.028, 0.66, 24).transformed(rot((1, 0, 0), 90), (0, 0, -0.24)),
        cylinder(0.095, 0.022, 36).transformed(rot((1, 0, 0), 90), (0, 0, 0.40)),
    )
    throws = []
    for c, d in CYL.items():
        a = math.radians(d["pin_deg"])
        pin = np.array([CRANK_R * math.cos(a), CRANK_R * math.sin(a), d["z"]])
        throws.append(cylinder(0.024, 0.04, 20).transformed(rot((1, 0, 0), 90), pin + (0, 0, -0.02)))
        for dz in (-0.026, 0.026):
            web_c = np.array([pin[0] / 2, pin[1] / 2, d["z"] + dz])
            web = box(0.06, CRANK_R + 0.05, 0.012).transformed(align((0, 1, 0), (pin[0], pin[1], 0)), web_c)
            throws.append(web)
    add_part(G, "crankshaft", merge(shaft, *throws), "steel", pivot=(0, 0, 0),
             extras={"anim": "crankshaft", "note": "throws 1&4 and 2&3 paired, 180 deg apart"})

    # camshaft above the crank, turns at half speed (opposite sense, gear driven)
    lobes = []
    for c, d in CYL.items():
        for dz in (-0.035, 0.035):
            lobes.append(sphere(0.022, 12, 8, scale=(1.0, 0.75, 0.45)).moved((0, 0.008, d["z"] + dz)))
    cam = merge(cylinder(0.014, 0.44, 16).transformed(rot((1, 0, 0), 90), (0, 0, -0.22)), *lobes)
    add_part(G, "camshaft", cam, "cam", pivot=(0, 0.085, 0), extras={"anim": "camshaft"})

    for c, d in CYL.items():
        ax = axis_of(c)
        z = d["z"]
        # barrel with cooling fins, along the bank axis
        fins = [cyl_between(ax * s + (0, 0, z), ax * (s + 0.005) + (0, 0, z), 0.090, 28) for s in np.arange(0.150, 0.250, 0.014)]
        barrel = merge(cyl_between(ax * 0.112 + (0, 0, z), ax * 0.262 + (0, 0, z), 0.072, 32), *fins)
        add_part(G, f"cylinder_{c}_barrel", barrel, "cylinder_barrel", pivot=ax * 0.19 + (0, 0, z),
                 extras={"cyl": c, "bank": "L" if d["side"] > 0 else "R", "xray": True})
        head_fins = [box(0.004, 0.17, 0.16).moved(ax * s + (0, 0, z)) for s in np.arange(0.275, 0.345, 0.012)]
        head = merge(box(0.10, 0.15, 0.15).moved(ax * 0.31 + (0, 0, z)), *head_fins)
        add_part(G, f"cylinder_{c}_head", head, "cylinder_head", pivot=ax * 0.31 + (0, 0, z),
                 extras={"cyl": c, "xray": True})
        add_part(G, f"cylinder_{c}_rocker_cover", box(0.03, 0.12, 0.13).moved(ax * 0.375 + (0, 0, z)), "rocker_cover",
                 extras={"cyl": c})

        # piston (node at piston-pin, crown toward the head) - viewer moves it along the axis
        pin_tdc = ax * (CRANK_R + ROD_L) + (0, 0, z)
        piston = merge(
            cyl_between(-ax * 0.040, ax * 0.032, BORE_R, 28),
            cyl_between((0, 0, -0.045), (0, 0, 0.045), 0.012, 12),
        )
        add_part(G, f"piston_{c}", piston.moved(pin_tdc), "piston", pivot=pin_tdc,
                 extras={"anim": "piston", "cyl": c})

        # connecting rod authored along +X from big end (node origin) to small end
        rod = merge(
            box(ROD_L, 0.020, 0.016, (ROD_L / 2, 0, 0)),
            cylinder(0.032, 0.026, 20).transformed(rot((1, 0, 0), 90), (0, 0, -0.013)),
            cylinder(0.019, 0.022, 16).transformed(rot((1, 0, 0), 90), (ROD_L, 0, -0.011)),
        )
        a = math.radians(d["pin_deg"])
        big_end = np.array([CRANK_R * math.cos(a), CRANK_R * math.sin(a), z])
        add_part(G, f"connecting_rod_{c}", rod.moved(big_end), "steel", pivot=big_end,
                 extras={"anim": "conrod", "cyl": c})

        # parallel valves in the head: node at the closed position; viewer opens them toward the crank
        for kind, dz in (("intake", -0.036), ("exhaust", 0.036)):
            seat = ax * 0.262 + (0, -0.03, z + dz)
            valve = merge(cyl_between(seat, seat + ax * 0.075, 0.0055, 10),
                          cyl_between(seat - ax * 0.003, seat + ax * 0.004, 0.022, 20))
            add_part(G, f"{kind}_valve_{c}", valve, "steel", pivot=seat,
                     extras={"anim": f"{kind}_valve", "cyl": c})

        # exhaust riser from the bottom of each head to the muffler
        riser = tube([ax * 0.31 + (0, -0.08, z + 0.036), ax * 0.30 + (0, -0.20, z + 0.05),
                      np.array([0.14 * d["side"], -0.30, 0.25]) - (0, 0, 0)], 0.017, 12)
        add_part(G, f"exhaust_riser_{c}", riser, "exhaust", extras={"cyl": c})

    # muffler / tail pipe (engine frame), carb-heat shroud is part of INDUCTION
    add_part(G, "muffler", cyl_between((-0.22, -0.30, 0.25), (0.22, -0.30, 0.25), 0.055, 24), "exhaust")
    add_part(G, "tail_pipe", tube([(-0.22, -0.30, 0.25), (-0.30, -0.40, 0.12)], 0.025, 12), "exhaust")

    # starter (front lower left) and alternator (front lower right) - illustrative placement
    add_part(G, "starter", merge(cyl_between((0.13, -0.11, 0.22), (0.13, -0.11, 0.38), 0.045, 24),
                                 cyl_between((0.13, -0.11, 0.38), (0.13, -0.11, 0.40), 0.02, 12)), "electrical_part")
    alt = merge(cyl_between((-0.14, -0.10, 0.26), (-0.14, -0.10, 0.36), 0.062, 28),
                cyl_between((-0.14, -0.10, 0.36), (-0.14, -0.10, 0.385), 0.04, 24))
    add_part(G, "alternator", alt, "electrical_part", extras={"rated_amps": 60, "ref": "POH p.7-23/7-25: 60-amp alternator"})
    belt_pts = [(-0.14 + 0.045 * math.cos(t), -0.10 + 0.045 * math.sin(t), 0.375) for t in np.linspace(0, math.pi * 2, 10)]
    add_part(G, "alternator_belt", tube(belt_pts + [(0, 0.098, 0.405), (0.098, 0, 0.405), (0, -0.098, 0.405), belt_pts[0]], 0.006, 6),
             "knob_black")

    # propeller: node rotates with the crank (viewer), blades twisted from 30 deg to 12 deg
    prop_parent = g.node("ENGINE__propeller", GN["ENGINE"], t=(0, 0, 0.43),
                         extras={"group": "ENGINE", "part": "propeller", "anim": "propeller",
                                 "ref": "POH p.2-5: McCauley 1C160/DTM7557, 75 in max diameter"})
    spinner = merge(cylinder(0.135, 0.27, 36, r_top=0.004).transformed(rot((1, 0, 0), 90), (0, 0, 0.02)),
                    cylinder(0.14, 0.02, 36).transformed(rot((1, 0, 0), 90), (0, 0, 0.0)))
    add_part(G, "spinner", spinner, "spinner", pivot=(0, 0, 0.0), parent=prop_parent)
    for k, sign in enumerate((1, -1)):
        def blade_stations(r0, r1, n):
            out = []
            for r in np.linspace(r0, r1, n):
                frac = (r - 0.12) / (0.952 - 0.12)
                chord = 0.16 - 0.06 * frac
                twist = math.radians(30 - 18 * frac)
                cdir = np.array([math.cos(twist), 0, -math.sin(twist)])
                udir = np.array([math.sin(twist), 0, math.cos(twist)])
                le = np.array([0, r, 0.06]) - cdir * chord * 0.35
                out.append((le, chord, cdir, udir))
            return out
        m180 = rot((0, 0, 1), 0 if sign > 0 else 180)
        blade = wing_panel("4410", blade_stations(0.12, 0.86, 9), k=12).transformed(m180)
        tip = wing_panel("4410", blade_stations(0.86, 0.952, 3), k=12).transformed(m180)
        add_part(G, f"propeller_blade_{k + 1}", blade, "prop_blade", pivot=(0, 0, 0.06), parent=prop_parent)
        add_part(G, f"propeller_tip_{k + 1}", tip, "prop_tip", pivot=(0, 0, 0.06), parent=prop_parent)


# ============================================================ IGNITION
def build_ignition():
    G = "IGNITION"
    mag_c = eng((0, 0.155, -0.325))
    add_part(G, "dual_magneto", merge(box(0.15, 0.10, 0.11).moved(mag_c),
                                      cyl_between(mag_c + (0, 0, 0.055), mag_c + (0, 0, 0.08), 0.03, 16)),
             "magneto", extras={"ref": "POH p.7-18: engine-driven dual magneto, two plugs per cylinder"})
    for c, d in CYL.items():
        ax = axis_of(c)
        for pos, sy in (("upper", 1), ("lower", -1)):
            base = ax * 0.31 + (0, 0.075 * sy, d["z"])
            plug = merge(cyl_between(base, base + (0, 0.05 * sy, 0), 0.011, 12),
                         cyl_between(base + (0, 0.012 * sy, 0), base + (0, 0.024 * sy, 0), 0.016, 6))
            mg = plug_magneto(c, pos)
            add_part(G, f"plug_c{c}_{pos}", plug.moved(E), "spark_plug", pivot=eng(base),
                     extras={"cyl": c, "position": pos, "magneto": mg, "anim": "spark"})
            # lead from the matching side of the dual magneto
            start = mag_c + ((0.045 if mg == "L" else -0.045), 0.05, 0.0)
            tip_pt = eng(base + (0, 0.055 * sy, 0))
            if pos == "upper":
                pts = [start, start + (0, 0.05, 0), eng((ax[0] * 0.20, 0.25, d["z"])), tip_pt + (0, 0.02, 0), tip_pt]
            else:
                pts = [start, start + (ax[0] * 0.07, 0, 0), eng((ax[0] * 0.16, -0.05, -0.30)),
                       eng((ax[0] * 0.24, -0.17, d["z"])), tip_pt]
            add_part(G, f"lead_c{c}_{pos}", tube(pts, 0.0045, 6), "ignition_lead",
                     extras={"cyl": c, "position": pos, "magneto": mg})


# ============================================================ INDUCTION
def build_induction():
    G = "INDUCTION"
    carb = eng((0, -0.315, -0.10))
    add_part(G, "carburetor", merge(box(0.10, 0.07, 0.09).moved(carb), cyl_between(carb + (0, -0.035, 0), carb + (0, -0.06, 0), 0.035, 20)),
             "carburetor", extras={"ref": "POH p.7-19: up-draft, float-type, fixed-jet carburetor with idle cut-off"})
    airbox = eng((0, -0.40, -0.10))
    add_part(G, "airbox_with_carb_heat_valve", box(0.18, 0.06, 0.15).moved(airbox), "induction")
    add_part(G, "induction_air_filter", box(0.20, 0.10, 0.035).moved((0, 0.86, 1.99)), "air_filter",
             extras={"ref": "POH p.7-19: ram-air intake with filter in lower front cowling"})
    add_part(G, "ram_air_duct", tube([(0, 0.86, 1.97), (0, 0.80, 1.80), airbox + (0, 0, 0.06)], 0.035, 14), "induction")
    add_part(G, "intake_riser", cyl_between(eng((0, -0.28, -0.10)), eng((0, -0.17, -0.06)), 0.03, 16), "induction")
    for c, d in CYL.items():
        ax = axis_of(c)
        pts = [eng((0, -0.18, -0.06)), eng((ax[0] * 0.13, -0.19, d["z"] - 0.03)), eng(ax * 0.29 + (0, -0.11, d["z"] - 0.036)),
               eng(ax * 0.30 + (0, -0.07, d["z"] - 0.036))]
        add_part(G, f"intake_tube_{c}", tube(pts, 0.018, 12), "induction", extras={"cyl": c})
    shroud_c0, shroud_c1 = eng((-0.16, -0.30, 0.25)), eng((0.16, -0.30, 0.25))
    add_part(G, "carb_heat_shroud", cyl_between(shroud_c0, shroud_c1, 0.068, 24), "ghost_surface",
             extras={"ref": "POH p.7-19: heated air from a shroud around an exhaust riser"})
    add_part(G, "carb_heat_duct", tube([eng((0.10, -0.33, 0.21)), eng((0.12, -0.40, 0.05)), airbox + (0.07, 0, 0.02)], 0.025, 12),
             "induction")


# ============================================================ FUEL
TANK = {"L": {"x0": 0.70, "x1": 1.95, "sign": 1}, "R": {"x0": -1.95, "x1": -0.70, "sign": -1}}
TANK_Y0, TANK_H, TANK_Z0, TANK_Z1 = 2.03, 0.12, -0.35, 0.42


def wing_y(x):
    """Chord-line height: 1 deg 44 min dihedral from the root (illustrative)."""
    return 2.05 + math.tan(math.radians(1.73)) * max(abs(x) - 0.56, 0)


def planform(x):
    """(leading-edge z, chord) - constant chord to 2.6 m, then tapered to the tip."""
    x = abs(x)
    if x <= 2.60:
        return 0.62, 1.63
    f = (x - 2.60) / (5.40 - 2.60)
    return 0.62 - 0.20 * f, 1.63 - 0.51 * f


def build_fuel():
    G = "FUEL"
    for side, t in TANK.items():
        cx = (t["x0"] + t["x1"]) / 2
        w = t["x1"] - t["x0"]
        y0 = wing_y(cx) - 0.05
        add_part(G, f"tank_{side}", box(w, TANK_H, TANK_Z1 - TANK_Z0).moved((cx, y0 + TANK_H / 2, (TANK_Z0 + TANK_Z1) / 2)),
                 "fuel_tank", extras={"side": side, "ref": "POH p.7-21: standard tanks 21.5 gal each, 20 usable"})
        level = box(w - 0.02, TANK_H - 0.01, TANK_Z1 - TANK_Z0 - 0.02).moved((cx, y0 + 0.005 + (TANK_H - 0.01) / 2, (TANK_Z0 + TANK_Z1) / 2))
        add_part(G, f"fuel_level_{side}", level, "avgas_100ll", pivot=(cx, y0 + 0.005, (TANK_Z0 + TANK_Z1) / 2),
                 extras={"side": side, "anim": "fuel_level"})
        cap_x = cx
        add_part(G, f"filler_cap_{side}", cyl_between((cap_x, wing_y(cap_x) + 0.09, 0.02), (cap_x, wing_y(cap_x) + 0.115, 0.02), 0.04, 20),
                 "fuel_valve", extras={"side": side})
        s = t["sign"]
        line = [(s * 0.74, y0 + 0.01, 0.38), (s * 0.58, y0 - 0.02, 0.60), (s * 0.56, 1.30, 0.66), (s * 0.54, 0.86, 0.62),
                (s * 0.12, 0.80, 0.46), (s * 0.03, 0.80, 0.41)]
        add_part(G, f"tank_outlet_line_{side}", tube(line, 0.010, 10), "fuel_line", extras={"side": side})
    add_part(G, "selector_valve_body", cylinder(0.055, 0.035, 28).moved((0, 0.77, 0.40)), "fuel_valve",
             extras={"ref": "POH p.7-20: four-position selector BOTH, RIGHT, LEFT, OFF"})
    handle = merge(box(0.025, 0.02, 0.11, (0, 0.0, 0.035)), cyl_between((0, -0.01, 0), (0, 0.012, 0), 0.02, 16))
    add_part(G, "selector_handle", handle.moved((0, 0.817, 0.40)), "knob_red", pivot=(0, 0.817, 0.40), extras={"anim": "fuel_selector"})
    add_part(G, "selector_to_strainer_line", tube([(0, 0.79, 0.44), (0, 0.80, 0.92), (-0.06, 0.90, 1.03)], 0.011, 10), "fuel_line")
    strainer = (-0.07, 0.94, 1.06)
    add_part(G, "fuel_strainer", merge(box(0.07, 0.06, 0.06).moved(strainer), cyl_between(np.add(strainer, (0, -0.03, 0)), np.add(strainer, (0, -0.075, 0)), 0.025, 16)),
             "fuel_valve", extras={"ref": "POH p.7-20: fuel strainer between selector and carburetor"})
    carb = eng((0, -0.315, -0.10))
    add_part(G, "strainer_to_carburetor_line", tube([np.add(strainer, (0.0, 0.0, 0.03)), (-0.05, 0.94, 1.20), carb + (-0.05, 0.0, 0)], 0.010, 10),
             "fuel_line")
    add_part(G, "primer_line", tube([np.add(strainer, (0.03, 0.02, 0)), (0.30, 1.05, 0.95), (0.47, 1.12, 0.82)], 0.004, 6), "fuel_line",
             extras={"ref": "POH p.7-20: manual primer draws fuel from the strainer"})


# ============================================================ OIL
def build_oil():
    G = "OIL"
    add_part(G, "sump", box(0.26, 0.13, 0.36).moved(eng((0, -0.215, 0.0))), "oil_part",
             extras={"capacity_qt": 6, "ref": "POH p.7-18: six-quart sump; do not operate below four quarts"})
    flt = eng((-0.085, 0.02, -0.33))
    add_part(G, "oil_filter_or_screen", cyl_between(flt, flt + (0, 0, -0.09), 0.042, 24), "oil_line")
    cooler = (-0.36, 0.98, 1.035)
    add_part(G, "oil_cooler", merge(box(0.22, 0.15, 0.045).moved(cooler), *[box(0.215, 0.004, 0.05).moved((cooler[0], cooler[1] - 0.06 + 0.015 * i, cooler[2])) for i in range(9)]),
             "oil_part", extras={"ref": "POH p.7-18: oil cooler on the lower right side of the firewall"})
    add_part(G, "cooler_supply_line", tube([eng((-0.12, -0.05, -0.30)), eng((-0.26, -0.15, -0.36)), np.add(cooler, (0.08, 0.0, 0.03))], 0.009, 10), "oil_line")
    add_part(G, "cooler_return_line", tube([np.add(cooler, (-0.06, -0.04, 0.03)), eng((-0.30, -0.22, -0.34)), eng((-0.11, -0.10, -0.30))], 0.009, 10), "oil_line")
    add_part(G, "filler_cap_dipstick", merge(cyl_between(eng((0.0, 0.10, -0.31)), eng((0.0, 0.25, -0.33)), 0.012, 12),
                                             cyl_between(eng((0.0, 0.25, -0.33)), eng((0.0, 0.27, -0.33)), 0.022, 16)), "oil_line",
             extras={"ref": "POH p.7-18: filler cap/dipstick at the rear of the engine"})
    for i, zz in enumerate((-0.12, 0.12)):
        add_part(G, f"gallery_{i}", cyl_between(eng((0.0, -0.12, zz)), eng((0.0, 0.06, zz)), 0.007, 8), "oil_line")


# ============================================================ ELECTRICAL
def build_electrical():
    G = "ELECTRICAL"
    bat = np.array([0.30, 1.30, 1.10])
    add_part(G, "battery", box(0.24, 0.18, 0.16).moved(bat), "battery",
             extras={"volts": 24, "ref": "POH p.7-25: 24-volt battery, left forward side of the firewall"})
    add_part(G, "battery_terminal_positive", cyl_between(bat + (-0.07, 0.09, 0), bat + (-0.07, 0.115, 0), 0.014, 12), "terminal_pos")
    add_part(G, "battery_terminal_negative", cyl_between(bat + (0.07, 0.09, 0), bat + (0.07, 0.115, 0), 0.014, 12), "terminal_neg")
    bc = np.array([0.30, 1.12, 1.035])
    add_part(G, "battery_contactor", merge(cylinder(0.035, 0.07, 20).moved(bc - (0, 0.035, 0)), box(0.09, 0.02, 0.06).moved(bc - (0, 0.04, 0))),
             "electrical_part", extras={"ref": "POH p.7-24 Fig 7-7 (battery contactor), controlled by BAT half of master"})
    sc = np.array([0.15, 1.00, 1.035])
    add_part(G, "starter_contactor", cylinder(0.03, 0.06, 20).moved(sc - (0, 0.03, 0)), "electrical_part")
    acu = np.array([-0.27, 1.36, 1.03])
    add_part(G, "alternator_control_unit", box(0.11, 0.08, 0.04).moved(acu), "electrical_part",
             extras={"ref": "POH p.7-26: regulator with high-low voltage control on the engine side of the firewall"})
    add_part(G, "primary_bus_bar", box(0.22, 0.015, 0.015).moved((0.18, 1.05, 0.835)), "terminal_pos")
    add_part(G, "avionics_bus_bar", box(0.12, 0.015, 0.015).moved((-0.12, 1.05, 0.835)), "terminal_pos",
             extras={"ref": "POH p.7-25: avionics bus fed through AVIONICS POWER switch/breaker"})
    starter = eng((0.13, -0.11, 0.30))
    alt = eng((-0.14, -0.10, 0.31))
    cables = {
        "cable_battery_to_contactor": [bat + (-0.07, 0.115, 0), bat + (-0.07, 0.14, -0.06), bc + (0, 0.0, 0.0)],
        "cable_contactor_to_starter_contactor": [bc - (0.03, 0.03, 0), sc + (0.02, 0.0, 0)],
        "cable_starter_contactor_to_starter": [sc + (0, -0.03, 0), (0.16, 0.98, 1.20), starter + (0.02, -0.03, -0.06)],
        "cable_contactor_to_primary_bus": [bc + (-0.02, 0.0, -0.02), (0.25, 1.06, 1.00), (0.22, 1.05, 0.84)],
        "cable_alternator_output": [alt + (-0.04, -0.03, -0.04), (-0.22, 1.00, 1.18), (-0.20, 1.02, 1.00), (0.08, 1.05, 0.84)],
        "wire_alternator_field": [acu + (0.0, -0.04, 0.0), (-0.24, 1.22, 1.12), alt + (-0.02, 0.05, -0.02)],
    }
    for name, pts in cables.items():
        add_part(G, name, tube([np.asarray(p, float) for p in pts], 0.008 if "wire" not in name else 0.004, 8), "electric_cable")


# ============================================================ VACUUM
def build_vacuum():
    G = "VACUUM"
    pump = eng((0.095, -0.04, -0.33))
    add_part(G, "engine_driven_pump", cyl_between(pump, pump + (0, 0, -0.075), 0.042, 24), "vacuum_part",
             extras={"ref": "POH p.7-32: engine-driven vacuum system for attitude and directional indicators"})
    relief = np.array([0.20, 0.97, 0.90])
    filt = np.array([0.30, 0.97, 0.88])
    add_part(G, "relief_valve", cylinder(0.022, 0.04, 16).moved(relief - (0, 0.02, 0)), "vacuum_part")
    add_part(G, "system_air_filter", box(0.07, 0.05, 0.05).moved(filt), "vacuum_part")
    add_part(G, "line_pump_to_relief_valve", tube([pump + (0, 0, -0.075), (0.11, 1.10, 1.02), (0.13, 1.00, 0.96), relief + (0, 0, 0.0)], 0.008, 8), "vacuum_line")
    add_part(G, "line_gyros", tube([relief + (0.0, 0.02, -0.01), (0.335, 1.25, 0.84), (0.335, 1.295, 0.835)], 0.006, 8), "vacuum_line")
    add_part(G, "line_gyro_crossover", tube([(0.335, 1.295, 0.835), (0.335, 1.40, 0.835)], 0.006, 8), "vacuum_line")
    add_part(G, "line_filter_to_gyros", tube([filt + (0.0, 0.02, -0.01), (0.31, 1.20, 0.84), (0.335, 1.40, 0.838)], 0.006, 8), "vacuum_line")
    add_part(G, "line_suction_gauge", tube([relief + (-0.01, 0.02, -0.01), (0.15, 1.30, 0.835), (0.125, 1.40, 0.835)], 0.004, 6), "vacuum_line")


# ============================================================ PITOT-STATIC
def build_pitot_static():
    G = "PITOT_STATIC"
    px = 2.45
    yb = wing_y(px) - 0.06
    tube_pts = merge(cyl_between((px, yb, 0.38), (px, yb - 0.09, 0.40), 0.012, 12),
                     cyl_between((px, yb - 0.09, 0.40), (px, yb - 0.09, 0.66), 0.011, 14))
    add_part(G, "pitot_tube", tube_pts, "pitot_tube", extras={"ref": "POH p.7-31: pitot tube on the lower surface of the left wing"})
    add_part(G, "pitot_line", tube([(px, yb, 0.38), (0.64, wing_y(0.64) - 0.06, 0.38), (0.57, 1.95, 0.62), (0.56, 1.45, 0.72),
                                    (0.47, 1.40, 0.825), (0.44, 1.40, 0.83)], 0.006, 8), "pitot_line")
    port = np.array([0.535, 1.02, 0.56])
    add_part(G, "static_port", cyl_between(port, port + (0.008, 0, 0), 0.022, 20), "pitot_tube",
             extras={"ref": "POH p.7-31: external static port, lower left side of forward fuselage"})
    manifold = np.array([0.33, 1.345, 0.84])
    add_part(G, "static_line_main", tube([port, (0.46, 1.04, 0.72), (0.40, 1.20, 0.84), manifold], 0.006, 8), "static_line")
    for name, p in (("asi", (0.44, 1.40, 0.83)), ("altimeter", (0.23, 1.40, 0.83)), ("vsi", (0.23, 1.295, 0.83))):
        add_part(G, f"static_branch_{name}", tube([manifold, p], 0.005, 8), "static_line")
    add_part(G, "alternate_static_line", tube([(0.02, 1.025, 0.82), (0.20, 1.20, 0.84), manifold], 0.005, 8), "static_line",
             extras={"ref": "POH p.7-31: alternate static source valve (if installed) below the throttle"})


# ============================================================ PANEL
PANEL_Z = 0.81  # panel mid-plane; pilot side faces -Z
FACE_Z = -0.011


def value_to_angle(spec, v):
    pts = spec["map"]
    if spec.get("wrap"):
        span = pts[-1][0] - pts[0][0]
        v = pts[0][0] + ((v - pts[0][0]) % span)
    v = min(max(v, pts[0][0]), pts[-1][0])
    for (v0, a0), (v1, a1) in zip(pts, pts[1:]):
        if v <= v1:
            return a0 + (a1 - a0) * (v - v0) / (v1 - v0)
    return pts[-1][1]


def gauge(key, x, y, rf):
    """Instrument at (x, y) on the panel. Returns the gauge node index."""
    spec = INSTR.get(key)
    node = g.node(f"PANEL__{key}", GN["PANEL"], t=(x, y, PANEL_Z - 0.0125),
                  extras={"group": "PANEL", "part": key, "instrument": key})

    def child(name, geom, material, extras=None, t=None):
        mesh = g.mesh(f"PANEL__{key}__{name}", geom, M[material])
        ex = {"group": "PANEL", "part": f"{key}__{name}", "instrument": key}
        if extras:
            ex.update(extras)
        return g.node(f"PANEL__{key}__{name}", node, t=t, mesh=mesh, extras=ex)

    rb = rf * 1.16
    child("bezel", disc(rb, 0.010, 40), "bezel")
    child("face", disc(rf, 0.011, 40), "dial_face")
    if spec:
        bands = {"outer": (rf * 0.84, rf * 0.95), "inner": (rf * 0.74, rf * 0.83)}
        by_color = {}
        for arc in spec["arcs"]:
            r0, r1 = bands[arc["band"]]
            by_color.setdefault(arc["color"], []).append(
                arc_band(r0, r1, value_to_angle(spec, arc["from"]), value_to_angle(spec, arc["to"])).moved((0, 0, FACE_Z)))
        for color, parts in by_color.items():
            child(f"arc_{color}", merge(*parts), f"arc_{color}")
        if spec["redlines"]:
            reds = [tick(value_to_angle(spec, r["value"]), rf * 0.72, rf * 0.97, rf * 0.06).moved((0, 0, FACE_Z - 0.001))
                    for r in spec["redlines"]]
            child("red_line", merge(*reds), "red_line")
        t = spec["ticks"]
        marks = [tick(value_to_angle(spec, v), rf * 0.80, rf * 0.97, rf * 0.035).moved((0, 0, FACE_Z - 0.0008)) for v in t["major"]]
        v = t["minor_from"]
        while v <= spec["max"] + 1e-9:
            if not any(abs(v - m) < 1e-9 for m in t["major"]):
                marks.append(tick(value_to_angle(spec, v), rf * 0.88, rf * 0.97, rf * 0.02).moved((0, 0, FACE_Z - 0.0008)))
            v += t["minor_step"]
        child("marks", merge(*marks), "dial_white")
    return node, child


def needle_geom(length, width, tail=0.18):
    return merge(box(width, length * (1 + tail), 0.0015, (0, length * (1 - tail) / 2, 0)),
                 cylinder(width * 1.4, 0.0025, 16).transformed(rot((1, 0, 0), -90), (0, 0, 0.001)))


def build_panel():
    G = "PANEL"
    add_part(G, "instrument_panel", box(1.16, 0.54, 0.025).moved((0, 1.25, PANEL_Z)), "panel")
    add_part(G, "glare_shield", box(1.18, 0.035, 0.12).moved((0, 1.535, PANEL_Z - 0.03)), "panel")
    big, small = 0.040, 0.022
    layout = {"ASI": (0.44, 1.40, big), "ALT": (0.23, 1.40, big), "VSI": (0.23, 1.295, big), "TACH": (0.23, 1.19, big),
              "SUCTION": (0.125, 1.40, small), "FUEL_L": (0.535, 1.43, small), "FUEL_R": (0.535, 1.375, small),
              "OIL_T": (0.535, 1.32, small), "OIL_P": (0.535, 1.265, small), "AMMETER": (0.535, 1.195, small)}
    for key, (x, y, rf) in layout.items():
        node, child = gauge(key, x, y, rf)
        if key == "ALT":
            child("needle_100ft", needle_geom(rf * 0.86, rf * 0.06), "needle", {"anim": "needle", "scale": "ALT"}, t=(0, 0, FACE_Z - 0.0035))
            child("needle_1000ft", needle_geom(rf * 0.55, rf * 0.11), "needle", {"anim": "needle", "scale": "ALT_1000"}, t=(0, 0, FACE_Z - 0.0025))
        else:
            child("needle", needle_geom(rf * 0.86, rf * 0.07), "needle", {"anim": "needle", "scale": key}, t=(0, 0, FACE_Z - 0.0025))

    # attitude indicator: horizon card rotates with bank and slides with pitch
    node, child = gauge("AI", 0.335, 1.40, big)
    sky = arc_band(0.0001, big * 0.97, -90, 90, steps=24)
    gnd = arc_band(0.0001, big * 0.97, 90, 270, steps=24)
    hor = g.node("PANEL__AI__horizon", node, t=(0, 0, FACE_Z - 0.0002), extras={"group": "PANEL", "part": "AI__horizon", "anim": "ai_horizon"})
    g.node("PANEL__AI__horizon_sky", hor, mesh=g.mesh("PANEL__AI__horizon_sky", sky, M["ai_sky"]), extras={"group": "PANEL", "part": "AI__horizon_sky"})
    g.node("PANEL__AI__horizon_ground", hor, mesh=g.mesh("PANEL__AI__horizon_ground", gnd, M["ai_ground"]), extras={"group": "PANEL", "part": "AI__horizon_ground"})
    g.node("PANEL__AI__horizon_line", hor, mesh=g.mesh("PANEL__AI__horizon_line", box(big * 1.9, 0.0016, 0.001, (0, 0, -0.0017)), M["dial_white"]),
           extras={"group": "PANEL", "part": "AI__horizon_line"})
    child("miniature_airplane", merge(box(big * 0.9, 0.003, 0.002), box(0.004, 0.006, 0.002, (0, 0.003, 0))), "ai_symbol",
          t=(0, 0, FACE_Z - 0.004))
    child("bank_marks", merge(*[tick(a, big * 0.86, big * 0.98, 0.0016) for a in (-60, -30, -20, -10, 0, 10, 20, 30, 60)]).moved((0, 0, FACE_Z - 0.003)), "dial_white")

    # heading indicator: card rotates (rotation.z = -heading)
    node, child = gauge("HI", 0.335, 1.295, big)
    card_marks = [tick(a, big * (0.70 if a % 30 else 0.62), big * 0.92, 0.0014 if a % 90 else 0.0028) for a in range(0, 360, 10)]
    card = g.node("PANEL__HI__card", node, t=(0, 0, FACE_Z - 0.0012), extras={"group": "PANEL", "part": "HI__card", "anim": "hi_card"})
    g.node("PANEL__HI__card_marks", card, mesh=g.mesh("PANEL__HI__card_marks", merge(*card_marks), M["dial_white"]),
           extras={"group": "PANEL", "part": "HI__card_marks"})
    g.node("PANEL__HI__card_north", card, mesh=g.mesh("PANEL__HI__card_north", tick(0, big * 0.50, big * 0.92, 0.004), M["red_line"]),
           extras={"group": "PANEL", "part": "HI__card_north"})
    child("lubber_line", merge(tick(0, big * 0.92, big * 1.0, 0.003), tick(180, big * 0.92, big * 1.0, 0.003)), "ai_symbol", t=(0, 0, FACE_Z - 0.003))
    child("airplane_symbol", merge(box(big * 0.6, 0.0025, 0.0015), box(0.0025, big * 0.5, 0.0015, (0, -0.004, 0))), "ai_symbol",
          t=(0, 0, FACE_Z - 0.003))

    # turn coordinator: miniature airplane rotates with standard-rate turn
    node, child = gauge("TC", 0.44, 1.295, big)
    child("marks", merge(tick(-90, big * 0.78, big * 0.95, 0.002), tick(90, big * 0.78, big * 0.95, 0.002),
                         tick(-110, big * 0.78, big * 0.95, 0.002), tick(110, big * 0.78, big * 0.95, 0.002)).moved((0, 0, FACE_Z - 0.0008)), "dial_white")
    child("airplane", merge(box(big * 1.4, 0.003, 0.0015), box(0.006, 0.008, 0.0015, (0, 0.004, 0)), box(big * 0.4, 0.0025, 0.0015, (0, -0.012, 0))),
          "dial_white", {"anim": "tc_airplane"}, t=(0, 0, FACE_Z - 0.003))
    child("ball_tube", box(big * 0.9, 0.009, 0.001, (0, -big * 0.55, 0)).moved((0, 0, FACE_Z - 0.0015)), "bezel")

    # low-voltage warning light below the ammeter (POH p.7-26)
    add_part(G, "LOW_VOLTAGE_light", cylinder(0.009, 0.012, 16).transformed(rot((1, 0, 0), -90), (0.535, 1.150, PANEL_Z - 0.0125)),
             "lamp_low_voltage", pivot=(0.535, 1.150, PANEL_Z - 0.0125), extras={"anim": "low_voltage_lamp", "ref": "POH p.7-26"})

    # ignition switch OFF-R-L-BOTH-START (POH p.7-19); key rotates about Z
    sw = np.array([0.49, 1.055, PANEL_Z - 0.0125])
    add_part(G, "ignition_switch_body", cylinder(0.022, 0.012, 24).transformed(rot((1, 0, 0), -90), sw), "bezel", pivot=sw)
    add_part(G, "ignition_switch_key", merge(box(0.009, 0.032, 0.008, (0, 0, -0.016)), box(0.016, 0.010, 0.010, (0, 0.014, -0.02))).moved(sw),
             "knob_white", pivot=sw, extras={"anim": "ignition_key", "positions": "OFF,R,L,BOTH,START"})

    # split master switch: ALT (left half) and BAT (right half), POH p.7-25
    for half, xx in (("ALT", 0.415), ("BAT", 0.393)):
        p = np.array([xx, 1.055, PANEL_Z - 0.0125])
        add_part(G, f"master_{half}", box(0.02, 0.04, 0.012, (0, 0, -0.006)).moved(p), "knob_red" if half == "BAT" else "switch_white",
                 pivot=p, extras={"anim": f"master_{half.lower()}"})
    av = np.array([0.345, 1.055, PANEL_Z - 0.0125])
    add_part(G, "avionics_power_switch", merge(box(0.014, 0.02, 0.005), cyl_between((0, 0, 0), (0, 0.006, -0.02), 0.003, 8)).moved(av), "switch_white", pivot=av,
             extras={"anim": "avionics_switch"})
    for i in range(8):
        p = np.array([0.27 - i * 0.025, 1.04, PANEL_Z - 0.0125])
        add_part(G, f"circuit_breaker_{i + 1}", cylinder(0.006, 0.010, 12).transformed(rot((1, 0, 0), -90), p), "bezel", pivot=p)

    # engine controls: push-pull knobs move along Z (viewer offsets them)
    for name, x, material, r in (("throttle", 0.02, "knob_black", 0.016), ("mixture", -0.05, "knob_red", 0.014), ("carb_heat", 0.09, "knob_black", 0.012),
                                 ("primer", 0.47, "knob_black", 0.008), ("alternate_static", 0.02, "knob_black", 0.008)):
        y = 1.025 if name == "alternate_static" else (1.12 if name == "primer" else 1.08)
        p = np.array([x, y, PANEL_Z - 0.0125])
        knob = merge(cyl_between((0, 0, 0), (0, 0, -0.04), 0.0035, 8), cyl_between((0, 0, -0.04), (0, 0, -0.05), r, 20))
        add_part(G, f"{name}_knob", knob.moved(p), material, pivot=p, extras={"anim": f"{name}_knob"})

    # radios (illustrative stack)
    for i, (label, yy, hh) in enumerate((("audio_panel", 1.465, 0.035), ("nav_com_1", 1.395, 0.07), ("nav_com_2", 1.315, 0.07), ("transponder", 1.24, 0.05))):
        p = np.array([-0.15, yy, PANEL_Z - 0.0125 - 0.01])
        add_part(G, f"radio_{label}", box(0.22, hh, 0.02).moved(p), "radio", pivot=p)
        add_part(G, f"radio_{label}_display", box(0.08, hh * 0.4, 0.002).moved(p + (0.03, 0.0, -0.011)), "radio_display")


# ============================================================ AIRFRAME
def build_airframe():
    G = "AIRFRAME"
    cowl = [(2.03, 1.19, 0.17, 0.17, 2.0), (1.95, 1.18, 0.40, 0.33, 2.4), (1.60, 1.16, 0.50, 0.38, 2.6), (1.00, 1.20, 0.53, 0.42, 2.6)]
    add_part(G, "engine_cowling", loft([superellipse_ring(0, yc, z, hw, hh, n) for z, yc, hw, hh, n in cowl], cap_start=False, cap_end=False),
             "ghost_airframe")
    fus = [(1.00, 1.22, 0.53, 0.44), (0.75, 1.36, 0.55, 0.60), (0.30, 1.40, 0.56, 0.66), (-0.60, 1.42, 0.55, 0.62), (-1.30, 1.47, 0.48, 0.50),
           (-2.20, 1.52, 0.38, 0.36), (-3.30, 1.55, 0.28, 0.26), (-4.40, 1.58, 0.18, 0.18), (-5.40, 1.62, 0.09, 0.12), (-5.95, 1.65, 0.035, 0.06)]
    add_part(G, "fuselage", loft([superellipse_ring(0, yc, z, hw, hh) for z, yc, hw, hh in fus], cap_start=False), "ghost_airframe",
             extras={"ref": "POH Figure 1-1: overall length 26 ft 11 in (envelope only)"})
    add_part(G, "firewall", loft([superellipse_ring(0, 1.20, 1.0, 0.52, 0.41), superellipse_ring(0, 1.20, 0.995, 0.52, 0.41)]), "firewall")

    for side, s in (("L", 1), ("R", -1)):
        def st(x):
            le_z, chord = planform(x)
            return ((s * x, wing_y(x), le_z), chord, (0, 0, -1), (0, 1, 0))
        main = wing_panel("2412", [st(0.56), st(2.60), st(5.40)], 0.0, 0.75)
        tip_te = wing_panel("2412", [st(5.05), st(5.40)], 0.75, 1.0)
        add_part(G, f"wing_{side}", merge(main, tip_te), "ghost_airframe",
                 extras={"side": side, "ref": "POH Figure 1-1: 36 ft span; NACA 2412 section is illustrative"})
        add_part(G, f"flap_{side}", wing_panel("2412", [st(0.58), st(2.60), st(2.85)], 0.75, 1.0), "ghost_surface", extras={"side": side})
        add_part(G, f"aileron_{side}", wing_panel("2412", [st(2.87), st(5.03)], 0.75, 1.0), "ghost_surface", extras={"side": side})
        add_part(G, f"wing_strut_{side}", cyl_between((s * 0.50, 0.86, 0.05), (s * 2.90, wing_y(2.9) - 0.03, 0.10), 0.03, 12), "ghost_surface")
        add_part(G, f"main_gear_leg_{side}", tube([(s * 0.45, 0.80, -0.10), (s * 1.15, 0.24, -0.18)], 0.03, 12), "gear")
        add_part(G, f"main_wheel_{side}", cyl_between((s * 1.18, 0.19, -0.18), (s * 1.31, 0.19, -0.18), 0.19, 28), "tire")

        def hs(x, le_z, chord):
            return ((s * x, 1.62, le_z), chord, (0, 0, -1), (0, 1, 0))
        add_part(G, f"horizontal_stabilizer_{side}", wing_panel("0009", [hs(0.08, -4.95, 1.05), hs(1.72, -5.12, 0.80)], 0.0, 0.62), "ghost_airframe",
                 extras={"side": side})
        add_part(G, f"elevator_{side}", wing_panel("0009", [hs(0.08, -4.95, 1.05), hs(1.72, -5.12, 0.80)], 0.62, 1.0), "ghost_surface",
                 extras={"side": side})

    def vs(y, le_z, chord):
        return ((0, y, le_z), chord, (0, 0, -1), (1, 0, 0))
    add_part(G, "vertical_stabilizer", wing_panel("0009", [vs(1.72, -4.30, 1.40), vs(2.64, -5.42, 0.42)], 0.0, 0.73), "ghost_airframe")
    add_part(G, "rudder", wing_panel("0009", [vs(1.66, -4.62, 1.43), vs(2.66, -5.42, 0.62)], 0.70, 1.0), "ghost_surface")
    add_part(G, "nose_gear_strut", tube([(0, 0.85, 1.05), (0, 0.30, 1.55), (0, 0.17, 1.62)], 0.035, 12), "gear")
    add_part(G, "nose_wheel", cyl_between((-0.055, 0.17, 1.62), (0.055, 0.17, 1.62), 0.17, 28), "tire")
    for side, x in (("pilot", 0.335), ("copilot", -0.335)):
        yoke = merge(cyl_between((x, 1.10, PANEL_Z), (x, 1.10, 0.62), 0.012, 12),
                     box(0.24, 0.03, 0.03, (x, 1.12, 0.61)),
                     cyl_between((x + 0.12, 1.12, 0.61), (x + 0.12, 1.20, 0.60), 0.016, 12),
                     cyl_between((x - 0.12, 1.12, 0.61), (x - 0.12, 1.20, 0.60), 0.016, 12))
        add_part(G, f"control_wheel_{side}", yoke, "yoke")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=pathlib.Path, default=OUT, help="GLB output path")
    ap.add_argument("--index", type=pathlib.Path, default=INDEX, help="model_index.json output path")
    args = ap.parse_args(argv)
    build_airframe()
    build_engine()
    build_ignition()
    build_induction()
    build_fuel()
    build_oil()
    build_electrical()
    build_vacuum()
    build_pitot_static()
    build_panel()
    data = g.to_bytes()
    args.out.write_bytes(data)
    counts = {}
    for row in INDEX_ROWS:
        counts[row["group"]] = counts.get(row["group"], 0) + 1
    mesh_nodes = sum(1 for n in g.doc["nodes"] if "mesh" in n)
    args.index.write_text(json.dumps({
        "file": OUT.name,
        "bytes": len(data),
        "nodes": len(g.doc["nodes"]),
        "mesh_nodes": mesh_nodes,
        "materials": len(g.doc["materials"]),
        "top_level_parts_by_group": dict(sorted(counts.items())),
        "engine_origin_m": [float(x) for x in E],
        "crank_radius_m": CRANK_R,
        "rod_length_m": ROD_L,
        "cylinders": {str(k): {"bank": "L" if v["side"] > 0 else "R", "z_m": v["z"], "crank_pin_deg": v["pin_deg"]} for k, v in CYL.items()},
        "firing_order": FIRING_ORDER,
        "plug_magneto_map": {f"c{c}_{p}": plug_magneto(c, p) for c in CYL for p in ("upper", "lower")},
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({len(data) / 1024:.0f} KiB, {len(g.doc['nodes'])} nodes, {mesh_nodes} meshes)")


if __name__ == "__main__":
    main()
