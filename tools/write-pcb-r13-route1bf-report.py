#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1be/AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1be/routing-seed-r13-1be.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bf"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1bf.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha = sha256(SRC_PCB)
    if source.get("output_sha256") != source_sha:
        raise SystemExit("route1be report/PCB SHA mismatch in route1bf report helper")

    out = {
        "revision": "r13-route1bf-r301-r503-1v8-local",
        "source_route1be_sha256": source_sha,
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": 1,
        "vias_added": 0,
        "track_width_mm": 0.30,
        "track_length_mm": 1.500,
        "connections": {
            "R301.1/+1V8 to R503.1/+1V8": {
                "r301_value": "47k PU",
                "r503_value": "47k PU",
                "r301_pad1_mm": [3.005, 25.975],
                "r503_pad1_mm": [3.005, 27.475],
                "r301_pad1_net": "+1V8",
                "r503_pad1_net": "+1V8",
                "r301_pad2_mm": [3.645, 25.975],
                "r503_pad2_mm": [3.645, 27.475],
                "r301_pad2_net": "FLASH_WP_N",
                "r503_pad2_net": "CHG_PRESENT_N",
            }
        },
        "preflight": {
            "rule_clearance_mm": 0.100,
            "conservative_lateral_gap_to_signal_pad_column_mm": 0.260,
            "expected_probe_blockers": 0,
        },
        "logical_connectivity_added": ["R301.1/+1V8 -> R503.1/+1V8"],
        "component_moves": [],
        "component_rotations": [],
        "accepted_route1be_geometry_modified": False,
        "signal_side_routing_touched": False,
        "rf_routing_touched": False,
        "supplier_gated_interfaces_touched": False,
        "sys_i2c_scl_status": "DEFERRED_GEOMETRY_GATED",
        "ldo2_in_status": "DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD",
        "route1n_chg5v_status": "REJECTED_AND_DEFERRED",
        "validation_status": "PENDING_EXECUTED_KICAD_DRC",
        "release_status": "NOT_FOR_GERBER",
        "report_process": "fresh_python_without_pcbnew",
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
