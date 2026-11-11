"""Figure 25-4 of the handbook: a walk-around route for a high-wing trainer, anticlockwise from the cabin door.
The model from above, nose up, on a light apron colour; the route round it as a dashed line with arrows and its eight stops,
the fuel drain points as drops, the pitot tube, and the place to step back and look from."""
import math


def smooth(points, per=10):
    """A closed Catmull-Rom curve through the points (every point is passed)."""
    n = len(points)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = points[(i - 1) % n], points[i], points[(i + 1) % n], points[(i + 2) % n]
        for k in range(per):
            t = k / per
            out.append([0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)])
    out.append(out[0])
    return out


def fraction(poly, point):
    """The fraction of the length of a polyline at its vertex nearest to point."""
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(poly, poly[1:])]
    total = sum(lengths)
    best = min(range(len(poly)), key=lambda i: (poly[i][0] - point[0]) ** 2 + (poly[i][1] - point[1]) ** 2)
    return sum(lengths[:best]) / total


def plate():
    # the route, in metres in the aircraft's own frame (x to the left wing, y aft): the stops are the first point of each group
    stops = {1: (1.65, 1.6), 2: (1.5, 2.9), 3: (0.0, 7.15), 4: (-3.2, 1.95), 5: (-3.2, -1.3), 6: (0.0, -3.25), 7: (3.2, -1.3), 8: (3.2, 1.95)}
    waypoints = [stops[1], stops[2], (2.0, 4.4), (2.6, 5.9), (1.9, 6.85), stops[3], (-1.9, 6.85), (-2.6, 5.9), (-2.0, 4.4), (-1.55, 2.7),
                 (-2.0, 2.2), stops[4], (-5.2, 1.9), (-6.3, 0.9), (-6.4, -0.3), (-5.6, -1.2), stops[5], (-1.7, -1.4), (-1.35, -2.3),
                 (-0.8, -3.0), stops[6], (0.8, -3.0), (1.35, -2.3), (1.7, -1.4), stops[7], (5.6, -1.2), (6.4, -0.3), (6.3, 0.9), (5.2, 1.9),
                 stops[8], (2.4, 1.95)]
    route = smooth(waypoints)
    t = {n: fraction(route, p) for n, p in stops.items()}
    route3d = [[x, y, 0.1] for x, y in route]
    order = [t[n] for n in range(1, 9)] + [1.0 + t[1]]
    marks = [round(((a + b) / 2) % 1.0, 4) for a, b in zip(order, order[1:])]            # one arrowhead midway between two stops
    return {
        "id": "fig-25-04-walk-around",
        "replaces": "fig-25-04-walk-around.svg",
        "book_file": "plate-25-04-walk-around.jpg",
        "caption": "Figure 25-4. A walk-around route for a high-wing trainer, anticlockwise from the cabin door",
        "desc": "The aeroplane seen from above, nose up, with a dashed route round it in eight stops, the fuel drain points, the pitot tube and the place to step back to.",
        "legend": [
            "Cabin: documents; ignition off; master on for fuel gauges, lights and flaps, then off; control lock out.",
            "Left rear fuselage: skin, antennas, windows.",
            "Tail: elevator, rudder, trim tab, hinges, sand in the gaps (Chapter 7); tie-down off.",
            "Right flap and aileron.",
            "Right wing: leading edge, tank (look in, cap, vent), drain; wheel, tyre, brake.",
            "Nose: oil, cowling, propeller, air intake and filter, nose wheel, strainer drain.",
            "Left wing: leading edge, pitot, stall warning, tank, vent, drain, wheel.",
            "Left flap and aileron.",
            "Step back: covers, chocks and tie-downs removed and counted.",
            "Fuel drain points in this example; your AFM shows yours.",
            "Pitot tube: cover off, opening clear.",
        ],
        "canvas": [640, 450],
        "background": "apron",
        "render": {
            "camera": {"view": "side", "target": [0, 1.95, 0.8], "width": 16.6, "azimuth": 0, "elevation": 90, "up": [0, -1, 0]},
            "size": [2560, 1800],
            "light": "outdoor",
            "pitch": {"deg": 0.0, "about": [0, 0, 1.3]},
            "hide": ["ELECTRICAL.adf_sense_wire"],
            "samples": 96,
            "anchors": {
                "drain_left": [1.75, 0.35, 0.9], "drain_right": [-1.75, 0.35, 0.9], "drain_nose": [0.35, -1.05, 0.9],
                "pitot_root": [3.45, -0.35, 0.9], "pitot_tip": [3.45, -0.95, 0.9],
                "look_from": [-6.2, 8.4, 0.1], "tail_view": [-1.2, 6.6, 0.1],
            },
            "curves": {"route": {"line": route3d}, "pitot": {"line": [[3.45, -0.32, 2.5], [3.45, -0.98, 2.5]]}},
        },
        "overlays": [
            {"type": "path", "curve": "route", "colour": "#0A7A4F", "width": 3.0, "dash": "9 6", "marks": marks},
            {"type": "path", "curve": "pitot", "colour": "#1E2A44", "width": 3.4, "halo": True},
            {"type": "icon", "name": "drop", "at": "drain_left", "size": 17},
            {"type": "icon", "name": "drop", "at": "drain_right", "size": 17},
            {"type": "icon", "name": "drop", "at": "drain_nose", "size": 17},
            {"type": "line", "points": ["tail_view", [575, 400]], "colour": "#8D96A5", "width": 1.6, "dash": "1.5 5", "halo": False},
            {"type": "icon", "name": "eye", "pos": [592, 402], "size": 20},
        ] + [{"type": "marker", "n": n, "on": {"curve": "route", "t": t[n]}} for n in range(1, 9)] + [
            {"type": "marker", "n": 9, "pos": [560, 426], "leader": False},
            {"type": "marker", "n": 10, "at": "drain_right", "pos": [452, 176], "leader": True, "gap": 8},
            {"type": "marker", "n": 11, "at": "pitot_tip", "pos": [143, 121], "leader": True},
        ],
    }
