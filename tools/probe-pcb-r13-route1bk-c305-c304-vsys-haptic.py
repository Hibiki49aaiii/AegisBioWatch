#!/usr/bin/env python3
"""Read-only exact Phase B probe for route-1bk C305.1/VSYS_HAPTIC -> C304.1/VSYS_HAPTIC."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bj.json"

POINTS = [[6.805, 22.335], [6.805, 21.65], [16.005, 21.65], [16.005, 23.725]]
SEGMENT_LENGTHS = [0.685, 9.2, 2.075]
TRACK_WIDTH = 0.30
TOTAL_LENGTH = 11.96
RULE = 0.10
EXPECTED_CLEARANCE = 0.125
NEAREST_GND_VIA = [12.75, 22.225]
VIA_DIAMETER = 0.60


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v: int) -> float:
    return float(pcbnew.ToMM(v))


def pos(pad) -> list[float]:
    p = pad.GetPosition()
    return [round(mm(p.x), 6), round(mm(p.y), 6)]


def size(pad) -> list[float]:
    s = pad.GetSize()
    return [round(mm(s.x), 6), round(mm(s.y), 6)]


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bj-drc-json", required=True)
    ap.add_argument("--route1bj-pin-net-audit", required=True)
    ap.add_argument("--dogleg-screen-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bk exact probe source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bj_drc_json))
    audit = load_json(Path(args.route1bj_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 114:
        raise SystemExit("route1bk exact probe source DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bk exact probe source audit gate failed")

    screen = load_json(Path(args.dogleg_screen_json))
    if screen.get("source_route1bj_sha256") != source_sha:
        raise SystemExit("route1bk exact probe screen/source SHA mismatch")
    if screen.get("source_gate") != {
        "rule_violations": 0,
        "unconnected_items": 114,
        "pin_net_audit": "PASS",
        "audited_nodes": 268,
    }:
        raise SystemExit("route1bk exact probe screen source gate mismatch")
    if screen.get("board_modified") is not False or abs(float(screen.get("grid_mm")) - 0.05) > 1e-9:
        raise SystemExit("route1bk exact probe screen mode gate failed")

    matches = [
        c for c in screen.get("passing_candidates", [])
        if c.get("net") == "VSYS_HAPTIC"
        and c.get("a", {}).get("description") == "Pad 1 [VSYS_HAPTIC] of C305 on Top_layer"
        and c.get("b", {}).get("description") == "Pad 1 [VSYS_HAPTIC] of C304 on Top_layer"
    ]
    if len(matches) != 1:
        raise SystemExit(f"route1bk selected candidate cardinality failed: {len(matches)}")

    candidate = matches[0]
    path = candidate.get("best_passing_path", {})
    if path.get("points_mm") != POINTS:
        raise SystemExit(f"route1bk selected path changed: {path.get('points_mm')}")
    if path.get("segment_count") != 3 or path.get("path_family") != "VHV":
        raise SystemExit("route1bk path family/scope gate failed")
    if abs(float(path.get("path_length_mm")) - TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bk path length gate failed")
    clearance = float(path.get("minimum_conservative_clearance_mm"))
    if clearance + 1e-9 < EXPECTED_CLEARANCE or clearance < RULE:
        raise SystemExit(f"route1bk clearance gate failed: {clearance}")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    c305, c304, u4, r305 = fps.get("C305"), fps.get("C304"), fps.get("U4"), fps.get("R305")
    if None in (c305, c304, u4, r305):
        raise SystemExit("route1bk missing C305/C304/U4/R305")
    if c305.GetValue() != "1uF" or c304.GetValue() != "100nF":
        raise SystemExit("route1bk capacitor value gate failed")
    if u4.GetValue() != "DRV2605LDGSR" or r305.GetValue() != "0R / FB OPTION":
        raise SystemExit("route1bk haptic supply identity gate failed")

    c305p1, c305p2 = get_pad(c305, "1"), get_pad(c305, "2")
    c304p1, c304p2 = get_pad(c304, "1"), get_pad(c304, "2")
    u4p10 = get_pad(u4, "10")
    r305p1, r305p2 = get_pad(r305, "1"), get_pad(r305, "2")

    observed = {
        "C305.1": {"net": c305p1.GetNetname(), "position_mm": pos(c305p1)},
        "C305.2": {"net": c305p2.GetNetname(), "position_mm": pos(c305p2)},
        "C304.1": {"net": c304p1.GetNetname(), "position_mm": pos(c304p1)},
        "C304.2": {"net": c304p2.GetNetname(), "position_mm": pos(c304p2)},
        "U4.10": {"net": u4p10.GetNetname(), "position_mm": pos(u4p10)},
        "R305.1": {"net": r305p1.GetNetname(), "position_mm": pos(r305p1)},
        "R305.2": {"net": r305p2.GetNetname(), "position_mm": pos(r305p2)},
    }
    expected = {
        "C305.1": {"net": "VSYS_HAPTIC", "position_mm": [6.805, 22.335]},
        "C305.2": {"net": "GND", "position_mm": [7.765, 22.335]},
        "C304.1": {"net": "VSYS_HAPTIC", "position_mm": [16.005, 23.725]},
        "C304.2": {"net": "GND", "position_mm": [16.645, 23.725]},
        "U4.10": {"net": "VSYS_HAPTIC", "position_mm": [23.005, 13.4]},
        "R305.1": {"net": "VSYS", "position_mm": [30.295, 18.595]},
        "R305.2": {"net": "VSYS_HAPTIC", "position_mm": [31.315, 18.595]},
    }
    if observed != expected:
        raise SystemExit(f"route1bk endpoint/context gate failed: {observed}")

    matched_vias = []
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA):
            continue
        p = item.GetPosition()
        pxy = [round(mm(p.x), 6), round(mm(p.y), 6)]
        if pxy == NEAREST_GND_VIA:
            matched_vias.append(item)
    if len(matched_vias) != 1:
        raise SystemExit(f"route1bk nearest via cardinality failed: {len(matched_vias)}")
    via = matched_vias[0]
    if via.GetNetname() != "GND":
        raise SystemExit("route1bk nearest via net gate failed")
    via_diameter = round(mm(via.GetWidth()), 6)
    if abs(via_diameter - VIA_DIAMETER) > 1e-6:
        raise SystemExit(f"route1bk nearest via diameter gate failed: {via_diameter}")

    independent_gap = round(
        abs(NEAREST_GND_VIA[1] - 21.65) - TRACK_WIDTH / 2.0 - VIA_DIAMETER / 2.0,
        6,
    )
    if abs(independent_gap - EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit(f"route1bk independent GND via gap failed: {independent_gap}")

    out = {
        "revision": "r13-route1bk-c305-c304-vsys-haptic-exact-probe",
        "source_route1bj_sha256": source_sha,
        "board_modified": False,
        "C305_value": c305.GetValue(),
        "C304_value": c304.GetValue(),
        "U4_value": u4.GetValue(),
        "R305_value": r305.GetValue(),
        "pads": observed,
        "path": {
            "points_mm": POINTS,
            "segment_count": 3,
            "segment_lengths_mm": SEGMENT_LENGTHS,
            "total_length_mm": TOTAL_LENGTH,
            "track_width_mm": TRACK_WIDTH,
            "minimum_conservative_clearance_mm": clearance,
            "independent_gnd_via_gap_mm": independent_gap,
            "required_clearance_mm": RULE,
            "nearest_unrelated_copper": path.get("nearest_unrelated_copper"),
        },
        "nearest_gnd_via": {
            "position_mm": NEAREST_GND_VIA,
            "diameter_mm": via_diameter,
            "net": via.GetNetname(),
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
