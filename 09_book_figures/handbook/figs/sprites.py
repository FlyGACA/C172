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
        # the instruments of Figure 31-5 (31-4 until round 40; the sprite ids keep the old number), as the model's own: climbing at 75 kt through 1,200 ft, 700 ft/min up, nose 10 degrees up
        dial_sprite("dial-31-04-ai", "AI", {"pitch": 10, "bank": 0}),
        dial_sprite("dial-31-04-asi", "ASI", {"ASI": 75}),
        dial_sprite("dial-31-04-alt", "ALT", {"ALT": 1200}),
        dial_sprite("dial-31-04-vsi", "VSI", {"VSI": 700}),
        # the heading indicator of Figure 9-4, pointing north
        dial_sprite("dial-09-03-dg", "DG", {"heading": 360}),
        # the example speeds of Figure 26-1 on the model's airspeed indicator, the needle on the normal final approach speed (65 kt)
        dial_sprite("dial-26-01-asi", "ASI", {"ASI": 65}, anchors={f"v{v}": {"dial": "ASI", "value": v, "radius": 0.80} for v in (45, 52, 55, 60, 62, 65, 75, 90)}),
        # the lower panel of the model about the flap switch and the flap position indicator (Figure 26-1)
        {"id": "panel-26-01-flaps", "width_m": 0.26, "render": {"camera": {"view": "panel", "target": {"part": "PANEL.flap_switch", "at": [0.5, 0.5, 0.5]}, "width": 0.26,
            "azimuth": 0, "elevation": 0, "distance": 0.5}, "size": [1200, 900], "light": "panel", "samples": 64, "fine_textures": True, "hide": ["INTERIOR.yoke_*", "INTERIOR.yoke_shaft_*", "PANEL.control_wheel_*"],
            "anchors": {"switch": {"part": "PANEL.flap_switch", "at": [0.5, 0.5, 0.5]}, "ind": {"part": "PANEL.flap_ind", "at": [0.5, 0.5, 0.5]}}}},
        # the radio stack of the model (Figure 19-1): audio panel, the two COM/NAV radios, the ADF and the transponder
        {"id": "panel-19-01-radios", "width_m": 0.34, "render": {"camera": {"view": "panel", "target": {"part": "PANEL.radio_COMNAV1", "at": [0.5, 0.5, 0.5]}, "width": 0.34,
            "azimuth": 0, "elevation": 0, "distance": 0.5}, "size": [1200, 1200], "light": "panel", "samples": 64, "fine_textures": True, "hide": ["INTERIOR.yoke_*", "INTERIOR.yoke_shaft_*", "PANEL.control_wheel_*"],
            "anchors": {"audio": {"part": "PANEL.radio_AUDIO", "at": [0.5, 0.5, 0.5]}, "com1": {"part": "PANEL.radio_COMNAV1", "at": [0.5, 0.5, 0.5]},
                        "com2": {"part": "PANEL.radio_COMNAV2", "at": [0.5, 0.5, 0.5]}, "xpdr": {"part": "PANEL.radio_XPDR", "at": [0.5, 0.5, 0.5]},
                        "jacks": {"part": "PANEL.microphone_jacks", "at": [0.5, 0.5, 0.5]}}}},
        # the operating-limitations placard of the model, its last two lines only (Figure 26-1: the flight manual comes first)
        {"id": "panel-26-01-placard", "width_m": 0.17, "render": {"camera": {"view": "panel", "target": {"part": "PANEL.placard_speed", "at": [0.5, 0.5, 0.25]}, "width": 0.17,
            "azimuth": 0, "elevation": 0, "distance": 0.5}, "size": [1700, 260], "light": "panel", "samples": 64, "fine_textures": True, "hide": ["INTERIOR.yoke_*", "INTERIOR.yoke_shaft_*", "PANEL.control_wheel_*"]}},
        # the cabin of the model from above and behind on the left, the skin, the roof and the wings taken away (Figure 13-5: the passenger briefing)
        {"id": "cabin-13-05-briefing", "width_m": 3.4, "render": {"light": "outdoor", "parked": True, "propeller": "none",
            "camera": {"view": "side", "target": [0.0, 0.55, 0.95], "width": 3.4, "azimuth": 215, "elevation": 48},
            "hide": ["AIRFRAME.fuselage", "WING_*", "INTERIOR.headliner", "INTERIOR.overhead_console", "AIRFRAME.windshield", "AIRFRAME.rear_window", "AIRFRAME.window_rear_*",
                     "AIRFRAME.door_L", "AIRFRAME.door_window_L", "AIRFRAME.door_*_L*", "INTERIOR.door_*_L", "INTERIOR.cabin_liner", "ELECTRICAL.adf_sense_wire", "AIRFRAME.carry_through_*",
                     "EMPENNAGE.*", "ENGINE.*", "AIRFRAME.cabin_vent_*", "ELECTRICAL.harness_wing_*", "AIRFRAME.marking_wordmark_*"],
            "props": [{"kind": "cylinder", "at": {"part": "INTERIOR.floor", "at": [0.5, 0.5, 1.0], "add": [0.0, 0.0, 0.17]}, "size": [0.045, 0.32], "rot": [90, 0, 0], "colour": "#C62828"}],
            "anchors": {"belt": {"part": "INTERIOR.seat_pilot.lap_belt", "at": [0.5, 0.5, 0.5]}, "harness": {"part": "INTERIOR.shoulder_harness_R", "at": [0.5, 0.5, 0.6]},
                        "back": {"part": "INTERIOR.seat_copilot.back", "at": [0.5, 0.5, 0.8]}, "door": {"part": "AIRFRAME.door_handle_R", "at": [0.5, 0.5, 0.5]},
                        "door_in": {"part": "INTERIOR.door_inner_handle_R", "at": [0.5, 0.5, 0.5]}, "net": {"part": "INTERIOR.baggage_net", "at": [0.5, 0.5, 0.5]},
                        "elt": {"part": "AVIONICS.elt", "at": [0.5, 0.5, 0.5]}, "ext": {"part": "INTERIOR.floor", "at": [0.5, 0.5, 1.0], "add": [0.0, 0.0, 0.30]},
                        "rear_back": {"part": "INTERIOR.seat_rear.back_L", "at": [0.5, 0.5, 0.8]}, "panel": {"part": "INTERIOR.glareshield", "at": [0.5, 0.5, 0.5]}},
            "size": [1800, 1300], "samples": 64, "mirror": True}},
        *__import__("figs.spots", fromlist=["spots"]).spots(),        # the small pictures of figs/spots.py
    ]
