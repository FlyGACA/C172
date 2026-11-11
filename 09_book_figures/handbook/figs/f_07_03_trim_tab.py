"""Figure 7-3. An elevator trim tab set for nose-up trim. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


def plate():
    return {
        "id": "fig-07-03-trim-tab",
        "replaces": "fig-07-03-trim-tab.svg",
        "book_file": "plate-07-03-trim-tab.jpg",
        "caption": "Figure 7-3. An elevator trim tab set for nose-up trim",
        "desc": "Figure 7-3. An elevator trim tab set for nose-up trim",
        "legend": [
            "Horizontal stabilizer, fixed.",
            "Elevator hinge.",
            "Elevator, trailing edge held up.",
            "Trim tab, deflected down, opposite to the elevator.",
            "Air load on the tab, holding the elevator in place.",
            "Extra downward load on the tail.",
            "Relative airflow.",
            "The tail load holds the nose up about the centre of gravity; the aeroplane settles at a lower airspeed with no force on the controls.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-07-03-trim-tab.svg",
            # the small aeroplane at the top left, a cartoon in the old figure, is the model seen from the left, with the centre of gravity on it
            "drop": [["<!-- Small aircraft symbol (top-left inset) -->", "<!-- Control surface movement arrow -->"]],
            "sprites": [{"name": "sprite-side-left", "at": [143, 66], "width": 207, **LOOK}],
            "markup": '<g transform="translate(-28 -5)"><circle cx="122" cy="76" r="6" fill="#ffffff" stroke="#475569" stroke-width="1.3"/>'
                      '<path d="M122,70 A6,6 0 0,1 128,76 L122,76 Z" fill="#475569"/><path d="M122,82 A6,6 0 0,1 116,76 L122,76 Z" fill="#475569"/></g>',
        },
    }
