"""Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-21-08-cross-check-fix",
        "replaces": "fig-21-08-cross-check-fix.svg",
        "book_file": "plate-21-08-cross-check-fix.jpg",
        "caption": "Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart",
        "desc": "Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart",
        "legend": [
            "Planned track 030° from aerodrome A; distances from A in NM.",
            "WADI, planned for 0615 UTC: radial 300, 8.0 NM from `NKL`.",
            "The fictional VOR/DME `NKL`; dashed grey, the planned 300 radial.",
            "The fix at 0614 UTC: the 290 radial and the 10 NM DME arc.",
            "The GNSS position, a few tenths of a mile from the fix.",
            "The wadi and the road crossing at WADI.",
            "New track to B, 034°, on heading 043.",
            "The track continues to aerodrome B, 48 NM from A.",
            "VOR indicator: OBS 290, needle centred, `FR`.",
            "DME 10.0 NM; slant range is negligible here.",
            "Scale in NM.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-21-08-cross-check-fix.svg"},
    }
