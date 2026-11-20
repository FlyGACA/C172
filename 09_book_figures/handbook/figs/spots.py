"""Small pictures of the model on a transparent ground ("spots"), for the figures to use in place of drawn icons: each instrument of the panel on its own,
and parts of the aeroplane a figure names (the engine, the propeller, the magneto, the fuel selector, the control lock, the pitot tube...). They are sprites
(figs/sprites.py lists them with its own; npm run plates:render, or render_plate.py --plate <id>, makes them) and a figure lays them as any sprite:
{"name": "spot-asi", "at": [x, y], "width": w}.

    spot-<instrument>   the instrument of the model, bezel, dial and pointers, with an ordinary reading (kit.dial_sprite)
    spot-<part>         the part (and what is fixed to it) on its own, three-quarters from the front and above, in the outdoor light of the sprites

The parts are the model's (08_realistic_digital_twin): where a part is still a simple block in the model (the carburettor), it has no spot."""
from figs.kit import dial_sprite

# (id, the instrument of the model, its reading)
INSTRUMENTS = [
    ("spot-asi", "ASI", {"ASI": 95}), ("spot-ai", "AI", {"pitch": 0, "bank": 0}), ("spot-alt", "ALT", {"ALT": 3500}), ("spot-tc", "TC", {}),
    ("spot-dg", "DG", {"heading": 90}), ("spot-vsi", "VSI", {"VSI": 0}), ("spot-tach", "TACH", {}), ("spot-oil-t", "OIL_T", {}), ("spot-oil-p", "OIL_P", {}),
    ("spot-fuel-l", "FUEL_L", {}), ("spot-fuel-r", "FUEL_R", {}), ("spot-ammeter", "AMMETER", {}), ("spot-suction", "SUCTION", {}), ("spot-clock", "CLOCK", {}),
    ("spot-vor", "VOR1", {}), ("spot-adf", "ADF", {}),
]

# (id, the parts shown, the part the camera is aimed at, the width of the picture in metres, azimuth, elevation, the view)
PARTS = [
    ("spot-engine", ["ENGINE.*", "IGNITION.*", "INDUCTION.*", "OIL.*", "ELECTRICAL.alternator*", "ELECTRICAL.starter", "VACUUM.engine_driven_pump", "POWERPLANT.propeller", "POWERPLANT.spinner*"],
     "IGNITION.dual_magneto", 1.9, 35, 20, "side"),
    ("spot-propeller", ["POWERPLANT.propeller", "POWERPLANT.propeller_bolt", "POWERPLANT.spinner", "POWERPLANT.spinner_backplate"], "POWERPLANT.spinner", 2.1, 60, 10, "side"),
    ("spot-magneto", ["IGNITION.dual_magneto"], "IGNITION.dual_magneto", 0.32, 35, 20, "side"),
    ("spot-battery", ["ELECTRICAL.battery"], "ELECTRICAL.battery", 0.36, 35, 25, "side"),
    ("spot-oil-dipstick", ["OIL.dipstick_filler"], "OIL.dipstick_filler", 0.32, 35, 20, "side"),
    ("spot-pitot", ["PITOT_STATIC.pitot_tube"], "PITOT_STATIC.pitot_tube", 0.42, 35, 15, "side"),
    ("spot-fuel-cap", ["WING_L.fuel_cap"], "WING_L.fuel_cap", 0.16, 35, 55, "side"),
    ("spot-fuel-selector", ["FUEL.selector_*"], "FUEL.selector_plate", 0.26, 20, 55, "side"),
    ("spot-control-lock", ["INTERIOR.control_lock", "INTERIOR.yoke_L", "INTERIOR.yoke_shaft_L", "PANEL.control_wheel_collars"], "INTERIOR.control_lock", 0.45, -40, 25, "side"),
    ("spot-yoke", ["INTERIOR.yoke_L", "INTERIOR.yoke_shaft_L"], "INTERIOR.yoke_L", 0.5, 25, 10, "side"),
    ("spot-nose-gear", ["GEAR.nose_*"], "GEAR.nose_strut", 1.1, 35, 10, "side"),
    ("spot-main-wheel", ["GEAR.main_wheel_L.*", "GEAR.main_leg_L", "GEAR.main_wheel_fairing_L", "GEAR.brake_line_L"], "GEAR.main_wheel_L.tyre", 1.3, 30, 10, "side"),
    ("spot-compass", ["PANEL.magnetic_compass"], "PANEL.magnetic_compass", 0.16, 0, 0, "panel"),
    ("spot-ignition", ["PANEL.ignition", "PANEL.ignition_switch", "PANEL.ignition_nut"], "PANEL.ignition_switch", 0.12, 0, 0, "panel"),
    ("spot-master", ["PANEL.master_alt", "PANEL.master_bat", "PANEL.lower_panel"], "PANEL.master_bat", 0.14, -35, 25, "panel"),
    ("spot-engine-controls", ["PANEL.throttle*", "PANEL.mixture*", "PANEL.carb_heat*", "PANEL.primer*"], "PANEL.mixture", 0.30, -30, 20, "panel"),
]


def spots():
    out = [dial_sprite(sid, inst, reading) for sid, inst, reading in INSTRUMENTS]
    for sid, show, target, width, az, el, view in PARTS:
        cam = {"view": view, "target": {"part": target, "at": [0.5, 0.5, 0.5]}, "width": width, "azimuth": az, "elevation": el}
        if view == "panel":
            cam["distance"] = 0.5
        out.append({"id": sid, "width_m": width, "render": {"camera": cam, "size": [1200, 1200], "light": "panel" if view == "panel" else "outdoor",
                                                            "show": show, "samples": 64, "fine_textures": True, "propeller": "blades"}})
    return out
