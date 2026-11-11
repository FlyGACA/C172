"""Where cables, pipes and wires run under the cabin floor and through the tailcone.

One table for the packs that lay the runs (controls, fuel, brakes, pneumatic, electrical) and for the
structure pack, which cuts a hole in each under-floor bulkhead, frame and keel beam where a run passes,
so that no run goes through sheet metal.

Status: estimated. The POH shows that these runs lie under the floor and in the tailcone (Fig 7-1,
7-6) but not where; the order from the centre outward is chosen so that nothing crosses.
"""
from ..units import fs
from .. import airframe as A

LEVEL = 0.893            # height of the fore-and-aft runs under the cabin floor (m, build frame)
PIPE_LEVEL = 0.872       # fuel pipes run a little lower, under the cables
FEED_LEVEL = 0.895       # the fuel feed pipe near the firewall
BRAKE_LEVEL = 0.880      # the two brake pipes
BRAKE_FWD_LEVEL = 0.886           # the brake pipes ahead of station 22
CROSS_LEVEL = 0.884      # the right brake pipe where it crosses the cabin
HOLE = 0.009             # radius of the hole a run gets in a bulkhead

# Fore-and-aft runs: name -> (x, z, first station, last station). Left is +x.
ALONG = {
    "fuel_feed":     (0.000, PIPE_LEVEL, 12.5, 45.0),
    "fuel_feed_fwd": (0.000, FEED_LEVEL, 2.0, 10.0),      # the belly rises toward the firewall, and the pipe with it
    "fuel_fwd_L":    (0.030, PIPE_LEVEL, 25.0, 45.0),
    "fuel_fwd_R":    (-0.030, PIPE_LEVEL, 25.0, 45.0),
    "elevator_up":   (0.055, LEVEL, 32.0, 96.0),
    "elevator_down": (-0.055, LEVEL, 32.0, 96.0),
    "trim_up":       (-0.095, LEVEL, 29.0, 96.0),
    "trim_down":     (-0.120, LEVEL, 29.0, 96.0),
    "rudder_L":      (0.160, LEVEL, 11.0, 96.0),
    "rudder_R":      (-0.160, LEVEL, 11.0, 96.0),
    "aileron_L":     (0.235, LEVEL, 18.0, 60.0),
    "aileron_R":     (-0.235, LEVEL, 18.0, 60.0),
    "brake_L_fwd":   (0.275, BRAKE_FWD_LEVEL, 12.0, 22.5),  # the belly rises toward the firewall: the brake pipes start further in and higher
    "brake_R_fwd":   (-0.275, BRAKE_FWD_LEVEL, 14.0, 22.5),
    "brake_L":       (0.300, BRAKE_LEVEL, 23.0, 66.6),      # through the main gear bulkhead, then out to the gear leg
    "brake_R":       (-0.300, BRAKE_LEVEL, 23.0, 66.6),
    "coax_xpdr":     (0.105, LEVEL, 7.0, 57.0),             # transponder antenna cable, in the free lane left of the centre
}

# Runs across the cabin, which pass through the two keel beams: name -> (station, z).
ACROSS = {
    "brake_R_cross": (14.0, CROSS_LEVEL),
    "fuel_fwd":      (25.0, PIPE_LEVEL),
    "fuel_aft":      (62.0, PIPE_LEVEL),
}

AILERON_TURN_FS = 60.0   # where the aileron cables turn outboard to the rear door posts (outside the keel beams)

# Behind the rear seat the belly rises and the runs climb with it, under the raised baggage floor,
# from CLIMB_STATION to AFT_LEVEL at the aft cabin bulkhead; from there they are led up into the tailcone.
CLIMB_STATION = 95.0
AFT_STATION, AFT_LEVEL = 108.0, 0.925
TAIL_STATION, TAIL_LEVEL = 118.0, 1.000


def crossing(station):
    """Runs that pass a bulkhead at this station: [(x, z)]."""
    return [(x, z) for x, z, first, last in ALONG.values() if first < station < last]


def point(name, station):
    """Point of a fore-and-aft run at a station."""
    x, z, _first, _last = ALONG[name]
    return (x, fs(station), z)


def floor_underside(station):
    return A.floor_z(station) - 0.015


# ----------------------------------------------------------------------------- wings
# Runs along each wing: name -> (first wing station, last wing station (in), chord fraction at the
# first and at the last, height above the middle of the section at the first and at the last (m)).
# The ribs get an opening where a run passes them. Inboard, everything runs behind the rear spar,
# because the fuel tank fills the bay between the spars.
WING = {
    "aileron_direct": (22.0, 146.0, 0.700, 0.668, 0.034, 0.000),
    "aileron_carry":  (22.0, 146.0, 0.722, 0.735, 0.034, 0.000),
    "flap_cable_a":   (22.0, 70.0, 0.676, 0.676, 0.010, 0.010),
    "flap_cable_b":   (22.0, 70.0, 0.742, 0.742, 0.010, 0.010),
    "flap_screw":     (41.0, 62.0, 0.690, 0.690, -0.028, -0.028),
    "fuel_fwd":       (22.0, 25.5, 0.220, 0.220, -0.078, -0.078),
    "fuel_aft":       (22.0, 25.5, 0.600, 0.600, -0.052, -0.052),
    "fuel_vent":      (22.0, 25.5, 0.250, 0.250, 0.080, 0.080),
    "pitot":          (22.0, 69.5, 0.090, 0.090, -0.012, -0.012),
    "stall_warning":  (22.0, 41.0, 0.098, 0.060, 0.004, 0.012),
    "wiring":         (22.0, 209.6, 0.070, 0.070, 0.000, 0.000),      # through the last rib into the wing tip
    "vent_duct":      (20.5, 26.5, 0.079, 0.079, 0.034, 0.034),       # cabin ventilator duct: above the wires and the pitot line, through the root nose rib
}
WING_HOLES = {"vent_duct": 0.019}      # runs that need a larger opening than HOLE


def wing_run(name, station):
    """(chord fraction, height above the middle of the section) of a wing run at a wing station (in)."""
    first, last, xc0, xc1, dz0, dz1 = WING[name]
    t = min(1.0, max(0.0, (station - first) / (last - first)))
    return xc0 + (xc1 - xc0) * t, dz0 + (dz1 - dz0) * t


def wing_crossing(station):
    """Runs that pass a rib at this wing station: [(chord fraction, height above the middle of the section)]."""
    return [wing_run(name, station) for name, (first, last, *_rest) in WING.items() if first < station < last]


def wing_openings(station):
    """The same, with the radius of the opening each run needs: [(chord fraction, height, radius)]."""
    return [wing_run(name, station) + (WING_HOLES.get(name, HOLE),) for name, (first, last, *_rest) in WING.items() if first < station < last]


def wing_point(name, side, station, more=0.0):
    """Point in space of a wing run at a wing station (in); `more` is added to its height."""
    xc, dz = wing_run(name, station)
    xabs = station * 0.0254
    middle = A.wing_hinge_point(xabs, side, xc)
    up = (A.wing_point(xabs, side, xc, 1.0) - A.wing_point(xabs, side, xc, 0.0)).normalized()
    return middle + up * (dz + more)
