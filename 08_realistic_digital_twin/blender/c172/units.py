"""Reference dimensions used by the Phase 8 model.

Every value carries a status:
  poh        — 1979 Cessna 172N Pilot's Operating Handbook (page cited)
  type_data  — published type data, not from the POH; confirm against TCDS 3A12 / E-274
  estimated  — proportions estimated from photographs / general arrangement; not manufacturer data

Frames
------
Blender build frame: Z up, -Y forward (nose), +X right wing. Ground plane z = 0 (tyres touch).
Fuselage station (FS, inches, POH datum = front face of firewall): y = (FS - FS_ORIGIN) * IN
with FS_ORIGIN = 40 so the model origin is near the CG range (POH p.6-x: 35.0–47.3 in).
Butt line (BL, inches from centreline): x = BL * IN. Water line here is simply z in metres.
"""
IN = 0.0254
FT = 0.3048
FS_ORIGIN = 40.0

def fs(station_in):
    """Fuselage station (inches aft of firewall) -> Blender y (metres, +aft)."""
    return (station_in - FS_ORIGIN) * IN

def bl(butt_in):
    return butt_in * IN

REF = {
    # ---- POH (Section 1, Figure 1-1 unless noted)
    "wingspan_m":        dict(v=35 * FT + 10 * IN, status="poh", ref="Fig 1-1, p.1-2 (35 ft 10 in)"),
    "length_m":          dict(v=26 * FT + 11 * IN, status="poh", ref="Fig 1-1, p.1-2 (26 ft 11 in)"),
    "height_m":          dict(v=8 * FT + 9.5 * IN, status="poh", ref="Fig 1-1, p.1-2 (8 ft 9½ in)"),
    "prop_diameter_m":   dict(v=75 * IN, status="poh", ref="p.1-3 (75 in maximum)"),
    "engine":            dict(v="Lycoming O-320-H2AD, 160 BHP at 2700 RPM", status="poh", ref="p.1-3"),
    "fuel_total_gal":    dict(v=43, status="poh", ref="p.1-4 (standard tanks)"),
    "max_takeoff_lb":    dict(v=2300, status="poh", ref="p.1-5"),
    # ---- type data
    "wing_area_ft2":     dict(v=174, status="type_data", ref="TCDS 3A12 / Cessna type data"),
    "airfoil_root":      dict(v="NACA 2412", status="type_data", ref="published type data"),
    "airfoil_tip":       dict(v="NACA 0012", status="type_data", ref="published type data"),
    "dihedral_deg":      dict(v=1.733, status="type_data", ref="1° 44′ published"),
    "washout_deg":       dict(v=3.0, status="type_data", ref="+1.5° root / −1.5° tip published"),
    "gear_track_m":      dict(v=8 * FT + 3.5 * IN, status="type_data", ref="published (8 ft 3½ in)"),
    "main_tyre":         dict(v="6.00-6", status="type_data", ref="published"),
    "nose_tyre":         dict(v="5.00-5", status="type_data", ref="published"),
    "h_tail_span_m":     dict(v=11 * FT + 4 * IN, status="type_data", ref="published (11 ft 4 in)"),
    # ---- estimated (photographs, general arrangement)
    "root_chord_m":      dict(v=64.5 * IN, status="estimated", ref="constant-chord inboard panel"),
    "taper_start_bl_in": dict(v=100, status="estimated", ref="taper begins near strut attach"),
    "tip_chord_m":       dict(v=41 * IN, status="estimated", ref="solves wing area 174 ft²"),
    "wing_le_fs_in":     dict(v=24, status="estimated", ref="LEMAC ≈ FS 25.9 published"),
    "wing_chord_z_m":    dict(v=2.09, status="estimated", ref="roof height"),
    "prop_axis_z_m":     dict(v=1.40, status="estimated", ref="ground clearance ~0.45 m"),
    "spinner_tip_fs_in": dict(v=-40, status="estimated", ref="overall length − tail end"),
    "tail_end_fs_in":    dict(v=283, status="estimated", ref="length 323 in from spinner tip"),
    "main_axle_fs_in":   dict(v=58, status="estimated", ref="W&B arm of main wheels ~FS 58"),
    "nose_axle_fs_in":   dict(v=-7, status="estimated", ref="wheel base ~65 in"),
    "cabin_half_width_m":dict(v=0.54, status="estimated", ref="cabin width ~40 in inside"),
}

def ref(key):
    return REF[key]["v"]

# Convenience constants (metres)
SPAN = ref("wingspan_m")
SEMISPAN = SPAN / 2
ROOT_CHORD = ref("root_chord_m")
TIP_CHORD = ref("tip_chord_m")
TAPER_START = bl(ref("taper_start_bl_in"))
WING_LE_Y = fs(ref("wing_le_fs_in"))
WING_Z = ref("wing_chord_z_m")
PROP_Z = ref("prop_axis_z_m")
PROP_R = ref("prop_diameter_m") / 2
SPINNER_TIP_Y = fs(ref("spinner_tip_fs_in"))
TAIL_END_Y = fs(ref("tail_end_fs_in"))
FIREWALL_Y = fs(0)
MAIN_AXLE_Y = fs(ref("main_axle_fs_in"))
NOSE_AXLE_Y = fs(ref("nose_axle_fs_in"))
TRACK = ref("gear_track_m")
MAIN_TYRE_R = 0.22     # 6.00-6 ≈ 17.5 in diameter (type_data)
MAIN_TYRE_W = 0.16
NOSE_TYRE_R = 0.18     # 5.00-5 ≈ 14.2 in diameter (type_data)
NOSE_TYRE_W = 0.13
H_TAIL_SPAN = ref("h_tail_span_m")
