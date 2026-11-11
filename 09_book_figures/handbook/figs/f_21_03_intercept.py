"""Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-03-intercept",
        "replaces": "fig-21-03-intercept.svg",
        "book_file": "plate-21-03-intercept.jpg",
        "caption": "Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind",
        "desc": "Figure 21-3. Intercepting the 060 radial outbound and tracking it in a crosswind",
        "legend": [
            "The station; the OBS stays on 060.",
            "On the 120 radial, 10 NM out: needle full scale left.",
            "Heading 015: a 45° intercept angle.",
            "Lead the turn as the needle leaves full scale: here about 2 dots, with the radial 3° to 4° away.",
            "On the radial, needle centred, heading 052.",
            "Wind 330° at 15 kt.",
            "All three displays: OBS 060, `FR`.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-21-03-intercept.svg"},
    }
