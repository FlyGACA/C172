"""Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-25-07-run-up",
        "replaces": "fig-25-07-run-up.svg",
        "book_file": "plate-25-07-run-up.jpg",
        "caption": "Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast",
        "desc": "Figure 25-7. A run-up position: into wind, on a clean surface, with nothing in the propeller blast",
        "legend": [
            "Wind.",
            "Nose into wind, nosewheel straight.",
            "Propeller blast: nothing behind you.",
            "Firm, clean surface, clear of the taxiway.",
            "Loose sand: it nicks the propeller.",
            "Runway-holding position: run up before it.",
            "The next aircraft, out of your blast.",
            "Traffic on final: look before you enter the runway.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-25-07-run-up.svg", "remove": [r'<circle cx="[\d.]+" cy="[\d.]+" r="1\.3" fill="#b45309"/>']}, "terrain-25-07", seed=257, kind="plain", veil=0.30, fills={"#f3f4f6": "concrete", "#fdf0e1": "gravel"}),
    }
