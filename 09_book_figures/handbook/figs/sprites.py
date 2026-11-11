"""Pictures of the aeroplane for diagrams (patterns, manoeuvres, ground reference, wake, wind): a render on a transparent background that a
plate lays on its canvas, as many times as it needs, at any place, size and heading (an overlay {"type": "sprite", ...}).

    sprite-top    from above, nose up (propeller as a disc)
    sprite-top-night   the same by moonlight, lights off (a night figure draws the lights itself)
    sprite-side   from the right, nose to the right
    sprite-side-left   from the left, nose to the left
    sprite-front  from ahead
    sprite-rear   from behind

width_m is the width of the picture in metres: a plate gives the scale in canvas units to a metre. The point of the aeroplane at the middle
of each picture (0, 1.95 m) is what an overlay places."""

WIDTH_M = 12.0


def sprites():
    common = {"light": "outdoor", "pitch": {"deg": 3.0, "about": [0, 0, 1.3]}, "hide": ["ELECTRICAL.adf_sense_wire"], "propeller": "disc", "samples": 64}
    return [
        {"id": "sprite-top", "width_m": WIDTH_M, "render": {**common, "pitch": {"deg": 0.0, "about": [0, 0, 1.3]},
            "camera": {"view": "side", "target": [0, 1.95, 0.8], "width": WIDTH_M, "azimuth": 0, "elevation": 90, "up": [0, -1, 0]}, "size": [1536, 1536]}},
        {"id": "sprite-top-night", "width_m": WIDTH_M, "render": {**common, "pitch": {"deg": 0.0, "about": [0, 0, 1.3]}, "light": "night", "exposure": 1.1,
            "camera": {"view": "side", "target": [0, 1.95, 0.8], "width": WIDTH_M, "azimuth": 0, "elevation": 90, "up": [0, -1, 0]}, "size": [1536, 1536]}},
        {"id": "sprite-side", "width_m": WIDTH_M, "render": {**common,
            "camera": {"view": "side", "target": [0, 1.95, 1.25], "width": WIDTH_M, "azimuth": 0, "elevation": 0}, "size": [1536, 640]}},
        {"id": "sprite-side-left", "width_m": WIDTH_M, "render": {**common, "mirror": True,
            "camera": {"view": "side", "target": [0, 1.95, 1.25], "width": WIDTH_M, "azimuth": 180, "elevation": 0}, "size": [1536, 640]}},
        {"id": "sprite-front", "width_m": WIDTH_M, "render": {**common,
            "camera": {"view": "side", "target": [0, 1.95, 1.25], "width": WIDTH_M, "azimuth": 90, "elevation": 0}, "size": [1536, 640]}},
        {"id": "sprite-rear", "width_m": WIDTH_M, "render": {**common, "propeller": "none",
            "camera": {"view": "side", "target": [0, 1.95, 1.25], "width": WIDTH_M, "azimuth": -90, "elevation": 0}, "size": [1536, 640]}},
    ]
