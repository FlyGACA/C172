"""Reference dimensions used by the Phase 8 model.

Every value carries a status:
  measured   — verified measurement from the identified aircraft (record ID cited)
  poh        — Cessna 172N Pilot's Operating Handbook (figure or page cited; the copy used is the 1978 edition)
  type_data  — published type data, not from the POH; confirm against TCDS 3A12 / E-274
  estimated  — proportions taken from drawings and photographs; not manufacturer dimensions

Where an outline is "estimated" it now comes from two manufacturer drawings laid under the model
(docs/05_shape_reference.md): the three-view of the POH (Figure 1-1) and the computer-drawn
three-view of the later 172S handbook, which shares this airframe aft of the firewall. They give
proportions, not dimensions; the printed dimensions of Figure 1-1 are carried as `poh`.

Frames
------
Build frame: Z up, -Y forward (nose), +X left wing.
Fuselage station (FS, inches aft of the firewall): y = (FS - FS_ORIGIN) * IN, FS_ORIGIN = 40.
Butt line (BL, inches from the centreline): x = BL * IN.
Water line (WL, inches): z = wl(WL) = WL * IN + GROUND_Z.

The build frame is not Cessna's own station system and it is not level on the ground:
  * The handbook's stations follow the fuselage reference line (the line the published wing
    incidence is measured from). That line is pitched FRL_PITCH_DEG nose-down in the build frame,
    so a part that stands "at station s" in the handbook leans back here: cessna_fs() converts.
  * On its wheels the aircraft sits GROUND_PITCH_DEG nose-up relative to the build frame. build.py
    turns the finished aircraft into that attitude and puts the tyres on z = 0; to_ground() and
    from_ground() convert points between the build frame and the saved scene.
"""
import math

IN = 0.0254
FT = 0.3048
FS_ORIGIN = 40.0

def fs(station_in):
    """Fuselage station (inches aft of firewall) -> Blender y (metres, +aft)."""
    return (station_in - FS_ORIGIN) * IN

def bl(butt_in):
    return butt_in * IN

GROUND_Z = 0.375   # build-frame height of water line 0 (kept from the first layout of the cabin interior)

def wl(water_in):
    """Water line (inches, build frame) -> build-frame z (metres)."""
    return water_in * IN + GROUND_Z

# ---- attitude. Status: estimated, by laying the model under the 172S three-view "normal ground
# attitude" (belly line, FS 0-240: the two agree within 0.3 in after this rotation). The 1978 POH marks
# 5 degrees between the level reference and the ground line on its side view; here FRL + GROUND = 4.7.
GROUND_PITCH_DEG = 1.66    # the aircraft at rest is this much nose-up relative to the build frame
GROUND_PIVOT_FS = 58.0     # main wheel station
GROUND_DROP_IN = 2.47      # the ground under the main wheels is this far below water line 0
FRL_PITCH_DEG = 3.0        # the fuselage reference line is pitched this much nose-down in the build frame
FRL_PIVOT_WL = 20.0        # ... about the foot of the firewall (FS 0 at this water line)

def ground_wl(station_in):
    """Water line (build frame, inches) of the ground under fuselage station s with the aircraft at rest."""
    return -GROUND_DROP_IN + (station_in - GROUND_PIVOT_FS) * math.tan(math.radians(GROUND_PITCH_DEG))

def ground_z(y):
    """Build-frame z (m) of the ground under build-frame y (m)."""
    return wl(ground_wl(y / IN + FS_ORIGIN))

def _ground_pivot():
    return fs(GROUND_PIVOT_FS), wl(-GROUND_DROP_IN)

def to_ground(point):
    """Build frame (x, y, z) -> the saved scene: aircraft at rest, tyres on z = 0, main wheels at their station."""
    x, y, z = point
    y0, z0 = _ground_pivot()
    c, s = math.cos(math.radians(GROUND_PITCH_DEG)), math.sin(math.radians(GROUND_PITCH_DEG))
    dy, dz = y - y0, z - z0
    return (x, y0 + dy * c + dz * s, -dy * s + dz * c)

def from_ground(point):
    """The saved scene (x, y, z) -> build frame."""
    x, y, z = point
    y0, z0 = _ground_pivot()
    c, s = math.cos(math.radians(GROUND_PITCH_DEG)), math.sin(math.radians(GROUND_PITCH_DEG))
    dy = y - y0
    return (x, y0 + dy * c - z * s, z0 + dy * s + z * c)

def cessna_fs(station_in, water_in):
    """Build-frame FS (inches) of the handbook station `station_in` at build water line `water_in`:
    a plane that is square to the fuselage reference line leans back in the build frame."""
    return station_in + (water_in - FRL_PIVOT_WL) * math.tan(math.radians(FRL_PITCH_DEG))

REF = {
    # ---- POH Section 1, Figure 1-1 "Three View" (p.1-2) and descriptive data
    "wingspan_strobes_m": dict(v=36 * FT, status="poh", ref="Fig 1-1 (36 ft; note 1: wing span shown with strobe lights installed)"),
    "length_m":          dict(v=26 * FT + 11 * IN, status="poh", ref="Fig 1-1 (26 ft 11 in)"),
    "height_m":          dict(v=8 * FT + 9.5 * IN, status="poh", ref="Fig 1-1 (8 ft 9½ in maximum; note 2: nose gear depressed, flashing beacon installed)"),
    "h_tail_span_m":     dict(v=11 * FT + 4 * IN, status="poh", ref="Fig 1-1 (11 ft 4 in)"),
    "gear_track_m":      dict(v=8 * FT + 4.5 * IN, status="poh", ref="Fig 1-1 (8 ft 4½ in)"),
    "wheel_base_m":      dict(v=65 * IN, status="poh", ref="Fig 1-1 note 3 (65 in)"),
    "prop_clearance_m":  dict(v=11.75 * IN, status="poh", ref="Fig 1-1 note 4 (11¾ in). It belongs to the same condition as the maximum height, nose gear depressed: see docs/05_shape_reference.md"),
    "wing_area_ft2":     dict(v=174, status="poh", ref="Fig 1-1 note 5 (174 sq ft)"),
    "prop_diameter_m":   dict(v=75 * IN, status="poh", ref="p.1-3 (75 in maximum); Fig 1-1 shows the 6 ft 3 in arc"),
    "engine":            dict(v="Lycoming O-320-H2AD, 160 BHP at 2700 RPM", status="poh", ref="p.1-3"),
    "fuel_total_gal":    dict(v=43, status="poh", ref="p.1-4 (standard tanks)"),
    "max_takeoff_lb":    dict(v=2300, status="poh", ref="p.1-5"),
    # ---- type data
    "wingspan_m":        dict(v=35 * FT + 10 * IN, status="type_data", ref="published span over the wing tips (35 ft 10 in); the POH gives 36 ft with strobe lights"),
    "airfoil_root":      dict(v="NACA 2412", status="type_data", ref="published type data"),
    "airfoil_tip":       dict(v="NACA 0012", status="type_data", ref="published type data"),
    "dihedral_deg":      dict(v=1.733, status="type_data", ref="1° 44′ published"),
    "incidence_root_deg": dict(v=1.5, status="type_data", ref="+1° 30′ at the root, published; relative to the fuselage reference line"),
    "washout_deg":       dict(v=3.0, status="type_data", ref="+1.5° root / −1.5° tip published"),
    "root_chord_m":      dict(v=64.0 * IN, status="type_data", ref="published 5 ft 4 in; 63.6 in measured on the 172S three-view"),
    "tip_rib_chord_m":   dict(v=44.5 * IN, status="type_data", ref="published 3 ft 8½ in at the tip rib, BL 208; 44.5 in measured on the 172S three-view"),
    "lemac_fs_in":       dict(v=25.90, status="type_data", ref="TCDS 3A12: leading edge of the 58.80 in mean aerodynamic chord (handbook station)"),
    "main_tyre":         dict(v="6.00-6", status="type_data", ref="published"),
    "nose_tyre":         dict(v="5.00-5", status="type_data", ref="published"),
    # ---- estimated (manufacturer three-views laid under the model; see docs/05_shape_reference.md)
    "taper_start_bl_in": dict(v=100, status="estimated", ref="172S three-view: constant chord to BL 100, where the strut meets the wing"),
    "tip_rib_bl_in":     dict(v=208, status="estimated", ref="172S three-view: last full rib; the tip cap closes the wing to 35 ft 10 in"),
    "taper_le_share":    dict(v=0.27, status="estimated", ref="172S three-view: 27 % of the taper is on the leading edge (5.2 in at the tip rib)"),
    "wing_le_fs_in":     dict(v=30.0, status="estimated", ref="build frame; root leading edge and trailing edge (FS 93.8) on the 172S side view. The handbook station is about 24.6 (LEMAC 25.90 less 1.3 in for the swept outer panel)"),
    "wing_chord_wl_in":  dict(v=70.0, status="estimated", ref="build frame; root leading edge, from the wing tip outline of the 172S side view"),
    "prop_axis_wl_in":   dict(v=49.25, status="estimated", ref="build frame; photo-profile, confirmed by the 172S side view"),
    "spinner_tip_fs_in": dict(v=-46.3, status="estimated", ref="build frame; gives 26 ft 11 in in ground attitude with the tail end below"),
    "tail_end_fs_in":    dict(v=275.6, status="estimated", ref="build frame; rear top corner of the rudder on the 172S side view"),
    "main_axle_fs_in":   dict(v=58, status="estimated", ref="equipment list of the 172S handbook: main wheel arm 57.8-58.2 in"),
    "nose_axle_fs_in":   dict(v=-7, status="estimated", ref="wheel base 65 in ahead of the main wheels"),
    "cabin_half_width_m":dict(v=21.6 * IN, status="estimated", ref="172S three-view; POH Fig 6-4 gives 39½ in inside at the lower window line"),
}

def ref(key):
    return REF[key]["v"]

# Convenience constants (metres)
SPAN = ref("wingspan_m")
SEMISPAN = SPAN / 2
ROOT_CHORD = ref("root_chord_m")
TAPER_START = bl(ref("taper_start_bl_in"))
TIP_RIB = bl(ref("tip_rib_bl_in"))
TIP_RIB_CHORD = ref("tip_rib_chord_m")
TAPER_PER_M = (ROOT_CHORD - TIP_RIB_CHORD) / (TIP_RIB - TAPER_START)       # chord lost per metre of span outboard of BL 100
TIP_CHORD = ROOT_CHORD - TAPER_PER_M * (SEMISPAN - TAPER_START)            # the straight taper carried to the tip (43.2 in)
TAPER_LE_SHARE = ref("taper_le_share")
WING_LE_Y = fs(ref("wing_le_fs_in"))
WING_Z = wl(ref("wing_chord_wl_in"))
PROP_R = ref("prop_diameter_m") / 2
PROP_Z = wl(ref("prop_axis_wl_in"))                    # crank axis, build frame
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
