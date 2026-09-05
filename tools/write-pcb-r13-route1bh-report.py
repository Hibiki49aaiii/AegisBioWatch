#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bg/AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bg/routing-seed-r13-1bg.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bh"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bh-r13.kicad_pcb"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1bh.json"

START = [13.755, 23.725]
END = [15.755, 26.725]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha = sha256(SRC_PCB)
    if source.get("output_sha256") != source_sha:
        raise SystemExit("route1bg report/PCB SHA mismatch in route1bh helper")

    out = {
        "revision": "r13-route1bh-c301-r404-1v8-local",
        "source_route1bg_sha256": source_sha,
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": 1,
        "vias_added": 0,
        "track_width_mm": 0.30,
        "track_length_mm": round(math.dist(START, END), 6),
        "connections": {
            "C301.1/+1V8 to R404.1/+1V8": {
                "c301_value": "100nF",
                "r404_value": "4.7k PU PROV",
                "c301_pad1_mm": START,
                "r404_pad1_mm": END,
                "c301_pad1_net": "+1V8",
                "r404_pad1_net": "+1V8",
                "c301_pad2_mm": [14.395, 23.725],
                "c301_pad2_net": "GND",
                "r404_pad2_mm": [16.395, 26.725],
                "r404_pad2_net": "SYS_I2C_SCL"
            }
        },
        "component_moves": [],
        "component_rotations": [],
        "accepted_route1bg_geometry_modified": False,
        "c301_gnd_routing_touched": False,
        "r404_scl_routing_touched": False,
        "rf_routing_touched": False,
        "supplier_gated_interfaces_touched": False,
        "sys_i2c_scl_u2_r104_status": "DEFERRED_GEOMETRY_GATED",
        "ldo2_in_status": "DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD",
        "route1n_chg5v_status": "REJECTED_AND_DEFERRED",
        "validation_status": "PENDING_EXECUTED_KICAD_DRC",
        "release_status": "NOT_FOR_GERBER",
        "report_process": "fresh_python_without_pcbnew"
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
