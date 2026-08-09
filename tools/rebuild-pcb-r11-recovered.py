#!/usr/bin/env python3
"""Build a recovered r11 placement seed in the actual r10 board datum.

The historical r11 payload is irrecoverably truncated.  This wrapper uses the
retained r8-equivalent electrical topology and the actual r10 KiCad floorplan,
then packs the 76 frozen footprints inside the real 41 x 34 mm Edge.Cuts.

Key recovery rules:
- use KiCad GetBoundingBox(False) so annotation text is not a fake component body;
- preserve a board-edge guard and the r10 all-layer RF antenna keep-out;
- keep U1 below the antenna window and U2 in the r10 PMIC area;
- rotate the physically wide J7 FH12 connector by 90 degrees and place it in the
  lower-right region, away from the RF window;
- use one global occupancy map so functional-zone bookkeeping cannot hide
  footprint overlap;
- let KiCad 9.0.9 courtyard/clearance/edge DRC be final placement authority.

This creates an unrouted recovery seed only.  r13 still replaces the U2 cluster
with Nordic-reference current-loop placement before power routing begins.
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

# Actual r10 geometry, read directly from AegisBioWatch-MainBoard-Floorplan-r10.kicad_pcb.
EDGE = (2.0, 2.75, 43.0, 36.75)
BOARD_INTERIOR = (2.35, 3.10, 42.65, 36.40)  # 0.35 mm synthetic packing guard
RF_ANTENNA_BLOCK = (30.80, 2.75, 43.0, 9.20)  # r10 KO plus 0.20 mm planning guard

# Real-r10 anchor centres.  U1/U2 are only broad seed anchors; r13 must replace
# their critical local passive geometry from Nordic reference-layout authority.
mod.FIXED_ANCHORS["U1"] = (28.75, 13.75)
mod.FIXED_ANCHORS["U2"] = (11.25, 28.50)

GLOBAL_OCCUPIED: list[tuple[float, float, float, float]] = []


def bbox_local_mm_no_text(fp):
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    box = fp.GetBoundingBox(False)
    return (
        float(pcbnew.ToMM(box.GetX())),
        float(pcbnew.ToMM(box.GetY())),
        float(pcbnew.ToMM(box.GetWidth())),
        float(pcbnew.ToMM(box.GetHeight())),
    )


def set_orientation_deg(fp, degrees: float):
    if hasattr(fp, "SetOrientationDegrees"):
        fp.SetOrientationDegrees(degrees)
    else:
        fp.SetOrientation(pcbnew.EDA_ANGLE(degrees, pcbnew.DEGREES_T))


def intersects(a, b, gap: float = 0.0):
    return not (
        a[2] + gap <= b[0] or b[2] + gap <= a[0] or
        a[3] + gap <= b[1] or b[3] + gap <= a[1]
    )


def inside(candidate, bounds):
    return (
        candidate[0] >= bounds[0] and candidate[1] >= bounds[1] and
        candidate[2] <= bounds[2] and candidate[3] <= bounds[3]
    )


def candidate_rect(fp, bbox_min_x: float, bbox_min_y: float, margin: float):
    _lx, _ly, w, h = bbox_local_mm_no_text(fp)
    return (
        bbox_min_x - margin,
        bbox_min_y - margin,
        bbox_min_x + w + margin,
        bbox_min_y + h + margin,
    )


def commit_bbox_min(fp, bbox_min_x: float, bbox_min_y: float, margin: float):
    rect = candidate_rect(fp, bbox_min_x, bbox_min_y, margin)
    mod.rect_for_fp_at_bbox_min(fp, bbox_min_x, bbox_min_y, margin)
    GLOBAL_OCCUPIED.append(rect)
    return rect


def valid_candidate(rect):
    if not inside(rect, BOARD_INTERIOR):
        return False
    if intersects(rect, RF_ANTENNA_BLOCK):
        return False
    if any(intersects(rect, other, 0.10) for other in GLOBAL_OCCUPIED):
        return False
    return True


original_place_anchor = mod.place_anchor


def place_anchor_global(fp, center_x: float, center_y: float, margin: float = 0.35):
    rect = original_place_anchor(fp, center_x, center_y, margin)
    if not inside(rect, BOARD_INTERIOR):
        raise SystemExit(f"fixed anchor {fp.GetReference()} exceeds r10 board interior: {rect}")
    if intersects(rect, RF_ANTENNA_BLOCK):
        raise SystemExit(f"fixed anchor {fp.GetReference()} enters r10 RF antenna keep-out: {rect}")
    if any(intersects(rect, other, 0.10) for other in GLOBAL_OCCUPIED):
        raise SystemExit(f"fixed anchor {fp.GetReference()} overlaps prior fixed placement: {rect}")
    GLOBAL_OCCUPIED.append(rect)
    return rect


def scan_global(fp, _zone, _occupied, margin: float = 0.25):
    ref = fp.GetReference()

    # J7's KiCad-9 no-text bbox is 16.15 x 7.95 mm at 0 degrees.  Rotate it so
    # its 7.95 mm width fits the right-side column while its 16.15 mm height
    # stays well below the RF antenna window.  No extra synthetic guard is used
    # because the KiCad bbox already contains the library courtyard geometry;
    # real courtyard clearance is checked by KiCad DRC later.
    if ref == "J7":
        set_orientation_deg(fp, 90.0)
        x, y = 31.50, 19.80
        rect = candidate_rect(fp, x, y, 0.0)
        print("J7 rotated bbox mm =", bbox_local_mm_no_text(fp), "candidate=", rect)
        if not valid_candidate(rect):
            raise SystemExit(f"fixed J7 recovery placement invalid: {rect}")
        return commit_bbox_min(fp, x, y, 0.0)

    # Search the actual r10 board interior.  Try the current orientation first,
    # then 90 degrees.  Large parts are placed first by the underlying builder.
    step = 0.25
    for angle in (0.0, 90.0):
        set_orientation_deg(fp, angle)
        _lx, _ly, w, h = bbox_local_mm_no_text(fp)
        max_x = BOARD_INTERIOR[2] - w - margin
        max_y = BOARD_INTERIOR[3] - h - margin
        y = BOARD_INTERIOR[1] + margin
        while y <= max_y + 1e-9:
            x = BOARD_INTERIOR[0] + margin
            while x <= max_x + 1e-9:
                rect = candidate_rect(fp, x, y, margin)
                if valid_candidate(rect):
                    return commit_bbox_min(fp, x, y, margin)
                x += step
            y += step
    return None


mod.bbox_local_mm = bbox_local_mm_no_text
mod.place_anchor = place_anchor_global
mod.scan_place = scan_global

# The underlying script expects named zones.  Keep them, but make every search
# domain the same actual board interior; scan_global owns the single collision map.
for key in list(mod.ZONES):
    mod.ZONES[key] = BOARD_INTERIOR

j7 = mod.load_fp("Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
j7.SetReference("J7")
print("r10 Edge.Cuts mm =", EDGE)
print("r10 packing interior mm =", BOARD_INTERIOR)
print("r10 RF antenna block mm =", RF_ANTENNA_BLOCK)
print("J7 KiCad GetBoundingBox(False) 0deg mm =", bbox_local_mm_no_text(j7))

mod.main()
