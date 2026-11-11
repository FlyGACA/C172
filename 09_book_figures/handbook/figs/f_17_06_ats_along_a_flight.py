"""Figure 17-6. The air traffic services a VFR flight meets from departure to arrival. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-17-06-ats-along-a-flight",
        "replaces": "fig-17-06-ats-along-a-flight.svg",
        "book_file": "plate-17-06-ats-along-a-flight.jpg",
        "caption": "Figure 17-6. The air traffic services a VFR flight meets from departure to arrival",
        "desc": "Figure 17-6. The air traffic services a VFR flight meets from departure to arrival",
        "legend": [
            "Aerodrome A: the tower (`TWR`) clears you to taxi and take off [[§91.99(f)]] [[§91.127(i)]].",
            "Leaving the control zone: the tower transfers you, or you report that you are leaving ATC service [[§91.99(g)]].",
            "En route: flight information service (`FIS`).",
            "Approaching aerodrome B, without a tower: TIBA broadcasts [[§91.121(d)]].",
            "After landing: the arrival report [[§91.73(h)]].",
            "Approach control (`APP`), dashed: only if the route enters the TMA or ATC transfers you.",
            "Alerting service, from departure to the arrival report.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-17-06-ats-along-a-flight.svg"},
    }
