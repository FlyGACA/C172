"""Pictures of the aeroplane for diagrams (patterns, manoeuvres, ground reference, wake, wind): a render on a transparent background that a
plate lays on its canvas, as many times as it needs, at any place, size and heading (an overlay {"type": "sprite", ...}).

    sprite-top    from above, nose up (propeller as a disc)
    sprite-top-night   the same by moonlight, lights off (a night figure draws the lights itself)
    sprite-side   from the right, nose to the right
    sprite-side-left   from the left, nose to the left
    sprite-front  from ahead
    sprite-rear   from behind
    sprite-spin   in a developed spin to the left, from ahead and the right

width_m is the width of the picture in metres: a plate gives the scale in canvas units to a metre. The point of the aeroplane at the middle
of each picture (0, 1.95 m) is what an overlay places."""

from figs.kit import dial_sprite      # noqa: E402

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
        # a developed spin to the left: nose well down, left wing down, seen from ahead and the right (Figure 6-2)
        {"id": "sprite-spin", "width_m": WIDTH_M, "render": {**common, "pitch": {"deg": -58.0, "bank": -32.0, "about": [0, 0, 1.3]},
            "camera": {"view": "side", "target": [0, 1.95, 0.9], "width": WIDTH_M, "azimuth": 38, "elevation": 14}, "size": [1536, 1536]}},
        # the instruments of Figure 31-4, as the model's own: climbing at 75 kt through 1,200 ft, 700 ft/min up, nose 10 degrees up
        dial_sprite("dial-31-04-ai", "AI", {"pitch": 10, "bank": 0}),
        dial_sprite("dial-31-04-asi", "ASI", {"ASI": 75}),
        dial_sprite("dial-31-04-alt", "ALT", {"ALT": 1200}),
        dial_sprite("dial-31-04-vsi", "VSI", {"VSI": 700}),
        # the heading indicator of Figure 9-3, pointing north
        dial_sprite("dial-09-03-dg", "DG", {"heading": 360}),
    ]
