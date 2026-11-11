"""Figure 15-6. Mechanical turbulence, mountain wave and rotor. The diagram of the book's figure (the ridge, the buildings, the streamlines, the arrows and the numbered
callouts) on a sky and with the clouds of the model of the sky (reskin.py, figs/clouds.py): the lens-shaped cloud on the crest, and a roll cloud in each rotor."""

SKY = ('<defs><linearGradient id="f1506-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FBFE4"/><stop offset="1" stop-color="#E9F1FA"/></linearGradient>'
       '<linearGradient id="f1506-rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D5D9DF"/><stop offset="0.5" stop-color="#A5ADB8"/><stop offset="1" stop-color="#7A8391"/></linearGradient></defs>'
       '<rect x="0" y="0" width="640" height="330" fill="url(#f1506-sky)"/>')
BACKGROUND = '<rect x="0" y="0" width="640" height="380" fill="#ffffff"/>'
RIDGE = '<polygon points="0,330 226,330 262,284 300,222 330,186 356,214 392,272 430,330 640,330 640,380 0,380" fill="#e5e7eb" stroke="#1f2937" stroke-width="1.5"/>'
SHADE = '<polygon points="330,186 356,214 392,272 430,330 330,330" fill="#1f2937" fill-opacity="0.2"/>'        # the lee side in shade
LENS = '<ellipse cx="475" cy="84" rx="46" ry="10" fill="#9ca3af" stroke="#9ca3af" stroke-width="3"/>'          # the outlined lens (two ellipses) ...
NEXT = '<line x1="250" y1="286" x2="299.1" y2="213.3" stroke="#b45309" stroke-width="3.5"/>'                    # ... up to the first arrow


def plate():
    return {
        "id": "fig-15-06-mountain-wave",
        "replaces": "fig-15-06-mountain-wave.svg",
        "book_file": "plate-15-06-mountain-wave.jpg",
        "caption": "Figure 15-6. Mechanical turbulence, mountain wave and rotor",
        "desc": "Figure 15-6. Mechanical turbulence, mountain wave and rotor",
        "legend": [
            "Wind.",
            "Eddies and gusts downwind of buildings near the runway.",
            "Smooth rising air on the windward slope.",
            "Strong sinking air on the lee slope, which can exceed a light aeroplane's climb.",
            "Standing wave crests.",
            "Lens-shaped cloud marking a crest.",
            "Rotors: violent turbulence below the crests.",
            "The ridge.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-06-mountain-wave.svg",
            "replace": [[BACKGROUND, BACKGROUND + SKY], [RIDGE, RIDGE.replace('fill="#e5e7eb"', 'fill="url(#f1506-rock)"') + SHADE]],
            "drop": [[LENS, NEXT, {"sprites": [
                {"name": "cloud-lenticular", "at": [475, 82], "width": 108},
                {"name": "cloud-roll", "at": [470, 262], "width": 76},
                {"name": "cloud-roll", "at": [598, 272], "width": 58},
            ]}]],
        },
    }
