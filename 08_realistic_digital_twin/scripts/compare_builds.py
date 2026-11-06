#!/usr/bin/env python3
"""Compare two Phase 8 build outputs (model_index_*.json): same parts, same triangle counts,
GLB sizes within 2 %. Used by CI to prove the scripted build reproduces the committed model."""
import json
import os
import sys

def load(d, lod):
    with open(os.path.join(d, f"model_index_{lod}.json"), encoding="utf-8") as f:
        return json.load(f)

def main(a, b):
    ok = True
    for lod in ("high", "medium", "low"):
        ia, ib = load(a, lod), load(b, lod)
        pa = {p["name"]: p["triangles"] for p in ia["parts"]}
        pb = {p["name"]: p["triangles"] for p in ib["parts"]}
        missing = sorted(set(pa) ^ set(pb))
        diff = [n for n in pa if n in pb and pa[n] != pb[n]]
        size_ok = abs(ia["bytes"] - ib["bytes"]) <= 0.02 * ia["bytes"]
        status = "OK" if not missing and not diff and size_ok else "DIFF"
        print(f"[{lod}] {status}: {len(pa)} vs {len(pb)} parts, {ia['triangles']} vs {ib['triangles']} tris, {ia['bytes']} vs {ib['bytes']} bytes")
        if missing: print("   parts only on one side:", missing[:10]); ok = False
        if diff: print("   triangle count differs:", [(n, pa[n], pb[n]) for n in diff[:10]]); ok = False
        if not size_ok: ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
