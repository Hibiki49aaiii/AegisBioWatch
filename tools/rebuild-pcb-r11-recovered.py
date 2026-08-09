#!/usr/bin/env python3
"""Run the recovered-r11 builder with KiCad-9 physical placement geometry.

KiCad FOOTPRINT.GetBoundingBox() includes footprint fields/text by default.
Those annotations are not component placement envelopes, so packing uses
GetBoundingBox(False).  The Main<->Bio FH12 connector is physically wide; its
KiCad no-text bounding box already contains the library placement geometry, so
only a small extra packing guard is added around J7.  KiCad courtyard and
clearance DRC remains final placement-rule authority after generation.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools/rebuild-pcb-r11-from-r8-r10.py"

spec = importlib.util.spec_from_file_location("aegis_r11_builder", TARGET)
if spec is None or spec.loader is None:
    raise SystemExit(f"unable to load {TARGET}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def bbox_local_mm_no_text(fp):
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    box = fp.GetBoundingBox(False)
    return (
        float(pcbnew.ToMM(box.GetX())),
        float(pcbnew.ToMM(box.GetY())),
        float(pcbnew.ToMM(box.GetWidth())),
        float(pcbnew.ToMM(box.GetHeight())),
    )


original_scan_place = mod.scan_place


def scan_place_physical(fp, zone, occupied, margin=0.25):
    ref = fp.GetReference()
    if ref == "J7":
        margin = 0.10
    return original_scan_place(fp, zone, occupied, margin)


mod.bbox_local_mm = bbox_local_mm_no_text
mod.scan_place = scan_place_physical
mod.ZONES["BIO"] = (100.25, 74.25, 115.75, 82.75)

j7 = mod.load_fp("Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
j7.SetReference("J7")
print("J7 KiCad GetBoundingBox(False) mm =", bbox_local_mm_no_text(j7))
print("BIO recovered reserve mm =", mod.ZONES["BIO"])

mod.main()
