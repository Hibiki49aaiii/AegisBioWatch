#!/usr/bin/env python3
"""Read-only exact Phase B probe for route-1bj R404.1/+1V8 -> R302.1/+1V8."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bi"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bi.json"

POINTS = [[15.755, 26.725], [15.755, 26.2], [20.255, 26.2], [20.255, 25.975]]
SEGMENT_LENGTHS = [0.525, 4.5, 0.225]
TRACK_WIDTH = 0.30
TOTAL_LENGTH = 5.25
RULE = 0.10
EXPECTED_CLEARANCE = 0.175


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
    ap.add_argument("--route1bi-drc-json", required=True)
    ap.add_argument("--route1bi-pin-net-audit", required=True)
    ap.add_argument("--dogleg-screen-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bj exact probe source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bi_drc_json))
    audit = load_json(Path(args.route1bi_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 115:
        raise SystemExit("route1bj exact probe source DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bj exact probe source audit gate failed")

    screen = load_json(Path(args.dogleg_screen_json))
    if screen.get("source_route1bi_sha256") != source_sha:
        raise SystemExit("route1bj exact probe screen/source SHA mismatch")
    if screen.get("source_gate") != {
        "rule_violations": 0,
        "unconnected_items": 115,
        "pin_net_audit": "PASS",
        "audited_nodes": 268,
    }:
        raise SystemExit("route1bj exact probe screen source gate mismatch")
    if screen.get("board_modified") is not False or abs(float(screen.get("grid_mm")) - 0.05) > 1e-9:
        raise SystemExit("route1bj exact probe screen mode gate failed")

    matches = [
        c for c in screen.get("passing_candidates", [])
        if c.get("net") == "+1V8"
        and c.get("a", {}).get("description") == "Pad 1 [+1V8] of R404 on Top_layer"
        and c.get("b", {}).get("description") == "Pad 1 [+1V8] of R302 on Top_layer"
    ]
    if len(matches) != 1:
        raise SystemExit(f"route1bj selected candidate cardinality failed: {len(matches)}")

    candidate = matches[0]
    path = candidate.get("best_passing_path", {})
    if path.get("points_mm") != POINTS:
        raise SystemExit(f"route1bj selected path changed: {path.get('points_mm')}")
    if path.get("segment_count") != 3 or path.get("path_family") != "VHV":
        raise SystemExit("route1bj path family/scope gate failed")
    if abs(float(path.get("path_length_mm")) - TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bj path length gate failed")
    clearance = float(path.get("minimum_conservative_clearance_mm"))
    if clearance + 1e-9 < EXPECTED_CLEARANCE or clearance < RULE:
        raise SystemExit(f"route1bj clearance gate failed: {clearance}")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r404, r302, r501 = fps.get("R404"), fps.get("R302"), fps.get("R501")
    if r404 is None or r302 is None or r501 is None:
        raise SystemExit("route1bj missing R404/R302/R501")
    if r404.GetValue() != "4.7k PU PROV":
        raise SystemExit(f"route1bj R404 value gate failed: {r404.GetValue()!r}")
    if r302.GetValue() != "47k PU":
        raise SystemExit(f"route1bj R302 value gate failed: {r302.GetValue()!r}")
    if r501.GetValue() != "100k":
        raise SystemExit(f"route1bj R501 value gate failed: {r501.GetValue()!r}")

    r404p1, r404p2 = get_pad(r404, "1"), get_pad(r404, "2")
    r302p1, r302p2 = get_pad(r302, "1"), get_pad(r302, "2")
    r501p1, r501p2 = get_pad(r501, "1"), get_pad(r501, "2")

    observed = {
        "R404.1": {"net": r404p1.GetNetname(), "position_mm": pos(r404p1)},
        "R404.2": {"net": r404p2.GetNetname(), "position_mm": pos(r404p2)},
        "R302.1": {"net": r302p1.GetNetname(), "position_mm": pos(r302p1)},
        "R302.2": {"net": r302p2.GetNetname(), "position_mm": pos(r302p2)},
        "R501.1": {"net": r501p1.GetNetname(), "position_mm": pos(r501p1), "size_mm": size(r501p1)},
        "R501.2": {"net": r501p2.GetNetname(), "position_mm": pos(r501p2)},
    }
    expected = {
        "R404.1": {"net": "+1V8", "position_mm": [15.755, 26.725]},
        "R404.2": {"net": "SYS_I2C_SCL", "position_mm": [16.395, 26.725]},
        "R302.1": {"net": "+1V8", "position_mm": [20.255, 25.975]},
        "R302.2": {"net": "FLASH_HOLD_N", "position_mm": [20.895, 25.975]},
        "R501.1": {"net": "CHG_5V", "position_mm": [18.005, 26.725], "size_mm": [0.46, 0.4]},
        "R501.2": {"net": "CHG_SENSE_GATE", "position_mm": [18.645, 26.725]},
    }
    if observed != expected:
        raise SystemExit(f"route1bj endpoint/context gate failed: {observed}")

    # Independent local clearance check for the horizontal segment versus R501.1.
    pad_bottom = observed["R501.1"]["position_mm"][1] - observed["R501.1"]["size_mm"][1] / 2
    track_top = 26.2 + TRACK_WIDTH / 2
    local_gap = round(pad_bottom - track_top, 6)
    if abs(local_gap - EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit(f"route1bj independent R501.1 gap gate failed: {local_gap}")

    out = {
        "revision": "r13-route1bj-r404-r302-1v8-exact-probe",
        "source_route1bi_sha256": source_sha,
        "board_modified": False,
        "R404_value": r404.GetValue(),
        "R302_value": r302.GetValue(),
        "R501_value": r501.GetValue(),
        "pads": observed,
        "path": {
            "points_mm": POINTS,
            "segment_count": 3,
            "segment_lengths_mm": SEGMENT_LENGTHS,
            "total_length_mm": TOTAL_LENGTH,
            "track_width_mm": TRACK_WIDTH,
            "minimum_conservative_clearance_mm": clearance,
            "independent_r501_pad_gap_mm": local_gap,
            "required_clearance_mm": RULE,
            "nearest_unrelated_copper": path.get("nearest_unrelated_copper"),
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
