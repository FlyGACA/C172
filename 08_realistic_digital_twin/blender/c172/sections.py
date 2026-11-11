"""Section tables of the fuselage and the cowl: plain numbers, with no bpy, read by the builders of both.

The cowl ends on the first section of the fuselage, so the two skins meet exactly at the firewall.
"""
from .units import wl, IN

# Fuselage sections, build frame: FS, half width, WL of the bottom, WL of the top, WL of the widest
# point (all inches), then the superellipse exponents of the upper and lower half.
# Status: estimated. Sources, laid under the model (docs/05_shape_reference.md):
#   belly and cowl deck   photo-profile, confirmed by the 172S side view (within 0.3 in over FS 0-240)
#   windshield, roof slope, tailcone top, tail end   172S side view
#   widths                172S top view (20.3 in at the firewall, 21.6 in at the doors, then a straight
#                         taper of 0.119 in per inch from FS 94 to the tail); POH Fig 6-4 agrees at FS 142
#   cabin roof            the upper surface of the wing root, which the cabin top is flush with
# The cabin is slab-sided with a flat belly and tight lower corners; the tailcone is widest near the
# top and narrows toward a rounded keel. The fuselage ends at the bulkhead that carries the rudder.
_FUS_IN = [
    (0.0,   20.30, 19.80, 57.80, 41.0, 2.6, 3.0),
    (4.0,   20.60, 19.40, 57.80, 40.6, 2.6, 3.2),
    (8.0,   20.75, 19.00, 57.80, 40.2, 2.6, 3.4),
    (10.3,  20.80, 18.75, 57.85, 40.0, 2.6, 3.5),     # foot of the windshield
    (13.0,  21.00, 18.60, 61.60, 40.0, 2.5, 3.6),
    (16.0,  21.20, 18.30, 64.40, 40.0, 2.8, 3.8),
    (19.7,  21.40, 17.95, 67.00, 40.0, 3.2, 4.0),
    (22.5,  21.50, 17.75, 68.60, 40.0, 3.6, 4.0),
    (25.5,  21.60, 17.55, 69.90, 40.0, 4.2, 4.0),
    (28.0,  21.60, 17.35, 70.90, 40.0, 5.0, 4.0),
    (31.0,  21.60, 17.15, 72.20, 40.5, 7.0, 4.0),     # top of the windshield, just behind the wing leading edge
    (34.0,  21.60, 16.95, 72.60, 41.5, 10.0, 4.0),
    (37.0,  21.60, 16.90, 72.95, 42.0, 14.0, 4.0),
    (43.0,  21.60, 16.90, 73.45, 42.0, 14.0, 4.0),
    (49.0,  21.60, 16.90, 73.30, 42.0, 14.0, 4.0),
    (55.5,  21.60, 16.95, 72.80, 42.0, 14.0, 4.0),
    (62.0,  21.60, 17.05, 71.90, 42.0, 14.0, 4.0),
    (68.5,  21.35, 17.40, 70.85, 42.0, 14.0, 4.0),
    (75.0,  21.10, 17.75, 69.60, 42.0, 12.0, 4.0),
    (81.0,  20.75, 18.15, 68.25, 42.0, 10.0, 3.9),
    (87.5,  20.25, 18.55, 66.60, 42.0, 8.0, 3.7),
    (93.8,  19.50, 19.00, 64.60, 42.0, 5.5, 3.5),     # wing trailing edge: the rear window slopes down from here ...
    (97.0,  19.10, 19.20, 62.60, 41.5, 5.0, 3.4),
    (101.0, 18.60, 19.50, 60.50, 41.0, 4.5, 3.3),
    (105.0, 18.10, 19.75, 58.40, 40.0, 4.0, 3.2),
    (109.0, 17.65, 20.00, 56.20, 39.0, 3.6, 3.0),
    (112.5, 17.25, 20.20, 54.40, 38.0, 3.3, 2.9),
    (115.5, 16.90, 20.35, 52.80, 37.5, 3.0, 2.8),     # ... to the top of the tailcone
    (120.0, 16.35, 20.70, 52.00, 38.2, 3.0, 2.5),
    (130.0, 15.15, 21.30, 51.00, 39.0, 3.0, 2.1),
    (140.0, 13.95, 21.90, 50.10, 39.5, 3.0, 1.9),
    (150.0, 12.80, 22.60, 49.30, 39.8, 3.0, 1.8),
    (165.0, 11.00, 23.45, 47.85, 39.6, 3.0, 1.75),
    (180.0, 9.20,  24.40, 46.60, 39.5, 3.0, 1.7),
    (200.0, 6.80,  25.70, 44.60, 38.8, 3.0, 1.7),
    (215.0, 5.05,  26.65, 43.10, 38.0, 3.0, 1.7),
    (225.0, 3.85,  27.20, 41.60, 37.0, 2.8, 1.8),
    (231.5, 3.10,  27.30, 40.60, 36.0, 2.6, 2.0),
]
# FS(in) -> half width, z bottom, z top, z of the widest point (m, build frame), n_top, n_bottom
FUS_TABLE = [(s, w * IN, wl(zb), wl(zt), wl(zc), nt, nb) for s, w, zb, zt, zc, nt, nb in _FUS_IN]
FUS_UV_END_FS = 283                    # texture v = 1 (kept from the first layout so the livery atlas stays valid)

# FS -> half width, z bottom, z top, ring centre z, n_top, n_bottom   (build frame). Status: estimated.
# Top and bottom lines follow the photo-profile side elevation: an almost straight top falling 6 in
# from the firewall to the nose, and an underside that sweeps up from the firewall to the spinner.
# The section is widest at crank height with square shoulders, to clear the cylinder heads; the widths
# follow the plan view of the manufacturer's three-view (20.3 in half width at the firewall).
COWL_TABLE = [
    (-33.6, 0.335, 1.468, 1.726, 1.612, 2.6, 2.0),
    (-32,   0.385, 1.405, 1.734, 1.610, 3.0, 2.0),
    (-30,   0.426, 1.330, 1.742, 1.608, 3.6, 2.0),
    (-27,   0.446, 1.205, 1.760, 1.605, 4.4, 2.05),
    (-23,   0.460, 1.075, 1.783, 1.600, 4.6, 2.2),
    (-19,   0.474, 0.988, 1.795, 1.590, 4.6, 2.4),
    (-10,   0.498, 0.913, 1.823, 1.540, 3.8, 2.7),
    (-4,    0.510, 0.890, 1.836, 1.470, 3.0, 2.9),
    FUS_TABLE[0],                 # the cowl meets the fuselage section at the firewall exactly
]
COWL_STATIONS = [-33.6, -33, -32, -30.5, -28.5, -26, -23, -19.5, -15, -10, -5, 0]
# The nose bowl: from the front ring of the cowl in toward the crank axis, in two steps.
NOSE_FS, NOSE_MID_FS = -34.3, -34.15          # stations of the inner edge of the nose face and of the ring between
NOSE_INNER, NOSE_MID = 0.40, 0.74             # how far toward the crank axis each lies (1 = the front ring of the cowl)

def cowl_uv_v():
    """Texture v of each ring of the cowl loft: the two rings of the nose face, then the stations to the firewall."""
    return [0.0, 0.03] + [0.06 + 0.94 * (s - COWL_STATIONS[0]) / (0 - COWL_STATIONS[0]) for s in COWL_STATIONS]
