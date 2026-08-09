#!/usr/bin/env python3
"""Recover an unrouted r11 seed in the actual r10 board datum.

The historical r11 payload is truncated. This wrapper keeps r8-equivalent nets,
r10 Edge.Cuts/RF keep-out, 76 frozen footprints, and delegates final geometry
validity to KiCad 9.0.9 PCB DRC. It does not recreate the lost r11 coordinates.
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

EDGE = (2.0, 2.75, 43.0, 36.75)
BOARD_INTERIOR = (2.35, 3.10, 42.65, 36.40)
RF_ANTENNA_BLOCK = (30.80, 2.75, 43.0, 9.20)
mod.FIXED_ANCHORS["U1"] = (28.75, 13.75)
mod.FIXED_ANCHORS["U2"] = (11.25, 28.50)
GLOBAL_OCCUPIED: list[tuple[float, float, float, float]] = []

# r10 intentionally has only the PCB floorplan file. The old generic builder
# expected a sibling .kicad_pro; skip only that absent optional copy.
_real_copy2 = mod.shutil.copy2
def _copy2_optional(src, dst, *args, **kwargs):
    if Path(src) == mod.R10_PRO and not Path(src).exists():
        print(f"r10 project file absent by design; PCB-only recovery continues: {src}")
        return str(dst)
    return _real_copy2(src, dst, *args, **kwargs)
mod.shutil.copy2 = _copy2_optional


def bbox_local_mm(fp):
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    b = fp.GetBoundingBox(False)
    return tuple(float(pcbnew.ToMM(v)) for v in (b.GetX(), b.GetY(), b.GetWidth(), b.GetHeight()))


def set_angle(fp, deg: float):
    if hasattr(fp, "SetOrientationDegrees"):
        fp.SetOrientationDegrees(deg)
    else:
        fp.SetOrientation(pcbnew.EDA_ANGLE(deg, pcbnew.DEGREES_T))


def intersects(a, b, gap=0.0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def candidate(fp, x, y, margin):
    _, _, w, h = bbox_local_mm(fp)
    return (x - margin, y - margin, x + w + margin, y + h + margin)


def valid(rect):
    return (inside(rect, BOARD_INTERIOR)
            and not intersects(rect, RF_ANTENNA_BLOCK)
            and not any(intersects(rect, o, 0.10) for o in GLOBAL_OCCUPIED))


def commit(fp, x, y, margin):
    rect = candidate(fp, x, y, margin)
    mod.rect_for_fp_at_bbox_min(fp, x, y, margin)
    GLOBAL_OCCUPIED.append(rect)
    return rect


_original_anchor = mod.place_anchor
def place_anchor(fp, x, y, margin=0.35):
    rect = _original_anchor(fp, x, y, margin)
    if not inside(rect, BOARD_INTERIOR) or intersects(rect, RF_ANTENNA_BLOCK):
        raise SystemExit(f"fixed anchor {fp.GetReference()} violates r10 geometry: {rect}")
    if any(intersects(rect, o, 0.10) for o in GLOBAL_OCCUPIED):
        raise SystemExit(f"fixed anchor {fp.GetReference()} overlaps prior placement: {rect}")
    GLOBAL_OCCUPIED.append(rect)
    return rect


def scan_place(fp, _zone, _occupied, margin=0.25):
    ref = fp.GetReference()
    if ref == "J7":
        set_angle(fp, 90.0)
        x, y = 31.50, 19.80
        rect = candidate(fp, x, y, 0.0)
        print("J7 rotated bbox mm =", bbox_local_mm(fp), "candidate=", rect)
        if not valid(rect):
            raise SystemExit(f"fixed J7 recovery placement invalid: {rect}")
        return commit(fp, x, y, 0.0)

    step = 0.25
    for angle in (0.0, 90.0):
        set_angle(fp, angle)
        _, _, w, h = bbox_local_mm(fp)
        y = BOARD_INTERIOR[1] + margin
        while y <= BOARD_INTERIOR[3] - h - margin + 1e-9:
            x = BOARD_INTERIOR[0] + margin
            while x <= BOARD_INTERIOR[2] - w - margin + 1e-9:
                rect = candidate(fp, x, y, margin)
                if valid(rect):
                    return commit(fp, x, y, margin)
                x += step
            y += step
    return None

mod.bbox_local_mm = bbox_local_mm
mod.place_anchor = place_anchor
mod.scan_place = scan_place
for key in list(mod.ZONES):
    mod.ZONES[key] = BOARD_INTERIOR

j7 = mod.load_fp("Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
j7.SetReference("J7")
print("r10 Edge.Cuts mm =", EDGE)
print("r10 packing interior mm =", BOARD_INTERIOR)
print("r10 RF antenna block mm =", RF_ANTENNA_BLOCK)
print("J7 KiCad GetBoundingBox(False) 0deg mm =", bbox_local_mm(j7))
mod.main()
