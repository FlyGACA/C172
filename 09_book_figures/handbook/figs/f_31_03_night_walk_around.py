"""Figure 31-3. The night walk-around: the lights, the ramp and the cockpit. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-31-03-night-walk-around",
        "replaces": "fig-31-03-night-walk-around.svg",
        "book_file": "plate-31-03-night-walk-around.jpg",
        "caption": "Figure 31-3. The night walk-around: the lights, the ramp and the cockpit",
        "desc": "Figure 31-3. The night walk-around: the lights, the ramp and the cockpit",
        "legend": [
            "Torch on white: light each item, not just the area.",
            "Left wingtip: red position light.",
            "Right wingtip: green position light.",
            "Tail: white position light.",
            "Anticollision beacon.",
            "Landing and taxi light.",
            "Hazards the dark hides: chocks, tie-downs, holes, ladders.",
            "Windscreen, clean inside and out.",
            "Fuel and oil, by torchlight.",
            "Cockpit: panel lights work and dim; red torch and spare batteries within reach.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {
            "svg": "fig-31-03-night-walk-around.svg",
            # the drawing of the aeroplane is the model by moonlight, the ramp is dark, the torch and the lights stay as they were
            "drop": [['<path d="M463.1 173.3', '<polygon points="80,324 239.2,163.8']],
            "sprites": [{"name": "sprite-top-night", "at": [299, 243], "width": 340, "shadow": {"dx": 0, "dy": 0, "blur": 6, "opacity": 0.35}}],
            "replace": [['fill="#fdf0e1" opacity="0.9"/>', 'fill="#FFD27A" opacity="0.34"/>'], ['fill="#ffffff" opacity="0.55"/>', 'fill="#FFFFFF" opacity="0.30"/>'], ['<rect x="10" y="10" width="620" height="400" rx="8" fill="#f3f4f6"/>', '<rect x="10" y="10" width="620" height="400" rx="8" fill="#0F1A34"/>']],
        },
    }
