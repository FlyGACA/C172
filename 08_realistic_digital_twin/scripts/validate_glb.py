#!/usr/bin/env python3
"""Structural validation of the Phase 8 GLBs without Blender or a browser.
Checks: GLB container, required extensions, every mesh primitive has NORMAL + TEXCOORD_0,
materials have PBR data, every part node carries the Phase 8 extras, sizes within budget."""
import json
import struct
import sys
import os

BUDGET_MB = {"high": 25, "medium": 12, "low": 5}
TRI_BUDGET = {"high": 600_000, "medium": 250_000, "low": 100_000}

def read_glb(path):
    with open(path, "rb") as f:
        magic, version, length = struct.unpack("<III", f.read(12))
        assert magic == 0x46546C67 and version == 2, "not a glTF 2.0 binary"
        clen, ctype = struct.unpack("<II", f.read(8))
        assert ctype == 0x4E4F534A, "first chunk must be JSON"
        js = json.loads(f.read(clen))
    return js, length

def main(models_dir):
    ok = True
    for lod in ("high", "medium", "low"):
        p = os.path.join(models_dir, f"C172N_realistic_{lod}.glb")
        if not os.path.exists(p):
            print(f"[{lod}] MISSING {p}"); ok = False; continue
        js, length = read_glb(p)
        mb = length / 1e6
        probs = []
        if mb > BUDGET_MB[lod]:
            probs.append(f"size {mb:.1f} MB > budget {BUDGET_MB[lod]} MB")
        if "KHR_draco_mesh_compression" not in js.get("extensionsRequired", []):
            probs.append("Draco compression not required/enabled")
        prims = 0
        for m in js.get("meshes", []):
            for pr in m["primitives"]:
                prims += 1
                a = pr["attributes"]
                if "NORMAL" not in a: probs.append(f"mesh {m['name']} has no NORMAL")
                if "TEXCOORD_0" not in a: probs.append(f"mesh {m['name']} has no TEXCOORD_0")
                if "material" not in pr: probs.append(f"mesh {m['name']} has no material")
        for mat in js.get("materials", []):
            if "pbrMetallicRoughness" not in mat: probs.append(f"material {mat.get('name')} is not PBR")
        parts = 0; missing = []
        for n in js.get("nodes", []):
            ex = n.get("extras", {})
            if "mesh" in n:
                parts += 1
                for k in ("system", "label_en", "label_ar", "status"):
                    if k not in ex: missing.append(f"{n.get('name')}:{k}")
                if ex.get("status") not in ("poh", "type_data", "estimated"):
                    missing.append(f"{n.get('name')}:status={ex.get('status')}")
        if missing: probs.append(f"{len(missing)} nodes with missing/invalid extras, e.g. {missing[:3]}")
        idx_path = os.path.join(models_dir, f"model_index_{lod}.json")
        tris = None
        if os.path.exists(idx_path):
            with open(idx_path, encoding="utf-8") as f:
                idx = json.load(f)
            tris = idx["triangles"]
            if tris > TRI_BUDGET[lod]: probs.append(f"{tris} triangles > budget {TRI_BUDGET[lod]}")
        status = "OK" if not probs else "FAIL"
        print(f"[{lod}] {status}: {mb:.1f} MB, {len(js.get('nodes', []))} nodes, {parts} mesh nodes, {prims} primitives, {len(js.get('materials', []))} materials, {len(js.get('images', []))} images, {tris} triangles")
        for pr_ in probs:
            print("   -", pr_)
        ok = ok and not probs
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")))
