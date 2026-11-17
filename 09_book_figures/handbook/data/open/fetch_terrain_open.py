"""Fetch open elevation data for the country round Thumamah and Riyadh and write it next to this file.

Source: NASA Shuttle Radar Topography Mission (SRTM), 1 arc-second, public domain, as the HGT tiles of the "Terrain Tiles" open dataset on AWS
(s3://elevation-tiles-prod/skadi/). Four tiles (N24E046, N25E046, N24E047, N25E047) are cut to 24.70-25.50 N, 46.20-47.20 E and thinned to
2 arc-seconds (about 60 m), which is finer than any figure draws.  -> riyadh_terrain.npz (int16 metres above mean sea level, row 0 is the north edge)
and riyadh_terrain.json.   Needs numpy and network access.   python fetch_terrain_open.py      Not for navigation.
"""
import gzip
import json
import os
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAT0, LAT1, LON0, LON1 = 24.70, 25.50, 46.20, 47.20
STEP = 2                                              # keep every second sample: 2 arc-seconds


def tile(lat, lon):
    name = f"N{lat:02d}E{lon:03d}"
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/N{lat:02d}/{name}.hgt.gz"
    raw = gzip.decompress(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "handbook-figure-builder/1.0"}), timeout=180).read())
    a = np.frombuffer(raw, dtype=">i2").reshape(3601, 3601).astype(np.int16)      # row 0 is the north edge (lat + 1), column 0 the west edge
    print(name, a.shape, int(a.min()), int(a.max()), flush=True)
    return a


def main():
    rows = []
    for lat in (25, 24):                              # north tile first
        rows.append(np.hstack([tile(lat, 46)[:, :-1], tile(lat, 47)]))            # the tiles share their edge column
    full = np.vstack([rows[0][:-1, :], rows[1]])      # rows from 26 N down to 24 N, columns from 46 E to 48 E, 1 arc-second
    r0, r1 = round((26.0 - LAT1) * 3600), round((26.0 - LAT0) * 3600)
    c0, c1 = round((LON0 - 46.0) * 3600), round((LON1 - 46.0) * 3600)
    cut = full[r0:r1 + 1:STEP, c0:c1 + 1:STEP]
    np.savez_compressed(os.path.join(HERE, "riyadh_terrain.npz"), elevation_m=cut)
    meta = {"source": "NASA Shuttle Radar Topography Mission (SRTM), 1 arc-second, from the Terrain Tiles open dataset on AWS (skadi HGT tiles N24E046, N25E046, N24E047, N25E047)",
            "licence": "SRTM data are in the public domain", "attribution": "Elevation: NASA SRTM",
            "north": LAT1, "south": LAT0, "west": LON0, "east": LON1, "step_arcsec": STEP, "shape": list(cut.shape), "units": "metres above mean sea level (EGM96)",
            "min_m": int(cut.min()), "max_m": int(cut.max())}
    json.dump(meta, open(os.path.join(HERE, "riyadh_terrain.json"), "w"), indent=1)
    print("wrote riyadh_terrain.npz", cut.shape, meta["min_m"], "to", meta["max_m"], "m")


if __name__ == "__main__":
    main()
