"""Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-28-01-slow-flight",
        "replaces": "fig-28-01-slow-flight.svg",
        "book_file": "plate-28-01-slow-flight.jpg",
        "caption": "Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve",
        "desc": "Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve",
        "legend": [
            "Cruise: nose near the horizon, cruise power.",
            "Slow flight with full flap: nose high, altitude held.",
            "The angle of attack between the chord line (dashed) and the level flight path (green): large.",
            "Throttle position.",
            "Power required for level flight against airspeed; schematic, not the example aeroplane's data.",
            "Minimum power.",
            "The region of reversed command.",
            "Slow flight (amber point); cruise is the green point.",
            "`VS0`, 45 kt.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {
            "svg": "fig-28-01-slow-flight.svg",
            # the two aeroplanes of the old figure (cruise and slow flight with full flap) are the model, in the same places and attitudes
            "remove": [r'<g transform="translate\(189\.6 95\.7\) rotate\(0\.63\) translate\(-125\.3 -32\.1\)">.*?</g>', r'<g transform="translate\(186\.5 250\.6\) rotate\(-9\.91\) translate\(-125\.3 -32\.1\)">.*?</g>'],
            "sprites": [{"name": "sprite-side", "at": [189.6, 95.7], "width": 250, "angle": 0.63, **LOOK}, {"name": "sprite-side", "at": [186.5, 250.6], "width": 250, "angle": -9.91, **LOOK}],
        },
    }
