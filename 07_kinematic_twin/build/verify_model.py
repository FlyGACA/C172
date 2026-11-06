#!/usr/bin/env python3
"""Rebuild the Phase 7 GLB in a temp dir and check it matches the committed file.

Byte-identical output is expected; if a different numpy/platform changes the last
float bits, the structure must still match and vertices may differ by < 1e-4 m.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import subprocess
import sys
import tempfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
COMMITTED = ROOT / "C172N_Phase7_Kinematic_Twin.glb"
INDEX = ROOT / "data" / "model_index.json"


def load(path: pathlib.Path):
    b = path.read_bytes()
    _, _, length = struct.unpack_from("<4sII", b, 0)
    off, js, binc = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<I4s", b, off)
        off += 8
        chunk = b[off:off + clen]
        off += clen
        if ctype == b"JSON":
            js = json.loads(chunk)
        else:
            binc = chunk
    return js, binc


def positions(js, binc):
    out = []
    for m in js["meshes"]:
        acc = js["accessors"][m["primitives"][0]["attributes"]["POSITION"]]
        bv = js["bufferViews"][acc["bufferView"]]
        out.append(np.frombuffer(binc, "<f4", acc["count"] * 3, bv["byteOffset"]).reshape(-1, 3))
    return out


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out, idx = pathlib.Path(tmp) / "model.glb", pathlib.Path(tmp) / "index.json"
        subprocess.run([sys.executable, str(HERE / "build_phase7_model.py"), "--out", str(out), "--index", str(idx)], check=True)
        a, b = COMMITTED.read_bytes(), out.read_bytes()
        if json.loads(idx.read_text()) | {"bytes": 0} != json.loads(INDEX.read_text()) | {"bytes": 0}:
            print("FAIL: data/model_index.json is stale - run npm run build:model")
            return 1
        if a == b:
            print(f"OK: rebuilt GLB is byte-identical (sha256 {hashlib.sha256(a).hexdigest()[:16]}…)")
            return 0
        ja, ba = load(COMMITTED)
        jb, bb = load(out)
        names = lambda j: [n["name"] for n in j["nodes"]]
        if names(ja) != names(jb) or len(ja["meshes"]) != len(jb["meshes"]):
            print("FAIL: node/mesh structure differs - the committed GLB is out of date; run npm run build:model")
            return 1
        worst = max(float(np.abs(pa - pb).max()) for pa, pb in zip(positions(ja, ba), positions(jb, bb)))
        if worst > 1e-4:
            print(f"FAIL: geometry differs by up to {worst:.6f} m - run npm run build:model")
            return 1
        print(f"OK: same structure, float noise only (max {worst:.2e} m)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
