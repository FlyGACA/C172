"""Reference dimensions used by the Phase 8 model.

Every value carries a status:
  measured   — verified measurement from the identified aircraft (record ID cited)
  poh        — 1979 Cessna 172N Pilot's Operating Handbook (page cited)
  type_data  — published type data, not from the POH; confirm against TCDS 3A12 / E-274
  estimated  — proportions estimated from photographs / general arrangement; not manufacturer data

"photo-profile" in a reference means the single-photograph side elevation described in
docs/05_shape_reference.md: a Cessna 172 photographed almost side-on, scaled by the POH overall
length (checked against the 65 in wheel base) and levelled on its own wheels. It is a proportion
reference for the type, not a survey of the FlyGACA aircraft.

Frames
------
Blender build frame: Z up, -Y forward (nose), +X left wing.
Fuselage station (FS, inches, POH datum = front face of firewall): y = (FS - FS_ORIGIN) * IN
with FS_ORIGIN = 40 so the model origin is near the CG range (POH p.6-x: 35.0–47.3 in).
Butt line (BL, inches from centreline): x = BL * IN.
Water line (WL, inches above the static ground line): z = wl(WL) = WL * IN + GROUND_Z while the
model is being built. The cabin interior was laid out in that build frame, so the ground sits at
z = GROUND_Z during the build; build.py lowers the finished aircraft by GROUND_Z, which leaves the
tyres on z = 0 in the saved scene and in the exported models.
"""
IN = 0.0254
FT = 0.3048
FS_ORIGIN = 40.0

def fs(station_in):
    """Fuselage station (inches aft of firewall) -> Blender y (metres, +aft)."""
    return (station_in - FS_ORIGIN) * IN

def bl(butt_in):
    return butt_in * IN

GROUND_Z = 0.375   # build-frame height of the static ground line (estimated, photo-profile: belly 16.7 in above ground at FS 45)

def wl(water_in):
    """Water line (inches above the static ground) -> build-frame z (metres)."""
    return water_in * IN + GROUND_Z

REF = {
    # ---- POH (Section 1, Figure 1-1 unless noted)
    "wingspan_m":        dict(v=35 * FT + 10 * IN, status="poh", ref="Fig 1-1, p.1-2 (35 ft 10 in)"),
    "length_m":          dict(v=26 * FT + 11 * IN, status="poh", ref="Fig 1-1, p.1-2 (26 ft 11 in)"),
    "height_m":          dict(v=8 * FT + 9.5 * IN, status="poh", ref="Fig 1-1, p.1-2 (8 ft 9½ in maximum, nose gear depressed)"),
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
    "wheel_base_m":      dict(v=65 * IN, status="type_data", ref="published three-view note (65 in); confirm against POH Fig 1-1"),
    "prop_clearance_m":  dict(v=11.75 * IN, status="type_data", ref="published three-view note (11¾ in); confirm against POH Fig 1-1"),
    # ---- estimated (photographs, general arrangement)
    "root_chord_m":      dict(v=64.5 * IN, status="estimated", ref="constant-chord inboard panel"),
    "taper_start_bl_in": dict(v=100, status="estimated", ref="taper begins near strut attach"),
    "tip_chord_m":       dict(v=41 * IN, status="estimated", ref="solves wing area 174 ft²"),
    "wing_le_fs_in":     dict(v=24, status="estimated", ref="LEMAC ≈ FS 25.9 published"),
    "wing_chord_z_m":    dict(v=2.09, status="estimated", ref="build frame; chord line 67.5 in above ground (photo-profile)"),
    "static_height_m":   dict(v=96.5 * IN, status="estimated", ref="photo-profile: beacon 96.5 in above ground at rest; the POH figure is the maximum with the nose strut depressed"),
    "spinner_tip_fs_in": dict(v=-44.5, status="estimated", ref="photo-profile; overall length − tail end"),
    "tail_end_fs_in":    dict(v=278.5, status="estimated", ref="photo-profile (rudder top trailing edge); length 323 in from spinner tip"),
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
PROP_R = ref("prop_diameter_m") / 2
PROP_Z = GROUND_Z + PROP_R + ref("prop_clearance_m")   # crank axis, build frame
SPINNER_TIP_Y = fs(ref("spinner_tip_fs_in"))
TAIL_END_Y = fs(ref("tail_end_fs_in"))
FIREWALL_Y = fs(0)
MAIN_AXLE_Y = fs(ref("main_axle_fs_in"))
NOSE_AXLE_Y = fs(ref("nose_axle_fs_in"))
TRACK = ref("gear_track_m")
MAIN_TYRE_R = 0.216    # 6.00-6: 17.0 in diameter as fitted (type_data; photo-profile agrees)
MAIN_TYRE_W = 0.16
NOSE_TYRE_R = 0.172    # 5.00-5: 13.5 in diameter as fitted (type_data; photo-profile agrees)
NOSE_TYRE_W = 0.13
H_TAIL_SPAN = ref("h_tail_span_m")
