"""Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""
from figs import h_plan



def plate():
    return {
        "id": "fig-25-06-taxi-wind",
        "replaces": "fig-25-06-taxi-wind.svg",
        "book_file": "plate-25-06-taxi-wind.jpg",
        "caption": "Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind",
        "desc": "Figure 25-6. Holding the controls while taxiing a nosewheel aeroplane in wind",
        "legend": [
            "Quartering headwind from the left: wheel turned left, into the wind (left aileron up); elevator neutral.",
            "Quartering headwind from the right: wheel turned right; elevator neutral.",
            "Quartering tailwind from the left: wheel turned right, away from the wind (left aileron down), and forward (elevator down).",
            "Quartering tailwind from the right: wheel turned left and forward.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": h_plan.layer({"svg": "fig-25-06-taxi-wind.svg"}, "terrain-25-06", seed=256, kind="apron", features=("tyres",), veil=0.0, soft=1.0, markup='<line x1="320" y1="0" x2="320" y2="400" stroke="#2B2A25" stroke-opacity="0.22" stroke-width="5.4"/><line x1="320" y1="0" x2="320" y2="400" stroke="#F2BE2B" stroke-width="3"/>'),
    }
