#!/usr/bin/env python3
"""Run the recovered-r11 builder with KiCad-9 text-free placement geometry.

KiCad FOOTPRINT.GetBoundingBox() includes footprint fields/text by default.
Those fields are display annotations, not component placement envelopes, and
can make long connector value strings artificially consume a reserve.  r11
packing therefore uses GetBoundingBox(False) while KiCad courtyard/clearance
DRC remains the actual placement-rule authority after generation.
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


mod.bbox_local_mm = bbox_local_mm_no_text
mod.main()
