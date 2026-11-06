"""Minimal deterministic glTF 2.0 binary (GLB) writer for the Phase 7 model."""
from __future__ import annotations

import json
import struct

import numpy as np

from geometry import Geom

ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER = 34962, 34963
FLOAT, UNSIGNED_SHORT, UNSIGNED_INT = 5126, 5123, 5125


class GLB:
    def __init__(self, generator: str):
        self.doc = {
            "asset": {"version": "2.0", "generator": generator},
            "scene": 0,
            "scenes": [{"name": "Scene", "nodes": []}],
            "nodes": [],
            "meshes": [],
            "materials": [],
            "accessors": [],
            "bufferViews": [],
            "buffers": [],
        }
        self.bin = bytearray()
        self._mat = {}

    # ------------------------------------------------------------ materials
    def material(self, name, rgba, metallic=0.0, roughness=0.6, emissive=None, double_sided=False):
        if name in self._mat:
            return self._mat[name]
        m = {
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorFactor": [round(float(c), 4) for c in rgba],
                "metallicFactor": metallic,
                "roughnessFactor": roughness,
            },
        }
        if rgba[3] < 1.0:
            m["alphaMode"] = "BLEND"
            double_sided = True
        if emissive:
            m["emissiveFactor"] = [round(float(c), 4) for c in emissive]
        if double_sided:
            m["doubleSided"] = True
        self.doc["materials"].append(m)
        self._mat[name] = len(self.doc["materials"]) - 1
        return self._mat[name]

    # -------------------------------------------------------------- buffers
    def _view(self, data: bytes, target):
        while len(self.bin) % 4:
            self.bin.append(0)
        self.doc["bufferViews"].append({"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(data), "target": target})
        self.bin += data
        return len(self.doc["bufferViews"]) - 1

    def _accessor(self, arr: np.ndarray, kind):
        if kind == "index":
            flat = arr.reshape(-1)
            if flat.max() < 65535:
                data, ctype = flat.astype("<u2").tobytes(), UNSIGNED_SHORT
            else:
                data, ctype = flat.astype("<u4").tobytes(), UNSIGNED_INT
            view = self._view(data, ELEMENT_ARRAY_BUFFER)
            acc = {"bufferView": view, "componentType": ctype, "count": int(flat.size), "type": "SCALAR"}
        else:
            a = arr.astype("<f4")
            view = self._view(a.tobytes(), ARRAY_BUFFER)
            acc = {"bufferView": view, "componentType": FLOAT, "count": int(len(a)), "type": "VEC3"}
            if kind == "position":
                acc["min"] = [float(x) for x in a.min(0)]
                acc["max"] = [float(x) for x in a.max(0)]
        self.doc["accessors"].append(acc)
        return len(self.doc["accessors"]) - 1

    def mesh(self, name, geom: Geom, material: int):
        # Round before float32 conversion so rebuilds are byte-stable across platforms.
        v = np.round(geom.v, 5)
        n = np.round(geom.n, 4)
        prim = {
            "attributes": {"POSITION": self._accessor(v, "position"), "NORMAL": self._accessor(n, "normal")},
            "indices": self._accessor(geom.f.astype(np.int64), "index"),
            "material": material,
        }
        self.doc["meshes"].append({"name": name, "primitives": [prim]})
        return len(self.doc["meshes"]) - 1

    # ---------------------------------------------------------------- nodes
    def node(self, name, parent=None, t=None, q=None, s=None, mesh=None, extras=None):
        nd = {"name": name}
        if t is not None and any(abs(x) > 1e-9 for x in t):
            nd["translation"] = [round(float(x), 5) for x in t]
        if q is not None and abs(q[3] - 1.0) > 1e-9:
            nd["rotation"] = [round(float(x), 6) for x in q]
        if s is not None:
            nd["scale"] = [round(float(x), 5) for x in s]
        if mesh is not None:
            nd["mesh"] = mesh
        if extras:
            nd["extras"] = extras
        self.doc["nodes"].append(nd)
        idx = len(self.doc["nodes"]) - 1
        if parent is None:
            self.doc["scenes"][0]["nodes"].append(idx)
        else:
            self.doc["nodes"][parent].setdefault("children", []).append(idx)
        return idx

    # ---------------------------------------------------------------- write
    def to_bytes(self) -> bytes:
        while len(self.bin) % 4:
            self.bin.append(0)
        self.doc["buffers"] = [{"byteLength": len(self.bin)}]
        js = json.dumps(self.doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        js += b" " * ((4 - len(js) % 4) % 4)
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        out = bytearray(struct.pack("<4sII", b"glTF", 2, total))
        out += struct.pack("<I4s", len(js), b"JSON") + js
        out += struct.pack("<I4s", len(self.bin), b"BIN\x00") + self.bin
        return bytes(out)
