#!/usr/bin/env python3
"""Materialize r13 nPM1300 placement from the validated recovered-r11 seed.

The historical r11 archive is irrecoverably truncated, so this materializer is
bound to a freshly rebuilt r11 whose exact PCB SHA has executed KiCad 9.0.9 DRC
(0 rule violations / 186 unrouted items) and a 268-node physical-pad audit.

Unlike the earlier r13 pad-anchor prototype, this implementation places PMIC
support components with KiCad's actual no-text footprint bounding geometry and
collision checks. U2 remains fixed. Functional attraction targets come only
from AegisBioWatch's actual U2 / inductor pad geometry; no third-party absolute
coordinates are copied.

Physical authority remains Nordic's nPM1300 QEAA reference-layout/current-loop
guidance. The algorithm prioritizes compact SW/PVDD/PVSS/VOUT loops while
allowing lower-speed VSET/I2C/LS-LDO support parts to sit farther away when
necessary for legal placement.

This is still an unrouted placement revision and is NOT fabrication authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_R11_DIR = ROOT / "hardware/main-board/pcb/placement-r11-rebuilt"
DEFAULT_R11_PCB = DEFAULT_R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pcb"
DEFAULT_R11_PRO = DEFAULT_R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pro"
DEFAULT_R11_MANIFEST = DEFAULT_R11_DIR / "placement-seed-manifest-r11-rebuilt.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/placement-r13"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pro"
OUT_REPORT = OUT_DIR / "placement-implementation-r13.json"

BOARD_INTERIOR = (2.35, 3.10, 42.65, 36.40)
RF_ANTENNA_BLOCK = (30.80, 2.75, 43.0, 9.20)
PLACEMENT_GAP_MM = 0.10

PMIC_SUPPORT = {
    *(f"C{i}" for i in range(101, 115)),
    "L101", "L102", "NT101", "NT102",
    *(f"R{i}" for i in range(101, 107)),
}
ALL_PMIC = PMIC_SUPPORT | {"U2"}

# Logical pin/net guard copied from the retained electrical authority. This is a
# gate, not a replacement for KiCad DRC or the 268-node source audit.
U2_CRITICAL = {
    "1": "+1V8", "2": "PVSS1_LOCAL", "3": "PMIC_SW1", "4": "VSYS",
    "5": "PMIC_SW2", "6": "PVSS2_LOCAL", "12": "+1V8",
    "13": "SYS_I2C_SDA", "14": "SYS_I2C_SCL", "15": "SHIP_HOLD",
    "16": "PMIC_VSET2", "17": "PMIC_VSET1", "18": "BAT_NTC",
    "19": "VBAT", "20": "VSYS", "21": "CHG_5V", "22": "VBUSOUT_SENSE",
    "28": "LDO1_IN", "29": "DISP_SW", "30": "LDO2_IN", "31": "BIO_SW",
    "32": "+3V0", "33": "GND",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing required evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def mm(value: int) -> float:
    return float(pcbnew.ToMM(value))


def iu(value_mm: float) -> int:
    return int(pcbnew.FromMM(value_mm))


def rect(fp) -> tuple[float, float, float, float]:
    b = fp.GetBoundingBox(False)
    return (mm(b.GetX()), mm(b.GetY()), mm(b.GetRight()), mm(b.GetBottom()))


def center_of_rect(r):
    return ((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)


def fp_center(fp):
    return center_of_rect(rect(fp))


def inside(a, bounds):
    return a[0] >= bounds[0] and a[1] >= bounds[1] and a[2] <= bounds[2] and a[3] <= bounds[3]


def intersects(a, b, gap=0.0):
    return not (
        a[2] + gap <= b[0] or b[2] + gap <= a[0]
        or a[3] + gap <= b[1] or b[3] + gap <= a[1]
    )


def set_angle(fp, deg: float):
    if hasattr(fp, "SetOrientationDegrees"):
        fp.SetOrientationDegrees(deg)
    else:
        fp.SetOrientation(pcbnew.EDA_ANGLE(deg, pcbnew.DEGREES_T))


def place_bbox_center(fp, cx: float, cy: float, angle: float):
    """Place footprint such that its no-text bbox center lands at cx/cy."""
    set_angle(fp, angle)
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    b = fp.GetBoundingBox(False)
    local_cx = mm(b.GetX()) + mm(b.GetWidth()) / 2.0
    local_cy = mm(b.GetY()) + mm(b.GetHeight()) / 2.0
    fp.SetPosition(pcbnew.VECTOR2I(iu(cx - local_cx), iu(cy - local_cy)))
    return rect(fp)


def pad_positions(fp, number: str):
    return [
        (mm(p.GetPosition().x), mm(p.GetPosition().y))
        for p in fp.Pads() if str(p.GetNumber()) == str(number)
    ]


def pad_point(fp, number: str):
    pts = pad_positions(fp, number)
    if not pts:
        raise SystemExit(f"{fp.GetReference()} missing pad {number}")
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def mean_points(points):
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def unit(v):
    d = math.hypot(v[0], v[1])
    if d < 1e-9:
        return (1.0, 0.0)
    return (v[0] / d, v[1] / d)


def rotate_vec(v, degrees):
    r = math.radians(degrees)
    return (v[0] * math.cos(r) - v[1] * math.sin(r), v[0] * math.sin(r) + v[1] * math.cos(r))


def bbox_distance(a, b):
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def validate_source(args, source_sha):
    manifest = load_json(args.source_manifest)
    if manifest.get("output_pcb_sha256") != source_sha:
        raise SystemExit(
            "recovered r11 manifest/PCB SHA mismatch: "
            f"manifest={manifest.get('output_pcb_sha256')} actual={source_sha}"
        )
    expected = {
        "components_r8": 79,
        "footprints_imported": 76,
        "nets_r8": 86,
        "net_nodes_r8": 268,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise SystemExit(f"recovered r11 invariant mismatch {key}: {manifest.get(key)} != {value}")

    drc = load_json(args.drc_summary)
    if drc.get("rule_violations") != 0 or drc.get("unconnected_items") != 186:
        raise SystemExit(
            "r13 source rejected by executed r11 DRC gate: "
            f"violations={drc.get('rule_violations')} unconnected={drc.get('unconnected_items')}"
        )
    audit = load_json(args.pin_net_audit)
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit(
            "r13 source rejected by recovered r11 pin/net gate: "
            f"result={audit.get('result')} nodes={audit.get('audited_present_source_nodes')}"
        )
    return manifest, drc, audit


def u2_pin_gate(u2):
    failures = []
    for pin, expected in U2_CRITICAL.items():
        pads = [p for p in u2.Pads() if str(p.GetNumber()) == pin]
        nets = sorted({p.GetNetname() for p in pads})
        if not pads or nets != [expected]:
            failures.append({"pin": pin, "expected": expected, "actual": nets})
    if failures:
        raise SystemExit("U2 critical pin/net gate failed: " + json.dumps(failures, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-pcb", type=Path, default=DEFAULT_R11_PCB)
    ap.add_argument("--source-pro", type=Path, default=DEFAULT_R11_PRO)
    ap.add_argument("--source-manifest", type=Path, default=DEFAULT_R11_MANIFEST)
    ap.add_argument("--drc-summary", type=Path, required=True)
    ap.add_argument("--pin-net-audit", type=Path, required=True)
    args = ap.parse_args()

    for path in (args.source_pcb, args.source_pro, args.source_manifest):
        if not path.is_file():
            raise SystemExit(f"missing recovered r11 source: {path}")
    source_sha = sha256(args.source_pcb)
    manifest, _drc, _audit = validate_source(args, source_sha)

    board = pcbnew.LoadBoard(str(args.source_pcb))
    if board is None:
        raise SystemExit(f"unable to load source PCB: {args.source_pcb}")
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if len(fps) != 76:
        raise SystemExit(f"r13 source footprint count changed: expected 76, got {len(fps)}")
    missing = sorted(ALL_PMIC - set(fps))
    if missing:
        raise SystemExit(f"r13 source missing PMIC refs: {missing}")

    u2 = fps["U2"]
    u2_pin_gate(u2)
    u2_box = rect(u2)
    u2_center = fp_center(u2)

    # Keep all non-PMIC seed footprints fixed. PMIC support placements are the
    # only moving geometry in this r13 stage; U2 itself remains fixed.
    occupied = []
    for ref, fp in fps.items():
        if ref in PMIC_SUPPORT:
            continue
        occupied.append((ref, rect(fp)))

    placement = {}

    def legal(candidate, ref):
        if not inside(candidate, BOARD_INTERIOR):
            return False
        if intersects(candidate, RF_ANTENNA_BLOCK):
            return False
        for other_ref, other_rect in occupied:
            if other_ref == ref:
                continue
            if intersects(candidate, other_rect, PLACEMENT_GAP_MM):
                return False
        return True

    def target_from_u2(pins, primary=None):
        points = [pad_point(u2, str(pin)) for pin in pins]
        base = mean_points(points)
        direction_source = pad_point(u2, str(primary if primary is not None else pins[0]))
        direction = unit((direction_source[0] - u2_center[0], direction_source[1] - u2_center[1]))
        return base, direction

    def place_radial(ref, base, direction, r_min, r_max, *, rotations=(0.0, 90.0), radial_step=0.20):
        fp = fps[ref]
        deltas = (0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90, 110, -110, 135, -135, 160, -160, 180)
        original_pos = fp.GetPosition()
        original_angle = fp.GetOrientation()
        attempts = 0
        r = r_min
        chosen = None
        while r <= r_max + 1e-9 and chosen is None:
            for delta in deltas:
                d = rotate_vec(direction, delta)
                cx, cy = base[0] + d[0] * r, base[1] + d[1] * r
                for angle in rotations:
                    attempts += 1
                    candidate = place_bbox_center(fp, cx, cy, angle)
                    if legal(candidate, ref):
                        chosen = (candidate, angle, r, delta, (cx, cy))
                        break
                if chosen:
                    break
            r += radial_step
        if chosen is None:
            fp.SetPosition(original_pos)
            fp.SetOrientation(original_angle)
            raise SystemExit(
                f"unable to collision-legally place {ref} near functional target "
                f"base={base} r={r_min}..{r_max}"
            )
        candidate, angle, radius, delta, candidate_center = chosen
        occupied.append((ref, candidate))
        placement[ref] = {
            "bbox_mm": [round(v, 4) for v in candidate],
            "bbox_center_mm": [round(v, 4) for v in center_of_rect(candidate)],
            "target_mm": [round(v, 4) for v in base],
            "target_distance_mm": round(math.dist(center_of_rect(candidate), base), 4),
            "radial_candidate_mm": round(radius, 4),
            "angular_deviation_deg": delta,
            "rotation_deg": angle,
            "attempts": attempts,
        }
        print(
            f"placed {ref}: target={base} radius={radius:.2f} delta={delta:+d} "
            f"rot={angle:.0f} bbox={candidate}"
        )

    # Critical current-loop placement. The r_min values are deliberately small;
    # physical bbox collision with U2/courtyards automatically sets the real
    # legal minimum. Search expands only as needed.
    critical_specs = [
        ("C103", (4, 2), 2, 0.70, 3.20),   # VSYS -> PVSS1 local input return
        ("C104", (4, 6), 6, 0.70, 3.20),   # VSYS -> PVSS2 local input return
        ("C114", (4,), 4, 0.80, 3.60),     # HF PVDD/VSYS bypass
        ("L101", (3,), 3, 0.90, 3.80),     # SW1
        ("L102", (5,), 5, 0.90, 3.80),     # SW2
        ("NT101", (2,), 2, 0.80, 4.20),    # PVSS1 local -> continuous GND
        ("NT102", (6,), 6, 0.80, 4.20),    # PVSS2 local -> continuous GND
    ]
    for ref, pins, primary, r_min, r_max in critical_specs:
        base, direction = target_from_u2(pins, primary)
        place_radial(ref, base, direction, r_min, r_max)

    # Output capacitors follow the corresponding inductor output pad, keeping the
    # VOUT side compact without colliding with the switch node or U2 courtyard.
    for ref, lref, lpad, primary_pin in (
        ("C107", "L101", "2", 3),
        ("C108", "L102", "2", 5),
    ):
        base = pad_point(fps[lref], lpad)
        u2_primary = pad_point(u2, str(primary_pin))
        direction = unit((base[0] - u2_primary[0], base[1] - u2_primary[1]))
        place_radial(ref, base, direction, 0.70, 4.00)

    # Remaining local power decoupling. These still use U2 functional pad
    # attraction, but may expand farther than the high-current switch loops.
    power_specs = [
        ("C102", (4,), 4, 1.00, 5.50),
        ("C106", (19,), 19, 0.90, 5.00),
        ("C101", (21,), 21, 0.90, 5.00),
        ("C105", (22,), 22, 0.90, 5.00),
        ("C113", (12,), 12, 0.80, 5.00),
    ]
    for ref, pins, primary, r_min, r_max in power_specs:
        base, direction = target_from_u2(pins, primary)
        place_radial(ref, base, direction, r_min, r_max)

    # Low-current configuration / I2C support. Keep electrically sensible
    # adjacency, but prioritize legal placement over unnecessarily short copper.
    low_specs = [
        ("R101", (17,), 17, 1.20, 7.00),
        ("R102", (16,), 16, 1.20, 7.00),
        ("R103", (13,), 13, 1.20, 7.00),
        ("R104", (14,), 14, 1.20, 7.00),
        ("R105", (28,), 28, 1.50, 8.50),
        ("C109", (29,), 29, 1.20, 8.50),
        ("C110", (29,), 29, 1.20, 9.50),
        ("R106", (30,), 30, 1.50, 8.50),
        ("C111", (31,), 31, 1.20, 8.50),
        ("C112", (31,), 31, 1.20, 9.50),
    ]
    for ref, pins, primary, r_min, r_max in low_specs:
        base, direction = target_from_u2(pins, primary)
        place_radial(ref, base, direction, r_min, r_max)

    if set(placement) != PMIC_SUPPORT:
        raise SystemExit(
            f"r13 PMIC placement completeness mismatch: missing={sorted(PMIC_SUPPORT-set(placement))} "
            f"unexpected={sorted(set(placement)-PMIC_SUPPORT)}"
        )

    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("pcbnew.SaveBoard returned false for r13")
    shutil.copy2(args.source_pro, OUT_PRO)

    # Geometry evidence useful for later route-1 and review. This is not a DRC
    # substitute; the workflow must run kicad-cli pcb drc on this exact SHA.
    pmic_boxes = [rect(fps[ref]) for ref in ALL_PMIC]
    cluster = (
        min(r[0] for r in pmic_boxes), min(r[1] for r in pmic_boxes),
        max(r[2] for r in pmic_boxes), max(r[3] for r in pmic_boxes),
    )
    critical_clearances = {}
    for ref in sorted(PMIC_SUPPORT):
        critical_clearances[ref] = round(bbox_distance(rect(fps[ref]), u2_box), 4)

    report = {
        "revision": "r13-recovered-collision-aware-npm1300-placement",
        "status": "PLACEMENT_GENERATED_PENDING_EXECUTED_KICAD_DRC",
        "source_lineage": "recovered_r8_topology_plus_r10_floorplan__kicad_9_0_9_validated_r11",
        "source_sha256": source_sha,
        "source_manifest_sha256": sha256(args.source_manifest),
        "source_drc_summary_sha256": sha256(args.drc_summary),
        "source_pin_net_audit_sha256": sha256(args.pin_net_audit),
        "source_gate": {
            "rule_violations": 0,
            "unconnected_items": 186,
            "pin_net_nodes": 268,
            "pin_net_result": "PASS",
        },
        "authority": {
            "physical": "Nordic nPM1300 QEAA reference layout/current-loop guidance",
            "coordinate_method": "AegisBioWatch U2 and L101/L102 actual pad geometry + KiCad physical bbox collision legalization",
            "third_party_absolute_coordinates": False,
        },
        "u2_fixed_bbox_mm": [round(v, 4) for v in u2_box],
        "u2_center_mm": [round(v, 4) for v in u2_center],
        "moved_refs": sorted(PMIC_SUPPORT),
        "moved_ref_count": len(PMIC_SUPPORT),
        "non_pmic_seed_refs_moved": [],
        "placement_gap_mm": PLACEMENT_GAP_MM,
        "pmic_cluster_bbox_mm": [round(v, 4) for v in cluster],
        "pmic_cluster_width_mm": round(cluster[2] - cluster[0], 4),
        "pmic_cluster_height_mm": round(cluster[3] - cluster[1], 4),
        "placement": placement,
        "u2_bbox_clearance_mm_by_ref": critical_clearances,
        "output": str(OUT_PCB.relative_to(ROOT)),
        "output_sha256": sha256(OUT_PCB),
        "routing_status": "UNROUTED",
        "validation_status": "PENDING_KICAD_PCB_DRC",
        "release_status": "NOT_FOR_GERBER",
        "privacy_boundary": "engineering_abstractions_only",
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("r13 collision-aware placement generated")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
