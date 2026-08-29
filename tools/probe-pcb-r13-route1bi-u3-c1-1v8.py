#!/usr/bin/env python3
"""Read-only exact Phase B probe for route-1bi U3.8/+1V8 -> C1.1/+1V8."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bg"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bg.json"

POINTS = [[11.08, 4.72], [10.305, 4.72], [10.305, 11.085]]
TRACK_WIDTH = 0.30
TOTAL_LENGTH = 7.14
RULE = 0.10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v: int) -> float:
    return float(pcbnew.ToMM(v))


def pos(pad) -> list[float]:
    p = pad.GetPosition()
    return [round(mm(p.x), 6), round(mm(p.y), 6)]


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dogleg-screen-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bi exact probe source report/PCB SHA mismatch")

    screen = load_json(Path(args.dogleg_screen_json))
    if screen.get("source_route1bg_sha256") != source_sha:
        raise SystemExit("route1bi exact probe dogleg/source SHA mismatch")
    if screen.get("source_gate") != {
        "rule_violations": 0,
        "unconnected_items": 116,
        "pin_net_audit": "PASS",
        "audited_nodes": 268,
    }:
        raise SystemExit("route1bi exact probe source gate mismatch")
    if screen.get("board_modified") is not False:
        raise SystemExit("route1bi dogleg screen unexpectedly modified board")

    matches = [
        c for c in screen.get("passing_candidates", [])
        if c.get("net") == "+1V8"
        and c.get("a", {}).get("description") == "Pad 8 [+1V8] of U3 on Top_layer"
        and c.get("b", {}).get("description") == "Pad 1 [+1V8] of C1 on Top_layer"
    ]
    if len(matches) != 1:
        raise SystemExit(f"route1bi selected candidate cardinality failed: {len(matches)}")
    candidate = matches[0]
    path = candidate.get("best_passing_path", {})
    if path.get("points_mm") != POINTS:
        raise SystemExit(f"route1bi selected path changed: {path.get('points_mm')}")
    if path.get("segment_count") != 2 or path.get("path_family") != "L-HV":
        raise SystemExit("route1bi path family/scope gate failed")
    if abs(float(path.get("path_length_mm")) - TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bi path length gate failed")
    clearance = float(path.get("minimum_conservative_clearance_mm"))
    if clearance < RULE:
        raise SystemExit(f"route1bi clearance gate failed: {clearance} < {RULE}")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    u3, c1 = fps.get("U3"), fps.get("C1")
    if u3 is None or c1 is None:
        raise SystemExit("route1bi missing U3/C1")
    if u3.GetValue() != "W25Q256JWPIQ 256Mbit":
        raise SystemExit(f"route1bi U3 value gate failed: {u3.GetValue()!r}")
    if c1.GetValue() != "10uF":
        raise SystemExit(f"route1bi C1 value gate failed: {c1.GetValue()!r}")

    u8 = get_pad(u3, "8")
    u7 = get_pad(u3, "7")
    u5 = get_pad(u3, "5")
    c1p1 = get_pad(c1, "1")
    c1p2 = get_pad(c1, "2")

    observed = {
        "U3.8": {"net": u8.GetNetname(), "position_mm": pos(u8)},
        "U3.7": {"net": u7.GetNetname(), "position_mm": pos(u7)},
        "U3.5": {"net": u5.GetNetname(), "position_mm": pos(u5)},
        "C1.1": {"net": c1p1.GetNetname(), "position_mm": pos(c1p1)},
        "C1.2": {"net": c1p2.GetNetname(), "position_mm": pos(c1p2)},
    }
    expected = {
        "U3.8": {"net": "+1V8", "position_mm": [11.08, 4.72]},
        "U3.7": {"net": "FLASH_HOLD_N", "position_mm": [11.08, 5.99]},
        "U3.5": {"net": "AUX_SPI_MOSI", "position_mm": [11.08, 8.53]},
        "C1.1": {"net": "+1V8", "position_mm": [10.305, 11.085]},
        "C1.2": {"net": "GND", "position_mm": [11.265, 11.085]},
    }
    if observed != expected:
        raise SystemExit(f"route1bi endpoint/context gate failed: {observed}")

    out = {
        "revision": "r13-route1bi-u3-c1-1v8-exact-probe",
        "source_route1bg_sha256": source_sha,
        "board_modified": False,
        "U3_value": u3.GetValue(),
        "C1_value": c1.GetValue(),
        "pads": observed,
        "path": {
            "points_mm": POINTS,
            "segment_count": 2,
            "segment_lengths_mm": [0.775, 6.365],
            "total_length_mm": TOTAL_LENGTH,
            "track_width_mm": TRACK_WIDTH,
            "minimum_conservative_clearance_mm": clearance,
            "required_clearance_mm": RULE,
            "nearest_unrelated_copper": path.get("nearest_unrelated_copper"),
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
